from LibPeerUnix.Models import Transport
from LibPeer.Logging import log

class TransportPreferences:
    def __init__(self, *transports):
        self.transports = transports
        self.transport = None

    def select_transport(self, app):
        # Find the preference index
        lowest_index = len(self.transports)

        for transport in app.transports:
            if(transport.name in self.transports):
                index = self.transports.index(transport.name)
                if(index < lowest_index):
                    lowest_index = index
                    self.transport = transport

        if(self.transport):
            log.debug("Using preference %i: %s" % (lowest_index, self.transport.name))
        
        else:
            raise IOError("No transport protocol satisfies the requirements of this interface is available on this system")

    @property
    def _tid(self):
        if(self.transport):
            return self.transport.identifier

        else:
            raise IOError("No transport has been selected")


        

