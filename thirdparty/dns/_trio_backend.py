# Copyright (C) Dnspython Contributors, see LICENSE for text of ISC license

"""trio async I/O library query support"""

import socket
import trio
import trio.socket  # type: ignore

import thirdparty.dns._asyncbackend
import thirdparty.dns.exception
import thirdparty.dns.inet


def _maybe_timeout(timeout):
    if timeout:
        return trio.move_on_after(timeout)
    else:
        return thirdparty.dns._asyncbackend.NullContext()


# for brevity
_lltuple = thirdparty.dns.inet.low_level_address_tuple


class DatagramSocket(thirdparty.dns._asyncbackend.DatagramSocket):
    def __init__(self, socket):
        self.socket = socket
        self.family = socket.family

    async def sendto(self, what, destination, timeout):
        with _maybe_timeout(timeout):
            return await self.socket.sendto(what, destination)
        raise thirdparty.dns.exception.Timeout(timeout=timeout)  # pragma: no cover

    async def recvfrom(self, size, timeout):
        with _maybe_timeout(timeout):
            return await self.socket.recvfrom(size)
        raise thirdparty.dns.exception.Timeout(timeout=timeout)

    async def close(self):
        self.socket.close()

    async def getpeername(self):
        return self.socket.getpeername()

    async def getsockname(self):
        return self.socket.getsockname()


class StreamSocket(thirdparty.dns._asyncbackend.DatagramSocket):
    def __init__(self, family, stream, tls=False):
        self.family = family
        self.stream = stream
        self.tls = tls

    async def sendall(self, what, timeout):
        with _maybe_timeout(timeout):
            return await self.stream.send_all(what)
        raise thirdparty.dns.exception.Timeout(timeout=timeout)

    async def recv(self, size, timeout):
        with _maybe_timeout(timeout):
            return await self.stream.receive_some(size)
        raise thirdparty.dns.exception.Timeout(timeout=timeout)

    async def close(self):
        await self.stream.aclose()

    async def getpeername(self):
        if self.tls:
            return self.stream.transport_stream.socket.getpeername()
        else:
            return self.stream.socket.getpeername()

    async def getsockname(self):
        if self.tls:
            return self.stream.transport_stream.socket.getsockname()
        else:
            return self.stream.socket.getsockname()


class Backend(thirdparty.dns._asyncbackend.Backend):
    def name(self):
        return 'trio'

    async def make_socket(self, af, socktype, proto=0, source=None,
                          destination=None, timeout=None,
                          ssl_context=None, server_hostname=None):
        s = trio.socket.socket(af, socktype, proto)
        stream = None
        try:
            if source:
                await s.bind(_lltuple(source, af))
            if socktype == socket.SOCK_STREAM:
                with _maybe_timeout(timeout):
                    await s.connect(_lltuple(destination, af))
        except Exception:  # pragma: no cover
            s.close()
            raise
        if socktype == socket.SOCK_DGRAM:
            return DatagramSocket(s)
        elif socktype == socket.SOCK_STREAM:
            stream = trio.SocketStream(s)
            s = None
            tls = False
            if ssl_context:
                tls = True
                try:
                    stream = trio.SSLStream(stream, ssl_context,
                                            server_hostname=server_hostname)
                except Exception:  # pragma: no cover
                    await stream.aclose()
                    raise
            return StreamSocket(af, stream, tls)
        raise NotImplementedError('unsupported socket ' +
                                  f'type {socktype}')    # pragma: no cover

    async def sleep(self, interval):
        await trio.sleep(interval)
