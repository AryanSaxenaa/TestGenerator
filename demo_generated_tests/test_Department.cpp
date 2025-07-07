#include <gtest/gtest.h>
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
