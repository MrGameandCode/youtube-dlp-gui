import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
import os
import validators
import configparser
import requests
from threading import Thread
import zipfile
import shutil
import threading
import subprocess
import signal
import time
import logging

logging.basicConfig(filename='youtube-dlp-gui.log', level=logging.DEBUG)

class MainView(tk.Frame):
    
    
    launched_threads = []
    all_params = []
    total_threads = 0

    def __init__(self, root):
        tk.Frame.__init__(self, root)
        config = configparser.ConfigParser()
        config.read('config.ini')
        label_enter_URLs = tk.Label(self, text="Enter URLs below")
        label_enter_URLs.place(x=10, y=10, width=93,height=25)
        self.text_Urls_2_download = tk.Text(self, width=20, height=3) 
        self.text_Urls_2_download.place(x=10, y=30, width=400,height=50)
        self.destination_folder_photo = tk.PhotoImage(file = r".\resources\free-folder-1166-470303.gif")
        self.destination_folder_photo = self.destination_folder_photo.subsample(7, 7) #resize Image size for the button
        button_destination_folder = tk.Button(self, image = self.destination_folder_photo, text = 'Select Folder', command=self.ask_folder)
        button_destination_folder.place(x=10, y=90, width=40, height=40)
        self.entry_destination_folder = tk.Entry()
        self.entry_destination_folder.insert(0, os.getcwd())
        self.entry_destination_folder.place(x=60, y=100, width=350, height=25)
        self.combo_extensions = ttk.Combobox(self, state="readonly")
        self.combo_extensions['values']=('webm','mp4','mp3','m4a','vorbis')
        self.combo_extensions.current(2)
        self.combo_extensions.place(x=460, y=100, width=60, height=25)
        button_add_URLs = tk.Button(self, text = 'Add', command=self.add_video_to_treeview);
        button_add_URLs.place(x = 520, y = 100, width=50, height=25)
        label_download_list = tk.Label(self, text="Download list")
        label_download_list.place(x=10, y=140, width=73,height=25)
        self.treeview = ttk.Treeview(self)
        self.treeview['columns']=('video_title', 'video_extension', 'video_size', 'video_percent', 'video_ETA', 'video_speed', 'video_status')
        self.treeview.column("#0", width=0,  stretch='NO')
        self.treeview.column("video_title",anchor='center', width=80)
        self.treeview.column("video_extension",anchor='center',width=80)
        self.treeview.column("video_size",anchor='center',width=80)
        self.treeview.column("video_percent",anchor='center',width=80)
        self.treeview.column("video_ETA",anchor='center',width=80)
        self.treeview.column("video_speed",anchor='center',width=80)
        self.treeview.column("video_status",anchor='center',width=80)
        self.treeview.heading("#0",text="",anchor='center')
        self.treeview.heading("video_title",text="Title",anchor='center')
        self.treeview.heading("video_extension",text="Extension",anchor='center')
        self.treeview.heading("video_size",text="Size",anchor='center')
        self.treeview.heading("video_percent",text="Percent",anchor='center')
        self.treeview.heading("video_ETA",text="ETA",anchor='center')
        self.treeview.heading("video_speed",text="Speed",anchor='center')
        self.treeview.heading("video_status",text="Status",anchor='center')
        self.treeview.place(x = 10, y = 170, width= int(config.get('config', 'treeview-width', fallback=620)), height=400)
        self.delete_from_list_photo = tk.PhotoImage(file = r".\resources\free-trash-5179495-4319281.gif")
        self.delete_from_list_photo = self.delete_from_list_photo.subsample(7, 7) #resize Image size for the button
        button_delete_from_list = tk.Button(self, image = self.delete_from_list_photo, text = 'Delete selection', command=self.ask_what_to_delete)
        button_delete_from_list.place(x=10, y=580, width=40, height=40)
        self.stop_downloads_photo = tk.PhotoImage(file = r".\resources\free-stop-196-458554.gif")
        self.stop_downloads_photo = self.stop_downloads_photo.subsample(7, 7) #resize Image size for the button
        button_stop_download = tk.Button(self, image = self.stop_downloads_photo, text = 'Stop downloading', command=self.stop_downloads)
        button_stop_download.place(x=120, y=580, width=40, height=40)
        self.download_photo = tk.PhotoImage(file = r".\resources\free-cloud-download-3315711-2757661.gif")
        self.download_photo = self.download_photo.subsample(7, 7) #resize Image size for the button
        button_start_download = tk.Button(self, image = self.download_photo, text = 'Start downloading', command=self.treeview_2_params)
        button_start_download.place(x=240, y=580, width=40, height=40)
        self.check_components_update()

    def ask_folder(self):
        file_path = filedialog.askdirectory()
        if os.name == 'nt':
            file_path = file_path.replace("/", "\\")
        self.entry_destination_folder.delete(0, 'end')
        self.entry_destination_folder.insert(0, file_path)
        
    def validate_url(seld, string):
        return validators.url(string)
        
    def add_video_to_treeview(self):
        text = self.text_Urls_2_download.get('1.0', 'end').splitlines()
        for line in text:
            if self.validate_url(line):
                self.treeview.insert(parent='',index='end',text='',values=(line,self.combo_extensions.get(),'-','0%','-','-','Queued'))
        self.text_Urls_2_download.delete('1.0', 'end')
        return
    
    def check_our_update(self):
        return #Provisional. Right now not function as we are still developing the first version and we don't know where will be hosting the updates
    
    def check_components_update(self):
        #First check if components are in the path and if they are, check if we can update them
        #right now for testing will always be ready to update components
        ytdlp_folder = os.path.join('bin', 'yt-dlp.exe')
        if(not os.path.isfile(ytdlp_folder)):
            print("No yt-dlp.exe found!")  
            logging.warn("No yt-dlp.exe found!")
            self.button_download_components = tk.Button(self, text = 'Install Components', command=lambda: Thread(target=self.download_Ytdlp).start());
            self.button_download_components.place(x = 420, y = 55, height=25)
        else: #function that returns true or false to check if there are updates
            logging.info("checking if yt-dlp.exe is updated")
            config = configparser.ConfigParser()
            config.read('config.ini')
            new_version = self.check_last_Ytdlp_version()
            current_version = config.get('external.files', 'yt-dlp.version', fallback=None)
            if(new_version != current_version):
                logging.info(f"a new version of yt-dlp is avaliable: from {current_version} to {new_version}")
                self.button_download_components = tk.Button(self, text = 'Update Components', command=self.download_Ytdlp);
                self.button_download_components.place(x = 420, y = 55, height=25)
    
    def download_Ytdlp(self):
        url = ("https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe")
        self.button_download_components.config(text="Updating, please wait (1/3)")
        logging.info("Updating yt-dlp (1/3)")
        filename = os.path.join("bin", "yt-dlp.exe")
        with requests.get(url, stream=True) as response:
            with open(filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
        self.button_download_components.config(text="Updating, please wait (2/3)")
        logging.info("Updating yt-dlp (2/3)")
        url = ("https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip")
        filezip = os.path.join("bin", "ffmpeg-master-latest-win64-gpl.zip")
        with requests.get(url, stream=True) as response:
            with open(filezip, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
        self.button_download_components.config(text="Updating, please wait (3/3)")
        logging.info("Updating yt-dlp (3/3)")
        with zipfile.ZipFile(filezip, 'r') as zip_ref:
            content_zip = zip_ref.namelist()
            ffmpeg = "ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe"
            file_ff = os.path.join("bin", "tmp")
            ffplay = "ffmpeg-master-latest-win64-gpl/bin/ffplay.exe"
            if ffmpeg in content_zip:
                zip_ref.extract(ffmpeg, file_ff)
                new_location = os.path.join("bin","ffmpeg.exe")
                old_location = os.path.join("bin","tmp","ffmpeg-master-latest-win64-gpl","bin","ffmpeg.exe")
                shutil.move(old_location, new_location)
            if ffplay in content_zip:
                zip_ref.extract(ffplay, file_ff)   
                new_location = os.path.join("bin","ffplay.exe")
                old_location = os.path.join("bin","tmp","ffmpeg-master-latest-win64-gpl","bin","ffplay.exe")
                shutil.move(old_location, new_location)
        os.remove(filezip)
        if os.path.exists(file_ff):
            shutil.rmtree(file_ff)
        self.button_download_components.config(text="Updated", state="disabled")
        logging.info("Updating yt-dlp -> completed")
        last_version = self.check_last_Ytdlp_version()
        if last_version is not None:
            config = configparser.ConfigParser()
            config.read('config.ini')
            config.set('external.files', 'yt-dlp.version', last_version)
            with open('config.ini', 'w') as config_file:
                config.write(config_file)
    
    def check_last_Ytdlp_version(self):
        url = ("https://api.github.com/repos/yt-dlp/yt-dlp/tags")
        response = requests.get(url)
        if response.status_code == 200:
            tags = response.json()
            return tags[0]['name']
        else:
            print(f'Could not obtain tags from repo. Status code: {response.status_code}')
            logging.info(f'Could not obtain tags from repo. Status code: {response.status_code}')
            return None
        
    def ask_what_to_delete(self):
        toplevel = tk.Toplevel(self)
        toplevel.title("Which elements do you wish to delete?")

        label = tk.Label(toplevel, text="Which elements do you wish to delete?")
        toplevel.minsize(240,160)
        toplevel.attributes('-topmost', 'true')
        toplevel.grab_set()
        toplevel.resizable(False, False)
        label.place(relx=0.5, rely=0.2, anchor=tk.CENTER)
        all_button = tk.Button(toplevel, text="All", command=lambda: delete_elements("all"))
        all_button.place(x=80, y=70, anchor=tk.CENTER)
        
        completed_button = tk.Button(toplevel, text="Completed", command=lambda: delete_elements("completed"))
        completed_button.place(x=170, y=70, anchor=tk.CENTER)

        selected_button = tk.Button(toplevel, text="Only selected", command=lambda: delete_elements("selected"))
        selected_button.place(x=80, y=100, anchor=tk.CENTER)

        cancel_button = tk.Button(toplevel, text="Cancel", command=toplevel.destroy)
        cancel_button.place(x=170, y=100, anchor=tk.CENTER)
        
        def delete_elements(option):
            if option == "all":
                #self.treeview.delete(self.treeview.get_children())
                for i in self.treeview.get_children():
                    self.treeview.delete(i)
            elif option == "selected":
                try:
                    self.treeview.delete(self.treeview.selection())
                except:
                    print("No options available to delete")
            elif option == "completed":
                for i in self.treeview.get_children():
                    row = self.treeview.item(i)
                    if row['values'][6] == "Completed":
                        self.treeview.delete(i)
            toplevel.destroy()
    
    def stop_downloads(self):
        logging.info("Stopping processes")
        for proc in self.launched_threads:
            print(proc.pid)
            subprocess.call(['taskkill', '/F', '/T', '/PID',  str(proc.pid)])
        self.launched_threads = []
        for i in self.treeview.get_children():
            element = list(self.treeview.item(i, 'values'))
            if element[6] != "Completed":
                if element[6] != "Error":
                    element[6] = "Stopped"
                self.treeview.item(i, values=element)
        
    def find_in_treeview(self, element):
        index = 0
        for i in self.treeview.get_children():
            e = self.treeview.item(i, 'values')
            if e[0] == element:
                return index
            else:
                index = index + 1    
                

                
    def treeview_2_params(self):
        if len(self.treeview.get_children()) != 0:
            ytdlp_folder = os.path.join('bin', 'yt-dlp.exe')
            for i in self.treeview.get_children():
                params = []
                if self.treeview.item(i)['values'][1] == "mp4" or self.treeview.item(i)['values'][1] == "webm":
                    params.extend([ytdlp_folder, "-f", self.treeview.item(i)['values'][1], self.treeview.item(i)['values'][0]])
                else:
                    destination_audio = os.path.join(self.entry_destination_folder.get(), "%(title)s.%(ext)s")
                    params.extend([ytdlp_folder, "--extract-audio", "--audio-format",self.treeview.item(i)['values'][1], "-o", destination_audio, "--audio-quality", "0", "--ffmpeg-location", os.path.join('bin', 'ffmpeg.exe'), self.treeview.item(i)['values'][0]])
                self.all_params.append(params)
            self.all_params.reverse()
            self.launch_threads()
        else:
            print("there's nothing to download!")
        return
    
    def launch_threads(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        max_concurrent_threads = int(config.get('config', 'max-paralell-downloads', fallback=None))
        threads = 0
        if len(self.all_params) != 0:
            if(len(self.all_params) >= max_concurrent_threads):
                for i in range(max_concurrent_threads):
                    next_launch = self.all_params.pop()
                    self.total_threads += 1
                    t = threading.Thread(target=lambda: self.start_download(next_launch))
                    t.start()
                    time.sleep(1) #idk why, but if we not wait, sometimes pop() doesnt work and weird things happen...
            else:
                to_launch = self.all_params
                self.all_params = []
                for param in to_launch:
                    self.total_threads += 1
                    t = threading.Thread(target=lambda: self.start_download(param))
                    t.start()
                    time.sleep(1) #idk why, but if we not wait, sometimes pop() doesnt work and weird things happen...

    def control_total_threads(self):    
        if self.total_threads <= 0:
            self.launch_threads()
            
    def start_download(self, param):
        url = ""
        if len(param) >= 10:
            url = param[10]
        else:
            url = param[3]
        print(f"Starting download: {url}")
        try:
            ytdlp_process = subprocess.Popen(param, stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True)
            self.launched_threads.append(ytdlp_process)
            logging.info(f"Starting download: {url}")
            for line in ytdlp_process.stdout:
                if "[download]" in line and "Destination" not in line and "has already been downloaded" not in line:
                    index = self.find_in_treeview(url)
                    row = self.treeview.item(self.treeview.get_children()[index])
                    row['values'] = list(row['values'])
                    row['values'][3] = line[line.index("]") + 1: line.index("of") -2].strip() + "%"
                    if "in" in line:
                        row['values'][2] = line[line.index("of") + 2: line.index("in") -1].strip()
                    else:
                        row['values'][2] = line[line.index("of") + 2: line.index("at") -1].strip()
                    if "ETA" in line:
                        row['values'][4] = line[line.index("ETA") + 3].strip()
                        row['values'][5] = line[line.index("at") + 2: line.index("ETA") -2].strip()
                    else:
                        row['values'][4] = "Unknown"
                        row['values'][5] = "Unknown"
                        row['values'][6] = "Downloading"
                    self.treeview.item(self.treeview.get_children()[index], values=row['values'])
                if "[ExtractAudio]" in line and "Destination" in line:
                    index = self.find_in_treeview(url)
                    row = self.treeview.item(self.treeview.get_children()[index])
                    row['values'] = list(row['values'])
                    row['values'][6] = "Converting"
                    self.treeview.item(self.treeview.get_children()[index], values=row['values'])
            for line in ytdlp_process.stderr:
                print(line)
                logging.error(line)
                index = self.find_in_treeview(url)
                row = self.treeview.item(self.treeview.get_children()[index])
                row['values'][6] = "Error"
                self.treeview.item(self.treeview.get_children()[index], values=row['values'])
            ytdlp_process.communicate()
        finally:
            print(f"{url} has finished")
            logging.info(f"{url} has finished")
            index = self.find_in_treeview(url)
            row = self.treeview.item(self.treeview.get_children()[index])
            row['values'] = list(row['values'])
            row['values'][2] = "100%"
            row['values'][4] = "-"
            row['values'][5] = "-"
            if row['values'][6] != "Stopped":
                if row['values'][6] != "Error":
                    row['values'][6] = "Completed"
            self.treeview.item(self.treeview.get_children()[index], values=row['values'])
            self.total_threads = self.total_threads - 1
            self.control_total_threads()
        return
    
    

        
#Agradecimientos:
#https://iconscout.com/free-icon/folder-1166

#https://stackoverflow.com/questions/52121950/tkinter-buttons-not-functioning-or-showing-image-when-placed-in-window
#https://pythonguides.com/python-tkinter-table-tutorial/
#https://stackoverflow.com/questions/17746817/how-to-read-the-inputline-by-line-from-a-multiline-tkinter-textbox-in-python

def read_config():
    if(os.path.isfile("config.ini")):
        print("config.ini detected")
        logging.info('Config file detected')
    else:
        logging.warning('No config file')
        print("No config file, so we create one with default values")
        config = configparser.ConfigParser()
        config['external.files'] = {
            'yt-dlp.version': ''
        }
        config['config'] = {
            'max-paralell-downloads': '3',
            'min-size-height' : '720',
            'min-size-width' : '1280',
            'max-size-height' : '1600',
            'max-size-width' : '2560',
            'treeview-width' : '650'
        }
        with open(os.path.join("config.ini"), 'w') as configfile:
            config.write(configfile)
            
    

if __name__=='__main__':
    root = tk.Tk()
    mainview = MainView(root)
    mainview.place(x=0, y=0, height=2560, width=1600)
    read_config()
    config = configparser.ConfigParser()
    config.read('config.ini')
    max_concurrent_threads = int(config.get('config', 'max-paralell-downloads', fallback=None))
    root.minsize(int(config.get('config', 'min-size-width', fallback=1280)),int(config.get('config', 'min-size-height', fallback=720)))
    root.maxsize(int(config.get('config', 'max-size-width', fallback=2560)),int(config.get('config', 'max-size-height', fallback=1600)))
    root.title("Youtube-dlp-gui main menu")
    root.mainloop()