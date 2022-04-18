from asyncio.windows_events import NULL
from audioop import mul
import ctypes
from datetime import datetime
import multiprocessing
from multiprocessing import Value, Array
import os
import time
from typing import List
from PIL import Image
import numpy as np
from alive_progress import alive_bar
from PixelInfo import PixelInfo

FILE_NAME = '2022_place_canvas_history'
MAX_FILE_NUM = 160
NUM_THREADS = 8
# width and height of the canvas
CANVAS_DIM = 2000
LAST_DATETIME = datetime(2022, 4, 4, 22, 47, 44)

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

def openNextFile(fileNum):
    with fileNum.get_lock():
        if fileNum.value > MAX_FILE_NUM:
            # silently exit
            return None
        fileName = os.path.join('input', FILE_NAME + str(fileNum.value) + '.csv')
        fileNum.value += 1
    return open(fileName, 'r')

def convertCoords(coords):
    return 2 * (CANVAS_DIM * coords[0] + coords[1])

def getDateTime(finalCanvasInfo, coords):
    return finalCanvasInfo[convertCoords(coords) + 1]

def threadBody(fileNum, finalCanvasInfo):
    # open file
    file = openNextFile(fileNum)
    # list of pixel infos
    pixelInfos = {}
    while (file != None):
        # read header line
        line = file.readline()
        # read first line of data
        line = file.readline()

        while len(line) > 0:
            # get the pixel info object from the line
            pixelInfo = getPixelInfo(line)
            # set the pixel info in the array
            x = pixelInfo.coords[0]
            y = pixelInfo.coords[1]
            if pixelInfo.date <= LAST_DATETIME:
                if (x not in pixelInfos):
                    pixelInfos[x] = dict([(y, pixelInfo)])
                elif y not in pixelInfos[x] or pixelInfos[x][y].date < pixelInfo.date:
                    pixelInfos[x][y] = pixelInfo
            # read the next line
            line = file.readline()

        for x, v in pixelInfos.items():
            for y, pixelInfo in v.items():
                if (pixelInfo != NULL):
                    shortDate = pixelInfo.getShortDate()
                    with finalCanvasInfo.get_lock():
                        # only hold the pixel info if there's no entry or the entry is later
                        if getDateTime(finalCanvasInfo, (x, y)) < shortDate:
                            finalCanvasInfo[convertCoords((x, y))] = pixelInfo.colour
                            finalCanvasInfo[convertCoords((x, y)) + 1] = shortDate
        
        pixelInfos.clear()
        # open file
        file = openNextFile(fileNum)

def vMain():
    fileNum = Value(ctypes.c_uint8, 0)
    # init the canvas as white
    finalCanvasInfo = Array(ctypes.c_uint32, [0] * CANVAS_DIM * CANVAS_DIM * 2)

    # start processes
    processes = []
    for i in range(NUM_THREADS):
        process = multiprocessing.Process(target=threadBody, args=(fileNum, finalCanvasInfo))
        process.start()
        processes.append(process)

    fileCount = 0
    with alive_bar(MAX_FILE_NUM) as bar:
        while (fileCount < MAX_FILE_NUM):
            time.sleep(.1)
            with fileNum.get_lock():
                while fileNum.value > fileCount:
                    fileCount += 1
                    bar()

    # join all the processes
    for process in processes:
        process.join()

    # create canvas of just pixels
    finalCanvas = [ [(0xFF, 0xFF, 0xFF)] * CANVAS_DIM for i in range(CANVAS_DIM)]
    for i in range(CANVAS_DIM):
        for j in range(CANVAS_DIM):
            hexColour = finalCanvasInfo[convertCoords((i, j))]
            r = hexColour >> 16
            g = (hexColour >> 8) & 0xFF
            b = hexColour & 0xFF
            finalCanvas[i][j] = (r, g, b)

    # Convert the pixels into an array using numpy
    array = np.array(finalCanvas, dtype=np.uint8)
    # Use PIL to create an image from the new array of pixels
    finalImage = Image.fromarray(array)
    finalImage.save('finalCanvas.png')

if __name__ == "__main__":
    vMain()