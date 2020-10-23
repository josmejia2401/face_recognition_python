from flask import Flask, render_template, Response
from core.camera import Camera

app = Flask(__name__)

_camera = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    _camera = Camera()
    _camera.release()
    _camera.initialize()
    return Response(_camera.generated_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_stop')
def video_stop():
    _camera.release()
    return "ok"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True, threaded=True, use_reloader=False)