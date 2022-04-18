from asyncio.windows_events import NULL
from audioop import mul
import ctypes
from datetime import datetime
import multiprocessing
from multiprocessing import Value
import time
from alive_progress import alive_bar

import constants as cs
import fileUtils
import pixelUtils

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
            pixelInfo = pixelUtils.getPixelInfo(line)
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
    with alive_bar(fileUtils.MAX_FILE_NUM) as bar:
        while (fileCount < fileUtils.MAX_FILE_NUM):
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