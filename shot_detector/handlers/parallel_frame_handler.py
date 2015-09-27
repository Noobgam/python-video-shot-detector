# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import logging

from shot_detector.utils.multiprocessing import SaveStateProcessPool


from shot_detector.utils.collections import Condenser


from .base_frame_handler import BaseFrameHandler

from .parallel_base_handler import ParallelBaseHandler


from multiprocessing import  Pool


def parallel_handle_image2(arg):
    self,features, frame, video_state = arg
    video_state = super(ParallelFameHandler, self).handle_extracted_frame_features(
        features, frame,
        video_state,
    )
    return video_state


class ParallelFameHandler(BaseFrameHandler, ParallelBaseHandler):

    __logger = logging.getLogger(__name__)

    def handle_extracted_frame_features(self, features, frame, video_state, process_pool=None, *args, **kwargs):
        if process_pool:
            process_pool.apply_async(
                func = self.handle_sequential_buffer,
                value = (features, frame),
                video_state = video_state,
                *args, **kwargs
            )

        return video_state

    def handle_sequential_buffer(self, ffeatures_rame, *args, **kwargs):
        features, frame = ffeatures_rame
        video_state = kwargs.pop('video_state')
        prev_result = kwargs.pop('prev_result')
        if prev_result:
            video_state = prev_result
        video_state = super(ParallelFameHandler, self).handle_extracted_frame_features(
            features,
            frame,
            video_state,
        )
        return video_state