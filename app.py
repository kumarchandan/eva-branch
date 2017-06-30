''' api.ai requests and odata access services '''

import json
import requests

from flask import Flask, request as flask_request, make_response
from requests.auth import HTTPBasicAuth


APP = Flask(__name__)

@APP.route('/')
def home():
    ''' home '''
    return 'hey there!'

@APP.route('/webhook', methods=['POST'])
def webhook():
    ''' endpoint to receive all api ai requests '''
    req = flask_request.get_json()
    if req is None:
        return '<h3>Request object is empty</h3>'

    resp = process_request(req)
    res = json.dumps(resp)

    res = make_response(res)
    res.headers['Content-Type'] = 'application/json'
    return res

def process_request(req):
    '''
    Process requests from API.AI
    '''
    base_url = "https://my316075.sapbydesign.com/sap/byd/odata/cust/v1/purchasing/ \
    PurchaseOrderCollection/"
    query = make_query(req)
    query_url = base_url + query
    print('query url: {}'.format(query_url))

    try:
        res = requests.get(query_url, auth=HTTPBasicAuth('odata_demo', 'Welcome01'))
    except RuntimeError as odata_failed_exception:
        print('odata query failed! {}'.format(odata_failed_exception))

    result = res.text
    print('result: {}'.format(result))

    data = json.loads(result)
    res = make_webhook_results(data, req)
    return res

def make_query(req):
    '''
    Build query to access odata
    '''
    result = req.get('result')
    parameters = result.get('parameters')
    purchase_order_id = parameters.get('id')
    purchase_order_status = parameters.get('status')
    print('Purhcase Order ID {} and status {}'.format(purchase_order_id, purchase_order_status))

    action = result.get('action')

    if action == 'find-status':
        return '?%24filter=PurchaseOrderID%20{}&%24format=json'.format(purchase_order_id)
    elif action == 'find-count':
        return '$count?%24filter=PurchaseOrderLifeCycleStatusCodeText%20eq%20\'{}\''.format \
        (purchase_order_status)
    else:
        return {}

def make_webhook_results(data, req):
    action = req.get('result').get('action')
    if action == 'find-status':
        d = data.get('d')
        value = d.get('results')
        speech_text = 'The status of Purhcase Order ID {} is {}'.format(value[0] \
        .get('PurchaseOrderID'), value[0].get('PurchaseOrderLifeCycleStatusCodeText'))
    elif action == 'find-count':
        if int(data) > 1:
            speech_text = 'There are {} Purchase orders in the system with {} status' \
            .format(data, req.get("result").get("parameters").get("status"))
        elif int(data) == 1:
            speech_text = 'There is {} Purchase order in the system with {} status' \
            .format(data, req.get("result").get("parameters").get("status"))
        else:
            speech_text = 'There are no puchase order in the system with {} status' \
            .format(req.get("result").get("parameters").get("status"))
    else:
            speech_text = 'What kind of purchase order is this? I can\'t find it'
    
    return {
        'speech': speech_text,
        'displayText': speech_text,
        'source': 'byd-assistant'
    }

if __name__ == '__main__':
    app.run()
