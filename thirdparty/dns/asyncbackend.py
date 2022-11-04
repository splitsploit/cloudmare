# Copyright (C) Dnspython Contributors, see LICENSE for text of ISC license

import thirdparty.dns.exception

from thirdparty.dns._asyncbackend import Socket, DatagramSocket, \
    StreamSocket, Backend  # noqa:


_default_backend = None

_backends = {}

# Allow sniffio import to be disabled for testing purposes
_no_sniffio = False

class AsyncLibraryNotFoundError(thirdparty.dns.exception.DNSException):
    pass


def get_backend(name):
    """Get the specified asychronous backend.

    *name*, a ``str``, the name of the backend.  Currently the "trio",
    "curio", and "asyncio" backends are available.

    Raises NotImplementError if an unknown backend name is specified.
    """
    backend = _backends.get(name)
    if backend:
        return backend
    if name == 'trio':
        import thirdparty.dns._trio_backend
        backend = thirdparty.dns._trio_backend.Backend()
    elif name == 'curio':
        import thirdparty.dns._curio_backend
        backend = thirdparty.dns._curio_backend.Backend()
    elif name == 'asyncio':
        import thirdparty.dns._asyncio_backend
        backend = thirdparty.dns._asyncio_backend.Backend()
    else:
        raise NotImplementedError(f'unimplemented async backend {name}')
    _backends[name] = backend
    return backend


def sniff():
    """Attempt to determine the in-use asynchronous I/O library by using
    the ``sniffio`` module if it is available.

    Returns the name of the library, or raises AsyncLibraryNotFoundError
    if the library cannot be determined.
    """
    try:
        if _no_sniffio:
            raise ImportError
        import sniffio
        try:
            return sniffio.current_async_library()
        except sniffio.AsyncLibraryNotFoundError:
            raise AsyncLibraryNotFoundError('sniffio cannot determine ' +
                                            'async library')
    except ImportError:
        import asyncio
        try:
            asyncio.get_running_loop()
            return 'asyncio'
        except RuntimeError:
            raise AsyncLibraryNotFoundError('no async library detected')
        except AttributeError:  # pragma: no cover
            # we have to check current_task on 3.6
            if not asyncio.Task.current_task():
                raise AsyncLibraryNotFoundError('no async library detected')
            return 'asyncio'


def get_default_backend():
    """Get the default backend, initializing it if necessary.
    """
    if _default_backend:
        return _default_backend

    return set_default_backend(sniff())


def set_default_backend(name):
    """Set the default backend.

    It's not normally necessary to call this method, as
    ``get_default_backend()`` will initialize the backend
    appropriately in many cases.  If ``sniffio`` is not installed, or
    in testing situations, this function allows the backend to be set
    explicitly.
    """
    global _default_backend
    _default_backend = get_backend(name)
    return _default_backend
