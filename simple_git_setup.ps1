# Simple Git setup script for Gemini PDF Translator
Write-Host "Setting up Git repository for Gemini PDF Translator..." -ForegroundColor Cyan

# Set Git path
$env:PATH += ";C:\Program Files\Git\bin"

# Navigate to project directory
Set-Location "c:\Users\30694\gemini_translator_env"
Write-Host "Working in: $(Get-Location)" -ForegroundColor Green

# Initialize Git repository
Write-Host "Initializing Git repository..." -ForegroundColor Yellow
git init

# Configure Git (you'll need to provide your details)
Write-Host "Configuring Git..." -ForegroundColor Yellow
$username = Read-Host "Enter your GitHub username"
$email = Read-Host "Enter your email address"

git config user.name "$username"
git config user.email "$email"

# Add all files
Write-Host "Adding files to repository..." -ForegroundColor Yellow
git add .

# Create initial commit
Write-Host "Creating initial commit..." -ForegroundColor Yellow
git commit -m "Initial commit: Gemini PDF Translator with Nougat integration

- Advanced PDF translation using Google Gemini AI
- Nougat integration for visual content extraction  
- Smart content optimization and caching
- Comprehensive error handling and fallbacks
- Modular architecture with extensive documentation"

Write-Host "Git repository setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Create a new repository on GitHub.com" -ForegroundColor White
Write-Host "2. Copy the repository URL" -ForegroundColor White
Write-Host "3. Run: git remote add origin <your-repo-url>" -ForegroundColor White
Write-Host "4. Run: git branch -M main" -ForegroundColor White
Write-Host "5. Run: git push -u origin main" -ForegroundColor White
