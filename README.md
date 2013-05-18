PyText
======

A Python application that wraps email-to-text functions into a messaging client. Fetches are done using IMAP server implementations, and mail is sent via SMTP. The application functionally wraps an email account into a way to easily communicate with someone using a phone. Eligable IMAP servers:

 - Gmail: stable, and works reliably. Most tests are done using Gmail, so it's the least likely to run into unexpected problems.
 - Yahoo: Yahoo's servers usually work, although they're not as reliable as Gmail's, probably because they're primarily for mobile use.
 - AOL: Does not work right now, as AOL seems to have neglected to implement partial matching in IMAP searches*, which PyText uses to identify mms/sms to email messages.


The application is an early beta right now, and I'm taking a break from developing it. That said, while it may be missing a lot of polish (settings must be changed in the config file, for example), it's entirely functional. Feedback and bug reports are welcome. Note that while a Windows installer is available, I would prefer any testing be done using the application as pure Python, both for the purpose of reporting exceptions and because I'm relatively new to cx_Freeze.

*The [IMAP RFC](http://tools.ietf.org/html/rfc3501#section-6.4.4) specifies that searches must match substrings, and I find it difficult to believe that AOL has deviated from matching IMAP specifications. However, all tests seem to indicate that AOL's imap searches do not support substring matching, so I'm at a loss here.

Eventual goals:

 - Settings menu
 - Edit contacts
 - Log alerts on received messages (even from unknown addresses)
 - Support for adding contacts by received address, as logged
 - GUI improvements
 - Option to flag fetched texts instead of just deleting them (or not)
 - Possibly look at implementing GSM multipart SMS headers
 - Timestamps on messages
 - Alert the user to (and don't save) unsuccessful outgoing messages
 - Fetch copies of sent messages from the server so we rely less on local storage
