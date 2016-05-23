import requests
import time
import bs4
import multiprocessing

# URL is GLOBAL

# SESSION
# login.php
# redirects to redirect.php with POST method

# LOGIN
# redirect.php
# "Referer":"http://webmail.fil.bg.ac.rs/src/login.php"
# "User-Agent":"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36"

# LOGOUT
# http://webmail.fil.bg.ac.rs/src/signout.php with GET method

def connecting(username, password, q):

    global r
    global url

    username = username
    password = password

    s = requests.Session()
    s.headers.update({"User-Agent":"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 "
                                   "(KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36"})

    payload = {"login_username": username, "secretkey": password, "js_autodetect_results": "1",
               "just_logged_in": "1"}
    session_url = url+'login.php'
    login_url = url+'redirect.php'

    try:
        r = s.get(session_url)
        print('Starting session: ',r.status_code)
        q.put('Starting session')
    except TimeoutError:
        return 2

    # allow_redirects=False omogucava Location u headers
    r = s.post(login_url, data=payload, allow_redirects=False)
    if r.content:
        soup = bs4.BeautifulSoup(r.content, "html.parser")
        title = soup.title.string
        if 'Unknown' in title:
            print('Neuspelo logovanje')
            q.put('Neuspelo logovanje')
            return 1
    else:
        print('Logging in: ',r.status_code)
        q.put('Ulogovanje')
        # print(r.headers)
        print('Redirecting to: ',r.headers['Location'])
        q.put('Preusmeravanje')
        home_url=url+r.headers['Location']
        r = s.get(home_url)
        print('Redirected to home page: ',r.status_code)
        print('Successfully connected')
        q.put('Logovanje uspelo')
        print('Printing s in connecting()', s)

        return s


def send_email(s, lst, *args):

    # compose.php?mailbox=INBOX&amp;startMessage=1 otvaranje sablona za pisanje
    global r
    global url

    print(lst)
    # recipient = 'some@email.com'
    recipient = lst[0]
    subject = 'Zaduzenje'
    body = "Postovani/Postovana,\n\n" \
           "Ovo je automatska poruka koja Vas obavestava da ste se zaduzili za knjigu " \
           ""+lst[1]+": '"+lst[2]+"', signatura: "+str(lst[3])+".\n" \
            "Datum uzimanja: "+lst[4]+"\nRok za vracanje: "+lst[5]+"\n\n" \
            "S postovanjem,\nMilan Todorovic\n\nBiblioteka Katedre za germanistiku\nFiloloski fakultet\n" \
            "Univerzitet u Beogradu\nStudentski trg 3\nTel: 011/2021-698\nRadno vreme: 9.00-17.00"

    files = {"startMessage":(None, "1"),
             "session":(None, "1"),
             "passed_id":(None,""),
             "send_to":(None, recipient),
             "send_to_cc":(None, ""),
             "send_to_bcc":(None, ""),
             "subject":(None, subject),
             "mailprio":(None, "3"),
             "body":(None, body),
             "send":(None, "Send"),
             "attachfile":("",""),
             "MAX_FILE_SIZE":(None, "20971520"),
             "username":(None, "milan.todorovic"),
             "smaction":(None, ""),
             "mailbox":(None, "INBOX"),
             "composesession":(None, "1"),
             "querystring":(None, "mailbox=INBOX&startMessage=1")}

    left_side = url+'left_main.php'
    right_side = url+'right_main.php'
    l = s.get(left_side)
    r = s.get(right_side)
    print('Loading left frame: ',l.status_code)
    print('Loading right frame: ',r.status_code)

    time.sleep(1)
    compose = url + 'compose.php?mailbox=INBOX&amp;startMessage=1'
    r = s.get(compose)
    print('Enterying "Compose": ',r.status_code)

    send = url+'compose.php'
    time.sleep(5)
    r = s.post(send, files=files, allow_redirects=False)
    print('Mail sent: ',r.status_code)
    print('Redirecting to: ',r.headers['Location'])
    r = s.get(r.headers['Location'])
    print('Redirected to home page: ',r.status_code)
    print('User successfully notified about taken book.')


def send_warning(s, lst, q, *args):
    # q is Queue()
    url = 'http://webmail.fil.bg.ac.rs/src/'

    subject = 'Kasnjenje'

    for i in lst:
        q.put(1)
        recipient=i[0]
        body='Postovani,\n\nKasnite s vracanjem knjige '+str(i[1])+': "'+str(i[2])+'", signatura: '+str(i[3])+' uzete ' \
                ''+str(i[4])+'.\n Rok za vracanje je bio '+str(i[5])+'.\n' \
                'Molim Vas da je vratite u sto kracem roku.\n' \
                'S postovanjem,\n' \
                'Milan Todorovic\n\n' \
                'Biblioteka Katedre za germanistiku\n' \
                'Filoloski fakultet\n' \
                'Univerzitet u Beogradu\nStudentski trg 3\n' \
                'Tel: 011/2021-698\nRadno vreme: 9.00-17.00'

        files = {"startMessage": (None, "1"),
                     "session": (None, "1"),
                     "passed_id": (None, ""),
                     "send_to": (None, recipient),
                     "send_to_cc": (None, ""),
                     "send_to_bcc": (None, ""),
                     "subject": (None, subject),
                     "mailprio": (None, "3"),
                     "body": (None, body),
                     "send": (None, "Send"),
                     "attachfile": ("", ""),
                     "MAX_FILE_SIZE": (None, "20971520"),
                     "username": (None, "milan.todorovic"),
                     "smaction": (None, ""),
                     "mailbox": (None, "INBOX"),
                     "composesession": (None, "1"),
                     "querystring": (None, "mailbox=INBOX&startMessage=1")}

        left_side = url + 'left_main.php'
        right_side = url + 'right_main.php'
        l = s.get(left_side)
        r = s.get(right_side)
        print('Loading left frame: ', l.status_code)
        print('Loading right frame: ', r.status_code)

        time.sleep(1)
        compose = url + 'compose.php?mailbox=INBOX&amp;startMessage=1'
        r = s.get(compose)
        print('Enterying "Compose": ', r.status_code)

        send = url + 'compose.php'
        time.sleep(5)
        r = s.post(send, files=files, allow_redirects=False)
        print('Mail sent: ', r.status_code)
        print('Redirecting to: ', r.headers['Location'])
        r = s.get(r.headers['Location'])
        print('Redirected to home page: ', r.status_code)
        print('Warning successfully sent.')
    q.put(0)


def send_info(s, lst, sub, text, q):
    # q is Queue()
    url = 'http://webmail.fil.bg.ac.rs/src/'

    subject = sub
    body = text

    for i in lst:
        q.put(1)
        recipient = i[0]

        files = {"startMessage": (None, "1"),
                     "session": (None, "1"),
                     "passed_id": (None, ""),
                     "send_to": (None, recipient),
                     "send_to_cc": (None, ""),
                     "send_to_bcc": (None, ""),
                     "subject": (None, subject),
                     "mailprio": (None, "3"),
                     "body": (None, body),
                     "send": (None, "Send"),
                     "attachfile": ("", ""),
                     "MAX_FILE_SIZE": (None, "20971520"),
                     "username": (None, "milan.todorovic"),
                     "smaction": (None, ""),
                     "mailbox": (None, "INBOX"),
                     "composesession": (None, "1"),
                     "querystring": (None, "mailbox=INBOX&startMessage=1")}

        left_side = url + 'left_main.php'
        right_side = url + 'right_main.php'
        l = s.get(left_side)
        r = s.get(right_side)
        print('Loading left frame: ', l.status_code)
        print('Loading right frame: ', r.status_code)

        time.sleep(1)
        compose = url + 'compose.php?mailbox=INBOX&amp;startMessage=1'
        r = s.get(compose)
        print('Enterying "Compose": ', r.status_code)

        send = url + 'compose.php'
        time.sleep(1)
        r = s.post(send, files=files, allow_redirects=False)
        print('Mail sent: ', r.status_code)
        print('Redirecting to: ', r.headers['Location'])
        r = s.get(r.headers['Location'])
        print('Redirected to home page: ', r.status_code)
        print('Info successfully sent.')
    q.put(0)

def sign_out(s):
    # signout.php
    global url

    so_url = url + 'signout.php'

    r = s.get(so_url)
    print('Signed out: ', r.status_code)
    # returns None so that the Session object can be checked later on
    return None

# starts a multiprocess for sending e-mails
def sendInfo(s, lst, sub, text, q):
    global p
    p = multiprocessing.Process(target=send_info, args=(s, lst, sub, text, q))
    p.start()

# starts a multiprocess for sending e-mails
def sendWarning(s, lst, q):
    global p
    p = multiprocessing.Process(target=send_warning, args=(s, lst, q))
    p.start()

url = 'http://webmail.fil.bg.ac.rs/src/'
p = None