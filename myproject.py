#!flask/bin/python
from app import app
import os
basedir = os.path.abspath(os.path.dirname(__file__))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, ssl_context=(os.path.join(basedir+'\certs','localhost.crt'), os.path.join(basedir+'\certs','localhost.key')))
