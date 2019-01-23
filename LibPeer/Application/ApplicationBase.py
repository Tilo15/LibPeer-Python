from LibPeer.Formats.BinaryAddress import BinaryAddress
from LibPeer.Modifiers import Modifier
from LibPeer.Application.Preferences import TransportPreferences
from LibPeer.Application.DiscoveryInformation import DiscoveryInformation
from LibPeer.Application.SystemInformation import *

import rx

class ApplicationBase:
    def __init__(self, namespace: bytes):
        # Save the namespace
        self.namespace = namespace

        # Create subjects
        self.incoming = rx.subjects.Subject()
        self.new_peer = rx.subjects.Subject()

        # Set up information properties
        self.networks = []
        self.transports = []
        self.discoverers = []


    def send(self, data: bytes, transport, peer: BinaryAddress, channel: bytes = b"\x00"*16):
        raise NotImplementedError

    
    def add_label(self, label: bytes):
        raise NotImplementedError


    def remove_label(self, label: bytes):
        raise NotImplementedError

    
    def clear_labels(self):
        raise NotImplementedError


    def set_discoverable(self, discoverable: bool):
        raise NotImplementedError


    def close(self):
        raise NotImplementedError


    def find_peers(self):
        raise NotImplementedError


    def find_peers_with_label(self, label: bytes):
        raise NotImplementedError

    
    def add_modifier(self, modifier: Modifier):
        raise NotImplementedError


    def _get_transport_identifier(self, transport) -> bytes:
        trans_id = None

        if(type(transport) == TransportPreferences):
            trans_id = transport._tid

        elif(type(transport) == str):
            for trans in self.transports:
                if(trans.name == transport):
                    trans_id = trans.identifier

        elif(type(transport) == bytes):
            trans_id = transport

        if(trans_id):
            return trans_id

        else:
            raise IOError("Unable to find requested transport")