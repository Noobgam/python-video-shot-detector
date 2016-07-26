# -*- coding: utf8 -*-

from __future__ import (absolute_import,
                        division,
                        print_function,
                        unicode_literals)

import logging

from shot_detector.filters import (
    FFMpegLikeTresholdSWFilter,
    ShiftSWFilter,
    DelayFilter,
    NormFilter,
    ModulusFilter,
    MaxSWFilter,
    MinSWFilter,
    BaseSWFilter,
    NormSWFilter,
)
from shot_detector.utils.collections import SmartDict
from .base_event_plotter import BaseEventPlotter

import pdb


from shot_detector.utils.log_meta import log_method_call_with

class StaticThresholdEventPlotter(BaseEventPlotter):

    __logger = logging.getLogger(__name__)

    @log_method_call_with(logging.WARN)
    def seq_filters(self):

        delay = DelayFilter()
        norm = NormFilter()
        modulus = ModulusFilter()
        shift = ShiftSWFilter()
        original = delay(0)
        diff = original - shift
        ffmpeglike = FFMpegLikeTresholdSWFilter()

        sw = BaseSWFilter(s=200, min_size=2)

        swmax = sw | max
        swmin = sw | min

        # swnorm = (original - min) / (max - min)
        #
        # normsw = NormSWFilter(s=200)


        return (
            SmartDict(
                name='$F_{L_1} = |F_{t}|_{L_1}$',
                plot_options=SmartDict(
                    linestyle='-',
                    color='gray',
                    linewidth=3.0,
                ),
                filter=norm(l=1),
            ),


            SmartDict(
                name='$D_{\,200,t} = swnorm_{\,200} D_{t}$',
                plot_options=SmartDict(
                    linestyle='-',
                    color='green',
                    linewidth=1.0,
                ),
                filter=norm(l=1) | diff | modulus | (original - swmin)
                                                    / (swmax - swmin)
            ),



            SmartDict(
                name='$D_{t} = |F_{t} - F_{t-1}|_{L_1}$',
                plot_options=SmartDict(
                    linestyle='-',
                    color='blue',
                    linewidth=2.0,
                ),
                filter=diff | modulus | norm(l=1)
            ),


          # SmartDict(
          #       name='$D^{ffmpeg}_{\,200,t} '
          #            '= swnorm_{\,200} D^{ffmpeg}_{t}$',
          #       plot_options=SmartDict(
          #           linestyle='-',
          #           color='orange',
          #           linewidth=1.0,
          #       ),
          #       filter=ffmpeglike | swnorm
          #   ),
          #
          #
          #   SmartDict(
          #       name='$D^{ffmpeg}_{t} = \min(D_t, D_t-D_{t-1})$',
          #       plot_options=SmartDict(
          #           linestyle='-',
          #           color='red',
          #           linewidth=2.0,
          #       ),
          #       filter=ffmpeglike
          #   ),

            SmartDict(
                name='$T_{const} = 0.8 \in (0; 1)$',
                plot_options=SmartDict(
                    linestyle='-',
                    color='black',
                    linewidth=2.0,
                ),
                filter=norm(l=1) | 0.8 ,
            ),
        )
