from app.models import User, Balance, Trade, Transfer
from app import app, db


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Balance': Balance, 'Trade': Trade,
            'Transfer': Transfer}
