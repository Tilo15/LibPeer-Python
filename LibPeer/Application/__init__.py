from LibPeer.Application.Unix import UnixApplication


import os

def _determine_ideal_class():
    # Determine our platform
    if(os.name == "posix"):
        # See if the LibPeer Unix Daemon is available
        if(os.path.exists("/var/run/net.unitatem.libpeer")):
            # Daemon is available, return UnixApplication class
            return UnixApplication

    # If all else fails, spin up a userland instance of the stack.
    # TODO do what the above comment states
    raise NotImplementedError


def Application(namespace) -> ApplicationBase:
    # If namespace is a string, convert to bytes
    if(type(namespace) == str):
        namespace = namespace.encode("utf-8")

    # Figure out what ApplicationBase descentant to use
    app_class = _determine_ideal_class()

    # Return a new instance
    return app_class(namespace)
