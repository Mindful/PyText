import imaplib, email, queue, collections

q = queue.deque()

mainQ = None
running = True

class var:
    addresses = collections.OrderedDict((('sprint','@messaging.sprintpcs.com'),
        ('verizon','@vtext.com'),
        ('t-mobile', '@tmomail.net'),
        ('at&t', '@txt.att.net'),
        ('virgin mobile', '@vmobl.com'),
        ('us cellular', '@email.uscc.net'),
        ('nextel', '@messaging.nextel.com'),
        ('boost', '@myboostmobile.com'),
        ('alltel', '@message.alltel.com')))

    imaps = {'gmail.com':'imap.gmail.com', 'yahoo.com':'imap.mail.yahoo.com', 'aol.com':'imap.aol.com'}

    status = ''
    mail = None

class mailException(Exception):
    def __init__(self, error):
        self.error = error.strip("b'")
    def __str__(self):
        return repr(self.error)


def mainExcept(error):
    mainQ.append(('mailException', mailException(error)))

def mainEnqueue(func, type = 'genericFunction'):
    mainQ.append((type, func))

def mainInstruction(instruction, value = None):
    mainQ.append((instruction, value))

def init():
    #any mail initialization code goes here
    while running:
        if len(q) > 0:
            q.popleft()()

def terminate():
    global running
    running = False

def check():
    if var.status != 'OK':
       mainExcept(var.status)
       return False
    else:
        return True


def logon(account, password):
    if account == '':
        mainExcept('Must enter an account')
        return
    elif password =='':
        mainExcept('Must enter a password')
        return
    at = account.rpartition('@')[2]
    if at in var.imaps:
        host = var.imaps[at]
    else:
        mainExcept('Unable to determine host')
        return
    try:
        var.mail = imaplib.IMAP4_SSL(host)
        var.mail.login(account, password)
        var.status, msgs = var.mail.select('INBOX')
    except Exception as e:
        mainExcept(str(e))
        return
    if check():
        mainInstruction(logon)

def logout():
    var.mail.close()
    var.mail.logout()
    mainInstruction(logout)
    #if var.status != 'BYE':
    #   mainExcept(var.status)




def fetchAll():
    searchString = 'or '*(len(var.addresses)-1)
    for key in var.addresses:
        searchString += ('FROM "' + var.addresses[key] +'" ')
    searchString = searchString.strip()
    var.status, data = var.mail.UID('search', None, searchString)
    check()
    fetch = ''
    for d in data:
        fetch+= d.decode()+','
    fetch = fetch.strip(',')
    print(fetch)
    var.status, texts = var.mail.UID('fetch', fetch, '(RFC822)')
    print(texts) #this is what's being called; we should stop that
    print('<>')
    raw_email = email.message_from_bytes(texts[0][1])
    print(raw_email['To'])