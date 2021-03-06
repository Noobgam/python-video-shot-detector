# -*- coding: utf8 -*-
"""
    This is part of shot detector.
    Produced by w495 at 2017.05.04 04:18:27
"""

from __future__ import absolute_import

from .base_video_unit import BaseVideoUnit
from .frame_position import FramePosition
from .time import (
    StreamTime,
    ClockTime,
    VideoTime
)


class BaseFrame(BaseVideoUnit):
    """
        Abstract structure, a point in a timeline,
        that can represent some video event or some part of this event.
        Event is a significant point in a timeline.
        The main idea can be represented in scheme:
            [video] => [frames] => [points] => [events]
        OR:
            [video] -> 
                \{extract frames} 
                ->  [raw frames] -> 
                    \{select frames} 
                    -> [some of frames] -> 
                       \{extract frame_number} 
                        ->  [raw points] -> 
                            \{select points} 
                            ->  [some of points] ->
                                \{filter frame_number}
                                ->  [filtered points] -> 
                                    \{extract events}
                                    -> [events]
                                        \{select events} 
                    -                   > [some of events].
    """

    __slots__ = [
        'av_frame',
        'position',
        'time',
    ]

    def __init__(self,
                 av_frame=None,
                 position=None,
                 **kwargs):
        """
        
        :param av_frame: 
        :param FramePosition position: 
        """

        self.av_frame = av_frame

        self.position = position

        self.time = VideoTime(
            stream_time=StreamTime(
                time=self.av_frame.time,
                time_base=self.av_frame.time_base,
                pts=self.av_frame.pts,
                dts=self.av_frame.dts,
            ),
            clock_time=ClockTime()
        )

        super(BaseFrame, self).__init__(**kwargs)

    def reformat(self, **kwargs):
        """
        
        :return: 
        """

        reformatted = self.av_frame.reformat(**kwargs)
        return reformatted

    def to_nd_array(self):
        """

        :return: 
        """

        return self.av_frame.to_nd_array()

    @classmethod
    def av_frame_seq(cls, frame_seq):
        """

        :param frame_seq: 
        :return: 
        """
        for frame in frame_seq:
            yield frame.av_frame
