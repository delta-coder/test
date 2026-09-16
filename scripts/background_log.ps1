# ============================================================
# CINEMA BOOKING - BACKGROUND MODE LOG
# ============================================================

$WorkspaceRoot = Split-Path -Parent $PSScriptRoot

$LogFolder = Join-Path `
    $WorkspaceRoot `
    "book_movie_ticket\logs"

$LogFile = Join-Path `
    $LogFolder `
    "background.log"


if (-not (Test-Path $LogFolder)) {

    New-Item `
        -ItemType Directory `
        -Path $LogFolder `
        -Force |
        Out-Null

}


if (-not (Test-Path $LogFile)) {

    New-Item `
        -ItemType File `
        -Path $LogFile `
        -Force |
        Out-Null

}


Clear-Host


Write-Host ""
Write-Host "============================================================" `
    -ForegroundColor DarkMagenta

Write-Host "          CINEMA BOOKING - BACKGROUND LOG" `
    -ForegroundColor Magenta

Write-Host "============================================================" `
    -ForegroundColor DarkMagenta

Write-Host ""
Write-Host "Chi hien thi khi Admin thay doi Background mode." `
    -ForegroundColor White

Write-Host ""
Write-Host "Log file:" `
    -ForegroundColor Yellow

Write-Host "  $LogFile"
Write-Host ""
Write-Host "Dang cho thay doi..." `
    -ForegroundColor Green

Write-Host ""


Get-Content `
    -Path $LogFile `
    -Wait `
    -Tail 30
