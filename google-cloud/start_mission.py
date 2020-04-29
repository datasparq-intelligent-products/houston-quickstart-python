
from houston import Houston
from requests_futures.sessions import FuturesSession
import os

KEY = os.getenv('API_KEY')

# initialise Houston client
h = Houston(plan="houston-quickstart", api_key=KEY)

# start a new mission and get an ID for it
mission_id = h.create_mission()

# trigger the first stage - it's a dummy stage
h.start_stage("start", mission_id)

# call houston to end the stage - response from houston will tell us which stages are next
response = h.end_stage("start", mission_id)

# requests-futures session allows us to make requests asynchronously
session = FuturesSession()

# trigger the next stage(s)
for next_stage in response['next']:
    session.get(response['params'][next_stage]['uri'], params=response['params'][next_stage])

    # don't wait for requests to resolve - this allows stages to run concurrently
