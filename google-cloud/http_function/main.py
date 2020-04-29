from houston import Houston
import requests
import os

import google.cloud.logging
client = google.cloud.logging.Client()
client.setup_logging()
import logging

KEY = os.getenv('API_KEY')


def main(request):
    """HTTP Cloud Function.
    :param flask.Request request: The request object - http://flask.pocoo.org/docs/1.0/api/#flask.Request
    """

    # initialise Houston client
    h = Houston(plan="houston-quickstart", api_key=KEY)

    stage = request.args.get('stage')

    if stage == "start":
        # start a new mission and get an ID for it
        mission_id = h.create_mission()
    else:
        mission_id = request.args.get('mission_id')

    # call houston to start the stage
    response = h.start_stage(stage, mission_id=mission_id)
    logging.info(response)

    #
    #
    #

    # run the main process - depending on the stage name
    if 'upload-file' in stage:
        upload_file(request.args.get('file_name'))

    elif 'run-query' in stage:
        run_query(request.args.get('query_name'))

    elif 'build-report' in stage:
        build_report(request.args.get('source_table'))

    elif stage == "start":
        pass

    else:
        raise ValueError(f"Didn't know what task to run for stage: '{stage}'")

    #
    #
    #

    # call houston to end the stage - response from houston will tell us which stages are next
    response = h.end_stage(stage, mission_id)
    logging.info(response)

    # trigger the next stage(s)
    for next_stage in response['next']:

        headers = get_authorization_headers(response['params'][next_stage]['uri'])

        # don't wait for requests to resolve - this allows stages to run concurrently
        fire_and_forget(response['params'][next_stage]['uri'], headers=headers, params=response['params'][next_stage])

    return "stage finished", 200


#
# utils
#


# https://cloud.google.com/functions/docs/securing/authenticating
def get_authorization_headers(target_url):

    # Set up metadata server request
    # See https://cloud.google.com/compute/docs/instances/verifying-instance-identity#request_signature
    token_request_url = 'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity?audience=' + target_url
    token_request_headers = {'Metadata-Flavor': 'Google'}

    # Fetch the token
    token_response = requests.get(token_request_url, headers=token_request_headers)
    jwt = token_response.content.decode("utf-8")

    # Provide this token in the request to the receiving function
    print(jwt)
    return {'Authorization': f'bearer {jwt}'}


#
# utils
#


def fire_and_forget(url, headers, params):
    """Send a get request without waiting for it to resolve.
    """
    try:
        requests.get(url, headers=headers, params=params, timeout=1)
    except requests.exceptions.ReadTimeout:
        pass


#
# tasks
#


def upload_file(file_location):
    pass


def run_query(query_name):
    pass


def build_report(source_table):
    pass
