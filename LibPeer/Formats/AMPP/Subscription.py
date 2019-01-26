import uuid
import msgpack

class Subscription:
    def __init__(self, apps: list, renewing: bool, sid: uuid.UUID = uuid.uuid4()):
        self.subscriptions = apps
        self.id = sid
        self.renewing = renewing


    def serialise(self):
        return msgpack.packb({
            b"subscriptions": self.subscriptions,
            b"id": self.id.bytes,
            b"renewing": self.renewing
        })


    @staticmethod
    def deserialise(data: bytes):
        message = msgpack.unpackb(data)
        return Subscription(message[b"subscriptions"], message[b"renewing"], uuid.UUID(bytes=message[b"id"]))