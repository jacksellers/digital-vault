import requests
import socket
import json


def get_from_bitcoind(method, params=[]):
    """response = get_from_bitcoind('getreceivedbyaddress',
                                    'msT1xh5vQ6ZsT3XhdNXFJ4XvEzmvwVfNMS')"""
    url = 'http://alice:default@127.0.0.1:18332/'
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
    s = socket.create_connection(('206.189.29.167', 50001))
    s.send(json.dumps({'id': 0, 'method': method,
                       'params': params}).encode() + b'\n')
    response = json.loads(s.recv(99999)[:-1].decode())
    return response


def search_blockchain(search):
    try:
        # address ???
        data = get_from_bitcoind('getblock', [search])
        data['message']
        try:
            height_to_hash = get_from_bitcoind('getblockhash', [search])
            data = get_from_bitcoind('getblock', [height_to_hash])
            data['message']
            try:
                data = get_from_bitcoind('getrawtransaction', [search, 1])
                data['message']
                category = None
                search_id = None
            except KeyError:
                category = 'tx'
                search_id = search
        except KeyError:
            category = 'block'
            search_id = search
    except KeyError:
        category = 'block'
        search_id = data['height']
    print('category: ', category)
    print('search_id: ', search_id)
    print('data: ', data)
    return category, search_id, data


def get_raw_mempool():
    tx_ids = []
    raw_mempool = get_from_bitcoind('getrawmempool')
    for tx_id in raw_mempool:
        tx_ids.append({'tx_id': tx_id})
    return tx_ids
