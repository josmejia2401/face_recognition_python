from flask import Flask, render_template, Response
from core.camera import Camera

app = Flask(__name__)

camera = Camera()
camera.initialize()
cam = camera.get_cam()

@app.route('/')
def index():
    return render_template('index.html')

def gen(cam, camera):
    while cam.isOpened():
        ret, frame_jpeg, is_mov = camera.get_frame_streaming_mov()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_jpeg.tobytes() + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(cam, camera), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_stop')
def video_stop():
    cam.release()
    return "ok"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)