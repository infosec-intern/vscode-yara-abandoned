$Location = Split-Path -parent $PSCommandPath
$PythonEnv = "$Location\env"
$Pip = "$PythonEnv\Scripts\pip.exe"
$Requirements = "yara-python"

# Set-Variable INCLUDE="C:\Program Files (x86)\Windows Kits\10\Include"
py -3 -m venv $PythonEnv
& "$Pip install $Requirements"
