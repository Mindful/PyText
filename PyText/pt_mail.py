import pt_mail_internal as internal, threading

# This is the file for all of PyText's mail related code. PyText is IMAP-only and uses the imaplib and email libraries
#
#
#


def init(deque):
    'Starts the mail thread. Must be called before any other pt_mail functions.'
    internal.mainQ = deque
    t = threading.Thread(target = internal.init, daemon = False)
    t.start()


def terminate():
    'Ends the mail thread and calls cleanup functions'
    internal.q.add(internal.terminate)


def enqueue(func):
    'Adds a function to the pt_mail queue; best used to do something immediately after something else. MUST BE A CALLABLE FUNCTION'
    internal.q.add(func)

def logon(account, password):
    'Logs on to the target IMAP server, and removes the login interface.'
    internal.q.add(lambda: internal.logon(account, password))

def logout():
    'Logs out of the current IMAP server, and moves the main screen back to the login interface.'
    internal.q.add(internal.logout)