# Chatty_to_JSON_Generator

First argument is a *relative* path to the Chatty Log.

Second argument is optional to add a custom video start time.

Command should look like this: 

`py .\Chatty_JSON_Generator.py 'Text\2023-04-25_streamer.log' '2023-04-25 15:00:47 -0400'`

----------------------------------------------------------------------------

This will only currently reliably work with an added argument structured like this (with quotes) 'YYYY-MM-DD HH:MM:SS TZ00' (TZ00 is time zone offset from GMT, i.e. 0500, -1200)

It will also work with the first line of the Chatty Log being the start of the log, which will set the time of the video from when the log was started: (i.e. first line being: '# Log started: 2023-04-25 15:00:42 -0400')
