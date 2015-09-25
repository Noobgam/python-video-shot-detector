# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import logging

from shot_detector.objects import BasePointState, Second

from .base_handler import BaseHandler


class BaseFrameHandler(BaseHandler):
    """
        Works with video at frame level, 
        wraps every frame into internal structure (PointState).
        The main idea can be represented in scheme:
            [video] => [frames] => [points].
        OR:
            [video] => 
                \{extract frames} 
                =>  [raw frames] => 
                    \{select frames} 
                    => [some of frames] => 
                       \{extract features} 
                        =>  [points].
        
        If you want, you can skip some frames. 
        For this, you should implement `select_frame` method.
        Also, you should implement `handle_point` method.
    """

    __logger = logging.getLogger(__name__)

    def handle_frame(self, frame, video_state=None, *args, **kwargs):
        frame, video_state = self.select_frame(
            frame,
            video_state,
            *args,
            **kwargs
        )
        if frame is not None:
            video_state.triggers.frame_selected = True
            video_state = self.handle_selected_frame(
                frame,
                video_state,
                *args,
                **kwargs
            )
        else:
            video_state.triggers.frame_selected = False
        return video_state

    def handle_selected_frame(self, frame, video_state=None, *args, **kwargs):
        features, video_state = self.extract_features(
            frame.raw,
            video_state,
            *args,
            **kwargs
        )
        features, video_state = self.filter_frame_features(
            features,
            video_state,
            *args,
            **kwargs
        )

        raw_point = self.build_point_state(
            features=features,
            frame=frame,
            timestamp=Second(frame.time)
        )
        video_state = self.handle_point(
            raw_point,
            video_state,
            *args,
            **kwargs
        )
        return video_state

    def build_point_state(self, *args, **kwargs):
        point = BasePointState(*args, **kwargs)
        return point

    def extract_features(self, frame, video_state, *args, **kwargs):
        """
            Should be implemented
        """
        return None, video_state

    def filter_frame_features(self, features, video_state, *args, **kwargs):
        """
            Should be implemented
        """
        return features, video_state

    def select_frame(self, frame, video_state=None, *args, **kwargs):
        """
            Should be implemented
        """
        return frame, video_state

    def handle_point(self, point, video_state=None, *args, **kwargs):
        """
            Should be implemented
        """
        return video_state
