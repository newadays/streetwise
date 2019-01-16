# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import json
import logging
from datetime import datetime, tzinfo, timedelta
import requests
import uuid

from flask import current_app, Flask, render_template, request
from google.cloud import pubsub_v1
from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials


app = Flask(__name__)

# Configure the following environment variables via app.yaml
# This is used in the push request handler to veirfy that the request came from
# pubsub and originated from a trusted source.
# app.config['PUBSUB_VERIFICATION_TOKEN'] =  os.environ['PUBSUB_VERIFICATION_TOKEN']
# app.config['PUBSUB_TOPIC'] = os.environ['PUBSUB_TOPIC']
# app.config['PROJECT'] = os.environ['GOOGLE_CLOUD_PROJECT']
# app.config['SENSORS_TOKEN'] = os.environ['SENSORS_TOKEN']

app.config['PUBSUB_VERIFICATION_TOKEN'] = 'gbenga'
app.config['PUBSUB_TOPIC'] = 'street-sensors'
app.config['PUBSUB_HISTORICAL_TOPIC'] = 'historical'
app.config['PROJECT'] = 'data-streamwise'
app.config['SENSORS_TOKEN'] = 'baRUbRLnaRUQk8RGJXpA2ezoV'


# Global list to storage messages received by this instance.
MESSAGES = []


# [START query_data_from_sensors_across_the_city]
def query_sensors(token):
    """
    Queries the Google Books API to find detailed information about the book
    with the given title.
    """
    r = requests.get('https://data.cityofchicago.org/resource/m65n-ux8y.json', headers={
        'X-App-Token': token
    })
    try:
        data = r.json()
        return data
    except KeyError:
        logging.info("No data received from data_street url {}".format('m65n-ux8y.json'))
        return None
    except ValueError:
        logging.info("Unexpected response from books API: {}".format(r))
        return None
# [END query_sensors]


# [START query_historical data]
def historical_job(token):
    """
    Queries the Google Books API to find detailed information about the book
    with the given title.
    """
    class simple_utc(tzinfo):
        def tzname(self, **kwargs):
            return "UTC"

        def utcoffset(self, dt):
            return timedelta(0)

    curr_time = datetime.utcnow().replace(tzinfo=simple_utc()).isoformat().split('.',1)[0]
    r = requests.get('https://data.cityofchicago.org/resource/kf7e-cur8.json?$where=time between "2017-01-01T12:00:00" and "{}"'.format(curr_time), headers={
        'X-App-Token': token
    })
    try:
        data = r.json()
        return data
    except KeyError:
        logging.info("No data received from data_street url {}".format('kf7e-cur8.json'))
        return None
    except ValueError:
        logging.info("Unexpected response from books API: {}".format(r))
        return None
# [END query_historical_data]


def datastore_to_gcs(entity, kind, location):
    credentials = GoogleCredentials.get_application_default()
    service = build('dataflow', 'v1b3', credentials=credentials)

    # Set the following variables to your values.
    JOBNAME = 'datastore-to-gcs'
    PROJECT = 'data-streamwise'
    BUCKET = 'streamwise'
    TEMPLATE = 'Datastore_to_GCS_Text.json'
    NAMESPACE = entity

    GCSPATH = "gs://{bucket}/templates/{template}".format(bucket=BUCKET, template=TEMPLATE)
    BODY = {
        "jobName": "{jobname}".format(jobname=JOBNAME),
        "parameters": {
            "datastoreReadGqlQuery": "SELECT * FROM {KIND}".format(KIND=kind),
            "datastoreReadProjectId": "{PROJECT_ID}".format(PROJECT_ID=PROJECT),
            "datastoreReadNamespace": "{entity}".format(entity=NAMESPACE),
            "textWritePrefix": "gs://{bucket}/{OUTPUT}/data".format(bucket=BUCKET, OUTPUT=location)
        },
        "environment": {
            "tempLocation": "gs://{bucket}/temp".format(bucket=BUCKET),
            "zone": "us-central1-f"
        }
    }

    r = service.projects().templates().launch(projectId=PROJECT, gcsPath=GCSPATH, body=BODY)
    response = r.execute()

    print(response)
    return response


def pubsub_to_gcs(topic, location):
    credentials = GoogleCredentials.get_application_default()
    service = build('dataflow', 'v1b3', credentials=credentials)

    # Set the following variables to your values.
    JOBNAME = 'pubsub-to-gcs'
    PROJECT = 'data-streamwise'
    BUCKET = 'streamwise'
    TEMPLATE = 'PubSub_to_GCS.json'

    GCSPATH = "gs://{bucket}/templates/{template}".format(bucket=BUCKET, template=TEMPLATE)
    BODY = {
        "jobName": "{jobname}".format(jobname=JOBNAME),
        "parameters": {
            "inputTopic": "projects/{PROJECT_ID}/topics/{TOPIC}".format(PROJECT_ID=PROJECT, TOPIC=topic),
            "outputDirectory": "gs://{BUCKET_ID}/{OUTPUT}/data".format(BUCKET_ID=BUCKET, OUTPUT=location),
            "outputFilenamePrefix": "output-",
            "outputFilenameSuffix": ".json"
        },
        "environment": {
            "tempLocation": "gs://{bucket}/temp".format(bucket=BUCKET),
            "zone": "us-central1-f"
        }
    }

    r = service.projects().templates().launch(projectId=PROJECT, gcsPath=GCSPATH, body=BODY)
    response = r.execute()

    print(response)
    return response


# [START gae_flex_pubsub_index]
@app.route('/', methods=['GET', 'POST'])
def index():
    data = query_sensors(app.config['SENSORS_TOKEN'])
    i = 0
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(
        current_app.config['PROJECT'],
        current_app.config['PUBSUB_TOPIC'])
    while i < len(data):

    # if request.method == 'GET':
    #     return render_template('index.html', messages=MESSAGES)
    #
    # data = request.form.get('payload', 'Example payload').encode('utf-8')
    #     body = {'messages': data[i]}
        data[i]['id'] = str(uuid.uuid1())
        publisher.publish(topic_path, data=json.dumps(data[i]).encode('utf-8'))
        i += 1

    return 'OK', 200
# [END gae_flex_pubsub_index]


# [START Collector]
@app.route('/tasks/sensor', methods=['GET'])
def send_to_queue():
    # project = current_app.config['PROJECT_ID']

    # Create a queue specifically for processing books and pass in the
    # Flask application context. This ensures that tasks will have access
    # to any extensions / configuration specified to the app, such as
    # models.
    data = query_sensors(current_app.config['SENSORS_TOKEN'])
    i = 0
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(
        current_app.config['PROJECT'],
        current_app.config['PUBSUB_TOPIC'])
    while i < len(data):
        # if request.method == 'GET':
        #     return render_template('index.html', messages=MESSAGES)
        #
        # data = request.form.get('payload', 'Example payload').encode('utf-8')
        #     body = {'messages': data[i]}
        data[i]['id'] = str(uuid.uuid1())
        publisher.publish(topic_path, data=json.dumps(data[i]).encode('utf-8'))
        i += 1

    return 'OK', 200
# [END send_to_queue]


# [START Batch Collector]
@app.route('/tasks/historical', methods=['GET'])
def send_to_historical_queue():
    # project = current_app.config['PROJECT_ID']

    # Create a queue specifically for processing books and pass in the
    # Flask application context. This ensures that tasks will have access
    # to any extensions / configuration specified to the app, such as
    # models.
    data = historical_job(current_app.config['SENSORS_TOKEN'])
    i = 0
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(
        current_app.config['PROJECT'],
        current_app.config['PUBSUB_HISTORICAL_TOPIC'])
    while i < len(data):
        # if request.method == 'GET':
        #     return render_template('index.html', messages=MESSAGES)
        #
        # data = request.form.get('payload', 'Example payload').encode('utf-8')
        #     body = {'messages': data[i]}

        # data[i]['id'] = str(uuid.uuid1())
        data[i].pop('nw_location')
        data[i].pop('se_location')
        publisher.publish(topic_path, data=json.dumps(data[i]).encode('utf-8'))
        i += 1
    print('{} messages processed in batch'.format(str(i)))

    return 'OK', 200
# [END send_to_queue]


# [START Download of Datastore Data]
@app.route('/tasks/queue_to_gcs', methods=['GET'])
def queue_to_gcs():
    print('data download from cloud datastore started at {}'.format(str(datetime.utcnow())))
    dataflow_resp = pubsub_to_gcs('historical', 'historical')
    print('data download from cloud datastore completed at {}'.format(str(datetime.utcnow())))
    return json.dumps(dataflow_resp), 200




# [START Download of Datastore Data]
@app.route('/tasks/download_to_gcs', methods=['GET'])
def download_to_gcs():
    print('data download from cloud datastore started at {}'.format(str(datetime.utcnow())))
    dataflow_resp = datastore_to_gcs('default', 'daily_traffic', 'stream')
    print('data download from cloud datastore completed at {}'.format(str(datetime.utcnow())))
    return json.dumps(dataflow_resp), 200

# [END Download of Datastore Data]




# [END Download of Datastore Data]

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
