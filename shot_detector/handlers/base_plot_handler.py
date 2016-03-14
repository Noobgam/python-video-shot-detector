# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import logging
from collections import OrderedDict

import matplotlib.pyplot as plt

from shot_detector.utils.collections import SmartDict

# plt.rc('text', usetex=True)
plt.rc('font', family='DejaVu Sans')


class BasePlotHandler(object):
    __logger = logging.getLogger(__name__)
    __plot_buffer = OrderedDict()
    __line_list = []

    xlabel = '$t$'
    ylabel = '$L_1$'

    def add_data(self, name, key, value, style='', **kwargs):

        if not self.__plot_buffer.get(name):
            self.__plot_buffer[name] = SmartDict(
                x_list=[],
                y_list=[],
                style=style,
                options={}
            )
        self.__plot_buffer[name].x_list += [key]
        self.__plot_buffer[name].y_list += [value]
        self.__plot_buffer[name].style = style
        self.__plot_buffer[name].options = kwargs

    def plot_data(self, name=None):
        if name:
            self.plot_data_name(name)
        else:
            for name in self.__plot_buffer:
                self.plot_data_name(name)
        plt.legend(handles=self.__line_list)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)

        fig = plt.gcf()
        ax = plt.gca()

        self.arrowed_spines(fig, ax)


        plt.show()
        # plt.savefig('foo.pdf')

    def plot_data_name(self, name):
        key_value = self.__plot_buffer.get(name)
        if key_value:
            if key_value.options.pop('axvline', False):
                for x in key_value.x_list:
                    plt.axvline(x, label=name, **key_value.options)
            else:
                line, = plt.plot(
                    key_value.x_list,
                    key_value.y_list,
                    key_value.style,
                    label=name,
                    **key_value.options
                )
                self.__line_list += [line]

    def arrowed_spines(self, fig, ax):

        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()

        # removing the default axis on all sides:
        # for side in ['bottom','right','top','left']:
        #     ax.spines[side].set_visible(False)

        # # removing the axis ticks
        # plt.xticks([]) # labels
        # plt.yticks([])
        # ax.xaxis.set_ticks_position('none') # tick markers
        # ax.yaxis.set_ticks_position('none')

        # get width and height of axes object to compute
        # matching arrowhead length and width
        dps = fig.dpi_scale_trans.inverted()
        bbox = ax.get_window_extent().transformed(dps)
        width, height = bbox.width, bbox.height

        # manual arrowhead width and length
        hw = 3./100.*(ymax-ymin)
        hl = 5./100.*(xmax-xmin)
        lw = 1. # axis line width
        ohg = 0.3 # arrow overhang

        # compute matching arrowhead length and width
        yhw = hw/(ymax-ymin)*(xmax-xmin)* height/width
        yhl = hl/(xmax-xmin)*(ymax-ymin)* width/height

        # draw x and y axis
        ax.arrow(xmin, 0, xmax-xmin, 0., fc='k', ec='k', lw = lw,
                 head_width=hw, head_length=hl, overhang = ohg,
                 length_includes_head= True, clip_on = False)

        ax.arrow(0, ymin, 0., ymax-ymin, fc='k', ec='k', lw = lw,
                 head_width=yhw, head_length=yhl, overhang = ohg,
                 length_includes_head= True, clip_on = False)

