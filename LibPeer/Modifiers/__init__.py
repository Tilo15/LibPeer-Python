from LibPeer.Formats.BinaryAddress import BinaryAddress

class Modifier:
    def __init__(self):
        pass

    def ingress(self, data: bytes, channel: bytes, address: BinaryAddress) -> bytes:
        raise NotImplemented

    def egress(self, data: bytes, channel: bytes, address: BinaryAddress) -> bytes:
        raise NotImplemented