# -*- coding: utf8 -*-

from __future__ import absolute_import

from .settings import start_logging

import sys
import time

from .lib.base_detector import BaseDetector

from .lib.base_vector_mixin import BaseVectorMixin



from .lib.rgb_colour_mixin import RgbColourMixin
from .lib.gray_colour_mixin import GrayColourMixin

from .lib.histogram_image_mixin import HistogramImageMixin
from .lib.sad_mixin import SadMixin
from .lib.zero_norm_mixin import ZeroNormMixin
from .lib.l2_norm_mixin import L2NormMixin


from .lib.threshold_mixin import ThresholdMixin


from .lib.normalize_mixin import NormalizeMixin




class SimpleDetector(ThresholdMixin, L2NormMixin, GrayColourMixin, BaseVectorMixin, BaseDetector):
    pass


import logging




if (__name__ == '__main__'):


    detector = SimpleDetector()

    ## Получаем имя видео-файла.
    #video_file_name = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FILE_NAME

    video_file_name  = './v.hi.und.mp4'


    t1 = time.time()

    detector.detect(video_file_name, thresold = 0.1)

    t2 = time.time()
    print t2 - t1
