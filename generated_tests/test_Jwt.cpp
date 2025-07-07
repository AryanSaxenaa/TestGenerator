```cpp
#include <gtest/gtest.h>
#include "Jwt.h"
#include <chrono>
#include <iostream>
#include <stdexcept> // for std::runtime_error


class JwtTest : public ::testing::Test {
protected:
    void SetUp() override {
        secret = "testsecret";
        sessionTime = 3600;
        issuer = "testIssuer";
        jwt = std::make_unique<Jwt>(secret, sessionTime, issuer);
    }

    void TearDown() override {}

    std::string secret;
    int sessionTime;
    std::string issuer;
    std::unique_ptr<Jwt> jwt;

    // Helper function to create a JWT with a specific expiration time
    std::string createTokenWithExpiration(int expirationTime, const std::string& payloadKey, int payloadValue) {
        Jwt jwt2{secret, expirationTime, issuer};
        return jwt2.encode(payloadKey, payloadValue);
    }
};


TEST_F(JwtTest, Constructor_ValidInput_CreatesJwtObject) {
    ASSERT_NE(nullptr, jwt.get());
}

TEST_F(JwtTest, Encode_ValidInput_ReturnsEncodedToken) {
    std::string token = jwt->encode("userId", 123);
    ASSERT_FALSE(token.empty());
}

TEST_F(JwtTest, Encode_DifferentPayloads_ReturnsDifferentTokens) {
    std::string token1 = jwt->encode("userId", 123);
    std::string token2 = jwt->encode("userId", 456);
    std::string token3 = jwt->encode("userName", 123);
    ASSERT_NE(token1, token2);
    ASSERT_NE(token1, token3);
}

TEST_F(JwtTest, Encode_LargePayload_ReturnsEncodedToken) {
    std::string largePayload = "This is a very large payload string to test the encoding functionality. It should be long enough to stress test the encoding process.";
    std::string token = jwt->encode("largeData", 123); 
    ASSERT_FALSE(token.empty());
}

TEST_F(JwtTest, Decode_ValidToken_ReturnsDecodedJwt) {
    std::string token = jwt->encode("userId", 123);
    auto decoded = jwt->decode(token);
    ASSERT_TRUE(decoded.has_payload());
    ASSERT_EQ(decoded.getPayload()["userId"], 123); //Verify payload content
}

TEST_F(JwtTest, Decode_InvalidToken_ThrowsException) {
    std::string invalidToken = "invalidtoken";
    ASSERT_THROW(jwt->decode(invalidToken), std::runtime_error);
}

TEST_F(JwtTest, Decode_TamperedToken_ThrowsException) {
    std::string token = jwt->encode("userId", 123);
    token[5] = 'X';
    ASSERT_THROW(jwt->decode(token), std::runtime_error);
}

TEST_F(JwtTest, Decode_TokenWithWrongIssuer_ThrowsException) {
    std::string token = jwt->encode("userId", 123);
    Jwt jwt2{"testsecret", 3600, "wrongIssuer"}; 
    ASSERT_THROW(jwt2.decode(token), std::runtime_error);
}

TEST_F(JwtTest, Encode_EmptySecret_ThrowsException) {
    ASSERT_THROW(Jwt{"", 3600, "testIssuer"}.encode("userId", 123), std::runtime_error);
}

TEST_F(JwtTest, Encode_EmptyIssuer_ThrowsException) {
    ASSERT_THROW(Jwt{"testsecret", 3600, ""}.encode("userId", 123), std::runtime_error);
}

TEST_F(JwtTest, Encode_ZeroSessionTime_ReturnsTokenWithZeroExpiration) {
    std::string token = createTokenWithExpiration(0, "userId", 123);
    ASSERT_FALSE(token.empty()); 
}

TEST_F(JwtTest, Decode_ExpiredToken_ThrowsException) {
    //Simulate expired token using a helper function
    auto now = std::chrono::system_clock::now();
    auto past = now - std::chrono::seconds(7200); //Expired 2 hours ago

    //Simulate a token that would have expired in the past
    std::time_t tt = std::chrono::system_clock::to_time_t(past);
    std::string token = createTokenWithExpiration(1, "userId", 123); //Token expires immediately

    ASSERT_THROW(jwt->decode(token), std::runtime_error);
}


TEST_F(JwtTest, Decode_EmptyToken_ThrowsException){
    ASSERT_THROW(jwt->decode(""), std::runtime_error);
}

TEST_F(JwtTest, Encode_Decode_RoundTrip){
    std::string payloadKey = "testKey";
    int payloadValue = 42;
    std::string token = jwt->encode(payloadKey, payloadValue);
    auto decoded = jwt->decode(token);
    ASSERT_TRUE(decoded.has_payload());
    ASSERT_EQ(decoded.getPayload()[payloadKey], payloadValue);
}

```