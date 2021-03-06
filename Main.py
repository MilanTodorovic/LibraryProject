from tkinter import *
from tkinter import ttk
from tkinter import tix
from tkinter import _setit
import datetime
import DataBase
from tkinter import messagebox
import Sending
from multiprocessing import Process, Queue, freeze_support
from queue import Empty
import threading

"""Version 1.6.1
Added a seperate window to manually enter the generation indicator of a students index number"""


# TO DO
# remove all the print statements used for debugging
# prozor za profesore
# iznajmljivanje knjiga za profesore

# CLASS FOR THE LOGIN WINDOW
class Login(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master=master
        self.lg_window()
        self.q = Queue()
        self.s = None  # used to store session object returned from Sending.connecting thru self.q
        self.id = None # used to store ID from after script

    def lg_window(self):
        self.master.title('Uspostavljanje veze sa imejlom')

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(4, weight=1)
        self.pack(fill=BOTH)

        self.lg_entry = [ttk.Entry(self) for i in range(0, 2)]
        self.lg_label = [ttk.Label(self, text=i) for i in ['Korisnicko ime', 'Sifra', 'Status logovanja']]
        self.lg_button = ttk.Button(self, text='Uloguj me', command=self.conn)
        self.lg_button.grid(row=5, column=2, padx=5, pady=10)
        self.lg_button.bind("<Return>", self.conn)
        self.lg_button.focus()

        self.lg_label[0].grid(row=2, column=1, padx=5, pady=5)
        self.lg_label[1].grid(row=3, column=1, padx=5, pady=5)
        self.lg_label[2].grid(row=4, column=2, padx=5, pady=5) # label to update the status
        self.lg_entry[0].grid(row=2, column=2, pady=5)
        self.lg_entry[1].grid(row=3, column=2, pady=5)


    def conn(self, *args):
        self.un = self.lg_entry[0].get()
        self.pw = self.lg_entry[1].get()

        if self.un == "" or self.pw == "":
            messagebox.showwarning('Upozorenje','Morate uneti korisnicko ime i sifru.')
        else:
            # start's a multiprocess for logging in
            p = Process(target=Sending.connecting, args=(self.un, self.pw, self.q))
            p.start()
            # self.id = self.master.after(100, self.uplab)
            self.uplab()

    def uplab(self, *args):
        self.id = self.master.after(100, self.uplab)
        # print(self.id)
        try:
            x = self.q.get_nowait()
            if x == 0:
                self.s = self.q.get_nowait()
                print('self.s u uplab()', self.s)
                Window.session = self.s
                print('Window.session u uplab()', Window.session)
                messagebox.showinfo('Cestitamo',
                                        'Uspesno ste se ulogovali.\nProgram se pokrece nakon sto pritisnete OK.')
                # print('poslednji self.id', self.id)
                self.master.after_cancel(self.id)
                self.master.destroy()
                return 0


            elif x == 1:
                self.s = None
                messagebox.showerror('Greska',
                                         'Uneli ste pogresno korisnicko ime ili pogresnu sifru.\n Pokusajte ponovo.')
                self.master.after_cancel(self.id)
                return 0


            elif x == 2:
                self.s = None
                messagebox.showerror('Greska', 'Nije bilo moguce usposatviti vezu.\nPokusajte ponovo kasnije.')
                self.master.after_cancel(self.id)
                return 0


            else:
                self.lg_label[2].config(text=x)

        except Empty:
            # if Queue is still empty, do nothing
            return 0
            # pass
            # self.uplab()




# CLASS FOR THE MAIN PROGRAM
class Window(ttk.Frame):
    # session variable for logging into the email
    session = None

    def __init__(self, master = None):
        ttk.Frame.__init__(self, master)

        # All the ttk.notebook frames
        self.master = master
        self.master.title("Cirkulacija V1.6.1")
        self.init_window() # initializes all the subframes and starts the first frame

        self.session = Window.session # stores a Session object to pass around
        self.q = Queue() # one Queue to rule them all
        self.pack(fill=BOTH, expand=1)  # self is a Frame
        # print('Window.session u Window klasi', Window.session)
        # print('self.session u Window klasi', self.session)

        # self je glavni Frame u koji ja stavljam Notebook frame-ove i ostalo

        # Checks if there are new due books on the start-up
        threading._start_new_thread(DataBase.checkDue, ("0",))
        # DataBase.checkDue('0')

        # Checks if there are unsetn Emails about lending books
        if self.session is not None:
            self.checkUnsentBook()


    # Opens Toplevel() for a Login Form
    # Uses self.establish_connection
    def login(self):
        if Window.session:
            messagebox.showinfo("Obavestenje", "Vec ste ulogovani")
        else:
            self.connect = Toplevel()

            self.lg_entry = [ttk.Entry(self.connect) for i in range(0, 2)]
            self.lg_label = [ttk.Label(self.connect, text=i) for i in ['Korisnicko ime', 'Sifra', 'Status logovanja']]
            self.lg_button = ttk.Button(self.connect, text='Uloguj me', command=self.establish_connection)

            self.lg_label[0].grid(row=2, column=1)
            self.lg_label[1].grid(row=3, column=1)
            self.lg_label[2].grid(row=4, column=2)
            self.lg_entry[0].grid(row=2, column=2)
            self.lg_entry[1].grid(row=3, column=2)
            self.lg_button.grid(row=5, column=2)

    # Establishes session and connection, checks for errors
    def establish_connection(self):
        self.un = self.lg_entry[0].get()
        self.pw = self.lg_entry[1].get()
        # self.id = self.master.after(100, self.uplabel)

        if self.un == "" or self.pw == "":
            messagebox.showerror('Greska', 'Morate uneti korisnicko ime i sifru.')
            # self.master.after_cancel(self.id)
        else:
            p = Process(target=Sending.connecting, args=(self.un, self.pw, self.q))
            p.start()
            self.uplabel()

    # updates label for login window inside the main window
    def uplabel(self):
        self.id = self.master.after(100, self.uplabel)
        try:
            x = self.q.get_nowait()
            if x == 0:
                self.session = self.q.get_nowait()
                # print('self.session direktno od self.q', self.session)
                Window.session = self.session
                # print('Window.session after self.session', Window.session)
                self.f5.checkLogin() # after successful login within the already open programm, we need to re-enable some buttons in the FifthFrame
                self.checkUnsentBook()
                messagebox.showinfo('Cestitamo',
                                    'Uspesno ste se ulogovali.')
                self.master.after_cancel(self.id)
                del self.id
                self.connect.destroy()
            elif x == 1:
                messagebox.showerror('Greska',
                                     'Uneli ste pogresno korisnicko ime ili pogresnu sifru.\nPokusajte ponovo.')
                self.master.after_cancel(self.id)
                del self.id
            elif x == 2:
                messagebox.showerror('Greska', 'Nije bilo moguce usposatviti vezu.\nPokusajte ponovo kasnije.')
                self.master.after_cancel(self.id)
                del self.id
            else:
                self.lg_label[2].config(text=x)
        except Empty:
            pass

    def logout(self):
        if not self.session:
            messagebox.showwarning('Upozorenja', 'Vec ste izlogovani.')
        else:
            self.session = Sending.sign_out(self.session)
            Window.session = self.session
            messagebox.showinfo('Obavestenje', 'Uspesno ste se izlogovali.')
            self.f5.checkLogin() # deactivates some buttons in the FifthFrame

    # Chesk if ther are unsent emails about lending a book
    def checkUnsentBook(self):
        # Unsent emails about lending a book
        response = DataBase.read_lendBookEmails()
        print('Response', response)
        if response:
            threading._start_new_thread(self.sendUnsentEmails, (response,))
        # Unsent emails about some information
        response1 = DataBase.unsent_read(0)
        print('Response1', response1)
        if response1:
            threading._start_new_thread(self.sendUnsentInformation, (response1,))
        # Unsent warning emails
        response2 = DataBase.unsent_read(1)
        print('Response2', response2)
        if response2:
            threading._start_new_thread(self.sendUnsentWarnings, (response2,))

    # Opens Toplevel for sending unsent Emails
    # lst is the resposne from reading the DB
    def sendUnsentEmails(self, lst):
        window = Toplevel()
        window.focus_set()
        l = ttk.Label(window, text='Slanje neposlatih mejlova')
        l.pack()
        pb = ttk.Progressbar(window, value=0, maximum=len(lst), length=200)
        pb.pack()
        for l in lst:
            response = Sending.send_email(Window.session, l)
            if response == 0:
                pb.step()
        messagebox.showinfo("Obavestenje", "Sva neposlata obavestenja o pozajmici knjige su uspesno poslata.")
        window.destroy()

    def sendUnsentWarnings(self, lst):
        window = Toplevel()
        window.focus_set()
        l = ttk.Label(window, text='Slanje neposlatih mejlova')
        l.pack()
        pb = ttk.Progressbar(window, value=0, maximum=len(lst), length=200)
        pb.pack()
        for l in lst:
            response = Sending.send_email(Window.session, l)
            if response == 0:
                pb.step()
        messagebox.showinfo("Obavestenje", "Sva neposlata upozorenja su uspesno poslata.")
        window.destroy()

    def sendUnsentInformation(self, lst):
        window = Toplevel()
        window.focus_set()
        l = ttk.Label(window, text='Slanje neposlatih mejlova')
        l.pack()
        pb = ttk.Progressbar(window, value=0, maximum=len(lst), length=200)
        pb.pack()
        for l in lst:
            response = Sending.send_email(Window.session, l)
            if response == 0:
                pb.step()
        messagebox.showinfo("Obavestenje", "Sva neposlata obavestenja e su uspesno poslata.")
        window.destroy()

    # MAIN FRAMES FOR ANY FURTHER WINDOWS
    def init_window(self):
        # list of all the frame classes
        self.nb = ttk.Notebook(self)
        FRAME_CLASSES = (FirstFrame, SecondFrame, ThirdFrame, ForthFrame, FifthFrame, SixthFrame)
        self.f1 = FirstFrame(self.nb)
        self.f2 = SecondFrame(self.nb)
        self.f3 = ThirdFrame(self.nb)
        self.f4 = ForthFrame(self.nb)
        self.f5 = FifthFrame(self.nb)
        self.f6 = SixthFrame(self.nb)


        self.tab_names=["Pretraga", "Novi korisnik", "Pozajmica knjige", "Ispravka podataka", "Slanje obaveštenja", "Brisanje korisnika"]
        # self.tab_frames = [ttk.Frame(self, width=900, height=625) for i in range(0,len(self.tab_names))]
        self.nb.add(self.f1, text=self.tab_names[0])
        self.nb.add(self.f2, text=self.tab_names[1])
        self.nb.add(self.f3, text=self.tab_names[2])
        self.nb.add(self.f4, text=self.tab_names[3])
        self.nb.add(self.f5, text=self.tab_names[4])
        self.nb.add(self.f6, text=self.tab_names[5])
        # for i in range(0, len(FRAME_CLASSES)):
        #     self.nb.add(FRAME_CLASSES[i](self), text=self.tab_names[i])
        self.nb.pack(expand=True, fill=BOTH)

        # Main Menu
        self.menubar = Menu(self.master)
        self.master.config(menu=self.menubar)

        # Submenues
        ## File menu
        file = Menu(self.menubar, tearoff=0)
        file.add_command(label='Uloguj me', command=self.login)
        file.add_command(label='Izloguj me', command=self.logout)
        file.add_command(label="Izlaz", command=on_closing) # defined outside this class
        self.menubar.add_cascade(label="File", menu=file)
        ## Help menu
        help = Menu(self.menubar, tearoff=0)
        help.add_command(label='O programu', command=self.helpWindow)
        self.menubar.add_cascade(label="Pomoc", menu=help)

    # Window for information about the program
    def helpWindow(self):
        top = Toplevel()
        top.title('O programu')
        top.geometry('250x100')
        top.focus_set()
        helplist = ['Turbo Cirkulator 3000', 'Verzija: 1.6.1', 'Copyright Milan Todorovic 2016-',
                    'Beta testeri: Danijel Milosevic,']
        helpLabels = [ttk.Label(top, text=i) for i in helplist]
        for i in range(0, len(helpLabels)):
            helpLabels[i].pack()

# Subframe for searchign user information
class FirstFrame(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.master=master
        self.session = Window.session
        self.userEntryW()

    # Frame that hosts all widgets
    def userEntryW(self):

        # Configuring rows and columns
        for i in range(0,8):
            self.rowconfigure(i, weight=1)
        for i in range(0,7):
            self.columnconfigure(i, weight=1)

        # Two seperate label frames to make things visually more appealing
        self.p_iw = ttk.LabelFrame(self, text="Pretraga korisnika", width = 275, height = 300)
        self.p_iw.configure(labelanchor = NSEW)
        self.p_iw.grid(row=1, column=0, padx=20, pady=20)
        self.p1_iw = ttk.LabelFrame(self, text="Pretraga knjiga", width = 275, height = 300)
        self.p1_iw.configure(labelanchor = NSEW)
        self.p1_iw.grid(row=1, column=1, padx=20, pady=10)

        # Statusbar
        self.sb = ttk.Label(self, relief=SUNKEN, anchor=W)
        self.sb.grid(row=4, column=0, columnspan=6, sticky=NSEW, pady=5)

        # TreeView
        self.column_names=['Student','Indeks', 'Adresa', 'Br. lic. karte','JMBG','Fiksni','Mobilni','Mejl']
        self.tree = ttk.Treeview(self, column=(self.column_names), show='headings')

        for i in self.column_names:
            self.tree.heading(i, text=i)
            # self.tree.heading(i, text=i, command=lambda _col=i: self.treeview_sort_column(self.tree,_col, False))

        self.tree.grid(row=3, column=0, columnspan=8, sticky=NSEW)

        # Buttons
        self.searchButton = ttk.Button(self, text = "Pretraži", command = self.print_entry, width = 12)
        self.searchButton.grid(row = 1, column = 2, padx = 10, pady = 10)
        self.deleteButton = ttk.Button(self, text = "Izbriši", command= lambda *args: self.emptyTree(), width = 11)
        self.deleteButton.grid(row = 1, column = 3, padx = 10, pady = 10)
        self.displayButton = ttk.Button(self, text="Prikaži podatke", command=lambda *args: self.tree_column_open(), width=18)
        self.displayButton.grid(row=2, column=2, columnspan=2, padx=10, pady=10)

        # Dropdown Selection
        self.l_lista = ttk.Label(self, text = "Tabele:", width = 8, anchor = W)
        self.l_lista.grid(row = 0, column = 0, padx = 10, pady = 5)
        self.store_selection = StringVar() # Stores selected option
        self.store_selection.set("Studenti")
        self.store_selection.trace("w", self.checkState)
        self.tableList = ['Studenti', 'Adrese', 'Iznajm. knjige']
        self.drop_down = OptionMenu(self, self.store_selection,*self.tableList)
        self.drop_down.grid(row = 0, column = 1)

        '''Frame layout'''
        # Left side
        ## Textvariable
        self.searchIndex = StringVar()
        self.searchName = StringVar()
        self.searchSurname = StringVar()
        self.searchCity = StringVar()
        self.searchAut = StringVar()
        self.searchBook = StringVar()
        self.searchSign = StringVar()
        self.searchDate = StringVar()


        ### Name label and entry
        self.l_name = ttk.Label(self.p_iw, text = "Ime:", width = 10, anchor = W)
        self.l_name.grid(row = 1, column = 0, padx = 5, pady = 5)
        self.e_name = ttk.Entry(self.p_iw, textvariable = self.searchName)
        self.e_name.grid(row = 1, column = 1, pady = 5) # OBAVEZNO textvariable
        self.e_name.focus()
        # self.e_name_help = ttk.Label(self.p_iw, text = "Upozorenje", width = 15, anchor = W)
        # self.e_name_help.grid(row = 1, column = 2, padx=10, pady=10)

        ## Surname
        self.l_sur = ttk.Label(self.p_iw, text = "Prezime:", width = 10, anchor = W)
        self.l_sur.grid(row = 2, column = 0, padx = 5, pady = 5)
        self.e_sur = ttk.Entry(self.p_iw, textvariable = self.searchSurname)
        self.e_sur.grid(row = 2, column = 1, pady = 5)
        # self.e_sur_help = ttk.Label(self.p_iw, text = "Upozorenje", width = 15, anchor = W)
        # self.e_sur_help.grid(row = 2, column = 2, padx=10, pady=10)

        ## Index number
        self.l_index = ttk.Label(self.p_iw, text = "Indeks:", width = 10, anchor = W)
        self.l_index.grid(row = 3, column = 0, padx = 5, pady = 5)
        self.e_index = ttk.Entry(self.p_iw, textvariable = self.searchIndex)
        self.e_index.grid(row = 3, column = 1, pady = 5)# Mora da se odvoji kako bi Delete radio!
        # ONLY usage is to make the grid look prettier
        self.e_index_help = ttk.Label(self.p_iw, text = "", width = 15, anchor = W)
        self.e_index_help.grid(row = 3, column = 2, padx=10, pady=10)

        ## City
        self.l_city = ttk.Label(self.p_iw, text = "Grad:", width = 10, anchor = W)
        self.l_city.grid(row = 4, column = 0, padx = 5, pady = 5)
        self.e_city = ttk.Entry(self.p_iw, textvariable = self.searchCity)
        self.e_city.grid(row = 4, column = 1, pady = 5)# Mora da se odvoji kako bi Delete radio!
        # self.e_city_help = ttk.Label(self.p_iw, text = "Upozorenje", width = 15, anchor = W)
        # self.e_city_help.grid(row = 4, column = 2, padx=10, pady=10)

        # Rigth side
        ## Author
        self.l_aut = ttk.Label(self.p1_iw, text = "Autor:", width = 10, anchor = W)
        self.l_aut.grid(row = 0, column = 0, padx = 5, pady = 5)
        self.e_aut = ttk.Entry(self.p1_iw, textvariable = self.searchAut)
        self.e_aut.grid(row = 0, column = 1, pady =5)
        # self.e_aut_help = ttk.Label(self.p1_iw, text = "Upozorenje", width = 15, anchor = W)
        # self.e_aut_help.grid(row = 0, column = 2, padx=10, pady=10)

        ## Book Title
        self.l_book = ttk.Label(self.p1_iw, text = "Knjiga:", width = 10, anchor = W)
        self.l_book.grid(row = 1, column = 0, padx = 5, pady = 5)
        self.e_book = ttk.Entry(self.p1_iw, textvariable = self.searchBook)
        self.e_book.grid(row = 1, column = 1, pady =5)
        # self.e_book_help = ttk.Label(self.p1_iw, text = "Upozorenje", width = 15, anchor = W)
        # self.e_book_help.grid(row = 1, column = 2, padx=10, pady=10)

        ## Signature
        self.l_sign = ttk.Label(self.p1_iw, text = "Signatura:", width = 10, anchor = W)
        self.l_sign.grid(row = 2, column = 0, padx = 5, pady = 5)
        self.e_sign = ttk.Entry(self.p1_iw, textvariable = self.searchSign)
        self.e_sign.grid(row = 2, column = 1, pady =5)
        # self.e_sign_help = ttk.Label(self.p1_iw, text = "Upozorenje", width = 15, anchor = W)
        # self.e_sign_help.grid(row = 2, column = 2, padx=10, pady=10)

        ## Date
        self.l_date = ttk.Label(self.p1_iw, text = "Datum:", width = 10, anchor = W)
        self.l_date.grid(row = 3, column = 0, padx = 5, pady = 5)
        self.e_date = ttk.Entry(self.p1_iw, textvariable = self.searchDate)
        self.e_date.grid(row = 3, column = 1, pady =5)
        self.e_date_help = ttk.Label(self.p1_iw, text = "dd-mm-yyyy", width = 15, anchor = W)
        self.e_date_help.grid(row = 3, column = 2, padx=10, pady=10)
        tix_ballon_date_help = tix.Balloon(self.p1_iw)
        tix_ballon_date_help.bind_widget(self.e_date_help, balloonmsg = 'Format u kom treba uneti datum.')

        self.checkState()

        self.searchIndex.trace("w", self.print_entry)
        self.searchName.trace("w", self.print_entry)
        self.searchSurname.trace("w", self.print_entry)
        self.searchCity.trace("w", self.print_entry)
        self.searchAut.trace("w", self.print_entry)
        self.searchBook.trace("w", self.print_entry)
        self.searchSign.trace("w", self.print_entry)
        self.searchDate.trace("w", self.print_entry)

    # Reads and prints the query into the Treeview
    def print_entry(self, *args):

        # Clears previous search results
        self.table_chosen = self.store_selection.get()

        if self.table_chosen == "Studenti":

            self.index_s= self.searchIndex.get()
            self.name_s = self.searchName.get()
            self.surname_s = self.searchSurname.get()
            self.city_s = None
            self.aut_s = None
            self.book_s = None
            self.sign_s = None
            self.date_s = None
            self.new_data = DataBase.read_db(self.index_s, self.name_s, self.surname_s, self.city_s, self.aut_s,
                                             self.book_s, self.sign_s, self.date_s, self.table_chosen)

            if len(self.new_data) == 0:
                self.emptyTree()
                self.sb.config(text="Nema rezultata za ovaj upit", foreground = "red")
            else:
                self.emptyTree()
                for d in self.new_data:
                    self.tree.insert("", 'end', values=(d[0],d[1],d[2],d[3],d[4],d[5],d[6],d[7]))
                self.sb.config(text="")

        elif self.table_chosen == "Adrese":
            self.index_s= self.searchIndex.get()
            self.name_s = self.searchName.get()
            self.surname_s = self.searchSurname.get()
            self.city_s = self.searchCity.get()
            self.aut_s = None
            self.book_s = None
            self.sign_s = None
            self.date_s = None
            self.new_data = DataBase.read_db(self.index_s, self.name_s, self.surname_s, self.city_s, self.aut_s,
                                             self.book_s, self.sign_s, self.date_s, self.table_chosen)
            if len(self.new_data) == 0:
                self.emptyTree()
                self.sb.config(text="Nema rezultata za ovaj upit", foreground = "red")
            else:
                self.emptyTree()
                for d in self.new_data:
                    self.tree.insert('', END, values=(d[0], d[1],d[2],d[3],d[4]))
                self.sb.config(text="")

        elif self.table_chosen == "Iznajm. knjige":
            self.index_s= self.searchIndex.get()
            self.aut_s = self.searchAut.get()
            self.book_s = self.searchBook.get()
            self.sign_s = self.searchSign.get()
            self.date_s = self.searchDate.get()
            self.name_s = None
            self.surname_s = None
            self.city_s = None
            self.new_data = DataBase.read_db(self.index_s, self.name_s, self.surname_s, self.city_s, self.aut_s,
                                             self.book_s, self.sign_s, self.date_s, self.table_chosen)
            if len(self.new_data) == 0:
                self.emptyTree()
                self.sb.config(text="Nema rezultata za ovaj upit", foreground = "red")
            else:
                self.emptyTree()
                for d in self.new_data:
                    self.tree.insert('', END, values=(d[0], d[1],d[2],d[3],d[4],d[5],d[6]))
                self.sb.config(text="")
        else:
            pass

    # Deletes information from the treeview
    def emptyTree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

    # opens up a new vindow with more user details
    def tree_column_open(self):
        curItem = self.tree.focus()
        print(self.tree.item(curItem))
        items = self.tree.item(curItem)
        # checks if an user is selected in the treeview
        if len(items['values']) > 0:
            index = str(items['values'][1]) # the treeview stores strings that contain numbers as int and now I have to convert back
            if len(index) < 6:
                print('0'+index)
                index = '0'+index
                user_data = DataBase.read_db(index, None, None, None, None, None, None, None, None)[0]
            else:
                print(index)
                user_data = DataBase.read_db(index, None, None, None, None, None, None, None, None)[0]
            print(user_data)
            taken_books = None
            overdue_books = None

            window = Toplevel()
            window.title('Pregled ličnih podataka korisnika')
            f = ttk.LabelFrame(window, text='Podaci o korisniku')
            f.pack(fill=BOTH)
            WIDTH = 28
            PADX = 5
            PADY = 5
            # Labels
            index_num = ttk.Label(f, text='Indeks: ', anchor=W)
            index_num.grid(row=0, column=0, sticky=W, padx=PADX, pady=PADY)
            surname = ttk.Label(f, text='Prezime: ', anchor=W)
            surname.grid(row=1, column=0, sticky=W, padx=PADX, pady=PADY)
            name = ttk.Label(f, text='Ime: ', anchor=W)
            name.grid(row=2, column=0, sticky=W, padx=PADX, pady=PADY)
            id_num = ttk.Label(f, text='Br. lic. karte: ', anchor=W)
            id_num.grid(row=3, column=0, sticky=W, padx=PADX, pady=PADY)
            jmbg = ttk.Label(f, text='JMBG: ', anchor=W)
            jmbg.grid(row=4, column=0, sticky=W, padx=PADX, pady=PADY)
            telephone = ttk.Label(f, text='Telefon: ', anchor=W)
            telephone.grid(row=5, column=0, sticky=W, padx=PADX, pady=PADY)
            mobile = ttk.Label(f, text='Mobilni: ', anchor=W)
            mobile.grid(row=6, column=0, sticky=W, padx=PADX, pady=PADY)
            email = ttk.Label(f, text='Imejl: ', anchor=W)
            email.grid(row=7, column=0, sticky=W, padx=PADX, pady=PADY)
            street = ttk.Label(f, text='Ulica: ', anchor=W)
            street.grid(row=0, column=2, sticky=W, padx=PADX, pady=PADY)
            str_number = ttk.Label(f, text='Broj: ', anchor=W)
            str_number.grid(row=1, column=2, sticky=W, padx=PADX, pady=PADY)
            city = ttk.Label(f, text='Mesto/Grad: ', anchor=W)
            city.grid(row=2, column=2, sticky=W, padx=PADX, pady=PADY)
            # Entries
            index_num_e = ttk.Entry(f, width=WIDTH)
            index_num_e.insert(END, index)
            index_num_e.config(state=DISABLED)
            index_num_e.grid(row=0, column=1, sticky=W, padx=PADX, pady=PADY)
            surname_e = ttk.Entry(f, width=WIDTH)
            surname_e.insert(END, user_data[0])
            surname_e.config(state=DISABLED)
            surname_e.grid(row=1, column=1, sticky=W, padx=PADX, pady=PADY)
            name_e = ttk.Entry(f, width=WIDTH)
            name_e.insert(END, user_data[1])
            name_e.config(state=DISABLED)
            name_e.grid(row=2, column=1, sticky=W, padx=PADX, pady=PADY)
            id_num_e = ttk.Entry(f, width=WIDTH)
            id_num_e.insert(END, user_data[2])
            id_num_e.config(state=DISABLED)
            id_num_e.grid(row=3, column=1, sticky=W, padx=PADX, pady=PADY)
            jmbg_e = ttk.Entry(f, width=WIDTH)
            jmbg_e.insert(END, user_data[3])
            jmbg_e.config(state=DISABLED)
            jmbg_e.grid(row=4, column=1, sticky=W, padx=PADX, pady=PADY)
            telephone_e = ttk.Entry(f, width=WIDTH)
            telephone_e.insert(END, user_data[4])
            telephone_e.config(state=DISABLED)
            telephone_e.grid(row=5, column=1, sticky=W, padx=PADX, pady=PADY)
            mobile_e = ttk.Entry(f, width=WIDTH)
            mobile_e.insert(END, user_data[5])
            mobile_e.config(state=DISABLED)
            mobile_e.grid(row=6, column=1, sticky=W, padx=PADX, pady=PADY)
            email_e = ttk.Entry(f, width=WIDTH)
            email_e.insert(END, user_data[6])
            email_e.config(state=DISABLED)
            email_e.grid(row=7, column=1, sticky=W, padx=PADX, pady=PADY)
            street_e = ttk.Entry(f, width=WIDTH)
            street_e.insert(END, user_data[7])
            street_e.config(state=DISABLED)
            street_e.grid(row=0, column=3, sticky=W, padx=PADX, pady=PADY)
            str_number_e = ttk.Entry(f, width=WIDTH)
            str_number_e.insert(END, user_data[8])
            str_number_e.config(state=DISABLED)
            str_number_e.grid(row=1, column=3, sticky=W, padx=PADX, pady=PADY)
            city_e = ttk.Entry(f, width=WIDTH)
            city_e.insert(END, user_data[9])
            city_e.config(state=DISABLED)
            city_e.grid(row=2, column=3, sticky=W, padx=PADX, pady=PADY)

            f1 = ttk.Labelframe(window, text='Iznajmljene knjige')
            f1.pack(fill=BOTH)
            column_names_1 = ['Autor', 'Naslov', 'Signatura', 'Datum uzimanja', 'Rok vracanja']
            tree = ttk.Treeview(f1, columns=(column_names_1), show='headings')
            for i in column_names_1:
                tree.heading(i, text=i)
            tree.column('#' + str(1), minwidth=120, width=120)
            tree.column('#' + str(2), minwidth=120, width=120)
            tree.column('#' + str(3), minwidth=50, width=50)
            tree.column('#' + str(4), minwidth=60, width=60)
            tree.column('#' + str(5), minwidth=60, width=60)

            tree.pack(fill=BOTH, expand=True)
            # self.emptyTree()

            takenBooks = DataBase.readLendBoosk(index)  # LOADING DUE BOOKS INTO THE TREEVIEW
            print(takenBooks)
            for d in takenBooks:
                tree.insert('', END, values=(d[0], d[1], d[2], d[3], d[4]))
        else:
            messagebox.showerror('Greška', "Morate odabrati nekog korisnika iz liste.")



    # activates/deactivates certain ttk.entries based on the selection of the optionmenu menu
    # ONLY for the first frame
    def checkState(self, *args):

        self.value = self.store_selection.get()
        if self.value == "Studenti":
            # Right side
            self.e_aut.config(state = DISABLED)
            self.e_book.config(state = DISABLED)
            self.e_sign.config(state = DISABLED)
            self.e_date.config(state = DISABLED)
            self.e_city.config(state=DISABLED)
            # Left side
            self.e_sur.config(state = NORMAL)
            self.e_name.config(state = NORMAL)
            self.e_index.config(state = NORMAL)

            # Changes in labels
            self.tree['columns']=self.column_names
            for i in self.column_names:
                self.tree.heading(i, text=i)
                self.tree.column(i, anchor=W)
            for i in range(1, 3):
                self.tree.column(i, minwidth=120,width=120)
            for i in (2,4,5, 6, 7):
                self.tree.column('#'+str(i), minwidth=70,width=70)
            self.emptyTree()
            self.print_entry()

        elif self.value == "Adrese":
            # Right side
            self.e_aut.config(state = DISABLED)
            self.e_book.config(state = DISABLED)
            self.e_sign.config(state = DISABLED)
            self.e_date.config(state = DISABLED)
            self.e_city.config(state=NORMAL)
            # Left side
            self.e_sur.config(state = NORMAL)
            self.e_name.config(state = NORMAL)
            self.e_index.config(state = NORMAL)
            # Changes in labels
            self.list_tags = ['Prezime','Ime','Indeks','Ulica i broj','Grad',"",""]
            self.tree['columns'] = self.list_tags
            for i in self.list_tags:
                self.tree.heading(i, text=i)
                self.tree.column(i, anchor=W)
            self.tree.column('#3', minwidth=130, width=130)
            for i in (2, 4):
                self.tree.column('#'+str(i), minwidth=80, width=80)

            self.emptyTree()
            self.print_entry()

        else:
            # When self.value == 'Iznajm. knjige'
            # Left side
            self.e_sur.config(state = DISABLED)
            self.e_name.config(state = DISABLED)
            self.e_index.config(state = NORMAL)
            self.e_city.config(state=DISABLED)
            # Right side
            self.e_aut.config(state = NORMAL)
            self.e_book.config(state = NORMAL)
            self.e_sign.config(state = NORMAL)
            self.e_date.config(state = NORMAL)
            # Changes in labels
            self.list_tags=['Stundet', 'Indeks', 'Naslov', 'Autor', 'Signatura', 'Datum uzimanja', 'Datum za vracanje']
            self.tree['columns'] = self.list_tags
            for i in self.list_tags:
                self.tree.heading(i, text=i)
                self.tree.column(i, anchor=W)
            self.emptyTree()
            self.print_entry()

    # might implement error checking next to the ttk.entry fields
    def helperText(self, *args):
        pass

    # DOESN'T WORK AT ALL
    # def treeview_sort_column(self, tree, col, reverse):
    #     print('tree view sort')
    #     l = [(tree.set(k, col), k) for k in tree.get_children('')]
    #     l.sort(reverse=reverse)
    #
    #     # rearrange items in sorted positions
    #     for i, (val, k) in enumerate(l):
    #         tree.move(k, '', i)
    #
    #     # reverse sort next time
    #     tree.heading(col, command=lambda: self.treeview_sort_column(tree, col, not reverse))


# Subframe for adding new users
class SecondFrame(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        global new_photo
        self.add_user_window()


    # Frame that hosts all widgets
    def add_user_window(self, *args):

        # Subframes to make things visually more appealing
        self.p_u = ttk.LabelFrame(self, text="Podaci o korisniku", width = 275, height = 300)
        self.p_u.configure(labelanchor = NSEW)
        self.p_u.grid(row=0, column=0, padx=20, pady=20)
        self.p1_u = ttk.LabelFrame(self, text="Adresa korisnika", width = 275, height = 300)
        self.p1_u.configure(labelanchor = NSEW)
        self.p1_u.grid(row=0, column=1, padx=20, pady=10)

        # Text variables for entries
        self.user = StringVar()
        self.surname = StringVar()
        self.index = StringVar()
        self.id = StringVar()
        self.jmbg = StringVar()
        self.tel = StringVar()
        self.mob = StringVar()
        self.mail = StringVar()
        self.street = StringVar()
        self.house_nr = StringVar()
        self.city = StringVar()

        # Labels and Entries
        ## User specific information
        ### Name
        self.user_l = ttk.Label(self.p_u, text = "Ime korisnika:", anchor = W)
        self.user_l.grid(row = 0, column = 0, sticky = W, padx = 5, pady = 5)
        self.user_e = ttk.Entry(self.p_u, textvariable = self.user)
        self.user_e.grid(row = 0, column = 1, sticky = W, padx = 5, pady = 5)
        ### Surname
        self.surname_l = ttk.Label(self.p_u, text = "Prezime korisnika:", anchor = W)
        self.surname_l.grid(row = 1, column = 0, sticky = W, padx = 5, pady = 5)
        self.surname_e = ttk.Entry(self.p_u, textvariable = self.surname)
        self.surname_e.grid(row = 1, column = 1, sticky = W, padx = 5, pady = 5)
        ### Index number
        self.index_l = ttk.Label(self.p_u, text = "Indeks:", anchor = W)
        self.index_l.grid(row = 2, column = 0, sticky = W, padx = 5, pady = 5)
        self.index_e = ttk.Entry(self.p_u, textvariable = self.index)
        self.index.trace("w", lambda *args: self.checkExistance(self.index.get()))
        self.index_e.grid(row = 2, column = 1, sticky = W, padx = 5, pady = 5)
        index_help = ttk.Label(self.p_u, image=new_photo)
        index_help.image= new_photo
        index_help.grid(row=2, column=3, sticky=W, padx=5, pady=5)
        index_balloon = tix.Balloon(self.p_u)
        index_balloon.bind_widget(index_help, balloonmsg='U slučaju da indeks odstupa \nod modela 09*, 10* i 201*'
                                                        '\nbićete zamoljeni da ručno \nodredite generaciju.')
        ### ID number
        self.id_l = ttk.Label(self.p_u, text = "Br. licne karte:", anchor = W)
        self.id_l.grid(row = 3, column = 0, sticky = W, padx = 5, pady = 5)
        self.id_e = ttk.Entry(self.p_u, textvariable = self.id)
        self.id_e.grid(row = 3, column = 1, sticky = W, padx = 5, pady = 5)
        ### JMBG
        self.jmbg_l = ttk.Label(self.p_u, text = "JMBG:", anchor = W)
        self.jmbg_l.grid(row = 4, column = 0, sticky = W, padx = 5, pady = 5)
        self.jmbg_e = ttk.Entry(self.p_u, textvariable = self.jmbg)
        self.jmbg_e.grid(row = 4, column = 1, sticky = W, padx = 5, pady = 5)
        ### Telephone number
        self.tel_l = ttk.Label(self.p_u, text = "Telefon:", anchor = W)
        self.tel_l.grid(row = 5, column = 0, sticky = W, padx = 5, pady = 5)
        self.tel_e = ttk.Entry(self.p_u, textvariable = self.tel)
        self.tel_e.grid(row = 5, column = 1, sticky = W, padx = 5, pady = 5)
        ### Mobile phone number
        self.mob_l = ttk.Label(self.p_u, text = "Mobilni:", anchor = W)
        self.mob_l.grid(row = 6, column = 0, sticky = W, padx = 5, pady = 5)
        self.mob_e = ttk.Entry(self.p_u, textvariable = self.mob)
        self.mob_e.grid(row = 6, column = 1, sticky = W, padx = 5, pady = 5)
        ### E-mail
        self.mail_l = ttk.Label(self.p_u, text = "E-mail:", anchor = W)
        self.mail_l.grid(row = 7, column = 0, sticky = W, padx = 5, pady = 5)
        self.mail_e = ttk.Entry(self.p_u, textvariable = self.mail)
        self.mail_e.grid(row = 7, column = 1, sticky = W, padx = 5, pady = 5)

        ## Adress
        ### Street
        self.street_l = ttk.Label(self.p1_u, text = "Ulica:")
        self.street_l.grid(row = 0, column = 2, sticky = NSEW, padx = 5, pady = 5)
        self.street_e = ttk.Entry(self.p1_u, textvariable = self.street)
        self.street_e.grid(row = 0, column = 3, sticky = W, padx = 5, pady = 5)
        ### House number
        self.house_nr_l = ttk.Label(self.p1_u, text = "Broj:")
        self.house_nr_l.grid(row = 1, column = 2, sticky = NSEW, padx = 5, pady = 5)
        self.house_nr_e = ttk.Entry(self.p1_u, textvariable = self.house_nr)
        self.house_nr_e.grid(row = 1, column = 3, sticky = W, padx = 5, pady = 5)
        ### City
        self.city_l = ttk.Label(self.p1_u, text = "Grad:")
        self.city_l.grid(row = 2, column = 2, sticky = NSEW, padx = 5, pady = 5)
        self.city_e = ttk.Entry(self.p1_u, textvariable = self.city)
        self.city_e.grid(row = 2, column = 3, sticky = W, padx = 5, pady = 5)

        # Button
        self.button = ttk.Button(self.p1_u, text = "Unesi korisnika", command = self.add_user)
        self.button.grid(row = 5, column = 3, sticky = NSEW, padx = 5, pady = 5)

    # Function that adds a user to the DB
    def add_user(self, *args):
        # the get() method retrieves an empty string if the enrty filed is left empty
        if self.surname.get() == "" or self.user.get() == "" or self.index.get() == "" or self.mail.get() == "":
            messagebox.showerror("Greška","Ne možete uneti korisnika bez sledećih podataka:\nime, prezime, indeks, imejl")
        # elif self.surname.get()==None:
        #     messagebox.showerror("Greska", "None greska")
        else:
            generation = DataBase.determine_generation(self.index.get())
            if generation == 0:
                w = Toplevel()
                w.title('Unos generacije studenta')
                le_strVar = StringVar()
                le = tix.LabelEntry(w, label='Unesite deo indeksa koji oznacava generaiju: ')
                le.entry.configure(textvariable = le_strVar)
                le.pack()
                b = ttk.Button(w, text='Unesi', command=lambda: self.manualGeneration(le_strVar.get(), w))
                b.pack()

            else:
                DataBase.data_entry(self.surname.get(), self.user.get(), self.index.get(), self.id.get(),
                                    self.jmbg.get(), self.tel.get(), self.mob.get(), self.mail.get(),
                                    self.street.get(), self.house_nr.get(), self.city.get(), generation)

                self.user_e.delete(0, END)
                self.surname_e.delete(0, END)
                self.index_e.delete(0, END)
                self.id_e.delete(0, END)
                self.jmbg_e.delete(0, END)
                self.tel_e.delete(0, END)
                self.mob_e.delete(0, END)
                self.mail_e.delete(0, END)
                self.street_e.delete(0, END)
                self.house_nr_e.delete(0, END)
                self.city_e.delete(0, END)

    # Checks if certain information in the DB exist (users, books, due books...)
    def checkExistance(self, index=None, *args):
        DataBase.check_Existance("0", index, None)

    def manualGeneration(self, gen, toplevel):

        # print(gen)
        DataBase.data_entry(self.surname.get(), self.user.get(), self.index.get(), self.id.get(),
                            self.jmbg.get(), self.tel.get(), self.mob.get(), self.mail.get(),
                            self.street.get(), self.house_nr.get(), self.city.get(), gen)

        toplevel.destroy()
        self.user_e.delete(0, END)
        self.surname_e.delete(0, END)
        self.index_e.delete(0, END)
        self.id_e.delete(0, END)
        self.jmbg_e.delete(0, END)
        self.tel_e.delete(0, END)
        self.mob_e.delete(0, END)
        self.mail_e.delete(0, END)
        self.street_e.delete(0, END)
        self.house_nr_e.delete(0, END)
        self.city_e.delete(0, END)


# Subframe for lending a book and book stuff
class ThirdFrame(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.session = Window.session
        global new_photo
        self.takeAbook()

    # Frame that hosts all widgets
    def takeAbook(self):

        # LabelFarmes
        self.p_b = ttk.LabelFrame(self, text="Podaci o knjizi", width = 400, height = 100)
        self.p_b.configure(labelanchor = NSEW)
        self.p_b.grid(row=0, column=0, padx=20, pady=20)
        self.p_b.grid_columnconfigure(2, weight = 1)

        self.p1_b = ttk.LabelFrame(self, text="Produzetak knjige", width = 400, height = 100)
        self.p1_b.configure(labelanchor = NSEW)
        self.p1_b.grid(row=0,column=1, padx=20, pady=20)

        self.p2_b = ttk.LabelFrame(self, text="Razduzivanje", width = 400, height = 100)
        self.p2_b.configure(labelanchor = NSEW)
        self.p2_b.grid(row=1,column=0, padx=20, pady=20)

        self.p3_b = ttk.LabelFrame(self, text="Lista kasnjenja", width=400, height=100)
        self.p3_b.configure(labelanchor=NSEW)
        self.p3_b.grid(row=1, column=1, padx=20, pady=20)

        # Textvariables
        self.index_b = StringVar()
        self.author = StringVar()
        self.book = StringVar()
        self.sign = StringVar()
        self.store_date = StringVar()
        # for updates of the date when the book was taken
        self.sign_j_var = StringVar()
        # for bringing back a book
        self.sign_b_var = StringVar()

        # Labels and Entries
        ## Index number
        self.index_l_b = ttk.Label(self.p_b, text = "Indeks studenta:", anchor = W)
        self.index_l_b.grid(row = 1, column= 0, sticky = W, padx = 5, pady = 5)
        self.index_e_b = ttk.Entry(self.p_b, textvariable = self.index_b)
        self.index_e_b.grid(row = 1, column = 1, sticky = W, padx = 5, pady = 5)
        self.index_b.trace("w", lambda *args: self.checkExistance("1", self.index_b.get(), None))
        self.name_surname_l = ttk.Label(self.p_b, text= "", anchor = W)
        self.name_surname_l.grid(row=1, column=2, sticky=W, padx=5, pady=5)
        ## Author
        self.aut_l = ttk.Label(self.p_b, text = "Autor knjige:", anchor = W)
        self.aut_l.grid(row = 2, column = 0, sticky = W, padx = 5, pady = 5)
        self.aut_e = ttk.Entry(self.p_b, textvariable = self.author)
        self.aut_e.grid(row = 2, column = 1, sticky = W, padx = 5, pady = 5)
        ## Book title
        self.book_l = ttk.Label(self.p_b, text = "Naslov knjige:", anchor = W)
        self.book_l.grid(row = 3, column = 0, sticky = W, padx = 5, pady = 5)
        self.book_e = ttk.Entry(self.p_b, textvariable = self.book)
        self.book_e.grid(row = 3, column = 1, sticky = W, padx = 5, pady = 5)
        ## Signature
        self.sign_l = ttk.Label(self.p_b, text = "Signatura:", anchor = W)
        self.sign_l.grid(row = 4, column = 0, sticky = W, padx = 5, pady = 5)
        self.sign_e = ttk.Entry(self.p_b, textvariable = self.sign)
        self.sign.trace('w', lambda *args: self.checkExistance("2", None, self.sign.get()))
        self.sign_e.grid(row = 4, column = 1, sticky = W, padx = 5, pady = 5)

        # Buttons
        self.button_b = ttk.Button(self.p_b, text = "Unesi", command = self.take_book_entry, width = 15)
        self.button_b.grid(row = 5, column = 2, sticky = NSEW, padx = 5, pady = 5)

        # OptionMenu
        self.label_b = ttk.Label(self.p_b, text = "Rok pozajmice:", anchor = W)
        self.label_b.grid(row = 5, column = 0, sticky = W, padx = 5, pady = 5)
        self.store_date.set("7")
        self.dateList_b = ['7', '14', '28']
        self.drop_down = OptionMenu(self.p_b, self.store_date,*self.dateList_b)
        self.drop_down.grid(row = 5, column = 1, sticky = W)

        # Part for updating the date
        self.sign_j = ttk.Label(self.p1_b, text="Signatura:", anchor=W)
        self.sign_j.grid(row=0,column=0, sticky=W, padx=5, pady=5)
        self.sign_j_e = ttk.Entry(self.p1_b, textvariable=self.sign_j_var)
        self.sign_j_e.grid(row=0, column=1, sticky=W, padx=5, pady=5)
        self.sign_j_var.trace("w", lambda *args: self.checkDate('0'))
        self.aut_title = ttk.Label(self.p1_b, text="Autor i knjiga:", anchor=W)
        self.aut_title.grid(row=1,column=0, padx=5, pady=5, sticky=W)
        self.aut_title_db = ttk.Label(self.p1_b, text="", anchor=W)
        self.aut_title_db.grid(row=1, column=1, padx=5, pady=5)
        self.date_l = ttk.Label(self.p1_b, text="Datum uzimanja: ", anchor=W)
        self.date_l.grid(row=2, column=0, padx=5, pady=5)
        self.date_l_db = ttk.Label(self.p1_b, text="", anchor=W)
        self.date_l_db.grid(row=2, column=1, padx=5, pady=5)
        self.new_date = ttk.Label(self.p1_b, text="Novi datum:", anchor=W)
        self.new_date.grid(row=3,column=0, sticky=W, padx=5, pady=5)
        self.new_date_1 = ttk.Label(self.p1_b, text=str(datetime.date.today().strftime("%d-%m-%Y")), anchor=W)
        self.new_date_1.grid(row=3, column=1, padx=5, pady=5)

        new_date_help = ttk.Label(self.p1_b, image=new_photo)
        new_date_help.photo= new_photo
        new_date_help.grid(row=3, column=2, padx=5, pady=5)
        new_date_help_b = tix.Balloon(self.p1_b)
        new_date_help_b.bind_widget(new_date_help,
                                  balloonmsg='Ovaj datum će biti unet u bazu podataka kao datum uzimanja.\n'
                                             'Knjiga se automatski produžava na 14 dana.')

        self.button_u_date = ttk.Button(self.p1_b, text="Produži", command = lambda: self.updateTables("1"), width=15)
        self.button_u_date.grid(row = 4, column = 2, sticky = NSEW, padx = 5, pady = 5)

        # Bringing a book back
        self.sign_b = ttk.Label(self.p2_b, text="Signatura:", anchor=W)
        self.sign_b.grid(row=0,column=0, sticky=W, padx=5, pady=5)
        self.sign_b_e = ttk.Entry(self.p2_b, textvariable=self.sign_b_var)
        self.sign_b_e.grid(row=0, column=1, sticky=W, padx=5, pady=5)
        self.sign_b_var.trace("w", lambda *args: self.checkDate('1'))
        self.aut_title_b = ttk.Label(self.p2_b, text="Autor i knjiga:", anchor=W)
        self.aut_title_b.grid(row=1,column=0, padx=5, pady=5, sticky=W)
        self.aut_title_db_b = ttk.Label(self.p2_b, text="", anchor=W)
        self.aut_title_db_b.grid(row=1, column=1, padx=5, pady=5)
        self.date_l_b = ttk.Label(self.p2_b, text="Datum uzimanja: ", anchor=W)
        self.date_l_b.grid(row=2, column=0, padx=5, pady=5)
        self.date_l_db_b = ttk.Label(self.p2_b, text="", anchor=W)
        self.date_l_db_b.grid(row=2, column=1, padx=5, pady=5)

        self.button_u_date = ttk.Button(self.p2_b, text="Razduži", command = lambda: self.updateTables("2"), width=15)
        self.button_u_date.grid(row = 4, column = 2, sticky = NSEW, padx = 5, pady = 5)

        # Due books list
        self.button_due = ttk.Button(self.p3_b, text="Prikazi listu", command = self.due_Book_List, width=15)
        self.button_due.grid(row=0, column=0, sticky=NSEW, padx=5, pady=5)
        self.button_due_u = ttk.Button(self.p3_b, text="Azuriraj listu", command = lambda *args: DataBase.checkDue("0"), width=15)
        self.button_due_u.grid(row=0, column=1, sticky=NSEW, padx=5, pady=5)

    def checkDate(self, mode =None, *args):
        if mode == "0":
            self.date_taken = DataBase.read_date(self.sign_j_var.get())
            if self.date_taken == None:
                self.date_l_db.config(text="")
                self.aut_title_db.config(text="")
            else:
                self.aut_title_db.config(text=str(self.date_taken[0][0]))
                self.date_l_db.config(text=str(self.date_taken[0][1]))

        elif mode == "1":
            # checks date for bringing back a book
            self.date_taken = DataBase.read_date(self.sign_b_var.get())
            if self.date_taken == None:
                self.date_l_db_b.config(text="")
                self.aut_title_db_b.config(text="")
            else:
                self.aut_title_db_b.config(text=str(self.date_taken[0][0]))
                self.date_l_db_b.config(text=str(self.date_taken[0][1]))

    def take_book_entry(self, *args):
        if self.index_b.get() == "":
            messagebox.showerror("Greska", "Morate uneti indeks studenta.")
        else:
            lst = DataBase.take_a_book(self.index_b.get(), self.book.get(), self.author.get(), self.sign.get(), self.store_date.get())
            # print(lst)
            # If the librarian hasn't logged in yet, the sending of the e-mail will be postponed
            if self.session == None:
                messagebox.showwarning("Upozorenje", "Niste ulogovani. Slanje obavestenja korisniku da je iznajmio knjigu"
                                                     " bice obavljeno naknadno, cim se ulogujete.")
                DataBase.lendBookEmails(lst[3])
            else:
                Process(target=Sending.send_email, args=(self.session, lst)).start()
            self.index_e_b.delete(0, END)
            self.aut_e.delete(0, END)
            self.book_e.delete(0, END)
            self.sign_e.delete(0, END)

    # Toplevel window with a due books list
    def due_Book_List(self):
        self.nw_due = Toplevel()
        self.nw_due.title("Knjige sa prekoracenim rokom drzanja")
        self.nw_due.focus_set()
        self.nw_due.geometry('700x300')
        self.column_names_1 = ['Korisnik','Indeks', 'Autor i naslov', 'Signatura', 'Datum uzimanja', 'Rok vracanja']
        self.treeDue = ttk.Treeview(self.nw_due, columns=(self.column_names_1), show='headings')
        for i in self.column_names_1:
            self.treeDue.heading(i, text=i)
        for i in (1,3):
            self.treeDue.column('#'+str(i), minwidth=120, width=120)
        for i in (2,4):
            self.treeDue.column('#'+str(i), minwidth=40, width=40)
        for i in (5,6):
            self.treeDue.column('#'+str(i), minwidth=70, width=70)
        self.treeDue.pack(fill=BOTH, expand=True)
        self.emptyTree()

        self.dueBooks = DataBase.checkDue("1") # LOADING DUE BOOKS INTO THE TREEVIEW
        print(self.dueBooks)
        for d in self.dueBooks:
                    self.treeDue.insert('', END, values=(d[0],d[1],d[2],d[3],d[4],d[5]))

    # updates the changes user information in the DB
    def updateTables(self, mode="", *args):
        if mode == "1":
            # Extandes changes date_taken and extends date_bring_back
            self.getValues = [None for i in range(0, 11)]
            DataBase.update_info(mode, *self.getValues, sign_db=self.sign_j_var.get())
        elif mode == "2":
            # deletes books from takenBooks DB
            DataBase.delete_info(self.sign_b_var.get())

    # checks if certain information in the DB exist (users, books, due books...)
    def checkExistance(self, mode=None, index=None, sign=None, *args):
        if mode == "1":
            # checks index number
            self.checking = DataBase.check_Existance("2", index, sign)
            if self.checking[0] == 1:
                self.name_surname_l.configure(text=str(self.checking[1][0][0]))
            else:
                self.name_surname_l.configure(text="")
        elif mode == "2":
            # checks book signature
            DataBase.check_Existance("1", None, sign)
        else:
            pass

    def emptyTree(self):
        for i in self.treeDue.get_children():
            self.treeDue.delete(i)

# Subframe for updating user information
class ForthFrame(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        global new_photo
        self.update_table()

    def update_table(self):
        self.info_label = ttk.Label(self, text="Korisnik se pretražuje na osnovu indeksa.")
        self.info_label.grid(row=0,column=0, padx=20, pady=10)

        self.p_ut = ttk.LabelFrame(self, text="Podaci o korisniku", width = 400, height = 100)
        self.p_ut.configure(labelanchor = NSEW)
        self.p_ut.grid(row=1, column=0, padx=20, pady=10)
        self.p_ut.grid_columnconfigure(2, weight = 1)

        self.p1_ut = ttk.LabelFrame(self, text="Adresa korisnika", width = 400, height = 100)
        self.p1_ut.configure(labelanchor = NSEW)
        self.p1_ut.grid(row=1,column=1, padx=20, pady=10)

        self.label_names_ut = ["Indeks:", "Prezime:", "Ime:", "Br. lic karte:", "JMBG:", "Telefon:", "Mobilni:", "E-mail:",
                               "Ulica:", "Broj:", "Grad:"]
        self.list_variables_ut = [StringVar() for i in range(0,11)]
        self.list_variables_ut[0].trace('w', self.loadInfo)
        self.label_list_ut = [ttk.Label(self.p_ut, text=self.label_names_ut[i], anchor=W) for i in range(0,8)]
        for i in range(8,11):
            self.label_list_ut.append(ttk.Label(self.p1_ut, text=self.label_names_ut[i], anchor=W))
        self.entry_list_ut = [ttk.Entry(self.p_ut, textvariable=self.list_variables_ut[i]) for i in range(0,8)]
        for i in range(8,11):
            self.entry_list_ut.append(ttk.Entry(self.p1_ut, textvariable=self.list_variables_ut[i]))

        for i in range(0,8):
            self.label_list_ut[i].grid(row=i, column=0, sticky=W, padx=5, pady=5)
            self.entry_list_ut[i].grid(row=i,column=1, sticky=W, padx=5, pady=5)
        for i in range(8,11):
            self.label_list_ut[i].grid(row=i-8, column=0, sticky=W, padx=5, pady=5)
            self.entry_list_ut[i].grid(row=i-8, column=1, sticky=W, padx=5, pady=5)

        self.button_ut = ttk.Button(self.p1_ut, text = "Unesi izmene", command = lambda: self.updateTables("0", None))
        # the lambda function is located at the bottom of the script
        self.button_ut.grid(row = 5, column = 3, sticky = NSEW, padx = 5, pady = 5)

        index_info = ttk.Label(self.p_ut, image=new_photo)
        index_info.image= new_photo
        index_info.grid(row=0, column=2, padx=5, pady=5, sticky=W)
        tix_balloon_index_info = tix.Balloon(self.p_ut)
        tix_balloon_index_info.bind_widget(index_info, balloonmsg = 'Indeks se ne moze ipravljati ovim putem.')

    # loads information into the fields for correction/addition of user information
    def loadInfo(self, index=None, *args):
        for i in range(1,11):
                self.entry_list_ut[i].delete(0, END)
        index = self.list_variables_ut[0].get()
        self.li_list = DataBase.read_db(index, None, None, None, None, None, None, None, None)
        # print('Loadinfo funckija', self.li_list)
        if len(self.li_list) > 0:
            j = 0
            for i in range(1,11):
                # 1st field is the index_num, so we don't fill that one
                self.entry_list_ut[i].insert(END, self.li_list[0][j])
                j=j+1
        else:
            return 0

    # updates the changes user information in the DB
    def updateTables(self,*args):
            # Changes students information
            self.getValues = []
            if not self.list_variables_ut[0].get():
                messagebox.showerror('Greska', 'Morate uneti indeks studenta.')
            elif not self.list_variables_ut[1].get():
                messagebox.showerror('Greska', 'Nepostojeci korisnik')
            else:
                for i in range(0, 11):
                    self.getValues.append(self.list_variables_ut[i].get())
                DataBase.update_info("0", *self.getValues, sign_db=None)


# Subframe for sending emails
class FifthFrame(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.session = Window.session
        self.q = Queue()
        self.Send_email()
        self.checkLogin()

    def Send_email(self):

        self.s_lables = ['Naslov imejla:', 'Tekst imejla:', 'Kome:', 'Indeks:']
        # Variables
        self.var_om = StringVar() # for drop_m
        self.var_om1 = StringVar() # for drop_m1
        self.var_om.set('Svi')
        self.var_om.trace('w', self.checkDrop)

        # OPTIONS FOR THE GENERATIONS OPTIONMENU
        self.gen_lst = DataBase.read_gen()

        # CREATES 2 FRAMES FOR BETTER STRUCTURE
        self.local_frame1 = ttk.Frame(self)
        self.s_w = ttk.LabelFrame(self.local_frame1, text="Imejl", width = 200, height = 500)
        self.s_w.configure(labelanchor = NSEW)
        self.inner_frame = ttk.Frame(self.local_frame1) # so that pbar and label can fit

        self.local_frame = ttk.Frame(self)
        self.s_w1 = ttk.LabelFrame(self.local_frame, text="Korisnicima", width = 100, height = 300)
        self.s_w1.configure(labelanchor = NSEW)
        self.s_w2 = ttk.LabelFrame(self.local_frame, text='Slanje upozorenja', width=100, height=100)
        self.s_w2.configure(labelanchor=NSEW)

        self.l_title = [ttk.Label(self.s_w, text=i) for i in self.s_lables[:2]]
        self.l_title1 = [ttk.Label(self.s_w1, text=i) for i in self.s_lables[2:]]
        self.l_title_e = ttk.Entry(self.s_w, width = 75)
        self.s_textbox = Text(self.s_w, height=25, width=70)
        self.drop_m = OptionMenu(self.s_w1, self.var_om, 'Svi', 'Generacija')
        self.drop_m.config(width=10)
        # self.drop_m1 = OptionMenu(self.s_w1, self.var_om1, *self.gen_lst)

        # self.s_w
        self.l_title[0].grid(row=0, column=0, padx=10, pady=5, sticky=W)
        self.l_title_e.grid(row=0, column=1, padx=10, pady=5, sticky=W)
        self.l_title[1].grid(row=1, column=0, padx=5, pady=5)
        self.s_textbox.grid(row=2, column=0, rowspan=2, columnspan=2, padx=10, pady=10)
        # self.s_w1
        self.l_title1[0].grid(row=0, column=0, padx=10, pady=5)
        self.drop_m.grid(row=0, column=1, padx=10, pady=5)
        self.l_title1[1].grid(row=2, column=0, padx=5, pady=5)

        self.button_send = ttk.Button(self.s_w1, text="Pošalji mejl", command = self.sendEmailInfo)
        self.button_send.grid(row=4, column=0, padx=5, pady=5)
        self.warning_desc = ttk.Label(self.s_w2, text='Molimo Vas da sačekate\nsa slanjem prethodnih mejlova\npre uključivanaj ove opcije.')
        self.warning_desc.grid(row=0, column=0)
        self.button_warning = ttk.Button(self.s_w2, text='Upozorenje', command=self.sendEmailWarning)
        self.button_warning.grid(row=1, column=0, padx=5, pady=10)

        self.warning_l = ttk.Label(self.s_w1, text='')
        self.warning_l.grid(row=6, column=0)

        # PROGRESSBAR AND LABEL FRO SENDING OUT EMAILS
        self.pbar = ttk.Progressbar(self.inner_frame, value=0, maximum=100, length=300)
        # self.pbar.grid(row=0, column=0, sticky=W, padx=10)
        self.pbar.pack(side=LEFT)
        self.label_progress = ttk.Label(self.inner_frame, text='Pokazuje slanje mejlova')
        # self.label_progress.grid(row=0, column=1, sticky=W, padx=10)
        self.label_progress.pack(side=LEFT, padx=10)
        self.inner_frame.grid(row=1, column=0)

        self.s_w.grid(row=0, column=0, padx=10, pady=10)
        self.s_w1.grid(row=0, column=0, pady=10)
        self.s_w2.grid(row=1, column=0, pady=10)
        self.local_frame.grid(row=0, column=1)
        self.local_frame1.grid(row=0, column=0)

    def sendEmailWarning(self):
        # lst = []
        self.amount=1
        lst = DataBase.getDue()
        print('Za upozorenje ', lst)
        if len(lst)==0:
            messagebox.showinfo('Obaveštenje', 'Lista knjiga s kašnjenjem je prazna')
        else:
            self.num_mail = len(lst)
            self.pbar['maximum'] = self.num_mail
            # security is used if a connection error occures
            # it receives a list of all the tuples (email, book...) which weren't sent
            # security = Sending.sendWarning(Window.session, lst, self.q)
            p = Process(target=Sending.send_warning, args=(Window.session, lst, self.q))
            p.start()
            self.uppbar_warning()

    def sendEmailInfo(self, *args):
        # lst = []
        self.amount = 1
        sub = self.l_title_e.get()
        text = self.s_textbox.get(1.0, END)
        if not sub or len(text) == 0:
            if not sub:
                messagebox.showwarning('Upozorenje', 'Zaboravili ste da unesete naslov poruke.')
            else:
                messagebox.showwarning('Upozorenje', 'Zaboravili ste da unesete tekst poruke.')
        else:
            if self.var_om.get() == 'Svi':
                lst = DataBase.read_email_all() # gets emails as a list of tuples
                print(lst)
                self.num_mail = len(lst)
                self.pbar['maximum'] = self.num_mail
                # security is used if a connection error occures
                # it receives a list of all the emails which weren't sent
                # Sending.sendInfo(Window.session, lst, sub, text, self.q)
                p = Process(target= Sending.send_info, args=(Window.session, lst, sub, text, self.q))
                p.start()
                self.uppbar_info()
            else:
                gen = self.var_om1.get() # returns ('09',) as a string, not a tuple element
                print(gen)
                if gen == "" or gen == None:
                    messagebox.showerror('Greška', 'Ne postoji spisak generacija.')
                else:
                    gen_1 = [s for s in gen.split("'") if s.isdigit()] # splits that string on quotes and checks which part are digits -> returns '09' as a string
                    print(gen_1)
                    lst = DataBase.read_email_gen(*gen_1) # returns a list of tuples
                    print('lst u info mejl ', lst)
                    self.num_mail = len(lst)
                    self.pbar['maximum']=self.num_mail
                    sub = self.l_title_e.get()
                    text = self.s_textbox.get(1.0, END)
                    p = Process(target=Sending.send_info, args=(Window.session, lst, sub, text, self.q))
                    p.start()
                    self.uppbar_info()

    # SETS NEWLY ENTERED VALUES USING _SETIT CLASS FROM TKINTER
    def refresh(self):
        self.gen_lst = DataBase.read_gen()
        print('Printing self,gen_lst', self.gen_lst)
        self.drop_m1['menu'].delete(0, 'end')
        menu = self.drop_m1['menu']
        for gen in self.gen_lst:
            menu.add_command(label=gen,
                             command=_setit(self.var_om1, gen[0], None))

    # UPDATES PROGRESSBAR
    def uppbar_info(self):
        self.id = self.master.after(100, self.uppbar_info)
        try:
            x = self.q.get_nowait()
            if x == 0:
                messagebox.showinfo('Obaveštenje', 'Svi mejlovi su uspešno poslati')
                self.master.after_cancel(self.id)
                self.label_progress.config(text='Trenutno se ne šalju mejlovi.')
                del self.id
            elif x == 2:
                l = self.q.get_nowait()
                sub = self.q.get_nowait()
                text = self.q.get_nowait()
                self.master.after_cancel(self.id)
                DataBase.unsent_store(l, sub, text)
                messagebox.showerror("Greška", "Došlo je do greške u vezi sa internetom."
                                                   "Neposlate poruke su sačuvane u sistemu i biće poslate kasnije.")
                del self.id
            else:
                self.pbar.step()
                self.label_progress.config(text='Obaveštenja: Šalje se mejl ' + str(self.amount) + ' od ' + str(self.num_mail))
                self.amount += 1
        except Empty:
            pass

    def uppbar_warning(self):
        self.id = self.master.after(100, self.uppbar_warning)
        try:
            x = self.q.get_nowait()
            if x == 0:
                messagebox.showinfo('Obaveštenje', 'Svi mejlovi su uspešno poslati')
                self.master.after_cancel(self.id)
                del self.id
                self.label_progress.config(text='Trenutno se ne šalju mejlovi.')
            elif x == 2: # error, next item is a list of unsent emails
                lst = self.q.get_nowait()
                DataBase.unsent_store(lst, None, None)
                self.master.after_cancel(self.id)
                del self.id
                messagebox.showerror("Greška", "Došlo je do greške u vezi sa internetom."
                                                   "Neposlate poruke su sačuvane u sistemu i biće poslate kasnije.")
            else:
                self.pbar.step()
                self.label_progress.config(text='Upozorenja: Šalje se mejl ' + str(self.amount) + ' od ' + str(self.num_mail))
                self.amount += 1
        except Empty:
            pass

    # REMOVES / ADDS AN OPTIONMENU AND BUTTON FOR ADDITIONAL SPECIFICATION
    def checkDrop(self, *args):
        if self.var_om.get()=='Svi':
            try:
                self.drop_m1.grid_forget()
                self.button_osv.grid_forget()
            except:
                pass
        else:
            if len(self.gen_lst) > 0:
                print(*self.gen_lst)
                self.drop_m1 = OptionMenu(self.s_w1, self.var_om1, *self.gen_lst)
                self.drop_m1.grid(row=2, column=1, padx=5, pady=5, sticky=W)
                self.button_osv = ttk.Button(self.s_w1, text='Osvezi', command=self.refresh)
                self.button_osv.grid(row=4, column=1)
                self.checkLogin()
            else:
                pass

    # DISABLES ALL "INTERNET" BUTTONS/OPTIONS IF THE USER ISN'T LOGGED IN
    def checkLogin(self):
        if not Window.session:
            self.button_send.config(state=DISABLED)
            self.button_warning.config(state=DISABLED)
            try:
                self.button_osv.config(state=DISABLED)
            except AttributeError:
                pass
            self.warning_l.config(text='Morate biti ulogovani\nkako biste koristili ove opcije.')

        else:
            self.button_send.config(state=NORMAL)
            self.button_warning.config(state=NORMAL)
            try:
                self.button_osv.config(state=NORMAL)
            except AttributeError:
                pass
            self.warning_l.config(text='')

# Subframe for deleting users
class SixthFrame(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.delUser()

    # Frame that hosts all widgets
    def delUser(self):
        self.du_strVar = StringVar()
        self.du_strVar.trace('w', self.du_loadInfo)
        self.user_exists = 0

        self.du_label = ttk.Label(self, text='Unesite indeks korisnika:')
        self.du_label.grid(row=0, column=0, sticky=W, padx=10, pady=10)
        self.du_index = ttk.Entry(self, textvariable=self.du_strVar)
        self.du_index.grid(row=0, column=1, padx=10, pady=10)

        self.du_label_names = ["Prezime:", "Ime:", "Br. lic karte:", "JMBG:", "Telefon:", "Mobilni:", "E-mail:",
                           "Ulica:", "Broj:", "Grad:"]

        self.du_labels = [ttk.Label(self, text=l, anchor=W) for l in
                          self.du_label_names]
        self.du_entries = [ttk.Entry(self, state=DISABLED) for l in self.du_label_names]

        for i in range(0, len(self.du_label_names)):
            if i >= 7:
                self.du_labels[i].grid(row=i-6, column=3, sticky=W, padx=10, pady=10)
                self.du_entries[i].grid(row=i-6, column=4, padx=10, pady=10)
            else:
                self.du_labels[i].grid(row=i+1, column=1, sticky=W, padx=10, pady=10)
                self.du_entries[i].grid(row=i+1, column=2, padx=10, pady=10)


        self.du_button = ttk.Button(self, text='Izbrisi korisnika', command = self.delete_users)
        self.du_button.grid(row=10, column=2, padx=10, pady=10)

    # Loads information of user into the entries
    def du_loadInfo(self, *args):

        for i in range(0, len(self.du_entries)):
            self.du_entries[i].config(state=NORMAL)

        for i in range(0, len(self.du_entries)):
            self.du_entries[i].delete(0, END)

        index = self.du_strVar.get()
        li_list = DataBase.read_db(index, None, None, None, None, None, None, None, None)
        print('du_loadInfo funckija:', li_list)

        if len(li_list) > 0:
            self.user_exists=1
            j = 0
            for i in range(0, len(self.du_entries)):
                self.du_entries[i].insert(END, li_list[0][j])
                j = j + 1
            for i in range(0, len(self.du_entries)):
                self.du_entries[i].config(state=DISABLED)
        else:
            self.user_exists=0
            for i in range(0, len(self.du_entries)):
                self.du_entries[i].config(state=DISABLED)
            return 0

    # Deletes user if possible
    # checks beforehand if the user still owes books
    def delete_users(self):
        if self.user_exists:
            x = DataBase.delete_user(self.du_index.get())
            if x:
                messagebox.showerror('Greška','Nije moguće izbrisati korisnika, jer još duguje knjige.')
            else:
                messagebox.showinfo('Obaveštenje', 'Korisnik je uspešno izbrisan iz baze podataka.')
                for i in range(0, len(self.du_entries)):
                    self.du_entries[i].config(state=NORMAL)
                for i in range(0, len(self.du_entries)):
                    self.du_entries[i].delete(0, END)
                for i in range(0, len(self.du_entries)):
                    self.du_entries[i].config(state=DISABLED)
        else:
            messagebox.showerror('Greška', 'Unesite ispravan indeks korisnika.')

# event function that performs a log out before closing the window
def on_closing():
    try:
        if Sending.p.is_alive():
            if messagebox.askyesno('Upozorenje', 'Slanje mejlova još nije okončano.\n'
                                                 'Da li ipak želite da ugasite program? '
                                                 '\n(Neposlati mejlovi će biti sačuvani za slanje '
                                                 '\nprilikom sledećeg pokretanja programa)'):
                Sending.stop_process()
                if Sending.current_info:
                    new_lst = [i for i in Sending.glst if not i in Sending.current_info]
                    sub = Sending.subject
                    text = Sending.body
                    DataBase.unsent_store(new_lst, sub, text)
                else:
                    new_lst = [i for i in Sending.glst if not i in Sending.current_warning]
                    DataBase.unsent_store(new_lst, None, None)

                if Window.session:
                    Sending.sign_out(Window.session)
                root.destroy()
    except:
        if messagebox.askokcancel("Izlaz", "Da li želite da ugasite program?\n"
                                           "Bićete automatski izlogovani prilikom napuštanja programa."):
            if Window.session:
                Sending.sign_out(Window.session)
            root.destroy()

if __name__ == '__main__':

    freeze_support() # if I ever decide to use CX_freeze, to make multiprocesses work as exe
    login = Tk()
    login.geometry('300x140')
    login.iconbitmap(default='hq_logo_icon.ico')
    lg = Login(login)
    login.mainloop()
    # this part was because of some serious errors, dunno if it is needed any longer
    while True:
        try:
            if login.state == 'normal':
                pass
            else:
                break
        except:
            break

    root = tix.Tk()
    root.geometry("920x580")
    root.resizable(width=FALSE, height=FALSE)
    root.iconbitmap(default='hq_logo_icon.ico')
    # DataBase.deleteTables()
    # DataBase.create_table()
    photo = PhotoImage(file='help.png')
    new_photo = photo.subsample(30, 30)
    app = Window(root) # root se prosledjuje u __init__ i zauzima mesto master
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

