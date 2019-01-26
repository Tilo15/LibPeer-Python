from LibPeer.Formats.AMPP.Subscription import Subscription
from LibPeer.Formats.BinaryAddress import BinaryAddress

class SubscriptionItemPeers:
    def __init__(self, app_id: bytes):
        self.id = app_id
        self.peers = set()

    def update(self, address: BinaryAddress, subscription: Subscription):
        if(self.id in subscription.subscriptions):
            self.peers.add(address)

        elif(address in self.peers):
            self.peers.remove(address)
        
    @property
    def has_peers(self):
        return len(self.peers) > 0