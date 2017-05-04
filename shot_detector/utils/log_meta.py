# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_func

import logging
import time
import types
from functools import wraps, partial

import six


class LogMeta(type):
    """
        Metaclass for logging every call 
        of every method of target class.
    """

    __default_logger = logging.getLogger(__name__)

    __default_log_level = logging.DEBUG

    @staticmethod
    def log_settings_configure(**kwargs):
        from shot_detector.utils.log_settings import LogSetting
        log_setting = LogSetting(**kwargs)
        conf = log_setting.configure()
        return conf

    @staticmethod
    def ignore_method_call(func):
        func.ignore_log_meta = True
        return func

    @staticmethod
    def should_be_overloaded(func):
        func.should_be_overloaded = True
        return func

    @classmethod
    def log_method_call(mcs, func):
        logger = mcs.__default_logger
        level = mcs.__default_log_level
        return mcs.decorate(logger, level, str(), func)

    @classmethod
    def log_method_call_with(mcs, level=None, logger=None):
        if not logger:
            logger = mcs.__default_logger
        if not level:
            level = mcs.__default_log_level

        def _log_call(func):
            return mcs.decorate(logger, level, str(), func)

        return _log_call

    @classmethod
    def log_dummy_call(mcs, func):
        logger = mcs.__default_logger
        level = mcs.__default_log_level
        func = mcs.should_be_overloaded(func)
        return mcs.decorate(logger, level, str(), func)

    def __new__(mcs,
                class_name=None,
                bases=None,
                attr_dict=None,
                *args,
                **kwargs):

        logger = attr_dict.get('meta_logger',
                               mcs.__default_logger)
        log_level = attr_dict.get('meta_log_level',
                                  mcs.__default_log_level)

        if logger.isEnabledFor(log_level):
            for key, value in six.iteritems(attr_dict):
                if (isinstance(value, types.funcType) or
                        isinstance(value, types.LambdaType) or
                        isinstance(value, types.MethodType)):
                    attr_dict[key] = mcs.decorate(
                        logger,
                        log_level,
                        class_name,
                        value
                    )

        return super(LogMeta, mcs).__new__(mcs,
                                           class_name,
                                           bases,
                                           attr_dict)

    @classmethod
    def decorate(mcs, logger, level, class_name, func):
        """
        Decorate method `func`.
        Every call of `func` will be reported to logger.
        This func (decorate) calls only one time
        — at target class construction,

        :param logging.Logger logger:  logger object
        :param int level: logger level 
        :param string class_name:
            the name of target class
        :param func | method | lambda | frame func: 
            input method for decoration
        :return: wrapped(func)
            decorated version of input func
        """

        if hasattr(func, 'ignore_log_meta'):
            return func

        if hasattr(func, 'should_be_overloaded'):
            pre_call = partial(mcs.dummy_pre_call,
                               logger,
                               level,
                               class_name,
                               func)

            @wraps(func)
            def dummy_wrapper(self, *args, **kwargs):
                pre_call()
                res = func(self, *args, **kwargs)
                return res

            return dummy_wrapper

        pre_call = partial(mcs.pre_call, logger, level, class_name,
                           func)
        post_call = partial(mcs.post_call, logger, level, class_name,
                            func)

        @wraps(func)
        def call_wrapper(self, *args, **kwargs):
            pre_call()
            res = func(self, *args, **kwargs)
            post_call()
            return res

        return call_wrapper

    @classmethod
    def pre_call(mcs, logger, level, class_name, func):
        func = mcs.add_pre_call_attrs(func)
        logger.log(level,
                   "[{num}] {mod}.{cls} {fun}".format(
                       num=func.call_number,
                       mod=func.__module__,
                       cls=class_name,
                       fun=func.__name__,
                   ))
        return func

    @classmethod
    def post_call(mcs, logger, level, class_name, func):
        func = mcs.add_post_call_attrs(func)
        logger.log(level,
                   "[{num}] {mod}.{cls} {fun} ({time:f})".format(
                       num=func.call_number,
                       mod=func.__module__,
                       cls=class_name,
                       fun=func.__name__,
                       time=func.delta_time,
                   ))
        return func

    @classmethod
    def dummy_pre_call(mcs, logger, level, class_name, func):
        logger.log(level,
                   "{mod}.{cls}{fun}: "
                   "dummy method: "
                   "should be overloaded".format(
                       mod=func.__module__,
                       cls=class_name,
                       fun=func.__name__,
                   ))
        return func

    @classmethod
    def add_pre_call_attrs(mcs, func):
        if not hasattr(func, 'call_number'):
            func.call_number = 0
        func.call_number += 1
        func.start_time = time.time()
        return func

    @classmethod
    def add_post_call_attrs(mcs, func):
        func.stop_time = time.time()
        func.delta_time = func.stop_time - func.start_time
        return func


ignore_log_meta = LogMeta.ignore_method_call

log_method_call = LogMeta.log_method_call

log_method_call_with = LogMeta.log_method_call_with

log_dummy_call = LogMeta.log_dummy_call

should_be_overloaded = LogMeta.should_be_overloaded

# for_overload = LogMeta.should_be_overloaded
# overload_me = should_be_overloaded
