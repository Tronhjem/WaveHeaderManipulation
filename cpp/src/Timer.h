#pragma once
#include <chrono>
#include <iostream>

using namespace std::chrono;

class Timer
{
public:
    Timer()
    {
        startTime = high_resolution_clock::now();
    }
    ~Timer()
    {
        auto endTime = high_resolution_clock::now();
        auto duration = duration_cast<microseconds>(endTime - startTime);
        
        std::cout << "Done in: " << duration.count() << " µs" << std::endl;
    }
private:
    steady_clock::time_point startTime;
};