# 🚀 GitHub Setup Guide for Gemini PDF Translator

This guide will help you upload your Gemini PDF Translator project to GitHub.

## 📋 Prerequisites

### 1. Install Git
If Git is not installed on your system:
1. Go to: https://git-scm.com/download/windows
2. Download "64-bit Git for Windows Setup"
3. Run the installer with default settings
4. Restart your terminal/command prompt

### 2. Create GitHub Account
If you don't have one:
1. Go to: https://github.com
2. Sign up for a free account

## 🤖 Automated Setup (Recommended)

### Option 1: PowerShell Script
1. Right-click on `setup_github_repo.ps1`
2. Select "Run with PowerShell"
3. Follow the prompts

### Option 2: Batch Script
1. Double-click `setup_github_repo.bat`
2. Follow the prompts

## 🔧 Manual Setup

If the automated scripts don't work, follow these manual steps:

### Step 1: Install Git
```bash
# Check if Git is installed
git --version
```

### Step 2: Configure Git (First time only)
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Step 3: Create GitHub Repository
1. Go to https://github.com
2. Click "New repository" (green button)
3. Repository name: `gemini-pdf-translator`
4. Description: `Advanced PDF translation system with Gemini AI and Nougat integration`
5. Choose "Public" or "Private"
6. **DO NOT** check "Initialize this repository with a README"
7. Click "Create repository"
8. Copy the repository URL (e.g., `https://github.com/USERNAME/gemini-pdf-translator.git`)

### Step 4: Initialize Local Repository
Open terminal in your project directory:
```bash
cd "c:\Users\30694\gemini_translator_env"
git init
```

### Step 5: Add Remote Repository
Replace `YOUR_REPO_URL` with the URL you copied:
```bash
git remote add origin YOUR_REPO_URL
```

### Step 6: Stage Files
```bash
git add .
```

### Step 7: Create Initial Commit
```bash
git commit -m "Initial commit: Gemini PDF Translator with Nougat integration

- Advanced PDF translation using Google Gemini AI
- Nougat integration for visual content extraction
- Smart content optimization and caching
- Comprehensive error handling and fallbacks
- Modular architecture with extensive documentation"
```

### Step 8: Push to GitHub
```bash
git branch -M main
git push -u origin main
```

## 🔐 Authentication

If you get authentication errors:

### Option 1: Personal Access Token (Recommended)
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token with `repo` permissions
3. Use token as password when prompted

### Option 2: GitHub CLI
```bash
# Install GitHub CLI
winget install --id GitHub.cli

# Authenticate
gh auth login
```

## 🔄 Future Updates

After initial setup, to update your repository:
```bash
git add .
git commit -m "Description of your changes"
git push
```

## 📁 What Gets Uploaded

### ✅ Files that WILL be uploaded:
- All Python source code (`.py` files)
- `README.md` - Project documentation
- `requirements.txt` - Dependencies
- `.gitignore` - Git ignore rules
- `config.ini.template` - Configuration template
- Documentation files (`.md` files)

### ❌ Files that will NOT be uploaded (protected by .gitignore):
- `credentials.json` - Your Google API credentials
- `client_secrets.json` - OAuth secrets
- `mycreds.txt` - Credential files
- `config.ini` - Your actual configuration with API keys
- All PDF files and test documents
- Virtual environment files (`Lib/`, `Scripts/`, etc.)
- Cache files and output directories
- `__pycache__/` directories

## 🎯 Repository Features to Enable

After uploading:

### 1. Add Topics/Tags
On your repository page, add these topics:
- `pdf-translation`
- `gemini-ai`
- `nougat`
- `python`
- `document-processing`
- `ai-translation`
- `ocr`
- `academic-tools`

### 2. Create Release
1. Go to "Releases" → "Create a new release"
2. Tag: `v1.0.0`
3. Title: "Gemini PDF Translator v1.0.0"
4. Describe the features

### 3. Enable Issues
Go to Settings → Features → Issues (check the box)

## 🆘 Troubleshooting

### Git not recognized
- Restart terminal after installing Git
- Add Git to PATH: `C:\Program Files\Git\bin`

### Authentication failed
- Use Personal Access Token instead of password
- Enable 2FA on GitHub account

### Permission denied
- Check repository URL is correct
- Ensure you have write access to the repository

### Large files error
- Files over 100MB need Git LFS
- Our .gitignore should prevent this

## 📞 Support

If you encounter issues:
1. Check this guide first
2. Try the automated scripts
3. Search GitHub documentation
4. Create an issue in the repository

---

**Your project will be publicly available and ready for collaboration! 🎉**
