# Digital Vault
## A Bitcoin custody platform
### Dependencies:
- [Python 3](https://www.python.org/)
- [Pip](https://pypi.org/project/pip/)
- [Flask](http://flask.pocoo.org/)
#### Installation:
```
git clone https://github.com/jackwsellers/digital-vault.git
cd digital-vault
pip3 install flask_sqlalchemy, flask_login, flask_migrate, flask_sslify, flask_excel, wtforms, flask_wtf
```
#### Running the app without HTTPS:
```
export FLASK_APP=app.py FLASK_DEBUG=1
flask run --host=0.0.0.0
```

#### Running the app with HTTPS:
pip install pyopenssl
python myproject.py

#### To create the key and certs
Go to https://ssl.indexnl.com/ and click "get me certificate" button.  (Free and Easy SSL certificates for Developers)
Put the certificates in the folder called as "certs" in the root directory of POC.
Go to https://ssl.indexnl.com/windows-root-ca/ and follow the instructions to install a CA Root Certificate.

