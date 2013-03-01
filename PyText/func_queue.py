from collections import deque

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
    def __init__(self):
        self.resolving = None
        self.commands = {'genericFunction': genericFunction, 'mailException': mailException, 
                         'dataException': dataException, d.internal.load_contacts: populateContacts,
                         m.internal.logon: var.l.saveLogon, m.internal.logout: mainLogout }

    def add(self, func):
        func = ('genericFunction', func)
        if not func == self.resolving:
            self.append(func)

    def run():
        self.resolving = self.popleft()
        self.commands[resolving[0]](resolving[1])
        self.resolving = None

    def mailException(error):
        self.append(('mailException', mailException(error)))

    def dataException(error):
        self.append(('dataException',dataException(error)))

    def insturction(instruction):
        mainQ.append((instruction, None))