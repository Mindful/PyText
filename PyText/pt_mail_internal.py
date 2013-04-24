import imaplib, email, pt_util, collections, time, pt_data_internal

q = pt_util.fq()

mainQ = None
running = True

class var: #there are more addresses; like vzwpix.com, stuff for multimedia messages TODO
    #SOMETHING HAPPENS DIFFERENTLY WHEN PARSING UNREAD EMAILS; I'M GETTING DIFFERENTLY FORMATTED RESULTS


    #simple/send-to addresses should always be first in the tuple for the sake of consistency
    addresses = collections.OrderedDict((('sprint',('@messaging.sprintpcs.com','@pm.sprint.com')),
        ('verizon',('@vtext.com','@vzwpix.com')),
        ('t-mobile', ('@tmomail.net',)), #only one, as far as I can see
        ('at&t', ('@txt.att.net','@mms.att.net')),
        ('virgin mobile', ('@vmobl.com','@vmpix.com')),
        ('us cellular', ('@email.uscc.net','@mms.uscc.net')),
        ('nextel', ('@page.nextel.com', '@messaging.nextel.com')), #test @page.nextel. also this is sprint/nextel, not pure nextel
        ('boost', ('@myboostmobile.com',)), #only one, as far as I can see
        ('alltel', ('@message.alltel.com','@mms.alltel.net')))) #this is verizon/alltell, not pure alltell. second address may be redundant

    imaps = {'gmail.com':'imap.gmail.com', 'yahoo.com':'imap.mail.yahoo.com', 'aol.com':'imap.aol.com'}

    status = ''
    mail = None

class msg:
    def __init__(self, text, sender, uid):
        self.text = text
        self.sender = sender
        self.uid = uid

    def __str__(self):
        return self.text

    def tuple(self):
        return (self.uid, self.sender, self.text)





def addressesList():
    r = []
    for key in var.addresses:
        for item in var.addresses[key]:
            r.append(item)

    return r


def init():
    #any mail initialization code goes here
    while running:
        if len(q) > 0:
            q.run()

def terminate():
    global running
    running = False

def check():
    if var.status != 'OK':
       mainQ.mailException(var.status)
       return False
    else:
        return True


def logon(account, password):
    if account == '':
        mainQ.mailException('Must enter an account')
        return
    elif password =='':
        mainQ.mailException('Must enter a password')
        return
    at = account.rpartition('@')[2]
    if at in var.imaps:
        host = var.imaps[at]
    else:
        mainQ.mailException('Unable to determine host')
        return
    try:
        var.mail = imaplib.IMAP4_SSL(host)
        var.mail.login(account, password)
        var.status, msgs = var.mail.select('INBOX')
    except Exception as e:
        mainQ.mailException(str(e))
        return
    if check(): #logon successful
        fetchAll()
        mainQ.instruction(logon)

def logout():
    var.mail.close()
    var.mail.logout()
    mainQ.instruction(logout)
    #if var.status != 'BYE':
    #   mainQ.mailException(var.status)




def fetchAll():
    #fetchTime = imaplib.Time2Internaldate(time.time()).strip('"')
    #fetchTime = fetchTime[:fetchTime.find(" ")]

    fetchTime = "1-Nov-2009"

    list = addressesList()
    searchString = 'or '*(len(list)-1)
    for item in list:
        searchString += ('FROM "' + item +'" ')
    searchString = searchString.strip()+' SINCE '+ fetchTime
    print(searchString)
    var.status, data = var.mail.UID('search', None, searchString)
    if data == [b'']: return #IF DATA IS EMPTY, RETURN HERE
    check()
    fetch = ''
    list = data[0].decode().split(" ")
    for d in list:
        fetch+= d+','
    fetch = fetch.strip(',')
    var.status, texts = var.mail.UID('fetch', fetch, '(RFC822)')
    file = open('mail.txt', 'w')
    for a in texts:
        ms = parseEmail(a)
        #file.write(str(a))
        if ms:
            print(ms.sender+' '+ms.uid)
            file.write(str(ms.text)+'\n\n')
            #print(re.items())
        else:
            pass
            #parse the possible values of other parts of the list; seen so far is b')' and b' FLAGS (\\Seen))'

    file.close()
    print(fetch)
    if pt_data_internal.var.lastFetch != fetchTime:
        pt_data_internal.var.lastFetch != fetchTime
        #reset the log of messages we've already fetched from today
    else:
        pass
        #add the fetched messages to the log of messages we've already fetched from today

def parseEmail(emailTuple):
    if isinstance(emailTuple, tuple):
        #get uid by searching for "UID" and then getting the next word
        metadata = emailTuple[0].decode().split(' ')
        for x in range(0, len(metadata)):
            if metadata[x].find('UID')!=-1:
                uid = metadata[x+1]
        mail = email.message_from_bytes(emailTuple[1])
        for part in mail.walk():
            if part.get_content_type()=='text/plain':
                text = part.get_payload().strip()
                break
        return msg(text, mail['From'], uid)
    else: return False