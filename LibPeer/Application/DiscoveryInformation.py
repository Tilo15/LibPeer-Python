from LibPeerUnix.Models import Peer as PeerModel
from LibPeer.Formats.BinaryAddress import BinaryAddress


class DiscoveryInformation:
    def __init__(self, peer: PeerModel, address: BinaryAddress):
        self.peer = address
        self.last_discovered = peer.last_seen
        self.ad = peer.administrative_distance