

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

    def serialise(self):
        data = b"\x01%b" % self.application

        if(self.label):
            data += b"\x2F%b" % self.label

        else:
            data += b"\x02"

        data += b"%b\x1F%b\x1F%b\x04" % (self.network_type, self.network_address, self.network_port)
        return data
    

    @staticmethod
    def deserialise(data: bytes):
        if(data[0:1] != b"\x01"):
            raise TypeError("Data is not a Binary Address")

        app = b""
        label = None
        network = b""
        address = b""
        port = b""


        if(b"\x02" not in data):
            # Has label
            app, data = data[1:].split(b"\x2F", 1)
            label = data[1]

        else:
            app, data = data[1:].split(b"\x02", 1)
        

        network, data = data.split(b"\x1F", 1)
        address, data = data.split(b"\x1F", 1)
        port = data.split(b"\x04", 1)[0]

        return BinaryAddress(network, address, port, app, label)


    def __hash__(self):
        return hash((self.network_type, self.network_address, self.network_port))

    def __eq__(self, other):
        return self.network_type == other.network_type and self.network_address == other.network_address and self.network_port == other.network_port


            

        
