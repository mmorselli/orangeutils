$pythonVersion = "3.12.1"
$pythonUrl = "https://www.python.org/ftp/python/$pythonVersion/python-$pythonVersion-amd64.exe"
$curDir = Get-Location
$pythonDownloadPath = Join-Path -Path $curDir -ChildPath "python-$pythonVersion-amd64.exe"
$pythonInstallDir = Join-Path -Path $curDir -ChildPath "Python"


# Create the directories if they do not exist
if (!(Test-Path -Path $pythonInstallDir)) { New-Item -ItemType Directory -Path $pythonInstallDir }

Write-Host "Installing Python $pythonVersion..."

(New-Object Net.WebClient).DownloadFile($pythonUrl, $pythonDownloadPath)
& Start-Process -FilePath $pythonDownloadPath -ArgumentList "/install /passive InstallAllUsers=1 PrependPath=1 Include_test=0 TargetDir=$pythonInstallDir" -Wait

Write-Host "Installing/updating pip..."

# update pip
Start-Process -FilePath "$pythonInstallDir\python.exe" -ArgumentList "-m pip install --upgrade pip" -Wait

Write-Host "Installing Dependencies..."

$requirementsPath = Join-Path -Path $curDir -ChildPath "requirements.txt"
Start-Process -FilePath "$pythonInstallDir\python.exe" -ArgumentList "-m pip install -r $requirementsPath" -Wait