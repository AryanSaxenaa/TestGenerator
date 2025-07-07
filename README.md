# C++ Unit Test Generator using AI Models

This project implements an AI-powered unit test generator for C++ applications, specifically designed to work with the [orgChartApi](https://github.com/keploy/orgChartApi) project. The tool uses large language models (LLMs) like Gemini 2.5 Pro to automatically generate comprehensive unit tests.


## Architecture

The system follows a multi-stage pipeline architecture:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   C++ Project   │───▶│  Initial Test    │───▶│  Test Refining  │
│   Source Code   │    │   Generation     │    │   & Cleanup     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Coverage Report │◀───│   Build & Test   │◀───│  Generated      │
│ & Improvements  │    │   Execution      │    │  Test Files     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Features

- 🤖 **AI-Powered Generation**: Uses LLMs to generate comprehensive unit tests
- 🔄 **Iterative Refinement**: Automatically improves tests through multiple passes
- 🛠️ **Build Integration**: Attempts to build tests and fix compilation issues
- 📊 **Coverage Analysis**: Analyzes test coverage and suggests improvements
- 🎯 **Multiple Providers**: Supports Ollama, GitHub Models, and OpenAI
- ⚙️ **Configurable**: YAML-based configuration for fine-tuning generation
- 🧪 **Google Test**: Generates tests using the Google Test framework

## Prerequisites

### Required Software
- **Python 3.8+**
- **CMake 3.10+**
- **C++ Compiler** (GCC, Clang, or MSVC)
- **Google Test Library**


## Installation

1. **Clone the repository**:
   ```bash
   git clone <this-repository>
   cd unit-test-generator
   ```

2. **Install dependencies**:
   
   **Linux/macOS:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
   
   **Windows:**
   ```cmd
   setup.bat
   ```

3. **Install Google Test** (if not already installed):
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt-get install libgtest-dev libgmock-dev
   ```
   
   **macOS:**
   ```bash
   brew install googletest
   ```
   
   **Windows:**
   - Download and build Google Test manually
   - Or use vcpkg: `vcpkg install gtest`

## Usage

### Basic Usage

Generate tests for the orgChartApi project 

```bash
python src/test_generator.py \
  --project-path ../orgChartApi \
  --output-dir ./generated_tests
```

### Advanced Usage

#### Using GitHub Models
```bash
python src/test_generator.py \
  --project-path ../orgChartApi \
  --output-dir ./generated_tests \
  --provider github \
  --model gpt-4 \
  --api-key YOUR_GITHUB_API_KEY
```

#### Running Specific Steps
```bash
# Only generate initial tests
python src/test_generator.py \
  --project-path ../orgChartApi \
  --output-dir ./generated_tests \
  --step initial

# Only refine existing tests
python src/test_generator.py \
  --project-path ../orgChartApi \
  --output-dir ./generated_tests \
  --step refine

# Only build tests
python src/test_generator.py \
  --project-path ../orgChartApi \
  --output-dir ./generated_tests \
  --step build
```

#### Custom Configuration
```bash
python src/test_generator.py \
  --project-path ../orgChartApi \
  --output-dir ./generated_tests \
  --temperature 0.1 \
  --max-tokens 5000
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--project-path` | Path to the C++ project | Required |
| `--output-dir` | Output directory for generated tests | Required |
| `--provider` | LLM provider (ollama, github) | ollama |
| `--model` | Model name | llama3.2:latest |
| `--api-key` | API key for external providers | None |
| `--api-url` | Custom API URL | None |
| `--temperature` | Model temperature (0.0-1.0) | 0.2 |
| `--max-tokens` | Maximum tokens per request | 4000 |
| `--step` | Specific step to run | full |

## Configuration

The tool uses YAML configuration files in the `config/` directory:

### Initial Test Generation (`config/initial_test_generation.yaml`)
Controls the initial test generation process, including:
- Test framework selection
- Coverage requirements
- Code style preferences
- Output format

### Test Refinement (`config/test_refinement.yaml`)
Defines refinement criteria:
- Duplicate removal
- Code quality improvements
- Library optimization
- Test structure enhancement

### Build Fix (`config/build_fix.yaml`)
Handles build issue resolution:
- Compiler error analysis
- Dependency resolution
- API compatibility fixes

### Coverage Improvement (`config/coverage_improvement.yaml`)
Guides coverage enhancement:
- Uncovered code identification
- Additional test generation
- Edge case testing

## Generated Output

The tool generates the following files in the output directory:

```
generated_tests/
├── test_Person.cpp              # Test for Person model
├── test_PersonsController.cpp   # Test for PersonsController
├── test_Department.cpp          # Test for Department model
├── test_Job.cpp                 # Test for Job model
├── CMakeLists.txt              # Build configuration
├── build/                      # Build artifacts
├── coverage_improvements.cpp   # Additional test suggestions
└── test_generation_report.md   # Comprehensive report
```

### Example Generated Test

```cpp
#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include "controllers/PersonsController.h"

class PersonsControllerTest : public ::testing::Test {
protected:
    void SetUp() override {
        controller = std::make_unique<PersonsController>();
    }
    
    void TearDown() override {
        controller.reset();
    }
    
    std::unique_ptr<PersonsController> controller;
};

TEST_F(PersonsControllerTest, GetPersons_ValidRequest_ReturnsPersonList) {
    // Test implementation
    auto request = HttpRequest::newHttpRequest();
    bool callbackCalled = false;
    
    controller->get(request, [&](const HttpResponsePtr& response) {
        EXPECT_NE(response, nullptr);
        EXPECT_EQ(response->getStatusCode(), k200OK);
        callbackCalled = true;
    });
    
    EXPECT_TRUE(callbackCalled);
}

TEST_F(PersonsControllerTest, GetPerson_InvalidId_ReturnsNotFound) {
    // Test invalid person ID
    auto request = HttpRequest::newHttpRequest();
    bool callbackCalled = false;
    
    controller->getOne(request, [&](const HttpResponsePtr& response) {
        EXPECT_NE(response, nullptr);
        EXPECT_EQ(response->getStatusCode(), k404NotFound);
        callbackCalled = true;
    }, -1);
    
    EXPECT_TRUE(callbackCalled);
}
```

## Workflow Steps

### 1. Initial Test Generation
- Scans C++ project for source files
- Generates comprehensive unit tests for each file
- Uses AI to understand code structure and create appropriate tests
- Saves tests in separate files following naming convention

### 2. Test Refinement
- Reviews generated tests for quality
- Removes duplicate test cases
- Adds missing library includes
- Optimizes test structure and readability
- Ensures proper use of Google Test features

### 3. Build and Debug
- Creates CMakeLists.txt for the test project
- Attempts to build the generated tests
- If build fails, uses AI to analyze and fix compilation errors
- Iterates until tests compile successfully

### 4. Coverage Analysis
- Runs the generated tests
- Analyzes code coverage using gcov/lcov
- Identifies uncovered code paths
- Generates additional tests to improve coverage

### 5. Final Output
- Produces final test suite with proper formatting
- Generates comprehensive report
- Provides recommendations for further improvements

## Project Structure

```
unit-test-generator/
├── src/
│   └── test_generator.py      # Main generator script
├── config/
│   ├── initial_test_generation.yaml
│   ├── test_refinement.yaml
│   ├── build_fix.yaml
│   ├── coverage_improvement.yaml
│   └── project_config.json
├── templates/                 # Template files (future use)
├── generated_tests/          # Output directory
├── requirements.txt          # Python dependencies
├── setup.sh                 # Linux/macOS setup script
├── setup.bat                # Windows setup script
└── README.md                # This file
```

## Integration with GNU Code Coverage

The tool integrates with GNU coverage tools:

1. **gcov**: For basic coverage analysis
2. **lcov**: For HTML coverage reports
3. **genhtml**: For generating visual coverage reports

To enable coverage analysis:

```bash
# Build with coverage flags
cmake -DCMAKE_CXX_FLAGS="--coverage" ..
make

# Run tests
./run_tests

# Generate coverage report
lcov --capture --directory . --output-file coverage.info
genhtml coverage.info --output-directory coverage_html
```

## Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   ```bash
   # Ensure Ollama is running
   ollama serve
   
   # Check if model is available
   ollama list
   ```

2. **Google Test Not Found**
   ```bash
   # Install on Ubuntu/Debian
   sudo apt-get install libgtest-dev libgmock-dev
   
   # Install on macOS
   brew install googletest
   ```

3. **CMake Configuration Failed**
   ```bash
   # Update CMake to latest version
   # Check CMakeLists.txt for correct paths
   ```

4. **Compilation Errors**
   - Check that all dependencies are installed
   - Verify C++ standard compatibility
   - Review generated test code for syntax errors

### Debugging

Enable verbose logging by setting the log level:

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Future Enhancements

- [ ] Support for Catch2 testing framework
- [ ] Integration with more AI providers
- [ ] Automated CI/CD pipeline integration
- [ ] Visual coverage reporting dashboard
- [ ] Performance testing capabilities
- [ ] Mocking framework integration
- [ ] Custom test templates
- [ ] Batch processing for multiple projects

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Keploy orgChartApi](https://github.com/keploy/orgChartApi) - Target C++ project
- [Google Test](https://github.com/google/googletest) - Testing framework
- [Drogon Framework](https://github.com/drogonframework/drogon) - Web framework used in target project
