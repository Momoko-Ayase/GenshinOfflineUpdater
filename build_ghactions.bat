@echo off
del /f /s /q .\dist\*.*
pyinstaller --clean --onedir --icon=icon.ico --name=genshinupd genshinupd.py util.py
pyinstaller --clean --onedir --icon=icon.ico --noconsole --name=genshinupd_gui genshinupd_gui.py util.py qtmainui.py qtupdatescreen.py mhygsuibase_rc.py
xcopy .\dist\genshinupd\* .\dist /y /q /s /h
xcopy .\dist\genshinupd_gui\* .\dist /y /q /s /h
copy .\hpatchz.exe .\dist /y
copy .\icon.ico .\dist /y
copy .\icon_tk.ico .\dist /y
rmdir /s /q .\dist\genshinupd
rmdir /s /q .\dist\genshinupd_gui
