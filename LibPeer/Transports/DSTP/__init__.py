from LibPeer.Transports import Transport
from LibPeer.Transports.DSTP.Connection import Connection
from LibPeer.Formats.BinaryAddress import BinaryAddress
from LibPeer.Muxer import Muxer

import rx

class DSTP(Transport):
    identifier = b"\x06"

    def __init__(self, muxer: Muxer, options: dict):
        super().__init__(muxer, options)

        # For storing the "vaguely stateful" connections
        self.connections = {}


    def send(self, data: bytes, channel: bytes, address: BinaryAddress) -> rx.Observable:
        # Send the data using a connection
        return self._get_connection(channel, address).send(data)

    
    def _receive(self, data, channel, address):
        # Pass data along to the connection
        self._get_connection(channel, address).receive(data)


    def _get_connection(self, channel: bytes, address: BinaryAddress) -> Connection:
        if((address.application, channel, address) in self.connections):
            # Get the existing connection
            return self.connections[(address.application, channel, address)]

        else:
            # Create new connection
            connection = Connection(self.muxer, channel, address)

            # Add the connection to the dict
            self.connections[(address.application, channel, address)] = connection

            # Subscribe to new data on the connection
            connection.data_ready.subscribe(self._data_ready)

            # Return the connection
            return connection


    def _data_ready(self, info):
        # Info is (data, channel, address) - pass along to application
        self.incoming.on_next(info)