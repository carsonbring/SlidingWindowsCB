from SlidingWindow import SlidingWindow

class NDVI(SlidingWindow):

    def __init__(self, x_max, y_max):
        SlidingWindow.__init__(self, x_max, y_max)

