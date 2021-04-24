from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import sqlite3
from sqlite3 import Error
import basics
import os
from datetime import date

hw_class_temp = []
hw_title = []
hw_class = []
due_date = []
notes = []
priority = []

def create_connection():
    con = sqlite3.connect('db.sqlite3')
    cur=con.cursor()
    cur.execute("SELECT * FROM hwapp_homework WHERE hw_user_id = 1 AND active=True")
    global hw_title
    global priority
    global notes
    global due_date
    for each in cur.fetchall():
        hw_title.append(each[1])
        priority.append(each[2])
        notes.append(each[3])
        due_date.append(each[5])
        hw_class_temp.append(each[7])

    for class1 in hw_class_temp:
        cur.execute(f"SELECT * FROM hwapp_class WHERE id={class1}")
        for each in cur.fetchall():
            hw_class.append(each[1])
            print(each)
create_connection()

def hourly_refresh_admin():
    listed= f'Homework email for Matthew.'
    for each in range(len(notes)):
        if notes[each] is not None:
            listed = listed + f"<ul><li>{hw_title[each]} for {hw_class[each]} is due at {due_date[each]}</li><ul>Notes: {notes[each]}</ul></ul>"
        else:
            listed = listed + f"<li>{hw_title[each]} for {hw_class[each]} is due at {due_date[each]}</li>"
    todays = date.today()
    message = Mail(
        from_email = basics.from_email,
        to_emails= basics.to_emails,
        subject = f"Matthew's Homework Email {todays}",
        html_content=listed
    )
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        pass
    except Exception as e:
        pass
        print(e)
    pass

hourly_refresh_admin()