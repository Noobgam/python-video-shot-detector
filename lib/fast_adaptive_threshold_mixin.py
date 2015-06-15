# -*- coding: utf8 -*-

from __future__ import absolute_import

import numpy as np
import logging

class FastAdaptiveThresholdMixin(object):

    __logger = logging.getLogger(__name__)

    def handle_difference(self, value, video_state, sigma_num = 3,
                          window_size = 200, window_limit = 50,
                          *args, **kwargs):

        if(not video_state.frame_counter):
            video_state.frame_counter = 0

        win_counter = video_state.frame_counter
        if(window_size):
            win_counter = win_counter % window_size

        video_state.frame_counter += 1

        video_state.value_mean = value
        video_state.value_max = value
        video_state.value_min = value

        if(win_counter):
            video_state.value_mean = \
                (value + video_state.value_mean * (win_counter - 1)) \
                / win_counter

            if(value > video_state.value_max):
                video_state.value_max = value
            if(value < video_state.value_min):
                video_state.value_min = value

        thresold_max =  video_state.value_mean + \
                        (video_state.value_max - video_state.value_min)/2

        if(not window_limit):
            window_limit = 1

        if (value > thresold_max) and (win_counter > window_limit):
            self.__logger.debug("%s sec = %s value = %s,  %s [%s]"%(
                video_state.curr.time.time(),
                video_state.curr.time,
                value,
                thresold_max,
                video_state.frame_counter
            ))

            video_state.cut_list += [video_state.curr]
            video_state.cut_counter += 1
            video_state.frame_counter = 0

        return video_state

