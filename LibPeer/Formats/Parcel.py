import uuid

class Parcel:
    def __init__(self, parcel_id: uuid.UUID, channel: bytes, transport_protocol: bytes, application_protocol: bytes, data: bytes):
        self.id = parcel_id
        self.channel = channel
        self.transport_protocol = transport_protocol
        self.application_protocol = application_protocol
        self.data = data

    def serialise(self) -> bytes:
        return b"MXR%b%b%b%b\x02%b" % (self.id.bytes, self.channel, self.transport_protocol, self.application_protocol, self.data)

    @staticmethod
    def deserialise(data: bytes):
        if(data[:3] != b"MXR"):
            raise TypeError("Passed data is not a muxer parcel")

        ident = uuid.UUID(bytes=data[3:19])
        chann = data[19:35]
        trans = data[35:36]
        app, data = data[36:].split(b"\x02", 1)

        return Parcel(ident, chann, trans, app, data)

