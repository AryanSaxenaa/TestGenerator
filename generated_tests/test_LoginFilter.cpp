```cpp
#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include "LoginFilter.h"
#include <drogon/drogon.h>
#include <string>
#include <jwt/jwt.hpp>
#include <stdexcept> // Added for std::runtime_error


using namespace drogon;
using namespace testing;

//Improved Mock:  Handles more scenarios and is more concise.
class MockJwtPlugin : public JwtPlugin {
public:
    MOCK_METHOD(jwt::jwt_decoded, decode, (const std::string& token), (override));
    MOCK_METHOD(jwt::jwt_object, init, (), (override));

    //Added to simulate different decode failures.
    void setDecodeResult(const jwt::jwt_decoded& decoded) { decodeResult = decoded; decodeError = false; }
    void setDecodeError(const std::exception& error) { decodeError = true; decodeException = &error; }

    virtual jwt::jwt_decoded decode(const std::string& token) override {
        if (decodeError) {
            throw *decodeException;
        }
        return decodeResult;
    }

private:
    jwt::jwt_decoded decodeResult;
    bool decodeError = false;
    const std::exception* decodeException = nullptr;
};


class LoginFilterTest : public ::testing::Test {
protected:
    void SetUp() override {
        mockJwtPlugin = std::make_shared<MockJwtPlugin>();
        drogon::app().addPlugin(mockJwtPlugin);
    }

    void TearDown() override {
        drogon::app().removePlugin<JwtPlugin>();
    }

    std::shared_ptr<MockJwtPlugin> mockJwtPlugin;
    HttpRequestPtr createRequest(const std::string& authHeader) {
        auto req = std::make_shared<HttpRequest>();
        req->setHeader("Authorization", authHeader);
        return req;
    }

    //Helper to reduce test code duplication.
    void runFilterTest(const std::string& token, const std::function<void(const HttpResponsePtr&)>& expectedCallback,
                       const std::function<void()>& expectedFilterChainCallback, int expectedStatusCode = -1) {
        LoginFilter filter;
        auto req = createRequest("Bearer " + token);
        bool callbackCalled = false;
        bool fccbCalled = false;

        auto fcb = [&](const HttpResponsePtr& resp) {
            expectedCallback(resp);
            callbackCalled = true;
        };
        auto fccb = [&]() {
            expectedFilterChainCallback();
            fccbCalled = true;
        };

        filter.doFilter(req, std::move(fcb), std::move(fccb));
        EXPECT_TRUE(callbackCalled);
        if (expectedStatusCode != -1) {
            EXPECT_EQ(expectedStatusCode, fcb_response->getStatusCode());
        }
        if (expectedFilterChainCallback) {
            EXPECT_TRUE(fccbCalled);
        }
    }

    HttpResponsePtr fcb_response; //Store response for later access.

};


TEST_F(LoginFilterTest, doFilter_MissingAuthorizationHeader_Returns400) {
    runFilterTest("", [&](const HttpResponsePtr& resp) {
        ASSERT_NE(resp, nullptr);
        EXPECT_EQ(resp->getStatusCode(), k400BadRequest);
        fcb_response = resp;
    }, [&]() { FAIL() << "FilterChainCallback should not be called"; }, k400BadRequest);
}


TEST_F(LoginFilterTest, doFilter_ValidToken_CallsFilterChainCallback) {
    jwt::jwt_decoded decoded;
    decoded.set_payload_claim("user_id", "123");
    EXPECT_CALL(*mockJwtPlugin, init()).WillRepeatedly(Return(jwt::jwt_object()));
    EXPECT_CALL(*mockJwtPlugin, decode("valid_token")).WillOnce(Return(decoded));
    runFilterTest("valid_token", [&](const HttpResponsePtr& resp) { FAIL() << "FilterCallback should not be called"; }, [&]() {}, -1);
}


TEST_F(LoginFilterTest, doFilter_InvalidToken_Returns400) {
    EXPECT_CALL(*mockJwtPlugin, init()).WillRepeatedly(Return(jwt::jwt_object()));
    EXPECT_CALL(*mockJwtPlugin, decode("invalid_token")).WillOnce(Throw(jwt::token_verification_exception("Invalid token")));
    runFilterTest("invalid_token", [&](const HttpResponsePtr& resp) {
        ASSERT_NE(resp, nullptr);
        EXPECT_EQ(resp->getStatusCode(), k400BadRequest);
        fcb_response = resp;
    }, [&]() { FAIL() << "FilterChainCallback should not be called"; }, k400BadRequest);
}


TEST_F(LoginFilterTest, doFilter_TokenDecodeError_Returns500) {
    EXPECT_CALL(*mockJwtPlugin, init()).WillRepeatedly(Return(jwt::jwt_object()));
    mockJwtPlugin->setDecodeError(std::runtime_error("Decoding error"));
    runFilterTest("invalid_token", [&](const HttpResponsePtr& resp) {
        ASSERT_NE(resp, nullptr);
        EXPECT_EQ(resp->getStatusCode(), k500InternalServerError);
        fcb_response = resp;
    }, [&]() { FAIL() << "FilterChainCallback should not be called"; }, k500InternalServerError);
}


TEST_F(LoginFilterTest, doFilter_MissingUserIdClaim_Returns500) {
    jwt::jwt_decoded decoded;
    EXPECT_CALL(*mockJwtPlugin, init()).WillRepeatedly(Return(jwt::jwt_object()));
    EXPECT_CALL(*mockJwtPlugin, decode("missing_userid_token")).WillOnce(Return(decoded));
    runFilterTest("missing_userid_token", [&](const HttpResponsePtr& resp) {
        ASSERT_NE(resp, nullptr);
        EXPECT_EQ(resp->getStatusCode(), k500InternalServerError);
        fcb_response = resp;
    }, [&]() { FAIL() << "FilterChainCallback should not be called"; }, k500InternalServerError);
}


TEST_F(LoginFilterTest, doFilter_InvalidUserIdClaim_Returns500) {
    jwt::jwt_decoded decoded;
    decoded.set_payload_claim("user_id", "abc"); 
    EXPECT_CALL(*mockJwtPlugin, init()).WillRepeatedly(Return(jwt::jwt_object()));
    EXPECT_CALL(*mockJwtPlugin, decode("invalid_userid_token")).WillOnce(Return(decoded));
    runFilterTest("invalid_userid_token", [&](const HttpResponsePtr& resp) {
        ASSERT_NE(resp, nullptr);
        EXPECT_EQ(resp->getStatusCode(), k500InternalServerError);
        fcb_response = resp;
    }, [&]() { FAIL() << "FilterChainCallback should not be called"; }, k500InternalServerError);
}

TEST_F(LoginFilterTest, doFilter_EmptyToken_Returns400) {
    runFilterTest("", [&](const HttpResponsePtr& resp) {
        ASSERT_NE(resp, nullptr);
        EXPECT_EQ(resp->getStatusCode(), k400BadRequest);
        fcb_response = resp;
    }, [&]() { FAIL() << "FilterChainCallback should not be called"; }, k400BadRequest);
}

TEST_F(LoginFilterTest, doFilter_WhitespaceToken_Returns400) {
    runFilterTest("   ", [&](const HttpResponsePtr& resp) {
        ASSERT_NE(resp, nullptr);
        EXPECT_EQ(resp->getStatusCode(), k400BadRequest);
        fcb_response = resp;
    }, [&]() { FAIL() << "FilterChainCallback should not be called"; }, k400BadRequest);
}

```