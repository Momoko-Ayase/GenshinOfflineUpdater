@echo off
pipenv run pyinstaller --clean --onefile --icon=icon.ico --name=genshinupd genshinupd.py util.py
copy .\hpatchz.exe .\dist /Y