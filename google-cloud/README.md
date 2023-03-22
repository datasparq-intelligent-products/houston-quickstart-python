
# Houston Quickstart - Google Cloud Platform
In this guide we will first show you how to setup your own Houston server with terraform. Once setup this guide will 
teach you how to use Houston to create a 100% serverless data pipeline on Google Cloud Platform using Python. You will 
need access to a GCP project and have [gcloud](https://cloud.google.com/sdk/install) installed.

This example uses Google Cloud Functions to execute each stage in the pipeline. The implementation would be the same for 
container based stages, just with different methods of triggering the stage.

Google Cloud Functions can be triggered with Google Cloud Pub/Sub, as well as with HTTP requests. This example uses 
Pub/Sub as this allows us to easily trigger functions in parallel, and guarantees our functions will execute by 
re-sending unacknowledged messages.

## Setup - Self Hosted via Terraform

1. First is to install terraform if you haven't already by following the instructions on the 
[terraform website](https://developer.hashicorp.com/terraform/tutorials/gcp-get-started/install-cli).
2. Once installed, authenticate with gcloud using the following commands.
```bash
   gcloud auth login
   gcloud auth application-default login
```
3. Change directory to the [terraform directory](./google-cloud/terraform) and initialise terraform.
```bash
    cd google-cloud/terraform
    terraform init
```
4. (Optional) There are three variables in [variables.tf](./google-cloud/terraform/variables.tf) that can be set when deploying 
with the terraform files provided. Defaults are set but if you wish to change them then `houston_zone` must be a valid 
GCP zone, `houston_compute_name` must be a valid GCP compute name and `houston_key_name` must be a valid secret name.
Details on how to pass this to terraform when planning or applying is available in the 
[terraform docs](https://developer.hashicorp.com/terraform/cli/commands/plan)
5. Run the command `terraform plan` to ensure none of your existing infrastructure will be changed or destroyed and then
run `terraform apply` to deploy those changes to GCP. An error will occur when trying to create the Houston API key:
```bash
╷
│ Error: Error making request
│ 
│   with module.houston-key.data.http.api_create_key,
│   on .terraform/modules/houston-key/main.tf line 8, in data "http" "api_create_key":
│    8: data "http" "api_create_key" {
│ 
│ Error making request: Post "http://<houston_ip_address>/api/v1/key": dial tcp <houston_ip_address>:80: connect: connection refused
╵
```
Re-run `terraform apply` after waiting some time, usually a few minutes, as the compute instance for the Houston server 
takes some time to setup. 

The latest terraform documentation for the `houston` module can be found 
[here](https://registry.terraform.io/modules/datasparq-ai/houston/google/latest) and for `houston-key` 
[here](https://registry.terraform.io/modules/datasparq-ai/houston-key/google/latest)

## Create a Plan

We need to create a plan that Houston can follow to sting together each stage of this pipeline. Plans are defined in 
either YAML or JSON, and have the following structure:

```json
{
   "name": "houston-quickstart",
   "services": [
      {
         "name": "my-microservice",
         "trigger": {
           "method": "pubsub",
           "topic": "houston-cloud-function-topic"
         }
      }
   ],
   "stages": [
      {
         "name": "upload-file-customers",
         "service": "my-microservice",
         "downstream": "run-query-clean-customers",
         "params": {
         }
      },
      {
         "name": "run-query-clean-customers",
         "service": "my-microservice",
         "params": {
         }
      },
      ...
   ]
}
```

We want to define the following plan, comprised of 7 stages:

![](./plan.png)

The plan definition has been written out in [plan.yaml](plan.yaml). An equivalent written in JSON is also available as [plan.json](plan.json)

We'll use the Houston Python client to save the plan.

1. Set your Houston API key as an environment variable:  
   ```bash
   export HOUSTON_KEY='<your api key>'
   ```
   **Never commit this key anywhere in your repo!**
   
   If you have a self-hosted solution then you will need another environment variable for the URL and port for your 
server.
   ```bash
   export HOUSTON_URL='<your Houston url>'
   ```
   
    If you didn't use the default value for `houston_key_name` then another environment variable is needed to specify 
that key name.
    ```bash
    export HOUSTON_KEY_SECRET_NAME='<your Houston key secret name>'
    ```

2. Save the plan
   ```bash
   python -m houston save --plan plan.yaml
   ```

3. Go to your self-hosted server's dashboard and check your plan has appeared. Click on it to view the DAG. Click on a 
stage to view its params. 

## Deploy a Cloud Function

For this example we've simplified things by using a single cloud function to execute each stage in the pipeline. This 
isn't recommended but as all the tasks we need to complete in our pipeline can be done with Python, we'll create a 
single cloud function that will execute a Python function corresponding to the Houston stage it's running.

1. Take a look at [pubsub_function/main.py](pubsub_function/main.py). Note the use of `@service()`. 
   This is a wrapper, which adds lots of functionality to the function it's decorating, and changes its arguments 
   to the arguments that Google Cloud Functions expects (event and context objects).
   Take a look at the [source code](https://github.com/datasparq-intelligent-products/houston-python/blob/feature/cloud-function-wrapper/houston/gcp/cloud_function.py) 
   for this wrapper to understand what the resulting function does.  

2. Deploy with the function either from the [Cloud Console](https://console.cloud.google.com/functions), or with gcloud:

   If using the Cloud Console (As of March 2023):
     - On the Configuration page, under Trigger:
       - Set the trigger to Pub/Sub and create a new topic called _'houston-cloud-function-topic'_
     - Under Runtime > Runtime Environment Variables
       - Add an environment variable with NAME = `GCLOUD_PROJECT` and VALUE = _your GCP project ID_
       - Add an environment variable with NAME = `HOUSTON_KEY` and VALUE = _your houston api key_
       - If self-hosting, add an environment variable with NAME = `HOUSTON_URL` and VALUE = _your houston server url_
     - On the Code page
       - Set the Runtime to Python 3.9
       - Copy _pusbsub_function/main.py_ into the box for MAIN.PY  
       - Copy _pusbsub_function/requirements.txt_ into the box for REQUIREMENTS.TXT
     - Click _Deploy_

        If using gcloud, run the following in the command line. (you may want to change the region to one closer to you):

   ```bash
   gcloud auth login
   gcloud functions deploy houston-cloud-function --runtime python39 --trigger-topic houston-cloud-function-topic \
       --source pubsub_function --entry-point main --region europe-west2 --timeout 540 \
       --set-env-vars HOUSTON_KEY=$HOUSTON_KEY
   ```
   Note: the timeout is set to the maximum of 9 minutes. The default timeout may not be enough for most stages. 

3. Before we can use this function in our pipeline we need to grant it permission to trigger other functions. Grant the Cloud Functions Invoker (roles/cloudfunctions.invoker) role to the calling function identity on the receiving function. By default, this identity is PROJECT_ID@appspot.gserviceaccount.com.

## Start a Mission

We will use the Houston Python client to create a mission and then trigger the first stages via Pub/Sub.

1. First, ensure that you have created 'default credentials', which are required to publish Pub/Sub messages:
   ```bash
   gcloud auth application-default login
   ```

2. Start a mission with the Python client from the command line: 
   ```bash
   export HOUSTON_KEY='<your api key>'
   # If you are self-hosting Houston also add this environment variable:
   export HOUSTON_URL='<your Houston url>'
   # If you did not use the default Houston secret name, also add this environment variable:
   export HOUSTON_KEY_SECRET_NAME='<your Houston key secret name>'
   
   python -m houston start --plan houston-quickstart
   ```

3. Go to your self-hosted one and check the active (or possibly already finished) mission.

Congratulations! You've got a working microservice pipeline. 

Now go to [your Cloud Function](https://console.cloud.google.com/functions/list) and view the logs to verify that the 
stages actually ran.

## (Optional) Clean Up

1. Delete your plan:
   ```bash
   python -m houston delete --plan houston-quickstart
   ```
