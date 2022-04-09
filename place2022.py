from asyncio.windows_events import NULL
from datetime import datetime
import os
from PIL import Image
import numpy as np

class PixelInfo:
    def __init__(self, date, userIdHash, colour, coords):
        self.date = date
        self.userIdHash = userIdHash
        self.colour = colour
        self.coords = coords

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
    # get colour information
    r = int(fields[2][1:3], 16)
    g = int(fields[2][3:5], 16)
    b = int(fields[2][5:],  16)
    # trim the leading '"'
    x = int(fields[3][1:])
    # trim the trailing '"' and '\n'
    y = int(fields[4][:-2])

    return PixelInfo(date, userIdHash, (r, g, b), (x, y))

# open file
fileName = os.path.join('input', '2022_place_canvas_history.csv')
file = open(fileName, 'r')

# read header line
line = file.readline()
# read first line of data
line = file.readline()
lineCount = 1

# width and height of the canvas
dims = 2000
# init the canvas as white
finalCanvasInfo = [ [NULL] * dims for i in range(dims)]

while len(line) > 0:
    # print rudimentary loading bar
    if lineCount % 100000 == 0:
        print('.', end='')
        lineCount = 0

    pixelInfo = getPixelInfo(line)
    if (pixelInfo != NULL):
        x = pixelInfo.coords[0]
        y = pixelInfo.coords[1]
        # only hold the pixel info if there's no entry or the entry is later
        if (finalCanvasInfo[x][y] == NULL or 
            finalCanvasInfo[x][y].date < pixelInfo.date):
            finalCanvasInfo[x][y] = pixelInfo

    # read the next line
    line = file.readline()
    lineCount += 1

# create canvas of just pixels
finalCanvas = [ [(0xFF, 0xFF, 0xFF)] * dims for i in range(dims)]
for i in range(dims):
    for j in range(dims):
        if (finalCanvasInfo[i][j] != NULL):
            finalCanvas[i][j] = finalCanvasInfo[i][j].colour

# Convert the pixels into an array using numpy
array = np.array(finalCanvas, dtype=np.uint8)
# Use PIL to create an image from the new array of pixels
finalImage = Image.fromarray(array)
finalImage.save('finalCanvas.png')