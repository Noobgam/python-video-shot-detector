# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import datetime


class Second(float):

    def time(self):
        return str(datetime.timedelta(seconds=self))