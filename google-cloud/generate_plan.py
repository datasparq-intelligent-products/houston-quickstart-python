
import json

topic = "houston-cloud-function-topic"

plan = {
  "name": "training-data-pipeline-XXX",
  "stages": [
    {
      "name": "start",
      "downstream": ["upload-file-customers", "upload-file-sales"],
      "params": {
        "topic": topic
      }
    },
    {
      "name": "upload-file-customers",
      "downstream": ["run-query-clean-customers"],
      "params": {
        "topic": topic,
        "operation": "upload",
        "file_location": "customers.csv"
      }
    },
    {
      "name": "upload-file-sales",
      "downstream": "run-query-clean-sales",
      "params": {
        "topic": topic,
        "operation": "upload",
        "file_location": "sales.csv"
      }
    },
    {
      "name": "run-query-clean-customers",
      "params": {
        "topic": topic,
        "operation": "query",
        "query_name": "foo.sql"
      }
    },
    {
      "name": "run-query-clean-sales",
      "params": {
        "topic": topic,
        "operation": "query",
        "query_name": "foo.sql"
      }
    },
    {
      "name": "run-query-report",
      "upstream": ["run-query-clean-customers", "run-query-clean-sales"],
      "params": {
        "topic": topic,
        "operation": "query",
        "query_name": "foo.sql"
      }
    }
  ]
}

# save plan as json
with open("plan.json", "w") as f:
  json.dump(plan, f, indent=2)
