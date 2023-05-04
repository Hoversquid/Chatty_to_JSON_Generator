import sys
import json
import os

class ChatTimeKeeper:
    def __init__(self, createdDay, createdHour, createdMinute, createdSecond):
        self.day = createdDay
        self.hour = createdHour
        self.minute = createdMinute 
        self.second = createdSecond

    def __str__(self):
        return 'Day: ' + str(self.day) + '\nHour: ' + str(self.hour) + '\nMinute: ' + str(self.minute) + '\nSecond: ' + str(self.second)

    def addToTime(self, timeStamp):
        pass
    
if __name__ == "__main__":
    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    rel_path = "Text\\2023-04-25_titatitanium.log"
    log_file_path = os.path.join(script_dir, rel_path)
    JSON_String = ''

    # with open(sys.argv[1]) as f:
    with open(log_file_path) as f:
        lines = f.readlines()

    # Read the initial timecode
    dateList = lines[0].split(': ')[1].replace('\r\n', '').split(' ')
    timeList = dateList[1].split(':')    
    timeZone = (dateList[-1][0:-3] + ':' + dateList[-1][-3:-1]).split(':')[0]

    localCreatedHour = int(timeList[0])
    globalCreatedHour = (localCreatedHour - int(timeZone)) % 24

    createdDay = int(dateList[0].split('-')[1])
    if localCreatedHour > globalCreatedHour:
        createdDay -= 1
    elif localCreatedHour < globalCreatedHour:
        createdDay += 1

    createdMinute = timeList[1]
    createdSecond = timeList[2]
    startingTimeStamp = str(globalCreatedHour) + ':' + dateList[1]

    timeKeeper = ChatTimeKeeper(createdDay, globalCreatedHour, createdMinute, createdSecond)
    print(timeKeeper)

    

    print('timeList: ' + ' '.join(dateList))
    print('timeZone: ' + str(timeZone))
    print('startingTimeStamp: ' + str(startingTimeStamp))
    # times = timeList[0] + 'T' + timeList[1] + 

