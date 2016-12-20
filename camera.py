import threading
import time
import picamera
import util
import datetime
import sys


class Camera(threading.Thread):
    """A threaded camera object"""

    def __init__(self,
                 base_filename="output",
                 horizontal_resolution=640,
                 vertical_resolution=480,
                 rotation=0,
                 image_format='png',
                 path="/tmp"):
        threading.Thread.__init__(self)
        self.daemon = True
        self.finish = False
        self.path = path
        self.camera = picamera.PiCamera()
        self.camera.resolution = (horizontal_resolution, vertical_resolution)
        self.camera.rotation = rotation
        self.base_filename = base_filename
        self.snapping = False
        self.image_format = image_format
        self.filename = None

    def _generate_image_filename(self):
        return "/".join((self.path,
                         "{}_{}.{}".format(datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'),
                                           self.base_filename,
                                           self.image_format)
                         ))

    def start_snapping(self):
        self.snapping = True

    def stop_snapping(self):
        self.snapping = False

    def snapshot(self, filename=None, annotate_text=None):
        try:
            if filename is None:
                filename = self._generate_image_filename()
            if annotate_text is not None:
                self.camera.annotate_text = annotate_text
            else:
                self.camera.annotate_text = ''
            self.camera.capture(filename, use_video_port=False)
            return filename
        except Exception as ex:
            return None

    def run(self):
        while not self.finish:
            if self.snapping:
                self.filename = self.snapshot(annotate_text=util.now_string())
            time.sleep(.001)
