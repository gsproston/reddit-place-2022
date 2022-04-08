import os
from PIL import Image
import numpy as np

# open file
fileName = os.path.join('input', '2022_place_canvas_history.csv')
file = open(fileName, 'r')

# read header line
line = file.readline()
line = file.readline()
lineCount = 1

# width and height of the canvas
dims = 4000
# init the canvas as white
finalCanvas = [ [(0xFF,0xFF,0xFF)] * dims for i in range(dims)]

while len(line) > 0:
    # print rudimentary loading bar
    if lineCount % 100000 == 0:
        print('.', end='')
        lineCount = 0

    # parse out each field
    fields = line.split(',')
    # make sure there are enough fields
    if len(fields) < 5:
        print("Too few fields")
        break

    date = fields[0]
    userIdHash = fields[1]
    # get colour information
    r = int(fields[2][1:3], 16)
    g = int(fields[2][3:5], 16)
    b = int(fields[2][5:],  16)
    # trim the leading '"'
    x = int(fields[3][1:])
    # trim the trailing '"' and '\n'
    y = int(fields[4][:-2])

    finalCanvas[x][y] = (r, g, b)

    # read the next line
    line = file.readline()
    lineCount += 1

# Convert the pixels into an array using numpy
array = np.array(finalCanvas, dtype=np.uint8)
# Use PIL to create an image from the new array of pixels
finalImage = Image.fromarray(array)
finalImage.save('finalCanvas.png')