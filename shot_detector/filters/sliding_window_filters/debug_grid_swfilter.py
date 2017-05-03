# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import logging

from .base_swfilter import BaseSWFilter


class DebugGridSWFilter(BaseSWFilter):
    __logger = logging.getLogger(__name__)

    def aggregate_windows(self,
                          window_seq,
                          triangles=True,
                          if_index=0,
                          **kwargs):

        for window in window_seq:
            window_len = len(window)
            for win_index, _ in enumerate(window):
                if triangles:
                    yield 1.0 * win_index / window_len
                else:
                    if if_index == win_index:
                        yield 1
                    else:
                        yield 0
