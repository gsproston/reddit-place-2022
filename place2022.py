# open file
import csv


file = open('2022_place_canvas_history.csv', 'r')

# read header line
line = file.readline()
line = file.readline()
lineNum = 1

while len(line) > 0:
    # print rudimentary loading bar
    if lineNum % 10000 == 0:
        print('.', end='')

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

    # read the next line
    line = file.readline()
    lineNum += 1
