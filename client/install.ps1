<#
    Check Python version and create a virtual environment

    ./install.ps1 <ExtensionRoot>
#>
[CmdletBinding()]
param (
    [Parameter(Position=1)]
    [String]
    $ExtensionRoot
)

$EnvPath = Join-Path -Path $ExtensionRoot -ChildPath "env"

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
    # python3 -m venv /tmp/vscode-yara/env
    $EnvOutput = Invoke-Expression -Command "$PyCmd -m venv $EnvPath"
}
