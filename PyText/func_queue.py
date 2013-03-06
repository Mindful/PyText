from collections import deque

class mailException(Exception):
    def __init__(self, error):
        self.error = error.strip("b'")
    def __str__(self):
        return repr(self.error)


class dataException(Exception):
    def __init__(self, error):
        self.error = error
    def __str__(self):
        return repr(self.error)

class fq(deque):
    def __init__(self):
        self.resolving = None

    def add(self, func):
        if not func == self.resolving:
            self.append(func)

    def run(self):
        self.resolving = self.popleft()
        self.resolving()
        self.resolving = None


class main_fq(deque):
    def __init__(self, cmd):
        self.resolving = None
        self.commands = cmd

    def add(self, func):
        func = ('genericFunction', func)
        if not func == self.resolving:
            self.append(func)

    def run(self):
        self.resolving = self.popleft()
        self.commands[self.resolving[0]](self.resolving[1])
        self.resolving = None

    def mailException(self, error):
        self.append(('mailException', mailException(error)))

    def dataException(self, error):
        self.append(('dataException',dataException(error)))

    def instruction(self, instruction):
        self.append((instruction, None))