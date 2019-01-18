from LibPeer.Formats.BinaryAddress import BinaryAddress
from LibPeer.Muxer import Muxer
from LibPeer.Transports import Transport

import rx

class EDP(Transport):

    identifier = b"\x01"

    def __init__(self, muxer: Muxer, options: dict):
        super().__init__(muxer, options)


    def send(self, data: bytes, channel: bytes, address: BinaryAddress) -> rx.Observable:
        return self.muxer.send(data, channel, self.identifier, address)

    
    def _receive(self, data, channel, address):
        self.incoming.on_next((data, channel, address))