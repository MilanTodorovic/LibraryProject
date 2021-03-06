import sqlite3
import datetime
from tkinter import messagebox

def create_table():
    conn = sqlite3.connect('cirkulacija.db')
    c = conn.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS cirkStudents(surname TEXT, name TEXT, index_num TEXT PRIMARY KEY, '
              'id_num TEXT, jmbg TEXT, telephone TEXT, mobile TEXT, email TEXT, i_value INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS addressStudents(index_num TEXT PRIMARY KEY, street TEXT, house_num TEXT, '
              'city TEXT, i_value INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS takenBooks(index_num TEXT, title TEXT, author TEXT, sign INTEGER, '
              'date_taken TEXT, date_bring_back TEXT, PRIMARY KEY(sign, index_num))')
    # It seems that putting a TEXT field in the first place in a Composit key doesn't work
    # therefore a INT field in placed first
    c.execute('CREATE TABLE IF NOT EXISTS dueBooks(index_num TEXT PRIMARY KEY, title TEXT, author TEXT, sign INTEGER, '
              'date_taken TEXT, '
              'date_bring_back TEXT)')
    # maybe change from autoincrement to MAX(i_value) thingy
    c.execute('CREATE TABLE IF NOT EXISTS generations(index_part TEXT UNIQUE, i_value INTEGER PRIMARY KEY AUTOINCREMENT)')
    c.execute('CREATE TABLE IF NOT EXISTS lendBookEmails(sign INTEGER PRIMARY KEY)')
    # last three store unsent emails
    c.execute('CREATE TABLE IF NOT EXISTS unsentWarnings(email TEXT, author TEXT, book TEXT, sign INTEGER, '
              'date_taken TEXT, date_back TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS unsentInformation(email TEXT, number INTEGER, PRIMARY KEY(number, email))')
    c.execute('CREATE TABLE IF NOT EXISTS sub_msg_emails(sub TEXT, msg TEXT, number INTEGER PRIMARY KEY)')

    c.close()
    conn.close()

def data_entry(surname, name, index_num, id_num, jmbg,
               tel, mob, email, street, house_num, city, gen):

    conn = sqlite3.connect('cirkulacija.db')
    c = conn.cursor()

    # gen is either returned from determine_generation (through some functions in Main.py),
    # if found, or manually enetred by the user
    # print(gen)
    c.execute('INSERT OR IGNORE INTO generations(index_part, i_value) VALUES(?, ?)', (gen,))
    ivalue = c.execute('SELECT i_value FROM generations WHERE index_part = ?', (gen,)).fetchone()[0]

    c.execute('INSERT INTO cirkStudents(surname, name, index_num, id_num, jmbg, telephone, mobile, email, i_value)'
              'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (surname, name, index_num, id_num, jmbg, tel, mob, email, ivalue))

    c.execute('INSERT INTO addressStudents(index_num, street, house_num, city, i_value) VALUES '
              '(?, ?, ?, ?, ?)', (index_num, street, house_num, city, ivalue))

    conn.commit()
    messagebox.showinfo("Obaveštenje", "Korisnik uspešno unet:\n"+str(name)+" "+str(surname))
    c.close()
    conn.close()

def determine_generation(index_num):

    conn = sqlite3.connect('cirkulacija.db')
    c = conn.cursor()

    if index_num.startswith('0') or index_num.startswith('1'):
        c.execute('INSERT OR IGNORE INTO generations(index_part) VALUES(?)', (index_num[:2],))
        ivalue = c.execute('SELECT i_value FROM generations WHERE index_part = ?', (index_num[:2],)).fetchone()[0]
    elif index_num.startswith('2'):
        c.execute('INSERT OR IGNORE INTO generations(index_part) VALUES(?)', (index_num[:4],))
        ivalue = c.execute('SELECT i_value FROM generations WHERE index_part = ?', (index_num[:4],)).fetchone()[0]
    else:
        ivalue = 0

    c.close()
    conn.close()
    return ivalue

def take_a_book(index_num, title, author, sign, days):

    conn = sqlite3.connect('cirkulacija.db')
    c = conn.cursor()

    date_taken = str(datetime.date.today().strftime("%d-%m-%Y"))
    date_bring_back = str((datetime.date.today() + datetime.timedelta(int(days))).strftime("%d-%m-%Y"))

    data = c.execute('SELECT COUNT(*) FROM cirkStudents WHERE index_num = ?', (index_num,)).fetchone()

    if data[0] == 0:
        messagebox.showerror("Greska", "Student ne postoji u bazi podataka")
        lst = []

    else:
        try:
            c.execute('INSERT INTO takenBooks(index_num, title, author, sign, date_taken, date_bring_back) '
              'VALUES (?, ?, ?, ?, ?, ?)', (index_num, title, author, sign, date_taken, date_bring_back))

            messagebox.showinfo("Obaveštenje",
                                "Knjiga " + str(author) + ": " + str(title) + " je iznajmljena korisniku " + str(
                                    index_num))
            # Send out a confirmation E-Mail
            user = c.execute("SELECT email FROM cirkStudents WHERE index_num=?", (index_num,)).fetchone()[0]
            # for independent processing
            # Process(target=Sending.send_email, args=([user, author, title, sign, date_taken, date_bring_back])).start()
            lst = user, author, title, sign, date_taken, date_bring_back

        except sqlite3.IntegrityError:
            messagebox.showerror("Greska", "Korisnik je vec zaduzen za jednu knjigu.")
            lst = []

    conn.commit()
    c.close()
    conn.close()

    if len(lst) == 0:
        pass
    else:
        return lst


def read_db(index_num=None, name_db = None, surname_db = None, city_db = None, aut_db = None,
            book_db = None, sign_db = None, date_db = None, table_chosen="Studenti"):

    conn = sqlite3.connect('cirkulacija.db')
    c = conn.cursor()

    arguments = [index_num, name_db, surname_db, city_db, aut_db, book_db, sign_db, date_db]
    i = 0
    for a in arguments:
        if a == None or a == "":
            if i == 0:
                index_num = "%"
            elif i == 1:
                name_db = "%"
            elif i == 2:
                surname_db = "%"
            elif i == 3:
                city_db = "%"
            elif i == 4:
                aut_db = "%"
            elif i == 5:
                book_db = "%"
            elif i == 6:
                sign_db = "%"
            else:
                date_db = "%"
        else:
            if i == 0:
                if table_chosen != None:
                    index_num = index_num + "%"
                else:
                    index_num = index_num
            elif i == 1:
                name_db = name_db + "%"
            elif i == 2:
                surname_db = surname_db + "%"
            elif i == 3:
                city_db = city_db + "%"
            elif i == 4:
                aut_db = aut_db + "%"
            elif i == 5:
                book_db = book_db + "%"
            elif i == 6:
                sign_db = sign_db + "%"
            else:
                date_db = date_db + "%"
        i = i+1


    if table_chosen == "Studenti":
        c.execute('SELECT (cirkStudents.surname||", "||cirkStudents.name) , cirkStudents.index_num, '
                  '(addressStudents.street||" "||addressStudents.house_num||", "||addressStudents.city), cirkStudents.id_num, '
                  'cirkStudents.jmbg, cirkStudents.telephone, cirkStudents.mobile, cirkStudents.email FROM cirkStudents INNER JOIN addressStudents'
                  ' ON addressStudents.index_num = cirkStudents.index_num WHERE cirkStudents.index_num LIKE ? AND cirkStudents.name LIKE ? '
                  'AND cirkStudents.surname LIKE ? ORDER BY cirkStudents.surname', (index_num, name_db, surname_db))
        try:
            new_data= c.fetchall()
        except:
            new_data = []
    elif table_chosen == "Adrese":
        c.execute('SELECT cirkStudents.surname, cirkStudents.name, cirkStudents.index_num, (addressStudents.street||" "||addressStudents.house_num), '
                  'addressStudents.city FROM addressStudents INNER JOIN cirkStudents ON cirkStudents.index_num = addressStudents.index_num '
                  'WHERE addressStudents.index_num LIKE ? AND addressStudents.city LIKE ? AND cirkStudents.name LIKE ? '
                  'AND cirkStudents.surname LIKE ?', (index_num, city_db, name_db, surname_db))
        try:
            new_data= c.fetchall()
        except:
            new_data = []
    elif table_chosen == "Iznajm. knjige":
        c.execute('SELECT (cirkStudents.surname||", "||cirkStudents.name), takenBooks.* FROM takenBooks INNER JOIN cirkStudents '
                  'ON cirkStudents.index_num = takenBooks.index_num WHERE takenBooks.index_num LIKE ? AND takenBooks.author LIKE ?'
                  'AND takenBooks.title LIKE ? AND takenBooks.sign LIKE ? AND (takenBooks.date_taken LIKE ? OR takenBooks.date_bring_back LIKE ?)'
                  'ORDER BY takenBooks.date_taken', (index_num, aut_db, book_db, sign_db, date_db, date_db))
        try:
            new_data= c.fetchall()
        except:
            new_data = []
    else:
        # LOADS INFORMATION FOR CORRECTION
        c.execute('SELECT cirkStudents.surname, cirkStudents.name, cirkStudents.id_num, cirkStudents.jmbg, '
                  'cirkStudents.telephone, cirkStudents.mobile, cirkStudents.email,'
                  'addressStudents.street, addressStudents.house_num, addressStudents.city '
                  'FROM cirkStudents INNER JOIN addressStudents '
                  'ON addressStudents.index_num = cirkStudents.index_num '
                  'WHERE cirkStudents.index_num = ?', (index_num,))
        try:
            new_data= c.fetchall()
        except:
            new_data = []

    c.close()
    conn.close()
    return new_data # Returns data

def readLendBoosk(index):

    conn = sqlite3.connect('cirkulacija.db')
    c = conn.cursor()

    c.execute(
        'SELECT author, title, sign, date_taken, date_bring_back FROM takenBooks WHERE index_num = ?', (index,))
    books = c.fetchall()

    c.close()
    conn.close()
    return books

# reads from DB to see if some books are overdue
def checkDue(mode=""):
    conn = sqlite3.connect('cirkulacija.db')
    c = conn.cursor()

    if mode == "0":
        j = 0 # counter for changes made
        for i in range(-7,0):
            c.execute('SELECT COUNT(*) FROM takenBooks WHERE date_bring_back = ?',(str((datetime.date.today()+datetime.timedelta(i)).strftime("%d-%m-%Y")),))
            data = c.fetchone()
            if data[0] > 0:
                s_data = c.execute('SELECT sign FROM takenBooks WHERE date_bring_back = ?', (str((datetime.date.today()+datetime.timedelta(i)).strftime("%d-%m-%Y")),)).fetchall()
                for d in s_data[0]:
                    c.execute('SELECT COUNT(*) FROM dueBooks WHERE sign = ?', (d,))
                    check = c.fetchone()
                    if check[0] == 0:
                        c.execute('INSERT INTO dueBooks SELECT * FROM takenBooks WHERE sign = ?',(d,))
                        j = j+1
                    else:
                        continue
            else:
                continue

        conn.commit()
        c.close()
        conn.close()

        if j == 0:
            messagebox.showinfo("Obavestenje", "Ne postoje nove knjige sa kasnjenjem.")
        else:
            messagebox.showinfo("Obavestenje", "Spisak uspesno azuriran.")
        return 0

    # CHECKS IF THERE ARE DUE BOOKS AND LOADS THEM INTO THE TREEVIEW
    elif mode == "1":
        c.execute('SELECT (cirkStudents.name||" "||cirkStudents.surname), dueBooks.index_num, (dueBooks.author||": "||dueBooks.title),'
                  'dueBooks.sign, dueBooks.date_taken, dueBooks.date_bring_back FROM cirkStudents INNER JOIN dueBooks '
                  'ON dueBooks.index_num = cirkStudents.index_num ORDER BY dueBooks.date_taken')
        due_books = c.fetchall()
        c.close()
        conn.close()
        return due_books


def check_Existance(mode=None, index=None, sign=None):
    conn = sqlite3.connect('cirkulacija.db')
    c = conn.cursor()

    new_data =[]
    if mode=="0":
        c.execute("SELECT COUNT(*) FROM cirkStudents WHERE index_num = ?", (index,))
        data = c.fetchone()
        if data[0] > 0:
            data_1 = c.execute("SELECT (surname||' '||name) FROM cirkStudents WHERE index_num=?", (index,)).fetchall()
            messagebox.showwarning("Upozorenje", "Korisnik vec postoji: "+str(data_1[0][0])+" "+str(index)+".")
        else:
            pass
        c.close()
        conn.close()
        return 0

    elif mode=="1":
        c.execute('SELECT COUNT(*) FROM takenBooks WHERE sign = ?', (sign,))
        data = c.fetchone()
        if data[0] > 0:
            data_1 = c.execute("""SELECT (author||': "'||title||'" ') FROM takenBooks WHERE sign=?""", (sign,)).fetchall()
            messagebox.showwarning("Upozorenje", "Knjiga "+str(data_1[0][0])+"je vec iznajmljena.\n Proverite signaturu.")
        else:
            new_data.append(0)
        c.close()
        conn.close()
        return new_data

    elif mode=='2':
        c.execute("SELECT COUNT(*) FROM cirkStudents WHERE index_num = ?", (index,))
        data = c.fetchone()
        if data[0] > 0:
            new_data.append(1)
            new_data.append(c.execute("SELECT (surname||' '||name) FROM cirkStudents WHERE index_num=?", (index,)).fetchall())
        else:
            new_data.append(0)
        c.close()
        conn.close()
        return new_data


def read_date(sign):
    conn = sqlite3.connect('cirkulacija.db')
    c = conn.cursor()

    c.execute('SELECT (author||": "||title), date_taken FROM takenBooks WHERE sign = ?', (sign,))
    date = c.fetchall()
    if len(date) > 0:
        c.close()
        conn.close()
        return date
    else:
        c.close()
        conn.close()


def update_info(mode = "", index_num=None, surname=None, name=None, id=None, jmbg=None, tel=None, mob=None, email=None,
                street=None, house=None, city=None, sign_db=None):
    conn = sqlite3.connect('cirkulacija.db')
    c = conn.cursor()

    if mode == "0":
        c.execute('UPDATE cirkStudents SET surname=?, name=?, id_num=?, jmbg=?, telephone=?, mobile=?, email=?'
                  ' WHERE index_num = ?', (surname, name, id, jmbg, tel, mob, email, index_num))
        conn.commit()
        c.execute('UPDATE addressStudents SET street=?, house_num=?, city=? WHERE index_num = ?', (street, house, city, index_num))
        conn.commit()
        messagebox.showinfo("Obavestenje", "Podaci su uspesno azurirani.")
    elif mode == "1":
        date_db = str(datetime.date.today().strftime("%d-%m-%Y"))
        date_bring_back = str((datetime.date.today() + datetime.timedelta(int('14'))).strftime("%d-%m-%Y"))

        data= c.execute('SELECT COUNT(*) FROM takenBooks WHERE sign = ?', (sign_db,)).fetchone()
        if data[0]>0:
            c.execute('UPDATE takenBooks SET date_taken = ?, date_bring_back = ? WHERE sign = ?', (date_db, date_bring_back,sign_db))
            conn.commit()
            messagebox.showinfo("Obaveštenje", "Knjiga "+str(sign_db)+" je produžena")

            data_ch = c.execute('SELECT COUNT(*) FROM dueBooks WHERE sign = ?', (sign_db,)).fetchone()
            if data_ch[0] > 1:
                c.execute('DELETE FROM dueBooks WHERE sign = ?', (sign_db,))
                conn.commit()
            else:
                pass

    else:
        pass

    c.close()
    conn.close()

def delete_user(index):
    conn = sqlite3.connect('cirkulacija.db')
    c = conn.cursor()

    x = c.execute('SELECT COUNT(*) FROM takenBooks WHERE index_num = ?', (index,)).fetchone()
    # if the users still ows some books, an error message pops up
    if x[0]:
        c.close()
        conn.close()
        return 1

    c.execute("DELETE FROM cirkStudents WHERE index_num = ?", (index,))
    c.execute("DELETE FROM addressStudents WHERE index_num = ?", (index,))

    # checks if the deleted user was the last one of his generation
    if index.startswith('0') or index.startswith('1'):
        x = c.execute('SELECT COUNT(*) FROM cirkStudents WHERE index_num LIKE ?', (str(index[:2])+'%',)).fetchone()
        # print(x)
        if not x[0]:
            c.execute('DELETE FROM generations WHERE index_part = ?', (index[:2],))
    elif index.startswith('2'):
        x = c.execute('SELECT COUNT(*) FROM cirkStudents WHERE index_num LIKE ?', (str(index[:4]) + '%',)).fetchone()
        if not x[0]:
            c.execute('DELETE FROM generations WHERE index_part = ?', (index[:4],))

    conn.commit()
    c.close()
    conn.close()
    return 0

# Deletes from taken, and due books(if it exists there)
def delete_info(sign=None):
    conn = sqlite3.connect('cirkulacija.db')
    c = conn.cursor()

    book = c.execute('SELECT (author||": "||title) FROM takenBooks WHERE sign = ?',(sign,)).fetchall()
    c.execute('DELETE FROM takenBooks WHERE sign = ?', (sign,))
    if book:
        messagebox.showinfo("Obavestenje", "Knjiga "+str(book[0][0])+" je uspesno razduzena.")
        c.execute('DELETE FROM dueBooks WHERE sign = ?', (sign,))
        conn.commit()
    else:
        messagebox.showerror("Greska", "Knjiga sa signaturom: " + str(sign) + " ne postoji u bazi.")



    c.close()
    conn.close()

# Reads generations for selected sending emails
def read_gen():
    conn = sqlite3.connect('cirkulacija.db')
    c = conn.cursor()

    c.execute('SELECT index_part FROM generations ORDER BY index_part')
    lst = c.fetchall()

    c.close()
    conn.close()
    if len(lst) == 0:
        return ""
    else:
        return lst

# Loads due books from DB
def getDue():
    conn = sqlite3.connect('cirkulacija.db')
    c = conn.cursor()

    c.execute('SELECT cirkStudents.email, dueBooks.author, dueBooks.title, dueBooks.sign, dueBooks.date_taken, '
              'dueBooks.date_bring_back FROM dueBooks INNER JOIN cirkStudents ON'
              ' cirkStudents.index_num=dueBooks.index_num ORDER BY cirkStudents.index_num')
    data = c.fetchall()
    print('Printing data from db ', data)
    c.close()
    conn.close()
    if len(data) > 0:
        return data
    else:
        return []

# Function for selecting e-mail addresses from certain generation of students
def read_email_all():

    conn = sqlite3.connect('cirkulacija.db')
    c = conn.cursor()

    c.execute("SELECT email FROM cirkStudents ORDER BY email")
    try:
        new_data = c.fetchall()
    except:
        new_data = []

    c.close()
    conn.close()
    return new_data

def read_email_gen(index_num):

    conn = sqlite3.connect('cirkulacija.db')
    c = conn.cursor()

    c.execute("SELECT cirkStudents.email FROM cirkStudents INNER JOIN generations "
              "ON generations.i_value = cirkStudents.i_value "
              "WHERE generations.index_part = ?", (index_num,))
    try:
        new_data = c.fetchall()
    except:
        new_data = []

    c.close()
    conn.close()
    return new_data

def deleteTables():
    conn = sqlite3.connect('cirkulacija.db')
    c = conn.cursor()
    # c.executescript('DROP TABLE IF EXISTS cirkStudents;'
    #                 'DROP TABLE IF EXISTS addressStudents;'
    #                 'DROP TABLE IF EXISTS takenBooks;'
    #                 'DROP TABLE IF EXISTS dueBooks;'
    #                 'DROP TABLE IF EXISTS generations;'
    #                 'DROP TABLE IF EXISTS lendBookEmails;'
                    # 'DROP TABLE IF EXISTS unsentInformation;'
                    # 'DROP TABLE IF EXISTS unsentWarnings;'
                    # 'DROP TABLE IF EXISTS sub_msg_emails;')
    c.executescript('DROP TABLE IF EXISTS lendBookEmails;'
                    'DROP TABLE IF EXISTS unsentInformation;'
                    'DROP TABLE IF EXISTS unsentWarnings;'
                    'DROP TABLE IF EXISTS sub_msg_emails;'
                    'DROP TABLE IF EXISTS takenBooks;')
    conn.commit()
    c.close()
    conn.close()

# Stores notifitacion emails for lending a book
# which couldn't be sent due to not being logged into the email acc
# or connection problems
def lendBookEmails(signature):
    conn = sqlite3.connect('cirkulacija.db')
    c = conn.cursor()

    c.execute('INSERT OR IGNORE INTO lendBookEmails(sign) VALUES(?)', (signature,))

    conn.commit()
    c.close()
    conn.close()

# Deletes entries from lendBookEmails if they were sent later on
def delete_lendBookEmails(signature):
    conn = sqlite3.connect('cirkulacija.db')
    c = conn.cursor()

    c.execute('DELETE FROM lendBookEmails WHERE sign = ?', (signature,))

    conn.commit()
    c.close()
    conn.close()

def read_lendBookEmails():
    conn = sqlite3.connect('cirkulacija.db')
    c = conn.cursor()

    lst = c.execute('SELECT cirkStudents.email, takenBooks.author, takenBooks.title, takenBooks.sign, takenBooks.date_taken,'
                    'takenBooks.date_bring_back FROM takenBooks INNER JOIN lendBookEmails ON lendBookEmails.sign = takenBooks.sign '
                    'INNER JOIN cirkStudents ON cirkStudents.index_num = takenBooks.index_num').fetchall()
    print("read_lendBookEmails", lst)
    if len(lst) == 0:
        c.close()
        conn.close()
        return 0
    else:
        c.close()
        conn.close()
        return lst

# Storing unsent Emails - warnings and information
def unsent_store(lst, sub=None, text=None):
    conn = sqlite3.connect('cirkulacija.db')
    c = conn.cursor()

    if sub == None:
        for l in lst:
            # Type for warnings
            c.execute('INSERT OR IGNORE INTO unsentWarnings VALUES(?,?,?,?,?,?)', (l[0],l[1],l[2],l[3],l[4],l[5]))
    else:
        # Type for information
        num = c.execute('SELECT MAX(number) FROM sub_msg_emails').fetchone()[0]
        if num == None:
            num = 0
        c.execute('INSERT INTO sub_msg_emails(sub, msg, number) VALUES(?,?, ?)', (sub, text, num+1))
        number = c.execute('SELECT number FROM sub_msg_emails WHERE sub = ?', (sub, )).fetchone()[0]
        for l in lst:
            c.execute('INSERT OR IGNORE INTO unsentInformation(email, type, number) VALUES(?,0,?)', (l[0], number))

    conn.commit()
    c.close()
    conn.close()

# Deletes sent warnings
def unsentWarning_delete(email):
    conn = sqlite3.connect('cirkulacija.db')
    c = conn.cursor()

    c.execute('DELETE FROM unsentWarning WHERE email = ?', (email,))

    conn.commit()
    c.close()
    conn.close()


# Deletes sent information
def unsentInformation_delete(email, sub):
    conn = sqlite3.connect('cirkulacija.db')
    c = conn.cursor()

    c.execute('DELETE FROM unsentInformation WHERE email = ? and number IN '
              '(SELECT number FROM sub_msg_emails WHERE sub = ?)', (email, sub))

    conn.commit()
    c.close()
    conn.close()

# Reads from unsentEmails
def unsent_read(type=None):
    conn = sqlite3.connect('cirkulacija.db')
    c = conn.cursor()

    # Info emails
    if type == 0:
        data = c.execute('SELECT unsentInformation.email, sub_msg_emails.sub, sub_msg_emails.msg '
                         'FROM unsentInformation INNER JOIN sub_msg_emails ON sub_msg_emails.number = unsentInformation.number').fetchall()
        if len(data) == 0:
            data = 0

    # Warning Emails
    elif type == 1:
        data = c.execute('SELECT * FROM unsentWarnings').fetchall()
        if len(data) == 0:
            data = 0
    else:
        # just in case i decide to add/change something
        data = 0

    c.close()
    conn.close()
    return data