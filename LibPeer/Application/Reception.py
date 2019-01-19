from LibPeer.Formats.BinaryAddress import BinaryAddress

class Reception:
    def __init__(self, data: bytes, transport_id: bytes, channel: bytes, address: BinaryAddress):
        self.data = data
        self.transport = transport_id
        self.channel = channel
        self.peer = address