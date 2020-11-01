#!/usr/bin/python3.8
from flask import Flask, request, Response, render_template
import server.controllers as c

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ms-sudo-cam/api/v1/video-feed/<int:type_cam>', methods=["GET", "POST"])
def video_feed(type_cam):
    return Response(c._video_feed(type_cam), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/ms-sudo-cam/api/v1/video-stop', methods=["GET", "POST"])
def video_stop():
    return c._video_stop()

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', '*')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response
