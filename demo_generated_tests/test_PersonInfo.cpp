#include <gtest/gtest.h>
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
