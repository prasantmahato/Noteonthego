from flask import render_template
from app import app, db


# Not found error template
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


# Invoked after a database/Internal server error
@app.errorhandler(500)
def internal_error(error):
    ''' Database rollback, so that failed database sesssion
    could not interfere with any database accesses triggred.
    
    This resets the session to a clean state'''
    db.session.rollback()
    return render_template('500.html'), 500
