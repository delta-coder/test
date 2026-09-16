# ============================================================
# CINEMA BOOKING - CONTROL TERMINAL
#
# Ctrl + C tai prompt:
# -> tao .cinema_stop_server
# -> pane Django Server nhan tin hieu va tat server.
#
# Ban nay KHONG goi function tu PSReadLine handler,
# tranh loi scope "Stop-CinemaServer is not recognized".
# ============================================================

$WorkspaceRoot = Split-Path -Parent $PSScriptRoot
$ProjectFolder = Join-Path $WorkspaceRoot "book_movie_ticket"
$PythonExe = Join-Path $WorkspaceRoot ".venv\Scripts\python.exe"
$ManagePy = Join-Path $ProjectFolder "manage.py"
$DatabaseFile = Join-Path $ProjectFolder "db.sqlite3"
$StopFile = Join-Path $WorkspaceRoot ".cinema_stop_server"

# Cho custom PSReadLine handler truy cap chac chan.
$global:CinemaWorkspaceRoot = $WorkspaceRoot
$global:CinemaStopFile = $StopFile

Set-Location $ProjectFolder


# ============================================================
# CHECK ENV
# ============================================================

if (-not (Test-Path -LiteralPath $PythonExe)) {

    Write-Host ""
    Write-Host "[ERROR] Khong tim thay .venv" -ForegroundColor Red
    Write-Host "Hay chay setup_windows.bat truoc." -ForegroundColor Yellow
    Write-Host ""

    return
}


# ============================================================
# SERVER STATUS
# ============================================================

function Get-CinemaServerStatus {

    $connection = Get-NetTCPConnection `
        -LocalPort 8000 `
        -State Listen `
        -ErrorAction SilentlyContinue

    Write-Host ""

    if ($connection) {

        Write-Host "[SERVER] ONLINE - PORT 8000" `
            -ForegroundColor Green
    }
    else {

        Write-Host "[SERVER] OFFLINE" `
            -ForegroundColor Red
    }

    Write-Host ""
}


# ============================================================
# STOP SERVER
# ============================================================

function Stop-CinemaServer {

    $connection = Get-NetTCPConnection `
        -LocalPort 8000 `
        -State Listen `
        -ErrorAction SilentlyContinue


    if (-not $connection) {

        Write-Host ""
        Write-Host "[SERVER] Da OFFLINE." `
            -ForegroundColor Yellow
        Write-Host ""

        return
    }


    try {

        Set-Content `
            -LiteralPath $global:CinemaStopFile `
            -Value "STOP" `
            -Encoding ASCII `
            -Force


        Write-Host ""
        Write-Host "[SERVER] Dang gui lenh tat sang Django Server..." `
            -ForegroundColor Yellow


        $stopped = $false


        for ($i = 0; $i -lt 48; $i++) {

            Start-Sleep `
                -Milliseconds 250


            $stillRunning = Get-NetTCPConnection `
                -LocalPort 8000 `
                -State Listen `
                -ErrorAction SilentlyContinue


            if (-not $stillRunning) {

                $stopped = $true

                break
            }
        }


        if ($stopped) {

            Write-Host "[SERVER] Da tat thanh cong." `
                -ForegroundColor Green
        }
        else {

            Write-Host "[SERVER] Chua tat sau 12 giay. Hay xem pane Django Server." `
                -ForegroundColor Red
        }


        Write-Host ""
    }
    catch {

        Write-Host ""
        Write-Host "[ERROR] Khong gui duoc lenh tat server." `
            -ForegroundColor Red

        Write-Host $_

        Write-Host ""
    }
}


# ============================================================
# CREATE NORMAL USER
# ============================================================

function New-CinemaUser {

    param(
        [Parameter(Mandatory=$true, Position=0)]
        [string]$Username,

        [Parameter(Mandatory=$true, Position=1)]
        [string]$Email,

        [Parameter(Mandatory=$true, Position=2)]
        [string]$Password
    )


    $env:CINEMA_NEW_USERNAME = $Username
    $env:CINEMA_NEW_EMAIL = $Email
    $env:CINEMA_NEW_PASSWORD = $Password


    try {

        & $PythonExe `
            $ManagePy `
            shell `
            -c `
            "import os; from book_movie_ticket_app.models import CustomUser; u=CustomUser.objects.create_user(username=os.environ['CINEMA_NEW_USERNAME'], email=os.environ['CINEMA_NEW_EMAIL'], password=os.environ['CINEMA_NEW_PASSWORD']); print('Da tao USER:', u.username)"
    }
    finally {

        Remove-Item Env:CINEMA_NEW_USERNAME `
            -ErrorAction SilentlyContinue

        Remove-Item Env:CINEMA_NEW_EMAIL `
            -ErrorAction SilentlyContinue

        Remove-Item Env:CINEMA_NEW_PASSWORD `
            -ErrorAction SilentlyContinue
    }
}


# ============================================================
# CREATE SUPERUSER
# ============================================================

function New-CinemaAdmin {

    & $PythonExe `
        $ManagePy `
        createsuperuser
}


# ============================================================
# LIST USERS
# ============================================================

function Get-CinemaUsers {

    & $PythonExe `
        $ManagePy `
        shell `
        -c `
        "from book_movie_ticket_app.models import CustomUser; print(); [print(f'{u.id:>3} | {u.username:<20} | staff={u.is_staff} | superuser={u.is_superuser}') for u in CustomUser.objects.all().order_by('id')]; print()"
}


# ============================================================
# DJANGO CHECK
# ============================================================

function Test-CinemaDjango {

    & $PythonExe `
        $ManagePy `
        check
}


# ============================================================
# MIGRATIONS
# ============================================================

function Show-CinemaMigrations {

    & $PythonExe `
        $ManagePy `
        showmigrations
}


# ============================================================
# DATABASE CHECK
# ============================================================

function Test-CinemaDatabase {

    if (-not (Test-Path -LiteralPath $DatabaseFile)) {

        Write-Host ""
        Write-Host "[DB] Khong tim thay db.sqlite3" `
            -ForegroundColor Red
        Write-Host ""

        return
    }


    $env:CINEMA_DB_PATH = $DatabaseFile


    try {

        & $PythonExe `
            -c `
            "import os, sqlite3; p=os.environ['CINEMA_DB_PATH']; c=sqlite3.connect(p); print('Database:', p); print('PRAGMA integrity_check:'); print(c.execute('PRAGMA integrity_check;').fetchall()); c.close()"
    }
    finally {

        Remove-Item Env:CINEMA_DB_PATH `
            -ErrorAction SilentlyContinue
    }
}


# ============================================================
# DATABASE BACKUP
# ============================================================

function Backup-CinemaDatabase {

    if (-not (Test-Path -LiteralPath $DatabaseFile)) {

        Write-Host ""
        Write-Host "[DB] Khong tim thay db.sqlite3" `
            -ForegroundColor Red
        Write-Host ""

        return
    }


    $stamp = Get-Date `
        -Format "yyyyMMdd_HHmmss"

    $backupFile = Join-Path `
        $ProjectFolder `
        ("db_backup_" + $stamp + ".sqlite3")


    Copy-Item `
        -LiteralPath $DatabaseFile `
        -Destination $backupFile `
        -Force


    Write-Host ""
    Write-Host "[DB] Backup thanh cong:" `
        -ForegroundColor Green

    Write-Host "     $backupFile"

    Write-Host ""
}


# ============================================================
# CLEAR BACKGROUND LOG
# ============================================================

function Clear-CinemaBackgroundLog {

    $LogFile = Join-Path `
        $ProjectFolder `
        "logs\background.log"

    $LogFolder = Split-Path `
        -Parent `
        $LogFile


    if (-not (Test-Path -LiteralPath $LogFolder)) {

        New-Item `
            -ItemType Directory `
            -Path $LogFolder `
            -Force |
            Out-Null
    }


    Set-Content `
        -LiteralPath $LogFile `
        -Value "" `
        -Encoding UTF8


    Write-Host ""
    Write-Host "[BACKGROUND LOG] Da xoa log." `
        -ForegroundColor Green
    Write-Host ""
}


# ============================================================
# HELP
# ============================================================

function Show-CinemaHelp {

    Write-Host ""
    Write-Host "============================================================"
    Write-Host "              CINEMA BOOKING - CONTROL"
    Write-Host "============================================================"
    Write-Host ""
    Write-Host "  Ctrl + C"
    Write-Host "      Tat Django Server o pane giua"
    Write-Host ""
    Write-Host "  stopserver"
    Write-Host "      Tat Django Server"
    Write-Host ""
    Write-Host "  serverstatus"
    Write-Host "      Kiem tra server port 8000"
    Write-Host ""
    Write-Host "  newuser <username> <email> <password>"
    Write-Host "      Tao user thuong"
    Write-Host ""
    Write-Host "  newadmin"
    Write-Host "      Tao Superuser"
    Write-Host ""
    Write-Host "  users"
    Write-Host "      Xem danh sach user"
    Write-Host ""
    Write-Host "  checkdjango"
    Write-Host "      Kiem tra Django"
    Write-Host ""
    Write-Host "  migrations"
    Write-Host "      Xem migrations"
    Write-Host ""
    Write-Host "  dbcheck"
    Write-Host "      Kiem tra SQLite"
    Write-Host ""
    Write-Host "  dbbackup"
    Write-Host "      Backup db.sqlite3"
    Write-Host ""
    Write-Host "  clearbglog"
    Write-Host "      Xoa Background Log"
    Write-Host ""
    Write-Host "============================================================"
    Write-Host ""
}


# ============================================================
# ALIASES
# ============================================================

Set-Alias newuser New-CinemaUser
Set-Alias newadmin New-CinemaAdmin
Set-Alias users Get-CinemaUsers
Set-Alias checkdjango Test-CinemaDjango
Set-Alias migrations Show-CinemaMigrations
Set-Alias serverstatus Get-CinemaServerStatus
Set-Alias stopserver Stop-CinemaServer
Set-Alias dbcheck Test-CinemaDatabase
Set-Alias dbbackup Backup-CinemaDatabase
Set-Alias clearbglog Clear-CinemaBackgroundLog
Set-Alias cinemahelp Show-CinemaHelp


# ============================================================
# CTRL + C -> STOP SERVER
#
# QUAN TRONG:
# Handler khong goi Stop-CinemaServer nua.
# No tu xu ly truc tiep bang bien $global:CinemaStopFile.
# ============================================================

try {

    Import-Module `
        PSReadLine `
        -ErrorAction Stop


    Set-PSReadLineKeyHandler `
        -Chord "Ctrl+c" `
        -ScriptBlock {

            try {

                [Microsoft.PowerShell.PSConsoleReadLine]::RevertLine()
            }
            catch {
            }


            try {

                $connection = Get-NetTCPConnection `
                    -LocalPort 8000 `
                    -State Listen `
                    -ErrorAction SilentlyContinue


                if (-not $connection) {

                    Write-Host ""
                    Write-Host "[SERVER] Da OFFLINE." `
                        -ForegroundColor Yellow
                    Write-Host ""

                    return
                }


                Set-Content `
                    -LiteralPath $global:CinemaStopFile `
                    -Value "STOP" `
                    -Encoding ASCII `
                    -Force


                Write-Host ""
                Write-Host "[SERVER] Ctrl+C -> dang gui lenh tat..." `
                    -ForegroundColor Yellow


                $stopped = $false


                for ($i = 0; $i -lt 48; $i++) {

                    Start-Sleep `
                        -Milliseconds 250


                    $stillRunning = Get-NetTCPConnection `
                        -LocalPort 8000 `
                        -State Listen `
                        -ErrorAction SilentlyContinue


                    if (-not $stillRunning) {

                        $stopped = $true

                        break
                    }
                }


                if ($stopped) {

                    Write-Host "[SERVER] Da tat thanh cong." `
                        -ForegroundColor Green
                }
                else {

                    Write-Host "[SERVER] Chua tat sau 12 giay. Hay xem pane Django Server." `
                        -ForegroundColor Red
                }


                Write-Host ""
            }
            catch {

                Write-Host ""
                Write-Host "[ERROR] Ctrl+C handler bi loi:" `
                    -ForegroundColor Red

                Write-Host $_

                Write-Host ""
            }
        }
}
catch {

    Write-Host ""
    Write-Host "[WARN] Khong bind duoc Ctrl+C. Dung lenh stopserver thay the." `
        -ForegroundColor Yellow
    Write-Host ""
}


# ============================================================
# START SCREEN
# ============================================================

Clear-Host

Write-Host ""
Write-Host "============================================================" `
    -ForegroundColor DarkCyan

Write-Host "            CINEMA BOOKING - CONTROL TERMINAL" `
    -ForegroundColor Cyan

Write-Host "============================================================" `
    -ForegroundColor DarkCyan

Write-Host ""

Write-Host "CTRL + C = TAT DJANGO SERVER" `
    -ForegroundColor Green

Write-Host ""

Write-Host "Lenh nhanh:" `
    -ForegroundColor Yellow

Write-Host ""
Write-Host "  newuser truong truong@gmail.com 12345678"
Write-Host "  newadmin"
Write-Host "  users"
Write-Host "  checkdjango"
Write-Host "  serverstatus"
Write-Host "  stopserver"
Write-Host "  dbcheck"
Write-Host "  dbbackup"
Write-Host ""

Write-Host "Go cinemahelp de xem day du." `
    -ForegroundColor Cyan

Write-Host ""
