import struct

import six

from zabbix_protocol.exceptions import InvalidZabbixDataException
from zabbix_protocol.exceptions import InvalidZabbixHeaderException
from zabbix_protocol.utils import hex_representation

ZBX_HEADER = b'ZBXD'
ZBX_VERSION = 1
ZBX_HEADER_FMT = '<4sBq'

MAX_BUFFER = 1024 * 32

StringIO = six.BytesIO

ZBX_UNSUPPORTED_ITEM = "ZBX_NOTSUPPORTED"

TYPES = ['ext2', 'ext3', 'ext4', 'xfs', 'devtmpfs', 'tmpfs', 'fat16', 'fat32', 'ntfs']


def __repr__(self):
    return ZBX_UNSUPPORTED_ITEM


ZBX_UNSUPPORTED = type('ZabbixUnsupported', (object,), {'__repr__': __repr__})()


def loads(socket, buffer_size=MAX_BUFFER):
    """

    :param socket:
    :param buffer_size:
    :return:
    """
    header_size = struct.calcsize(ZBX_HEADER_FMT)
    buf = socket.recv(header_size)
    if len(buf) < header_size:
        msg = hex_representation(buf)
        raise InvalidZabbixHeaderException(msg)
    zbx_header, zbx_version, data_length = struct.unpack(ZBX_HEADER_FMT, buf)
    assert zbx_header == ZBX_HEADER
    assert zbx_version == ZBX_VERSION
    if data_length < 0:
        raise InvalidZabbixDataException(0, data_length)

    buf = StringIO()
    receive_size = 0
    while True:
        data = socket.recv(buffer_size)
        if len(data) <= 0:
            break

        buf.write(data)
        receive_size += len(data)
        if receive_size == data_length:
            break
        elif receive_size > data_length:
            raise InvalidZabbixDataException(data_length, receive_size)

    return buf.getvalue().decode('utf-8')


def dumps(data):
    """

    :param data:
    :return:
    """
    json_byte = len(data)
    header = struct.pack(ZBX_HEADER_FMT, ZBX_HEADER, ZBX_VERSION, json_byte)
    return header + data.encode('utf-8')


def is_disk_format(fs_type):
    return fs_type.lower() in TYPES
