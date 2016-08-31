import threading
import time
import logging
import util
import os


class S3Archiver(threading.Thread):
    """A threaded object to archive files to S3"""

    def __init__(self,
                 bucket,
                 log_level=logging.INFO):
        threading.Thread.__init__(self)
        self.finish = False
        self.daemon = True
        self.bucket = bucket
        self.logger = util.set_logger(level=log_level)
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
                self.logger.debug('S3Archiver processing %s file(s)' % len(self.files))
                for f in self.files:
                    self.logger.info('S3Archiver processing file %s' % f)
                    util.move_to_s3(f, self.bucket, os.path.basename(f))
            time.sleep(60)
