import threading
import time
import util
import os


class S3Archiver(threading.Thread):
    """A threaded object to archive files to S3"""

    def __init__(self, bucket):
        threading.Thread.__init__(self)
        self.finish = False
        self.daemon = True
        self.bucket = bucket
        self.files = []

    def add_file(self, f):
        self.files.append(f)

    def empty(self):
        if self.files > 0:
            return False
        return True

    def run(self):
        while not self.finish:
            if not self.empty():
                stragglers = []
                for f in self.files:
                    if util.is_locked(f):
                        stragglers.append(f)
                    else:
                        util.move_to_s3(f, self.bucket, os.path.basename(f))
                self.files = stragglers
            time.sleep(60)
