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
    #searchString = ('or '*(len(list)-1))
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
    #print(fetch)
    var.status, texts = var.mail.UID('fetch', fetch, '(RFC822)')
    #print(texts) #this is what's being called; we should stop that
    #print('<>')
    #print(texts)
    file = open('mail.txt', 'w')
    #print((texts))
    for a in texts:
        if isinstance(a, tuple): #this is to test if it's am email; otherwise it's a single informative bytestring
            #print(a[1])
            re = email.message_from_bytes(a[1])
            file.write(str(re.items())+'\n\n')
            #print(re.items())
        else:
            pass
            #parse the possible values of other parts of the list; seen so far is b')' and b' FLAGS (\\Seen))'

    file.close()
    print(fetch)
    pt_data_internal.var.lastFetch = fetchTime
            
    #raw_email = email.message_from_bytes(texts[0][1])
    #print(raw_email['From'])