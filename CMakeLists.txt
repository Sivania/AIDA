cmake_minimum_required(VERSION 3.10)
project(Search)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)

# Include directories
include_directories(include)

# Add source files
set(SOURCES
    src/main.cpp
)

# Create executable
add_executable(search ${SOURCES})