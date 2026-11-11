[CmdletBinding()]
param([switch]$SoloRuntime)

$ErrorActionPreference = 'Stop'
$python = (Get-Command py.exe -ErrorAction Stop).Source
$null = Get-Command pyw.exe -ErrorAction Stop
if (-not $SoloRuntime) {
    $codex = (Get-Command codex.exe -ErrorAction Stop).Source
}
& $python -3.13-64 -I -c 'import platform, sys; sys.exit(sys.platform != "win32" or platform.machine() != "AMD64")'
if ($LASTEXITCODE -ne 0) {
    throw 'Serve Python 3.13 x64 con il launcher py.exe.'
}

$state = $env:CODEX_DESKTOP_RDP_STATE
if (-not $state) {
    $state = Join-Path $env:LOCALAPPDATA 'CodexDesktopRemoto'
}
$state = (New-Item -ItemType Directory -Path $state -Force).FullName
$runtime = Join-Path $state 'runtime-v1'
if (-not (Test-Path -LiteralPath $runtime -PathType Container)) {
    $staging = Join-Path $state ('.runtime-' + [Guid]::NewGuid().ToString('N'))
    $parent = (Resolve-Path -LiteralPath $state).Path
    foreach ($path in $staging, $runtime) {
        if ([IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($path)) -ne $parent) {
            throw 'Percorso runtime non valido.'
        }
    }

    try {
        $requirements = Join-Path $PSScriptRoot 'requirements.lock'
        & $python -3.13-64 -I -m pip --isolated --disable-pip-version-check --no-cache-dir install `
            --no-input --index-url 'https://pypi.org/simple' --only-binary ':all:' --require-hashes `
            --no-compile --target $staging -r $requirements
        if ($LASTEXITCODE -ne 0) { throw 'Installazione delle dipendenze non riuscita.' }
        [IO.Directory]::Move($staging, $runtime)
    }
    finally {
        if (Test-Path -LiteralPath $staging -PathType Container) {
            Remove-Item -LiteralPath $staging -Recurse -Force
        }
    }
}

if (-not $SoloRuntime) {
    & $codex plugin marketplace add $PSScriptRoot
    if ($LASTEXITCODE -ne 0) { throw 'Registrazione del catalogo locale non riuscita.' }
    & $codex plugin add 'desktop-remoto@desktop-remoto-locale'
    if ($LASTEXITCODE -ne 0) { throw 'Installazione del plugin non riuscita.' }
    Write-Host 'Plugin installato. Esegui Configura.ps1 e riapri ChatGPT Desktop quando ti è comodo.'
}
else {
    Write-Host 'Runtime RDP pronto.'
}
