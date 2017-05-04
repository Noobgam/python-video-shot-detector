# -*- coding: utf8 -*-
"""
    This is part of shot detector.
    Produced by w495 at 2017.05.04 04:18:27
"""


from __future__ import (absolute_import,
                        division,
                        print_function,
                        unicode_literals)

import logging

from shot_detector.filters import (
    Filter,
    ShiftSWFilter,
    DelayFilter,
    NormFilter,
    # FFMpegLikeThresholdSWFilter
)
from shot_detector.plotters.event.base import (
    BaseEventPlotter,
    FilterDescription,
    PlotOptions
)
from shot_detector.utils.log_meta import log_method_call_with


class FfmpegLikeEventPlotter(BaseEventPlotter):
    """
        ...
    """
    __logger = logging.getLogger(__name__)

    THRESHOLD = 0.08

    @log_method_call_with(logging.INFO)
    def seq_filters(self):
        """
        
        :return: 
        """
        delay = DelayFilter()
        norm = NormFilter()
        shift = ShiftSWFilter()
        original = delay(0)
        diff = original - shift
        self.THRESHOLD = 0.08
        threshold = (original > self.THRESHOLD) * 1.1

        sad_filter = diff | abs | norm(l=1)

        sad_diff_filter = sad_filter | diff | abs

        ffmpeg_like = Filter.tuple(sad_filter, sad_diff_filter) | min

        # ffmpeg_like_hardcore = FFMpegLikeThresholdSWFilter()

        return (
            FilterDescription(
                # Original signal.
                name='$F_{L_1} = ||F_{t}||_{L_1}$',
                plot_options=PlotOptions(
                    style='-',
                    color='gray',
                    width=3.0,
                ),
                formula=norm(l=1),
            ),

            FilterDescription(
                name='$D^{ffmpeg}_{t} = \min(D_t, |D_t-D_{t-1}|)$',
                plot_options=PlotOptions(
                    style='-',
                    color='red',
                    width=2.0,
                ),
                formula=ffmpeg_like
            ),

            FilterDescription(
                name='$D^{ffmpeg}_{t} > T_{const} $',
                plot_options=PlotOptions(
                    style=':',
                    color='orange',
                    width=2.0,
                ),
                formula=ffmpeg_like | threshold
            ),
            FilterDescription(
                # The threshold value.
                name='$T_{{const}} = {threshold} \in (0; 1)$'.format(
                    threshold=self.THRESHOLD
                ),
                plot_options=PlotOptions(
                    style='-',
                    color='black',
                    width=2.0,
                ),
                formula=norm(l=1) | self.THRESHOLD,
            ),
        )
