# Copyright (c) 2014 IBM Corporation.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
# IBM - initial implementation
from __future__ import print_function
import threading
import bottle
import os
import json
import mqlight
import uuid

MQLIGHT_SERVICE_NAME = 'mqlight'
MESSAGEHUB_SERVICE_NAME = 'messagehub'
SUBSCRIBE_TOPIC = 'mqlight/sample/wordsuppercase'
PUBLISH_TOPIC = 'mqlight/sample/words'
SHARE_ID = 'python-front-end'
CLIENT_ID = 'python_frontend_' + str(uuid.uuid4()).replace('-', '_')[0:7]
LOCK = threading.RLock()

if os.environ.get('VCAP_SERVICES'):
    vcap_services = json.loads(os.environ.get('VCAP_SERVICES'))
    for vcap_service in vcap_services:
        if vcap_service.startswith(MQLIGHT_SERVICE_NAME):
            mqlight_service = vcap_services[vcap_service][0]
            service = str(mqlight_service['credentials']['nonTLSConnectionLookupURI'])
            security_options = {
                'user': str(mqlight_service['credentials']['username']),
                'password': str(mqlight_service['credentials']['password'])
            }
        elif vcap_service.startswith(MESSAGEHUB_SERVICE_NAME):
            messagehub_service = vcap_services[vcap_service][0]
            service = str(messagehub_service['credentials']['connectionLookupURI'])
            security_options = {
                'user': str(messagehub_service['credentials']['user']),
                'password': str(messagehub_service['credentials']['password'])
            }
else:
    service = 'amqp://127.0.0.1:5672'
    security_options = {}

recv_queue = []
send_queue = []


def subscribe(err):
    client.subscribe(
        topic_pattern=SUBSCRIBE_TOPIC,
        share=SHARE_ID,
        on_message=process_message)
    send_message()

client = mqlight.Client(
    service=service,
    client_id=CLIENT_ID,
    security_options=security_options,
    on_started=subscribe)


def send_message():
    with LOCK:
        if len(send_queue) > 0:
            message = send_queue.pop(0)
            client.send(message['topic'], message['message'])
        timer = threading.Timer(0.2, send_message)
        timer.start()


def process_message(message_type, data, delivery):
    if message_type == mqlight.MESSAGE:
        print('Received a message: {0}'.format(data))
        recv_queue.append({
            'data': data,
            'delivery': delivery
        })


@bottle.route('/images/<filename>')
def static_image(filename):
    return bottle.static_file(filename, root='static/images')


@bottle.route('/style.css')
def static_css():
    return bottle.static_file('style.css', root='static')


@bottle.get('/')
def index():
    return bottle.static_file('index.html', root='static')


@bottle.post('/rest/words')
def post_words():
    body = bottle.request.json

    # check they've sent { "words" : "some sentence" }
    if not 'words' in body:
        bottle.response.status = '500 No words'
        return bottle.response

    # split it up into words
    msg_count = 0
    for word in body['words'].split(' '):
        with LOCK:
            # send it as a message
            message = {
                'word': word,
                'frontend': 'Python: {0}'.format(client.get_id())
            }
            print('Sending response: {0}'.format(message))
            send_queue.append({
                'topic': PUBLISH_TOPIC,
                'message': json.dumps(message)
            })
            msg_count += 1
            # send back a count of messages sent
            response = bottle.Response(
                body=json.dumps({'msgCount': msg_count}))
    return response


@bottle.get('/rest/wordsuppercase')
def get_uppercase_words():
    # do we have a message held?
    if len(recv_queue) == 0:
        # just return no-data
        bottle.response.status = 204
        return bottle.response
    else:
        # send the data to the caller
        message = recv_queue.pop(0)
        response = bottle.Response(body=message['data'])
        response.content_type = 'application/json'
        return response

application = bottle.default_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', '8000'))
    bottle.run(host='0.0.0.0', port=port)
