# -*- coding=utf-8 -*-

import os
import urllib3
import zipfile
import tkinter as tk
from tkinter import messagebox
import json

# Check latest version on GitHub
def get_latest_version():
    http = urllib3.PoolManager()
    r = http.request('GET', 'https://api.github.com/repos/MomokkoW/GenshinOfflineUpdater/releases/latest')
    if r.status == 200:
        return r.data.decode('utf-8')
    else:
        tk.messagebox.showerror('Error', 'Failed to get latest version from GitHub.')
        exit(1)
root = tk.Tk()
root.withdraw()
root.iconbitmap(r'icon_tk.ico')
latest_ver = json.loads(get_latest_version())['tag_name']
latest_name = json.loads(get_latest_version())['name']
latest_body = json.loads(get_latest_version())['body']
latest_link = json.loads(get_latest_version())['assets'][0]['browser_download_url']
with open('VERSION', 'r') as f:
    current_ver = f.read()
if latest_ver == current_ver:
    tk.messagebox.showinfo('Info', 'You have the latest version.')
    exit(0)
else:
    if tk.messagebox.askokcancel('Info', 'There is a new version available.\n'
                                         + latest_name + '\n' + latest_body + '\n' +
                                         'Do you want to update?'):
        pass
    else:
        exit(0)
# Download the latest version
http = urllib3.PoolManager()
r = http.request('GET', latest_link)
if r.status == 200:
    with open('update.zip', 'wb') as f:
        f.write(r.data)
    with zipfile.ZipFile('update.zip', 'r') as zip_ref:
        zip_ref.extractall('.')
    os.remove('update.zip')
    tk.messagebox.showinfo('Info', 'Update finished.')
    exit(0)
else:
    tk.messagebox.showerror('Error', 'Failed to download latest version.')
    exit(1)
