@echo off
echo ========================================
echo   Gemini PDF Translator - GitHub Setup
echo ========================================
echo.

REM Check if Git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git is not installed!
    echo.
    echo 📥 Please install Git first:
    echo    1. Go to: https://git-scm.com/download/windows
    echo    2. Download and install Git for Windows
    echo    3. Restart this script after installation
    echo.
    pause
    exit /b 1
)

echo ✅ Git is installed!
echo.

REM Navigate to project directory
cd /d "c:\Users\30694\gemini_translator_env"

echo 🔄 Setting up Git repository...
echo.

REM Initialize Git repository
git init
if %errorlevel% neq 0 (
    echo ❌ Failed to initialize Git repository
    pause
    exit /b 1
)

echo ✅ Git repository initialized!
echo.

REM Configure Git (you'll need to update these)
echo 🔧 Configuring Git...
set /p username="Enter your GitHub username: "
set /p email="Enter your email: "

git config user.name "%username%"
git config user.email "%email%"

echo ✅ Git configured!
echo.

REM Add all files
echo 📁 Adding files to repository...
git add .
if %errorlevel% neq 0 (
    echo ❌ Failed to add files
    pause
    exit /b 1
)

echo ✅ Files added!
echo.

REM Create initial commit
echo 💾 Creating initial commit...
git commit -m "Initial commit: Gemini PDF Translator with Nougat integration - Advanced PDF translation using Google Gemini AI - Nougat integration for visual content extraction - Smart content optimization and caching - Comprehensive error handling and fallbacks - Modular architecture with extensive documentation"
if %errorlevel% neq 0 (
    echo ❌ Failed to create commit
    pause
    exit /b 1
)

echo ✅ Initial commit created!
echo.

REM Instructions for GitHub
echo 🌐 Next steps for GitHub:
echo.
echo 1. Go to https://github.com and create a new repository
echo 2. Repository name: gemini-pdf-translator
echo 3. Description: Advanced PDF translation system with Gemini AI and Nougat integration
echo 4. Choose Public or Private
echo 5. DO NOT initialize with README (we already have one)
echo 6. Click "Create repository"
echo.
echo 7. Copy the repository URL (it will look like: https://github.com/USERNAME/gemini-pdf-translator.git)
echo.

set /p repo_url="Paste your GitHub repository URL here: "

REM Add remote origin
echo 🔗 Adding remote repository...
git remote add origin "%repo_url%"
if %errorlevel% neq 0 (
    echo ❌ Failed to add remote repository
    pause
    exit /b 1
)

echo ✅ Remote repository added!
echo.

REM Set main branch and push
echo 🚀 Pushing to GitHub...
git branch -M main
git push -u origin main
if %errorlevel% neq 0 (
    echo ❌ Failed to push to GitHub
    echo 💡 You may need to authenticate with GitHub
    echo    Try running: git push -u origin main
    pause
    exit /b 1
)

echo.
echo 🎉 SUCCESS! Your project has been uploaded to GitHub!
echo.
echo 📋 Your repository is now available at:
echo    %repo_url%
echo.
echo 🔄 For future updates, use:
echo    git add .
echo    git commit -m "Your commit message"
echo    git push
echo.
pause
