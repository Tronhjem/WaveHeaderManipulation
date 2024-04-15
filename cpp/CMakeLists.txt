cmake_minimum_required(VERSION 3.19)

project(WriteWave)

set(CMAKE_CXX_STANDARD 20)

add_executable(WriteWave 
    src/main.cpp 
    src/WaveFileReader.cpp 
    src/WaveFileReader.h)
