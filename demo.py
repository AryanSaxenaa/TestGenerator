#!/usr/bin/env python3
"""
Demo script for the C++ Unit Test Generator
This demonstrates the test generator with mock responses when LLM is not available
"""

import os
import sys
import json
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from test_generator import CppTestGenerator, GeneratorConfig, OllamaProvider

class MockLLMProvider:
    """Mock LLM provider for demonstration purposes"""
    
    def __init__(self, config):
        self.config = config
    
    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        """Generate mock response based on the prompt type"""
        
        if "test_main.cpp" in prompt or "main.cc" in prompt:
            return self._generate_main_test()
        elif "PersonsController" in prompt:
            return self._generate_controller_test()
        elif "Person.h" in prompt or "Person model" in prompt:
            return self._generate_person_test()
        elif "Department" in prompt:
            return self._generate_department_test()
        elif "refinement" in prompt.lower() or "refine" in prompt.lower():
            return self._generate_refinement_response()
        elif "build" in prompt.lower() or "error" in prompt.lower():
            return self._generate_build_fix()
        elif "coverage" in prompt.lower():
            return self._generate_coverage_improvement()
        else:
            return self._generate_generic_test()
    
    def _generate_main_test(self) -> str:
        return '''#include <gtest/gtest.h>
#include <gmock/gmock.h>

// Note: main.cc primarily contains application startup code
// These tests focus on testable components and initialization

class MainAppTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Setup test environment
    }
    
    void TearDown() override {
        // Cleanup
    }
};

TEST_F(MainAppTest, ApplicationStartup_ValidConfig_InitializesSuccessfully) {
    // Test that the application can be initialized with valid configuration
    // This is a placeholder test as main() primarily starts the server
    EXPECT_TRUE(true); // Placeholder assertion
}

TEST_F(MainAppTest, ConfigFile_Loading_ReturnsValidConfiguration) {
    // Test configuration file loading
    // This would need to be extracted into a testable function
    EXPECT_TRUE(true); // Placeholder assertion
}

// Note: For better testability, consider extracting application logic
// from main() into separate, testable functions
'''
    
    def _generate_controller_test(self) -> str:
        return '''#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include <drogon/HttpRequest.h>
#include <drogon/HttpResponse.h>
#include "controllers/PersonsController.h"
#include "models/Person.h"

using namespace drogon;
using namespace drogon_model::org_chart;

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

TEST_F(PersonsControllerTest, GetPersons_ValidRequest_ReturnsSuccess) {
    auto request = HttpRequest::newHttpRequest();
    bool callbackCalled = false;
    
    controller->get(request, [&](const HttpResponsePtr& response) {
        EXPECT_NE(response, nullptr);
        EXPECT_EQ(response->getStatusCode(), k200OK);
        callbackCalled = true;
    });
    
    // Note: This test may need database mocking for complete isolation
    EXPECT_TRUE(callbackCalled);
}

TEST_F(PersonsControllerTest, GetOnePerson_ValidId_ReturnsPersonData) {
    auto request = HttpRequest::newHttpRequest();
    bool callbackCalled = false;
    int testPersonId = 1;
    
    controller->getOne(request, [&](const HttpResponsePtr& response) {
        EXPECT_NE(response, nullptr);
        // Response code depends on whether person exists in test database
        callbackCalled = true;
    }, testPersonId);
    
    EXPECT_TRUE(callbackCalled);
}

TEST_F(PersonsControllerTest, GetOnePerson_InvalidId_ReturnsNotFound) {
    auto request = HttpRequest::newHttpRequest();
    bool callbackCalled = false;
    int invalidPersonId = -1;
    
    controller->getOne(request, [&](const HttpResponsePtr& response) {
        EXPECT_NE(response, nullptr);
        EXPECT_EQ(response->getStatusCode(), k404NotFound);
        callbackCalled = true;
    }, invalidPersonId);
    
    EXPECT_TRUE(callbackCalled);
}

TEST_F(PersonsControllerTest, CreatePerson_ValidData_ReturnsCreated) {
    auto request = HttpRequest::newHttpRequest();
    request->setContentTypeCode(CT_APPLICATION_JSON);
    
    Person newPerson;
    // Set person data for test
    
    bool callbackCalled = false;
    
    controller->createOne(request, [&](const HttpResponsePtr& response) {
        EXPECT_NE(response, nullptr);
        // Expected status code: k201Created or appropriate response
        callbackCalled = true;
    }, std::move(newPerson));
    
    EXPECT_TRUE(callbackCalled);
}

TEST_F(PersonsControllerTest, UpdatePerson_ValidData_ReturnsSuccess) {
    auto request = HttpRequest::newHttpRequest();
    request->setContentTypeCode(CT_APPLICATION_JSON);
    
    Person updatedPerson;
    int testPersonId = 1;
    bool callbackCalled = false;
    
    controller->updateOne(request, [&](const HttpResponsePtr& response) {
        EXPECT_NE(response, nullptr);
        callbackCalled = true;
    }, testPersonId, std::move(updatedPerson));
    
    EXPECT_TRUE(callbackCalled);
}

TEST_F(PersonsControllerTest, DeletePerson_ValidId_ReturnsSuccess) {
    auto request = HttpRequest::newHttpRequest();
    int testPersonId = 1;
    bool callbackCalled = false;
    
    controller->deleteOne(request, [&](const HttpResponsePtr& response) {
        EXPECT_NE(response, nullptr);
        callbackCalled = true;
    }, testPersonId);
    
    EXPECT_TRUE(callbackCalled);
}

TEST_F(PersonsControllerTest, GetDirectReports_ValidManagerId_ReturnsReports) {
    auto request = HttpRequest::newHttpRequest();
    int managerId = 1;
    bool callbackCalled = false;
    
    controller->getDirectReports(request, [&](const HttpResponsePtr& response) {
        EXPECT_NE(response, nullptr);
        EXPECT_EQ(response->getStatusCode(), k200OK);
        callbackCalled = true;
    }, managerId);
    
    EXPECT_TRUE(callbackCalled);
}

TEST_F(PersonsControllerTest, GetDirectReports_InvalidManagerId_ReturnsNotFound) {
    auto request = HttpRequest::newHttpRequest();
    int invalidManagerId = -1;
    bool callbackCalled = false;
    
    controller->getDirectReports(request, [&](const HttpResponsePtr& response) {
        EXPECT_NE(response, nullptr);
        EXPECT_EQ(response->getStatusCode(), k404NotFound);
        callbackCalled = true;
    }, invalidManagerId);
    
    EXPECT_TRUE(callbackCalled);
}
'''
    
    def _generate_person_test(self) -> str:
        return '''#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include "models/Person.h"
#include <json/json.h>

using namespace drogon_model::org_chart;

class PersonTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Initialize test person data
        person = std::make_unique<Person>();
    }
    
    void TearDown() override {
        person.reset();
    }
    
    std::unique_ptr<Person> person;
};

TEST_F(PersonTest, Constructor_DefaultConstruction_CreatesValidObject) {
    EXPECT_NE(person, nullptr);
    // Test default values if any
}

TEST_F(PersonTest, SetId_ValidId_StoresCorrectly) {
    int testId = 123;
    person->setId(testId);
    EXPECT_EQ(person->getValueOfId(), testId);
}

TEST_F(PersonTest, SetFirstName_ValidName_StoresCorrectly) {
    std::string firstName = "John";
    person->setFirstName(firstName);
    EXPECT_EQ(person->getValueOfFirstName(), firstName);
}

TEST_F(PersonTest, SetFirstName_EmptyString_HandlesGracefully) {
    std::string emptyName = "";
    person->setFirstName(emptyName);
    EXPECT_EQ(person->getValueOfFirstName(), emptyName);
}

TEST_F(PersonTest, SetLastName_ValidName_StoresCorrectly) {
    std::string lastName = "Doe";
    person->setLastName(lastName);
    EXPECT_EQ(person->getValueOfLastName(), lastName);
}

TEST_F(PersonTest, SetHireDate_ValidDate_StoresCorrectly) {
    trantor::Date hireDate(2024, 1, 15);
    person->setHireDate(hireDate);
    EXPECT_EQ(person->getValueOfHireDate(), hireDate);
}

TEST_F(PersonTest, SetJobId_ValidJobId_StoresCorrectly) {
    int jobId = 456;
    person->setJobId(jobId);
    EXPECT_EQ(person->getValueOfJobId(), jobId);
}

TEST_F(PersonTest, SetDepartmentId_ValidDepartmentId_StoresCorrectly) {
    int deptId = 789;
    person->setDepartmentId(deptId);
    EXPECT_EQ(person->getValueOfDepartmentId(), deptId);
}

TEST_F(PersonTest, SetManagerId_ValidManagerId_StoresCorrectly) {
    int managerId = 101;
    person->setManagerId(managerId);
    EXPECT_EQ(person->getValueOfManagerId(), managerId);
}

TEST_F(PersonTest, SetManagerId_NullManager_HandlesCorrectly) {
    // Test setting manager to null/empty
    person->setManagerIdToNull();
    EXPECT_TRUE(person->getManagerId().empty());
}

TEST_F(PersonTest, ToJson_ValidPerson_ReturnsValidJson) {
    // Set up person data
    person->setId(1);
    person->setFirstName("John");
    person->setLastName("Doe");
    person->setJobId(2);
    person->setDepartmentId(3);
    
    Json::Value json = person->toJson();
    
    EXPECT_FALSE(json.isNull());
    EXPECT_EQ(json["id"].asInt(), 1);
    EXPECT_EQ(json["first_name"].asString(), "John");
    EXPECT_EQ(json["last_name"].asString(), "Doe");
}

TEST_F(PersonTest, FromJson_ValidJson_CreatesCorrectPerson) {
    Json::Value json;
    json["id"] = 1;
    json["first_name"] = "Jane";
    json["last_name"] = "Smith";
    json["job_id"] = 2;
    json["department_id"] = 3;
    
    // Assuming fromJson method exists
    // person->fromJson(json);
    
    // EXPECT_EQ(person->getValueOfId(), 1);
    // EXPECT_EQ(person->getValueOfFirstName(), "Jane");
    // EXPECT_EQ(person->getValueOfLastName(), "Smith");
}

TEST_F(PersonTest, Equality_SamePersonData_ReturnsTrue) {
    Person person1, person2;
    
    person1.setId(1);
    person1.setFirstName("John");
    person1.setLastName("Doe");
    
    person2.setId(1);
    person2.setFirstName("John");
    person2.setLastName("Doe");
    
    // Assuming equality operator exists
    // EXPECT_EQ(person1, person2);
}

TEST_F(PersonTest, CopyConstructor_ValidPerson_CreatesCorrectCopy) {
    person->setId(1);
    person->setFirstName("John");
    person->setLastName("Doe");
    
    Person copiedPerson(*person);
    
    EXPECT_EQ(copiedPerson.getValueOfId(), person->getValueOfId());
    EXPECT_EQ(copiedPerson.getValueOfFirstName(), person->getValueOfFirstName());
    EXPECT_EQ(copiedPerson.getValueOfLastName(), person->getValueOfLastName());
}
'''
    
    def _generate_department_test(self) -> str:
        return '''#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include "models/Department.h"

using namespace drogon_model::org_chart;

class DepartmentTest : public ::testing::Test {
protected:
    void SetUp() override {
        department = std::make_unique<Department>();
    }
    
    void TearDown() override {
        department.reset();
    }
    
    std::unique_ptr<Department> department;
};

TEST_F(DepartmentTest, Constructor_DefaultConstruction_CreatesValidObject) {
    EXPECT_NE(department, nullptr);
}

TEST_F(DepartmentTest, SetId_ValidId_StoresCorrectly) {
    int testId = 42;
    department->setId(testId);
    EXPECT_EQ(department->getValueOfId(), testId);
}

TEST_F(DepartmentTest, SetName_ValidName_StoresCorrectly) {
    std::string deptName = "Engineering";
    department->setName(deptName);
    EXPECT_EQ(department->getValueOfName(), deptName);
}

TEST_F(DepartmentTest, SetName_EmptyString_HandlesGracefully) {
    std::string emptyName = "";
    department->setName(emptyName);
    EXPECT_EQ(department->getValueOfName(), emptyName);
}

TEST_F(DepartmentTest, SetManagerId_ValidManagerId_StoresCorrectly) {
    int managerId = 100;
    department->setManagerId(managerId);
    EXPECT_EQ(department->getValueOfManagerId(), managerId);
}

TEST_F(DepartmentTest, ToJson_ValidDepartment_ReturnsValidJson) {
    department->setId(1);
    department->setName("HR");
    department->setManagerId(50);
    
    Json::Value json = department->toJson();
    
    EXPECT_FALSE(json.isNull());
    EXPECT_EQ(json["id"].asInt(), 1);
    EXPECT_EQ(json["name"].asString(), "HR");
    EXPECT_EQ(json["manager_id"].asInt(), 50);
}
'''
    
    def _generate_generic_test(self) -> str:
        return '''#include <gtest/gtest.h>
#include <gmock/gmock.h>

// Generic test template
class GenericTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Setup code
    }
    
    void TearDown() override {
        // Cleanup code
    }
};

TEST_F(GenericTest, BasicFunctionality_ValidInput_ReturnsExpected) {
    // Test implementation
    EXPECT_TRUE(true);
}
'''
    
    def _generate_refinement_response(self) -> str:
        return "Tests have been refined: removed duplicates, improved assertions, added proper includes."
    
    def _generate_build_fix(self) -> str:
        return """## Error Analysis
Missing include files and linking issues detected.

## Required Fixes
### File: test_PersonsController.cpp
Line 3: Add #include <memory>
Line 4: Add #include <functional>
Reason: Required for std::unique_ptr and std::function

## Additional Dependencies
- Link against gtest_main
- Add drogon framework linking
"""
    
    def _generate_coverage_improvement(self) -> str:
        return '''// Additional tests for improved coverage

TEST_F(PersonsControllerTest, ErrorHandling_DatabaseError_ReturnsInternalError) {
    // Test database error scenarios
    EXPECT_TRUE(true);
}

TEST_F(PersonTest, BoundaryValues_MaxIntId_HandlesCorrectly) {
    // Test boundary value for ID
    EXPECT_TRUE(true);
}
'''

def demo_test_generation():
    """Demonstrate the test generator functionality"""
    print("🚀 C++ Unit Test Generator Demo")
    print("=" * 50)
    
    # Configuration
    config = GeneratorConfig(
        project_path="../orgChartApi",
        output_dir="./demo_generated_tests",
        model_provider="mock",
        model_name="mock-model"
    )
    
    # Create generator with mock provider
    generator = CppTestGenerator(config)
    generator.llm_provider = MockLLMProvider(config)
    
    print(f"📁 Project path: {config.project_path}")
    print(f"📁 Output directory: {config.output_dir}")
    print(f"🤖 Using mock LLM provider for demonstration")
    print()
    
    try:
        # Step 1: Find C++ files
        print("🔍 Step 1: Finding C++ files...")
        cpp_files = generator.find_cpp_files()
        print(f"   Found {len(cpp_files)} C++ files")
        for file in cpp_files[:5]:  # Show first 5
            print(f"   - {file.name}")
        if len(cpp_files) > 5:
            print(f"   ... and {len(cpp_files) - 5} more files")
        print()
        
        # Step 2: Generate initial tests
        print("🧪 Step 2: Generating initial tests...")
        success = generator.generate_initial_tests()
        if success:
            print("   ✅ Initial tests generated successfully")
            
            # Show generated files
            test_files = list(generator.output_dir.glob("test_*.cpp"))
            print(f"   Generated {len(test_files)} test files:")
            for test_file in test_files:
                print(f"   - {test_file.name}")
        else:
            print("   ❌ Initial test generation failed")
            return False
        print()
        
        # Step 3: Refine tests
        print("🔧 Step 3: Refining tests...")
        refine_success = generator.refine_tests()
        if refine_success:
            print("   ✅ Tests refined successfully")
        else:
            print("   ⚠️  Test refinement had issues, continuing...")
        print()
        
        # Step 4: Generate CMakeLists.txt
        print("🔨 Step 4: Creating build configuration...")
        cmake_content = generator._generate_cmake_for_tests()
        cmake_path = generator.output_dir / "CMakeLists.txt"
        with open(cmake_path, 'w') as f:
            f.write(cmake_content)
        print(f"   ✅ Created {cmake_path}")
        print()
        
        # Step 5: Generate report
        print("📊 Step 5: Generating report...")
        report = generator.generate_report()
        print("   ✅ Report generated successfully")
        print()
        
        # Show summary
        print("📋 Generation Summary:")
        print("=" * 30)
        test_files = list(generator.output_dir.glob("test_*.cpp"))
        total_lines = 0
        for test_file in test_files:
            with open(test_file, 'r') as f:
                lines = len(f.readlines())
                total_lines += lines
                print(f"   {test_file.name}: {lines} lines")
        
        print(f"\n   Total: {len(test_files)} files, {total_lines} lines of test code")
        print(f"   Output directory: {generator.output_dir}")
        
        # Show a sample of generated test
        if test_files:
            print(f"\n📝 Sample from {test_files[0].name}:")
            print("-" * 40)
            with open(test_files[0], 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines[:20]):  # Show first 20 lines
                    print(f"{i+1:2d}: {line.rstrip()}")
                if len(lines) > 20:
                    print(f"... and {len(lines) - 20} more lines")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = demo_test_generation()
    if success:
        print("\n🎉 Demo completed successfully!")
        print("\nNext steps:")
        print("1. Install Google Test framework")
        print("2. Install Ollama or configure GitHub Models API")
        print("3. Run the real generator with: python src/test_generator.py --project-path ../orgChartApi --output-dir ./generated_tests")
    else:
        print("\n❌ Demo failed. Check the error messages above.")
