#!/usr/bin/python3.8
import os
from flask import Flask, request, Response, render_template
import server.webserver.controllers as c

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video-feed', methods=["GET", "POST"])
def video_feed():
    return Response(c._video_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video-stop', methods=["GET", "POST"])
def video_stop():
    return c._video_stop()

@app.route('/video-reset', methods=["GET", "POST"])
def video_reset():
    return c._video_reset()

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', '*')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

def __stop():
    c.__stop_all()

def run():
    try:
        if "enviroment" in os.environ and os.environ.get("enviroment") == "production":
            from waitress import serve
            serve(app, host="0.0.0.0", port="5000")
        else:
            app.run(host='0.0.0.0', port='5000', debug=True, threaded=True, use_reloader=False) 
    except SystemExit as e:
        print(e)
        __stop()
    except KeyboardInterrupt as e:
        print(e)
        __stop()
    except Exception as e:
        print(e)
        __stop()