# -*- coding=utf-8 -*-
import glob
import os


def cleanup(patch_root):
    print("I: Cleaning up...")
    if os.path.exists(patch_root):
        os.system("rmdir /s /q " + patch_root)
    print("I: Cleanup finished.")


def delhdiff(game_path):
    hdiff_files = glob.glob(game_path + '\\' + '*' + '\\' + '*.hdiff', recursive=True)
    for hdiff_file in hdiff_files:
        os.remove(hdiff_file)


def convert(game_build, patch_root):
    if game_build == 1:
        os.rename(patch_root + '\\' + 'GenshinImpact.exe', patch_root + '\\' + 'YuanShen.exe')
        os.rename(patch_root + '\\' + 'GenshinImpact_Data', patch_root + '\\' + 'YuanShen_Data')
    else:
        os.rename(patch_root + '\\' + 'YuanShen.exe', patch_root + '\\' + 'GenshinImpact.exe')
        os.rename(patch_root + '\\' + 'YuanShen_Data', patch_root + '\\' + 'GenshinImpact_Data')
    print("I: Conversion finished.")
