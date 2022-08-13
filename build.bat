@echo off
del /f /s /q .\dist\*.*
pipenv run pyinstaller --clean --onefile --icon=icon.ico --name=genshinupd genshinupd.py util.py
pipenv run pyinstaller --clean --onefile --icon=icon.ico --noconsole --name=genshinupd_gui genshinupd_gui.py util.py qtmainui.py qtupdatescreen.py mhygsuibase_rc.py
copy .\hpatchz.exe .\dist /Y