import os.path 
import threading
import json 
import sys

Languages = {}
lock = threading.Lock()
OASIS_MARKER = bytearray(b'OasisID')
CUE_MARKER = bytearray(b'cue ')
MISSING_FILES_JSON = './Files.json'
LANGUAGES_MISSING_FILES = "Missing Files"
LANGUAGES_PATH = "Path"
LANGUAGES_MISSING_FILES_COUNT = "Missing Files Count"

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
            self.Label.append(Label())


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


def ReadCueMarkersAsByteArray(file):
    cueMarker = CueIDs(2) 
    listMarker = LIST(2)
    
    binarySound = bytearray()

    with open(file, 'rb') as f:
        binarySound = f.read()
    
    cueIndex = binarySound.find(b'cue ')
    index = cueIndex
    print(binarySound[cueIndex: len(binarySound)])

# CUE MARKER
    cueMarker.cueLabel = binarySound[cueIndex:cueIndex + 4]
    index += 4
    cueMarker.size = ReadBytesAsInt(binarySound, index, 4)
    index += 4
    cueMarker.numberOfCuePoints= ReadBytesAsInt(binarySound, index, 4)

#CUE POINT 1
    pointMood = cueMarker.cuePoints[0]
    index += 4
    pointMood.id = ReadBytesAsInt(binarySound, index, 4)
    index += 4
    pointMood.position = ReadBytesAsInt(binarySound, index, 4)
    index += 4
    pointMood.dataChunkId = binarySound[index:index + 4]
    index += 4
    pointMood.chunkStart = ReadBytesAsInt(binarySound, index, 4)
    index += 4
    pointMood.blockStart = ReadBytesAsInt(binarySound, index, 4)
    index += 4
    pointMood.sampleStart = ReadBytesAsInt(binarySound, index, 4)

#CUE POINT 2
    pointOasis = cueMarker.cuePoints[1]
    index += 4
    pointOasis.id = ReadBytesAsInt(binarySound, index, 4)
    index += 4
    pointOasis.position = ReadBytesAsInt(binarySound, index, 4)
    index += 4
    pointOasis.dataChunkId = binarySound[index:index + 4]
    index += 4
    pointOasis.chunkStart = ReadBytesAsInt(binarySound, index, 4)
    index += 4
    pointOasis.blockStart = ReadBytesAsInt(binarySound, index, 4)
    index += 4
    pointOasis.sampleStart = ReadBytesAsInt(binarySound, index, 4)

#LIST 
    index += 4
    listMarker.listChunk = binarySound[index:index + 4]
    index += 4
    listMarker.size = ReadBytesAsInt(binarySound, index, 4)
    index += 4
    listMarker.listType = binarySound[index:index + 4]

#Label Mood
    labelMood = listMarker.Label[0]
    index += 4
    labelMood.labelChunk = binarySound[index:index + 4]
    index += 4
    labelMood.size = ReadBytesAsInt(binarySound, index, 4)
    index += 4
    labelMood.cuePointId = ReadBytesAsInt(binarySound, index, 4)
    index += 4
    labelMood.label = binarySound[index : index + labelMood.GetActualLabelSize()]

    index = index + labelMood.GetActualLabelSize() 

#Label OASIS
    labelOasis = listMarker.Label[1]
    labelOasis.labelChunk = binarySound[index:index + 4]
    index += 4
    labelOasis.size = ReadBytesAsInt(binarySound, index, 4)
    index += 4
    labelOasis.cuePointId = ReadBytesAsInt(binarySound, index, 4)
    index += 4
    labelOasis.label = binarySound[index : index + labelOasis.GetActualLabelSize()]

    markChunk = CueMarkWaveChunk(2)
    markChunk.CueId = cueMarker
    markChunk.List = listMarker

    return markChunk.WriteToByteArray()


def PrintInfo(path):
    binarySound = bytearray()

    with open(path, 'rb') as f:
        binarySound = f.read()

    CueMarkerIndex = binarySound.find(CUE_MARKER)
    print(f'cue index: {CueMarkerIndex}')

    oasisIndex = binarySound.find(OASIS_MARKER)
    print(f'oasis index: {oasisIndex}')

    print("_______________")


def ExtraOasisIdFromFile(path):
    fileName = os.path.basename(path)
    splitName = fileName.split("_")
    if (splitName[0] == "CI"):
        return ''

    return splitName[len(splitName) - 1].split('.')[0]
    

def HasOasisMarkerAndIsCorrect(path):
    oasisFileId = ExtraOasisIdFromFile(path)
    if len(oasisFileId) < 1:
        return True  

    binarySound = bytearray()

    with open(path, 'rb') as f:
        binarySound = f.read()

    OasisMarkerIndex = binarySound.find(OASIS_MARKER)
    if OasisMarkerIndex == -1:
        return False
    
    sizeIndex = OasisMarkerIndex - 8
    a = binarySound[sizeIndex: sizeIndex + 4]
    size = int.from_bytes(a, byteorder="little")
    sizeNoOasis = size - 4 - 7
    OasisId = (binarySound[OasisMarkerIndex + 7: OasisMarkerIndex  + 6 + sizeNoOasis]).decode('utf-8')

    isCorrect = OasisId == oasisFileId
    if isCorrect:
        return True
    else:
        return False
    

def CountInstancesOfMarkers(files, languageName):
    global Languages
    for file in files:
        if not HasOasisMarkerAndIsCorrect(file):
            lock.acquire()
            try:
                fileName = os.path.basename(file)
                Languages[languageName][LANGUAGES_MISSING_FILES].append(fileName)
                Languages[languageName][LANGUAGES_MISSING_FILES_COUNT] += 1
            finally:
                lock.release()


def LogMissingForLanguage(languagePath):
    languageName = os.path.basename(languagePath)
    print(f'Logging information {languageName} ...')

    Languages[languageName] = {}
    Languages[languageName][LANGUAGES_PATH] = languagePath
    Languages[languageName][LANGUAGES_MISSING_FILES] = []
    Languages[languageName][LANGUAGES_MISSING_FILES_COUNT] = 0

    waveFilesToCheck = [os.path.join(languagePath, file) for file in os.listdir(languagePath) if os.path.splitext(file)[1] == ".wav"]
    split = 7
    portion_size = len(waveFilesToCheck) // split # // is floored divison
    portions = []
    portions.append(waveFilesToCheck[:portion_size])
    portions.append(waveFilesToCheck[portion_size:portion_size * 2])
    portions.append(waveFilesToCheck[portion_size * 2:portion_size * 3])
    portions.append(waveFilesToCheck[portion_size * 3:portion_size * 4])
    portions.append(waveFilesToCheck[portion_size * 4:portion_size * 5])
    portions.append(waveFilesToCheck[portion_size * 5:portion_size * 6])
    portions.append(waveFilesToCheck[portion_size * 6:])

    threads = []
    for x in range(split):
        thread = threading.Thread(target=CountInstancesOfMarkers, args=(portions[x], languageName, ))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def LogMissingCueMarkers(waveFilePaths, logFile):
    foldersToSearch = [os.path.join(waveFilePaths, folder) for folder in os.listdir(waveFilePaths) if os.path.isdir(os.path.join(waveFilePaths, folder))]

    if len(foldersToSearch) < 1:
        LogMissingForLanguage(waveFilePaths)
    else:
        for languagePath in foldersToSearch:
            LogMissingForLanguage(languagePath)

    with open(logFile, "w") as file:
        json.dump(Languages, file)


def ReadBytesAsInt(binaryArray, index, size):
    return int.from_bytes(binaryArray[index:index + size], byteorder="little")


def SaveMarkerToFile(cueMarkChunk, file, savePath):
    binarySound = bytearray()
    with open(file, 'rb') as f:
        binarySound = f.read()

    junkIndex = binarySound.find(bytearray(b'JUNK'))
    # junkSizeToRemove = 0
    # if junkIndex != -1:
    #     fmtIndex = binarySound.find(bytearray(b'fmt '))
    #     header = binarySound[:junkIndex]
    #     junkSizeToRemove = int.from_bytes(binarySound[junkIndex + 4: junkIndex + 4 + 4], byteorder="little") + 4 + 4 # here plus 4 to include JUNK and Size 
    #     binarySound = header + binarySound[fmtIndex:]

    binarySound += cueMarkChunk

    oldSizeInt = int.from_bytes(binarySound[4:8], byteorder="little")
    oldSize = binarySound[4:8] # size for the file is at 4 at 4 bytes. 
                          
    newSize = len(binarySound) - 8
    newSizeBytes = newSize.to_bytes(4, byteorder="little")
    binarySound = binarySound.replace(oldSize, newSizeBytes, 4)

    newPath = os.path.join(savePath, os.path.basename(file)) 
    with open(newPath, 'wb') as f:
        f.write(binarySound)


def MakeMarkerByteArray(markers):
    numberOfMarkers = len(markers)
    markerChunk = CueMarkWaveChunk(numberOfMarkers)

    for x in range(numberOfMarkers):
        markerChunk.CueId.cuePoints[x].id = x + 1
        markerChunk.List.Label[x].cuePointId = x + 1
        markerChunk.List.Label[x].label = bytes(markers[x],'utf-8')
    
    return markerChunk.WriteToByteArray()


def WriteMarkersForFiles(files, path, savePath):
    for file in files:
        filePath = os.path.join(path, file)
        id = ExtraOasisIdFromFile(filePath)
        if len(id) > 1:
            oasisID = MakeMarkerByteArray([f'OasisID{id}'])
            SaveMarkerToFile(oasisID, filePath, savePath)


def ProcessAllMarkersForMissingFiles(savePath):

    for language in Languages:
        print(f'Writing markers for {language}')

        newFolderPath = os.path.join(savePath, language)
        if not os.path.exists(newFolderPath):
            os.mkdir(newFolderPath)
        
        filePath = Languages[language][LANGUAGES_PATH]
        filesToWrite = Languages[language][LANGUAGES_MISSING_FILES]

        split = 5
        portion_size = len(filesToWrite) // split # // is floored divison
        portions = []
        portions.append(filesToWrite[:portion_size])
        portions.append(filesToWrite[portion_size:portion_size * 2])
        portions.append(filesToWrite[portion_size * 2:portion_size * 3])
        portions.append(filesToWrite[portion_size * 3:portion_size * 4])
        portions.append(filesToWrite[portion_size * 4:])

        threads = []
        for x in range(split):
            thread = threading.Thread(target=WriteMarkersForFiles, args=(portions[x], filePath, newFolderPath, ))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
    

if __name__ == "__main__":
    VoicesPath = sys.argv[1]
    UseLog = len(sys.argv) > 2

    print(VoicesPath)
    executionDir = os.path.dirname(__file__)

    missingFilePath = os.path.join(executionDir, MISSING_FILES_JSON)

    if not os.path.exists(missingFilePath) or not UseLog:
        print(f'Scanning for missing Cue Markers at: {VoicesPath}' )
        LogMissingCueMarkers(VoicesPath, MISSING_FILES_JSON)
    else:
        print(f'Loading missing files from JSON...')
        with open(missingFilePath, 'r') as file:
            Languages = json.load(file)

    print("____________")

    processedFilePath = os.path.join(executionDir, "ProcessedFiles")
    if not os.path.exists(processedFilePath):
        os.mkdir(processedFilePath)
    
    ProcessAllMarkersForMissingFiles(processedFilePath)

    # VERIFY 
    # print("____________")
    # print("Verifying Processed Files...")
    # Languages = {}
    # verifyFile = os.path.join(executionDir, "Verification.json")
    # LogMissingCueMarkers(processedFilePath, verifyFile)
    # print("____________")
    ####### 

    print()
    print("DONE")
    print("____________")

#NOTES#
# {
#  'D:/Projects/NexusMain/project/NexusVR/WwiseProject/Audio_NexusVR_01/Originals/Voices/English(US)': 1301, 
#  'D:/Projects/NexusMain/project/NexusVR/WwiseProject/Audio_NexusVR_01/Originals/Voices/French(France)': 146075, 
#  'D:/Projects/NexusMain/project/NexusVR/WwiseProject/Audio_NexusVR_01/Originals/Voices/German': 0, 
#  'D:/Projects/NexusMain/project/NexusVR/WwiseProject/Audio_NexusVR_01/Originals/Voices/Spanish(Spain)': 0
# }


# structure of the cue and list chunk 
# first cue chunk with 2 data 
# then LIST 
# in list we

# b'cue 
# 4\x00\x00\x00\    size, minus itself and 'cue ' 
# x02\x00\x00\x00\  number of cue points

# x01\x00\x00\x00\  ID
# x00\x00\x00\x00   Position
# data              data
# \x00\x00\x00\x00\ chunk start
# x00\x00\x00\x00\  block start
# x00\x00\x00\x00\  sample Start

# x02\x00\x00\x00\  ----
# n\x00\x00\x00
# data\
# x00\x00\x00\x00\
# x00\x00\x00\x00\
# n\x00\x00\x00

# LIST              List chunk
# 0\x00\x00\x00     size
# adtl              list typr

# labl              label   
# \n\x00\x00\x00\   size, minus itself and labl. Meaning the size of the actual string is this -4 as cue point ID is calculated in.
# x01\x00\x00\x00   cue point ID
# Mood:\x00         

# labl\
# x12\x00\x00\x00\
# x02\x00\x00\x00
# OasisID260216\x00'