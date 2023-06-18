# Read Me- Homework App

## Distinctiveness and Complexity:
This project is an integrated task manager, and allows users to import their school calendars from common web-based applications such as Canvas and Schoology. It also allows users to import calendars from any ICS link. Once imported, users can easily check off tasks from their calendars, manually add classes and homework, and filter by class. Users are able to export these manually created events into their personal calendar via a custom ICS link that includes a hash for security measures. There is an optional email notification field, which allows end users to receive daily, weekly, or monthly emails regarding their active homework. This email comes from a custom email domain, and users are able to disable this feature if they wish. It is built with security in mind, with all views requiring the user to log in or register, and allows users to easily manage a large amount of tasks at once. It is also mobile responsive, with mobile users able to access the easy to use side navigation bar and mobile-friendly representations of their tasks and classes. There are easy to follow instructions for the integrations.

## File Information:
1. Hwapp:
    - Contains functions relating to the main page, such as adding, editing, and removing homework and classes, modifying preferences and profile, and the main HTML views. It also includes an email_helper function, which allows this system to send emails based on scheduled requests to a dedicated, secure link
2. Integrations:
    - Contains functions related to ICS processing and calendar export

## Information about the Sub Apps(how to use each one):
To start this app, enter:
1. python pip install -r requirements.txt
2. "python manage.py runserver" 
into the command line
### App 1: HW App(Homework dropdown):
1. Add a class 
    - hover over Homework -> click classes -> Add Class 
2. Add homework:
    - fill in bottom row of the assignment list
3. Check/Uncheck Homework:
    - Click checkbox under "Completed"
4. View completed HW:
    - Click "Show All Homework(Including Inactive)" at the bottom of page
5. Filter for classes by clicking the settings button in the upper right corner and selecting a class
6. Pagination- can change #/results per page and page number with the bottom navigation bars and results per page dropdown(default is 10/page)
7. Edit Class:
    - Hover over Homework, select Classes, press on the pencil to edit the class details or the trash can icon to delete the class
8. View homework for each class:
    - Click on the class name on the class page from the previous step. This may also be accomplished via the filters on the home page
#### On Mobile View:
1. Add homework with the button at the bottom of the page
2. Compacted table view of homework
3. Side menu available with large text to improve accessibility on a mobile device

### App 2: Calendar/Task Integrations:
1. Under the Calendar tab, the link to an ICS feed may be found. This does not include the Schoology or Canvas events. This link may be used to add the homework events to the user's personal calendar

### App 3: Email Notifications
1. Users can select email recurrences and preferences in the preferences section of their profile. An email will be scheduled to send once a day or week or month depending on their preferences
2. Users could receive a text(not recommended- higher bounce rate), with their homework information by sending an email to the email representation of their phone number

### System Settings:
- Profile: add/update name, email address
- Preferences: add/update email/text preferences
- About: About me, website functions
