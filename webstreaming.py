# USAGE
# python webstreaming.py --ip 0.0.0.0 --port 8000

# import the necessary packages
#from pyimagesearch.motion_detection import SingleMotionDetector
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse
#import datetime
import imutils
import time
import cv2

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful for multiple browsers/tabs
# are viewing tthe stream)
outputFrame = None
lock = threading.Lock()

# initialize a flask object
app = Flask(__name__)

# initialize the video stream and allow the camera sensor to
# warmup
#vs = VideoStream(usePiCamera=1).start()
vs = VideoStream(src=0).start()
time.sleep(2.0)

@app.route("/index")
def index():
  # return the rendered template
  return render_template("index.html")

def generate():
  global outputFrame, lock

  
  # loop over frames from the output stream
  while True:
    outputFrame = vs.read()
    outputFrame = imutils.resize(outputFrame, width=400)
    (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

    # ensure the frame was successfully encoded
    if not flag:
      continue

    # yield the output frame in the byte format
    yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
      bytearray(encodedImage) + b'\r\n')


@app.route("/")
def video_feed():
  # return the response generated along with the specific media
  # type (mime type)
  return Response(generate(),
    mimetype = "multipart/x-mixed-replace; boundary=frame")

# check to see if this is the main thread of execution
if __name__ == '__main__':
  # construct the argument parser and parse command line arguments
  ap = argparse.ArgumentParser()
  ap.add_argument("-i", "--ip", type=str, required=True,
    help="ip address of the device")
  ap.add_argument("-o", "--port", type=int, required=True,
    help="ephemeral port number of the server (1024 to 65535)")
  ap.add_argument("-f", "--frame-count", type=int, default=32,
    help="# of frames used to construct the background model")
  args = vars(ap.parse_args())


  # start the flask app
  app.run(host=args["ip"], port=args["port"], debug=True,
    threaded=True, use_reloader=False)

# release the video stream pointer
vs.stop()
