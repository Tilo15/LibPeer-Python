from LibPeer.Application.Unix import UnixApplication


import os

def determine_ideal_class():
    # Determine our platform
    if(os.name == "posix"):
        # See if the LibPeer Unix Daemon is available
        if(os.path.isfile("/var/run/net.unitatem.libpeer")):
            # Daemon is available, return UnixApplication class
            return UnixApplication

    # If all else fails, spin up a userland instance of the stack.
    # TODO do what the above comment states
    raise NotImplemented