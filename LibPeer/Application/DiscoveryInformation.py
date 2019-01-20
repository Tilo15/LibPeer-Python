from LibPeer.Formats.BinaryAddress import BinaryAddress


class DiscoveryInformation:
    def __init__(self, peer: BinaryAddress, timestamp: int, distance: int):
        self.peer = peer
        self.last_discovered = timestamp
        self.ad = distance