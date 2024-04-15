import os
import statusbar
import argparse

def ChangeSampleRate(file, targetSamplerate):
    binaryArray = bytearray()

    with open(file, 'rb') as f:
        binaryArray = f.read()

    chunk = b'fmt'
    indexOfChunk = binaryArray.find(chunk)
    oldHeader = binaryArray[indexOfChunk + 12:indexOfChunk + 16]
    newHeader = int.to_bytes(targetSamplerate, 4, byteorder="little")
    newBinaryArray = binaryArray.replace(oldHeader, newHeader, 4)
    name = os.path.basename(file).split(".")
    newName = os.path.join(path, name[0] + "_hacked_" + str(targetSamplerate) + "." + name[1])

    with open(newName, 'wb') as f:
        f.write(newBinaryArray)

def HackFolderOfFiles(pathOfFiles):
    i = 0
    files = os.listdir(pathOfFiles)
    numOfFiles = len(files)

    for file in files:

        if os.path.basename(file).split(".")[1].lower() == 'wav':
            absolutePath = os.path.join(pathOfFiles, file)

            for s in sampleRates:
                ChangeSampleRate(absolutePath, int(s))
                statusbar.show(i, numOfFiles * len(sampleRates), status="Hacking samplerate")
                i += 1

def HackSingleFile(file):
    i = 0
    if os.path.basename(file).split(".")[1].lower() == 'wav':
        absolutePath = os.path.join(path, file)

        for s in sampleRates:
            ChangeSampleRate(absolutePath, int(s))
            statusbar.show(i, len(sampleRates), status="Hacking samplerate")
            i += 1


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Changes sample rate in header and saves to new files. Provide a path and sample rates.',
                                     usage="-p path-goes-here -s samplerates-goes-here \n\n"
                                           "EXAMPLE: python HeaderHacker.py -p Users/JohnDoe/samples/ConversionFolder -s 22050,44100")

    parser.add_argument('-p', metavar='path', type=str,
                        help='path to directory of files or a single file')
    parser.add_argument('-s', metavar='sample rate', type=str,
                        help='sample rantes seperated by comma, like so: 44100,22050')

    args = parser.parse_args()
    sampleRateString = args.s

    if sampleRateString is None or len(sampleRateString) < 1:
        print("\nERROR No valid sample rates set\n")
        parser.print_help()
        print("\n")
        exit(0)

    sampleRates = sampleRateString.split(",")
    path = args.p

    if path is None or len(path) < 1:
        print("\nERROR No valid path set\n")
        parser.print_help()
        print("\n")
        exit(0)

    if os.path.isdir(path):
        HackFolderOfFiles(path)

    elif os.path.isfile(path):
        fileName = path
        path = os.path.dirname(path)
        HackSingleFile(fileName)

    print("\n")
    print("***************************")
    print("********* D O N E *********")
    print("***************************")