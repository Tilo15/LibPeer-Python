from LibPeer.Formats.BinaryAddress import BinaryAddress

import rx

class Discoverer:
    def __init__(self, networks: list):
        """Initialise the discoverer"""
        self.discovered = rx.subjects.Subject()
        self.networks = {}

        # Create dict
        for network in networks:
            self.networks[network.identifier] = network
            

    def advertise(self, address: BinaryAddress) -> int:
        """Returns the recommended time in seconds to wait before re-advertising"""
        raise NotImplementedError

    def add_application(self, namespace: bytes):
        """Add an application namespace to discover"""
        raise NotImplementedError

    def remove_aplication(self, namespace: bytes):
        """Stop discovering an application namespace"""
        raise NotImplementedError

    def get_addresses(self) -> list:
        """Get a list of addresses that peers claim to see us as"""
        raise NotImplementedError

    def stop(self):
        """Stop the discoverer"""
        raise NotImplementedError
