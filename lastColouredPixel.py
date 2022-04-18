from asyncio.windows_events import NULL
from audioop import mul
import ctypes
from datetime import datetime
import multiprocessing
from multiprocessing import Value
import time
from alive_progress import alive_bar
from PixelInfo import PixelInfo
import constants as cs
import fileUtils

def getPixelInfo(infoStr):
    # parse out each field
    fields = infoStr.split(',')
    # make sure there are enough fields
    if len(fields) < 5:
        print("Too few fields")
        return NULL

    try:
        date = datetime.strptime(fields[0], "%Y-%m-%d %H:%M:%S.%f %Z")
    except ValueError:
        date = datetime.strptime(fields[0], "%Y-%m-%d %H:%M:%S %Z")

    userIdHash = fields[1]
    # get colour information, trimming the leading '#'
    colour = int(fields[2][1:], 16)
    # trim the leading '"'
    y = int(fields[3][1:])
    # trim the trailing '"' and '\n'
    x = int(fields[4][:-2])

    return PixelInfo(date, userIdHash, colour, (x, y))

def threadBody(fileNum, lastTimestamp):
    # open file
    file = fileUtils.openNextFile(fileNum)
    lastTimestampTemp = 0.0
    while (file != None):
        # read header line
        line = file.readline()
        # read first line of data
        line = file.readline()

        while len(line) > 0:
            # get the pixel info object from the line
            pixelInfo = getPixelInfo(line)
            if pixelInfo.colour != 0xFFFFFF and lastTimestampTemp < pixelInfo.date.timestamp():
                lastTimestampTemp = pixelInfo.date.timestamp()
            # read the next line
            line = file.readline()
        
        # open file
        file = fileUtils.openNextFile(fileNum)

    with lastTimestamp.get_lock():
        if lastTimestampTemp > lastTimestamp.value:
            lastTimestamp.value = lastTimestampTemp    

def vMain():
    fileNum = Value(ctypes.c_uint8, 0)
    lastTimestamp = Value(ctypes.c_float, 0.0)

    # start processes
    processes = []
    for i in range(cs.NUM_THREADS):
        process = multiprocessing.Process(target=threadBody, args=(fileNum, lastTimestamp))
        process.start()
        processes.append(process)

    fileCount = 0
    with alive_bar(cs.MAX_FILE_NUM) as bar:
        while (fileCount < cs.MAX_FILE_NUM):
            time.sleep(.1)
            with fileNum.get_lock():
                while fileNum.value > fileCount:
                    fileCount += 1
                    bar()

    # join all the processes
    for process in processes:
        process.join()

    checkDate = datetime.fromtimestamp(lastTimestamp.value)
    print(lastTimestamp.value)
    print(checkDate)

if __name__ == "__main__":
    vMain()