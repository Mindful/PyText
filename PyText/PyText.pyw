from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import pt_mail as m, pt_data as d, pt_util, queue

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
    l = None
    c = None
    i = None
    info = None
    contact = None
    messaging = None
    updatables = set()

class infoFrame: 
    #todo: scrollbar and max log length
    def __init__(self):
        self.frame = ttk.Frame(mainFrame)
        self.logout_button= ttk.Button(self.frame, text = "Logout", command = self.logout)
        self.frame.grid(column = 0, row = 0, columnspan = 2, rowspan = 7)
        self.text = Text(self.frame, state = 'disabled', borderwidth = '2', background = 'SteelBlue', relief = 'groove', foreground = 'WhiteSmoke')
        self.text.grid(column = 0, row = 1, columnspan = 2, rowspan = 4)
        self.logout_button.grid(column = 0, row = 10, sticky = (E,S))
        self.text.tag_configure('emphasis', foreground = 'Black')
        self.line = 1.0
        self.log(" --- Welcome to PyText! --- ")
        self.log("Latest version always found at: https://github.com/Mindfulness/PyText", 32, 69)
        #self.text.configure(inactiveselectbackground=self.text.cget("selectbackground")) #foreground = 'WhiteSmoke'

    def log(self, string, emphasis_start = 0, emphasis_end = 0):
        #self.text.update_idletasks()
        self.text['state']='normal'
        self.text.insert(self.line,string+"\n")
        start = str(self.line).strip("0")+str(emphasis_start)
        end = str(self.line).strip("0")+str(emphasis_end)
        if not (emphasis_start == emphasis_end == 0):
            self.text.tag_add('emphasis', start, end)
        self.line = self.line+1
        #stuff
        self.text['state']='disabled'

    def error(self, string):
        #self.text.update_idletasks()
        self.text['state']='normal'
        self.text.insert(self.line,"Error: "+string+"\n")
        self.text.tag_add('emphasis',self.line, self.line+0.6)
        self.line = self.line+1
        main.focus()
        #stuff
        self.text['state']='disabled'

    def logout(self):
        d.save_contacts()
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
        #TODO: column should not be resizable. may have to avoid displaying column header
        self.frame = ttk.Frame(mainFrame)
        self.frame.grid(column = 3, row = 0, columnspan = 2, rowspan = 7)
        self.addContact_button = ttk.Button(self.frame, text = "Add Contact", command = lambda: var.c.open())
        self.contacts_pane = ttk.Treeview(self.frame, show = 'headings', columns = 'Contacts') 
        self.contacts_pane.heading('Contacts', text = 'Contacts')
        self.contacts_pane['selectmode'] = 'browse' #select only one at a time
        self.contacts_pane.tag_configure('favorite', background = 'SteelBlue', foreground = 'WhiteSmoke')
        self.contacts_pane.grid(column = 0,row = 0, columnspan = 2, rowspan = 6, sticky = (N,E,S,W))
        self.contacts_pane.bind('<Delete>', self.deleteContact)
        self.contacts_pane.bind('<Return>', self.favoriteContact)
        #self.contacts_pane.column('Contacts', stretch = False, minwidth = 200)
        #self.tree.bind("<Double-1>", self.OnDoubleClick) <---TODO
        self.addContact_button.grid(column = 0, row = 7, sticky = (N,E))

    def deleteContact(self, null):
        item = self.contacts_pane.selection()
        loc = self.contacts_pane.index(item)
        if item != "":
             name = self.contacts_pane.item(item)['text'].strip('{}')
             if d.internal.var.settings['confirmation_windows']=='0' or messagebox.askyesno("Delete Contact?", "Remove "+name+" from contacts?"):
                self.contacts_pane.selection_set(self.contacts_pane.next(item))
                q.add(lambda: self.contacts_pane.delete(item))
                #self.contacts_pane.delete(item)
                del d.internal.var.contacts[name]
                var.i.log(name+" removed from contacts.",0,len(name))



    def favoriteContact(self,null):
        item = self.contacts_pane.selection()
        name = self.contacts_pane.item(item)['text'].strip('{}')
        contact = d.internal.var.contacts[name]
        del d.internal.var.contacts[name]
        if contact.favorited == '0':
            treeloc = d.internal.var.contacts.add(contact.name, contact.number, contact.provider, '1') #remove, change, readd
            self.contacts_pane.item(item, tags = ('favorite',))
            self.contacts_pane.move(item, '', treeloc)
            var.i.log(name+" marked as a favorite.",0,len(name))
        else:
            treeloc = d.internal.var.contacts.add(contact.name, contact.number, contact.provider, '0') #remove, change, readd
            self.contacts_pane.item(item, tags = ())
            self.contacts_pane.move(item, '', treeloc)
            var.i.log(name+" is no longer a favorite.",0,len(name))

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
        self.name_entry = ttk.Entry(self.entryFrame, textvariable = self.name_string)
        self.name_entry.grid(column = 0, row = 0, sticky = (W,E))
        #Name Label
        ttk.Label(self.frame, text = "Name:",  anchor = 'e').grid(column = 0, row = 0, sticky = (W))
        #Number Entry
        ttk.Entry(self.entryFrame, textvariable = self.num_string).grid(column = 0, row = 1, sticky = (W,E))
        #Number Label
        ttk.Label(self.frame, text = "Number:", anchor = 'e').grid(column = 0, row = 1, sticky = (W))
        #Provider Label
        ttk.Label(self.frame, text = "Provider:", anchor = 'e').grid(column = 0, row = 2, sticky = (W))
        #provider box here for the sake of tab order - tab order is by default dependent on the order things are added
        self.provider_box = ttk.Combobox(self.entryFrame, state = 'readonly', values = tuple(values))
        self.provider_box.grid(column = 0, row = 2, sticky = (W,E))
        #Add Button
        ttk.Button(self.frame, text = "Add Contact", command = self.addContact).grid(column = 1, row = 3, sticky = (W,E), columnspan = 2)

    def open(self): #this may need to be added and removed from updatables, otherwise we need to figure out relevant error handling
        self.main.state('normal')
        self.main.lift()
        #self.main.focus()
        self.name_entry.focus()

    def close(self, *args):
        self.main.withdraw()

    def addContact(self, *args):
        name = capitalizeWords(self.name_string.get())
        if len(name) == 0:
            var.i.error('Cannot add a contact without a name.')
            return
        for word in name.split():
            nameValid = word.isalnum() 
        if not nameValid:
            var.i.error('Contact names must contain only numbers and letters.')
            return
        num = self.num_string.get().strip()
        if len(num)!=10 or not num.isdigit():
            var.i.error('Phone numbers must have 10 characters and be exclusively digits.')
            return
        if self.provider_box.current() == -1:
            var.i.error('Cannot add a contact without a phone provider.')
            return
        provider = self.provider_box.get().lower()
        if name in d.internal.var.contacts:
            var.i.error('You already have '+name+' as a contact.')
            return
        treeloc = d.internal.var.contacts.add(name, num, provider, '0') #save the location it goes in the contact list so it goes the same place in the tree
        var.contact.contacts_pane.insert('', treeloc, text = (name,), values = (name,)) #must be item inside a tuple so it takes it as a SINGLE STRING INCLUDING SPACES
        var.i.log(name+" successfully added to contacts.",0,len(name))
        self.name_string.set("")
        self.num_string.set("")
        self.provider_box.set("")

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
        var.i.log("Logged in as "+self.account_string.get()+" successfully.",13,13+len(self.account_string.get()))


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
    for item in d.internal.var.contacts: #No custom definition for this, but default iteration seems to work with __getitem__ defined
        if item.favorited == '1': #we know it's favorited
            var.contact.contacts_pane.insert('', 0, text = (item,), values = (item,), tags = ('favorite',))
        else:
            var.contact.contacts_pane.insert('', 'end', text = (item,), values = (item,)) #must be item inside a tuple so it takes it as a SINGLE STRING INCLUDING SPACES

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
    if d.internal.var.settings['confirmation_windows']=='0' or messagebox.askyesno("Quit?", "Close PyText?"):
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
    var.contact = contactFrame()
    var.messaging = messagingFrame()
    q = pt_util.main_fq({'genericFunction': genericFunction, 'mailException': mailException, 
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