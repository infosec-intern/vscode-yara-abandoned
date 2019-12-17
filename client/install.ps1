<#
    Check Python version and create a virtual environment

    ./install.ps1 <ExtensionRoot> <TargetDir>
#>
[CmdletBinding()]
param (
    [Parameter(Position=1)]
    [String]
    $ExtensionRoot,
    [Parameter(Position=2)]
    [String]
    $TargetDir
)

<#
    Build a virtual environment with the necessary packages with the provided Python path
    Requires path to python executable to validate
#>
function Invoke-BuildVenv ($ExtensionRoot, $TargetDir, $SystemPython) {
    $EnvPath = Join-Path -Path $TargetDir -ChildPath "env"
    Write-Verbose "Building virtual environment in ${EnvPath}"
    # python3 -m venv /tmp/vscode-yara/env
    Invoke-Command "$SystemPython -m venv $EnvPath"
    if (Test-Path -Path "$EnvPath\\Scripts" -PathType Container) {
        Write-Verbose "Virtual environment creation successful"
        $EnvPip = "$EnvPath\\Scripts\\pip.exe"
        Write-Verbose "Using $EnvPip to install yarals package and dependencies"
        # use wheel package to install
        Invoke-Command "$EnvPip -m pip install wheel --disable-pip-version-check"
        Invoke-Command "$EnvPip -m pip wheel $ExtensionRoot\\..\\server --disable-pip-version-check --no-deps --wheel-dir $EnvPath"
        $Wheel = "$EnvPath/yarals-*.whl"
        Invoke-Command "$EnvPip install $Wheel --disable-pip-version-check"
    }
    else {
        Write-Error "Virtual environment creation failed. $($error.ToString())"
    }
}

function Invoke-CheckVersion () {
    try {
        $Python = Get-Command -Module "python"
        $PyCmd = "python"
    }
    catch [CommandNotFoundException] {
        Write-Verbose -Message "Could not find python.exe"
        try {
            $Python = Get-Command -Module "py"
            $PyCmd = "py -3"
        }
        catch {
            Write-Verbose -Message "Could not find py.exe"
            exit 1
        }
    }

    # ensure the python version is 3.6+
    if (($Python.Version.Major -eq 3) -and ($Python.Version.Minor -ge 6)) {
        return $PyCmd
    }
    else {
        Write-Error "$($Python.Source) version must be at least 3.6.0 to complete installation"
        return $false
    }
}

$PyCmd = Invoke-CheckVersion
if ($PyCmd -ne $false) {
    Invoke-BuildVenv $ExtensionRoot $TargetDir, $PyCmd
}
