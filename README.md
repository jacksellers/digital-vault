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
#### Running the app:
```
export FLASK_APP=app.py FLASK_DEBUG=1
flask run --host=0.0.0.0
```