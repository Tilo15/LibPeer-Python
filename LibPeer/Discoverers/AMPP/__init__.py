from LibPeer.Discoverers import Discoverer
from LibPeer.Networks import Network
from LibPeer.Formats.BinaryAddress import BinaryAddress
from LibPeer.Formats.AMPP.Advertorial import Advertorial
from LibPeer.Formats.AMPP.Subscription import Subscription
from LibPeer.Discoverers.AMPP.SubscriptionItemPeers import SubscriptionItemPeers
from LibPeer.Discoverers.AMPP.Bootstrappers.Ipv4Multicast import Ipv4Multicast
from LibPeer.Discoverers.AMPP.Bootstrappers.DNS import DNS
from LibPeer.Logging import log


import rx
import uuid

CACHE_LIMIT = 10000
BOOTSTRAPPERS = [Ipv4Multicast, DNS]

class AMPP(Discoverer):
    def __init__(self, networks: list):
        super().__init__(networks)

        self.applications = set()

        self._peers_address_queried = set()
        self._reported_addresses = set()

        self._instance_id = uuid.uuid4().bytes

        self._peers = set()
        self._subscription_item_peers = {
            b"AMPP": SubscriptionItemPeers(b"AMPP")
        }
        self._cahce = set()
        self._resubscribe = True
        self._subscription_ids = set()

        for network in self.networks.values():
            network.incoming.subscribe(self._network_incoming)

        # Setup bootstrappers
        self._bootstrappers = [bootstrapper(networks) for bootstrapper in BOOTSTRAPPERS]
        for bootstrapper in self._bootstrappers:
            bootstrapper.discovered.subscribe(self._new_ampp_peer)


    def _network_incoming(self, info):
        data: bytes = info[0]
        address: BinaryAddress = info[1]

        if(data[:4] == b"AMPP"):
            # This is an AMPP peer
            address.application = b"AMPP"

            if(self._instance_id == data[4:20]):
                # Ignore if we are hearing ourselves
                return

            # If we are talking to someone new, add them (check done inside function)
            self._new_ampp_peer(address)
                
            # It's an AMPP packet!
            msg_type = data[20:23]
            message = data[23:]

            if(msg_type == b"ADV"):
                # Advertorial
                advertorial = Advertorial.deserialise(message)
                peer = advertorial.address

                # Have we received this before?
                if(advertorial not in self._cahce):
                    # Do we have peers interested in this app?
                    if(advertorial.address.application in self._subscription_item_peers):
                        # Can we forward it?
                        if(advertorial.ttl > 0):
                            # Forward to those peers
                            for peer in self._subscription_item_peers[advertorial.address.application].peers.copy():
                                # Make sure we don't send it back to the sending peer
                                if(peer != address):
                                    self._send(b"ADV" + advertorial.serialise(), peer)

                    # Are we interested in it?
                    if(advertorial.address.application in self.applications):
                        # Let the application know
                        # TODO Calculate a useful AD
                        self.discovered.on_next((advertorial.address, 10))

                    # Is it an AMPP advertorial?
                    if(advertorial.address.application == b"AMPP"):
                        self._new_ampp_peer(peer)
                        
                    # Add to cache
                    if(advertorial.ttl > 0):
                        self._add_to_cache(advertorial)


            elif(msg_type == b"SUB"):
                # Subscription
                subscription = Subscription.deserialise(message)

                # Have we received this before?
                if(subscription.id.bytes not in self._subscription_ids):
                    # Add to received subscriptions
                    self._subscription_ids.add(subscription.id.bytes)

                    # If they aren't already, subscribe them to AMPP discoveries
                    if(b"AMPP" not in subscription.subscriptions):
                        subscription.subscriptions.append(b"AMPP")

                    # Have they subscribed to something that we don't know of yet?
                    for app in set(subscription.subscriptions).difference(self._subscription_item_peers.keys()):
                        # Create it
                        self._subscription_item_peers[app] = SubscriptionItemPeers(app)

                    # Add/Remove sender from subscriptions
                    for sub_item in self._subscription_item_peers.values():
                        sub_item.update(address, subscription)

                    # Do they want to see cached items?
                    if(not subscription.renewing):
                        # Send relevent cached items
                        advertorials = self._get_in_cache(subscription.subscriptions)
                        for adv in advertorials:
                            self._send(b"ADV" + adv.serialise(), address)

                        # Send to all AMPP peers
                        for peer in self._peers.copy():
                            if peer != address:
                                self._send(b"SUB" + subscription.serialise(), peer)


            elif(msg_type == b"ADQ"):
                # Address query
                address.application = b""
                address.label = None
                # Reply with address
                self._send(b"ADR" + address.serialise(), address)


            elif(msg_type == b"ADR"):
                # Address response
                if(address in self._peers_address_queried):
                    # If we asked this peer for it's opinion, deserialise the response
                    reported_address = BinaryAddress.deserialise(message)

                    # Log out the response
                    log.info("%s sees us as %s" % (address, reported_address))

                    # Save the response
                    self._reported_addresses.add(reported_address)

                    # Remove peer from list of queries peers
                    self._peers_address_queried.remove(address)
                

    def _send(self, message: bytes, address: BinaryAddress):
        self.networks[address.network_type].send(b"AMPP%b%b" % (self._instance_id, message), address).subscribe()


    def _new_ampp_peer(self, peer: BinaryAddress):
        # Do we already have this peer?
        if(peer not in self._peers):
            log.debug("Found peer %s" % peer)
            # Add the peer
            self._peers.add(peer)

            # Autosubscribe it to AMPP
            self._subscription_item_peers[b"AMPP"].peers.add(peer)

            # Send it our subscriptions
            self._resubscribe = True
            self._send_subscriptions([peer,])

            # Send it an address query
            self._peers_address_queried.add(peer)
            self._send(b"ADQ", peer)

            # Advertise our known other AMPP peers to it TODO maybe don't do this
            for other_peer in self._peers:
                self._send(b"ADV" + Advertorial(other_peer, 1, 280).serialise(), peer)


    def _clean_cahce(self):
        expired = [adv for adv in self._cahce if adv.expired]
        for adv in expired:
            self._cahce.remove(adv)


    def _add_to_cache(self, advertorial: Advertorial):
        # Clean up cache (may have more room)
        self._clean_cahce()

        # Do we have room?
        if(len(self._cahce) < CACHE_LIMIT):
            # Add the advertorial
            self._cahce.add(advertorial)


    def _get_in_cache(self, apps):
        # Clean up the cache (don't want to restransmit expired advertorials)
        self._clean_cahce()

        # Return all valid items
        return [adv for adv in self._cahce if adv.address.application in apps]


    def _send_subscriptions(self, peers):
        # Get all relevent app namespaces
        #apps = [app for app, sips in self._subscription_item_peers.items() if sips.has_peers]
        # ^^^ What was I thinking?
        
        # Add applications that the user wants
        apps = [app for app in self.applications]

        # Add AMPP subscription
        apps.append(b"AMPP")

        # Create subscription
        sub  = Subscription(apps, not self._resubscribe)

        # Set resubscription status
        self._resubscribe = False

        # Send to all AMPP peers
        for peer in peers:
            self._send(b"SUB" + sub.serialise(), peer)


    def advertise(self, address: BinaryAddress) -> int:
        """Returns the recommended time in seconds to wait before re-advertising"""
        # Create the advertorial
        advertorial = Advertorial(address, 30, 180)

        # Cache the advertorial to immediately send to new peers
        self._add_to_cache(advertorial)

        # Keep track of the number of peers that the advertorial was sent to
        send_count = 0

        # Could there possibly be any peers interested?
        if(address.application in self._subscription_item_peers):
            # Send to all peers interested (if any still exist)
            for peer in self._subscription_item_peers[address.application].peers:
                self._send(b"ADV" + advertorial.serialise(), peer)
                if(advertorial.address.application != b"AMPP"):
                    send_count += 1

        # TODO the manager probably calls this a few times, (if there's labels etc) so the below
        # should only be done once per time period.

        # While we're at it, update our subscriptions too
        self._send_subscriptions(self._peers)

        # Assuming this isn't advertising "AMPP", take this opportunity to advertise AMPP
        if(address.application != b"AMPP"):
            self.advertise(BinaryAddress(address.network_type, address.network_address, address.network_port, b"AMPP"))

        # Did we send to any peers?
        if(send_count > 0):
            # Tell the manager to re-advertised in 180 seconds (the timeout)
            return 180

        else:
            # Try again in 5 seconds
            return 5


    def add_application(self, namespace: bytes):
        """Add an application namespace to discover"""
        self.applications.add(namespace)
        self._resubscribe = True
        self._send_subscriptions(self._peers)


    def remove_aplication(self, namespace: bytes):
        """Stop discovering an application namespace"""
        self.applications.remove(namespace)


    def get_addresses(self) -> list:
        """Get a list of addresses that peers claim to see us as"""
        return [addr for addr in self._reported_addresses]


    def stop(self):
        """Stop the discoverer"""
        for bootstrapper in self._bootstrappers:
            bootstrapper.stop()