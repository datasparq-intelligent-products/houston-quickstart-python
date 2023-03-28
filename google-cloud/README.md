# Houston Quickstart - Google Cloud Platform

In this guide we will first set up a Houston server with terraform, then create a data pipeline using serverless tools. 
You will need access to a GCP project and have [gcloud](https://cloud.google.com/sdk/install) installed.

This guide will incur a Google Cloud bill of about £0.10. Care should be taken to delete all resources once completed, see [clean up](#clean-up).

This example uses Google Cloud Functions to execute each stage in the pipeline, which can be triggered with Google Cloud 
Pub/Sub, as well as with HTTP requests. This example uses Pub/Sub as this allows us to easily trigger functions in 
parallel, and guarantees our functions will execute by re-sending unacknowledged messages.

If you are following this quickstart in an environment where there already exist one or more Houston instances, for 
example a training project, then read [Appendix 1: Using Custom Names for Houston Infrastructure](#appendix-1--using-custom-names-for-houston-infrastructure)
first and take the additional actions mentioned.

Before continuing, clone this repo to your local machine:

```bash
git clone git@github.com:datasparq-intelligent-products/houston-quickstart-python.git
cd houston-quickstart-python/google-cloud
```

## Deploy via Terraform

1. Install terraform if you haven't already by following the instructions on the [terraform website](https://developer.hashicorp.com/terraform/tutorials/gcp-get-started/install-cli).
2. Once installed, authenticate with gcloud using the following commands.
   ```bash
   gcloud auth login
   gcloud auth application-default login
   gcloud config set project '<YOUR GCP PROJECT ID>'
   ```
3. Change directory to the [terraform directory](./google-cloud/terraform) and initialise terraform.
   ```bash
   cd google-cloud/terraform
   terraform init
   ```
4. Run `terraform plan` to ensure none of your existing infrastructure will be changed or destroyed. 
   Either use the `-var` argument to provide your project ID, or change the default 'project_id' variable value in [terraform/main.tf](./terraform/main.tf):
   ```bash
   export GCP_PROJECT=$(gcloud config get project)
   terraform plan -var project_id=${GCP_PROJECT}
   ```
5. Run `terraform apply` to deploy those changes to GCP:
   ```bash
   terraform apply -var project_id=${GCP_PROJECT}
   ```

The latest terraform documentation for the `houston` module can be found 
[here](https://registry.terraform.io/modules/datasparq-ai/houston/google/latest) and for `houston-key` 
[here](https://registry.terraform.io/modules/datasparq-ai/houston-key/google/latest)

You will also need to find your Houston Key and Houston Base URL to use the client and set up the Cloud Function. There are three ways
you can find this:
1. Getting them from the outputs defined in [terraform/outputs.tf](./terraform/outputs.tf): `terraform output -json`
2. Using gcloud to print the secret: `gcloud secrets versions access latest --secret=houston-base-url`
3. Going to [Google Compute Engine](https://console.cloud.google.com/compute/instances) and looking at the external IP, meaning your base URL is `http://<external ip>/api/v1`
4. Going to the [Secret Manager](https://console.cloud.google.com/security/secret-manager/secret/houston-base-url/versions) in the cloud console and viewing the secret value

## Create a Plan

We need to create a plan that Houston can follow to sting together each stage of this pipeline. Plans are defined in 
either YAML or JSON, and have the following structure:

```yaml
name: houston-quickstart

services:
  - name: houston-cloud-function
    trigger:
      method: pubsub
      topic: houston-cloud-function-topic

stages:
  - name: start
    service: houston-cloud-function
    downstream:
      - upload-file-customers
      - upload-file-sales
    params:
      operation: none
      ...
```

We want to define the following plan, comprised of 6 stages:

![](./plan.png)

The plan definition has been written out in [plan.yaml](plan.yaml). An equivalent written in JSON is also available 
as [plan.json](plan.json)

We'll use the Houston Python client to save the plan.

1. Set your Houston API key and Houston URL as an environment variable:  
   ```bash
   export HOUSTON_KEY='<your houston key>'
   export HOUSTON_BASE_URL='http://<your Houston VM public IP>/api/v1'
   ```
   **Never commit this key anywhere in your repo!**  
   If you prefer to read these values from secret manager using gcloud, you can use:
   ```bash
   export HOUSTON_KEY=$(gcloud secrets versions access latest --secret=houston-key)
   export HOUSTON_BASE_URL=$(gcloud secrets versions access latest --secret=houston-base-url)
   ```
2. Save the plan
   ```bash
   python -m houston save --plan plan.yaml
   ```
3. Go to your Houston server's dashboard (at `http://<your Houston VM public IP>`) and check your plan has appeared. 
   Click on it to view the DAG. Click on a stage to view its params. 

## Deploy a Cloud Function

For this example we've simplified things by using a single cloud function to execute each stage in the pipeline. This 
isn't recommended, but as all the tasks we need to complete in our pipeline can be done with Python, we'll create a 
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
       - Add an environment variable with NAME = `GCP_PROJECT` and VALUE = _your GCP project ID_
       - Add an environment variable with NAME = `HOUSTON_KEY` and VALUE = _your houston api key_
       - Add an environment variable with NAME = `HOUSTON_BASE_URL` and VALUE = _your houston server url_
     - On the Code page
       - Set the Runtime to Python 3.9
       - Copy _pusbsub_function/main.py_ into the box for MAIN.PY  
       - Copy _pusbsub_function/requirements.txt_ into the box for REQUIREMENTS.TXT
     - Click _Deploy_

   If using gcloud, run the following in the command line. (you may want to change the region to one closer to you):

   ```bash
   gcloud auth login
   export GCP_PROJECT=$(gcloud config get project)
   gcloud functions deploy houston-cloud-function --runtime python39 --trigger-topic houston-cloud-function-topic \
       --source pubsub_function --entry-point main --region europe-west2 --timeout 540 \
       --set-env-vars HOUSTON_KEY=$HOUSTON_KEY \
       --set-env-vars HOUSTON_BASE_URL=$HOUSTON_BASE_URL \
       --set-env-vars GCP_PROJECT=$GCP_PROJECT
   ```
   Note: the timeout is set to the maximum of 9 minutes. The default timeout may not be enough for most stages  
   Note: make sure that each of the environment variables used above is set (`echo $HOUSTON_KEY`) or **the function will not work**

3. Before we can use this function in our pipeline we need to grant it permission to trigger other functions. 
   Grant the Cloud Functions Invoker (roles/cloudfunctions.invoker) role to the calling function identity on the receiving function. By default, this identity is PROJECT_ID@appspot.gserviceaccount.com.

## Start a Mission

We will use the Houston Python client to create a mission and then trigger the first stages via Pub/Sub.

1. First, ensure that you have created 'default credentials', which are required to publish Pub/Sub messages:
   ```bash
   gcloud auth application-default login
   ```

2. Start a mission with the Python client from the command line: 
   ```bash
   export HOUSTON_KEY='<your api key>'
   export HOUSTON_BASE_URL='<your Houston url>'
   
   python -m houston start --plan houston-quickstart
   ```

3. Go to the dashboard and check the active (or possibly already finished) mission.

Congratulations! You've built a microservice pipeline. 

Now go to [your Cloud Function](https://console.cloud.google.com/functions/list) and view the logs to verify that the 
stages actually ran.

## Clean Up

To avoid unwanted charges for the VM used, delete all GCP resources.

1. Delete your Houston VM, secrets, and static IP address via terraform:
   ```bash
   export GCP_PROJECT=$(gcloud config get project)
   terraform destroy -var project_id=${GCP_PROJECT}
   ```

## Appendix 1: Using Custom Names for Houston Infrastructure

We recommend using one Houston key per GCP project, and one Houston API instance per organization. The Houston client
and the houston-key Terraform module are configured to look for a secret named 'houston-key' by default. 
To use multiple keys in one project you will need to use different name for each key.

Before using Terraform to create any infrastructure:
1. Open the [Terraform config](terraform/main.tf)  
2. If you want multiple Houston API instances in this GCP project, uncomment 'instance_name' and change this to a unique name 
3. If you want multiple Houston keys in this GCP project, uncomment 'secret_name' and change this to a unique name

If `houston_key_name` is changed, then the cloud function will need that value as an environment variable with the key 
`HOUSTON_KEY_SECRET_NAME`. Add the following to the `gcloud functions deploy` command:

```text
--set-env-vars HOUSTON_KEY_SECRET_NAME=<your houstuon_key_name>  \
```

In addition, anything you do locally with the Houston client (e.g. `python -m houston save`) will require this environment variable:
```bash
export HOUSTON_KEY_SECRET_NAME=<your houstuon_key_name>
```
