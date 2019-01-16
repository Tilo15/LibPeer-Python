from LibPeer.Formats.BinaryAddress import BinaryAddress
from LibPeer.Formats.Parcel import Parcel
from LibPeer.Muxer import Muxer

import rx

class Transport:

    identifier = b""

    def __init__(self, muxer: Muxer, options: dict):
        self.muxer = muxer
        self.options = options
        self.incoming = rx.subjects.Subject()

        self.muxer.incoming.subscribe(self._receive_handler)


    def send(self, data: bytes, address: BinaryAddress) -> rx.Observable:
        raise NotImplementedError

    def _receive_handler(self, info):
        # Get the data
        parcel: Parcel = info[0]
        address: BinaryAddress = info[1]

        # Make sure we are the ones to handle this
        if(parcel.transport_protocol == self.identifier):
            self._receive(parcel.data, parcel.channel, address)


    def _receive(self, data, channel, address):
        raise NotImplementedError