"""Example Houston Stage"""

import os
from houston.plugin.gcp import GCPHouston as Houston

KEY = os.getenv('API_KEY')


def main(event, context):
    """Google Cloud Function for running simple Python functions. The function run depends on the Houston stage
    specified in the message event.

    :param dict event: Event payload - expected to contain Houston 'stage', 'mission_id', and all stage parameters.
    :param google.cloud.functions.Context context: Metadata for the event.
    """

    # initialise Houston client
    h = Houston(plan="houston-quickstart", api_key=KEY)

    # get instructions from the message that triggered this function
    stage_info = h.extract_stage_information(event["data"])
    stage = stage_info['stage']

    if stage == "start":
        # start a new mission and get an ID for it
        mission_id = h.create_mission()
        print(f"Starting a new mission with id: {mission_id}")
    else:
        # otherwise continue the existing mission
        mission_id = stage_info['mission_id']

    # call houston to start the stage
    stage_detail = h.start_stage(stage, mission_id=mission_id)

    #
    #
    #

    # run the main process
    if 'file_location' in stage_detail["params"]:
        upload_file(stage_detail["params"]["file_location"])

    elif 'query_name' in stage_detail["params"]:
        run_query(stage_detail["params"]["query_name"])

    elif 'source_table' in stage_detail["params"]:
        build_report(stage_detail["params"]["source_table"])

    # call houston to end the stage - response from houston will tell us which stages are next
    response = h.end_stage(stage, mission_id)
    # trigger the next stage(s)
    h.call_stage_via_pubsub(response, mission_id)
    return

#
# tasks
#


def upload_file(file_location):
    print(f"Uploading File: {file_location}")
    pass


def run_query(query_name):
    print(f"Running Query: {query_name}")
    pass


def build_report(source_table):
    print(f"Building Report: {source_table}")
    pass
