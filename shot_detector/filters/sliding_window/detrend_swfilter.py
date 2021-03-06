# -*- coding: utf8 -*-
"""
    This is part of shot detector.
    Produced by w495 at 2017.05.04 04:18:27
"""

from __future__ import absolute_import, division, print_function

import logging

from scipy.signal import detrend

from .base_stat_swfilter import BaseStatSWFilter


class DetrendSWFilter(BaseStatSWFilter):
    """
        ...
    """
    __logger = logging.getLogger(__name__)

    def aggregate_windows(self,
                          window_seq,
                          **kwargs):
        """
        
        :param window_seq: 
        :param kwargs: 
        :return: 
        """
        for window in window_seq:
            window_detrended = detrend(window)
            for win_index, win_item in enumerate(window_detrended):
                yield win_item
