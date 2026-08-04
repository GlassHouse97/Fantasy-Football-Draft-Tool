$ErrorActionPreference = "Stop"

$python = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    throw "Local .venv not found. Follow the setup commands in README.md first."
}

function Invoke-Check {
    param([string[]]$Arguments)

    & $python @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Check failed: python $($Arguments -join ' ')"
    }
}

Invoke-Check -Arguments @("-m", "ruff", "check", ".")
Invoke-Check -Arguments @("-m", "mypy")
Invoke-Check -Arguments @("-m", "pytest")
