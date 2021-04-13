import sqlite3
import os
import hashlib
import uuid
import re
import random
import string
import nltk
from tkinter import *

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('tagsets')

def create_root():
    root = Tk()
    root.title("Infinite Learner")
    root.geometry('600x300')
    root.configure(bg = 'black')

    return root

counter = 0.01
userTable = '''CREATE TABLE IF NOT EXISTS User
(UserID INTEGER PRIMARY KEY,
Username TEXT,
Password INTEGER,
Salt TEXT)
'''
#SQL statement used to create the user table in the database.

pairTable = '''CREATE TABLE IF NOT EXISTS Pairs
(Word1 TEXT,
Word2 TEXT,
Counter INTEGER)
'''
#Creates the word pair table

sentenceTable = '''CREATE TABLE IF NOT EXISTS Sentences
(Sentence TEXT,
Counter INTEGER)
'''
#Creates the sentences table

class Pairs:
    first = ""
    last = ""

    def __init__(self, first, last):
        self.first = first
        self.last = last

class Sentences:
    sentString = ""

    def __init__(self, sentence):
        self.sentString = sentence

class User:
    id = ""
    username = ""
    password = ""
    salt = uuid.uuid4().hex #creating the salt
    hash_salt = hashlib.sha512(salt.encode('utf8')).hexdigest()

    def valid_username(self):
        if len(self.username) < 3:
            print("Error: username too short.")
            return False
        if " " in self.username:
            print("Error: username must not contain spaces. Only letter and numbers are allowed.")
            return False

        return True

    def valid_password(self):
        if len(str(self.password)) < 3:
            print("Error: password is too short.")
            return False

        return True

def create_database(): #creates the database
    if not os.path.isfile("AI_DB.db"):
        database = sqlite3.connect("AI_DB.db")
        cursor = database.cursor()
        cursor.execute("PRAGMA Foreign_keys = ON")
    else:
        database = sqlite3.connect("AI_DB.db")
        cursor = database.cursor()
        cursor.execute("PRAGMA Foreign_keys = ON")

    return cursor, database

def create_tables(cursor, database, sql): #function to add the tables to the database
    cursor.execute(sql)
    database.commit()

def pass_to_table(cursor, database): #function that passes the tables to be inserted into the database to the above function (^)
    tables = [userTable, pairTable, sentenceTable]
    for table in tables:
        create_tables(cursor, database, table)

    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_w1_w2 ON Pairs(Word1, Word2)")
    database.commit()
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_s ON Sentences(Sentence)")
    database.commit()

def create_manual_ui():
    root = Tk()
    root.title("Manual Page")
    root.geometry('800x300')
    root.configure(bg = 'black')

    return root

def manual_page():
    root = create_manual_ui()

    manualFile = open("manual.txt")
    manualData = manualFile.read()
    manualFile.close()

    manual = Label(root, text = manualData, bg = 'black', fg = 'white')
    manual.grid(row = 0, column = 0)

    manButton = Button(root, text = 'Back', width = 10, bg = 'black', fg = 'white', command = root.destroy).grid(row = 1, column = 0)

    root.mainloop()

def scanning(document, window): #function for scanning the text file and adding the word pairs and sentences to the database
    cursor = create_database()

    if os.path.exists(str(document+".txt")) == False:
        existError = Label(window, text = "Document not found", bg = 'black', fg = 'red2')
        existError.grid(row = 7, column = 1)
        window.after(1000, existError.destroy)
    else:
        filehandler = open(str(document)+".txt", "r", encoding = 'utf8')
        doc = filehandler.read()
        docSplit = doc.split()
        lastWord = doc.split()[-1]

        wordIndex = 0
        for word in docSplit: #splits document into a segmented list to iterate through each word
            if word == lastWord: #prevents index error
                break

            wordPair = Pairs(word, docSplit[wordIndex + 1])

            wordIndex += 1

            pairChecker = cursor[0].execute("SELECT Word1 AND Word2 FROM Pairs WHERE Word1 = ? AND Word2 = ?", (wordPair.first, wordPair.last)) #checks if the scanned word pair is already in the database
            pairChecker2 = pairChecker.fetchall()
            if not pairChecker2:
                cursor[0].execute("INSERT INTO Pairs(Word1, Word2, Counter) VALUES(?, ?, ?)", (wordPair.first, wordPair.last, counter)) #inserts the word pair into the database
            else:
                cursor[0].execute("UPDATE Pairs SET Counter = Counter + 0.01 WHERE Word1 = ? AND Word2 = ?", (wordPair.first, wordPair.last)) #increases the counter by 0.01 when an existing pair is found.

        SIndex = 0
        PIndex = 1
        for punc in doc:
            if punc == doc[-1]:
                break
        splits = re.split("(\?|!|\.)", doc) #splits doc into sentences using regular expressions.
        for _ in range(len(splits)): #for loop to iterate the number of times there are elements in splits. '_' is used because I am not using its value
            if SIndex > len(splits) or  PIndex >= len(splits): #prevents index error
                break
            sentence = splits[SIndex] + ''.join(splits[PIndex]) #merges the sentence and its punctuation together
            SIndex += 2
            PIndex += 2

            sent = Sentences(sentence)

            sentChecker = cursor[0].execute("SELECT Sentence FROM Sentences WHERE Sentence = ?", (sent.sentString,)) #checks if the scanned word pair is already in the database
            sentChecker2 = sentChecker.fetchall()
            if not sentChecker2:
                cursor[0].execute("INSERT INTO Sentences(Sentence, Counter) VALUES(?, ?)", (sent.sentString, counter)) #inserts the sentence pair into the database
            else:
                cursor[0].execute("UPDATE Sentences SET Counter = Counter + 0.01 WHERE Sentence = ?", (sent.sentString,)) #increases the counter by 0.01 when an existing sentence is found.

        cursor[1].commit()

        scannedLabel = Label(window, text = "Scanned", bg = 'black', fg = 'green2')
        scannedLabel.grid(row = 7, column = 1)
        window.after(1000, scannedLabel.destroy)

def validate_subject(root, subject, chatbox):
    if subject == "":
        entryEmpty = Label(root, text = "Entry box empty", bg = 'black', fg = 'red2')
        entryEmpty.grid(row = 7, column = 0)
        root.after(1000, entryEmpty.destroy)
    elif subject in string.punctuation:
        invalidEntry = Label(root, text = "Invalid input", bg = 'black', fg = 'red2')
        invalidEntry.grid(row = 7, column = 0)
        invalidEntry.after(1000, invalidEntry.destroy)
    elif subject.isdigit() == True:
        invalidEntry = Label(root, text = "Invalid input", bg = 'black', fg = 'red2')
        invalidEntry.grid(row = 7, column = 0)
        invalidEntry.after(1000, invalidEntry.destroy)
    else:
        sentence = talking(subject)
        print(sentence)
        chatbox.insert(END, "AI: " + sentence + "\n\n")

def create_talking_ui():
    root = Tk()
    root.title("Infinite Learner")
    root.geometry('860x400')
    root.configure(bg = 'black')

    menuButton = Button(root, text = 'Menu', width = 5, bg = 'black', fg = 'white', command = lambda:[root.destroy(), create_menu()]).grid(row = 0, column = 0, sticky = "w")
    manButton = Button(root, text = 'Manual', width = 5, bg = 'black', fg = 'white', command = manual_page).grid(row = 0, column = 0)

    chatbox = Text(root, width = 100, height = 10, bg = 'black', fg = 'white')
    chatbox.grid(row = 1, column = 0)

    subjectLabel = Label(root, text = "Subject:", bg = 'black', fg = 'white').grid(row = 2, column = 0, sticky = "w")
    subjectEntry = Entry(root, width = 20, bg = 'black', fg = 'white')
    subjectEntry.grid(row = 2, column = 0)
    subjectButton = Button(root, text = 'Submit', width = 5, bg = 'black', fg = 'white', command = lambda:[validate_subject(root, subjectEntry.get(), chatbox)]).grid(row = 2, column = 0, sticky = "e")

    root.mainloop()

def talking(subject):
    cursor = create_database()

    fetchedSentences = cursor[0].execute("SELECT Sentence FROM Sentences WHERE Sentence LIKE '%"+subject+"%'").fetchall() #selects sentences from DB.
    sentence = random.choice(fetchedSentences)
    sentenceTokens = nltk.word_tokenize(sentence[0]) #splits sentence into words
    sentenceTags = [tag[1] for tag in nltk.pos_tag(sentenceTokens)] #tags each word, returning its word type.

    finalSentenceList = [subject]
    for wordTypeIndex in range(len(sentenceTags) - 1): #forming a sentence with a length of 10 - includes the 'startingWord'

        fetchedNextWords = cursor[0].execute("SELECT Word2, Counter FROM Pairs WHERE Word1 = ?", (finalSentenceList[-1],)).fetchall()
        fetchedNextWords.sort(key = lambda nextWord: nextWord[1], reverse = True)
        nextWords = [word for word in fetchedNextWords if word[0] not in finalSentenceList] #list comprehension for filtering list based on if word exists in final sentence

        currentTag = sentenceTags[wordTypeIndex + 1]
        for wordCandidate in nextWords:
            if nltk.pos_tag([wordCandidate[0]])[0][1] == currentTag:
                finalSentenceList.append(wordCandidate[0])
                break

    return " ".join(finalSentenceList)

def create_menu(): #creating the menu
    root = create_root()

    manLabel = Label(root, text = "Click to display the manual page", bg = 'black', fg = 'white').grid(row = 0, column = 0)
    Button(root, text = 'Manual Page', width = 10, bg = 'black', fg = 'white', command = manual_page).grid(row = 0, column = 2)

    scanLabel = Label(root, text = "Enter the name of the document\nyou want to scan then click\nthe scan button", bg = 'black', fg = 'white').grid(row = 1, column = 0)
    docName = Entry(root, width = 20, bg = 'black', fg = 'white')
    docName.grid(row = 1, column = 1)
    Button(root, text = 'Scan', width = 5, bg = 'black', fg = 'white', command = lambda:[scanning(docName.get(), root)]).grid(row = 1, column = 2)

    talkLabel = Label(root, text = "Click to start talking to the AI", bg = 'black', fg = 'white').grid(row = 2, column = 0)
    Button(root, text = 'Talk', width = 5, bg = 'black', fg = 'white', command = lambda:[root.destroy(), create_talking_ui()]).grid(row = 2, column = 2)

    quitLabel = Label(root, text = "Quit the program", bg = 'black', fg = 'white').grid(row = 3, column = 0)
    Button(root, text = 'Quit', width = 5, bg = 'black', fg = 'white', command = lambda:[print("PROGRAM CLOSED"), quit()]).grid(row = 3, column = 2)

    root.mainloop()

def create_login_ui():
    root = create_root()

    #creating UI and entry fields for user details
    loginLabel = Label(root, text = "If you already have an account,\nenter login details and then click the login button", bg = 'black', fg = 'white').grid(row = 0, column = 1)
    usernameLabel = Label(root, text = "Username:", bg = 'black', fg = 'white').grid(row = 1, column = 0)
    logUsername = Entry(root, width = 20, bg = 'black', fg = 'white')
    logUsername.grid(row = 1, column = 1, sticky = "w")
    passwordLabel = Label(root, text = "Password:", bg = 'black', fg = 'white').grid(row = 2, column = 0)
    logPassword = Entry(root, width = 20, bg = 'black', fg = 'white')
    logPassword.grid(row = 2, column = 1, sticky = "w")

    createLogLabel = Label(root, text = "If you do not have an account,\nenter your desired login details then click the create button", bg = 'black', fg = 'white').grid(row = 4, column = 1)
    usernameLabel = Label(root, text = "Username:", bg = 'black', fg = 'white').grid(row = 5, column = 0)
    createUsername = Entry(root, width = 20, bg = 'black', fg = 'white')
    createUsername.grid(row = 5, column = 1, sticky = "w")
    passwordLabel = Label(root, text = "Integer Password:", bg = 'black', fg = 'white').grid(row = 6, column = 0)
    createPassword = Entry(root, width = 20, bg = 'black', fg = 'white')
    createPassword.grid(row = 6, column = 1, sticky = "w")

    #creating buttons for logging in/creating account
    Button(root, text = 'Log in', width = 5, bg = 'black', fg = 'white', command = lambda:[login_click(root, logUsername.get(), logPassword.get())]).grid(row = 2, column = 1, sticky = "e")
    Button(root, text = 'Create', width = 5, bg = 'black', fg = 'white', command = lambda:[create_click(root, createUsername.get(), createPassword.get())]).grid(row = 6, column = 1, sticky = "e")

    root.mainloop()

def login_click(root, username, password):
    cursor = create_database()

    user = User()
    user.username = username
    user.password = password

    hash_pass = hashlib.sha512(str(user.password).encode('utf8')).hexdigest()
    checkUser = cursor[0].execute("SELECT Username FROM User WHERE Username = ?", (user.username,)) #checks whether username exists in the database
    DBUsers = checkUser.fetchall()

    if (((user.valid_username() == False) or (user.valid_password() == False))):
        usernameOrPasswordInvalid = Label(root, text = "Username or password is invalid", bg = 'black', fg = 'red2')
        usernameOrPasswordInvalid.grid(row = 7, column = 1)
        root.after(2000, usernameOrPasswordInvalid.destroy)
    elif not DBUsers:
        usernameInexistantLabel = Label(root, text = "Username does not exist", bg = 'black', fg = 'red2')
        usernameInexistantLabel.grid(row = 7, column = 1)
        root.after(2000, usernameInexistantLabel.destroy)
    elif DBUsers:
        checkSalt = cursor[0].execute("SELECT Salt From User Where Username = ?", (user.username,))
        checkSalt = str(checkSalt.fetchone()).strip("(),'")
        checkPass = cursor[0].execute("SELECT Password From User Where Username = ?", (user.username,))
        checkPass = str(checkPass.fetchone()).strip("(),'")
        if (hash_pass + checkSalt) != (checkPass + checkSalt):
            passwordInvalid = Label(root, text = "Password is invalid", bg = 'black', fg = 'red2')
            passwordInvalid.grid(row = 7, column = 1)
            root.after(2000, passwordInvalid.destroy)
        else:
            root.destroy()
            create_menu()

def create_click(root, username, password):
    cursor = create_database() #calls the create database function again so 'cursor' and 'database' can be called without parameter passing

    user = User()
    user.username = username
    user.password = password

    if (((user.valid_username() == False) or (user.valid_password() == False))):
        usernameOrPasswordInvalid = Label(root, text = "Username or password is invalid", bg = 'black', fg = 'red2')
        usernameOrPasswordInvalid.grid(row = 7, column = 1)
        root.after(2000, usernameOrPasswordInvalid.destroy)
    elif user.valid_username() == True and user.valid_password() == True:
        hash_pass = hashlib.sha512(str(user.password).encode('utf8')).hexdigest()
        cursor[0].execute("INSERT INTO User(Username, Password, Salt) VALUES(?, ?, ?)", (user.username, hash_pass, user.hash_salt))
        cursor[1].commit()
        root.destroy()
        create_menu()

def main():
    cursor = create_database()[0]
    database = create_database()[1]
    pass_to_table(cursor, database)
    create_login_ui()

main()

