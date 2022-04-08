# open file
import csv


file = open('2022_place_canvas_history.csv', 'r')

# read header line
line = file.readline()
line = file.readline()
lineCount = 1
width = 0
height = 0

while len(line) > 0:
    # print rudimentary loading bar
    if lineCount % 10000 == 0:
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
    colour = fields[2]
    # trim the leading '"'
    x = fields[3][1:]
    # trim the ending '"' and '\n'
    y = fields[4][:-2]

    # check x and y are ints 
    if not x.isdecimal() or not y.isdecimal():
        print("Could not parse co-ordinates")
        break

    # convert to ints
    x = int(x)
    y = int(y)

    # calculate the width and height of the canvas
    if x > width:
        width = x
    if y > height:
        height = y

    # read the next line
    line = file.readline()
    lineCount += 1

print("Width: "  + x + " Height: " + y)