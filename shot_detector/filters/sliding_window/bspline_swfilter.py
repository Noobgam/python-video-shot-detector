# -*- coding: utf8 -*-
"""
    This is part of shot detector.
    Produced by w495 at 2017.05.04 04:18:27
"""

from __future__ import absolute_import, division, print_function

import logging
from builtins import range

import numpy as np
from scipy.signal import bspline

from .base_stat_swfilter import BaseStatSWFilter


class BsplineSWFilter(BaseStatSWFilter):
    """
        For experiments.
    """

    __logger = logging.getLogger(__name__)

    def aggregate_windows(self,
                          window_seq,
                          order=2,
                          **kwargs):
        """
        
        :param window_seq: 
        :param order: 
        :param kwargs: 
        :return: 
        """

        coef = 30
        for window in window_seq:
            splined_window = bspline(
                1 - np.array(window)[::coef],
                n=order,
            )
            for win_index, win_item in enumerate(splined_window):
                for i in range(coef):
                    yield win_item
