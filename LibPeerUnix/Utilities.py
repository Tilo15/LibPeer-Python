from LibMedium.Medium.Listener.Application import Application
from LibMedium.Util.Defer import Defer
from LibPeerUnix.Exceptions import DataError
from LibPeerUnix.Models import Peer as PeerModel
from LibPeerUnix.Models import Address
from LibPeer.Formats.BinaryAddress import BinaryAddress
from LibPeer.Transports import Transport

import threading
import time

class LabelCollection:
    def __init__(self):
        self.labels = set()
        self.lock = threading.Lock()

    def add_label(self, label: bytes):
        if(len(label) != 32):
            raise DataError("Peer labels must be exactly 32 bytes, not %i byte(s)" % len(label))

        with self.lock:
            self.labels.add(label)

    def remove_label(self, label: bytes):
        with self.lock:
            if(label in self.labels):
                self.labels.remove(label)

    def clear_labels(self):
        with self.lock:
            self.labels.clear()

class PeerLabel:
    def __init__(self, label: bytes):
        self.label = label
        self.last_seen = time.time()

    def seen(self):
        self.last_seen = time.time()

    def expired(self):
        # Expire a label after four mins
        return self.last_seen > time.time() - 240


class Peer:
    def __init__(self, address: BinaryAddress, ad: int):
        self.address = address
        self.administrative_distance = ad
        self.last_seen = time.time()
        self.labels = {}
        self.lock = threading.Lock()

        if(address.label != None):
            self.labels[address.label] = PeerLabel(address.label)

    def seen(self, label: bytes):
        if(label != None):
            with self.lock:
                if(label in self.labels):
                    self.labels[label].seen()

                else:
                    self.labels[label] = PeerLabel(label)

        self.last_seen = time.time()
    
    def get_labels(self):
        with self.lock:
            return [l for l in self.labels if not l.expired()]

    def get_model(self) -> PeerModel:
        label = b""
        if(self.address.label):
            label = self.address.label

        address = Address(self.address.network_type, self.address.network_address, self.address.network_port, label)
        return PeerModel(self.administrative_distance, self.last_seen, address)

    def has_label(self, label: bytes):
        with self.lock:
            for l in self.labels:
                if(l.label == label and not l.expired()):
                    return True
        
            return False



class PeerCollection:
    def __init__(self):
        self.peers = {}
        self.lock = threading.Lock()

    def found_peer(self, address: BinaryAddress, ad: int) -> Peer:
        with self.lock:
            # Do we have this peer?
            if(address in self.peers):
                # Update last seen
                self.peers[address].seen(address.label)

            else:
                # We need to add the peer
                self.peers[address] = Peer(address, ad)

            # Return the peer object
            return self.peers[address]

    def get_peer_models(self):
        with self.lock:
            return [p.get_model() for p in self.peers.values()]

    def get_peer_models_with_label(self, label: bytes):
        with self.lock:
            return [p.get_model() for p in self.peers.values() if p.has_label(label)]


class TransmitItem:
    def __init__(self, transport: Transport, data: bytes, channel: bytes, address: bytes, defer: Defer, priority: int):
        self.transport = transport
        self.data = data
        self.channel = channel
        self.address = address
        self.defer = defer
        self.priority = priority
        self.timestamp = time.time()

        if(len(self.channel) != 16):
            raise DataError("Channel must be exactly 16 bytes")

    def execute(self):
        self.transport.send(self.data, self.channel, self.address).subscribe(
            lambda res: self.defer.complete(res),
            lambda err: self.defer.error(LibPeerUnix.Exceptions.NetworkError(str(err)))
        )

    def __lt__(self, other):
        return self.priority < other.priority or self.timestamp < other.timestamp

    def __eq__(self, other):
        return self.priority == other.priority and self.timestamp == other.timestamp

    def __gt__(self, other):
        return self.priority > other.priority or self.timestamp > other.timestamp