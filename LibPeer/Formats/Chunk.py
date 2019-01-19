import time
import zlib
import struct
import rx


class Chunk:
    def __init__(self, chunk_id: bytes, prev_chunk_id: bytes, payload: bytes):
        self.id = chunk_id
        self.prev_id = prev_chunk_id
        self.payload = payload
        self.time_sent = 0

    
    def serialise(self) -> bytes:
        # Create the data section
        data = b"%b%b%b" % (self.id, self.prev_id, self.payload)

        # Update time sent
        self.time_sent = time.time()

        # Create chunk data (TODO implement full checksum)
        return b"%b%b%b" % (struct.pack("!dI", self.time_sent, zlib.adler32(data)), b"\x00"*16, data)


    @staticmethod
    def deserialise(data: bytes):
        # Get the metadata
        time_sent, checksum = struct.unpack("!dI", data[:12])

        # Create the chunk
        chunk = Chunk(data[28:44], data[44:60], data[60:])

        # Return the chunk, its validity, and time send field
        return chunk, checksum == zlib.adler32(data[28:]), time_sent
