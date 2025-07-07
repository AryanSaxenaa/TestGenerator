#!/bin/bash

# Setup script for C++ Unit Test Generator
echo "Setting up C++ Unit Test Generator environment..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "Error: pip is required but not installed."
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Check if CMake is installed
if ! command -v cmake &> /dev/null; then
    echo "Warning: CMake is not installed. Please install CMake for building tests."
    echo "On Ubuntu/Debian: sudo apt-get install cmake"
    echo "On macOS: brew install cmake"
    echo "On Windows: Download from https://cmake.org/download/"
fi

# Check if Google Test is available
echo "Checking for Google Test..."
if ! pkg-config --exists gtest; then
    echo "Warning: Google Test not found via pkg-config."
    echo "You may need to install Google Test:"
    echo "On Ubuntu/Debian: sudo apt-get install libgtest-dev libgmock-dev"
    echo "On macOS: brew install googletest"
fi

# Check if Ollama is running (if using Ollama)
echo "Checking Ollama availability..."
if curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "✅ Ollama is running and available"
    
    # Check if required model is available
    if curl -s http://localhost:11434/api/tags | grep -q "llama3.2"; then
        echo "✅ llama3.2 model is available"
    else
        echo "⚠️  llama3.2 model not found. Run: ollama pull llama3.2"
    fi
else
    echo "⚠️  Ollama is not running or not installed"
    echo "To install Ollama: curl -fsSL https://ollama.ai/install.sh | sh"
    echo "To start Ollama: ollama serve"
fi

# Create necessary directories
mkdir -p generated_tests
mkdir -p templates

echo "Setup completed!"
echo ""
echo "Usage examples:"
echo "  # Generate tests using Ollama (default)"
echo "  python3 src/test_generator.py --project-path ../orgChartApi --output-dir ./generated_tests"
echo ""
echo "  # Generate tests using GitHub Models"
echo "  python3 src/test_generator.py --project-path ../orgChartApi --output-dir ./generated_tests --provider github --api-key YOUR_API_KEY"
echo ""
echo "  # Run only specific steps"
echo "  python3 src/test_generator.py --project-path ../orgChartApi --output-dir ./generated_tests --step initial"
