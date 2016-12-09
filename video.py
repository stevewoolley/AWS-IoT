import threading
import time
import picamera
import logging
import util


class Video(threading.Thread):
    """A threaded video object"""

    def __init__(self,
                 base_filename="output",
                 video_format='h264',
                 horizontal_resolution=640,
                 vertical_resolution=480,
                 rotation=0,
                 path="/tmp",
                 max_recording_seconds=10.0,
                 log_level=logging.INFO
                 ):
        threading.Thread.__init__(self)
        self.daemon = True
        self.finish = False
        self.path = path
        self.camera = picamera.PiCamera()
        self.camera.resolution = (horizontal_resolution, vertical_resolution)
        self.camera.rotation = rotation
        self.base_filename = base_filename
        self.recording = False
        self.video_format = video_format
        self.filename = None
        self.st_recording = None
        self.max_recording_seconds = max_recording_seconds
        # set logger
        self.logger = util.set_logger(level=log_level)

    def start_recording(self):
        if not self.recording:
            try:
                self.filename = util.full_path(self.path,
                                               util.file_name(self.video_format, util.now_string().replace(" ", "_"),
                                                              self.base_filename))
                self.camera.start_recording(self.filename, format=self.video_format)
                self.recording = True
                self.st_recording = time.time()
            except Exception as ex:
                self.logger.debug('ERROR start_recording {}'.format(ex.message))
                self.filename = None
                self.recording = False
                self.st_recording = None
        else:
            if self.st_recording is not None:
                self.st_recording = time.time()
        return self.recording

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.st_recording = None
            self.camera.stop_recording()
            return self.filename
        else:
            return None

    def snapshot(self, snapshot_filename=None, annotate_text=None):
        try:
            if snapshot_filename is None:
                snapshot_filename = util.full_path(self.path,
                                                   util.file_name('png', util.now_string().replace(" ", "_"),
                                                                  self.base_filename))
            if annotate_text is not None:
                self.camera.annotate_text = annotate_text
            if self.recording:
                self.camera.capture(snapshot_filename, use_video_port=True)
            else:
                self.camera.capture(snapshot_filename, use_video_port=False)
            return snapshot_filename
        except Exception as ex:
            self.logger.debug('ERROR snapshot {} {}'.format(snapshot_filename, ex.message))
            return None

    def run(self):
        while not self.finish:
            if self.recording:
                if self.st_recording is not None:
                    if time.time() - self.st_recording > self.max_recording_seconds:
                        self.stop_recording()
            time.sleep(.001)
