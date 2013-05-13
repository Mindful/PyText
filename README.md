PyText
======

A Python application that wraps email-to-text functions into a messaging client. Fetches are done using IMAP server implementations, and mail is sent via SMTP. The application functionally wraps an email account into a way to easily communicate with someone using a phone. Eligable IMAP servers:

 - Gmail: stable, and works reliably. Most tests are done using Gmail, so it's the most likely to work.
 - Yahoo: Yahoo's servers usually work, although they're not as reliable as Gmail's.
 - AOL: Does not work (yet), as AOL seems to have neglected to implement partial matching in IMAP searches, which PyText uses to identify mms/sms to email messages.


The application is in early stages right now, but has some basic functionalities. Once the messaging GUI is finished, testers will most certainly be welcome.