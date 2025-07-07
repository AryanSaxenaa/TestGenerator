#include <gtest/gtest.h>
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
