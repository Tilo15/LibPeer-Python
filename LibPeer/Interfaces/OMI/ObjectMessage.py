import struct
import msgpack
import uuid

class ObjectMessage:
    def __init__(self, obj, ttl: int, message_id: uuid.UUID = None):
        self.payload_size = 0
        self.ttl = ttl
        self.message_id = message_id

        # Create random id if none
        if(not self.message_id):
            self.message_id = uuid.uuid4()

        # Space to store the raw data
        self._raw_data = b""

        # Set to true when all data received
        self._ready = False

        # Store the object
        self.object = obj

        # Pre-Serialise the object if not none
        if(self.object):
            self._raw_data = msgpack.packb(self.object, encoding="utf-8")
            self.payload_size = len(self._raw_data)


    def _receive(self, data: bytes):
        # How much data are we missing?
        remaining = self.payload_size - len(self._raw_data)

        # Add up to the remaining amount to the buffer
        self._raw_data = data[:remaining]

        # Are we done?
        if(len(self._raw_data) == self.payload_size):
            # Yes, unpack the object
            self.object = msgpack.unpackb(self._raw_data, encoding="utf-8")

            self._ready = True

        # Return any leftover data to the sender
        return data[remaining:]


    @staticmethod
    def from_header(header: bytes):
        # Get data-field size
        payload_size = struct.unpack("!I", header[:4])[0]

        # Get time to live (and decrement)
        ttl = struct.unpack("!B", header[4:5])[0] - 1

        # Get message id
        message_id = uuid.UUID(bytes=header[5:21])

        # Create the message object
        om = ObjectMessage(None, ttl, message_id)
        om.payload_size = payload_size
        return om

    
    def serialise(self):
        return b"%b%b%b%b" % (struct.pack("!I", self.payload_size), struct.pack("!B", self.ttl), self.message_id.bytes, self._raw_data)