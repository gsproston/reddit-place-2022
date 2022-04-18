from datetime import datetime

class PixelInfo:
    def __init__(self, date, userIdHash, colour, coords):
        self.date = date
        self.userIdHash = userIdHash
        self.colour = colour
        self.coords = coords

    def getShortDate(self):
        startTime = datetime(2022, 4, 1, 0, 0, 0)
        timestampDiff = self.date.timestamp() - startTime.timestamp()
        return int(timestampDiff * 1000)