"""Example Houston Service"""

from houston.gcp.cloud_function import service


@service(name="My Service")
def main(operation: str, file_location: str = None, query_name: str = None, source_table: str = None):
    """Google Cloud Function for running simple Python functions. The function run depends on the Houston stage
    parameters defined in the plan.
    """

    if operation == "upload":
        upload_file(file_location)

    elif operation == "query":
        run_query(query_name)

    elif operation == "report":
        build_report(source_table)


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
