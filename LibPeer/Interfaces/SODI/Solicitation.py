import uuid
import msgpack
import struct

class Solicitation:
    def __init__(self, sodi, peer, query: str, token: uuid.UUID = None):
        self.query = query
        self.token = token
        if(self.token == None):
            self.token = uuid.uuid4()

        self._sodi = sodi
        self.peer = peer
        self.tx_fraction = 0.0


    def serialise(self):
        data = msgpack.packb({
            b"query": self.query.encode("utf-8"),
            b"token": self.token.bytes
        })
        
        return struct.pack("!H", len(data)) + data


    @staticmethod
    def deserialise(data: bytes, peer, sodi):
        message = msgpack.unpackb(data[2:])
        return Solicitation(sodi, peer, message[b"query"].decode("utf-8"), uuid.UUID(bytes=message[b"token"]))

    
    def reply(self, obj: dict, data = b"", encoding="utf-8"):
        """Reply with an object and optionally either a bytes object or a file object to send as the binary data"""
        # Is data bytes or a file?
        if(type(data) == bytes):
            # Send it all along
            self._sodi._send(self._create_reply(obj, encoding, len(data)) + data, self.peer)
            self.data_sent_frac = 1

        else:
            # Send in segments
            f = data
            if(not f.seekable()):
                raise IOError("Cannot reply with non-seekable stream")

            if(not f.readable()):
                raise IOError("Cannot reply with non-readable stream")

            # Get stream length
            f.seek(0, 2)
            size = f.tell()
            f.seek(0, 0)

            # Send object and size information
            self._sodi._send(self._create_reply(obj, encoding, size), self.peer)

            # Keep track of amount sent
            sent = 0

            # Read the file in 8172 byte chunks
            while sent < size:
                data = f.read(8172)
                self._sodi._send(data, self.peer)
                sent += len(data)
                self.tx_fraction = sent / float(size)


    def _create_reply(self, obj, encoding, datasize):
        obj_data = msgpack.packb(obj, encoding=encoding)
        return struct.pack("!I", len(obj_data)) + self.token.bytes + obj_data + struct.pack("!Q", datasize)