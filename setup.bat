@echo off
REM AI Video GPU Setup Script for Windows
echo 🧠 AI Video GPU Setup Script (Windows)
echo ==========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not installed.
    echo Please install Python 3.8 or later from https://python.org
    pause
    exit /b 1
)

echo ✓ Python detected
python --version

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is required but not installed.
    echo Please install pip and try again.
    pause
    exit /b 1
)

REM Check if NVIDIA GPU is available
nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo ⚠️  No NVIDIA GPU detected. CPU-only mode will be used.
) else (
    echo ✓ NVIDIA GPU detected
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits | findstr /n "^"
)

REM Check if FFmpeg is installed
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ❌ FFmpeg is required but not installed.
    echo Please install FFmpeg from https://ffmpeg.org/
    echo Or use chocolatey: choco install ffmpeg
    pause
    exit /b 1
)
echo ✓ FFmpeg detected

REM Create virtual environment
echo 📦 Creating Python virtual environment...
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM Install PyTorch
echo 📦 Installing PyTorch...
nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo Installing PyTorch CPU-only version...
    pip install torch torchvision torchaudio
) else (
    echo Installing PyTorch with CUDA support...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
)

REM Install other dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Create directories
echo 📁 Creating project directories...
mkdir config 2>nul
mkdir models 2>nul
mkdir output 2>nul
mkdir temp 2>nul
mkdir assets\avatars 2>nul
mkdir assets\music 2>nul
mkdir assets\voices 2>nul

REM Initialize configuration
echo ⚙️  Initializing configuration...
python main.py init

REM Test installation
echo 🧪 Testing installation...
python -c "try: from src.pipeline import AIVideoPipeline; print('✓ Installation test passed'); except Exception as e: print(f'❌ Test failed: {e}'); exit(1)"

echo.
echo 🎉 Setup completed successfully!
echo.
echo Quick start commands:
echo   venv\Scripts\activate.bat  # Activate virtual environment
echo   python main.py status      # Check system status
echo   python main.py generate "Hello world!"  # Generate first video
echo.
echo For more information, see README.md
pause
