from LibPeer.Formats.AMPP.Subscription import Subscription
from LibPeer.Formats.BinaryAddress import BinaryAddress
from LibPeer.Logging import log

class SubscriptionItemPeers:
    def __init__(self, app_id: bytes):
        self.id = app_id
        self.peers = set()

    def update(self, address: BinaryAddress, subscription: Subscription):
        if(self.id in subscription.subscriptions):
            self.peers.add(address)
            log.debug("Peer %s just subscribed to application '%s'" % (address, self.id))

        elif(address in self.peers):
            log.debug("Peer %s just unsubscribed from application '%s'" % (address, self.id))
            self.peers.remove(address)
        
    @property
    def has_peers(self):
        return len(self.peers) > 0