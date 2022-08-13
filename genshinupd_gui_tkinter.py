# -*- coding=utf-8 -*-

print("UNFINISHED CURRENTLY")
print("DO NOT USE IT. USE genshinupd_gui.py INSTEAD.")
exit(0)



import time
import tkinter
from tkinter import *
from tkinter import messagebox
from tkinter import font
from tkinter.ttk import *
import argparse
import zipfile
import os
import util
import sentry_sdk
from distutils.dir_util import copy_tree
import glob
from sys import exit

parser = argparse.ArgumentParser()
parser.add_argument('--disable-sentry', action='store_true', help='Disable Sentry error reporting')
args = parser.parse_args()
sentry_enable = not args.disable_sentry

if sentry_enable:
    sentry_sdk.init(
        dsn="https://514b66ac611c492693100f1e6bf38724@o1123722.ingest.sentry.io/6597606",
        traces_sample_rate=1.0
    )

# Draw the GUI
root = Tk()
root.title("GenshinOfflineUpdater")
width = 800
height = 300
root.geometry(f'{width}x{height}')
screen_width = root.winfo_screenwidth() / 2 - width / 2
screen_height = root.winfo_screenheight() / 2 - height / 2
root.geometry(f"+{int(screen_width)}+{int(screen_height)}")
root.resizable(False, False)
root.iconbitmap(r'icon.ico')
label = Label(root, text="GenshinOfflineUpdater", font=("SDK_SC_Web", 20))
label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
label = Label(root, text="Game Folder Path:", font=("SDK_SC_Web", 12))
label.grid(row=1, column=0, padx=15, pady=10, sticky=W)
game_path = StringVar()
entry = Entry(root, textvariable=game_path, width=34)
entry.grid(row=1, column=1, sticky=W, padx=20, pady=10)
label = Label(root, text="Patch File Path:", font=("SDK_SC_Web", 12))
label.grid(row=2, column=0, padx=15, pady=10, sticky=W)
patch_file = StringVar()
entry = Entry(root, textvariable=patch_file, width=34)
entry.grid(row=2, column=1, sticky=W, padx=20, pady=10)
label = Label(root, text="Force Update:", font=("SDK_SC_Web", 12))
label.grid(row=3, column=0, padx=15, pady=10, sticky=W)
force_enable = BooleanVar()
checkbutton = Checkbutton(root, variable=force_enable)
checkbutton.grid(row=3, column=1, sticky=W, padx=20, pady=10)
button = Button(root, text="Update", command=lambda: update(game_path.get(), patch_file.get(), force_enable.get()))
button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
progress_bar = Progressbar(root, orient=HORIZONTAL, length=425, mode='determinate')
progress_bar.grid(row=6, column=0, columnspan=2, padx=20, pady=10, sticky=W)
label = Label(root, text="Log Viewer", font=("SDK_SC_Web", 12))
label.grid(row=0, column=2, padx=15, pady=10, sticky=W)
log_text = Text(root, width=38, height=16, font=("SDK_SC_Web", 8))
log_text.grid(row=1, column=2, rowspan=10, padx=10, sticky=W)


start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
log_text.insert(END, f"I: Starting GenshinOfflineUpdater GUI on {start_time}\n")

# Pre-check requirements
log_text.insert(END, "I: Checking requirements...\n")
if not os.path.exists("hpatchz.exe"):
    log_text.insert(END, "E: hpatchz not found.\n")
    tkinter.messagebox.showerror("Error", "hpatchz not found.\n"
                                          "Go to https://github.com/sisong/HDiffPatch/releases/latest to download it"
                                          "or get it from the game launcher folder.")
    exit(1)
if not os.name == "nt":
    log_text.insert(END, "E: This script is only for Windows.\n")
    tkinter.messagebox.showerror("Error", "This script is only for Windows.\n"
                                          "Running Genshin on Linux/Mac? Sounds awesome. "
                                          "Then try running this script inside Wine.")
    exit(1)
log_text.insert(END, "I: Ready.\n")


def update(game_path, patch_file, force_enable):
    if sentry_enable:
        tkinter.messagebox.showinfo("Info",
                                    "We use Sentry to report errors. You can disable it by using --disable-sentry.\n"
                                    "By continuing, you agree to Sentry's Terms of Service and Privacy Policy.")
    log_text.insert(END, "--------------------------------------------------\n")
    log_text.insert(END, f"I: Game path:{game_path}\n")
    log_text.insert(END, f"I: Patch file:{patch_file}\n")
    log_text.insert(END, "I: Checking before update...\n")
    # Check game status
    if not os.path.exists(game_path) and not os.path.exists(game_path + '\\' + 'GenshinImpact.exe') \
            and not os.path.exists(game_path + '\\' + 'YuanShen.exe'):
        log_text.insert(END, "E: Game not found.\n")
        if os.path.exists(game_path + '\\' + 'launcher.exe'):
            tkinter.messagebox.showerror("Error", "Game not found.\n"
                                                  "Note: DO NOT SPECIFY THE LAUNCHER FOLDER.\n"
                                                  "Usually the subfolder \"Genshin Impact game\" "
                                                  "is the actual game folder.")
        else:
            tkinter.messagebox.showerror("Error", "Game not found.")


root.mainloop()

