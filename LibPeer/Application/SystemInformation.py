
class TransportInformation:
    def __init__(self, name: str, identifier: bytes):
        self.name = name
        self.identifier = identifier

class NetworkInformation:
    def __init__(self, name: str, identifier: bytes, active: bool):
        self.name = name
        self.identifier = identifier
        self.active = active

class DiscovererInformation:
    def __init__(self, name: str):
        self.name = name