import rx

class ChunkTracker:
    def __init__(self, chunk_ids: list):
        self.chunk_count = len(chunk_ids)
        self.chunks = set(chunk_ids)
        self.sent = rx.subjects.Subject()
        self.complete = False

    def chunk_acked(self, chunk_id: bytes):
        # Is it one of ours?
        if(chunk_id in self.chunks):
            # Remove from set
            self.chunks.remove(chunk_id)

            # Are they all gone?
            if(len(self.chunks) == 0):
                self.complete = True
                self.sent.on_next(self.chunk_count)
                self.sent.on_completed()


    def canceled(self, reason):
        if(not self.complete):
            self.sent.on_error(IOError(reason))
            self.sent.on_completed()