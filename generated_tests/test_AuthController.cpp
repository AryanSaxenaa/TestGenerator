```cpp
// test_AuthController.cpp
#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include "AuthController.h"
#include "../plugins/JwtPlugin.h"
#include <memory>
#include <string>
#include <bcrypt/BCrypt.hpp>
#include <drogon/orm/Mapper.h>
#include <drogon/orm/Criteria.h>
#include <drogon/HttpAppFramework.h> //Ensure HttpAppFramework is included

using ::testing::_;
using ::testing::Return;
using ::testing::NiceMock;
using ::testing::Throw;
using namespace drogon;
using namespace drogon_model::org_chart;


// Mock JwtPlugin
class MockJwtPlugin : public JwtPlugin {
public:
    MOCK_METHOD(void, init(), (const)); // Changed return type to void, assuming init doesn't return anything useful for testing.
    MOCK_METHOD(std::string, encode, (const std::string&, const std::string&), (const));
};

// Mock DbClient to handle exceptions
class MockDbClient : public drogon::DbClient {
public:
    MOCK_METHOD(std::shared_ptr<drogon::Connection>, getConnection, (), (const, override));
};


class AuthControllerTest : public ::testing::Test {
protected:
    void SetUp() override {
        jwtPlugin = std::make_shared<NiceMock<MockJwtPlugin>>();
        mockDbClient = std::make_shared<NiceMock<MockDbClient>>();
        drogon::app().addPlugin(jwtPlugin);
        drogon::app().setDbClient(mockDbClient);
    }

    void TearDown() override {
        drogon::app().removePlugin<JwtPlugin>();
        drogon::app().setDbClient(nullptr); //Clean up DbClient
    }

    std::shared_ptr<NiceMock<MockJwtPlugin>> jwtPlugin;
    std::shared_ptr<NiceMock<MockDbClient>> mockDbClient;
};


TEST_F(AuthControllerTest, registerUser_ValidUser_Success) {
    User user;
    user.setUsername("testuser");
    user.setPassword("password123");

    EXPECT_CALL(*jwtPlugin, init()).Times(1);
    EXPECT_CALL(*jwtPlugin, encode("user_id", _)).Times(1).WillOnce(Return("mock_token"));
    EXPECT_CALL(*mockDbClient, getConnection()).Times(1).WillByDefault(Return(std::make_shared<drogon::Connection>()));


    auto callback = [](const HttpResponsePtr &resp) {
        ASSERT_EQ(resp->getStatusCode(), HttpStatusCode::k201Created);
    };

    AuthController authController;
    authController.registerUser(nullptr, std::move(callback), std::move(user));
}


TEST_F(AuthControllerTest, registerUser_MissingFields_BadRequest) {
    User user; 
    auto callback = [](const HttpResponsePtr &resp) {
        ASSERT_EQ(resp->getStatusCode(), HttpStatusCode::k400BadRequest);
    };

    AuthController authController;
    authController.registerUser(nullptr, std::move(callback), std::move(user));
}

TEST_F(AuthControllerTest, registerUser_UsernameTaken_BadRequest) {
    User user;
    user.setUsername("testuser");
    user.setPassword("password123");

    auto mockMapper = std::make_shared<drogon::orm::Mapper<User>>(mockDbClient);
    auto mockCriteria = drogon::orm::Criteria(User::Cols::_username, drogon::orm::CompareOperator::EQ, "testuser");
    EXPECT_CALL(*mockMapper, findFutureBy(mockCriteria)).WillOnce(Return(std::vector<User>{User()}));
    EXPECT_CALL(*mockDbClient, getConnection()).Times(1).WillByDefault(Return(std::make_shared<drogon::Connection>()));

    auto callback = [](const HttpResponsePtr &resp) {
        ASSERT_EQ(resp->getStatusCode(), HttpStatusCode::k400BadRequest);
    };

    AuthController authController;
    authController.registerUser(nullptr, std::move(callback), std::move(user));
}


TEST_F(AuthControllerTest, registerUser_DatabaseError_InternalServerError) {
    User user;
    user.setUsername("testuser");
    user.setPassword("password123");

    EXPECT_CALL(*mockDbClient, getConnection()).WillOnce(Throw(std::runtime_error("Database error")));

    auto callback = [](const HttpResponsePtr &resp) {
        ASSERT_EQ(resp->getStatusCode(), HttpStatusCode::k500InternalServerError);
    };

    AuthController authController;
    authController.registerUser(nullptr, std::move(callback), std::move(user));
}


TEST_F(AuthControllerTest, loginUser_ValidCredentials_Success) {
    User user;
    user.setUsername("testuser");
    user.setPassword("password123");
    std::string hashedPassword = BCrypt::generateHash("password123");
    User dbUser;
    dbUser.setUsername("testuser");
    dbUser.setPassword(hashedPassword);
    dbUser.setId(1); 

    auto mockMapper = std::make_shared<drogon::orm::Mapper<User>>(mockDbClient);
    auto mockCriteria = drogon::orm::Criteria(User::Cols::_username, drogon::orm::CompareOperator::EQ, "testuser");
    EXPECT_CALL(*mockMapper, findFutureBy(mockCriteria)).WillOnce(Return(std::vector<User>{dbUser}));
    EXPECT_CALL(*jwtPlugin, init()).Times(1);
    EXPECT_CALL(*jwtPlugin, encode("user_id", "1")).Times(1).WillOnce(Return("mock_token"));
    EXPECT_CALL(*mockDbClient, getConnection()).Times(1).WillByDefault(Return(std::make_shared<drogon::Connection>()));

    auto callback = [](const HttpResponsePtr &resp) {
        ASSERT_EQ(resp->getStatusCode(), HttpStatusCode::k200OK);
    };

    AuthController authController;
    authController.loginUser(nullptr, std::move(callback), std::move(user));
}


TEST_F(AuthControllerTest, loginUser_InvalidCredentials_Unauthorized) {
    User user;
    user.setUsername("testuser");
    user.setPassword("wrongpassword");

    auto mockMapper = std::make_shared<drogon::orm::Mapper<User>>(mockDbClient);
    auto mockCriteria = drogon::orm::Criteria(User::Cols::_username, drogon::orm::CompareOperator::EQ, "testuser");
    EXPECT_CALL(*mockMapper, findFutureBy(mockCriteria)).WillOnce(Return(std::vector<User>{}));
    EXPECT_CALL(*mockDbClient, getConnection()).Times(1).WillByDefault(Return(std::make_shared<drogon::Connection>()));

    auto callback = [](const HttpResponsePtr &resp) {
        ASSERT_EQ(resp->getStatusCode(), HttpStatusCode::k401Unauthorized);
    };

    AuthController authController;
    authController.loginUser(nullptr, std::move(callback), std::move(user));
}


TEST_F(AuthControllerTest, loginUser_DatabaseError_InternalServerError) {
    User user;
    user.setUsername("testuser");
    user.setPassword("password123");

    EXPECT_CALL(*mockDbClient, getConnection()).WillOnce(Throw(std::runtime_error("Database error")));

    auto callback = [](const HttpResponsePtr &resp) {
        ASSERT_EQ(resp->getStatusCode(), HttpStatusCode::k500InternalServerError);
    };

    AuthController authController;
    authController.loginUser(nullptr, std::move(callback), std::move(user));
}


TEST_F(AuthControllerTest, areFieldsValid_ValidUser_True) {
    User user;
    user.setUsername("testuser");
    user.setPassword("password123");
    AuthController authController;
    ASSERT_TRUE(authController.areFieldsValid(user));
}

TEST_F(AuthControllerTest, areFieldsValid_InvalidUser_False) {
    User user;
    AuthController authController;
    ASSERT_FALSE(authController.areFieldsValid(user));
}

TEST_F(AuthControllerTest, isPasswordValid_ValidPassword_True) {
    std::string hash = BCrypt::generateHash("password123");
    AuthController authController;
    ASSERT_TRUE(authController.isPasswordValid("password123", hash));
}

TEST_F(AuthControllerTest, isPasswordValid_InvalidPassword_False) {
    std::string hash = BCrypt::generateHash("password123");
    AuthController authController;
    ASSERT_FALSE(authController.isPasswordValid("wrongpassword", hash));
}

TEST_F(AuthControllerTest, UserWithToken_Constructor_GeneratesToken) {
    User user;
    user.setId(1);
    user.setUsername("testuser");

    EXPECT_CALL(*jwtPlugin, init()).Times(1);
    EXPECT_CALL(*jwtPlugin, encode("user_id", "1")).Times(1).WillOnce(Return("mock_token"));

    AuthController::UserWithToken userWithToken(user, *jwtPlugin); // Pass JwtPlugin to constructor
    ASSERT_EQ(userWithToken.username, "testuser");
    ASSERT_FALSE(userWithToken.token.empty());
}

TEST_F(AuthControllerTest, UserWithToken_toJson_CorrectJson) {
    User user;
    user.setId(1);
    user.setUsername("testuser");
    AuthController::UserWithToken userWithToken(user, *jwtPlugin); // Pass JwtPlugin to constructor
    userWithToken.token = "mock_token";
    Json::Value json = userWithToken.toJson();
    ASSERT_EQ(json["username"].asString(), "testuser");
    ASSERT_EQ(json["token"].asString(), "mock_token");
}

//Test for isUserAvailable - combined positive and negative cases into one test.
TEST_F(AuthControllerTest, isUserAvailable_ChecksAvailability){
    auto mockMapper = std::make_shared<drogon::orm::Mapper<User>>(mockDbClient);
    AuthController authController;
    User userAvailable;
    userAvailable.setUsername("availableUser");
    User userUnavailable;
    userUnavailable.setUsername("unavailableUser");

    EXPECT_CALL(*mockMapper, findFutureBy(_)).WillOnce(Return(std::vector<User>{}));
    ASSERT_TRUE(authController.isUserAvailable(userAvailable, *mockMapper));

    EXPECT_CALL(*mockMapper, findFutureBy(_)).WillOnce(Return(std::vector<User>{User()}));
    ASSERT_FALSE(authController.isUserAvailable(userUnavailable, *mockMapper));
}
```