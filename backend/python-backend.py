#Copyright (c) 2014 IBM Corporation.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
# IBM - initial implementation
import bottle
import os, json
import mqlight
import uuid

MQLIGHT_SERVICE_NAME = 'mqlight'
MESSAGEHUB_SERVICE_NAME = 'messagehub'
SUBSCRIBE_TOPIC = 'mqlight/sample/words'
PUBLISH_TOPIC = 'mqlight/sample/wordsuppercase'
SHARE_ID = 'python-back-end'
CLIENT_ID = 'python_backend_' + str(uuid.uuid4()).replace('-', '_')[0:7]

if os.environ.get('VCAP_SERVICES'):
    vcap_services = json.loads(os.environ.get('VCAP_SERVICES'))
    for vcap_service in vcap_services:
        if vcap_service.startswith(MQLIGHT_SERVICE_NAME):
            mqlight_service = vcap_services[vcap_service][0]
            service = str(mqlight_service['credentials']['nonTLSConnectionLookupURI'])
            security_options = {
                'property_user': str(mqlight_service['credentials']['username']),
                'property_password': str(mqlight_service['credentials']['password'])
            }
        elif vcap_service.startswith(MESSAGEHUB_SERVICE_NAME):
            messagehub_service = vcap_services[vcap_service][0]
            service = str(messagehub_service['credentials']['connectionLookupURI'])
            security_options = {
                'property_user': str(messagehub_service['credentials']['user']),
                'property_password': str(messagehub_service['credentials']['password'])
            }
else:
    service = 'amqp://127.0.0.1:5672'
    security_options = {}

def subscribe(err):
    client.subscribe(
        topic_pattern=SUBSCRIBE_TOPIC,
        share=SHARE_ID,
        on_message=process_message)

client = mqlight.Client(
    service=service,
    client_id=CLIENT_ID,
    security_options=security_options,
    on_started=subscribe)
def process_message(type, data, delivery):
    word = json.loads(data)['word']
    reply_data = {
        'word': word.upper(),
        'backend': 'Python: ' + CLIENT_ID
    }
    send_reply(json.dumps(reply_data))

def send_reply(message):
    client.send(PUBLISH_TOPIC, message)

@bottle.get('/')
def index():
    return 'python-backend: ' + client.get_id() + ' connected to ' + \
        client.get_service()

application = bottle.default_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', '8000'))
    bottle.run(host='0.0.0.0', port=port)
