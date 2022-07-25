# -*- coding=utf-8 -*-

import time

print("I: Starting GenshinOfflineUpdater on " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

import argparse
import zipfile
import os
import util
import sentry_sdk
import distutils
import glob
from sys import exit

# Pre-check requirements
if not os.path.exists("hpatchz.exe"):
    print("E: hpatchz not found.")
    print("Go to https://github.com/sisong/HDiffPatch/releases/latest to download it"
          "or get it from the game launcher folder.")
    exit(1)
if not os.name == "nt":
    print("E: This script is only for Windows.")
    print("Running Genshin on Linux/Mac? Sounds awesome. Then try running this script inside Wine.")
    exit(1)

# Parse arguments
parser = argparse.ArgumentParser(description="A Genshin Offline Updater for convenient use.")
parser.add_argument('-p', '--patch', type=str, help='new version patch file', required=True)
parser.add_argument('-g', '--game', type=str, help='game installation path', required=True)
parser.add_argument('-f', '--force', action='store_true', help='Ignore warnings and force update')
parser.add_argument('--disable-sentry', action='store_true', help='Disable Sentry error reporting')
args = parser.parse_args()
game_path = args.game
patch_file = args.patch
force_enable = args.force
sentry_enable = not args.disable_sentry

if sentry_enable:
    print("I: We use Sentry to report errors. You can disable it by using --disable-sentry.")
    print("I: By continuing, you agree to Sentry's Terms of Service and Privacy Policy.")
    sentry_sdk.init(
        dsn="https://514b66ac611c492693100f1e6bf38724@o1123722.ingest.sentry.io/6597606",
        traces_sample_rate=1.0
    )
else:
    print("I: Sentry is disabled during this operation.")

# Check game status
# Check if game exists
if not os.path.exists(game_path) and not os.path.exists(game_path + '\\' + 'GenshinImpact.exe') \
        and not os.path.exists(game_path + '\\' + 'YuanShen.exe'):
    print("E: Game not found.")
    if os.path.exists(game_path + '\\' + 'launcher.exe'):
        print("Note: DO NOT SPECIFY THE LAUNCHER FOLDER.\n"
              "Usually the subfolder \"Genshin Impact game\" is the actual game folder.")
    exit(1)
# Check if game is running
if os.system("tasklist | findstr GenshinImpact.exe") == 0 or os.system("tasklist | findstr YuanShen.exe") == 0:
    print("E: Game is running.")
    print("Note: We can't check whether the game to update is the one you're playing.\n"
          "So if you have multiple games please close them all before updating.")
    exit(1)

# Unzip the patch file
patch_root = game_path + '\\' + 'patch'
with zipfile.ZipFile(patch_file, "r") as archive:
    try:
        print("I: Extracting patch file, this may take a while...")
        archive.extractall(path=patch_root)
    except zipfile.BadZipfile:
        print("E: Invalid patch file. Please check your file and try again.")
        exit(1)

# Pre-check patch files
# game_build = 1 -> CN
# game_build = 2 -> OS
convert = False  # We assume that no need to convert
if not (os.path.exists(game_path + '\\' + 'YuanShen.exe') and os.path.exists(game_path + '\\' + 'GenshinImpact.exe')):
    if os.path.exists(game_path + '\\' + 'YuanShen.exe') and os.path.exists(patch_root + '\\' + 'GenshinImpact.exe'):
        print("W: You're updating CN build with OS patch. Unexpected behavior may occur after upgrade.")
        if not force_enable:
            print("You can use -f option to force update but it's not recommended.")
            util.cleanup(patch_root)
            exit(1)
        else:
            print("I: Continuing...")
            game_build = 1
            convert = True

    elif os.path.exists(game_path + '\\' + 'GenshinImpact.exe') and os.path.exists(patch_root + '\\' + 'YuanShen.exe'):
        print("W: You're updating OS build with CN patch. Unexpected behavior may occur after upgrade.")
        if not force_enable:
            print("You can use -f option to force update but it's not recommended.")
            util.cleanup(patch_root)
            exit(1)
        else:
            print("I: Continuing...")
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
    print("I: Seems like you install both versions in one folder...")
    print("I: Then it's your duty to check whether you're updating the right version...")
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
    print("F: Internal error: game_build is not properly set.")
    util.cleanup(patch_root)
    raise SyntaxError()

# Rename the patch files if converting is needed
if convert:
    util.convert(game_build, patch_root)

# Check game and patch version
try:
    with open(game_path + '\\' + game_name + '_Data' + '\\' + 'Persistent' + '\\' + 'ScriptVersion', 'r') as f:
        game_version = f.read()
except:
    print("W: Oops, we can't find the game version.\n"
          "We can still update for you, but you should check the version to avoid errors after updating.")
# try:
#    with open(patch_root + '\\' + game_name + '_Data' + '\\' + 'Persistent' + '\\' + 'ScriptVersion', 'r') as f:
#        patch_version = f.read()
# except:
#    print("W: Oops, we can't find the patch version.\n"
#          "We can still update for you, but you should check the version to avoid errors after updating.")

print("I: Base Game version: " + game_version)
# print("I: Patch version: " + patch_version)  # Patches don't have Persistent folder
print("I: Please check if the version is correct.")
a = input("Continue? (y/N)")
if a != 'y' and a != 'Y':
    print("E: Aborted.")
    util.cleanup(patch_root)
    exit(1)

# Delete the old game files
files2del = open(patch_root + '\\' + "deletefiles.txt", "r").readlines()
count = len(files2del)
for i in range(count):
    files2del[i] = files2del[i].strip()
    if os.path.exists(game_path + '\\' + files2del[i]):
        os.remove(game_path + '\\' + files2del[i])
        print("I: Deleted: " + files2del[i])
    else:
        print("W: Not found: " + files2del[i] + ". Skipping...")

# Copy the new game files and replace the old ones
print("I: Copying files, this may take a while...")
distutils.dir_util.copy_tree(patch_root, game_path)
print("I: New files copied.")

# patch some files
# Find the .hdiff files and use hpatchz to patch them
hdiff_files = glob.glob(game_path + '\\' + '**' + '\\' + '*.hdiff', recursive=True)
for hdiff_file in hdiff_files:
    orig_file = hdiff_file.replace('.hdiff', '')
    print("I: Patching: " + orig_file)
    os.system("hpatchz.exe -f " + orig_file + " " + hdiff_file + " " + orig_file)

# Delete the patch files
print("I: Almost done. Cleaning up...")
util.delhdiff(game_path)
util.cleanup(patch_root)
os.remove(game_path + '\\' + 'deletefiles.txt')
os.remove(game_path + '\\' + 'hdifffiles.txt')

print("Finished!")
