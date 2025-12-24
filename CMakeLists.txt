cmake_minimum_required(VERSION 3.16)

project(Ritual VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_COMPILER C:/llvm-mingw/bin/g++.exe)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 REQUIRED COMPONENTS Core)

qt_standard_project_setup()

qt_add_executable(Ritual
    main.cpp
)

target_link_libraries(Ritual PRIVATE Qt6::Core)