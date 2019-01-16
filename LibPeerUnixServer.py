from LibMedium.Medium.Listener.Application import Application
from LibMedium.Util.Defer import Defer
from LibPeerUnix.Server import LibPeerUnixServerBase
import LibPeerUnix.Exceptions
import LibPeerUnix.Models

class LibPeerUnixServer(LibPeerUnixServerBase):
    
    def run(self):
        # This is called when the daemon is ready to communicate. Do your background tasks in here.
        # Communication is managed in a different thread, so feel free to place your infinate loop here.
        # A set of application connections can be found at 'self.applications'.
        # All your events are available to fire off at any time using 'self.event_name(*params)'.
        # To fire an event to a single application instance, pass in the application as the last
        # paramater in the event call, eg. 'self.event_name(param1, param2, application)'
        pass
    
    
    # Below are all the method calls you will need to handle.
    def available_discoverers(self, caller: Application) -> list:
        pass
    
    
    def available_networks(self, caller: Application) -> list:
        pass
    
    
    def available_transports(self, caller: Application) -> list:
        pass
    
    
    def bind(self, caller: Application, application: bytes, local: bool):
        pass
    
    
    def set_discoverable(self, caller: Application, discoverable: bool):
        pass
    
    
    def add_label(self, caller: Application, label: bytes):
        pass
    
    
    def remove_label(self, caller: Application, label: bytes):
        pass
    
    
    def clear_labels(self, caller: Application):
        pass
    
    
    def get_peers(self, caller: Application) -> list:
        pass
    
    
    def get_labelled_peers(self, caller: Application, label: bytes) -> list:
        pass
    
    
    def send(self, caller: Application, message: LibPeerUnix.Models.Message):
        pass
    
    
    def close(self, caller: Application):
        pass
    
    
# If you run this module, it will run your daemon class above
if __name__ == '__main__':
    daemon = LibPeerUnixServer()

