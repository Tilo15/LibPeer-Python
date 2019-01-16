

class BinaryAddress:
    def __init__(self, network_type: bytes, network_address: bytes, network_port: bytes, application: bytes = None, label: bytes = None):
        self.application = application
        self.network_type = network_type
        self.network_address = network_address
        self.network_port = network_port
        self.label = label

    def __str__(self):
        out = b"%s[" % self.network_type
        if(self.application):
            out += b"%s://" % self.application

        out += b"%s:%s" % (self.network_address, self.network_port)
        if(self.label):
            out += b"/%s" % self.label

        out += b"]"

        return out.decode("utf-8")
    
