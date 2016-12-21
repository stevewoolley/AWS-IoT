import picamera
import argparse


class Camera:
    """A camera object"""

    def __init__(self,
                 filename='snapshot.png',
                 horizontal_resolution=640,
                 vertical_resolution=480,
                 rotation=0,
                 annotation=None,
                 image_format='png'):
        self.camera = picamera.PiCamera()
        self.camera.resolution = (horizontal_resolution, vertical_resolution)
        self.camera.rotation = rotation
        self.filename = filename
        self.annotation = annotation

    def snap(self, new_filename=None):
        if new_filename is not None:
            self.filename = new_filename
        try:
            if self.annotation is not None:
                self.camera.annotate_text = self.annotation
            self.camera.capture(self.filename, use_video_port=False)
            return True
        except Exception as ex:
            return False


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-x", "--horizontal_resolution", help="horizontal_resolution", type=int, default=640)
    parser.add_argument("-y", "--vertical_resolution", help="vertical resolution", type=int, default=480)
    parser.add_argument("-z", "--rotation", help="image rotation", type=int, default=0)
    parser.add_argument("-o", "--filename", help="Output Filename", default='snapshot.png')
    args = parser.parse_args()

    Camera(rotation=args.rotation, horizontal_resolution=args.horizontal_resolution, vertical_resolution=args.vertical_resolution).snap(args.filename)
