from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import pt_mail as m, pt_data as d, func_queue, queue

#logout button can be double clicked, which is bad. need a generalized solution to disable buttons on use (like login)
#so that they can't be double clicked

#---------Main
main = Tk()
main.title("PyText")
main.title("PyText") #shift+tab is mass unindent, tab is mass indent. good times
main.resizable(False, False)
mainFrame = ttk.Frame(main, padding="40 40 40 40") #can always rowconfigure and columnconfigure
#----------end Main

running = True

q = None

mailQ = queue.deque()
dataQ = queue.deque()
mailExceptionQ = queue.deque()
dataExceptionQ = queue.deque()


class var:
    currentAccount = ''
    l = None
    c = None
    i = None
    info = None
    contact = None
    messaging = None
    updatables = set()

class infoFrame: #THIS LAMBDA SHOULD NOT GO DIRECTLY TO m.logout IT SHOULD DISABLE THE BUTTON AND THEN DO THAT
    def __init__(self):
        self.frame = ttk.Frame(mainFrame)
        self.logout_button= ttk.Button(self.frame, text = "Logout", command = self.logout) #m.logout causing stalls
        self.frame.grid(column = 0, row = 0, columnspan = 2, rowspan = 7)
        self.text = Text(self.frame, state = 'disabled', borderwidth = '5', background = 'SteelBlue', relief = 'groove')
        self.text.grid(column = 0, row = 1, columnspan = 2, rowspan = 4)
        self.logout_button.grid(column = 0, row = 10, sticky = (E,S))

    def log(self, string):
        self.text['state']='normal'
        #stuff
        self.text['state']='disabled'

    def logout(self):
        var.i.logout_button['state'] = 'disabled'
        var.l.logon_button['state'] = 'disabled'
        var.c.close()
        m.logout()
        mainFrame.grid_forget()
        oldContacts = var.contact.contacts_pane.get_children()
        for c in oldContacts:
            var.contact.contacts_pane.delete(c)
        var.l.active()


class messagingFrame:
    def __init__(self):
        pass


class contactFrame:
    def __init__(self):
        self.frame = ttk.Frame(mainFrame)
        self.frame.grid(column = 3, row = 0, columnspan = 2, rowspan = 7)
        self.addContact_button = ttk.Button(self.frame, text = "Add Contact", command = lambda: var.c.open())
        self.contacts_pane = ttk.Treeview(self.frame, show = 'headings', columns = 'Contacts') 
        self.contacts_pane.heading('Contacts', text = 'Contacts')
        self.contacts_pane['selectmode'] = 'browse' #select only one at a time
        self.contacts_pane.tag_configure('favorite', background = 'SteelBlue', foreground = 'WhiteSmoke')
        self.contacts_pane.grid(column = 0,row = 0, columnspan = 2, rowspan = 6, sticky = (N,E,S,W))
        self.addContact_button.grid(column = 0, row = 7, sticky = (N,E))

class contactWindow:

    def __init__(self):
        self.main = Toplevel(main)
        self.main.withdraw()
        self.main.protocol("WM_DELETE_WINDOW", self.close)
        self.main.title("Add Contact")
        self.main.bind('<Return>', self.addContact)
        self.main.bind('<Escape>', self.close)
        self.main.resizable(False, False)
        self.frame = ttk.Frame(self.main, padding="10 10 10 10")
        self.frame.grid(column = 0, row = 0, sticky = (N, W, E, S))
        self.entryFrame = ttk.Frame(self.frame, height = '40', width = '35')
        self.entryFrame.grid(column = 1, row = 0, sticky = (N,W,E), rowspan = 3)
        self.name_string = StringVar()
        self.num_string = StringVar()
        values = []
        for item in m.internal.var.addresses.keys():
            values.append(capitalizeWords(item))
        self.provider_box = ttk.Combobox(self.entryFrame, state = 'readonly', values = tuple(values))
        self.provider_box.grid(column = 0, row = 2, sticky = (W,E))
        #Name Entry
        ttk.Entry(self.entryFrame, textvariable = self.name_string).grid(column = 0, row = 0, sticky = (W,E))
        #Name Label
        ttk.Label(self.frame, text = "Name:",  anchor = 'e').grid(column = 0, row = 0, sticky = (W))
        #Number Entry
        ttk.Entry(self.entryFrame, textvariable = self.num_string).grid(column = 0, row = 1, sticky = (W,E))
        #Number Label
        ttk.Label(self.frame, text = "Number:", anchor = 'e').grid(column = 0, row = 1, sticky = (W))
        #Provider Label
        ttk.Label(self.frame, text = "Provider:", anchor = 'e').grid(column = 0, row = 2, sticky = (W))
        #Add Button
        ttk.Button(self.frame, text = "Add Contact", command = self.addContact).grid(column = 1, row = 3, sticky = (W,E), columnspan = 2)

    def open(self): #this may need to be added and removed from updatables, otherwise we need to figure out relevant error handling
        self.main.state('normal')
        self.main.lift()
        self.main.focus()

    def close(self, *args):
        self.main.withdraw()

    def addContact(self, *args):
        #Validate name
        name = capitalizeWords(self.name_string.get())
        if len(name) == 0:
            print('must enter name')
        num = self.num_string.get().strip()
        if len(num)!=10:
            print('phone numbers must have at least 10 digits')
        if not num.isdigit():
            print('phone numbers must be exclusively digits')
        print(name)
        if self.provider_box.current() == -1:
            print('must select provider')
        else:
            provider = self.provider_box.get().lower()
            print(provider)
        pass #HUGE VALIDATION here

class loginFrame:

    def update(self):
        if len(mailExceptionQ) > 0:
            self.error(str(mailExceptionQ.pop()))

    def toggleLogonButton(self, onoff):
        if onoff:
            self.logon_button['state'] = 'normal'
        else:
            self.logon_button['state'] = 'disabled'

    def saveLogon(self, null): #settings are saved on shutdown or manually; don't need to save default_account here
        saveAccount =  d.internal.var.settings['default_account'].lower() != self.account_string.get().lower() and d.internal.var.settings['save_account'] == '1'
        savePassword = d.internal.var.settings.get(self.account_string.get(), '') != self.password_string.get() and d.internal.var.settings['save_password'] == '1'
        if saveAccount:
            d.internal.var.settings['default_account'] = self.account_string.get()
        if savePassword:
            d.internal.var.accounts[self.account_string.get()] = self.password_string.get()
            d.save_account(self.account_string.get(), self.password_string.get())
        else:
            d.internal.var.accounts[self.account_string.get()] = ''
            d.save_account(self.account_string.get())
        q.add(self.inactive)
        d.load_contacts(self.account_string.get())

    def login(self, *args):
        self.toggleLogonButton(False)
        self.account_string.set(self.account_string.get().strip())
        self.password_string.set(self.password_string.get().strip())
        m.logon(self.account_string.get(), self.password_string.get())
        m.enqueue(lambda: q.add(lambda: self.toggleLogonButton(True)))

    def error(self, text = None):
        self.error_text['state'] = 'normal'
        if text:
            self.error_text.delete(1.0, END)
            width = int(self.error_text['width'])
            height = int((len(text)/width)+0.5) #poor man's ceiling function = int(val+0.5)
            self.error_text['height'] = str(height)
            self.error_text.insert(END, text)
        else:
            self.error_text.delete(1.0, END)
            self.error_text['height'] = '1'
        self.error_text['state'] = 'disabled'


    def __init__(self):
        self.frame = ttk.Frame(main, padding="35 20 35 20")
        self.frame.columnconfigure(0, weight = 1)
        self.frame.rowconfigure(0, weight = 2)
        self.account_string = StringVar()
        self.account_entry = ttk.Entry(self.frame, width = 35, textvariable = self.account_string)
        self.account_label = ttk.Label(self.frame, text = "Account:",  anchor = 'e')
        self.password_string = StringVar()
        self.password_entry = ttk.Entry(self.frame, width = 35, show='*', textvariable = self.password_string)
        self.password_label = ttk.Label(self.frame, text = "Passowrd:",  anchor = 'e')
        self.logon_button= ttk.Button(self.frame, text = "Login", command = self.login)
        self.error_text = Text(self.frame, state='disabled', relief = 'flat', fg='red', height = '1', width = '30', background = main['background'], wrap = 'word') #relief = 'flat' is removing the border for us
        self.active()

    def active(self):
        "This grids all of the loginFrame's widgets into its frame, binds <Return> to logging in, and adds itself to updatables"
        self.frame.grid(column = 0, row = 0, sticky = (N, W, E, S))
        self.account_entry.grid(column = 2, row = 2, sticky = (W, E))
        self.account_label.grid(column = 1, row = 2, sticky=(W, E))
        self.password_entry.grid(column = 2, row = 3, sticky = (W, E))
        self.password_label.grid(column = 1, row = 3, sticky = (W, E))
        self.logon_button.grid(column = 2, row = 4, sticky = (W, E))
        self.error_text.grid(column = 2, row = 5, sticky = (S))
        self.funcid = main.bind('<Return>', self.login)
        var.updatables.add(self)

    def inactive(self):
        '''This forgets all of the loginFrame's widgets from its grid, unbinds <Return> from login, and sets main
        active. Even clears the error frame, and removes itself from updatables.'''
        self.error()
        self.frame.grid_forget()
        main.unbind('<Return>', self.funcid)
        var.updatables.remove(self)
        mainActive()


def capitalizeWords(string):
    words = string.strip().lower().split()
    final = ""
    for w in words:
        final += w.capitalize()+' '
    return final.strip()

def mainActive():
    mainFrame.grid(column = 0, row = 0, sticky = (N, W, E, S))
    var.i.logout_button['state'] = 'normal'

def populateContacts(null):
    'Should typically be run on account setting fetch resoluton, and only in the main thread.'
    for item in d.internal.var.contacts:
        if d.internal.var.contacts[item][2] == '1': #we know it's favorited
            contacts_pane.insert('', 0, item, values = item, tags = ('favorite',))
        else:
            contacts_pane.insert('', 'end', item, values = item)

def mainLogout(null):
     var.i.logout_button['state'] = 'normal'
     var.l.logon_button['state'] = 'normal'

  
def genericFunction(func):
    func()

def mailException(ex):
    mailExceptionQ.append(ex)

def dataException(ex):
    dataExceptionQ.append(ex)

def quit(): #can add a confirmation window in here to check with users if they REALLY want to quit
    if messagebox.askyesno("Quit?", "Close PyText?"):
        global running
        running = False
        var.c.main.destroy()
        main.destroy()

def minimize(*args):
    main.iconify()

def init():
    global q
    var.l = loginFrame()
    var.c = contactWindow()
    var.i = infoFrame()
    var.info = infoFrame()
    var.contact = contactFrame()
    var.messaging = messagingFrame()
    q = func_queue.main_fq({'genericFunction': genericFunction, 'mailException': mailException, 
                         'dataException': dataException, d.internal.load_contacts: populateContacts,
                         m.internal.logon: var.l.saveLogon, m.internal.logout: mainLogout })
    d.init(q, var)
    m.init(q)
    main.protocol("WM_DELETE_WINDOW", quit)
    main.bind('<Escape>', minimize)
    main.focus()
    while running: #this seems the best way to alter the mainloop; write my own using update
        if len(q) > 0:
            q.run()
        main.update()
        for item in var.updatables:
            item.update()
    d.terminate()
    m.terminate() 

init() #This is what actually starts the program.