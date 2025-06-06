#!/usr/bin/env python3
"""
Nougat Environment Setup Script

This script implements the comprehensive solution for fixing Nougat installation
by creating a clean Python 3.11 environment with compatible dependencies.

Based on the analysis that identified:
1. transformers version incompatibility (cache_position error)
2. Python 3.13 wheel availability issues for tokenizers<0.19
3. Rust compilation requirements for source builds

Usage:
    python setup_nougat_environment.py
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def check_python_version():
    """Check if Python 3.11 is available"""
    print("🔍 Checking Python 3.11 availability...")
    
    # Try different Python 3.11 commands
    python_commands = [
        'python3.11',
        'py -3.11',
        'python311',
        'python'
    ]
    
    for cmd in python_commands:
        try:
            result = subprocess.run([cmd, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip()
                if '3.11' in version:
                    print(f"✅ Found Python 3.11: {version}")
                    print(f"   Command: {cmd}")
                    return cmd
                else:
                    print(f"   {cmd}: {version} (not 3.11)")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    print("❌ Python 3.11 not found")
    print("\n📥 Please install Python 3.11 from:")
    print("   https://www.python.org/downloads/release/python-3118/")
    print("   Make sure to check 'Add python.exe to PATH' during installation")
    return None

def create_virtual_environment(python_cmd):
    """Create a new virtual environment with Python 3.11"""
    print("\n🔧 Creating virtual environment...")
    
    env_path = Path("nougat_env")
    
    if env_path.exists():
        print(f"⚠️ Environment '{env_path}' already exists")
        response = input("Do you want to remove it and create a new one? (y/N): ")
        if response.lower() == 'y':
            import shutil
            shutil.rmtree(env_path)
            print("🗑️ Removed existing environment")
        else:
            print("✅ Using existing environment")
            return env_path
    
    try:
        # Create virtual environment
        cmd = [python_cmd, '-m', 'venv', str(env_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"✅ Created virtual environment: {env_path}")
            return env_path
        else:
            print(f"❌ Failed to create virtual environment: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ Virtual environment creation timed out")
        return None
    except Exception as e:
        print(f"❌ Error creating virtual environment: {e}")
        return None

def get_activation_script(env_path):
    """Get the activation script path for the virtual environment"""
    if platform.system() == "Windows":
        return env_path / "Scripts" / "activate.bat"
    else:
        return env_path / "bin" / "activate"

def get_python_executable(env_path):
    """Get the Python executable path in the virtual environment"""
    if platform.system() == "Windows":
        return env_path / "Scripts" / "python.exe"
    else:
        return env_path / "bin" / "python"

def install_packages(env_path):
    """Install packages in the correct order with compatible versions"""
    print("\n📦 Installing packages with compatible versions...")
    
    python_exe = get_python_executable(env_path)
    
    if not python_exe.exists():
        print(f"❌ Python executable not found: {python_exe}")
        return False
    
    # Step 1: Upgrade pip
    print("   Upgrading pip...")
    try:
        result = subprocess.run([str(python_exe), '-m', 'pip', 'install', '--upgrade', 'pip'], 
                              capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"⚠️ Pip upgrade warning: {result.stderr}")
    except Exception as e:
        print(f"⚠️ Pip upgrade failed: {e}")
    
    # Step 2: Install PyTorch (CPU version)
    print("   Installing PyTorch (CPU)...")
    try:
        cmd = [str(python_exe), '-m', 'pip', 'install', 'torch', 
               '--index-url', 'https://download.pytorch.org/whl/cpu']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("   ✅ PyTorch installed successfully")
        else:
            print(f"   ❌ PyTorch installation failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ❌ PyTorch installation timed out")
        return False
    except Exception as e:
        print(f"   ❌ PyTorch installation error: {e}")
        return False
    
    # Step 3: Install Nougat and compatible dependencies
    print("   Installing Nougat with compatible dependencies...")
    
    packages = [
        'nougat-ocr==0.1.17',
        'transformers==4.36.2',
        'tokenizers==0.15.2',
        'requests==2.31.0',
        'pypdf==4.2.0'
    ]
    
    try:
        cmd = [str(python_exe), '-m', 'pip', 'install'] + packages
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print("   ✅ All packages installed successfully")
            return True
        else:
            print(f"   ❌ Package installation failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ❌ Package installation timed out")
        return False
    except Exception as e:
        print(f"   ❌ Package installation error: {e}")
        return False

def verify_installation(env_path):
    """Verify the installation by running the verification script"""
    print("\n🧪 Verifying installation...")
    
    python_exe = get_python_executable(env_path)
    verify_script = Path("verify_nougat.py")
    
    if not verify_script.exists():
        print(f"❌ Verification script not found: {verify_script}")
        return False
    
    try:
        print("   Running verification script...")
        result = subprocess.run([str(python_exe), str(verify_script)], 
                              capture_output=True, text=True, timeout=300)
        
        print("   Verification output:")
        print("   " + "\n   ".join(result.stdout.split('\n')))
        
        if result.returncode == 0:
            print("   ✅ Verification passed!")
            return True
        else:
            print("   ❌ Verification failed")
            if result.stderr:
                print("   Error details:")
                print("   " + "\n   ".join(result.stderr.split('\n')))
            return False
            
    except subprocess.TimeoutExpired:
        print("   ❌ Verification timed out")
        return False
    except Exception as e:
        print(f"   ❌ Verification error: {e}")
        return False

def create_activation_instructions(env_path):
    """Create instructions for activating the environment"""
    print("\n📋 Environment Setup Complete!")
    print("=" * 50)
    
    activation_script = get_activation_script(env_path)
    python_exe = get_python_executable(env_path)
    
    print("🎯 To use Nougat:")
    print()
    
    if platform.system() == "Windows":
        print("1. Activate the environment:")
        print(f"   {env_path}\\Scripts\\activate")
        print()
        print("2. Verify it's working:")
        print(f"   python verify_nougat.py")
        print()
        print("3. Use Nougat command line:")
        print("   nougat your_document.pdf -o output_folder")
        print()
        print("4. Use Nougat in Python:")
        print("   from nougat import NougatModel")
    else:
        print("1. Activate the environment:")
        print(f"   source {env_path}/bin/activate")
        print()
        print("2. Verify it's working:")
        print(f"   python verify_nougat.py")
        print()
        print("3. Use Nougat command line:")
        print("   nougat your_document.pdf -o output_folder")
        print()
        print("4. Use Nougat in Python:")
        print("   from nougat import NougatModel")
    
    print()
    print("💡 Tips:")
    print("   - The environment is isolated and won't affect other Python projects")
    print("   - Always activate the environment before using Nougat")
    print("   - The first run will download model files (~500MB)")

def main():
    """Main setup function"""
    print("🚀 Nougat Environment Setup")
    print("=" * 50)
    print()
    print("This script will:")
    print("1. Check for Python 3.11")
    print("2. Create a clean virtual environment")
    print("3. Install compatible versions of all dependencies")
    print("4. Verify the installation works")
    print()
    
    # Step 1: Check Python 3.11
    python_cmd = check_python_version()
    if not python_cmd:
        return False
    
    # Step 2: Create virtual environment
    env_path = create_virtual_environment(python_cmd)
    if not env_path:
        return False
    
    # Step 3: Install packages
    if not install_packages(env_path):
        return False
    
    # Step 4: Verify installation
    if not verify_installation(env_path):
        print("⚠️ Installation completed but verification failed")
        print("   You may still be able to use Nougat, but there might be issues")
    
    # Step 5: Show usage instructions
    create_activation_instructions(env_path)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 Setup completed successfully!")
        else:
            print("\n❌ Setup failed")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
