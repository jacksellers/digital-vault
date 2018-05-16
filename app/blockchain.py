import bitcoin.rpc
import socket
import json


def get_from_electrum(method, params=[]):
    params = [params] if type(params) is not list else params
    s = socket.create_connection(('54.169.18.143', 50001))
    s.send(json.dumps({'id': 0, 'method': method, 'params': params}).encode() + b'\n')
    return json.loads(s.recv(99999)[:-1].decode())

x = get_from_electrum('blockchain.address.get_balance', 'msT1xh5vQ6ZsT3XhdNXFJ4XvEzmvwVfNMS')
print(x)