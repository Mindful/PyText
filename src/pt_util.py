from collections import deque
import string


class msg:
    def __init__(self, text, address, uid, date, sent, format = True):
        'Message body, sender address (converted to phone #), UID, and 1 for sent or 0 for received'
        self.text = text
        if format:
            self.number = address.rpartition('@')[0]
        else:
            self.number = address
        if uid:
            self.uid = int(uid)
        self.sent = sent
        self.date = date

    def __str__(self):
        return self.text

    def tuple(self):
        return (self.uid, self.date, self.number, self.text, self.sent)

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
        self.numDict = {}

    def __getitem__(self, index):
        if type(index) == int:
            return self.list[index]
        elif type(index) == str:
            return self.dict[index]
        else: raise LookupError("Contact must be accessed by name or index")

    def withNumber(self, num):
        'Returns contact with that number, or the number itself if the contact does not exist.'
        res = self.numDict.get(num, False)
        if res: return res
        return num

    def __delitem__(self, index):
        if type(index) == int:
            item = self.list[index]
            del self.dict[item.name]
            del self.numDict[item.number]
            del self.list[index]
        elif type(index) == str:
            item = self[index]
            self.list.remove(item) #This must come first because we are using the dict to fetch the item
            del self.numDict[item.number]
            del self.dict[index]
            #search for and remove from string

    def __len__(self):
        return len(self.list)

    def __contains__(self, item):
        'Searches for the contact by name, not object reference'
        return item in self.dict.keys()

    def invalidAdd(self, name, number):
       '''Checks for duplicate names or numbers. Returns False if addition is valid, else "name" for invalid name and
       the name of the duplicate if the number is invalid'''
       for item in self.list:
           if item.name == name: return 'name'
           if item.number == number: return item.name
       return False

    def fromList(self, list):
        self.list = sorted(list)
        for item in self.list:
            self.dict[item.name]=item
            self.numDict[item.number]=item

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
        self.numDict[number]=contact
        return lo #This must return the index it inserts at, so we know where to place items in the treeview



