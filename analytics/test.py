import googleapiclient.discovery
import os

PROJECT_ID = 'data-streamwise'
VERSION_NAME = 'staged'
MODEL_NAME = 'xgboost'

service = googleapiclient.discovery.build('ml', 'v1')
name = 'projects/{}/models/{}'.format(PROJECT_ID, MODEL_NAME)
name += '/versions/{}'.format(VERSION_NAME)

response = service.projects().predict(
    name=name,
    body={'instances': [[1, 0, 21, 22.4]]}
).execute()

if 'error' in response:
  print (response['error'])
else:
  online_results = response['predictions']
  # convert floats to booleans
  converted_responses = [x > 0.5 for x in online_results]
  # Print the first 10 responses
  for i, response in enumerate(converted_responses[:5]):
    print('Prediction: {}\tLabel: {}'.format(response, 1))
