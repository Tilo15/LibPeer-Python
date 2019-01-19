from LibPeer.System import Binding
from LibPeerUnix.Models import Transport
from LibPeer.Logging import log

class TransportPreferences:
    def __init__(self, *transports):
        self.transports = transports
        self.transport = None

    def select_transport(self, binding: Binding):
        # Find the preference index
        lowest_index = len(self.transports)

        for transport in binding.transports:
            if(transport.name in self.transports)
                index = self.transports.index(transport.name)
                if(index < lowest_index):
                    lowest_index = index
                    self.transport = transport

        if(self.transport):
            log.debug("Using preference %i: %s" % (lowest_index, self.transport.name))
        
        else:
            raise IOError("No transport protocol satisfies the requirements of this interface")

    @property
    def _tid(self):
        if(self.transport):
            return self.transport.protocol

        else:
            raise IOError("No transport has been selected")


        

