# -*- coding: utf8 -*-
"""
    This is part of shot detector.
    Produced by w495 at 2017.05.04 04:18:27
"""

from __future__ import absolute_import, division, print_function

import logging

from shot_detector.handlers import BasePointHandler


class BasePointSelector(BasePointHandler):
    """
        ...
    """
    __logger = logging.getLogger(__name__)

    # noinspection PyUnusedLocal,PyUnusedLocal
    @staticmethod
    def select_point(event, video_state=None, **_kwargs):
        """
            Should be implemented
            :param event:
            :param video_state:
        """
        return event, video_state
