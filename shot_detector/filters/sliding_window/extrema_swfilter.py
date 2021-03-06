# -*- coding: utf8 -*-
"""
    This is part of shot detector.
    Produced by w495 at 2017.05.04 04:18:27
"""

from __future__ import absolute_import, division, print_function

import logging

import numpy as np
from scipy.signal import argrelmax, argrelmin

from .base_stat_swfilter import BaseStatSWFilter


class ExtremaSWFilter(BaseStatSWFilter):
    """
        ...
    """
    __logger = logging.getLogger(__name__)

    def aggregate_windows(self,
                          window_seq,
                          x=1,
                          case=max,
                          order=25,
                          **kwargs):
        """
        
        :param window_seq: 
        :param x: 
        :param case: 
        :param order: 
        :param kwargs: 
        :return: 
        """
        extrema_function = argrelmax
        if case is not max:
            extrema_function = argrelmin

        for window in window_seq:
            arg_max_seq = extrema_function(
                np.array(window),
                order=order,
            )
            arg_max_list = list(arg_max_seq)
            arg_max = arg_max_list[0]
            for win_index, win_item in enumerate(window):
                if win_index == 0:
                    yield -0.1
                elif win_index in arg_max:
                    yield x * 1
                else:
                    yield 0
