from app import app, db
from app.model import User, Todo

@app.shell_context_processor
def make_shell_context():
    return {
        'db' : db,
        'User' : User,
        'Todo' : Todo
    }