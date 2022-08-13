@echo off
pipenv run pyuic5 genshinupd.ui -o ..\qtmainui.py
pipenv run pyuic5 updatescreen.ui -o ..\qtupdatescreen.py
pipenv run pyrcc5.exe mhygsuibase.qrc -o ..\mhygsuibase_rc.py