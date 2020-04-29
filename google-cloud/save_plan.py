
from houston import Houston
import os

KEY = os.getenv('API_KEY')
ENV = os.getenv('PIPELINE_ENV', 'dev')
ps_topic = os.getenv('PS_TOPIC', "houston-cloud-function-topic")

# define plan - some parameters are dependent on the environment
plan = {
  "name": "houston-quickstart",
  "stages": [
    # a dummy stage at the start is useful for triggering the pipeline with one request
    {
      "name": "start",
      "downstream": ["upload-file-customers", "upload-file-sales"],
    },
    {
      "name": "upload-file-customers",
      "downstream": "run-query-clean-customers",
      "params": {
        "psq": ps_topic,
        "file_location": f"./data-bucket-{ENV}/customers_raw.csv",
      }
    },
    {
      "name": "run-query-clean-customers",
      "params": {
        "psq": ps_topic,
        "query_name": "clean_customers.sql"}
    },
    {
      "name": "upload-file-sales",
      "downstream": "run-query-clean-sales",
      "params": {
        "psq": ps_topic,
        "file_location": f"./data-bucket-{ENV}/sales_raw.csv"}
    },
    {
      "name": "run-query-clean-sales",
      "params": {
        "psq": ps_topic,
        "query_name": "clean_sales.sql"}
    },
    {
      "name": "run-query-report",
      "upstream": [
        "run-query-clean-customers",
        "run-query-clean-sales"
      ],
      "downstream": "build-report",
      "params": {
        "psq": ps_topic,
        "query_name": "report_data.sql"}
    },
    {
      "name": "build-report",
      "params": {
        "psq": ps_topic,
        "source_table": "report_data"}
    }
  ]
}

# initialise Houston client
h = Houston(plan=plan, api_key=KEY)

# note: if you want to change an existing plan you'll need to delete it first
# h.delete_plan()

# save the plan
h.save_plan()
