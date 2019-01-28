from LibPeer.Formats.BinaryAddress import BinaryAddress

import uuid
import msgpack
import time

class Advertorial:
    def __init__(self, address: BinaryAddress, ttl: int, expires_in: int, aid: uuid.UUID = uuid.uuid4()):
        self._received = time.time()
        self.address = address
        self.ttl = ttl - 1
        self.expires_in = expires_in
        self.id = aid


    def serialise(self):
        return msgpack.packb({
            b"address": self.address.serialise(),
            b"ttl": self.ttl,
            b"expires_in": self.expires_in,
            b"id": self.id.bytes
        })


    @staticmethod
    def deserialise(data: bytes):
        message = msgpack.unpackb(data)
        return Advertorial(BinaryAddress.deserialise(message[b"address"]), message[b"ttl"], message[b"expires_in"], uuid.UUID(bytes=message[b"id"]))

    @property
    def expired(self) -> bool:
        return time.time() > self._received + self.expires_in


    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id
