import imaplib, smtplib, email, pt_util, collections, time, pt_data
from email.mime.text import MIMEText

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
    smtps = {'gmail.com':('smtp.gmail.com', 587), 'smtp.aol.com':('smtp.aol.com', 587), 'yahoo.com':('smtp.mail.yahoo.com', 587)}

    status = ''
    imap = None
    smtp = None

class msg:
    def __init__(self, text, address, uid, sent):
        'Message body, sender address (converted to phone #), UID, and 1 for sent or 0 for received'
        self.text = text
        self.number = address.rpartition('@')[0]
        self.uid = uid
        self.sent = sent

    def __str__(self):
        return self.text

    def tuple(self):
        return (self.uid, self.number, self.text, self.sent)





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
    if var.smtp != None:
        var.smtp.quit()
    if var.imap != None:
        var.imap.logout()

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
    imapHost = var.imaps.get(at, False)
    smtpHost = var.smtps.get(at, False)
    if not imapHost:
        mainQ.mailException('Unable to determine IMAP host')
        return
    if not smtpHost:
        mainQ.mailException('Unable to determine SMTP host')
        return
    #we need smtp connection AND imap connection. good times
    ttls = True
    try:
        var.smtp = smtplib.SMTP(smtpHost[0], smtpHost[1])
        try:
            var.smtp.starttls()
        except Exception:
            ttls = False
        var.smtp.ehlo()
        var.smtp.login(account, password)
    #except smtplib.SMTPException as e:
    except Exception as e:
        mainQ.mailException(str(e))
        return
    try:
        var.imap = imaplib.IMAP4_SSL(imapHost)
        var.imap.login(account, password)
        var.status, msgs = var.imap.select('INBOX')
    #except imaplib.IMAP4.error as e:
    except Exception as e:
        mainQ.mailException(str(e))
        return
    if check(): #logon successful
        pt_data.internal.var.currentAccount = account
        #mainQ.instruction(logon)
        mainQ.append((logon, ttls))

def logout():
    var.imap.close()
    var.imap.logout()
    var.smtp.quit()
    var.imap = None
    var.smtp = None
    mainQ.instruction(logout)
    #if var.status != 'BYE':
    #   mainQ.mailException(var.status)


def mail(text, number, provider):
    #TODO: this needs to handle breaking messages up into multiple numbered texts if necessary
    #remember the counting algorithm has to be dynamic to include possible counts of numbering characters too
    to = number+var.addresses[provider][0]
    From = pt_data.internal.var.currentAccount
    message = MIMEText(text)
    message['From'], message['To'], message['subject'] = From, to, ''
    var.smtp.send_message(message)


def fetchAll():

    list = addressesList()
    searchString = 'or '*(len(list)-1)
    for item in list:
        searchString += ('FROM "' + item +'" ')
    searchString = searchString.strip()+' UID '+str(pt_data.internal.var.lastFetch+1)+':*' 
    #IMPORTANT: IMAP ranges are inclusive, so it's at least one greater than the lastFetch's UID
    var.status, data = var.imap.UID('search', None, searchString)
    if data == [b'']: return #IF DATA IS EMPTY, RETURN HERE
    check()
    fetch = ''
    list = data[0].decode().split(" ")
    for d in list:
        fetch+= d+','
    fetch = fetch.strip(',')
    var.status, texts = var.imap.UID('fetch', fetch, '(RFC822)')
    results = []
    for a in texts:
        ms = parseEmail(a)
        #file.write(str(a))
        if ms:
            results.append(ms)
            #print(ms.sender+' '+ms.uid)
            #print(re.items())
        else:
            pass
            #parse the possible values of other parts of the list; seen so far is b')' and b' FLAGS (\\Seen))'

    pt_data.save_messages(results)
    mainQ.append((fetchAll, results))
    #TODO IMPORTANT - pass messages to gui thread somehow, probably drop them in queue tagged messagelist
    #also, probably want to log when we get new message from someone, whether their contact frame is open or not
    #print(fetch)

def parseEmail(emailTuple):
    if isinstance(emailTuple, tuple):
        #get uid by searching for "UID" and then getting the next word
        metadata = emailTuple[0].decode().split(' ')
        for x in range(0, len(metadata)):
            if metadata[x].find('UID')!=-1:
                uid = metadata[x+1]
        mail = email.message_from_bytes(emailTuple[1])
        print(mail['Date'])
        for part in mail.walk():
            if part.get_content_type()=='text/plain':
                text = part.get_payload().strip()
                break
        return msg(text, mail['From'], uid, 0)
    else: return False