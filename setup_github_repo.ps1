# PowerShell script to set up GitHub repository for Gemini PDF Translator
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Gemini PDF Translator - GitHub Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Git is installed
try {
    $gitVersion = git --version 2>$null
    Write-Host "✅ Git is installed: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "📥 Please install Git first:" -ForegroundColor Yellow
    Write-Host "   1. Go to: https://git-scm.com/download/windows" -ForegroundColor White
    Write-Host "   2. Download and install Git for Windows" -ForegroundColor White
    Write-Host "   3. Restart this script after installation" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Navigate to project directory
$projectPath = "c:\Users\30694\gemini_translator_env"
Set-Location $projectPath
Write-Host "📁 Working in: $projectPath" -ForegroundColor Cyan

Write-Host ""
Write-Host "🔄 Setting up Git repository..." -ForegroundColor Yellow

# Initialize Git repository
try {
    git init
    Write-Host "✅ Git repository initialized!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to initialize Git repository" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Configure Git
Write-Host "🔧 Configuring Git..." -ForegroundColor Yellow
$username = Read-Host "Enter your GitHub username"
$email = Read-Host "Enter your email"

git config user.name "$username"
git config user.email "$email"

Write-Host "✅ Git configured!" -ForegroundColor Green
Write-Host ""

# Add all files
Write-Host "📁 Adding files to repository..." -ForegroundColor Yellow
try {
    git add .
    Write-Host "✅ Files added!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to add files" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Create initial commit
Write-Host "💾 Creating initial commit..." -ForegroundColor Yellow
$commitMessage = @"
Initial commit: Gemini PDF Translator with Nougat integration

- Advanced PDF translation using Google Gemini AI
- Nougat integration for visual content extraction
- Smart content optimization and caching
- Comprehensive error handling and fallbacks
- Modular architecture with extensive documentation
"@

try {
    git commit -m "$commitMessage"
    Write-Host "✅ Initial commit created!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create commit" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Instructions for GitHub
Write-Host "🌐 Next steps for GitHub:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Go to https://github.com and create a new repository" -ForegroundColor White
Write-Host "2. Repository name: gemini-pdf-translator" -ForegroundColor White
Write-Host "3. Description: Advanced PDF translation system with Gemini AI and Nougat integration" -ForegroundColor White
Write-Host "4. Choose Public or Private" -ForegroundColor White
Write-Host "5. DO NOT initialize with README (we already have one)" -ForegroundColor Yellow
Write-Host "6. Click 'Create repository'" -ForegroundColor White
Write-Host ""
Write-Host "7. Copy the repository URL (it will look like: https://github.com/USERNAME/gemini-pdf-translator.git)" -ForegroundColor White
Write-Host ""

$repoUrl = Read-Host "Paste your GitHub repository URL here"

# Add remote origin
Write-Host ""
Write-Host "🔗 Adding remote repository..." -ForegroundColor Yellow
try {
    git remote add origin "$repoUrl"
    Write-Host "✅ Remote repository added!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to add remote repository" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Set main branch and push
Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Yellow
try {
    git branch -M main
    git push -u origin main
    
    Write-Host ""
    Write-Host "🎉 SUCCESS! Your project has been uploaded to GitHub!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Your repository is now available at:" -ForegroundColor Cyan
    Write-Host "   $repoUrl" -ForegroundColor White
    Write-Host ""
    Write-Host "🔄 For future updates, use:" -ForegroundColor Yellow
    Write-Host "   git add ." -ForegroundColor White
    Write-Host "   git commit -m 'Your commit message'" -ForegroundColor White
    Write-Host "   git push" -ForegroundColor White
    
} catch {
    Write-Host "❌ Failed to push to GitHub" -ForegroundColor Red
    Write-Host "💡 You may need to authenticate with GitHub" -ForegroundColor Yellow
    Write-Host "   Try running: git push -u origin main" -ForegroundColor White
}

Write-Host ""
Read-Host "Press Enter to exit"
