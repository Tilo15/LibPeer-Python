from LibPeer.Application import Application
from LibPeer.Interfaces.SODI import SODI
from LibPeer.Interfaces.SODI.Reply import Reply
from LibPeer.Interfaces.SODI.Solicitation import Solicitation

import glob
import time
import threading
import os

# Handle solicitations
def new_solicitation(solicitation: Solicitation):
    if(solicitation.query.startswith("get ")):
        try:
            f = open(solicitation.query[4:], 'rb')
            solicitation.reply({"status": "OK"}, f)
            f.close()

        except Exception as e:
            solicitation.reply({"status": str(e)})

    else:
        files = glob.glob("ftp/**.*")
        info = {
            "motd": "This is a message of the day. Hello world!",
            "entries": []
        }

        for file in files:
            info["entries"].append({
                "path": file,
                "size": os.path.getsize(file)
            })

        solicitation.reply(info)


# Create a LibPeer app instance
app = Application("testftp")

# Get the SODI
sodi = SODI(app)

# Handle solicitations
sodi.solicited.subscribe(new_solicitation)

# Make the app visible to other peers
app.set_discoverable(True)

while True:
    # Get a list of peers
    discoveries = app.find_peers()

    # Display them
    for i, discovery in enumerate(discoveries):
        print("[%i] %s distance: %i, last seen: %i seconds ago" % (i, discovery.peer, discovery.ad, round(time.time() - discovery.last_discovered)))

    # Ask user which to connect to
    selection = input("Get listing: ")
    
    # Search again for peers
    if(selection == ""):
        continue

    # Exit
    if(selection == "#"):
        app.close()
        break

    # Get selected peer
    peer = discoveries[int(selection)].peer

    while True:

        # Lock to wait for result
        lock = threading.Lock()
        lock.acquire()

        items = []

        def process_listing(reply: Reply):
            obj = reply.get_object()
            print("Got response from %s:" % reply.peer)
            print(obj["motd"])
            # Add to array
            for item in obj["entries"]:
                items.append(item)

            # Release lock
            lock.release()

        # Print requesting message
        print("Requesting listing from %s..." % peer)

        # Ask peer for directiory listing
        sodi.solicit(peer, "listing").subscribe(process_listing)

        # Acquire lock to block until ready
        lock.acquire()

        # Format the items
        for i, item in enumerate(items):
            print("[%i] %i bytes\t%s" % (i, item["size"], item["path"]))

        # Get the selection
        selection = input("Download: ")
        
        # Reload listing
        if(selection == ""):
            continue

        # Back to peers
        if(selection == "#"):
            break

        # Get path of file
        path = items[int(selection)]["path"]

        reply = None

        def process_download(r: Reply):
            global reply
            # Save the reply
            reply = r

            # Release lock
            lock.release()

        # Display activity
        print("Requesting file %s from peer %s..." % (path, peer))

        # Download file
        sodi.solicit(peer, "get %s" % path).subscribe(process_download)

        # Wait for response
        lock.acquire()

        obj = reply.get_object()
        if(obj["status"] == "OK"):
            print("Peer accepted request")
            
            f = open("download", "wb")
            while reply.transfer_information[4] != 1:
                f.write(reply.read())
                print("Downloading %s %i%% complete..." % (path, round(reply.transfer_information[4] * 100)))

            f.close()
            print("Download complete!")

        else:
            print("Peer rejected request with status: %s" % obj["status"])