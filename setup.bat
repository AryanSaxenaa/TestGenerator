@echo off
echo Setting up C++ Unit Test Generator environment...

REM Check if Python 3 is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python 3 is required but not installed.
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: pip is required but not installed.
    pause
    exit /b 1
)

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Check if CMake is installed
cmake --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: CMake is not installed. Please install CMake for building tests.
    echo Download from: https://cmake.org/download/
)

REM Check if Ollama is running (if using Ollama)
echo Checking Ollama availability...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Ollama is running and available
) else (
    echo ⚠️  Ollama is not running or not installed
    echo To install Ollama: Download from https://ollama.ai/download
)

REM Create necessary directories
if not exist "generated_tests" mkdir generated_tests
if not exist "templates" mkdir templates

echo Setup completed!
echo.
echo Usage examples:
echo   # Generate tests using Ollama (default)
echo   python src/test_generator.py --project-path ../orgChartApi --output-dir ./generated_tests
echo.
echo   # Generate tests using GitHub Models
echo   python src/test_generator.py --project-path ../orgChartApi --output-dir ./generated_tests --provider github --api-key YOUR_API_KEY
echo.
echo   # Run only specific steps
echo   python src/test_generator.py --project-path ../orgChartApi --output-dir ./generated_tests --step initial

pause
