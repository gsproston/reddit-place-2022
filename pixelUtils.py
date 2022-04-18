from asyncio.windows_events import NULL
from datetime import datetime

from PixelInfo import PixelInfo

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