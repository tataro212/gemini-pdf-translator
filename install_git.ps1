# PowerShell script to download and install Git
Write-Host "🔄 Downloading Git for Windows..." -ForegroundColor Yellow

# Create temp directory
$tempDir = "$env:TEMP\GitInstaller"
if (!(Test-Path $tempDir)) {
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
}

# Download Git installer
$gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe"
$installerPath = "$tempDir\Git-Installer.exe"

try {
    Write-Host "📥 Downloading from: $gitUrl" -ForegroundColor Cyan
    Invoke-WebRequest -Uri $gitUrl -OutFile $installerPath -UseBasicParsing
    
    Write-Host "✅ Download completed!" -ForegroundColor Green
    Write-Host "🚀 Installing Git..." -ForegroundColor Yellow
    
    # Install Git silently
    Start-Process -FilePath $installerPath -ArgumentList "/VERYSILENT", "/NORESTART", "/NOCANCEL", "/SP-", "/CLOSEAPPLICATIONS", "/RESTARTAPPLICATIONS", "/COMPONENTS=icons,ext\reg\shellhere,assoc,assoc_sh" -Wait
    
    Write-Host "✅ Git installation completed!" -ForegroundColor Green
    Write-Host "🔄 Refreshing environment variables..." -ForegroundColor Yellow
    
    # Refresh environment variables
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    # Clean up
    Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    
    Write-Host "🎉 Git is now installed! Please restart your terminal." -ForegroundColor Green
    
} catch {
    Write-Host "❌ Error installing Git: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "💡 Please download Git manually from: https://git-scm.com/download/windows" -ForegroundColor Yellow
}
