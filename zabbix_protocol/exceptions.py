# -:- coding:utf8 -:-

class ZabbixError(Exception):
    """The base class of all zabbix protocol exception

    """


class ZabbixAgentException(ZabbixError):
    """The base class for all zabbix agent relative exception

    """


class ZabbixAgentDownException(ZabbixAgentException):
    """The Zabbix agent unavailable

    """


class InvalidZabbixDataException(ZabbixAgentException):
    """

    """

    def __init__(self, expect_length, actual_length):
        message = 'Expect data length: {0}, actual data length:{1}'.format(expect_length, actual_length)
        super(InvalidZabbixDataException, self).__init__(message)


class InvalidZabbixHeaderException(ZabbixAgentException):
    """invalid zabbix header raise this exception

    """

    def __init__(self, message):
        message = 'Invalid zabbix header, actual data : {0}'.format(message)
        super(InvalidZabbixHeaderException, self).__init__(message)


class KeyUnsupportedException(ZabbixAgentException):
    """ 当获取某些特殊Item出错时，触发该异常

    """