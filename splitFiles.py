# open file to read from
fileName = '2022_place_canvas_history'
fileRead = open(fileName + '.csv', 'r')

# read header line
headerLine = fileRead.readline()
line = fileRead.readline()
lineCount = 1

# open file to write to
fileNum = 0
fileWrite = open(fileName + str(fileNum) + '.csv', 'w')
fileWrite.write(headerLine)

linesPerFile = 1000000

while len(line) > 0:
    # print rudimentary loading bar
    if lineCount % 10000 == 0:
        print('.', end='')
    
    # open new file
    if lineCount % linesPerFile == 0:
        fileWrite.close()
        fileNum += 1
        fileWrite = open(fileName + str(fileNum) + '.csv', 'w')
        fileWrite.write(headerLine)

    fileWrite.write(line)
    # read the next line
    line = fileRead.readline()
    lineCount += 1