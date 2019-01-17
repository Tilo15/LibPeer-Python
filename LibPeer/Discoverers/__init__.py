from LibPeer.Formats.BinaryAddress import BinaryAddress

import rx

class Discoverer:
    def __init__(self, networks: list):
        """Initialise the discoverer"""
        self.discovered = rx.subjects.Subject()
        self.networks = networks

    def advertise(self, address: BinaryAddress) -> int:
        """Returns the recommended time in seconds to wait before re-advertising"""
        raise NotImplemented

    def add_application(self, namespace: bytes):
        """Add an application namespace to discover"""
        raise NotImplemented

    def remove_aplication(self, namespace: bytes):
        """Stop discovering an application namespace"""
        raise NotImplemented

    def get_addresses(self) -> list:
        """Get a list of addresses that peers claim to see us as"""
        raise NotImplemented

    def stop(self):
        """Stop the discoverer"""
        raise NotImplemented
