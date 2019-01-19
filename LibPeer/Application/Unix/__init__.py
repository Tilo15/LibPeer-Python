from LibPeer.Application import ApplicationBase
from LibPeerUnix.Models import Peer, Address, Message
from LibPeerUnix import LibPeerUnixConnection
from LibPeer.Modifiers import Modifier
from LibPeer.Formats.BinaryAddress import BinaryAddress
from LibPeer.Application.Preferences import TransportPreferences
from LibPeer.Application.DiscoveryInformation import DiscoveryInformation
from LibPeer.Application.Reception import Reception
from LibPeer.Application.SystemInformation import TransportInformation, NetworkInformation, DiscovererInformation

import rx

class UnixApplication(ApplicationBase):
    def __init__(self, namespace: bytes):
        # Initialise the base class
        super().__init__(namespace)

        # Store list of modifiers
        self.modifiers = []

        # Connect to the daemon
        self.system = LibPeerUnixConnection()

        # Connect messages to those interested
        self.system.receive.subscribe(lambda m: self.incoming.on_next(self._receive)
        self.system.new_peer.subscribe(lambda p: self.new_peer.on_next(DiscoveryInformation(p, self._address_to_baddress(p.address))))


        # Collect information on the system
        self.networks = [NetworkInformation(n.name, n.protocol, n.actice) for n in self.system.available_networks()]
        self.transports = [TransportInformation(t.name, t.protocol) for t in self.system.available_transports()
        self.discoverers = [DiscovererInformation(d) for d in self.system.available_discoverers()]

        # Bind to the namespace
        self.system.bind(namespace)


    def _receive(self, message: Message):
        # Convert address
        address = self._address_to_baddress(message.address)

        # Run any modifiers
        for mod in self.modifiers:
            message.payload = mod.ingress(message.payload, message.channel, address)

        # Create the reception object
        reception = Reception(message.payload, message.transport, message.channel, address)

        # Emit
        self.incoming.on_next(reception)


    def send(self, data: bytes, transport, peer: BinaryAddress, channel: bytes = b"\x00"*16):
        # Get the transport id
        trans = self._get_transport_identifier(transport)

        # Run any modifiers
        for mod in self.modifiers:
            data = mod.egress(data, channel, peer)

        # Convert LibPeer binary address to LibPeerUnix Address
        addr = self._baddress_to_address(address)

        # Create the message object
        message = Message(addr, data, channel, trans)

        # Send the message
        self.system.send(message)

    
    def add_label(self, label: bytes):
        self.system.add_label(label)


    def remove_label(self, label: bytes):
        self.system.remove_label(label)

    
    def clear_labels(self):
        self.system.clear_labels()


    def set_discoverable(self, discoverable: bool):
        self.system.set_discoverable(discoverable)


    def close(self):
        self.close()


    def find_peers(self):
        return [DiscoveryInformation(p, self._address_to_baddress(p.address)) for p in self.get_peers()]


    def find_peers_with_label(self, label: bytes):
        return [DiscoveryInformation(p, self._address_to_baddress(p.address)) for p in self.get_labeled_peers(label)]


    def add_modifier(self, modifier: Modifier):
        self.modifiers.append(modifier)


    def _baddress_to_address(self, baddress: BinaryAddress) -> Address:
        label = baddress.label or b""
        return Address(baddress.network_type, baddress.network_address, baddress.network_port, label)


    def _address_to_baddress(self, address: Address) -> BinaryAddress:
        return BinaryAddress(address.protocol, address.address, address.port, self.namespace, address.label)