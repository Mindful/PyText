import sqlite3, os, base64, func_queue, json

q = func_queue.fq() 

mainQ = None
running = True

class var: #python's core classes are supposedly threadsafe in cPython, so I should be able to just read/write this from the main thread
    settings = {'save_account':'1', 'save_password':'1', 'default_account':'', 'confirmation_windows':'1'} 
    accounts ={} #'accountName': settings //note that settings should include password as its FIRST value
    contacts = {'Josh': ('5103263431','verizon','1'), 'Robert':('5554443333','dunno','1'), 'Kalex':('1234567890','dunno','0')} 

    fileName = 'settings.pt'
    file = None

class dataException(Exception):
    def __init__(self, error):
        self.error = error
    def __str__(self):
        return repr(self.error)

def encode64_dict(dict):
    newDict = {}
    for key in dict:
        newDict[key] = base64.b64encode(dict[key].encode())
    return newDict
    

def decode64_dict(dict):
    newDict = {}
    for key in dict:
        newDict[key] = base64.b64decode(dict[key]).decode()
    return newDict


def encode64_string(string):
    return base64.b64encode(string.encode())


def decode64_string(string):
    return base64.b64decode(string).decode()



def init(mainVar):
    build = not os.path.exists(var.fileName)
    var.file = sqlite3.connect(var.fileName)
    var.file.row_factory = sqlite3.Row #so info is returned as dicts
    if build:
        var.file = sqlite3.connect(var.fileName)
        cur = var.file.cursor()
        cur.execute("BEGIN") #this makes it all one action, and saves a decent amount of overhead
        cur.execute("CREATE TABLE accounts (account TEXT, password TEXT, contacts TEXT, UNIQUE(account))") #no duplicate accounts
        cur.execute("CREATE TABLE settings (setting TEXT, value TEXT, UNIQUE(setting))")
        cur.execute("CREATE TABLE mail (uid INTEGER PRIMARY KEY ASC, sender TEXT, recipient TEXT, message TEXT)") #this must be ascending; descending primary keys just don't work apparently
        #sorting by rowids is much faster, and there could be a LOT of messages, so the above uses a primary key
        cur.executemany("INSERT INTO settings VALUES (?, ?)", list(var.settings.items()))
        var.file.commit()
    load()
    l = mainVar.l
    l.account_string.set(var.settings['default_account'])
    l.password_string.set(var.accounts.get(var.settings['default_account'],''))
    if l.account_string.get() != '' and l.password_string.get() != '':
        l.login()
    while running:
        if len(q) > 0:
            q.run()

def terminate():
    global running
    running = False
    

def save_account(account, password, favorites):
    cur = var.file.cursor()
    cur.execute("BEGIN")
    cur.execute("INSERT OR IGNORE INTO accounts VALUES (?, ?, ?)", (account, '', '{}'))
    if password:
        cur.execute("UPDATE accounts SET password=? WHERE account=?", (encode64_string(password,), account))
    else:
        cur.execute("UPDATE accounts SET password=? WHERE account=?", (b'', account))
    if favorites:
        pass #I think here, use json to turn a list of  into a string and then save it like that. probably
    var.file.commit()
    

def load_contacts(account): 
    cur = var.file.cursor()
    cur.execute("SELECT * FROM accounts WHERE account=?", (account,)) #must be a tuple, even if there is only one value
    a = cur.fetchone() #this is returning a tuple instead of a dictionary
    var.contacts = json.loads(a[2]) #note this overrides defaults, makes testing hard
    mainQ.instruction(load_contacts)
    #list = cur.fetchmany() #THIS RETURNS A LIST OF SQLITE OBJECTS, WHICH ARE DICTS
    #print(list)
    #print(list[0]['account']) 

def save_contacts(account):
    cur = var.file.cursor()
    cur.execute("UPDATE accounts SET contacts=? WHERE account=?", (json.dumps(var.contacts), account))
    var.file.commit()


def save_settings():
    cur = var.file.cursor()
    #list([[v,k] for k,v in encode64_dict(var.settings).items()]) is inverting the dict and making it a list,
    #since in this case, it's value, setting (instead of the norm setting, value)
    cur.executemany("UPDATE settings SET value=? WHERE setting=?", list([[v,k] for k,v in var.settings.items()]))  
    var.file.commit()


def load():
    cur = var.file.cursor()
    cur.arraysize = 0 #no max on selected settings - ARRAYSIZE MUST BE SET TO >1 TO GET MORE THAN 1 RESULT
    cur.execute("SELECT * FROM settings")
    list = cur.fetchmany()
    for item in list:
        var.settings[item[0]] = item[1]
    cur.execute("SELECT * FROM accounts")
    list = cur.fetchmany()
    for item in list:
        var.accounts[item[0]] = decode64_string(item[1])


