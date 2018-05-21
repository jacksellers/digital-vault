import requests
import socket
import json


def get_from_bitcoind(method, params=[]):
    """response = get_from_bitcoind('getreceivedbyaddress',
                                    'msT1xh5vQ6ZsT3XhdNXFJ4XvEzmvwVfNMS')"""
    url = 'http://alice:default@54.169.18.143:18332/'
    headers = {'content-type': 'application/json'}
    payload = {
        'method': method,
        'params': params,
        'jsonrpc': '2.0',
        'id': 0,
    }
    response = requests.post(
        url, data=json.dumps(payload), headers=headers).json()
    if response['error'] is None:
        return response['result']
    else:
        return response['error']


def get_from_electrum(method, params=[]):
    """response = get_from_electrum('blockchain.address.get_balance',
                                    'msT1xh5vQ6ZsT3XhdNXFJ4XvEzmvwVfNMS')"""
    params = [params] if type(params) is not list else params
    s = socket.create_connection(('54.169.18.143', 50001))
    s.send(json.dumps({'id': 0, 'method': method,
                       'params': params}).encode() + b'\n')
    response = json.loads(s.recv(99999)[:-1].decode())
    return response


# def get_blocks(hash):
