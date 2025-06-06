# Complete GitHub upload script
Write-Host "Completing GitHub upload for Gemini PDF Translator..." -ForegroundColor Cyan

# Set Git path
$env:PATH += ";C:\Program Files\Git\bin"

# Navigate to project directory
Set-Location "c:\Users\30694\gemini_translator_env"

Write-Host ""
Write-Host "GitHub Repository Setup Instructions:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Go to https://github.com" -ForegroundColor White
Write-Host "2. Click the '+' button in the top right corner" -ForegroundColor White
Write-Host "3. Select 'New repository'" -ForegroundColor White
Write-Host "4. Repository name: gemini-pdf-translator" -ForegroundColor Yellow
Write-Host "5. Description: Advanced PDF translation system with Gemini AI and Nougat integration" -ForegroundColor White
Write-Host "6. Choose Public or Private (your choice)" -ForegroundColor White
Write-Host "7. DO NOT check 'Add a README file' (we already have one)" -ForegroundColor Red
Write-Host "8. DO NOT check 'Add .gitignore' (we already have one)" -ForegroundColor Red
Write-Host "9. Click 'Create repository'" -ForegroundColor White
Write-Host ""
Write-Host "10. Copy the repository URL from the page (it will look like:" -ForegroundColor White
Write-Host "    https://github.com/tataro212/gemini-pdf-translator.git)" -ForegroundColor Yellow
Write-Host ""

$repoUrl = Read-Host "Paste your GitHub repository URL here"

if ($repoUrl -eq "") {
    Write-Host "No URL provided. Exiting..." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Adding remote repository..." -ForegroundColor Yellow
try {
    git remote add origin "$repoUrl"
    Write-Host "Remote repository added!" -ForegroundColor Green
} catch {
    Write-Host "Remote might already exist, trying to set URL..." -ForegroundColor Yellow
    git remote set-url origin "$repoUrl"
}

Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "This may take a moment for the first push..." -ForegroundColor Cyan

try {
    git branch -M main
    git push -u origin main

    Write-Host ""
    Write-Host "SUCCESS! Your project has been uploaded to GitHub!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your repository is now available at:" -ForegroundColor Cyan
    Write-Host "   $repoUrl" -ForegroundColor White
    Write-Host ""
    Write-Host "For future updates, use these commands:" -ForegroundColor Yellow
    Write-Host "   git add ." -ForegroundColor White
    Write-Host "   git commit -m 'Your commit message'" -ForegroundColor White
    Write-Host "   git push" -ForegroundColor White
    Write-Host ""
    Write-Host "Files uploaded include:" -ForegroundColor Cyan
    Write-Host "   - Complete source code (134 files)" -ForegroundColor Green
    Write-Host "   - Professional documentation" -ForegroundColor Green
    Write-Host "   - Installation guides" -ForegroundColor Green
    Write-Host "   - Configuration templates" -ForegroundColor Green
    Write-Host "   - Comprehensive README files" -ForegroundColor Green
    Write-Host ""
    Write-Host "Protected files (not uploaded):" -ForegroundColor Yellow
    Write-Host "   - credentials.json" -ForegroundColor Red
    Write-Host "   - client_secrets.json" -ForegroundColor Red
    Write-Host "   - config.ini" -ForegroundColor Red
    Write-Host "   - PDF files" -ForegroundColor Red
    Write-Host "   - Virtual environment files" -ForegroundColor Red
    Write-Host "   - Cache and output directories" -ForegroundColor Red

} catch {
    Write-Host ""
    Write-Host "Failed to push to GitHub" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible solutions:" -ForegroundColor Yellow
    Write-Host "1. Make sure you're logged into GitHub in your browser" -ForegroundColor White
    Write-Host "2. You may need to authenticate. Try running:" -ForegroundColor White
    Write-Host "   git push -u origin main" -ForegroundColor Cyan
    Write-Host "3. If prompted, use your GitHub username and a Personal Access Token" -ForegroundColor White
    Write-Host "   (not your password - GitHub requires tokens now)" -ForegroundColor White
    Write-Host ""
    Write-Host "To create a Personal Access Token:" -ForegroundColor Cyan
    Write-Host "   1. Go to GitHub.com -> Settings -> Developer settings -> Personal access tokens" -ForegroundColor White
    Write-Host "   2. Generate new token with repo permissions" -ForegroundColor White
    Write-Host "   3. Use the token as your password when prompted" -ForegroundColor White
}

Write-Host ""
Read-Host "Press Enter to exit"
