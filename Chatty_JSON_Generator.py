import sys
import json
import os
import re

from datetime import datetime, timedelta

class ChatTimeKeeper:
    def __init__(self, dateList, timeList, timeOffset):

        self.timeOffset = 0
        self.createdDate = self.convertTimeStamp(dateList, timeList)
        print('Time keeper created at ' + str(self.createdDate))
        if timeOffset != 0:
        
            self.timeOffset = int(timeOffset)
            print('with time offset: ' + str(timeOffset))

        self.date = self.createdDate

    def getTimeStamp(self, withTimeZone):
        if withTimeZone:
            timeOffset = str(self.timeOffset) + ':00'
            dateToPrint = self.date + timedelta(hours=self.timeOffset)
        else:
            timeOffset = '.000Z'
            dateToPrint = self.date
            
        return dateToPrint.strftime('%Y-%m-%dT%H:%M:%S') + timeOffset
    
    # sets the new time of the Timekeeper with a date object
    def setNewTime(self, newTime):

        # Needs to get difference in time and add a day to the elapsed time if it passes the 24 hour mark
        if newTime < self.date:
            newTime += timedelta(days=1)

        self.date = newTime
        createdTimeDiff = newTime - self.createdDate
        return createdTimeDiff.total_seconds()

    # takes two lists of strings to create a datetime object
    def convertTimeStamp(self, dateList, timeList):

        # format of input lists given here:
        # - dateList: [yyy, mm, dd]
        # - timeList: [hh, mm, ss]

        # If no date is provided, use the one stored on the Timekeeper
        if dateList is None:
             year = self.date.year
             month = self.date.month
             day = self.date.day
             
        # Otherwise, set it from the provided list
        else:
            year = int(dateList[0])
            month = int(dateList[1])
            day = int(dateList[2])

        hour = int(timeList[0])

        newDateTime = datetime(year, month, day, hour, int(timeList[1]), int(timeList[2]))

        # If using a time offset, use it here
        if self.timeOffset != 0:
            newDateTime = newDateTime - timedelta(hours=self.timeOffset)

        return newDateTime



if __name__ == "__main__":
    # This section can read a relative path:
    # script_dir = os.path.dirname(__file__) # <-- absolute dir the script is in
    # rel_path = "Text\\yourlog.log"
    # log_file_path = os.path.join(script_dir, rel_path)

    print('args: ' + ' '.join(sys.argv))

    # This is the list of labels for the required arguments and their order
    # Argument amount can match to different label sets for future use cases
    argValNames = ['pyFile', 'file', 'timestamp', 'name', 'id']
    if len(sys.argv) != len(argValNames):
        print('ERROR: Incorrect amount of arguments.')
        print('Provide the arguments listed: ' + ', '.join(argValNames))
        sys.exit(0)
    
    # Handle each argument in order
    for argPos in range(len(argValNames)):
        currLabel = argValNames[argPos]
        match currLabel:
            case 'timestamp':
                dateList = sys.argv[argPos].split(' ')
            case 'name':
                streamerName = sys.argv[argPos]
            case 'id':
                streamerId = sys.argv[argPos]
            case 'file':
                with open(sys.argv[argPos], encoding='utf-8') as file:
                    lines = file.readlines()

    # This line can read the 'Log Started' line in Chatty, might be useful?    
    # dateList = lines[0].split(': ')[1].replace('\r\n', '').split(' ')

    # This line can read the Streamer name from Chatty but I'm just going to require it as an arg
    # streamerName = lines[1][lines[1].find('#'):lines[1].find('..')]

    # timeList is the hours, minutes, seconds pulled from the timestamp as a list
    timeList = dateList[1].split(':')   

    # if the time given has a time offset, set it
    if len(dateList) == 3:
        timeOffset = dateList[2][0:-2]
    else:
        timeOffset = 0

    # Create the timekeeper with the date argument as its starting point
    timeKeeper = ChatTimeKeeper(dateList[0].split('-'), timeList, timeOffset)

    # Gets user display name and badge information from extracted Chatty line user data
    def getUserInfo(displayName):
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
        
    # Concatenate the lines in an array
    commentJSONLines = []
    video_creation_time = timeKeeper.getTimeStamp(False)

    for line in lines:
        # Log messages start with a #, skip for now until the timestamp is needed to be parsed
        if line[0] == '#':
            # print('LOG LINE: ' + line)
            continue

        # Getting rid of anything that doesn't start with a timestamp just to be safe
        if line[0] != '[':
            # print('NO TIMESTAMP LINE: ' + line)
            continue

        # Parse the timestamp
        createdDateTime = timeKeeper.convertTimeStamp(None, line[1:9].split(':'))
        
        # Only display messages after the start time
        if createdDateTime < timeKeeper.createdDate:
            # print('TOO EARLY LINE: ' + line)
            continue

        # User names are surrounded with '< >' tags that start after the timestamp
        startOfNameIndex = line[10:12]

        # Don't create comment for non-user messages
        if startOfNameIndex != ' <':
            # print('NO NAME LINE: ' + line)
            continue

        
        # Get seconds between the timekeeper start and the message
        offsetSeconds = timeKeeper.setNewTime(createdDateTime)

        # Save the timecode to store on the JSON
        timeCode = timeKeeper.getTimeStamp(False)

        # Extract user info and message to put into a spoofed JSON file
        endOfNameIndex = line.find('> ')
        displayName = line[12:endOfNameIndex]
        message = line[endOfNameIndex+2:].replace('\n', '')
        name, badgeJSON = getUserInfo(displayName)

        # Pretty much all of this can be left blank
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

        commentJSONLines.append(commentJSON) 
        # End of JSON generation loop

    # Make header level data
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

    # Name file here:
    fileName = 'output.json'

    # Create new json file in folder
    with open(fileName, "w") as outfile:
        json.dump(fileJSON, outfile, indent=4)