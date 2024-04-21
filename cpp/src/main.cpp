#include <string>
#include "Timer.h"
#include "WaveFileReader.h"

int main()
{
    std::string folderPath = "/Users/christiantronhjem/dev/WaveHeaderManipulation/cpp/testfiles/";
    std::string inFilePath = folderPath + "beep.wav";
    std::string outFilePath = folderPath + "beep_Manipulated.wav";

    // Timer scope
    {
        // Timer t;
        WaveFileReader reader;

        reader.ReadHeader(inFilePath);

        // parser.ReadFile(inName);
        // parser.PrintInfo();

        // parser.ChangeSampleRate(34000);
        // parser.WriteFile(outName);
    }

    return 0;
}