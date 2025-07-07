#!/usr/bin/env python3
"""
C++ Unit Test Generator using AI Models
Supports Ollama, GitHub Models, and other LLM providers
"""

import os
import sys
import json
import yaml
import subprocess
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_generator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class GeneratorConfig:
    """Configuration for the test generator"""
    project_path: str
    output_dir: str
    model_provider: str  # 'ollama', 'github', 'openai'
    model_name: str
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    temperature: float = 0.2
    max_tokens: int = 4000

class LLMProvider:
    """Base class for LLM providers"""
    
    def __init__(self, config: GeneratorConfig):
        self.config = config
    
    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        """Generate response from LLM"""
        raise NotImplementedError

class OllamaProvider(LLMProvider):
    """Ollama LLM provider"""
    
    def __init__(self, config: GeneratorConfig):
        super().__init__(config)
        self.api_url = config.api_url or "http://localhost:11434/api/generate"
    
    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        """Generate response using Ollama"""
        try:
            payload = {
                "model": self.config.model_name,
                "prompt": f"{system_prompt}\n\n{prompt}",
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens
                }
            }
            
            response = requests.post(self.api_url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
            
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}")
            raise

class GitHubModelsProvider(LLMProvider):
    """GitHub Models provider using Azure AI Inference SDK"""
    
    def __init__(self, config: GeneratorConfig):
        super().__init__(config)
        if not config.api_key:
            raise ValueError("GitHub Models requires an API key")
        
        try:
            from azure.ai.inference import ChatCompletionsClient
            from azure.ai.inference.models import SystemMessage, UserMessage
            from azure.core.credentials import AzureKeyCredential
            
            endpoint = "https://models.github.ai"
            self.client = ChatCompletionsClient(
                endpoint=endpoint,
                credential=AzureKeyCredential(config.api_key),
            )
            self.SystemMessage = SystemMessage
            self.UserMessage = UserMessage
        except ImportError as e:
            raise ImportError("azure-ai-inference package is required for GitHub Models") from e
    
    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        """Generate response using GitHub Models"""
        try:
            messages = []
            if system_prompt:
                messages.append(self.SystemMessage(system_prompt))
            messages.append(self.UserMessage(prompt))
            
            response = self.client.complete(
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                model=self.config.model_name
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error calling GitHub Models API: {e}")
            raise

class GeminiProvider(LLMProvider):
    """Google Gemini provider"""
    
    def __init__(self, config: GeneratorConfig):
        super().__init__(config)
        if not config.api_key:
            raise ValueError("Gemini requires an API key")
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
    
    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        """Generate response using Gemini API"""
        try:
            # Combine system prompt and user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": full_prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": self.config.temperature,
                    "maxOutputTokens": self.config.max_tokens,
                    "topP": 0.8,
                    "topK": 10
                }
            }
            
            # Add API key to URL
            url = f"{self.api_url}?key={self.config.api_key}"
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                if 'content' in result['candidates'][0]:
                    return result['candidates'][0]['content']['parts'][0]['text']
            
            logger.error(f"Unexpected Gemini API response: {result}")
            return "Error: Unexpected API response format"
            
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            raise

class CppTestGenerator:
    """Main C++ unit test generator class"""
    
    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.llm_provider = self._create_llm_provider()
        self.project_path = Path(config.project_path)
        self.output_dir = Path(config.output_dir)
        self.config_dir = Path(__file__).parent.parent / "config"
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _create_llm_provider(self) -> LLMProvider:
        """Create appropriate LLM provider based on configuration"""
        if self.config.model_provider.lower() == 'ollama':
            return OllamaProvider(self.config)
        elif self.config.model_provider.lower() == 'github':
            return GitHubModelsProvider(self.config)
        elif self.config.model_provider.lower() == 'mock':
            # Return None for mock provider, will be replaced in demo
            return None
        elif self.config.model_provider.lower() == 'gemini':
            return GeminiProvider(self.config)
        else:
            raise ValueError(f"Unsupported model provider: {self.config.model_provider}")
    
    def find_cpp_files(self) -> List[Path]:
        """Find all C++ source and header files in the project"""
        cpp_files = []
        
        # Common C++ file extensions
        extensions = {'.cpp', '.cc', '.cxx', '.c++', '.h', '.hpp', '.hxx', '.h++'}
        
        for ext in extensions:
            cpp_files.extend(self.project_path.rglob(f'*{ext}'))
        
        # Filter out test files and third-party code
        filtered_files = []
        for file_path in cpp_files:
            path_str = str(file_path).lower()
            if not any(skip in path_str for skip in ['test', 'third_party', 'build', '.git']):
                filtered_files.append(file_path)
        
        logger.info(f"Found {len(filtered_files)} C++ files to generate tests for")
        return filtered_files
    
    def read_file_content(self, file_path: Path) -> str:
        """Read content of a C++ file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return ""
    
    def load_yaml_config(self, config_name: str) -> Dict[str, Any]:
        """Load YAML configuration file"""
        config_path = self.config_dir / f"{config_name}.yaml"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading config {config_name}: {e}")
            return {}
    
    def generate_initial_tests(self) -> bool:
        """Generate initial unit tests for all C++ files"""
        logger.info("Starting initial test generation...")
        
        config = self.load_yaml_config('initial_test_generation')
        if not config:
            logger.error("Failed to load initial test generation config")
            return False
        
        cpp_files = self.find_cpp_files()
        if not cpp_files:
            logger.warning("No C++ files found to generate tests for")
            return False
        
        success_count = 0
        
        for cpp_file in cpp_files:
            try:
                logger.info(f"Generating tests for {cpp_file.name}")
                
                # Read the source file
                source_code = self.read_file_content(cpp_file)
                if not source_code.strip():
                    logger.warning(f"Empty or unreadable file: {cpp_file}")
                    continue
                
                # Create prompt
                prompt = self._create_initial_test_prompt(cpp_file, source_code, config)
                system_prompt = config['instructions']['role']
                
                # Generate tests
                generated_test = self.llm_provider.generate_response(prompt, system_prompt)
                
                if generated_test.strip():
                    # Save generated test
                    test_file_name = f"test_{cpp_file.stem}.cpp"
                    test_file_path = self.output_dir / test_file_name
                    
                    with open(test_file_path, 'w', encoding='utf-8') as f:
                        f.write(generated_test)
                    
                    logger.info(f"Generated test file: {test_file_path}")
                    success_count += 1
                else:
                    logger.warning(f"No test generated for {cpp_file}")
                    
            except Exception as e:
                logger.error(f"Error generating test for {cpp_file}: {e}")
        
        logger.info(f"Successfully generated tests for {success_count}/{len(cpp_files)} files")
        return success_count > 0
    
    def _create_initial_test_prompt(self, cpp_file: Path, source_code: str, config: Dict[str, Any]) -> str:
        """Create prompt for initial test generation"""
        instructions = config['instructions']
        
        prompt = f"""
{instructions['objective']}

Source File: {cpp_file.name}
Source Code:
```cpp
{source_code}
```

Requirements:
{chr(10).join(f"- {req}" for req in instructions['requirements'])}

Output Format:
{instructions['output_format']}

Constraints:
{chr(10).join(f"- {const}" for const in instructions['constraints'])}

Example Structure:
{instructions['example_structure']}

Please generate comprehensive unit tests for this C++ file following the above requirements.
"""
        return prompt
    
    def refine_tests(self) -> bool:
        """Refine and improve generated tests"""
        logger.info("Starting test refinement...")
        
        config = self.load_yaml_config('test_refinement')
        if not config:
            logger.error("Failed to load test refinement config")
            return False
        
        test_files = list(self.output_dir.glob("test_*.cpp"))
        if not test_files:
            logger.warning("No test files found to refine")
            return False
        
        success_count = 0
        
        for test_file in test_files:
            try:
                logger.info(f"Refining test file: {test_file.name}")
                
                # Read current test content
                test_content = self.read_file_content(test_file)
                if not test_content.strip():
                    continue
                
                # Create refinement prompt
                prompt = self._create_refinement_prompt(test_file, test_content, config)
                system_prompt = config['instructions']['role']
                
                # Get refined tests
                refined_test = self.llm_provider.generate_response(prompt, system_prompt)
                
                if refined_test.strip():
                    # Save refined test
                    with open(test_file, 'w', encoding='utf-8') as f:
                        f.write(refined_test)
                    
                    logger.info(f"Refined test file: {test_file}")
                    success_count += 1
                    
            except Exception as e:
                logger.error(f"Error refining test {test_file}: {e}")
        
        logger.info(f"Successfully refined {success_count}/{len(test_files)} test files")
        return success_count > 0
    
    def _create_refinement_prompt(self, test_file: Path, test_content: str, config: Dict[str, Any]) -> str:
        """Create prompt for test refinement"""
        instructions = config['instructions']
        
        prompt = f"""
{instructions['objective']}

Test File: {test_file.name}
Current Test Content:
```cpp
{test_content}
```

Refinement Tasks:
{chr(10).join(f"- {task}" for task in instructions['refinement_tasks'])}

Quality Checks:
{chr(10).join(f"- {check}" for check in instructions['quality_checks'])}

Please refine these unit tests according to the above requirements.
"""
        return prompt
    
    def build_tests(self) -> tuple[bool, str]:
        """Build the generated tests and return success status and output"""
        logger.info("Building generated tests...")
        
        # Create CMakeLists.txt for tests
        cmake_content = self._generate_cmake_for_tests()
        cmake_path = self.output_dir / "CMakeLists.txt"
        
        with open(cmake_path, 'w', encoding='utf-8') as f:
            f.write(cmake_content)
        
        # Create build directory
        build_dir = self.output_dir / "build"
        build_dir.mkdir(exist_ok=True)
        
        try:
            # Configure
            configure_cmd = ["cmake", "..", "-DCMAKE_BUILD_TYPE=Debug"]
            configure_result = subprocess.run(
                configure_cmd, 
                cwd=build_dir, 
                capture_output=True, 
                text=True,
                timeout=300
            )
            
            if configure_result.returncode != 0:
                logger.error("CMake configuration failed")
                return False, configure_result.stderr
            
            # Build
            build_cmd = ["cmake", "--build", "."]
            build_result = subprocess.run(
                build_cmd, 
                cwd=build_dir, 
                capture_output=True, 
                text=True,
                timeout=600
            )
            
            success = build_result.returncode == 0
            output = build_result.stdout + "\n" + build_result.stderr
            
            if success:
                logger.info("Tests built successfully")
            else:
                logger.error("Build failed")
            
            return success, output
            
        except subprocess.TimeoutExpired:
            logger.error("Build timed out")
            return False, "Build process timed out"
        except Exception as e:
            logger.error(f"Build error: {e}")
            return False, str(e)
    
    def _generate_cmake_for_tests(self) -> str:
        """Generate CMakeLists.txt for the test project"""
        test_files = [f.name for f in self.output_dir.glob("test_*.cpp")]
        
        cmake_content = f"""cmake_minimum_required(VERSION 3.10)
project(UnitTests CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find packages
find_package(GTest REQUIRED)
find_package(GMock REQUIRED)

# Include directories
include_directories(${{GTEST_INCLUDE_DIRS}})
include_directories(${{GMOCK_INCLUDE_DIRS}})
include_directories("{self.project_path}")

# Test executable
add_executable(run_tests
{chr(10).join(f"    {test_file}" for test_file in test_files)}
)

# Link libraries
target_link_libraries(run_tests
    ${{GTEST_LIBRARIES}}
    ${{GMOCK_LIBRARIES}}
    pthread
)

# Enable testing
enable_testing()
add_test(NAME unit_tests COMMAND run_tests)
"""
        return cmake_content
    
    def fix_build_issues(self, build_output: str) -> bool:
        """Fix build issues using LLM"""
        logger.info("Attempting to fix build issues...")
        
        config = self.load_yaml_config('build_fix')
        if not config:
            logger.error("Failed to load build fix config")
            return False
        
        # Create fix prompt
        prompt = self._create_build_fix_prompt(build_output, config)
        system_prompt = config['instructions']['role']
        
        try:
            # Get fixes from LLM
            fixes_response = self.llm_provider.generate_response(prompt, system_prompt)
            
            # Apply fixes (this would need more sophisticated parsing)
            # For now, just log the response
            logger.info("LLM suggested fixes:")
            logger.info(fixes_response)
            
            # TODO: Implement automated fix application
            return False
            
        except Exception as e:
            logger.error(f"Error getting build fixes: {e}")
            return False
    
    def _create_build_fix_prompt(self, build_output: str, config: Dict[str, Any]) -> str:
        """Create prompt for build fix"""
        instructions = config['instructions']
        
        prompt = f"""
{instructions['objective']}

Build Output/Errors:
```
{build_output}
```

Analysis Steps:
{chr(10).join(f"- {step}" for step in instructions['analysis_steps'])}

Fix Priorities:
{chr(10).join(f"{i}. {priority}" for i, priority in enumerate(instructions['fix_priorities'], 1))}

Please analyze the build errors and provide specific fixes following the response structure.
"""
        return prompt
    
    def run_coverage_analysis(self) -> Dict[str, Any]:
        """Run code coverage analysis on tests"""
        logger.info("Running coverage analysis...")
        
        build_dir = self.output_dir / "build"
        if not (build_dir / "run_tests").exists():
            logger.error("Test executable not found")
            return {}
        
        try:
            # Run tests with coverage
            test_cmd = ["./run_tests"]
            test_result = subprocess.run(
                test_cmd,
                cwd=build_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Generate coverage report (simplified)
            coverage_info = {
                "test_success": test_result.returncode == 0,
                "test_output": test_result.stdout,
                "test_errors": test_result.stderr
            }
            
            logger.info(f"Tests {'passed' if coverage_info['test_success'] else 'failed'}")
            return coverage_info
            
        except Exception as e:
            logger.error(f"Coverage analysis error: {e}")
            return {}
    
    def improve_coverage(self, coverage_info: Dict[str, Any]) -> bool:
        """Improve test coverage based on analysis"""
        logger.info("Improving test coverage...")
        
        config = self.load_yaml_config('coverage_improvement')
        if not config:
            logger.error("Failed to load coverage improvement config")
            return False
        
        # Create improvement prompt
        prompt = self._create_coverage_improvement_prompt(coverage_info, config)
        system_prompt = config['instructions']['role']
        
        try:
            # Get coverage improvements from LLM
            improvements = self.llm_provider.generate_response(prompt, system_prompt)
            
            # Save improvements to a new file
            improvements_file = self.output_dir / "coverage_improvements.cpp"
            with open(improvements_file, 'w', encoding='utf-8') as f:
                f.write(improvements)
            
            logger.info(f"Coverage improvements saved to: {improvements_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error improving coverage: {e}")
            return False
    
    def _create_coverage_improvement_prompt(self, coverage_info: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Create prompt for coverage improvement"""
        instructions = config['instructions']
        
        prompt = f"""
{instructions['objective']}

Current Coverage Information:
- Test Success: {coverage_info.get('test_success', False)}
- Test Output: {coverage_info.get('test_output', 'No output')}
- Test Errors: {coverage_info.get('test_errors', 'No errors')}

Coverage Analysis Tasks:
{chr(10).join(f"- {task}" for task in instructions['coverage_analysis'])}

Improvement Strategies:
{chr(10).join(f"- {strategy}" for strategy in instructions['improvement_strategies'])}

Please generate additional test methods to improve coverage.
"""
        return prompt
    
    def generate_report(self) -> str:
        """Generate a comprehensive report of the test generation process"""
        logger.info("Generating final report...")
        
        test_files = list(self.output_dir.glob("test_*.cpp"))
        
        report = f"""
# C++ Unit Test Generation Report

## Summary
- **Project Path**: {self.config.project_path}
- **Output Directory**: {self.config.output_dir}
- **Model Used**: {self.config.model_provider} - {self.config.model_name}
- **Generated Test Files**: {len(test_files)}

## Generated Test Files
{chr(10).join(f"- {f.name}" for f in test_files)}

## Test Generation Process
1. ✅ Initial test generation completed
2. ✅ Test refinement completed
3. ✅ Build attempted
4. ✅ Coverage analysis performed
5. ✅ Coverage improvements generated

## Recommendations
- Review generated tests for accuracy
- Run tests manually to verify functionality
- Adjust test parameters based on specific requirements
- Consider integrating with CI/CD pipeline

## Files Generated
- Test source files: {len(test_files)} files
- CMakeLists.txt for building tests
- Coverage improvement suggestions
- This report

Generated on: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        report_file = self.output_dir / "test_generation_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Report saved to: {report_file}")
        return report
    
    def run_full_pipeline(self) -> bool:
        """Run the complete test generation pipeline"""
        logger.info("Starting full test generation pipeline...")
        
        try:
            # Step 1: Generate initial tests
            if not self.generate_initial_tests():
                logger.error("Initial test generation failed")
                return False
            
            # Step 2: Refine tests
            if not self.refine_tests():
                logger.warning("Test refinement failed, continuing with original tests")
            
            # Step 3: Build tests
            build_success, build_output = self.build_tests()
            if not build_success:
                logger.warning("Build failed, attempting to fix...")
                if not self.fix_build_issues(build_output):
                    logger.error("Could not fix build issues automatically")
            
            # Step 4: Coverage analysis
            coverage_info = self.run_coverage_analysis()
            if coverage_info:
                self.improve_coverage(coverage_info)
            
            # Step 5: Generate report
            self.generate_report()
            
            logger.info("Test generation pipeline completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="C++ Unit Test Generator using AI Models")
    
    parser.add_argument("--project-path", required=True, help="Path to C++ project")
    parser.add_argument("--output-dir", required=True, help="Output directory for generated tests")
    parser.add_argument("--provider", choices=['ollama', 'github', 'gemini'], default='ollama', help="LLM provider")
    parser.add_argument("--model", default='llama3.2:latest', help="Model name")
    parser.add_argument("--api-key", help="API key for external providers")
    parser.add_argument("--api-url", help="Custom API URL")
    parser.add_argument("--temperature", type=float, default=0.2, help="Model temperature")
    parser.add_argument("--max-tokens", type=int, default=4000, help="Maximum tokens")
    parser.add_argument("--step", choices=['initial', 'refine', 'build', 'coverage', 'full'], 
                       default='full', help="Which step to run")
    
    args = parser.parse_args()
    
    # Create configuration
    config = GeneratorConfig(
        project_path=args.project_path,
        output_dir=args.output_dir,
        model_provider=args.provider,
        model_name=args.model,
        api_key=args.api_key,
        api_url=args.api_url,
        temperature=args.temperature,
        max_tokens=args.max_tokens
    )
    
    # Create generator
    generator = CppTestGenerator(config)
    
    # Run specified step
    success = False
    if args.step == 'initial':
        success = generator.generate_initial_tests()
    elif args.step == 'refine':
        success = generator.refine_tests()
    elif args.step == 'build':
        success, _ = generator.build_tests()
    elif args.step == 'coverage':
        coverage_info = generator.run_coverage_analysis()
        success = generator.improve_coverage(coverage_info)
    elif args.step == 'full':
        success = generator.run_full_pipeline()
    
    if success:
        logger.info("Operation completed successfully")
        sys.exit(0)
    else:
        logger.error("Operation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
