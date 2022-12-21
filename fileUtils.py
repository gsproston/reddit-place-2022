import os

FILE_NAME = '2022_place_canvas_history'
MAX_FILE_NUM = 160

def getPathToNextFile(fileNum):
    with fileNum.get_lock():
        if fileNum.value > MAX_FILE_NUM:
            # silently exit
            return None
        fileNum.value += 1
        return os.path.join('input', FILE_NAME + str(fileNum.value) + '.csv')