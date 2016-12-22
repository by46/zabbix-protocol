import json
import logging
import socket

from zabbix_protocol.exceptions import KeyUnsupportedException
from zabbix_protocol.exceptions import ZabbixAgentDownException
from zabbix_protocol.utils import cached_property
from .common import ZBX_UNSUPPORTED
from .common import ZBX_UNSUPPORTED_ITEM
from .common import dumps
from .common import is_disk_format
from .common import loads
from .items import AGENT_VERSION
from .items import NET_IF_DISCOVERY
from .items import SYSTEM_CPU_DISCOVERY
from .items import SYSTEM_UNAME
from .items import VFS_FS_DISCOVERY


class KeyItem(object):
    SEP = '\x00'

    def __init__(self, raw):
        self.msg = None
        self.value = raw
        if self.SEP in raw:
            pos = raw.index(self.SEP)
            if pos:
                result = raw[:pos]
                if result == ZBX_UNSUPPORTED_ITEM:
                    self.value = ZBX_UNSUPPORTED
                    self.msg = raw[pos + 1:]

    @property
    def success(self):
        return self.msg is None

    def __repr__(self):
        return '{0}'.format(self.value)


class ZabbixClient(object):
    Windows = 1
    Linux = 2
    Other = 255

    def __init__(self, hostname, port=10050, logger =None):
        self.hostname = hostname
        self.port = port
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger('zabbix_protocol')
        item = self.get_key(AGENT_VERSION)
        self.agent_version = item.value

    def get_key(self, key):
        """

        :param key:
        :return: class:`str`
        """
        try:
            transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            transport.connect((self.hostname, self.port))
            transport.sendall(dumps(key))
            return KeyItem(loads(transport))
        except socket.error as e:
            self.logger.exception(e)
            raise ZabbixAgentDownException(e)

    @cached_property
    def platform(self):
        item = self.get_key(SYSTEM_UNAME)
        if not item.success:
            return self.Other
        value = item.value
        if 'Windows' in value:
            return self.Windows
        elif 'Linux' in value:
            return self.Linux
        return self.Other

    @cached_property
    def is_windows(self):
        return self.platform == self.Windows

    @cached_property
    def is_linux(self):
        return self.platform == self.Linux

    @cached_property
    def fs(self):
        item = self.get_key(VFS_FS_DISCOVERY)
        if not item.success:
            self.logger.warning('get key %s on %s:%s failed, msg: %s', NET_IF_DISCOVERY, self.hostname, self.port,
                                item.msg)
            raise KeyUnsupportedException(item.msg)
        return [item['{#FSNAME}'] for item in json.loads(item.value)['data'] if is_disk_format(item['{#FSTYPE}'])]

    @cached_property
    def ifs(self):
        item = self.get_key(NET_IF_DISCOVERY)
        if not item.success:
            self.logger.warning('get key %s on %s:%s failed, msg: %s', NET_IF_DISCOVERY, self.hostname, self.port,
                                item.msg)
            raise KeyUnsupportedException(item.msg)
        return [x['{#IFNAME}'] for x in json.loads(item.value).get('data', [])]

    @cached_property
    def cpus(self):
        item = self.get_key(SYSTEM_CPU_DISCOVERY)
        if not item.success:
            self.logger.warning('get key %s on %s:%s failed, msg: %s', SYSTEM_CPU_DISCOVERY, self.hostname, self.port,
                                item.msg)
            raise KeyUnsupportedException(item.msg)
        return [x['{#CPU.NUMBER}'] for x in json.loads(item.value).get('data', []) if
                x['{#CPU.STATUS}'] == 'online']
