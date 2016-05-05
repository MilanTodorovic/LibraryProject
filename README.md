# LibraryProject
A simple program I wrote to use in my library.

<h1>About the program</h1>
<h2>Intro</h2>
This program is written in Python 3.5.1 + Tkinter + Sqlite3 and uses Requests 2.10.0 and Beautifulsoup 4.4.1 as dependencies.<br>
It's my first real project in Python. The purpose was to learn more about Python and it's modules.<br>
It is written solely for the purpose of my library (meaning some features won't apply to any other situation) 
and everything is in Serbian (comments are in English).
<h2>Structure</h2>
The program cosists of a ttk.Notebook widget divided into multiple parts. It features many options such as storing students' 
information into tables, changing the very save information, searching and filtering of information in real-time (filtering while typing), 
sending E-mails and warning, if a book is overdue and many more.<br>
Main.py - Main window and it's features<br>
Sending.py - takes care of loggin into the email account and sending Emails<br>
DataBase.py - Database stuff
<h2>Purpose</h2>
The purpose was to modernize the work at my library. Instead of the old-fashioned way of storing and working with data and students,
this little program offers huge advantages.<br>
I am extremely happy about teh fact, that it can send Emails through our local host and show a progressbar (which is a seperate process, 
using multiprocessing and queues) of the number of sent Emails.<br>
It has a big number of error checking and prevention from breaking (mostly by the user).
