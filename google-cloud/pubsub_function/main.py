from houston.plugin.gcp import GCPHouston as Houston
import os

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
    else:
        # otherwise continue the existing mission
        mission_id = stage_info['mission_id']

    # call houston to start the stage
    h.start_stage(stage, mission_id=mission_id)

    #
    #
    #

    # run the main process
    if 'upload-file' in stage:
        upload_file(stage_info['file_name'])

    elif 'run-query' in stage:
        run_query(stage_info['query_name'])

    elif 'build-report' in stage:
        build_report(stage_info['source_table'])

    else:
        raise ValueError(f"Didn't know what task to run for stage: '{stage}'")

    #
    #
    #

    # call houston to end the stage - response from houston will tell us which stages are next
    response = h.end_stage(stage, mission_id)

    # trigger the next stage(s)
    h.call_stage_via_pubsub(response, mission_id)


#
# tasks
#


def upload_file(file_location):
    pass


def run_query(query_name):
    pass


def build_report(source_table):
    pass
