import imaplib, smtplib, email, pt_util, collections, time, email.parser as parse, pt_data, re, quopri
from email.mime.text import MIMEText

q = pt_util.fq()


mainQ = None
running = True

class var: 

    #Addresses for each of the providers. This needs to be comprehensive to catch incoming messages properly.
    #Simple/send-to addresses should always be first in the tuple for the sake of consistency
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
    def __init__(self, text, address, uid, date, sent):
        'Message body, sender address (converted to phone #), UID, and 1 for sent or 0 for received'
        self.text = text
        self.number = address.rpartition('@')[0]
        self.uid = uid
        self.sent = sent
        self.date = date

    def __str__(self):
        return self.text

    def tuple(self):
        return (self.uid, self.date, self.number, self.text, self.sent)





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
    var.status, data = var.imap.UID('search', None, searchString)
    if data == [b'']: return #If there's nothing to fetch, return here
    check()
    fetch = ''
    list = data[0].decode().split(" ")
    for d in list:
        fetch+= d+','
    fetch = fetch.strip(',')
    var.status, texts = var.imap.UID('fetch', fetch, '(INTERNALDATE BODY[1] BODY[HEADER.FIELDS (FROM)])')
    results = parseEmails(texts) #Is it safe to pass the same list reference to these two separate functions?
    pt_data.save_messages(results) #Save newly retrieved messages
    mainQ.append((fetchAll, results)) #Log newly retreived messages


def parseEmails(emailList):
    ret = []
    x = 0
    max = len(emailList)
    while x < max:
        m = emailList[x]
        if isinstance(m, tuple):
            #Parse the metadata
            metadata = m[0].decode()
            uidLoc = metadata.find('UID ')+4 #Length 4, so we add 4 to look afterwards
            uid = metadata[uidLoc:metadata.find(' ', uidLoc)]
            internaldateLoc = metadata.find('INTERNALDATE ') #No +i here, we want to include 'INTERNALDATE' for parsing puposes
            internaldate = metadata[internaldateLoc: metadata.find('" ')+1] #We want the space after the ", so we add 1
            date = int(time.mktime(imaplib.Internaldate2tuple(internaldate.encode()))) #Internaldate->timetuple->float->int
            #Compose the actual email
            p1 = m[1] #Get the headers
            x = x+1
            p2 = emailList[x][1] #Get the first part of the body (only part we fetch)
            header = parse.BytesHeaderParser().parsebytes(p1)
            if b'<html>' == p2[0:6]:
                text = decodeAndStrip(p2)
            else: 
                text = p2.decode()
            print(text, header['From'], uid, date, 0)
            ret.append(msg(text, header['From'], uid, date, 0))
        x = x+1 #This is the normal loop increment
    return ret


def decodeAndStrip(bytes):
    #Source: http://www.codigomanso.com/en/2010/09/truco-manso-eliminar-tags-html-en-python/
    #Modified to also handle quoted-printables
    
    text = quopri.decodestring(bytes).decode()
    # apply rules in given order!
    rules = [
    { r'>\s+' : u'>'},                  # remove spaces after a tag opens or closes
    { r'\s+' : u' '},                   # replace consecutive spaces
    { r'\s*<br\s*/?>\s*' : u'\n'},      # newline after a <br>
    { r'</(div)\s*>\s*' : u'\n'},       # newline after </p> and </div> and <h1/>...
    { r'</(p|h\d)\s*>\s*' : u'\n\n'},   # newline after </p> and </div> and <h1/>...
    { r'<head>.*<\s*(/head|body)[^>]*>' : u'' },     # remove <head> to </head>
    { r'<a\s+href="([^"]+)"[^>]*>.*</a>' : r'\1' },  # show links instead of texts
    { r'[ \t]*<[^<]*?/?>' : u'' },            # remove remaining tags
    { r'^\s+' : u'' }                   # remove spaces at the beginning
    ]
 
    for rule in rules:
        for (k,v) in rule.items():
            regex = re.compile (k)
            text  = regex.sub (v, text)
 
    # replace special strings
    special = {
    '&nbsp;' : ' ', '&amp;' : '&', '&quot;' : '"',
    '&lt;'   : '<', '&gt;'  : '>'
    }
 
    for (k,v) in special.items():
        text = text.replace (k, v)
 
    return text

