import sys
import json
import os
import re

from datetime import datetime, timedelta

class ChatTimeKeeper:
    def __init__(self, dateList, timeList, timeOffset):

        self.timeOffset = int(timeOffset)
        self.createdDate = self.convertTimeStamp(dateList, timeList)
        self.date = self.createdDate

    def getTimeStamp(self, withTimeZone):
        if withTimeZone:
            timeOffset = str(self.timeOffset) + ':00'
            dateToPrint = self.date + timedelta(hours=self.timeOffset)
        else:
            timeOffset = '.000Z'
            dateToPrint = self.date
            
        return dateToPrint.strftime('%Y-%m-%dT%H:%M:%S') + timeOffset
    
    def setNewTime(self, newTime):
        timeDiff = newTime - self.date
        self.date += timeDiff
        createdTimeDiff = newTime - self.createdDate
        return createdTimeDiff.total_seconds()

    def convertTimeStamp(self, dateList, timeList):

        # dateList: yyy, mm, dd
        # timeList: hh, mm, ss

        if dateList is None:
             year = self.date.year
             month = self.date.month
             day = self.date.day
             hour = self.date.hour
        else:
            year = int(dateList[0])
            month = int(dateList[1])
            day = int(dateList[2])
            hour = int(timeList[0])

        newDateTime = datetime(year, month, day, hour, int(timeList[1]), int(timeList[2]))
        if dateList is not None:
            newDateTime = newDateTime - timedelta(hours=self.timeOffset)

        return newDateTime
    
if __name__ == "__main__":
    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    # rel_path = "Text\\yourlog.log"
    # log_file_path = os.path.join(script_dir, rel_path)

    print('args: ' + ' '.join(sys.argv))

    # with open(log_file_path) as f:
    with open(sys.argv[1]) as f:
        lines = f.readlines()

    # Read the initial timecode
    if len(sys.argv) > 1 != None and sys.argv[2] is not None:
        dateList = sys.argv[2].split(' ')
    else: 
        dateList = lines[0].split(': ')[1].replace('\r\n', '').split(' ')

    timeList = dateList[1].split(':')    
    timeZone = (dateList[-1][0:-3] + ':' + dateList[-1][-3:-1]).split(':')[0]

    timeKeeper = ChatTimeKeeper(dateList[0].split('-'), timeList, timeZone)

    streamerName = lines[1][lines[1].find('#'):lines[1].find('..')]

    del lines[0:3]

    def getUserInfo(displayName):
        print('displayName: ' + displayName)
        readingBadges = True
        badgeJSON = []
        while readingBadges:
            if displayName[0] == '!':
                displayName = displayName[1:]
                badgeJSON.append({"_id": "vip", "version": "1"})
            elif displayName[0:2] == '~%':
                displayName = displayName[2:]
                badgeJSON.append({ "_id": "broadcaster", "version": "1" })
            else:
                readingBadges = False

        return displayName, badgeJSON
        
    commentJSONLines = {"comments": []}

    video_creation_time = timeKeeper.getTimeStamp(False)

    for line in lines:
        startOfNameIndex = line[10:12]

        # Don't create comment for non-user messages
        if startOfNameIndex != ' <':
            continue

        
        createdDateTime = timeKeeper.convertTimeStamp(None, line[1:9].split(':'))
        offsetSeconds = timeKeeper.setNewTime(createdDateTime)
        timeCode = timeKeeper.getTimeStamp(False)
        endOfNameIndex = line.find('> ')
        displayName = line[12:endOfNameIndex]

        message = line[endOfNameIndex+2:].replace('\n', '')
        name, badgeJSON = getUserInfo(displayName)
        commentJSON = {
            "_id": "", 
            "created_at": str(timeCode),
            "channel_id": "", 
            "content_type": "video", 
            "content_id": "",
            "content_offset_seconds": int(offsetSeconds),
            "commenter": {
                "display_name": name,
                "_id": "",
                "name": "",
                "bio": "",
                "created_at": "",
                "updated_at": "",
                "logo": ""
            },
            "message": {
                "body": message,
                "bits_spent": 0,
                "fragments": [
                    {
                        "text":  message,
                        "emoticon": None
                    }
                ],
                "user_badges": badgeJSON,
                "user_color": None,
                "emoticons": []
            }
        }

        commentJSONLines['comments'].append(commentJSON) 

    fileJSON = {
        "FileInfo": {
            "Version": {
                "Major": 1,
                "Minor": 3,
                "Patch": 0
            },
            "CreatedAt": timeKeeper.getTimeStamp(True),
            "UpdatedAt": "0001-01-01T00:00:00",
        },
        "streamer": {
            "name": streamerName,
            "id": ""
        },
        "video": {
            "title": "",
            "id": "",
            "created_at": video_creation_time,
            "start": 0,
            "end": int((timeKeeper.date - timeKeeper.createdDate).total_seconds()),
            "length": int((timeKeeper.date - timeKeeper.createdDate).total_seconds()),
            "chapters": []
        },
        "comments": commentJSONLines,
        "embeddedData": None
    }

    with open("sample.json", "w") as outfile:
        json.dump(fileJSON, outfile, indent=4)