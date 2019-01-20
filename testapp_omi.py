from LibPeer.Application import Application
from LibPeer.Interfaces.OMI import OMI

app = Application("omichat")

omi = OMI(app)

def new_message(info):
    message = info[0]
    peer = info[1]

    print("-" * 80)
    print(message.object["body"])
    print("From: %s at %s" % (message.object["name"], str(peer)))
    print()

omi.new_message.subscribe(new_message)
app.set_discoverable(True)

name = input("Enter your name: ")
print()

while True:
    msg = input("Type your message at any time\n")

    message = {
        "name": name,
        "body": msg
    }

    peers = app.find_peers()
    print("Found %i peers to send to" % len(peers))

    for peer in peers:
        try:
            omi.send(message, peer.peer)
            print("Sent to IP %s" % str(peer.peer))
        except Exception as e:
            print("Failed to send to %s: %s" % (str(peer.peer), str(e)))

