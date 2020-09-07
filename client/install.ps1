<#
    Check Python version and create a virtual environment

    ./install.ps1 <TargetDir>
#>
[CmdletBinding()]
param (
    [Parameter(Position=1)]
    [String]
    $TargetDir
)

<#
    Build a virtual environment with the necessary packages with the provided Python path
    Requires path to python executable to validate
#>
function Invoke-BuildVenv ($TargetDir, $SystemPython) {
    $EnvPath = Join-Path -Path ${TargetDir} -ChildPath "env"
    Write-Verbose "Building virtual environment in ${EnvPath}"
    # python3 -m venv /tmp/vscode-yara/env
    Invoke-Expression "${SystemPython} -m venv ${EnvPath}"
    if (Test-Path -Path "${EnvPath}\Scripts" -PathType Container) {
        Write-Verbose "Virtual environment creation successful"
        $EnvPip = "${EnvPath}\Scripts\pip.exe"
        Write-Verbose "Using ${EnvPip} to install yarals package and dependencies"
        # use wheel package to install
        Invoke-Expression "${EnvPip} install wheel --disable-pip-version-check"
        $PkgPath = Join-Path -Path "${PSScriptRoot}" -ChildPath "..\server"
        Invoke-Expression "${EnvPip} wheel ${PkgPath} --disable-pip-version-check --no-deps --wheel-dir ${EnvPath}"
        $Wheel = (Resolve-Path "${EnvPath}/yarals-*.whl").Path
        Invoke-Expression "${EnvPip} install ${Wheel} --disable-pip-version-check"
    }
    else {
        Write-Error "Virtual environment creation failed. $($error[0])"
    }
}

function Invoke-CheckVersion () {
    $Python = Get-Command "python"
    $PyCmd = "python"
    if (!$Python) {
        Write-Verbose -Message "Could not find python.exe"
        $Python = Get-Command "py"
        $PyCmd = "py -3"
        if (!$Python) {
            Write-Verbose -Message "Could not find py.exe"
            exit 1
        }
    }

    # ensure the python version is 3.6+
    if (($Python.Version.Major -eq 3) -and ($Python.Version.Minor -ge 7)) {
        return $PyCmd
    }
    else {
        Write-Error "${Python.Source} version must be at least 3.7.0 to complete installation"
        return $false
    }
}

$PyCmd = Invoke-CheckVersion
if ($PyCmd -ne $false) {
    Invoke-BuildVenv $TargetDir $PyCmd
}
