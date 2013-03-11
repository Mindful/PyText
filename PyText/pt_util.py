from collections import deque
import string

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


class ContactsList:
    def __init__(self):
        self.list = []
        self.dict = {}

    def __getitem__(self, index):
        if type(index) == int:
            return self.list[index]
        elif type(index) == string:
            return self.list[self.dict[index]]
        else: raise LookupError("Contact must be accessed by name or index")

    def __len__(self):
        return len(self.list)

    def __contains__(self, item):
        return item in self.list

    def fromList(self, list):
        #sort the list, set it to our list, and bind dictionary keys to indices
        pass

    def add(self, name, number, provider, favorited):
        contact = (number, provider, favorited, name)
        lo = 0
        hi = len(self.list) #insorting
        while lo < hi:
            mid = (lo+hi)//2
            if self.contactValue(contact) < self.list[mid]: hi = mid
            else: lo = mid +1
        self.list.insert(lo, contact)
        #TODO: UPDATE THE HASH TABLE TO REFLECT THE CHANGED INDICES (or hash directly ot items?)
        #format is (number, provider, favorited, name)
        pass

    def contactValue(self, contact):
        str = contact[3].lower()
        i = 10
        val = 0
        for c in str:
            i = i/10
            if c in string.ascii_lowercase: val = val+c/i
        if contact[2] == '1':
            val = val+100

def sortContacts(list):
    'Organizes the contats list'
    pass

def insertContact(item, list):
    'Binary searches the contact list to find the appropriate insert location'
    pass

def contactKey(c1):
    
    if c1[2] == '1':
        value = value +10
#not sure I need any of these, pything lists have built in sorting


