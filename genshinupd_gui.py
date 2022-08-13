# -*- coding=utf-8 -*-

import threading
import time
from PyQt5 import QtCore, QtGui, QtWidgets
import qtmainui
import qtupdatescreen
import argparse
import zipfile
import os
import sys
import util
import sentry_sdk
from distutils.dir_util import copy_tree
import glob
from sys import exit
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from win10toast import ToastNotifier

parser = argparse.ArgumentParser()
parser.add_argument('--disable-sentry', action='store_true', help='Disable Sentry error reporting')
args = parser.parse_args()
sentry_enable = not args.disable_sentry
root = tk.Tk()
root.withdraw()
root.iconbitmap(r'icon_tk.ico')  # The default icon looks weird with Tkinter.
if sentry_enable:
    tk.messagebox.showinfo("Info",
                           "We use Sentry to report errors. You can disable it by using --disable-sentry.\n"
                           "By continuing, you agree to Sentry's Terms of Service and Privacy Policy.")
    sentry_sdk.init(
        dsn="https://514b66ac611c492693100f1e6bf38724@o1123722.ingest.sentry.io/6597606",
        traces_sample_rate=1.0
    )

# Pre-check requirements
if not os.path.exists("hpatchz.exe"):
    tk.messagebox.showerror("Error", "hpatchz not found.\n"
                                     "Go to https://github.com/sisong/HDiffPatch/releases/latest to download it"
                                     "or get it from the game launcher folder.")
    exit(1)
if not os.name == "nt":
    tk.messagebox.showerror("Error", "This script is only for Windows.\n"
                                     "Running Genshin on Linux/Mac? Sounds awesome. "
                                     "Then try running this script inside Wine.")
    exit(1)


# Check whether run in administrator mode
# if not ctypes.windll.shell32.IsUserAnAdmin():
#     tk.messagebox.showinfo("Warning", "This script needs administrator permission to function properly.\n"
#                                       "Otherwise it may encounter problems during update.\n"
#                                       "We strongly recommend running this script as administrator.")

# Define functions

def appexit():
    exit(0)


def gameselect():
    gamepathorig = filedialog.askdirectory()
    ui.game_path.setText(gamepathorig.replace("/", "\\"))


def patchselect():
    patchfileorig = filedialog.askopenfilename()
    ui.patch_file.setText(patchfileorig.replace("/", "\\"))


def fallback():
    window.close()
    ui = qtmainui.Ui_MainWindow()
    ui.setupUi(window)
    window.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)
    window.setWindowIcon(QtGui.QIcon('icon.ico'))
    window.show()
    QtWidgets.QApplication.processEvents()
    ui.exit.clicked.connect(appexit)
    ui.gameselect.clicked.connect(gameselect)
    ui.patchselect.clicked.connect(patchselect)
    ui.start.clicked.connect(lambda: update(ui.game_path.text(), ui.patch_file.text(), ui.enableforce.isChecked()))


def update(game_path, patch_file, force_enable):
    try:
        # Check game status
        # Check if game exists
        if game_path == "" or patch_file == "":
            tk.messagebox.showerror("Error", "Please specify game path and patch file.")
            return
        if not os.path.exists(game_path) and not os.path.exists(game_path + '\\' + 'GenshinImpact.exe') \
                and not os.path.exists(game_path + '\\' + 'YuanShen.exe'):
            tk.messagebox.showerror("Error", "Game not found.")
            if os.path.exists(game_path + '\\' + 'launcher.exe'):
                tk.messagebox.showinfo("Info", "Note: DO NOT SPECIFY THE LAUNCHER FOLDER.\n"
                                               "Usually the subfolder \"Genshin Impact game\" "
                                               "is the actual game folder.")
            return
        # Check if game is running
        if os.system("tasklist | findstr GenshinImpact.exe") == 0 or os.system("tasklist | findstr YuanShen.exe") == 0:
            tk.messagebox.showerror("Error", "Game is running.\n"
                                             "Please close the game and try again.\n"
                                             "Note: We can't check whether the game to update is the one you're playing.\n"
                                             "So if you have multiple games please close them all before updating.")
            return
        window.close()
        updui = qtupdatescreen.Ui_Form()
        updui.setupUi(window)
        updui.progress.setStyleSheet("border-image: url(:/progress/element1.png);")
        updui.logview.setText("I: Starting GenshinOfflineUpdater on " +
                              time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        window.show()
        QtWidgets.QApplication.processEvents()
        time.sleep(1)  # Wait for a short while, don't be anxious:)
        # Unzip the patch file
        patch_root = game_path + '\\' + 'patch'
        try:
            with zipfile.ZipFile(patch_file, "r") as archive:
                try:
                    updui.progress.setStyleSheet("border-image: url(:/progress/element2.png);")
                    updui.logview.setText("I: Extracting patch file, this may take a while...")
                    QtWidgets.QApplication.processEvents()
                    archive.extractall(path=patch_root)
                except zipfile.BadZipfile:
                    tk.messagebox.showerror("E: Invalid patch file. Please check your file and try again.")
                    fallback()
        except FileNotFoundError:
            tk.messagebox.showerror("E: Patch file not found.")
            fallback()
        # Pre-check patch files
        # game_build = 1 -> CN
        # game_build = 2 -> OS
        updui.progress.setStyleSheet("border-image: url(:/progress/element3.png);")
        QtWidgets.QApplication.processEvents()
        convert = False  # We assume that no need to convert
        if not (os.path.exists(game_path + '\\' + 'YuanShen.exe') and os.path.exists(
                game_path + '\\' + 'GenshinImpact.exe')):
            if os.path.exists(game_path + '\\' + 'YuanShen.exe') and os.path.exists(
                    patch_root + '\\' + 'GenshinImpact.exe'):
                if not force_enable:
                    tk.messagebox.showinfo("Warning",
                                           "You're updating CN build with OS patch. Unexpected behavior may occur "
                                           "after upgrade.\n"
                                           "You can enable force update but it's not recommended.")
                    util.cleanup(patch_root)
                    fallback()
                else:
                    updui.logview.setText("W: You're updating CN build with OS patch. Unexpected behavior may occur "
                                          "after upgrade.")
                    game_build = 1
                    convert = True
            elif os.path.exists(game_path + '\\' + 'GenshinImpact.exe') and os.path.exists(
                    patch_root + '\\' + 'YuanShen.exe'):
                if not force_enable:
                    tk.messagebox.showinfo("Warning",
                                           "You're updating OS build with CN patch. Unexpected behavior may occur "
                                           "after upgrade.\n"
                                           "You can enable force update but it's not recommended.")
                    util.cleanup(patch_root)
                    fallback()
                else:
                    updui.logview.setText("W: You're updating OS build with CN patch. Unexpected behavior may occur "
                                          "after upgrade.")
                    game_build = 2
                    convert = True
            else:
                if os.path.exists(patch_root + '\\' + 'YuanShen.exe'):
                    game_build = 1
                    convert = False
                if os.path.exists(patch_root + '\\' + 'GenshinImpact.exe'):
                    game_build = 2
                    convert = False
        else:
            tk.messagebox.showinfo("Info", "Seems like you install both versions in one folder...\n"
                                           "Then it's your duty to check whether you're updating the right version...")
            if os.path.exists(patch_root + '\\' + 'YuanShen.exe'):
                game_build = 1
                convert = False
            if os.path.exists(patch_root + '\\' + 'GenshinImpact.exe'):
                game_build = 2
                convert = False
        try:
            if game_build == 1:
                game_name = 'YuanShen'
            elif game_build == 2:
                game_name = 'GenshinImpact'
        except SyntaxError:  # Clean up before throwing error
            tk.messagebox.showerror("F: Internal error: game_build is not properly set.")
            util.cleanup(patch_root)
            raise SyntaxError()
        # Rename the patch files if converting is needed
        if convert:
            util.convert(game_build, patch_root)
        # Check version function is not available now.
        # If you get a solution, please let me know.
        # Delete the old game files
        updui.progress.setStyleSheet("border-image: url(:/progress/element4.png);")
        QtWidgets.QApplication.processEvents()
        files2del = open(patch_root + '\\' + "deletefiles.txt", "r").readlines()
        count = len(files2del)
        for i in range(count):
            files2del[i] = files2del[i].strip()
            if os.path.exists(game_path + '\\' + files2del[i]):
                os.remove(game_path + '\\' + files2del[i])
                updui.logview.setText("I: Deleted: " + files2del[i] + "( " + str(i + 1) + "/" + str(count) + " )")
                QtWidgets.QApplication.processEvents()
            else:
                updui.logview.setText("W: Not found: " + files2del[i] + ". Skipping..." +
                                      "( " + str(i + 1) + "/" + str(count) + " )")
                QtWidgets.QApplication.processEvents()
        # Copy the new game files and replace the old ones
        updui.progress.setStyleSheet("border-image: url(:/progress/element5.png);")
        updui.logview.setText("I: Copying files, this may take a while...")
        QtWidgets.QApplication.processEvents()
        try:
            copy_tree(patch_root, game_path)
        except Exception as ExceptionInfo:
            if str(ExceptionInfo).find("PermissionError"):
                tk.messagebox.showerror("Error", str(ExceptionInfo) + "\n"
                                                                      "Please manually delete target file and try again.")
                util.cleanup(patch_root)
                fallback()

        # patch some files
        # Find the .hdiff files and use hpatchz to patch them
        updui.progress.setStyleSheet("border-image: url(:/progress/element6.png);")
        QtWidgets.QApplication.processEvents()
        hdiff_files = glob.glob(game_path + '\\' + '**' + '\\' + '*.hdiff', recursive=True)
        for hdiff_file in hdiff_files:
            orig_file = hdiff_file.replace('.hdiff', '')
            print("I: Patching: " + orig_file +
                  "( " + str(hdiff_files.index(hdiff_file) + 1) + "/" + str(len(hdiff_files)) + " )")
            QtWidgets.QApplication.processEvents()
            os.system("hpatchz.exe -f " + orig_file + " " + hdiff_file + " " + orig_file)
        # Delete the patch files
        updui.progress.setStyleSheet("border-image: url(:/progress/element7.png);")
        updui.logview.setText("I: Almost done. Cleaning up...")
        QtWidgets.QApplication.processEvents()
        util.delhdiff(game_path)
        util.cleanup(patch_root)
        os.remove(game_path + '\\' + 'deletefiles.txt')
        try:
            os.remove(game_path + '\\' + 'hdifffiles.txt')
        except FileNotFoundError:
            pass  # Old version of the game patch doesn't have this file
        updui.progress.setStyleSheet("border-image: url(:/progress/element8.png);")
        updui.logview.setText("I: Done.")
        QtWidgets.QApplication.processEvents()
        # Check whether window is activated
        if window.isActiveWindow():
            tk.messagebox.showinfo("Success", "Update finished, enjoy your journey in Teyvat!")
        else:
            try:
                toaster = ToastNotifier()
                toaster.show_toast("Success - GenshinOfflineUpdater", "Update finished, enjoy your journey in Teyvat!",
                                   icon_path="icon.ico", duration=10)
            except:
                pass
        exit(0)
    except Exception as ExceptionInfo:
        tk.messagebox.showerror("Error", str(ExceptionInfo) + "\n"
                                                              "Please send a issue to GitHub.")
        patch_root = game_path + '\\' + 'patch'
        if os.path.exists(patch_root):
            util.cleanup(patch_root)
        fallback()



# Draw UI
app = QtWidgets.QApplication([])
window = QtWidgets.QMainWindow()
ui = qtmainui.Ui_MainWindow()
ui.setupUi(window)
window.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)
window.setWindowIcon(QtGui.QIcon('icon.ico'))
window.show()
QtWidgets.QApplication.processEvents()
ui.exit.clicked.connect(appexit)
ui.gameselect.clicked.connect(gameselect)
ui.patchselect.clicked.connect(patchselect)
ui.start.clicked.connect(lambda: update(ui.game_path.text(), ui.patch_file.text(), ui.enableforce.isChecked()))
sys.exit(app.exec_())
