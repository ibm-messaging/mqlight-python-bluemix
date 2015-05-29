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

SUBSCRIBE_TOPIC = 'mqlight/sample/words'
PUBLISH_TOPIC = 'mqlight/sample/wordsuppercase'
SHARE_ID = 'python-back-end'
CLIENT_ID = 'python_backend_' + str(uuid.uuid4()).replace('-', '_')[0:7]

if os.environ.get('VCAP_SERVICES'):
    vcap_services = os.environ.get('VCAP_SERVICES')
    decoded = json.loads(vcap_services)['mqlight'][0]

    service = str(decoded['credentials']['nonTLSConnectionLookupURI'])
    username = str(decoded['credentials']['username'])
    password = str(decoded['credentials']['password'])
    security_options = {
        'property_user': username,
        'property_password': password
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
