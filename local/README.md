
# Houston Quickstart - Local Machine

This guide explains how to run a Houston mission (workflow or DAG) entirely locally, using a locally hosted Houston API 
and locally hosted microservice. Messages will be sent between services via HTTP.

This is not the recommended way to use Houston; the main advantages of Houston come from running workflows on serverless 
tools from cloud providers such as Google Cloud Functions, or AWS Lambdas. These allow for better parallelism, lower 
cost, lower maintenance, and ease of code reuse.

Once you understand how Houston works, we recommend following the quickstart guide for [Google Cloud](../google-cloud). 


### 1. Create a Houston API server

#### 1.1. Install Houston

If you have [go](https://golang.org/doc/install) installed you can build the binary yourself and install with:

```bash
go install github.com/datasparq-ai/houston
```

#### 1.2. Start the API Locally 

Start a local Houston server with the default config:

```bash
houston api
```

#### 1.3. Create an API Key

The server is now running at `localhost:8000`. To ensure the houston client can find our API,
we need to set the following environment variable:

```bash
export HOUSTON_BASE_URL="http://localhost:8000/api/v1"
```


Create a new Houston key with ID = 'quickstart':

```bash
houston create-key -i quickstart -n quickstart
```


### 2. Create a Plan

First, clone the quickstart repository:

```bash
git clone git@github.com:datasparq-intelligent-products/houston-quickstart-python.git
cd houston-quickstart-python/local
```

There is an example plan in this repository; see [plan.yaml](plan.yaml). It contains:
- A service definition, which tells our services how to trigger each other:
  ```yaml
  services:
   - name: local-http-service
     trigger:
       method: http
       url: http://localhost:8001/houston
  ```
- Stages, containing the parameters for each stage, and the dependencies between stages (upstream and downstream):
  ```yaml
  stages:
   - name: start
     service: local-http-service
     downstream:
       - intro
     params:
       operation: "start-story"
  ```

TODO: install houston Python client  

Save the plan using the python client. We need to tell the client which key to use and the address of our 
Houston server, via environment variables:

```bash
export HOUSTON_KEY=quickstart
export HOUSTON_BASE_URL="http://localhost:8000/api/v1"
python -m houston save plan.yaml
```

Then go to http://localhost:8000. Enter your Houston key 'quickstart'.


#### 3. Create a service

A simple HTTP server application has been defined in [http_service/main.py](http_service/main.py). 
It uses the Houston Python client to communicate with your local Houston API server and then carry 
out a task corresponding to the parameters of the stage it has been asked to run.

First, install the Python requirements for this service:

```bash
cd local/http_service
pip install -r requirements.txt
```

Start the Service, which also needs to know our key and server URL:

```bash
export HOUSTON_KEY=quickstart
export HOUSTON_BASE_URL="http://localhost:8000/api/v1"
uvicorn main:app --reload --port 8001
```

#### 4. Run a Workflow (Mission)

(in a new terminal window) Start a Mission:

```bash
export HOUSTON_KEY=quickstart
export HOUSTON_BASE_URL="http://localhost:8000/api/v1"
python -m houston start houston-quickstart
```

View the dashboard at http://localhost:8000/ to see the newly created mission (which appears as a circle underneath the 
name of the plan). All stages should be green if they have completed successfully. 

If your mission hasn't started, check your HTTP service for error logs. 

If your mission completes without any errors, you will see that it completed almost instantly. This is because our 
stages only take a few milliseconds, and the communication between the service and the API server is also in the order 
of a few milliseconds.

