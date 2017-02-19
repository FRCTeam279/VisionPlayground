from networktables import NetworkTables
from pipeline import ContourPipeline
from picamera.array import PiRGBArray
from picamera import PiCamera
import picamera
from PIL import Image as PImage
from datetime import datetime
from datetime import timedelta
import numpy as np
import cv2
import sys
import math
import io
import os
import shutil
from subprocess import Popen, PIPE
from string import Template
from struct import Struct
from threading import Thread
from time import sleep, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from wsgiref.simple_server import make_server
from ws4py.websocket import WebSocket
from ws4py.server.wsgirefserver import WSGIServer, WebSocketWSGIRequestHandler
from ws4py.server.wsgiutils import WebSocketWSGIApplication

NetworkTables.initialize(server='10.2.79.2')
print('Waiting to connect...')
while NetworkTables.isConnected() is False:
    time.sleep(0.1)

nt = NetworkTables.getTable("Gear")
imageWidth = 1640

###########################################
# CONFIGURATION
WIDTH = 1640
HEIGHT = 1232
FRAMERATE = 20
HTTP_PORT = 8082
WS_PORT = 8084
COLOR = u'#444'
BGCOLOR = u'#333'
JSMPEG_MAGIC = b'jsmp'
JSMPEG_HEADER = Struct('>4sHH')
###########################################


class StreamingHttpHandler(BaseHTTPRequestHandler):

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
            return
        elif self.path == '/jsmpg.js':
            content_type = 'application/javascript'
            content = self.server.jsmpg_content
        elif self.path == '/index.html':
            content_type = 'text/html; charset=utf-8'
            tpl = Template(self.server.index_template)
            content = tpl.safe_substitute(dict(
                ADDRESS='%s:%d' % (self.request.getsockname()[0], WS_PORT),
                WIDTH=WIDTH, HEIGHT=HEIGHT, COLOR=COLOR, BGCOLOR=BGCOLOR))
        else:
            self.send_error(404, 'File not found')
            return
        content = content.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', len(content))
        self.send_header('Last-Modified', self.date_time_string(time()))
        self.end_headers()
        if self.command == 'GET':
            self.wfile.write(content)


class StreamingHttpServer(HTTPServer):
    def __init__(self):
        super(StreamingHttpServer, self).__init__(
                ('', HTTP_PORT), StreamingHttpHandler)
        with io.open('index.html', 'r') as f:
            self.index_template = f.read()
        with io.open('jsmpg.js', 'r') as f:
            self.jsmpg_content = f.read()


class StreamingWebSocket(WebSocket):
    def opened(self):
        self.send(JSMPEG_HEADER.pack(JSMPEG_MAGIC, WIDTH, HEIGHT), binary=True)


class BroadcastOutput(object):
    def __init__(self, camera):
        print('Spawning background conversion process')
        self.converter = Popen([
            'avconv',
            '-f', 'rawvideo',
            '-pix_fmt', 'yuv420p',
            '-s', '%dx%d' % camera.resolution,
            '-r', str(float(camera.framerate)),
            '-i', '-',
            '-f', 'mpeg1video',
            '-b', '800k',
            '-r', str(float(camera.framerate)),
            '-'],
            stdin=PIPE, stdout=PIPE, stderr=io.open(os.devnull, 'wb'),
            shell=False, close_fds=True)

    def write(self, b):
        self.converter.stdin.write(b)

    def flush(self):
        print('Waiting for background conversion process to exit')
        self.converter.stdin.close()
        self.converter.wait()


class BroadcastThread(Thread):
    def __init__(self, converter, websocket_server):
        super(BroadcastThread, self).__init__()
        self.converter = converter
        self.websocket_server = websocket_server

    def run(self):
        try:
            while True:
                buf = self.converter.stdout.read(512)
                if buf:
                    self.websocket_server.manager.broadcast(buf, binary=True)
                elif self.converter.poll() is not None:
                    break
        finally:
            self.converter.stdout.close()


def getDFromW(width):
    return 7362.30054*(math.pow(float(width), -1.186536))


def getDFromH(height):
    return 9963.977172*(math.pow(float(height), -1.072971))


def getDFromWt(widthTotal):
    return 5745.771277*(math.pow(float(widthTotal), -0.895025))


start_time = datetime.now()


def millis():
    dt = datetime.now() - start_time
    ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
    return ms


vis = ContourPipeline()
camera = PiCamera()
lastTime = -1


def currentMillis():
    return int(round(time.time() * 1000))


def main():
    print('Initializing camera')
    with picamera.PiCamera() as camera:
        camera.resolution = (WIDTH, HEIGHT)
        camera.framerate = FRAMERATE
        sleep(1)  # camera warm-up time
        print('Initializing websockets server on port %d' % WS_PORT)
        websocket_server = make_server(
            '', WS_PORT,
            server_class=WSGIServer,
            handler_class=WebSocketWSGIRequestHandler,
            app=WebSocketWSGIApplication(handler_cls=StreamingWebSocket))
        websocket_server.initialize_websockets_manager()
        websocket_thread = Thread(target=websocket_server.serve_forever)
        print('Initializing HTTP server on port %d' % HTTP_PORT)
        http_server = StreamingHttpServer()
        http_thread = Thread(target=http_server.serve_forever)
        print('Initializing broadcast thread')
        output = BroadcastOutput(camera)
        broadcast_thread = BroadcastThread(output.converter, websocket_server)
        print('Starting recording')
        camera.start_recording(output, 'yuv')
        try:
            print('Starting websockets thread')
            websocket_thread.start()
            print('Starting HTTP server thread')
            http_thread.start()
            print('Starting broadcast thread')
            broadcast_thread.start()
            while True:
                res = []
                imgArray = PiRGBArray(camera, size=(1640, 1232))
                camera.capture(imgArray, format="bgr", use_video_port=True)
                img = imgArray.array

                contours = vis.process(img)

                rect1Exists = False
                rect2Exists = False

                if 1 < len(contours):
                    rect1 = cv2.boundingRect(contours[0])
                    rect2 = cv2.boundingRect(contours[1])
                    rectsExist = True
                else:
                    rectsExist = False

                if(rectsExist is True):
                    # declaring rectangle objects
                    class rectObj1:
                        # top left point
                        topLeftX = rect1[0]
                        pt1 = (rect1[0], rect1[1])
                        # bottom right point
                        bottomRightX = (rect1[0] + rect1[2])
                        pt2 = ((rect1[0] + rect1[2]), (rect1[1] + rect1[3]))
                        # width and height
                        w = rect1[2]
                        h = rect1[3]

                    class rectObj2:
                        # top left point
                        topLeftX = rect2[0]
                        pt1 = (rect2[0], rect2[1])
                        # bottom right point
                        bottomRightX = (rect2[0] + rect2[2])
                        pt2 = ((rect2[0] + rect2[2]), (rect2[1] + rect2[3]))
                        # width and height
                        w = rect2[2]
                        h = rect2[3]

                    if(rectObj1.pt1 < rectObj2.pt1):
                        leftRect = rectObj1
                        rightRect = rectObj2
                    else:
                        leftRect = rectObj2
                        rightRect = rectObj1

                    leftDist = getDFromW(leftRect.w)
                    rightDist = getDFromW(rightRect.w)
                    cv2.rectangle(img, leftRect.pt1, leftRect.pt2, (0, 255, 0), 2)
                    cv2.rectangle(img, rightRect.pt1, rightRect.pt2, (0, 255, 0), 2)
                    cv2.imwrite('output.png', img)
                    pixelOffset = (imageWidth/2)-((leftRect.topLeftX + rightRect.bottomRightX)/2)
                    if(rightDist > leftDist):
                        nearDist = leftDist
                        farDist = rightDist
                    elif(rightDist < leftDist):
                        nearDist = rightDist
                        farDist = leftDist
                    else:
                        middleDist = leftDist
                        nearDist = middleDist
                        farDist = middleDist

                    if(nearDist != farDist):
                        middleDist = (farDist + nearDist) / 2
                        angle = 0
                        try:
                            angle = math.degrees(math.acos((26.2656+math.pow(middleDist,2)-math.pow(farDist,2))/(2*5.125*middleDist)))
                        except:
                            print("error")
                        if leftDist < rightDist:
                            angle *= -1
                        lastTime = millis()
                        res[0] = nt.putValue("angle", angle)
                        res[1] = nt.putValue("distance", middleDist)
                        res[2] = nt.putValue("eyes", True)
                        res[3] = nt.putValue("lastTimeDetected", 0)
                        res[4] = nt.putValue("pixelOffset", pixelOffset)
                    else:
                        lastTime = millis()

                        res[0] = nt.putValue("angle", 0)
                        res[1] = nt.putValue("distance", middleDist)
                        res[2] = nt.putValue("eyes", True)
                        res[3] = nt.putValue("lastTimeDetected", 0)
                        res[4] = nt.putValue("pixelOffset", pixelOffset)
                else:
                    if lastTime == -1:
                        timeSinceLast = -1
                    else:
                        timeSinceLast = millis() - lastTime
                    res2 = nt.putValue("eyes", False)
                    res3 = nt.putValue("lastTimeDetected", timeSinceLast)
                for i in res:
                    if not res[i]:
                        print('Writing result #' + i + ' failed')
                camera.wait_recording(1)
        except KeyboardInterrupt:
            pass
        finally:
            print('Stopping recording')
            camera.stop_recording()
            print('Waiting for broadcast thread to finish')
            broadcast_thread.join()
            print('Shutting down HTTP server')
            http_server.shutdown()
            print('Shutting down websockets server')
            websocket_server.shutdown()
            print('Waiting for HTTP server thread to finish')
            http_thread.join()
            print('Waiting for websockets thread to finish')
            websocket_thread.join()


if __name__ == '__main__':
    main()
