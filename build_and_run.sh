#!/bin/bash

# Create build directory if it doesn't exist
if [ ! -d "build" ]; then
  mkdir build
fi

# Navigate to build directory
cd build

# Run CMake and build the project
cmake ..
make

# Run the executable if build succeeded
if [ $? -eq 0 ]; then
  echo "Build succeeded, running the executable..."
  ./my_microservice
else
  echo "Build failed."
fi