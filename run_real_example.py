#!/usr/bin/env python3
"""
Real-world example of using the C++ Unit Test Generator with Ollama
This script checks for Ollama availability and runs the generator
"""

import subprocess
import sys
import time
from pathlib import Path

def check_ollama_availability():
    """Check if Ollama is running and has the required model"""
    try:
        # Check if Ollama is running
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/tags"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            print("❌ Ollama is not running")
            print("To start Ollama:")
            print("  1. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
            print("  2. Start Ollama: ollama serve")
            print("  3. Pull model: ollama pull llama3.2:latest")
            return False
        
        # Check if required model is available
        if "llama3.2" in result.stdout:
            print("✅ Ollama is running with llama3.2 model")
            return True
        else:
            print("⚠️  Ollama is running but llama3.2 model not found")
            print("To install the model: ollama pull llama3.2:latest")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  Ollama check timed out")
        return False
    except FileNotFoundError:
        print("❌ curl command not found")
        print("Please install curl or check Ollama manually at http://localhost:11434")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False

def run_generator_with_ollama():
    """Run the test generator using Ollama"""
    print("🚀 Running C++ Unit Test Generator with Ollama")
    print("=" * 50)
    
    # Check Ollama first
    if not check_ollama_availability():
        return False
    
    # Project paths
    project_path = str(Path("../orgChartApi").resolve())
    output_dir = "./real_generated_tests"
    
    print(f"📁 Project: {project_path}")
    print(f"📁 Output: {output_dir}")
    print()
    
    # Command to run the generator
    cmd = [
        "c:/Users/91730/Documents/KEP/.venv/Scripts/python.exe",
        "src/test_generator.py",
        "--project-path", project_path,
        "--output-dir", output_dir,
        "--provider", "ollama",
        "--model", "llama3.2:latest",
        "--temperature", "0.2",
        "--max-tokens", "4000"
    ]
    
    print("🔧 Running command:")
    print(" ".join(cmd))
    print()
    
    try:
        # Run the generator
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30 min timeout
        end_time = time.time()
        
        print(f"⏱️  Execution time: {end_time - start_time:.1f} seconds")
        print()
        
        if result.returncode == 0:
            print("✅ Test generation completed successfully!")
            print()
            print("📋 Generated files:")
            
            # List generated files
            output_path = Path(output_dir)
            if output_path.exists():
                test_files = list(output_path.glob("test_*.cpp"))
                for test_file in test_files:
                    print(f"  - {test_file.name}")
                
                print(f"\n📊 Total: {len(test_files)} test files generated")
                print(f"📁 Output directory: {output_path.resolve()}")
                
                # Show report if exists
                report_file = output_path / "test_generation_report.md"
                if report_file.exists():
                    print(f"📄 Report: {report_file}")
            
            return True
        else:
            print("❌ Test generation failed!")
            print("\nStdout:", result.stdout)
            print("\nStderr:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏱️  Test generation timed out (30 minutes)")
        return False
    except Exception as e:
        print(f"❌ Error running generator: {e}")
        return False

def run_step_by_step():
    """Run the generator step by step for better control"""
    print("🚀 Running C++ Unit Test Generator Step-by-Step")
    print("=" * 50)
    
    if not check_ollama_availability():
        return False
    
    project_path = str(Path("../orgChartApi").resolve())
    output_dir = "./step_by_step_tests"
    
    steps = [
        ("initial", "Initial test generation"),
        ("refine", "Test refinement"),
        ("build", "Build tests"),
        ("coverage", "Coverage improvement")
    ]
    
    for step, description in steps:
        print(f"🔄 Step: {description}")
        
        cmd = [
            "c:/Users/91730/Documents/KEP/.venv/Scripts/python.exe",
            "src/test_generator.py",
            "--project-path", project_path,
            "--output-dir", output_dir,
            "--provider", "ollama",
            "--model", "llama3.2:latest",
            "--step", step
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                print(f"  ✅ {description} completed")
            else:
                print(f"  ❌ {description} failed")
                print(f"  Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"  ⏱️  {description} timed out")
            return False
        except Exception as e:
            print(f"  ❌ Error in {description}: {e}")
            return False
    
    print("\n🎉 All steps completed successfully!")
    return True

def main():
    """Main entry point"""
    print("C++ Unit Test Generator - Real Usage Example")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--step-by-step":
        success = run_step_by_step()
    else:
        success = run_generator_with_ollama()
    
    if success:
        print("\n🎯 Next steps:")
        print("1. Review the generated test files")
        print("2. Install Google Test if not already installed")
        print("3. Build and run the tests:")
        print("   cd real_generated_tests/build")
        print("   cmake ..")
        print("   make")
        print("   ./run_tests")
        print("4. Check test coverage with gcov/lcov")
    else:
        print("\n🔧 Troubleshooting:")
        print("1. Ensure Ollama is running: ollama serve")
        print("2. Check model availability: ollama list")
        print("3. Pull required model: ollama pull llama3.2:latest")
        print("4. Check project path exists: ../orgChartApi")

if __name__ == "__main__":
    main()
