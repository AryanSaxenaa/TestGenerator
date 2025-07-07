cmake_minimum_required(VERSION 3.10)
project(UnitTests CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find packages
find_package(GTest REQUIRED)
find_package(GMock REQUIRED)

# Include directories
include_directories(${GTEST_INCLUDE_DIRS})
include_directories(${GMOCK_INCLUDE_DIRS})
include_directories("..\orgChartApi")

# Test executable
add_executable(run_tests
    test_AuthController.cpp
    test_Department.cpp
    test_DepartmentsController.cpp
    test_Job.cpp
    test_JobsController.cpp
    test_Jwt.cpp
    test_JwtPlugin.cpp
    test_LoginFilter.cpp
    test_main.cpp
    test_Person.cpp
    test_PersonInfo.cpp
    test_PersonsController.cpp
    test_User.cpp
    test_utils.cpp
)

# Link libraries
target_link_libraries(run_tests
    ${GTEST_LIBRARIES}
    ${GMOCK_LIBRARIES}
    pthread
)

# Enable testing
enable_testing()
add_test(NAME unit_tests COMMAND run_tests)
