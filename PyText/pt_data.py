import pt_data_internal as internal, threading

# This is the file for all of PyText's data related code. Information is saved via the sqlite3 library and loaded here.
#
#Consider using json to pack all setting data into the second field of the account sql table
#

def init(deque, var):
    'Initializes the database as well as the data handling thread. Must be called before other pt_data functions can be used'
    internal.mainQ = deque
    initfunc = lambda: internal.init(var)
    t = threading.Thread(target = initfunc, daemon = False)
    t.start()

def terminate():
    'Ends the data thread and calls cleanup functions (like a last settings save)'
    save_contacts()
    internal.q.add(internal.save_settings)
    internal.q.add(internal.terminate)

def save_contacts():
    internal.q.add(lambda: internal.save_contacts(internal.var.currentAccount))

def enqueue(func):
    'Adds a function to the pt_data queue; best used to do something immediately after something else. MUST BE A CALLABLE FUNCTION'
    internal.q.add(func)

def save_account(account, password = None, favorites = None): #this needs to be updated to also save account-specific settings
    'Save account-related values. If no values are specified, the function does nothing'
    internal.q.add(lambda: internal.save_account(account, password, favorites))

def load_contacts(account): #this needs to be updated to also load account-specific settings
    'Load any settings associated with the given account. Also sets this account as the current account.'
    internal.q.add(lambda: internal.load_contacts(account))
    
def save_settings():
    'Save general PyText settings.'
    internal.q.add(internal.save_settings)
    
def load_settings():
    'Load general PyText settings.'
    internal.q.add(internal.load_settings)

