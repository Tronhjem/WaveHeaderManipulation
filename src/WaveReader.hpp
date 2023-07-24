//
//  WaveReader.hpp
//  WaveHeaderHacker - App
//
//  Created by Christian Tronhjem on 10.09.22.
//

#ifndef WaveReader_hpp
#define WaveReader_hpp
#define RAW_HEADER_LENGTH 400
#include <filesystem>

struct WaveInfo
{
    char RawHeaderBuffer[RAW_HEADER_LENGTH]; // buffer for having space for big headers.
    int RawHeaderSize; // this is the actual size of the header.
    uint16_t AudioFormat;
    int16_t Channels;
    uint32_t SampleRate;
    uint32_t BytesPerSec;
    uint16_t BlockAlign;        // Bytes Per Sample
    uint16_t BitsPerSample;
    uint16_t DataStartIndex = -1;
    uint32_t DataSize;
    float LengthInMs;
};

class WaveFileReader
{
private:
    int m_fmtIndex = -1;
    int iterator = 0;
public:
    std::filesystem::path pathToFile;
    int LengthOfData;
    WaveInfo Info;
    int32_t* Data = nullptr;
    
    ~WaveFileReader()
    {
        delete[] Data;
    }
    
    void ReadFile(const std::string &in_name);
    void ChangeSampleRate(int newSampleRate);
    void ChangeChannels(int newChannels);
    void ChangeBitDepth(int newChannels);
    void WriteFile(const std::string &out_name);
    void PrintInfo() const;
    void TrimBeginning(int lengthInSamples);
};
#endif /* WaveReader_hpp */
