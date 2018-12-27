pyinstaller.exe pyinstaller_pack_f.spec
copy .\dist\NXPMcuUtilityBoot.exe ..\bin
rd /q /s .\build
rd /q /s .\dist