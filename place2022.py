from asyncio.windows_events import NULL
from audioop import mul
import ctypes
from datetime import datetime
import multiprocessing
from multiprocessing import Value, Array
import time
from PIL import Image
import numpy as np
from alive_progress import alive_bar

import constants as cs
import fileUtils
import pixelUtils

def convertCoords(coords):
    return 2 * (cs.CANVAS_DIM * coords[0] + coords[1])

def getDateTime(finalCanvasInfo, coords):
    return finalCanvasInfo[convertCoords(coords) + 1]

def threadBody(fileNum, finalCanvasInfo):
    # open file
    file = fileUtils.openNextFile(fileNum)
    # list of pixel infos
    pixelInfos = {}
    while (file != None):
        # read header line
        line = file.readline()
        # read first line of data
        line = file.readline()

        while len(line) > 0:
            # get the pixel info object from the line
            pixelInfo = pixelUtils.getPixelInfo(line)
            # set the pixel info in the array
            x = pixelInfo.coords[0]
            y = pixelInfo.coords[1]
            if pixelInfo.date <= cs.LAST_DATETIME:
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
        file = fileUtils.openNextFile(fileNum)

def vMain():
    fileNum = Value(ctypes.c_uint8, 0)
    # init the canvas as white
    finalCanvasInfo = Array(ctypes.c_uint32, [0] * cs.CANVAS_DIM * cs.CANVAS_DIM * 2)

    # start processes
    processes = []
    for i in range(cs.NUM_THREADS):
        process = multiprocessing.Process(target=threadBody, args=(fileNum, finalCanvasInfo))
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

    # create canvas of just pixels
    finalCanvas = [ [(0xFF, 0xFF, 0xFF)] * cs.CANVAS_DIM for i in range(cs.CANVAS_DIM)]
    for i in range(cs.CANVAS_DIM):
        for j in range(cs.CANVAS_DIM):
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