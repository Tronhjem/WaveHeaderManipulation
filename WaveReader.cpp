//
// Created by Christian Tronhjem on 21.08.22.
//
#include <fstream>
#include <iostream>
#include <cstdlib>
#include "WaveReader.hpp"
#include <filesystem>

void WaveFileReader::ReadFile(const std::string &in_name)
{
    pathToFile = std::filesystem::path(in_name);
    std::ifstream inStream(in_name, std::ifstream::binary);
    const auto start = inStream.tellg();
    inStream.seekg(0, std::ios::end);
    const auto end = inStream.tellg();
    const auto fileLength = end - start;
    inStream.seekg(0, std::ios::beg);

    char temp;
    char startF = 'f';
    char startM = 'm';
    char startD = 'd';
    m_fmtIndex = -1;
    int dataIndex = -1;

    for (int i = 0; i < RAW_HEADER_LENGTH; i++)
    {
        inStream.read(reinterpret_cast<char *>(&temp), sizeof(char));
        Info.RawHeaderBuffer[i] = temp;

        if (m_fmtIndex == -1 && temp == startF)
        {
            i++;
            inStream.read(reinterpret_cast<char *>(&temp), sizeof(char));
            Info.RawHeaderBuffer[i] = temp;
            
            if (temp == startM)
                m_fmtIndex = i-1;
        }

        if (dataIndex == -1 && temp == startD)
        {
            dataIndex = i;
            Info.RawHeaderSize = i + 8;
            Info.DataStartIndex = Info.RawHeaderSize;
        }
        if (dataIndex != -1 && i > dataIndex + 8)
            break;
    }


    if (m_fmtIndex == -1)
    {
        return;
    }

    if (dataIndex == -1)
    {
        return;
    }

    char* buf = Info.RawHeaderBuffer;
    
    Info.AudioFormat = (buf[m_fmtIndex + 8] & 0xFF) |
                       ((buf[m_fmtIndex + 9] & 0xFF) << 8);

    Info.Channels = (buf[m_fmtIndex + 10] & 0xFF) |
                    ((buf[m_fmtIndex + 11] & 0xFF) << 8);

    Info.SampleRate = (buf[m_fmtIndex + 12] & 0xFF) |
                      ((buf[m_fmtIndex + 13] & 0xFF) << 8) |
                      ((buf[m_fmtIndex + 14] & 0xFF) << 16) |
                      ((buf[m_fmtIndex + 15] & 0xFF) << 24);

    Info.BytesPerSec = (buf[m_fmtIndex + 16] & 0xFF) |
                       ((buf[m_fmtIndex + 17] & 0xFF) << 8) |
                       ((buf[m_fmtIndex + 18] & 0xFF) << 16) |
                       ((buf[m_fmtIndex + 19] & 0xFF) << 24);

    Info.BlockAlign = (buf[m_fmtIndex + 20] & 0xFF) |
                      ((buf[m_fmtIndex + 21] & 0xFF) << 8);

    Info.BitsPerSample = (buf[m_fmtIndex + 22] & 0xFF) |
                         ((buf[m_fmtIndex + 23] & 0xFF) << 8);
    
    Info.DataSize = static_cast<int32_t>((buf[dataIndex + 4] & 0xFF) |
                    ((buf[dataIndex + 5] & 0xFF) << 8) |
                    ((buf[dataIndex + 6] & 0xFF) << 16) |
                    ((buf[dataIndex + 7] & 0xFF) << 24));


    Info.LengthInMs = (((static_cast<float>(Info.DataSize) /
                         static_cast<float>(Info.Channels)) /
                        (static_cast<float>(Info.BitsPerSample) / 8.f)) /
                       static_cast<float>(Info.SampleRate)) * 1000.f;

    inStream.seekg(Info.DataStartIndex, std::ios::beg);
    int chunkSize = Info.BlockAlign / Info.Channels;
    LengthOfData = Info.DataSize / chunkSize;
    
    if (Data != nullptr)
        delete Data;
    
    Data = new int32_t[LengthOfData];

    int sampleIndex = 0;
    char tempSample;

    for (int i = Info.DataStartIndex; i < fileLength; i += chunkSize)
    {
        int32_t sample = 0;
        for (int j = 0; j < chunkSize; ++j)
        {
            inStream.read(reinterpret_cast<char *>(&tempSample), sizeof(char));
            sample |= (tempSample & 0xFF) << (j * 8);
        }

        if (chunkSize == 2)
        {
            auto bitset = std::bitset<32>(sample);
            if (bitset.test(15))
            {
                sample |= 0xFFFF0000;
            }
        }
        else if (chunkSize == 3)
        {
            auto bitset = std::bitset<32>(sample);
            if (bitset.test(23))
            {
                sample |= 0xFF000000;
            }
            else
            {
                sample |= 0x000000FF;
            }
        }
        Data[sampleIndex] = sample;
        ++sampleIndex;
    }
}


void WaveFileReader::ChangeSampleRate(int newSampleRate)
{
    char newSample[4];
    newSample[0] = newSampleRate & 0xFF;
    newSample[1] = (newSampleRate >> 8) & 0xFF;
    newSample[2] = (newSampleRate >> 16) & 0xFF;
    newSample[3] = (newSampleRate >> 24) & 0xFF;

    for (size_t i = 0; i < 4; i++)
    {
        Info.RawHeaderBuffer[m_fmtIndex + 12 + i] = newSample[i];
    }
}

void WaveFileReader::ChangeChannels(int newChannels)
{
    char newSample[2];
    newSample[0] = newChannels & 0xFF;
    newSample[1] = (newChannels >> 8) & 0xFF;

    for (size_t i = 0; i < 2; i++)
    {
        Info.RawHeaderBuffer[m_fmtIndex + 10 + i] = newSample[i];
    }
}

void WaveFileReader::ChangeBitDepth(int newChannels)
{
    char newSample[2];
    newSample[0] = newChannels & 0xFF;
    newSample[1] = (newChannels >> 8) & 0xFF;

    for (size_t i = 0; i < 2; i++)
    {
        Info.RawHeaderBuffer[m_fmtIndex + 22 + i] = newSample[i];
    }
}

void WaveFileReader::WriteFile(const std::string &out_name)
{
    
    auto oldFilePath = pathToFile.string();
    
    size_t lastindex = oldFilePath.find_last_of(".");
    std::string iteration = std::to_string(++iterator);
    iteration = std::string("_") + iteration;
    std::string newFileName = oldFilePath.substr(0, lastindex) + out_name + iteration + std::string(".wav");
    
    auto newPathToFile = pathToFile;
    newPathToFile.replace_filename(newFileName);
    
    std::ofstream out(newPathToFile.string(), std::ofstream::binary);
    int chunkSize = Info.BlockAlign / Info.Channels;

    char temp;
    for (size_t i = 0; i < Info.RawHeaderSize; i++)
    {
        temp = Info.RawHeaderBuffer[i];
        out.write(reinterpret_cast<const char *>(&temp), sizeof(char));
    }

    for (int i = 0; i < LengthOfData; ++i)
    {
        int32_t sample = Data[i];
        for (int j = 0; j < chunkSize; ++j)
        {
            temp = (sample >> (j * 8));
            out.write(reinterpret_cast<const char *>(&temp), sizeof(char));
        }
    }
}

void WaveFileReader::PrintInfo() const
{
    std::cout << "Format            :  " << Info.AudioFormat << std::endl;
    std::cout << "Channels          :  " << Info.Channels << std::endl;
    std::cout << "Sample Rate       :  " << Info.SampleRate << std::endl;
    std::cout << "Bytes Per Sec     :  " << Info.BytesPerSec << std::endl;
    std::cout << "Block Align       :  " << Info.BlockAlign << std::endl;
    std::cout << "Bits Per Sample   :  " << Info.BitsPerSample << std::endl;
    std::cout << "Data Size         :  " << Info.DataSize << std::endl;
    std::cout << "Length in ms      :  " << Info.LengthInMs << std::endl;
}
