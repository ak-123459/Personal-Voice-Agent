#!/usr/bin/env python3
"""
Setup script for AI Voice Assistant
Helps automate the installation and configuration process
"""

import subprocess
import sys
import os
import platform


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def check_python_version():
    """Check if Python version is adequate"""
    print_header("Checking Python Version")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")


def install_dependencies():
    """Install required Python packages"""
    print_header("Installing Dependencies")

    packages = [
        "websockets==12.0",
        "SpeechRecognition==3.10.0",
        "pyttsx3==2.90",
        "openai==1.12.0",
        "python-dotenv==1.0.0"
    ]

    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"⚠️  Failed to install {package}")


def install_pyaudio():
    """Install PyAudio with platform-specific instructions"""
    print_header("Installing PyAudio")

    system = platform.system()

    if system == "Windows":
        print("Installing PyAudio for Windows...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pipwin"])
            subprocess.check_call([sys.executable, "-m", "pipwin", "install", "pyaudio"])
            print("✅ PyAudio installed successfully")
        except subprocess.CalledProcessError:
            print("⚠️  PyAudio installation failed. Try manual installation:")
            print("   pip install pipwin")
            print("   pipwin install pyaudio")

    elif system == "Darwin":  # macOS
        print("Installing PyAudio for macOS...")
        print("Please install portaudio first:")
        print("   brew install portaudio")
        input("Press Enter after installing portaudio...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyaudio"])
            print("✅ PyAudio installed successfully")
        except subprocess.CalledProcessError:
            print("⚠️  PyAudio installation failed")

    elif system == "Linux":
        print("Installing PyAudio for Linux...")
        print("Please install dependencies first:")
        print("   sudo apt-get install portaudio19-dev python3-pyaudio")
        input("Press Enter after installing dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyaudio"])
            print("✅ PyAudio installed successfully")
        except subprocess.CalledProcessError:
            print("⚠️  PyAudio installation failed")


def setup_env_file():
    """Create .env file if it doesn't exist"""
    print_header("Setting up Environment Variables")

    if os.path.exists(".env"):
        print("✅ .env file already exists")
        return

    print("Creating .env file...")
    api_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()

    with open(".env", "w") as f:
        if api_key:
            f.write(f"OPENAI_API_KEY={api_key}\n")
            print("✅ .env file created with API key")
        else:
            f.write("OPENAI_API_KEY=your-openai-api-key-here\n")
            print("⚠️  .env file created. Please add your API key manually")


def create_files():
    """Create necessary project files"""
    print_header("Checking Project Files")

    files = ["server.py", "index.html", "requirements.txt"]
    missing_files = [f for f in files if not os.path.exists(f)]

    if missing_files:
        print(f"⚠️  Missing files: {', '.join(missing_files)}")
        print("   Please ensure all project files are in the directory")
    else:
        print("✅ All project files present")


def print_next_steps():
    """Print instructions for running the project"""
    print_header("Setup Complete!")

    print("Next steps:")
    print("\n1. Make sure your OpenAI API key is set in .env file")
    print("   Edit .env and add: OPENAI_API_KEY=your-actual-key")
    print("\n2. Start the server:")
    print("   python server.py")
    print("\n3. Open index.html in your browser")
    print("\n4. Start talking to your AI assistant!")
    print("\n" + "=" * 60 + "\n")


def main():
    """Main setup function"""
    print_header("AI Voice Assistant - Setup")

    try:
        check_python_version()
        install_dependencies()
        install_pyaudio()
        setup_env_file()
        create_files()
        print_next_steps()

    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()