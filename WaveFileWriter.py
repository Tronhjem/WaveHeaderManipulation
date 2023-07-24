from os import path

class WaveFile:
    

    def __init__(self, path):
        if not path.exists(path):
            raise Exception('FileNotFound', 'File was not found')

        waveFile = bytearray()
        with open(path, 'rb') as f:
            waveFile = f.read()
        self.riffHeader = waveFile[1:5]
        self.FileSize = waveFile[5:8]
        self.Format = self.MakeFormatHeader()
        

    def MakeFormatHeader(file):
        return


    class FormatHeader:
        def __init__(self):
            self.fmtHeader = 'fmt '
            self.size = 0
            self.type = 1
            self.channels = 0
            self.sampleRate = 44100
            self.bytes = 0           # sampleRate * bitsPerSamples * channels / 8
            self.bitsPerSample = 0   # Bitdepth, 8, 16, 24, 32 usually
            self.dataHeader = 'data'
            self.audioData = []
            self.audioDataSize = 0   # size of the audio Data   


        def WriteToByteArray(self):
            return


    class CuePoint:
        def __init__(self):
            self.id = 0
            self.position = 0
            self.dataChunkId = b'data'
            self.chunkStart = 0
            self.blockStart = 0
            self.sampleStart = 0


        def WriteToByteArray(self):
            byteArray = bytearray()
            byteArray += self.id.to_bytes(4, byteorder="little")
            byteArray += self.position.to_bytes(4, byteorder="little")
            byteArray += self.dataChunkId
            byteArray += self.chunkStart.to_bytes(4, byteorder="little")
            byteArray += self.blockStart.to_bytes(4, byteorder="little")
            byteArray += self.sampleStart.to_bytes(4, byteorder="little")
            return byteArray


    class LIST:
        def __init__(self, numOfLabels):
            self.listChunk = b'LIST'
            self.size = 0
            self.listType = b'adtl'
            self.Label = []
            for x in range(numOfLabels):
                self.Label.append(self.Label())


        def WriteToByteArray(self):
            byteArray = bytearray()
            listByteArray = bytearray()

            self.size = 4 # 4 for adtl plus one at the end
            for x in range(len(self.Label)):
                listByteArray += self.Label[x].WriteToByteArray()
                self.size += (4 + 4 + self.Label[x].size)

            byteArray += self.listChunk
            byteArray += self.size.to_bytes(4, byteorder="little")
            byteArray += self.listType
            byteArray += listByteArray

            return byteArray


    class Label:
        def __init__(self):
            self.labelChunk = b'labl'
            self.size = 0
            self.cuePointId = 0
            self.label = bytearray()


        def GetActualLabelSize(self):
            return self.size - 4


        def WriteToByteArray(self):
            byteArray = bytearray()
            byteArray += self.labelChunk
            if len(self.label) % 2:
                self.label += b'\x00'
            self.size = len(self.label) + 4
            byteArray += self.size.to_bytes(4, byteorder="little")
            byteArray += self.cuePointId.to_bytes(4, byteorder="little")
            byteArray += self.label
            return byteArray


    class CueIDs:
        def __init__(self, numberOfCuePoints):
            self.cueLabel = bytearray(b'cue ')
            self.size = 4 + numberOfCuePoints * 24
            self.numberOfCuePoints = numberOfCuePoints
            self.cuePoints = []
            for x in range(numberOfCuePoints):
                self.cuePoints.append(CuePoint())


        def WriteToByteArray(self):
            byteArray = bytearray()
            byteArray += self.cueLabel
            byteArray += self.size.to_bytes(4, byteorder="little")
            byteArray += self.numberOfCuePoints.to_bytes(4, byteorder="little")
            for x in range(len(self.cuePoints)):
                byteArray += self.cuePoints[x].WriteToByteArray()

            return byteArray


    class CueMarkWaveChunk:
        def __init__(self, numberOfCuePoints):
            self.CueId = CueIDs(numberOfCuePoints)
            self.List = LIST(numberOfCuePoints)


        def WriteToByteArray(self):
            byteArray = bytearray()
            byteArray += self.CueId.WriteToByteArray()
            byteArray += self.List.WriteToByteArray()

            return byteArray