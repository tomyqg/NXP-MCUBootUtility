pyinstaller.exe pyinstaller_pack.spec
copy .\dist\nxpSecBoot.exe ..\bin
rd /q /s .\build
rd /q /s .\dist