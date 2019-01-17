from LibPeer.Formats.BinaryAddress import BinaryAddress

import uuid
import msgpack
import hashlib

class SambandPacket:
    def __init__(self, message_id: uuid.UUID, address: BinaryAddress):
        self.id = message_id
        self.address = address

    def serialise(self) -> bytes:
        address = self.address.serialise()
        id_bytes = self.id.bytes

        hasher = hashlib.sha256()
        hasher.update(id_bytes)
        hasher.update(address)
        checksum = hasher.digest()

        return b"\xF0\x9F\x87\xAE\xF0\x9F\x87\xB8%s" % msgpack.packb([id_bytes, address, checksum])


    @staticmethod
    def deserialise(data: bytes):
        """Returns tuple, first item is boolean which is set to true when the checksum is valid, second item is the packet"""
        if(data[:8] != b"\xF0\x9F\x87\xAE\xF0\x9F\x87\xB8"):
            raise TypeError("Data is missing Samband header")

        pid, address, checksum = msgpack.unpackb(data[8:])

        hasher = hashlib.sha256()
        hasher.update(pid)
        hasher.update(address)
        hashed = hasher.digest()

        packet = SambandPacket(uuid.UUID(bytes=pid), BinaryAddress.deserialise(address))
        return (packet, hashed == checksum)