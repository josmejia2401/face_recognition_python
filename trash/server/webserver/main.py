from flask import Flask, render_template, Response
import os
from server.webserver.api import app

def run():
    if "enviroment" in os.environ and os.environ.get("enviroment") == "production":
        from waitress import serve
        serve(app, host="0.0.0.0", port="5000")
    else:
        app.run(host='0.0.0.0', port='5000', debug=True, threaded=True, use_reloader=False)