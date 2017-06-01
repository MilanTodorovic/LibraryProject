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

<h1>Updates</h1>

<h2>Version 1.3</h2>
Some radical changes in the structure of the Main.py file. The <b>Window</b> class broken down into multiple classes, each for every individual <b>ttk.Notebook</b> frame. This might result in some bugs, but I hope it won't.

<h2>Version 1.4.5</h2>
Added a mechanism to store unsend Emails in case of connection issues or something similar.<br>
Not all Emails can be stored and some fucntions don't work.

<h2>Version 1.5</h2>
Changes: <br>
1. Some SQLite queries and Table schemes<br>
2. New functions that store and send unsent Emails (due to connection loss, etc.)<br>
3. Toplevel window with progressbar for sending out previously unsent Emails<br>
4. Slight changes in some parts of the code<br>

<h2>Version 1.5 Hotfix</h2>
Fixed problems with multiprocessing (logging in and sending emails) and some minor code changes.

<h2>Version 1.5.6</h2>
Testing out the tix.Balloon and style feature. No important changes in the program itself.

<h2>Version 1.6.0</h2>
1. Fixed major bugs.
2. Added a new Toplevel window to display user information of the selected user in the treeview.
3. Changed some functions in the DataBase file. Broke up <b>some</b> multitool functions in favour of smaller and more specialized ones.
4. Small layout changes. More planned.

<h2>Version 1.6.1</h2>
1. Added a seperate window to manually enter the generation indicator of a students index number.
2. Split some functions in the DataBase file to make it more readable.
3. Some other minor changes which don't have any impact to the program itself.

<h1>Known issues</h1>
1. <strike>Logging in afterwards won't send emails.</strike> <br>FIXED: The session object couldn't be saved to a variable for unknown reasons
2. <strike>After getting the message, that all unsent emails were sent, the program crashes.</strike> <br>FIXED: I was using .quit() on Toplevel windows instead of .destroy()

<h1>TO DO</h1>
1. <strike>Enable saving unsent e-mails to a file/database in case of internet connection loss. (Partially done with 1.4.5)</strike><br>
2. Changes in variable names. (Make them more readable and informative)<br>
3. Some changes to the structure of the code and maybe some more features.<br>
4. Add a log. (Either as a seperate window and as a .txt file)<br>
5. <strike>Add tix.Balloon (hovering frame to display helpful information)</strike> (maybe i will add some more)<br>
6. Break up big multitool functions in favour of smaller ones. (A lot of wokr.)<br>
7. <strike>Add a custom icon to the window. (self.iconbitmap(self, default='icon.ico'))</strike><br>
