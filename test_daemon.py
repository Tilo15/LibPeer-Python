from LibPeerUnix import LibPeerUnixConnection
from LibPeerUnix.Models import *

libpeer = LibPeerUnixConnection()

print("Connected to Daemon!")
print("Available discoverers:")
for d in libpeer.available_discoverers():
    print("\t%s" % d)
print()
print("Available networks:")
for n in libpeer.available_networks():
    if(n.active):
        print("\t[ ACTIVE ] %s" % n.name)
    else:
        print("\t[INACTIVE] %s" % n.name)
print()

transport_names = {}
print("Available transports:")
for t in libpeer.available_transports():
    print("\t%s" % t.name)
    transport_names[t.protocol] = t.name
print()


peers = []
def new_peer(args):
    peer: Peer = args[0]
    # print("--------")
    # print("Found peer %s://%s:%s with AD of %i" % (peer.address.protocol.decode("utf-8"), peer.address.address.decode("utf-8"), peer.address.port.decode("utf-8"), peer.administrative_distance))
    peers.append(peer)

# Subscribe to new peer discoveries
libpeer.new_peer.subscribe(new_peer)

def new_message(args):
    message: Message = args[0]
    print("--------")
    print("Got message: %s\nFrom: %s://%s:%s, via transport: %s" % (message.payload.decode("utf-8"), message.address.protocol.decode("utf-8"), message.address.address.decode("utf-8"), message.address.port.decode("utf-8"), transport_names[message.transport]))

# Subscribe to new messages
libpeer.receive.subscribe(new_message)

# Bind to the app namespace
libpeer.bind(b"helloworld")
print("Bound to 'helloworld'")

libpeer.set_discoverable(True)
print("Enabled discovery")

libpeer.add_label(b"yeet" * 8)
print("Added label")

libpeer.remove_label(b"yeet" * 8)
print("Removed label")

libpeer.add_label(b"yeet" * 8)
print("Added label")

libpeer.clear_labels()
print("Cleared labels")

libpeer.add_label(b"yeet" * 8)
print("Added label")

while True:
    print()
    msg = input("Type your message at any time\n")
    
    print()
    peers = libpeer.get_peers()
    print("Got peers")

    for peer in peers:
        if(peer.administrative_distance != 0):
            try:
                libpeer.send(Message(peer.address, msg.encode("utf-8"), b"\x00"*16, b"\x06"))
                print("Sent to IP %s" % str(peer.address.address))
            except Exception as e:
                print("Failed to send to %s: %s" % (str(peer.address.address), str(e)))

    