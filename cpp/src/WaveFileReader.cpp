//
// Created by Christian Tronhjem on 21.08.22.
//
#include <fstream>
#include <iostream>
#include <cstdlib>
#include "WaveFileReader.h"

constexpr size_t DEFAULT_CHUNK_SIZE = 4;

enum CHUNK_TYPE
{
    UNDEFINED = 0,
    JUNK = 1,
    FMT = 2,
    DATA = 3
};

CHUNK_TYPE CheckChunkType(const IDChunk& idToCheck)
{
    if (idToCheck.ID[0] == 'J' && idToCheck.ID[1] == 'U')
    {
        return CHUNK_TYPE::JUNK;
    }
    else if(idToCheck.ID[0] == 'f' && idToCheck.ID[1] == 'm')
    {
        return CHUNK_TYPE::FMT;
    }
    else if(idToCheck.ID[0] == 'd' && idToCheck.ID[1] == 'a')
    {
        return CHUNK_TYPE::DATA;
    }

    return CHUNK_TYPE::UNDEFINED;
}


void WaveFileReader::ReadHeader(const std::string& filePath)
{
    WaveHeader header;

    // stream reader
    std::ifstream inStream(filePath, std::ifstream::binary);
    const auto start = inStream.tellg();

    // Read RIFF
    inStream.read(reinterpret_cast<char*>(&header.RIFF), sizeof(header.RIFF));

    // read WAVE
    inStream.read(reinterpret_cast<char*>(&header.WAVE), sizeof(uint32_t));

    bool running = true;
    while (running)
    {
        IDChunk tempID;
        inStream.read(reinterpret_cast<char *>(&tempID), sizeof(tempID));

        CHUNK_TYPE chunkType = CheckChunkType(tempID);

        if (chunkType == CHUNK_TYPE::JUNK)
        {
            header.JUNK = tempID;
            const auto position = inStream.tellg();
            inStream.seekg(header.JUNK.size + position);
            const auto newposition = inStream.tellg();
            std::cout << newposition << std::endl;
        }
        else if(chunkType == CHUNK_TYPE::FMT)
        {
            header.FMT = tempID;
            inStream.read(reinterpret_cast<char*>(&header.fmtData), sizeof(header.fmtData));
        }
        else if(chunkType == CHUNK_TYPE::DATA)
        {
            header.DATA = tempID;
            running = false;
        }
        else
        {
            running = false;
        }
    }


    // =============================================================
    // LOGGING
    // =============================================================
    for (size_t i = 0; i < sizeof(header.RIFF.ID); i++)
    {
        std::cout << header.RIFF.ID[i];
    }
    std::cout << std::endl;

    // std::cout << "RIFF: " << header.RIFF.ID<< std::endl;
    std::cout << "File size: " << header.RIFF.size<< std::endl;

    // std::cout << "WAVE: " << header.WAVE<< std::endl;
    for (size_t i = 0; i < sizeof(header.WAVE); i++)
    {
        std::cout << header.WAVE[i];
    }
    std::cout << std::endl;

    for (size_t i = 0; i < sizeof(header.JUNK.ID); i++)
    {
        std::cout << header.JUNK.ID[i];
    }
    std::cout << std::endl;
    std::cout << "JUNK size: " << header.JUNK.size << std::endl;
    // =============================================================

    for (size_t i = 0; i < sizeof(header.FMT.ID); i++)
    {
        std::cout << header.FMT.ID[i];
    }
    std::cout << std::endl;
    std::cout << "FMT size: " << header.FMT.size << std::endl;

}


void WaveFileReader::ReadFile(const std::string &in_name)
{
    std::ifstream inStream(in_name, std::ifstream::binary);
    const auto start = inStream.tellg();
    inStream.seekg(0, std::ios::end);
    const auto end = inStream.tellg();
    const auto fileLength = end - start;
    inStream.seekg(0, std::ios::beg);

    char temp;
    char startF = 'f';
    char startD = 'd';
    m_fmtIndex = -1;
    int dataIndex = -1;

    for (int i = 0; i < 150; i++)
    {
        inStream.read(reinterpret_cast<char *>(&temp), sizeof(char));
        Info.RawHeaderBuffer[i] = temp;

        if (m_fmtIndex == -1 && temp == startF)
        {
            m_fmtIndex = i;
        }

        if (dataIndex == -1 && temp == startD)
        {
            dataIndex = i;
            Info.RawHeaderSize = i + 8;
            Info.DataStartIndex = Info.RawHeaderSize;
        }
    }

    char* buf = Info.RawHeaderBuffer;

    int32_t sizeFile = (buf[4] & 0xFF) |
                      ((buf[5] & 0xFF) << 8) |
                      ((buf[6] & 0xFF) << 16) |
                      ((buf[7] & 0xFF) << 24);

    std::cout << "file size " << sizeFile << std::endl;
    std::cout << "file length" << fileLength << std::endl;

    if (m_fmtIndex == -1)
    {
        std::cout << "no fmt index found" << std::endl;
        return;
    }

    if (dataIndex == -1)
    {
        std::cout << "no data found" << std::endl;
        return;
    }

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

    Info.DataSize = (buf[dataIndex + 4] & 0xFF) |
                    ((buf[dataIndex + 5] & 0xFF) << 8) |
                    ((buf[dataIndex + 6] & 0xFF) << 16) |
                    ((buf[dataIndex + 7] & 0xFF) << 24);


    Info.LengthInMs = (((static_cast<float>(Info.DataSize) /
                         static_cast<float>(Info.Channels)) /
                        (static_cast<float>(Info.BitsPerSample) / 8.f)) /
                       static_cast<float>(Info.SampleRate)) * 1000.f;

    inStream.seekg(Info.DataStartIndex, std::ios::beg);
    int chunkSize = Info.BlockAlign / Info.Channels;
    LengthOfData = Info.DataSize / chunkSize;
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

void WaveFileReader::TrimBeginning(int lengthInSamples)
{
    int dataSizeToCut = lengthInSamples * Info.Channels;
    int32_t sizeInBytes = dataSizeToCut * (Info.BitsPerSample / 8);
    int32_t newSize = Info.DataSize - sizeInBytes;

    int32_t* newData = new int32_t[dataSizeToCut];
    int newDataIndex = 0;
    for (int i = LengthOfData - dataSizeToCut; i < LengthOfData; ++i)
    {
        newData[newDataIndex] = Data[i];
    }

    std::cout << Info.DataSize << std::endl;
//    Info.DataSize
//    int32_t
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

void WaveFileReader::WriteFile(const std::string &out_name)
{
    std::ofstream out(out_name, std::ofstream::binary);
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
