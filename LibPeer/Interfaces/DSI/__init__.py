from LibPeer.Interfaces import Interface
from LibPeer.Application.ApplicationBase import ApplicationBase
from LibPeer.Formats.BinaryAddress import BinaryAddress
from LibPeer.Interfaces.DSI.Connection import Connection

import rx

class DSI(Interface):
    def __init__(self, app: ApplicationBase, channel: bytes = b"\x00"*16, transport: str = "DSTP"):
       super().__init__(app, channel, transport)
       self._connections = {}
       self.new_connection = rx.subjects.Subject()


    def _receive(self, data: bytes, peer: BinaryAddress):
        # Do we have an existing connection with this peer?
        if(peer in self._connections):
            # Pass the message along
            self._connections[peer]._receive(data)

        else:
            # Create a new connection object for this peer
            conn = Connection(self, peer)

            # Save the connection
            self._connections[peer] = conn

            # Process first lot of data
            conn._receive(data)


    def connect(self, peer: BinaryAddress, timeout: int = 20) -> Connection:
        """Initiate a DSI connection with the specified peer"""
        if(peer in self._connections and self._connections[peer].connected):
            raise IOError("Active DSI connection with specified peer alredy exists over this channel")

        conn = Connection(self, peer)
        self._connections[peer] = conn

        conn._connect()
        conn._wait_connected(timeout)


        return conn