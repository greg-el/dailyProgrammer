import sqlite3
import praw
import re
import argparse
import os

reddit = praw.Reddit(client_id="5KuYf2bGxU1HHA",
                    client_secret="kMMQi7d0lMyTd1jqw3Hx32NR4es",
                    user_agent="dailyProgrammer print to stdout - Kamoda")

class Challenge():
    def __init__(self, number, url, task, title, difficulty, complete, in_progress, *args, **kwargs):
        self.number = number
        self.difficulty = difficulty
        self.task = task
        self.title = title
        self.url = url
        self.complete = complete
        self.in_progress = in_progress
        
    def returnDifficultyEqualLength(self):
        return self.difficulty + " "*(20-(len(self.difficulty))) 

    def returnNumberEqualLength(self):
        return str(self.number) + " "*(3-len(str(self.number)))

    def returnCompleteYesNo(self):
        if self.complete == 0:
            return u"\u2715" + " |"
        else:
            return u"\u2713" + " |"


def initialDataDump():
    conn = sqlite3.connect("dailyProgrammer.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE challenges (
        number int PRIMARY KEY, 
        difficulty varchar(30), 
        task varchar(1),
        title varchar(1),
        url varchar(1),
        complete int,
        in_progress int
        )''')



    pattern = re.compile(r"\[\d/\d{2}/\d{4}]")
    pattern2 = re.compile(r"\[\d{4}-\d{2}-\d{2}]")
    #taskNumber = re.compile(r"# ?\d+| \d{2,3}")
    difficulty = re.compile(r"\[(\w*\/?\s?\w*)\]|intermediate|easy|hard")
    challenge = re.compile(r"Challenge")
    #url = re.compile(r"comments\/(\w+)")

    number = 0
    for submission in reddit.subreddit("dailyprogrammer").new(limit=None):
        if pattern.match(submission.title) and challenge.findall(submission.title) or pattern2.match(submission.title) and challenge.findall(submission.title):
            
            try:
                difficultyEntry = difficulty.search(submission.title.lower()).group(1)
            except Exception:
                difficultyEntry = difficulty.search(submission.title.lower()).group(0)
            if difficultyEntry == None:
                difficultyEntry = "other"
            taskEntry = (number, difficultyEntry, submission.selftext, submission.title, submission.url,  0, 0)
            c.execute('''INSERT INTO challenges VALUES (?,?,?,?,?,?,?)''', taskEntry)
            number+=1
        
    conn.commit()
    conn.close()

def getChallengeByNumber(n):
    conn = sqlite3.connect("dailyProgrammer.db")
    c = conn.cursor()
    lines = c.execute('''SELECT number, difficulty, task, complete FROM challenges WHERE number=?''', (n,))
    chall = lines.fetchone()
    print(f"Task: {chall[0]} // Difficulty: {chall[1]} // Complete: {chall[3]} \n \n")

    print(chall[2])
    while True:
        current = input("[s] - Set as the in-progress challenge // [q] - Quit \n")
        if current=="s":
            addCurrentToDatabase(chall)
        elif current == "q":
            os.system("clear")
            exit(1)
        else:
            print("Incorrect command. Try again.")


def getChallengeByDifficulty(diff):
    conn = sqlite3.connect("dailyProgrammer.db")
    c = conn.cursor()
    current = c.execute('''SELECT number, difficulty, task, complete FROM challenges WHERE difficulty=?''', (diff,))
    currentFetch = current.fetchall()
    return(currentFetch[2])

def addCurrentToDatabase(challenge):
    conn = sqlite3.connect("dailyProgrammer.db")
    c = conn.cursor()
    current = c.execute('''SELECT number, difficulty FROM current''')
    currentFetch = current.fetchone()
    if currentFetch[0] == challenge[0] and currentFetch[1] == challenge[1]:
        print("This challenge is already the current one")
        return
    c.execute('''DELETE FROM current''')
    c.execute('''INSERT INTO current VALUES (?, ?)''', (challenge[0], challenge[1]))
    print(f"In-progress set as: {challenge[0]} [{challenge[1]}]")
    conn.commit()
    conn.close()

def getCurrentFromDatabase():
    conn = sqlite3.connect("dailyProgrammer.db")
    c = conn.cursor()
    current = c.execute('''SELECT number, difficulty FROM current''')
    currentFetch = current.fetchone()
    print(getChallengeByNumberAndDifficulty(currentFetch[0], currentFetch[1]))

    conn.commit()
    conn.close()


def dbToChallenge(line):
    return Challenge(number=line[0], difficulty=line[1], task=line[2], title=line[3], url=line[4], complete=line[5], in_progress=line[6])


def getAllChallenges():
    conn = sqlite3.connect("dailyProgrammer.db")
    c = conn.cursor()
    query = c.execute('''SELECT * FROM challenges''')
    data = query.fetchall()

    col, row = os.get_terminal_size()
    col_count = 0
    row_count = 0

    print("Num  Difficulty   Done  "*3)
    for line in data:
        if row <= row_count+3:
            row_count = 0
            browse = input("\n [b] - Prev // [n] - Next")
            if browse == "n":
                os.system("clear")
                print("Num  Difficulty   Done  "*3)
                continue
            
        #if line[0] == None and line[1] == None:
        #    break
        challenge = dbToChallenge(line)
        if col > col_count+60:
            print(f"{challenge.returnNumberEqualLength()}: {challenge.returnDifficultyEqualLength()}", end=" ")
            col_count+=len(challenge.returnNumberEqualLength())+len(challenge.returnDifficultyEqualLength())+4
        else:
            print("\r")
            print(f"{challenge.returnNumberEqualLength()}: {challenge.returnDifficultyEqualLength()}", end=" ")
            col_count = 0
            row_count+=1
    print("\n")
    conn.close()

def browseAllChallenges():
    conn = sqlite3.connect("dailyProgrammer.db")
    c = conn.cursor()
    query = c.execute('''SELECT * FROM challenges''')
    data = query.fetchall()


    col, row = os.get_terminal_size()
    col_count = 0
    row_count = 0
    row_limit = 0
    test = [x for x in data] #TODO be able to browse back/forward
    pageIndex = [0]
    row = row-3
    entry_limit = (int(col/30)*row)


    for i in range(0, len(test)):
        if row <= row_count+3:
            pageIndex.append(i)
            row_limit = 0
            row_count = 0
        if col > col_count+60:
            challenge = dbToChallenge(test[i])
            col_count+=len(challenge.returnNumberEqualLength())+len(challenge.returnDifficultyEqualLength())+4
            row_limit+=1
        else:
            col_count = 0
            row_count+=1

    pageEntries = int(entry_limit/int(col/30))
    pages = pageEntries*int(col/30)
    maxPages = int((len(test)/pages))
    page = 0
    print(maxPages)
    tooltip = ""
    while True:
        printScreen(test, page*entry_limit)
        print(tooltip)
        
        output = input("[b] - prev // [n] - next  ")
        
        tooltip = ""
        if output == "n":
            if page >= maxPages:
                tooltip = "// At last page //"
            else:
                page+=1
        if output == "b":
            if page-1 < 0:
                tooltip = "// At first page //"
            else:
                page-=1

    print(len(data))


def printScreen(test, page):
    col, row = os.get_terminal_size()
    row = row-3
    entry_limit = (int(col/30)*row)
    
    out = []
    for i in range(entry_limit):
        try:
            challenge = dbToChallenge(test[i+page])
        except IndexError:
            continue
        out.append(challenge)

    pageEntries = int(entry_limit/int(col/30))

    arrOut = []
    for i in range(pageEntries):
        for j in range(int(col/30)):
            try:
                arrOut.append((out[i+pageEntries*j].returnNumberEqualLength(), out[i+pageEntries*j].returnDifficultyEqualLength(), out[i+pageEntries*j].returnCompleteYesNo()))
            except IndexError:
                pass
        for item in arrOut:
            print(f" {item[0]} {item[1]} {item[2]}", end="")
        arrOut = []
        print("\r")
    
    print("\r")



parser = argparse.ArgumentParser(description="Reddit dailyProgrammer client")
parser.add_argument("integer", metavar='N', type=int, nargs='?', help="An integer for challenge selection")
parser.add_argument("-c", "--challenge", help="Select challenge", dest="getNum", action="store_const", const=getChallengeByNumber)
parser.add_argument("-p", "--in-progress", help="Show in-progress challenge", dest="getInProgress", action="store_const", const=getCurrentFromDatabase)
parser.add_argument("-s", "--setCurrent", help="Show all challenges", dest="showAll", action="store_const", const=browseAllChallenges)
args = parser.parse_args()
#print(args)

if not os.path.isfile("dailyProgrammer.db"):
    print("Creating database...")
    initialDataDump()
    print("Complete")


if args.getNum:
    args.getNum(args.integer)
if args.getInProgress:
    args.getInProgress()
if args.showAll:
    args.showAll()