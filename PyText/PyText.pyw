from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import pt_mail as m, pt_data as d, pt_util, queue, pt_data_internal, pt_mail_internal



#new messages update should be a lsit: "New messages from: x, y, z..." not one per line







dVar = pt_data_internal.var
mVar = pt_mail_internal.var

#---------Main
main = Tk()
main.title("PyText")
main.title("PyText")
main.resizable(False, False) 
mainFrame = ttk.Frame(main, padding="20 20 20 20") 
#can always rowconfigure and columnconfigure
#----------end Main

running = True

q = None

mailQ = queue.deque()
dataQ = queue.deque()
mailExceptionQ = queue.deque()
dataExceptionQ = queue.deque()


class var:
    loginFrame = None
    contactWindow = None
    infoFrame = None
    discussionFrame = None
    contactFrame = None
    messages = None
    updatables = set()



class messages:

    #TODO: update to include dates in messagetuples
    #this list may need to be updated when a contact is added (or potentially removed) to reflect names
    #exact naming should be determined when we load; that's when we check for an appropriate contact entry
        def __init__(self):
            self.dict = {}


       # def __getitem__(self, index):
        #    return self.dict.get(index, [])
        

        def add(self, sent, number, text):
            list = self.dict.get(number, False)
            msg = (sent, number, text)
            if list:
                list.append(msg)
                if var.discussionFrame.number == number:
                    var.discussionFrame.writeMsg(msg)
            else: raise Exception("attempting to add messages for an unloaded address:"+number)



        def select(self, number):
            list = self.dict.get(number, False)
            if list:
                self.write(list)
            else:
                print('loading')
                d.load_messages(number)


        def write(self, list):
            for item in list:
                var.discussionFrame.writeMsg(item)

        def received(self, msglist):
            for m in msglist:
                if self.dict.get(m.number, False):
                    self.add(m) #update only happens if we've already loaded for this contact

        def loaded(self, msgtuple):
            #(number, messagelist)
            if not self.dict.get(msgtuple[0], False): raise Exception("loading onto existing address:"+number)
            self.dict[msgtuple[0]] = msgtuple[1]
            if var.discussionFrame.number == msgtuple[0]:
                self.dict[msgtuple[0]] = msgtuple[1]
                self.write(msgtuple[1]) #this means we were waiting on this load to populate the current discussion frame

        def sent(self, number, text):
            #TODO: need a way to handle the UID (negative incrementing, I think) of sent msgs,
            #also that second -1 should be a date
            #Format may need to be false here, if we get the number from the discussionframe
            add(pt_util.msg(text, number, -1, int(time.mktime(time.gmtime())), 1))

        def clear(self):
            self.dict = {}



class discussionFrame:

    def writeMsg(self, msg):
        #TODO: this is writing tons of extra linebreaks. why?
        #TODO: also, need to update this so the cursor's back at the bottom when we're done, and we can get to writing.
        if msg.number != self.number:
            raise Exception("irrelevant write")
        self.text['state']='normal'
        self.text.insert(self.line, '\n') #this avoids our fencepost issue by appending a linebreak to the previous line, basically
        self.text.yview('moveto', '1.0')
        if msg.sent:
            self.text.insert(self.line,"You: "+msg.text)
            end = str(self.line).strip("0")+'5'
            self.text.tag_add('self', self.line, end)
        else:
            name = str(dVar.contacts.withNumber(msg.number)) #can return a Contact if it exists, else a string
            self.text.insert(self.line,name+": "+msg.text)
            end = str(self.line).strip("0")+str(len(name)+2)
            self.text.tag_add('person', self.line, end)
        self.line = self.line+1
        #stuff
        self.text['state']='disabled'

        #msg is tuple (False, number, text) for received, or (True, number, text) for sent

    def __init__(self): 
        #be cool if we could let them type in the messaging frame, just have it show up as their pending message
        #color it differently, but have it next to their name like - Josh: xxxx....
        #some obvious change when it'd been sent
        self.person = None
        self.number = None
        self.provider = None
        #also change frame name to Messaging: <contact name>
        self.frame = ttk.Frame(mainFrame)
        self.frame.grid(column = 0, row = 1, sticky = (N,S,W))
        self.logout_button= ttk.Button(self.frame, text = "Logout", command = self.logout)
        self.logout_button.grid(column = 1, row = 7, sticky = (W,S))
        self.textframe = ttk.Frame(self.frame)
        #self.text = Text(self.textframe, state = 'disabled', borderwidth = '2', background = 'White', relief = 'groove', foreground = 'Black', insertofftime = '0', font = ('Helvetica', '10'))
        self.text = Text(self.textframe, borderwidth = '2', background = 'White', relief = 'groove', foreground = 'Black', insertofftime = '0', wrap = "word", font = ('Helvetica', '10'))
        self.text_scrollbar = ttk.Scrollbar(self.frame, orient=VERTICAL, command=self.text.yview)
        self.text['yscrollcommand']=self.text_scrollbar.set 
        self.text_scrollbar.grid(column = 0, row = 0, rowspan = 7, sticky = (N,E,S,W))
        self.text.grid(column = 0, row = 0, sticky = (N,E,S,W))
        self.textframe.grid_propagate(False)
        self.textframe.grid_rowconfigure(0, weight=1)
        self.textframe.grid_columnconfigure(0, weight=1)
        self.textframe['height']=400
        self.textframe['width']=500
        self.label = ttk.Label(self.frame, text = "Messaging", relief = "raised", background = "White", anchor = "center")
        self.label.grid(column = 1, row = 0, columnspan = 4, sticky = (N,E,S,W))
        self.textframe.grid(column = 1, row = 1, columnspan = 4, rowspan = 6, sticky = (N,E,S,W))
        self.text.tag_configure('person', foreground = 'SteelBlue')
        self.text.tag_configure('self', foreground = 'Gray')
        self.text.tag_configure('unsent', foreground = 'LimeGreen')
        self.text.bind("<Up>", lambda x: self.text.yview('scroll', '-1', 'units'))
        self.text.bind("<Down>", lambda x: self.text.yview('scroll', '1', 'units'))
        self.textBinding()
        self.line = 1.0

    def clear(self): #written twice on first set. why?
        self.person = None
        self.number = None
        self.provider = None
        self.label['text'] = 'Messaging'
        self.text['state']='normal'
        self.text.delete('0.0', 'end')
        self.line = 1.0
        self.text['state']='disabled'

    def textBinding(self):
        self.text.bind("<Button-1>", "break") #this overwrites/disables bindings, but we do apparently have to use "break"
        self.text.bind("<Double-Button-1>", "break")
        self.text.bind("<Triple-Button-1>", "break")
        self.text.bind("<B1-Motion>", "break")
        self.text.bind("<Leave>", "break")
        self.text.bind("<Control-a>", "break")
        self.text.bind("<Control-b>", "break")
        self.text.bind("<Control-f>", "break")
        self.text.bind("<Control-p>", "break")
        self.text.bind("<Control-n>", "break")
        self.text.bind("<Control-h>", "break")
        self.text.bind("<Control-d>", "break")
        self.text.bind("<Control-space>", "break")
        self.text.bind("<Home>", "break")
        self.text.bind("<End>", "break")
        self.text.bind("<Next>", "break")
        self.text.bind("<Prior>", "break")
        self.text.bind("<Select>", "break")
        self.text.bind("<Shift-Return>", self.shiftReturn)
        self.text.bind("<Return>", self.Return)
        self.text.bind("<ButtonRelease-1>", self.buttonRelease)
        self.text.bind("<Left>", self.left)
        self.text.bind("<Right>", self.right)
        self.text.bind("<Up>", self.up)
        self.text.bind("<Down>", self.down)
        #bind move cursor up, move cursor left, and backspace so that they can only move onto other text tagged 'unsent'


    def Return(self, null):
        return 'break' #canceled early right now, too easy to send stuff
        #TODO: we also want to break if the stuff to send is empty. mostly, we want our textbox working properly
        #we also want to log sent messages
        if self.number == None or self.provider == None: return 'break'
        m.mail(self.text.get('1.0', 'end'),self.number, self.provider)
        return 'break'

    def shiftReturn(self, null):
        self.text.insert('insert', '\n')
        return 'break'

    def buttonRelease(self, null):
        self.text.focus()
        return 'break' #interrupts tk's response chain

    def left(self, null):
        #CONDITIONALLY - CHECK FOR OUR LIMIT
        self.text.mark_set('insert', self.text.index('insert')+'- 1 chars')
        return 'break'

    def right (self, null):
        self.text.mark_set('insert', self.text.index('insert')+'+ 1 chars')
        return 'break'

    def up(self, null):
        #CONDITIONALLY - CHECK FOR OUR LIMIT
        self.text.mark_set('insert', self.text.index('insert')+'- 1 lines')
        return 'break'

    def down(self, null):
        self.text.mark_set('insert', self.text.index('insert')+'+ 1 lines')
        return 'break'

    def backspace(self, null):
        return 'break'


    
    #self.text.bind("<Key>", lambda x: self.write(x.char)) #event has char attribute, containing char of pressed key


    def setPerson(self, contact):
        contact = dVar.contacts[contact]
        if contact.number == self.number:
            return #person already selected
        self.person = contact.name
        self.number = contact.number
        self.provider = contact.provider
        self.label['text'] = 'Messaging: '+contact.name+' ('+contact.number+')'
        #d.load_messages(self.number)
        var.messages.select(self.number)
        #for item in 


    #function for later, for receiving msgs from unknown numbers
    def setPersonAddress(self, address):
        self.person = None
        split = address.rpartition('@')
        self.number = split[0]
        self.provider = 'umm' #TODO" detect provider based on address. we probably need the inverse setup of the address dictionary



    
    def logout(self): #logout function here.
        d.save_contacts()
        var.discussionFrame.logout_button['state'] = 'disabled'
        var.loginFrame.logon_button['state'] = 'disabled'
        var.contactWindow.close()
        var.discussionFrame.clear()
        var.messages.clear()
        m.logout()
        mainFrame.grid_forget()
        oldContacts = var.contactFrame.contacts_pane.get_children()
        for c in oldContacts:
            var.contactFrame.contacts_pane.delete(c)
        var.loginFrame.active()


class infoFrame: 
    #todo: max log length
    #also, a special function for logging "new message from X" that uses tag binding to bind opening a chat with the user you just
    #got a message from to clicking on the text
    def __init__(self):
        self.frame = ttk.Frame(mainFrame)
        self.frame.grid(column = 0, row = 0, sticky = (N,W,S,E), columnspan = 2)
        self.textframe = ttk.Frame(self.frame)
        self.text = Text(self.textframe, state = 'disabled', borderwidth = '2', background = 'SteelBlue', relief = 'groove', foreground = 'WhiteSmoke', insertofftime = '0', font = ('Helvetica', '10'))
        
        #DO NOT DELETE, this is scrollbar configuration. it might comeback
        self.text_scrollbar = ttk.Scrollbar(self.frame, orient=VERTICAL, command=self.text.yview)
        #self.text['yscrollcommand']=self.text_scrollbar.set 
        self.text['yscrollcommand']=self.multiscroll
        self.text_scrollbar.grid(column = 0, row = 1, rowspan = 6, sticky = (N,S))
        self.text_scrollbartwo = ttk.Scrollbar(self.frame, orient=VERTICAL, command=self.text.yview)
        self.text_scrollbartwo.grid(column = 2, row = 1, rowspan = 6, sticky = (N,S))


        self.text.grid(column = 0, row = 0, sticky = (N,E,S,W))
        self.textframe.grid_propagate(False)
        self.textframe.grid_rowconfigure(0, weight=1)
        self.textframe.grid_columnconfigure(0, weight=1)
        self.textframe['height']=125
        self.textframe['width']=680       #print(var.i.frame.winfo_width()) - scrollbars.winfo_w to get width
        ttk.Label(self.frame, text = "PyText", relief = "raised", background = "White", anchor = "center").grid(column = 0, row = 0, columnspan = 3, sticky = (N,E,S,W))
        self.textframe.grid(column = 1, row = 1, rowspan = 6, sticky = (N,E,S,W))
        self.text.tag_configure('emphasis', foreground = 'Black')
        self.text.bind("<Up>", lambda x: self.text.yview('scroll', '-1', 'units'))
        self.text.bind("<Down>", lambda x: self.text.yview('scroll', '1', 'units'))
        self.line = 1.0
        self.log(" --- Welcome to PyText! --- ", linebreak = False)
        self.log("Latest version always found at: https://github.com/Mindful/PyText", 32, 69)
        #self.text.configure(inactiveselectbackground=self.text.cget("selectbackground")) #foreground = 'WhiteSmoke'

    def multiscroll(self, first, last):
        self.text_scrollbar.set(first, last)
        self.text_scrollbartwo.set(first, last)

    def log(self, string, emphasis_start = 0, emphasis_end = 0, linebreak = True):
        self.text['state']='normal'
        if linebreak:
            self.text.insert(self.line, '\n') #this avoids our fencepost issue by appending a linebreak to the previous line, basically
        self.text.yview('moveto', '1.0')
        self.text.insert(self.line,string)
        start = str(self.line).strip("0")+str(emphasis_start)
        end = str(self.line).strip("0")+str(emphasis_end)
        if not (emphasis_start == emphasis_end == 0):
            self.text.tag_add('emphasis', start, end)
        self.line = self.line+1
        #stuff
        self.text['state']='disabled'

    def error(self, string, linebreak = True):
        #self.text.update_idletasks()
        self.text['state']='normal'
        if linebreak:
            self.text.insert(self.line, '\n')
        self.text.yview('moveto', '1.0')
        self.text.insert(self.line,"Error: "+string)
        self.text.tag_add('emphasis',self.line, self.line+0.6)
        self.line = self.line+1
        main.focus()
        #stuff
        self.text['state']='disabled'




class contactFrame:
    def __init__(self):
        self.frame = ttk.Frame(mainFrame)
        self.frame.grid(column = 1, row = 1, sticky = (N,S,E))
        self.contactsframe = ttk.Frame(self.frame)
        self.addContact_button = ttk.Button(self.frame, text = "Add Contact", command = lambda: var.contactWindow.open(None))
        self.deleteContact_button = ttk.Button(self.frame, text = "Delete Contact", command = lambda: self.deleteContact(None))
        self.contacts_pane = ttk.Treeview(self.contactsframe, show = '', columns = 'Contacts') 
        self.contacts_scrollbar = ttk.Scrollbar(self.frame, orient=VERTICAL, command=self.contacts_pane.yview)
        self.contacts_pane['yscrollcommand']=self.contacts_scrollbar.set
        self.contacts_pane.heading('Contacts', text = 'Contacts')
        self.contacts_pane['selectmode'] = 'browse' #select only one at a time
        self.contacts_pane.tag_configure('favorite', background = 'SteelBlue', foreground = 'WhiteSmoke')
        self.contacts_pane.bind('<Delete>', self.deleteContact)
        self.contacts_pane.bind('<Return>', var.contactWindow.open)
        self.contacts_pane.bind('<f>', self.favoriteContact)
        self.contacts_pane.bind("<Double-1>", self.onDoubleClick)
        ttk.Label(self.frame, text = "Contacts", relief = "raised", background = "White", anchor = "center").grid(column = 0, row = 0, columnspan = 2, sticky = (N,E,S,W))
        self.contacts_scrollbar.grid(column = 2, row = 0, rowspan = 7, sticky = (N,E,S,W))
        self.contacts_pane.grid(column = 0, row = 0, sticky = (N,E,S,W))
        self.contacts_pane.column('Contacts', width='175')
        self.contactsframe.grid_propagate(False)
        self.contactsframe.grid_rowconfigure(0, weight=1)
        self.contactsframe.grid_columnconfigure(0, weight=1)
        self.contactsframe.grid(column = 0,row = 1, columnspan = 2, rowspan = 6, sticky = (N,E,S,W))
        self.contactsframe['height']=400
        self.contactsframe['width']=180
        #self.contacts_pane.grid(column = 0,row = 1, columnspan = 2, rowspan = 6, sticky = (N,E,S,W))
        self.addContact_button.grid(column = 0, row = 8, sticky = (N,W,E))
        self.deleteContact_button.grid(column = 1, row = 8, sticky = (N,W,E))

    def onDoubleClick(self, null):
        var.discussionFrame.setPerson(self.contacts_pane.item(self.contacts_pane.selection())['text'])

    def deleteContact(self, null):
        item = self.contacts_pane.selection()
        loc = self.contacts_pane.index(item)
        if item != "":
             name = self.contacts_pane.item(item)['text'].strip('{}')
             if dVar.settings['confirmation_windows']=='0' or messagebox.askyesno("Delete Contact?", "Remove "+name+" from contacts?"):
                self.contacts_pane.selection_set(self.contacts_pane.next(item))
                q.add(lambda: self.contacts_pane.delete(item))
                #self.contacts_pane.delete(item)
                del dVar.contacts[name]
                var.infoFrame.log(name+" removed from contacts.",0,len(name))



    def favoriteContact(self,null):
        item = self.contacts_pane.selection()
        name = self.contacts_pane.item(item)['text'].strip('{}')
        contact = dVar.contacts[name]
        del dVar.contacts[name]
        if contact.favorited == '0':
            treeloc = dVar.contacts.add(contact.name, contact.number, contact.provider, '1') #remove, change, readd
            self.contacts_pane.item(item, tags = ('favorite',))
            self.contacts_pane.move(item, '', treeloc)
            var.infoFrame.log(name+" marked as a favorite.",0,len(name))
        else:
            treeloc = dVar.contacts.add(contact.name, contact.number, contact.provider, '0') #remove, change, readd
            self.contacts_pane.item(item, tags = ())
            self.contacts_pane.move(item, '', treeloc)
            var.infoFrame.log(name+" is no longer a favorite.",0,len(name))

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
        for item in mVar.addresses.keys():
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

    def open(self, null): #this may need to be added and removed from updatables, otherwise we need to figure out relevant error handling
        self.main.state('normal')
        self.main.lift()
        #self.main.focus()
        self.name_entry.focus()

    def close(self, *args):
        self.main.withdraw()

    def addContact(self, *args):
        name = capitalizeWords(self.name_string.get())
        if len(name) == 0:
            var.infoFrame.error('Cannot add a contact without a name.')
            return
        for word in name.split():
            nameValid = word.isalnum() 
        if not nameValid:
            var.infoFrame.error('Contact names must contain only numbers and letters.')
            return
        num = self.num_string.get().strip()
        if len(name)==10 and name.isdigit():
            var.infoFrame.error('Contact names cannot be potential phone numbers.')
            return
        if len(num)!=10 or not num.isdigit():
            var.infoFrame.error('Phone numbers must have 10 characters and be exclusively digits.')
            return
        if self.provider_box.current() == -1:
            var.infoFrame.error('Cannot add a contact without a phone provider.')
            return
        provider = self.provider_box.get().lower()
        invalid = dVar.contacts.invalidAdd(name, num)
        if invalid == "name":
            var.infoFrame.error('You already have '+name+' as a contact.')
            return
        if invalid: #true and not name, must be duplicate number, so this is the name of the duplicate
            var.infoFrame.error('Contact ' +invalid+' already has number '+num+'.')
            return

        treeloc = dVar.contacts.add(name, num, provider, '0') #save the location it goes in the contact list so it goes the same place in the tree
        var.contactFrame.contacts_pane.insert('', treeloc, text = (name,), values = (name,)) #must be item inside a tuple so it takes it as a SINGLE STRING INCLUDING SPACES
        var.infoFrame.log(name+" successfully added to contacts.",0,len(name))
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

    def saveLogon(self, ttls): #settings are saved on shutdown or manually; don't need to save default_account here
        saveAccount =  dVar.settings['default_account'].lower() != self.account_string.get().lower() and dVar.settings['save_account'] == '1'
        savePassword = dVar.settings.get(self.account_string.get(), '') != self.password_string.get() and dVar.settings['save_password'] == '1'
        if saveAccount:
            dVar.settings['default_account'] = self.account_string.get()
        if savePassword:
            dVar.accounts[self.account_string.get()] = self.password_string.get()
            d.save_account(self.account_string.get(), self.password_string.get())
        else:
            dVar.accounts[self.account_string.get()] = ''
            d.save_account(self.account_string.get())
        q.add(self.inactive)
        d.load_account(self.account_string.get())
        #m.fetch() called by d.load_account
        var.infoFrame.log("Logged in as "+self.account_string.get()+" successfully.",13,13+len(self.account_string.get()))
        if not ttls:
            var.infoFrame.log("Could not start TTLS (STARTTLS); the server may not support it.")


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
    var.discussionFrame.logout_button['state'] = 'normal'

def populateContacts(null):
    'Should typically be run on account setting fetch resoluton, and only in the main thread.'
    for item in dVar.contacts: #No custom definition for this, but default iteration seems to work with __getitem__ defined
        if item.favorited == '1': #we know it's favorited
            var.contactFrame.contacts_pane.insert('', 0, text = (item,), values = (item,), tags = ('favorite',))
        else:
            var.contactFrame.contacts_pane.insert('', 'end', text = (item,), values = (item,)) #must be item inside a tuple so it takes it as a SINGLE STRING INCLUDING SPACES

def mainLogout(null):
     var.discussionFrame.logout_button['state'] = 'normal'
     var.loginFrame.logon_button['state'] = 'normal'

  
def genericFunction(func):
    func()

def mailException(ex):
    mailExceptionQ.append(ex)

def dataException(ex):
    dataExceptionQ.append(ex)

def loadedMessages(messagetuple):
    #(number, messagelist)
    var.messages.dict[messagetuple[0]] = messagetuple[1]
    if var.discussionFrame.number == messagetuple[0]:
        var.messages.loaded(messagetuple)



def quit(): #can add a confirmation window in here to check with users if they REALLY want to quit
    if dVar.settings['confirmation_windows']=='0' or messagebox.askyesno("Quit?", "Close PyText?"):
        global running
        running = False
        var.contactWindow.main.destroy()
        main.destroy()

def minimize(*args):
    main.iconify()

def init():
    global q
    var.loginFrame = loginFrame()
    var.contactWindow = contactWindow()
    var.messages = messages()
    var.discussionFrame = discussionFrame()
    var.contactFrame = contactFrame()
    var.infoFrame = infoFrame() #must be initialized last to get global width?
    q = pt_util.main_fq({'genericFunction': genericFunction, 'mailException': mailException, 
                         'dataException': dataException, d.internal.load_account: populateContacts, d.internal.load_messages: loadedMessages,
                         m.internal.logon: var.loginFrame.saveLogon, m.internal.logout: mainLogout, m.internal.fetchAll: var.messages.received })
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