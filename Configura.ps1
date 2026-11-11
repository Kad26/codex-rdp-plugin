[CmdletBinding()]
param([switch]$Disattiva)

$ErrorActionPreference = 'Stop'
$python = (Get-Command py.exe -ErrorAction Stop).Source
$launch = Join-Path $PSScriptRoot 'plugins\desktop-remoto\server\avvio.py'
$mode = if ($Disattiva) { '--disattiva' } else { '--configura' }
& $python -3.13-64 -I -S -B $launch $mode
if ($LASTEXITCODE -ne 0) { throw 'Configurazione RDP non completata.' }
