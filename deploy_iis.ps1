<#
.SYNOPSIS
    Deploy QNet Agent to IIS on Windows Server.

.DESCRIPTION
    This script performs a FULL deployment of the QNet Agent Flask application
    into IIS using HttpPlatformHandler + Waitress.

    Run this script from an ELEVATED (Administrator) PowerShell prompt on the
    target Windows Server.

.NOTES
    Tested on: Windows Server 2019 / 2022
    Requires:  PowerShell 5.1+, Administrator privileges

.EXAMPLE
    .\deploy_iis.ps1
    .\deploy_iis.ps1 -SiteName "QNetAgent" -Port 8080 -PythonPath "C:\Python312\python.exe"
#>

[CmdletBinding()]
param(
    # -- Configurable parameters ---------------------------------------
    [string]$SiteName       = "QNetAgent",
    [string]$AppPoolName    = "QNetAgentPool",
    [int]   $Port           = 80,
    [string]$HostHeader     = "",               # e.g. "qnet.yourdomain.com"
    [string]$PhysicalPath   = "C:\inetpub\QNetAgent",
    [string]$PythonPath     = "C:\Python313\python.exe",
    [string]$SourcePath     = $PSScriptRoot      # directory containing this script
)

# =====================================================================
#  0. PRE-FLIGHT CHECKS
# =====================================================================
$ErrorActionPreference = "Stop"

function Write-Step  { param([string]$msg) Write-Host "`n>> $msg" -ForegroundColor Cyan }
function Write-OK    { param([string]$msg) Write-Host "   [OK] $msg" -ForegroundColor Green }
function Write-Warn  { param([string]$msg) Write-Host "   [WARN] $msg" -ForegroundColor Yellow }
function Write-Fail  { param([string]$msg) Write-Host "   [FAIL] $msg" -ForegroundColor Red }

# Must run as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Fail "This script must be run as Administrator. Right-click PowerShell -> 'Run as administrator'."
    exit 1
}

Write-Host "============================================================" -ForegroundColor White
Write-Host "  QNet Agent - IIS Deployment Script" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor White
Write-Host ""
Write-Host "  Site name    : $SiteName"
Write-Host "  App pool     : $AppPoolName"
Write-Host "  Port         : $Port"
Write-Host "  Physical path: $PhysicalPath"
Write-Host "  Python       : $PythonPath"
Write-Host "  Source       : $SourcePath"
Write-Host ""


# =====================================================================
#  1. VERIFY PYTHON IS INSTALLED
# =====================================================================
Write-Step "1/9 - Checking Python installation"

if (-not (Test-Path $PythonPath)) {
    Write-Fail "Python not found at $PythonPath"
    Write-Host @"

    Python 3.11+ is required.  Download from https://www.python.org/downloads/
    During install, check "Add Python to PATH" and "Install for all users".
    
    Alternatively, re-run this script with:
      .\deploy_iis.ps1 -PythonPath "C:\Path\To\python.exe"
"@
    exit 1
}

$pyVersion = & $PythonPath --version 2>&1
Write-OK "Found $pyVersion at $PythonPath"


# =====================================================================
#  2. INSTALL IIS + REQUIRED FEATURES
# =====================================================================
Write-Step "2/9 - Installing IIS features"

$features = @(
    "IIS-WebServerRole",
    "IIS-WebServer",
    "IIS-CommonHttpFeatures",
    "IIS-StaticContent",
    "IIS-DefaultDocument",
    "IIS-HttpErrors",
    "IIS-HttpLogging",
    "IIS-RequestFiltering",
    "IIS-ISAPIExtensions",
    "IIS-ISAPIFilter",
    "IIS-ManagementConsole"
)

foreach ($feature in $features) {
    $state = (Get-WindowsOptionalFeature -Online -FeatureName $feature -ErrorAction SilentlyContinue)
    if ($state -and $state.State -eq "Enabled") {
        Write-OK "$feature (already enabled)"
    } else {
        Write-Host "   Installing $feature ..." -NoNewline
        try {
            Enable-WindowsOptionalFeature -Online -FeatureName $feature -All -NoRestart -ErrorAction Stop | Out-Null
            Write-OK "done"
        } catch {
            Write-Warn "Failed to enable $feature : $_"
        }
    }
}


# =====================================================================
#  3. INSTALL HttpPlatformHandler
# =====================================================================
Write-Step "3/9 - Installing HttpPlatformHandler"

$hphDll = "$env:SystemRoot\System32\inetsrv\httpPlatformHandler.dll"
if (Test-Path $hphDll) {
    Write-OK "HttpPlatformHandler already installed"
} else {
    Write-Host "   Downloading HttpPlatformHandler v1.2 installer..."
    $installerUrl = "https://download.microsoft.com/download/5/0/2/502F8E94-3222-4D58-A1A4-41ADE3EC22F3/httpPlatformHandler_amd64.msi"
    $installerPath = "$env:TEMP\httpPlatformHandler_amd64.msi"
    
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath -UseBasicParsing
        Write-Host "   Running installer..."
        Start-Process msiexec.exe -ArgumentList "/i `"$installerPath`" /quiet /norestart" -Wait -NoNewWindow
        Write-OK "HttpPlatformHandler installed"
    } catch {
        Write-Warn "Auto-install failed. Install manually from:"
        Write-Host "   https://www.iis.net/downloads/microsoft/httpplatformhandler"
        Write-Host "   Then re-run this script."
        exit 1
    }
}


# =====================================================================
#  4. COPY APPLICATION FILES
# =====================================================================
Write-Step "4/9 - Copying application files to $PhysicalPath"

if (-not (Test-Path $PhysicalPath)) {
    New-Item -ItemType Directory -Path $PhysicalPath -Force | Out-Null
    Write-OK "Created $PhysicalPath"
}

# Copy everything except .git, __pycache__, venv, data/*.db
$excludeDirs = @(".git", "__pycache__", "venv", ".venv", "node_modules")
$sourceItems = Get-ChildItem -Path $SourcePath -Force | Where-Object {
    $excludeDirs -notcontains $_.Name
}
foreach ($item in $sourceItems) {
    Copy-Item -Path $item.FullName -Destination $PhysicalPath -Recurse -Force
    Write-Host "   Copied: $($item.Name)"
}

# Ensure data and logs directories exist
New-Item -ItemType Directory -Path "$PhysicalPath\data" -Force | Out-Null
New-Item -ItemType Directory -Path "$PhysicalPath\logs" -Force | Out-Null
Write-OK "Application files deployed"


# =====================================================================
#  5. CREATE VIRTUAL ENVIRONMENT + INSTALL DEPENDENCIES
# =====================================================================
Write-Step "5/9 - Creating Python virtual environment"

$venvPath = "$PhysicalPath\venv"
if (-not (Test-Path "$venvPath\Scripts\python.exe")) {
    & $PythonPath -m venv $venvPath
    Write-OK "Virtual environment created at $venvPath"
} else {
    Write-OK "Virtual environment already exists"
}

Write-Host "   Installing Python dependencies (this may take a few minutes)..."
# pip writes warnings/progress to stderr; temporarily allow that so PowerShell
# does not treat stderr output from native commands as a terminating error.
$prevEAP = $ErrorActionPreference
$ErrorActionPreference = "Continue"
try {
    & "$venvPath\Scripts\pip.exe" install --upgrade pip --quiet 2>&1 | Out-Null
    & "$venvPath\Scripts\pip.exe" install -r "$PhysicalPath\requirements.txt" --quiet 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Warn "pip exited with code $LASTEXITCODE - check dependency errors above"
    } else {
        Write-OK "Dependencies installed"
    }
} finally {
    $ErrorActionPreference = $prevEAP
}


# =====================================================================
#  6. CONFIGURE .env FILE
# =====================================================================
Write-Step "6/9 - Configuring environment variables"

$envFile = "$PhysicalPath\.env"
if (-not (Test-Path $envFile)) {
    Copy-Item "$PhysicalPath\.env.example" $envFile -Force
    Write-Warn ".env created from .env.example - YOU MUST EDIT IT:"
    Write-Host "   >> notepad $envFile" -ForegroundColor Yellow
    Write-Host "   Set OPENAI_API_KEY and SECRET_KEY before first use."
} else {
    Write-OK ".env already exists"
}

# Ensure production settings
$envContent = Get-Content $envFile -Raw
if ($envContent -match "FLASK_DEBUG=1") {
    $envContent = $envContent -replace "FLASK_DEBUG=1", "FLASK_DEBUG=0"
    Set-Content -Path $envFile -Value $envContent -NoNewline
    Write-OK "Set FLASK_DEBUG=0 for production"
}


# =====================================================================
#  7. FIX web.config PATHS
# =====================================================================
Write-Step "7/9 - Updating web.config paths"

$webConfigPath = "$PhysicalPath\web.config"
$webConfig = Get-Content $webConfigPath -Raw

# Replace %HOME% placeholders with the actual physical path
$webConfig = $webConfig -replace '%HOME%', $PhysicalPath

Set-Content -Path $webConfigPath -Value $webConfig -NoNewline
Write-OK "web.config paths updated to $PhysicalPath"


# =====================================================================
#  8. UNLOCK IIS CONFIGURATION SECTIONS + CREATE SITE
# =====================================================================
Write-Step "8/9 - Configuring IIS Application Pool and Site"

# Unlock sections that are denied by default at the server level,
# so that web.config can use them without a 500.19 error (0x80070021).
$appcmd = "$env:SystemRoot\System32\inetsrv\appcmd.exe"
$sectionsToUnlock = @(
    "system.webServer/handlers",
    "system.webServer/security/requestFiltering"
)
foreach ($section in $sectionsToUnlock) {
    try {
        & $appcmd unlock config -section:$section 2>&1 | Out-Null
        Write-OK "Unlocked config section: $section"
    } catch {
        Write-Warn "Could not unlock $section (may already be unlocked)"
    }
}

Import-Module WebAdministration -ErrorAction SilentlyContinue

# -- Application Pool --------------------------------------------------
if (-not (Test-Path "IIS:\AppPools\$AppPoolName")) {
    New-WebAppPool -Name $AppPoolName | Out-Null
    Write-OK "Created application pool: $AppPoolName"
} else {
    Write-OK "Application pool already exists: $AppPoolName"
}

# Configure the pool
Set-ItemProperty "IIS:\AppPools\$AppPoolName" -Name "managedRuntimeVersion" -Value ""
Set-ItemProperty "IIS:\AppPools\$AppPoolName" -Name "startMode" -Value "AlwaysRunning"
Set-ItemProperty "IIS:\AppPools\$AppPoolName" -Name "processModel.idleTimeout" -Value ([TimeSpan]::FromMinutes(0))
Set-ItemProperty "IIS:\AppPools\$AppPoolName" -Name "processModel.loadUserProfile" -Value $true
Write-OK "App pool configured (No Managed Code, AlwaysRunning, No idle timeout)"

# -- Site --------------------------------------------------------------
$existingSite = Get-Website -Name $SiteName -ErrorAction SilentlyContinue
if ($existingSite) {
    Write-Warn "Site '$SiteName' already exists - updating binding"
    Set-ItemProperty "IIS:\Sites\$SiteName" -Name "physicalPath" -Value $PhysicalPath
    Set-ItemProperty "IIS:\Sites\$SiteName" -Name "applicationPool" -Value $AppPoolName
} else {
    $bindingInfo = "*:${Port}:${HostHeader}"
    New-Website -Name $SiteName `
                -PhysicalPath $PhysicalPath `
                -ApplicationPool $AppPoolName `
                -Port $Port `
                -HostHeader $HostHeader `
                -Force | Out-Null
    Write-OK "Created IIS site: $SiteName on port $Port"
}

# If port 80 is used by Default Web Site, stop it
if ($Port -eq 80) {
    $defaultSite = Get-Website -Name "Default Web Site" -ErrorAction SilentlyContinue
    if ($defaultSite -and $defaultSite.State -eq "Started") {
        Stop-Website -Name "Default Web Site" -ErrorAction SilentlyContinue
        Write-Warn "Stopped 'Default Web Site' (was blocking port 80)"
    }
}


# =====================================================================
#  9. SET PERMISSIONS + START
# =====================================================================
Write-Step "9/9 - Setting file permissions and starting the site"

# Grant IIS_IUSRS + the AppPool identity read/write on the app directory
$acl = Get-Acl $PhysicalPath
$identities = @("IIS_IUSRS", "IIS AppPool\$AppPoolName")
foreach ($identity in $identities) {
    $rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
        $identity, "Modify", "ContainerInherit,ObjectInherit", "None", "Allow"
    )
    $acl.SetAccessRule($rule)
}
Set-Acl -Path $PhysicalPath -AclObject $acl
Write-OK "File permissions set for IIS_IUSRS and AppPool identity"

# Start the site
Start-Website -Name $SiteName -ErrorAction SilentlyContinue
Write-OK "Site started"

# =====================================================================
#  DONE
# =====================================================================
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  DEPLOYMENT COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Site URL : http://$(if($HostHeader){$HostHeader}else{'localhost'})$(if($Port -ne 80){':'+$Port})"
Write-Host "  Site name: $SiteName"
Write-Host "  App pool : $AppPoolName"
Write-Host "  App path : $PhysicalPath"
Write-Host "  Logs     : $PhysicalPath\logs\"
Write-Host ""
Write-Host "  IMPORTANT NEXT STEPS:" -ForegroundColor Yellow
Write-Host "  1. Edit $PhysicalPath\.env and set your OPENAI_API_KEY"
Write-Host "  2. Set a strong SECRET_KEY in .env"
Write-Host "  3. Open Windows Firewall for port $Port if needed"
Write-Host "  4. (Optional) Configure HTTPS with an SSL certificate"
Write-Host ""
Write-Host "  To test:  Start-Process http://localhost$(if($Port -ne 80){':'+$Port})"
Write-Host ""
