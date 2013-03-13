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


class Contact():
    def __init__(self, name, number, provider, favorited):
        self.name = name
        self.number = number
        self.provider = provider
        self.favorited = favorited

    def __lt__(self, other):
        if self.favorited == other.favorited:
            return self.name.lower() < other.name.lower()
        elif self.favorited == '1': 
            return True
        else: 
            return False

    def __str__(self):
        return self.name

        

class ContactsList:
    def __init__(self):
        self.list = []
        self.dict = {}

    def __getitem__(self, index):
        if type(index) == int:
            return self.list[index]
        elif type(index) == str:
            return self.dict[index]
        else: raise LookupError("Contact must be accessed by name or index")

    def __delitem__(self, index):
        if type(index) == int:
            del self.dict[self.list[index].name]
            del self.list[index]
        elif type(index) == str:
            self.list.remove(self[index]) #This must come first because we are using the dict to fetch the item
            del self.dict[index]
            #search for and remove from string

    def __len__(self):
        return len(self.list)

    def __contains__(self, item):
        'Searches for the contact by name, not object reference'
        return item in self.dict.keys()

    def fromList(self, list):
        self.list = sorted(list)
        for item in self.list:
            self.dict[item.name]=item

    def add(self, name, number, provider, favorited):
        contact = Contact(name, number, provider, favorited)
        lo = 0
        hi = len(self.list) #insorting
        while lo < hi:
            mid = (lo+hi)//2
            if contact < self.list[mid]: hi = mid
            else: lo = mid +1
        self.list.insert(lo, contact)
        self.dict[name]=contact
        return lo #This must return the index it inserts at, so we know where to place items in the treeview



