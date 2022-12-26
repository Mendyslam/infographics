from flask import render_template

from app import app, db


@app.errorhandler(404)
def not_found_error(error):
    """
    404 error handler
    """
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    """
    Internal server error handler
    """
    db.session.rollback()
    return render_template('500.html'), 500
