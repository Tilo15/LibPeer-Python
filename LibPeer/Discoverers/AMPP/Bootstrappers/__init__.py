import rx

class Bootstrapper:
    def __init__(self, networks):
        self.discovered = rx.subjects.Subject()

    def stop(self):
        raise NotImplementedError