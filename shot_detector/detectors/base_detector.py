# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import six
import logging

import av
from av.video.frame import VideoFrame
from av.video.stream import VideoStream
from av.audio.stream import AudioStream

from shot_detector.objects          import SmartDict, BaseVideoState, Second
from shot_detector.utils.common     import get_objdata_dict
from shot_detector.utils.log_meta   import LogMeta

class BaseDetector(six.with_metaclass(LogMeta, SmartDict)):

    __logger = logging.getLogger(__name__)

    def detect(self, video_file_name, video_state = None, *args, **kwargs):
        video_state = self.handle_video(video_file_name, video_state, *args, **kwargs)
        return video_state

    def handle_video(self, video_file_name, video_state = None, *args, **kwargs):
        video_state = self.init_video_state(video_state, *args, **kwargs)
        video_container = av.open(video_file_name)
        logger = self.__logger
        if (logger.isEnabledFor(logging.INFO)):
            logger.debug("%s"%(video_container))
            self.log_tree(
                logger,
                get_objdata_dict(
                    video_container,
                    ext_classes_keys = ['format', 'layout']
                )
            )
        video_state = self.handle_video_container(video_container, video_state, *args, **kwargs)
        return video_state

    def log_tree(self, logger, value, level = 1, *args, **kwargs):
        space = ' ⇾ ' * level
        for key, value in six.iteritems(value):
            if isinstance(value, dict):
                xtype = value.get('type')
                if(xtype):
                    key += " [%s]"%str(xtype)
                name = value.get('name')
                if(name):
                    key += " {%s} "%str(name)
                long_name = value.get('long_name')
                if(long_name):
                    key += " «%s»"%str(long_name)
                logger.debug("%s %s:"%(space, key))
                self.log_tree(logger, value, level = level + 1)
            else:
                logger.debug("%s %s: %s"%(space, key, value))

    def handle_video_container(self, video_container, video_state = None, *args, **kwargs):
        packet_list = video_container.demux()
        video_state = self.handle_packet_list(packet_list, video_state, *args, **kwargs)
        return video_state

    def handle_packet_list(self, packet_list, video_state = None, *args, **kwargs):
        for packet in packet_list:
            video_state = self.handle_packet(packet, video_state, *args, **kwargs)
        return video_state

    def handle_packet(self, packet, video_state = None, *args, **kwargs):
        frame_list = packet.decode()
        for frame in frame_list:
            video_state = self.handle_frame(frame, video_state, *args, **kwargs)
        return video_state

    def handle_frame(self, frame, video_state = None, *args, **kwargs):
        if(type(frame) == VideoFrame):
            video_state = self.handle_videoframe(frame, video_state, *args, **kwargs)
        return video_state

    def handle_videoframe(self, frame, video_state = None, *args, **kwargs):
        video_state.prev.features = video_state.curr.features
        video_state.curr.features, video_state = self.extract_features(frame, video_state, *args, **kwargs)
        video_state.prev.time = video_state.curr.time
        video_state.curr.time = Second(frame.time)
        video_state = self.select_transition(video_state, *args, **kwargs)
        return video_state

    def init_video_state(self, video_state = None, *args, **kwargs):
        if video_state:
            return self.build_video_state(**video_state)
        return self.build_video_state(
            options = SmartDict(*args, **kwargs)
        )

    def build_video_state(self, *args, **kwargs):
        return BaseVideoState(
            detector_options = self,
            *args, **kwargs
        )

    def extract_features(self, frame, video_state = None, *args, **kwargs):
        '''
            Should be implemented
        '''
        features = None
        return features, video_state

    def select_transition(self, video_state = None, *args, **kwargs):
        '''
            Should be implemented
        '''
        return video_state

