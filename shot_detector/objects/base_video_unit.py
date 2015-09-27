# -*- coding: utf8 -*-

from __future__ import absolute_import
import six


from .second import Second


class BaseVideoUnit(object):

    __source = None

    __time = None
    __global_number = None

    __UNDEFINED = object()

    def __init__(self, **kwargs):
        self._stored_attrs(kwargs)

    def _stored_attrs(self, attr_dict):
        for attr, value in six.iteritems(attr_dict):
            setattr(self, attr, value)

    @property
    def time(self):
        if self.__time is None:
            if self.source and self.source.time:
                self.__time = Second(self.source.time)
        return self.__time

    @time.setter
    def time(self, value):
        self.__time = value

    @property
    def hms(self):
        if self.time:
            return self.time.hms()
        return '00:00:00'

    @hms.setter
    def hms(self, value):
        self.__time = value


    @property
    def global_number(self):
        if self.__global_number is None:
            if self.source:
                self.__global_number = self.source.global_number
        return self.__global_number

    @global_number.setter
    def global_number(self, value):
        self.__global_number = value

    @property
    def number(self):
        return self.global_number

    @number.setter
    def number(self, value):
        self.global_number = value

    @property
    def source(self):
        return self.__source

    @source.setter
    def source(self, value):
        self.__source = value

    def __repr__(self):
        repr_list = []
        cname = self.__class__.__name__
        for key, value in six.iteritems(vars(self)):
            key = key.replace('_%s__'%(cname), '@')
            repr_list += ["'%s':%s"%(key, value)]
        repr_str = ','.join(repr_list)
        return "{%s}"%(repr_str)
