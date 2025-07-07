"""
Demo LLM Provider for testing the C++ Unit Test Generator pipeline
This provider generates realistic test files without requiring external API calls
"""

import os
import time
from typing import Dict

class DemoProvider:
    """Demo provider that generates realistic C++ test files"""
    
    def __init__(self, config):
        self.config = config
        
    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        """Generate realistic test code based on the source file"""
        
        # Extract filename from prompt
        filename = self._extract_filename(prompt)
        
        # Generate appropriate test based on file type
        if "AuthController" in filename:
            return self._generate_auth_controller_test()
        elif "PersonsController" in filename:
            return self._generate_persons_controller_test()
        elif "DepartmentsController" in filename:
            return self._generate_departments_controller_test()
        elif "Person.h" in filename or "Person.cc" in filename:
            return self._generate_person_model_test()
        elif "Department" in filename:
            return self._generate_department_model_test()
        elif "LoginFilter" in filename:
            return self._generate_login_filter_test()
        else:
            return self._generate_generic_test(filename)
    
    def _extract_filename(self, prompt: str) -> str:
        """Extract filename from the prompt"""
        lines = prompt.split('\n')
        for line in lines:
            if 'File:' in line or 'filename:' in line or '.h' in line or '.cpp' in line or '.cc' in line:
                return line
        return "unknown_file"
    
    def _generate_auth_controller_test(self) -> str:
        return '''#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include "controllers/AuthController.h"
#include <drogon/HttpTypes.h>
#include <drogon/HttpRequest.h>
#include <drogon/HttpResponse.h>

using namespace drogon;
using namespace testing;

class AuthControllerTest : public ::testing::Test {
protected:
    void SetUp() override {
        controller = std::make_unique<AuthController>();
    }
    
    void TearDown() override {
        controller.reset();
    }
    
    std::unique_ptr<AuthController> controller;
};

TEST_F(AuthControllerTest, Login_ValidCredentials_ReturnsSuccess) {
    auto request = HttpRequest::newHttpRequest();
    Json::Value loginData;
    loginData["username"] = "testuser";
    loginData["password"] = "testpass";
    request->setBody(loginData.toStyledString());
    request->setContentTypeCode(CT_APPLICATION_JSON);
    
    bool callbackCalled = false;
    controller->login(request, [&](const HttpResponsePtr& response) {
        EXPECT_NE(response, nullptr);
        EXPECT_EQ(response->getStatusCode(), k200OK);
        callbackCalled = true;
    });
    
    EXPECT_TRUE(callbackCalled);
}

TEST_F(AuthControllerTest, Login_InvalidCredentials_ReturnsUnauthorized) {
    auto request = HttpRequest::newHttpRequest();
    Json::Value loginData;
    loginData["username"] = "wronguser";
    loginData["password"] = "wrongpass";
    request->setBody(loginData.toStyledString());
    request->setContentTypeCode(CT_APPLICATION_JSON);
    
    bool callbackCalled = false;
    controller->login(request, [&](const HttpResponsePtr& response) {
        EXPECT_NE(response, nullptr);
        EXPECT_EQ(response->getStatusCode(), k401Unauthorized);
        callbackCalled = true;
    });
    
    EXPECT_TRUE(callbackCalled);
}

TEST_F(AuthControllerTest, Login_EmptyRequest_ReturnsBadRequest) {
    auto request = HttpRequest::newHttpRequest();
    
    bool callbackCalled = false;
    controller->login(request, [&](const HttpResponsePtr& response) {
        EXPECT_NE(response, nullptr);
        EXPECT_EQ(response->getStatusCode(), k400BadRequest);
        callbackCalled = true;
    });
    
    EXPECT_TRUE(callbackCalled);
}

TEST_F(AuthControllerTest, Logout_ValidSession_ReturnsSuccess) {
    auto request = HttpRequest::newHttpRequest();
    request->addHeader("Authorization", "Bearer valid-token");
    
    bool callbackCalled = false;
    controller->logout(request, [&](const HttpResponsePtr& response) {
        EXPECT_NE(response, nullptr);
        EXPECT_EQ(response->getStatusCode(), k200OK);
        callbackCalled = true;
    });
    
    EXPECT_TRUE(callbackCalled);
}'''

    def _generate_persons_controller_test(self) -> str:
        return '''#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include "controllers/PersonsController.h"
#include <drogon/HttpTypes.h>
#include <drogon/HttpRequest.h>
#include <drogon/HttpResponse.h>

using namespace drogon;
using namespace testing;

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

TEST_F(PersonsControllerTest, GetAll_ReturnsPersonsList) {
    auto request = HttpRequest::newHttpRequest();
    
    bool callbackCalled = false;
    controller->getAll(request, [&](const HttpResponsePtr& response) {
        EXPECT_NE(response, nullptr);
        EXPECT_EQ(response->getStatusCode(), k200OK);
        
        auto jsonResponse = response->getJsonObject();
        EXPECT_NE(jsonResponse, nullptr);
        EXPECT_TRUE(jsonResponse->isArray());
        callbackCalled = true;
    });
    
    EXPECT_TRUE(callbackCalled);
}

TEST_F(PersonsControllerTest, GetOne_ValidId_ReturnsPerson) {
    auto request = HttpRequest::newHttpRequest();
    bool callbackCalled = false;
    int validPersonId = 1;
    
    controller->getOne(request, [&](const HttpResponsePtr& response) {
        EXPECT_NE(response, nullptr);
        EXPECT_EQ(response->getStatusCode(), k200OK);
        
        auto jsonResponse = response->getJsonObject();
        EXPECT_NE(jsonResponse, nullptr);
        EXPECT_TRUE(jsonResponse->isMember("id"));
        EXPECT_TRUE(jsonResponse->isMember("name"));
        callbackCalled = true;
    }, validPersonId);
    
    EXPECT_TRUE(callbackCalled);
}

TEST_F(PersonsControllerTest, GetOne_InvalidId_ReturnsNotFound) {
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

TEST_F(PersonsControllerTest, Create_ValidData_ReturnsCreated) {
    auto request = HttpRequest::newHttpRequest();
    Json::Value personData;
    personData["name"] = "John Doe";
    personData["email"] = "john.doe@example.com";
    personData["department_id"] = 1;
    request->setBody(personData.toStyledString());
    request->setContentTypeCode(CT_APPLICATION_JSON);
    
    bool callbackCalled = false;
    controller->create(request, [&](const HttpResponsePtr& response) {
        EXPECT_NE(response, nullptr);
        EXPECT_EQ(response->getStatusCode(), k201Created);
        
        auto jsonResponse = response->getJsonObject();
        EXPECT_NE(jsonResponse, nullptr);
        EXPECT_TRUE(jsonResponse->isMember("id"));
        callbackCalled = true;
    });
    
    EXPECT_TRUE(callbackCalled);
}

TEST_F(PersonsControllerTest, Update_ValidData_ReturnsSuccess) {
    auto request = HttpRequest::newHttpRequest();
    Json::Value personData;
    personData["name"] = "Jane Doe Updated";
    personData["email"] = "jane.updated@example.com";
    request->setBody(personData.toStyledString());
    request->setContentTypeCode(CT_APPLICATION_JSON);
    
    bool callbackCalled = false;
    int personId = 1;
    
    controller->update(request, [&](const HttpResponsePtr& response) {
        EXPECT_NE(response, nullptr);
        EXPECT_EQ(response->getStatusCode(), k200OK);
        callbackCalled = true;
    }, personId);
    
    EXPECT_TRUE(callbackCalled);
}

TEST_F(PersonsControllerTest, Delete_ValidId_ReturnsSuccess) {
    auto request = HttpRequest::newHttpRequest();
    bool callbackCalled = false;
    int personId = 1;
    
    controller->remove(request, [&](const HttpResponsePtr& response) {
        EXPECT_NE(response, nullptr);
        EXPECT_EQ(response->getStatusCode(), k200OK);
        callbackCalled = true;
    }, personId);
    
    EXPECT_TRUE(callbackCalled);
}'''

    def _generate_departments_controller_test(self) -> str:
        return '''#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include "controllers/DepartmentsController.h"
#include <drogon/HttpTypes.h>

using namespace drogon;
using namespace testing;

class DepartmentsControllerTest : public ::testing::Test {
protected:
    void SetUp() override {
        controller = std::make_unique<DepartmentsController>();
    }
    
    std::unique_ptr<DepartmentsController> controller;
};

TEST_F(DepartmentsControllerTest, GetAll_ReturnsAllDepartments) {
    auto request = HttpRequest::newHttpRequest();
    
    bool callbackCalled = false;
    controller->getAll(request, [&](const HttpResponsePtr& response) {
        EXPECT_NE(response, nullptr);
        EXPECT_EQ(response->getStatusCode(), k200OK);
        callbackCalled = true;
    });
    
    EXPECT_TRUE(callbackCalled);
}

TEST_F(DepartmentsControllerTest, Create_ValidDepartment_ReturnsCreated) {
    auto request = HttpRequest::newHttpRequest();
    Json::Value deptData;
    deptData["name"] = "Engineering";
    deptData["description"] = "Software Engineering Department";
    request->setBody(deptData.toStyledString());
    
    bool callbackCalled = false;
    controller->create(request, [&](const HttpResponsePtr& response) {
        EXPECT_NE(response, nullptr);
        EXPECT_EQ(response->getStatusCode(), k201Created);
        callbackCalled = true;
    });
    
    EXPECT_TRUE(callbackCalled);
}'''

    def _generate_person_model_test(self) -> str:
        return '''#include <gtest/gtest.h>
#include "models/Person.h"

class PersonTest : public ::testing::Test {
protected:
    void SetUp() override {
        testPerson = std::make_unique<Person>();
    }
    
    std::unique_ptr<Person> testPerson;
};

TEST_F(PersonTest, Constructor_DefaultValues_InitializesCorrectly) {
    EXPECT_EQ(testPerson->getId(), 0);
    EXPECT_TRUE(testPerson->getName().empty());
    EXPECT_TRUE(testPerson->getEmail().empty());
}

TEST_F(PersonTest, SetName_ValidName_SetsCorrectly) {
    std::string testName = "John Doe";
    testPerson->setName(testName);
    EXPECT_EQ(testPerson->getName(), testName);
}

TEST_F(PersonTest, SetEmail_ValidEmail_SetsCorrectly) {
    std::string testEmail = "john.doe@example.com";
    testPerson->setEmail(testEmail);
    EXPECT_EQ(testPerson->getEmail(), testEmail);
}

TEST_F(PersonTest, SetEmail_InvalidEmail_ThrowsException) {
    std::string invalidEmail = "invalid-email";
    EXPECT_THROW(testPerson->setEmail(invalidEmail), std::invalid_argument);
}

TEST_F(PersonTest, ToJson_PopulatedObject_ReturnsValidJson) {
    testPerson->setId(1);
    testPerson->setName("Jane Doe");
    testPerson->setEmail("jane@example.com");
    
    Json::Value json = testPerson->toJson();
    
    EXPECT_EQ(json["id"].asInt(), 1);
    EXPECT_EQ(json["name"].asString(), "Jane Doe");
    EXPECT_EQ(json["email"].asString(), "jane@example.com");
}

TEST_F(PersonTest, FromJson_ValidJson_PopulatesObject) {
    Json::Value json;
    json["id"] = 2;
    json["name"] = "Bob Smith";
    json["email"] = "bob@example.com";
    
    testPerson->fromJson(json);
    
    EXPECT_EQ(testPerson->getId(), 2);
    EXPECT_EQ(testPerson->getName(), "Bob Smith");
    EXPECT_EQ(testPerson->getEmail(), "bob@example.com");
}'''

    def _generate_department_model_test(self) -> str:
        return '''#include <gtest/gtest.h>
#include "models/Department.h"

class DepartmentTest : public ::testing::Test {
protected:
    void SetUp() override {
        testDepartment = std::make_unique<Department>();
    }
    
    std::unique_ptr<Department> testDepartment;
};

TEST_F(DepartmentTest, Constructor_DefaultValues_InitializesCorrectly) {
    EXPECT_EQ(testDepartment->getId(), 0);
    EXPECT_TRUE(testDepartment->getName().empty());
}

TEST_F(DepartmentTest, SetName_ValidName_SetsCorrectly) {
    std::string deptName = "Engineering";
    testDepartment->setName(deptName);
    EXPECT_EQ(testDepartment->getName(), deptName);
}

TEST_F(DepartmentTest, AddEmployee_ValidEmployee_AddsSuccessfully) {
    testDepartment->addEmployee(1);
    EXPECT_EQ(testDepartment->getEmployeeCount(), 1);
}'''

    def _generate_login_filter_test(self) -> str:
        return '''#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include "filters/LoginFilter.h"
#include <drogon/HttpTypes.h>

using namespace drogon;

class LoginFilterTest : public ::testing::Test {
protected:
    void SetUp() override {
        filter = std::make_unique<LoginFilter>();
    }
    
    std::unique_ptr<LoginFilter> filter;
};

TEST_F(LoginFilterTest, DoFilter_ValidToken_PassesThrough) {
    auto request = HttpRequest::newHttpRequest();
    request->addHeader("Authorization", "Bearer valid-token");
    
    bool filterCalled = false;
    filter->doFilter(request, nullptr, [&]() {
        filterCalled = true;
    });
    
    EXPECT_TRUE(filterCalled);
}

TEST_F(LoginFilterTest, DoFilter_NoToken_ReturnsUnauthorized) {
    auto request = HttpRequest::newHttpRequest();
    
    bool filterCalled = false;
    filter->doFilter(request, nullptr, [&]() {
        filterCalled = true;
    });
    
    EXPECT_FALSE(filterCalled);
}'''

    def _generate_generic_test(self, filename: str) -> str:
        class_name = filename.split('/')[-1].replace('.h', '').replace('.cc', '').replace('.cpp', '')
        return f'''#include <gtest/gtest.h>
#include "{filename}"

class {class_name}Test : public ::testing::Test {{
protected:
    void SetUp() override {{
        // Setup test fixtures
    }}
    
    void TearDown() override {{
        // Cleanup
    }}
}};

TEST_F({class_name}Test, Constructor_InitializesCorrectly) {{
    // Test constructor
    EXPECT_TRUE(true); // Placeholder test
}}

TEST_F({class_name}Test, BasicFunctionality_WorksAsExpected) {{
    // Test basic functionality
    EXPECT_TRUE(true); // Placeholder test
}}'''
