from LibPeer.Formats.BinaryAddress import BinaryAddress
import rx

class Network:
    identifier = b""

    def __init__(self, options: dict):
        self.options = options
        self.available = False
        self.incoming = rx.subjects.Subject()
        self.up = False

    def go_up(self) -> bool:
        """Attempt to get the network ready to used. Returns true on success"""
        raise NotImplementedError

    def go_down(self,):
        """Shut down the network interface"""
        raise NotImplementedError

    def send(self, data: bytes, address: BinaryAddress) -> rx.Observable:
        """Send the specified data to the specified address"""
        raise NotImplementedError

