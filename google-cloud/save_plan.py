
from houston import client
import os

KEY = os.getenv('HOUSTON_KEY')

url = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv"
bucket_name = "gcs-training-cf-34th"
file_name = "us-counties.csv"
query_file_name = "casualties_percentage_by_state.sql"
target_table_name = "clean"
target_dataset = "todor_training_clean"
dataset_id = "todor_training_raw"
table_id = "raw"
gcs_uri = "gs://gcs-training-cf-35th/corona_cases.csv"


plan = {
  "name": "training-data-pipeline-todor",
  "stages": [
    {
      "name": "start",
      "downstream": "download-covid-cases-data",
      "params": {
        "psq": "begin-pipeline",
        "time_to_wait": "3",
      }
    },
    {
      "name": "download-covid-cases-data",
      "downstream": ["wait-5-seconds", "load-corona-data-into-bigquery"],
      "params": {
        "psq": "get-file-from-url",
        "url": url,
        "bucket_name": bucket_name,
        "file_name": file_name,
      }
    },
    {
      "name": "wait-5-seconds",
      "params": {
        "psq": "begin-pipeline",
        "time_to_wait": "5",
      }
    },
    {
      "name": "load-corona-data-into-bigquery",
      "params": {
        "psq": "save-file-to-BQ",
        "dataset_id": dataset_id,
        "table_id": table_id,
        "gcs_uri": gcs_uri,
      }
    },
    {
      "name": "run-query-clean-sales",
      "upstream": ["wait-5-seconds", "load-corona-data-into-bigquery"],
      "params": {
        "psq": 	"execute-query",
        "query_file_name": query_file_name,
        "target_table_name": target_table_name,
        "target_dataset": target_dataset,
      }
    },
  ]
}

# initialise Houston client
h = client.Houston(plan=plan, api_key=KEY)

# note: if you want to change an existing plan you'll need to delete it first
# h.delete_plan()

# save the plan
h.save_plan()

# what variables to pass as env.variables and which to pass through Houston + which to set as secrets
