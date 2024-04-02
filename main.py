from sseclient import SSEClient
import requests
import json
import re
import requests
from ditto_threads import dittoCurrentStateThread, dittoGeneralInfoThread
import os
from dotenv import load_dotenv

load_dotenv()
DITTO_THING_SUFIX_REGEX = os.getenv('DITTO_THING_SUFIX_REGEX')
DITTO_BASE_URL = os.getenv('DITTO_BASE_URL')

url = DITTO_BASE_URL + '/api/2/things'
hearders = {'Accept': 'text/event-stream'}
response = requests.get(url=url, stream=True, headers=hearders)
client = SSEClient(response)

for event in client.events():
        if event.data:
            data = json.loads(event.data)
            print(data['thingId'])
            split = data['thingId'].split(':')
            if len(data) > 1 and re.fullmatch(DITTO_THING_SUFIX_REGEX, split[1]):
                thread = dittoCurrentStateThread(split[1])
            #else: thread = dittoGeneralInfoThread(split[1]) #it will commented until it is found if it is necessary
            thread.run()