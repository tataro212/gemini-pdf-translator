# Quick Git Setup for Gemini PDF Translator
Write-Host "🚀 Gemini PDF Translator - Quick GitHub Setup" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
$currentDir = Get-Location
Write-Host "📁 Current directory: $currentDir" -ForegroundColor Yellow

# Check for key project files
$keyFiles = @("main_workflow.py", "config_manager.py", "README.md", ".gitignore")
$missingFiles = @()

foreach ($file in $keyFiles) {
    if (!(Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "❌ Missing key project files:" -ForegroundColor Red
    foreach ($file in $missingFiles) {
        Write-Host "   - $file" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "💡 Please run this script from the project directory: c:\Users\30694\gemini_translator_env" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Project files found!" -ForegroundColor Green
Write-Host ""

# Try to find Git
$gitPaths = @(
    "git",
    "C:\Program Files\Git\bin\git.exe",
    "C:\Program Files (x86)\Git\bin\git.exe",
    "$env:LOCALAPPDATA\Programs\Git\bin\git.exe"
)

$gitFound = $false
$gitPath = ""

foreach ($path in $gitPaths) {
    try {
        $result = & $path --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $gitFound = $true
            $gitPath = $path
            Write-Host "✅ Found Git: $result" -ForegroundColor Green
            break
        }
    } catch {
        # Continue to next path
    }
}

if (!$gitFound) {
    Write-Host "❌ Git not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "📥 Please install Git first:" -ForegroundColor Yellow
    Write-Host "   1. Go to: https://git-scm.com/download/windows" -ForegroundColor White
    Write-Host "   2. Download and install Git for Windows" -ForegroundColor White
    Write-Host "   3. Restart PowerShell and run this script again" -ForegroundColor White
    Write-Host ""
    Write-Host "🔗 Direct download link:" -ForegroundColor Cyan
    Write-Host "   https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe" -ForegroundColor Blue
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Check if already a git repository
if (Test-Path ".git") {
    Write-Host "ℹ️ This is already a Git repository" -ForegroundColor Blue
    $reinit = Read-Host "Do you want to reinitialize? (y/N)"
    if ($reinit -eq "y" -or $reinit -eq "Y") {
        Remove-Item ".git" -Recurse -Force
        Write-Host "🗑️ Removed existing Git repository" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Using existing Git repository" -ForegroundColor Green
    }
}

# Initialize Git repository if needed
if (!(Test-Path ".git")) {
    Write-Host "🔄 Initializing Git repository..." -ForegroundColor Yellow
    try {
        & $gitPath init
        Write-Host "✅ Git repository initialized!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to initialize Git repository: $($_.Exception.Message)" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""

# Configure Git
Write-Host "🔧 Git Configuration" -ForegroundColor Yellow
$username = Read-Host "Enter your GitHub username"
$email = Read-Host "Enter your email address"

& $gitPath config user.name "$username"
& $gitPath config user.email "$email"

Write-Host "✅ Git configured!" -ForegroundColor Green
Write-Host ""

# Show what will be committed
Write-Host "📋 Files to be committed:" -ForegroundColor Cyan
& $gitPath status --porcelain | ForEach-Object {
    Write-Host "   $_" -ForegroundColor White
}
Write-Host ""

$proceed = Read-Host "Proceed with adding these files? (Y/n)"
if ($proceed -eq "n" -or $proceed -eq "N") {
    Write-Host "❌ Aborted by user" -ForegroundColor Red
    exit 1
}

# Add files
Write-Host "📁 Adding files..." -ForegroundColor Yellow
& $gitPath add .
Write-Host "✅ Files added!" -ForegroundColor Green
Write-Host ""

# Create commit
Write-Host "💾 Creating initial commit..." -ForegroundColor Yellow
$commitMessage = "Initial commit: Gemini PDF Translator with Nougat integration`n`n- Advanced PDF translation using Google Gemini AI`n- Nougat integration for visual content extraction`n- Smart content optimization and caching`n- Comprehensive error handling and fallbacks`n- Modular architecture with extensive documentation"

& $gitPath commit -m "$commitMessage"
Write-Host "✅ Initial commit created!" -ForegroundColor Green
Write-Host ""

# GitHub instructions
Write-Host "🌐 GitHub Setup Instructions:" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Go to: https://github.com" -ForegroundColor White
Write-Host "2. Click 'New repository' (green button)" -ForegroundColor White
Write-Host "3. Repository name: gemini-pdf-translator" -ForegroundColor Yellow
Write-Host "4. Description: Advanced PDF translation system with Gemini AI and Nougat integration" -ForegroundColor White
Write-Host "5. Choose Public or Private" -ForegroundColor White
Write-Host "6. ❌ DO NOT check 'Initialize this repository with a README'" -ForegroundColor Red
Write-Host "7. Click 'Create repository'" -ForegroundColor White
Write-Host ""

$repoUrl = Read-Host "Paste your GitHub repository URL here (e.g., https://github.com/username/gemini-pdf-translator.git)"

if ($repoUrl -eq "") {
    Write-Host "❌ No repository URL provided" -ForegroundColor Red
    Write-Host "💡 You can add it later with: git remote add origin YOUR_URL" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Add remote
Write-Host ""
Write-Host "🔗 Adding remote repository..." -ForegroundColor Yellow
& $gitPath remote add origin "$repoUrl"
Write-Host "✅ Remote repository added!" -ForegroundColor Green

# Push to GitHub
Write-Host ""
Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "💡 You may be prompted for authentication" -ForegroundColor Blue

& $gitPath branch -M main
& $gitPath push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "🎉 SUCCESS! Your project is now on GitHub!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Repository URL: $repoUrl" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🔄 For future updates:" -ForegroundColor Yellow
    Write-Host "   git add ." -ForegroundColor White
    Write-Host "   git commit -m 'Your message'" -ForegroundColor White
    Write-Host "   git push" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "⚠️ Push may have failed - check authentication" -ForegroundColor Yellow
    Write-Host "💡 Try running manually: git push -u origin main" -ForegroundColor Blue
}

Write-Host ""
Read-Host "Press Enter to exit"
