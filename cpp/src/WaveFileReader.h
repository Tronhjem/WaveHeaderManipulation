#ifndef WRITEWAVE_WAVEFILEREADER_H
#define WRITEWAVE_WAVEFILEREADER_H

struct IDChunk
{
    char ID[4] = {' ',' ',' ',' '};
    uint32_t size = 0;
};

struct FMTChunk
{
   uint16_t Format_Tag;       //  format_Tag 1=PCM         8-9
   uint16_t Num_Channels;                              //  10-11
   uint32_t Sample_rate;      // Sampling Frequency in (44100)Hz 12-13-14-15
   uint32_t byte_rate;        // Byte rate                       16-17-18-19
   uint16_t block_Align;      // 2=16-bit mono, 4=16-bit stereo    20-21
   uint16_t bits_Per_Sample;  // 16                                22-23
};

struct WaveHeader
{
    // RIFF Chunk
    IDChunk RIFF;
    char WAVE[4] = {' ',' ',' ',' '};
    IDChunk JUNK;
    IDChunk FMT;
    FMTChunk fmtData;

    IDChunk DATA;
    /* "data" sub-chunk */
    uint8_t chunk2_ID[4] = {'d', 'a', 't', 'a'}; // data
    uint32_t chunk2_data_Size; // Size of the audio data
};

struct WaveInfo
{
    char RawHeaderBuffer[200];
    int RawHeaderSize;
    uint16_t AudioFormat;
    int16_t Channels;
    uint32_t SampleRate;;
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
public:
    WaveInfo Info;
    int32_t *Data;
    int LengthOfData;

    void ReadHeader(const std::string& filePath);

    void ReadFile(const std::string &in_name);
    void ChangeSampleRate(int newSampleRate);
    void WriteFile(const std::string &out_name);
    void PrintInfo() const;

    void TrimBeginning(int lengthInSamples);
};

#endif //WRITEWAVE_WAVEFILEREADER_H
