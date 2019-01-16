import logging
import json
from flask import current_app
from google.cloud import pubsub_v1
import requests

# [START query_data_from_sensors_across_the_city]
def query_sensors(token):
    """
    Queries the Google Books API to find detailed information about the book
    with the given title.
    """
    r = requests.get(' https://data.cityofchicago.org/resource/m65n-ux8y.json', headers={
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

        publisher.publish(topic_path, data=json.dumps(data[i]).encode('utf-8'))
        i += 1

    return 'OK', 200
# [END send_to_queue]


# [START query_historical data]
def batch_job(token):
    """
    Queries the Google Books API to find detailed information about the book
    with the given title.
    """
    r = requests.get('https://data.cityofchicago.org/resource/kf7e-cur8.json?$where=time between "2017-01-01T12:00:00" and "2018-10-11T14:00:00"', headers={
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

# [Write to BigQuery]
def write_to_bigquery():
    body = {
        'jobName': 'street-flow',
        'parameters': {
            'topic': 'projects/roadwise-2/topics/street-sensors',
            'table': 'roadwise-2:street_traffic.daily_traffic_10mins'
        },
        'environment': {
            'tempLocation': 'gs://roadwise-2.appspot.com/tmp_data_flow',
            'zone': 'us-east1-f'
        }
    }

    url = 'https://dataflow.googleapis.com/v1b3/projects/roadwise-2/templates:launch'

    headers = {
        'Content-Type': "application/json",
    }

    response = requests.request("POST", url, data=json.dumps(body), headers=headers)

    return response.status_code


# # [START DataFlow]
# @app.route('/tasks/dataflow', methods=['GET'])
# def write_to_bigquery():
#     body = {
#         'jobName': 'street-flow',
#         'parameters': {
#             'topic': 'projects/roadwise-2/topics/street-sensors',
#             'table': 'roadwise-2:street_traffic.daily_traffic_10mins'
#         },
#         'environment': {
#             'tempLocation': 'gs://roadwise-2.appspot.com/tmp_data_flow',
#             'zone': 'us-east1-f'
#         }
#     }
#     url = 'https://dataflow.googleapis.com/v1b3/projects/streetwise-2/templates:launch'
#     headers = {
#         'Content-Type': "application/json",
#     }
#     response = requests.request("POST", url, data=json.dumps(body), headers=headers)
#
#     return response.status_code
# # [End DataFlow]
#
#
# # [START gae_flex_pubsub_push]
# @app.route('/pubsub/push', methods=['POST'])
# def pubsub_push():
#     if (request.args.get('token', '') !=
#             current_app.config['PUBSUB_VERIFICATION_TOKEN']):
#         return 'Invalid request', 400
#
#     envelope = json.loads(request.data.decode('utf-8'))
#     payload = base64.b64decode(envelope['message']['data'])
#
#     MESSAGES.append(payload)
#
#     # Returning any 2xx status indicates successful receipt of the message.
#     return 'OK', 200
# # [END gae_flex_pubsub_push]


