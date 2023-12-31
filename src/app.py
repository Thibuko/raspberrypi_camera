"""
This module defines a Flask application that provides a streaming video feed from a camera.

The application uses the Picamera2 library to interface with the camera. The video feed is
encoded as JPEG and streamed over HTTP.

The module defines a single route, '/camera', which returns the video feed.

Classes:
    StreamingOutput: A class representing a streaming output for the camera frames.

Functions:
    generate_video(): A generator function that yields the video frames as they become available.
    camera(): The route handler for the '/camera' route. It initializes the camera and starts the
    video stream.
"""

import io
from threading import Condition
from flask import Flask, Response

from picamera2 import picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput


app = Flask(__name__)

class StreamingOutput(io.BufferedIOBase):
    """A class representing a streaming output for the camera frames.

    Attributes:
        frame (bytes): The current frame captured by the camera.
        condition (threading.Condition): A condition variable for synchronization.
    """

    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        """Write method to update the current frame and notify waiting threads.

        Args:
            buf (bytes): The frame data to be written.
        """
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


def generate_video():
    """A generator function for the video streaming."""
    global cameraOutput

    while True:
        with cameraOutput.condition:
            cameraOutput.condition.wait()
            frame = cameraOutput.frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/camera')
def camera():
    """The camera route."""

    global picam2
    global cameraOutput

    # Initialize the camera
    if picam2 is None:
        picam2 = picamera2.Picamera2()
        picam2.configure(picam2.create_video_configuration(
            main={"size": (640, 480)}))

        cameraOutput = StreamingOutput()
        picam2.start_recording(JpegEncoder(), FileOutput(cameraOutput))

    return Response(generate_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    picam2 = None
    cameraOutput = None
    app.run(host='0.0.0.0', port=5000)