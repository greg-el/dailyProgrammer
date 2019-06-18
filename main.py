import sqlite3
import praw
import re
import argparse
import os


class Challenges():
    def __init__(self):
        self.easy = None
        self.intermediate = None
        self.hard = None
        self.other = None

    def returnList(self):
        out = [self.easy, self.intermediate, self.hard, self.other]
        return [x for x in out if x != None]

    def clear(self):
        self.easy = None
        self.intermediate = None
        self.hard = None
        self.other = None


reddit = praw.Reddit(client_id="5KuYf2bGxU1HHA",
                    client_secret="kMMQi7d0lMyTd1jqw3Hx32NR4es",
                    user_agent="dailyProgrammer print to stdout - Kamoda")


def initialDataDump():
    conn = sqlite3.connect("dailyProgrammer.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE challenges (
        code CHAR(6) PRIMARY KEY, 
        number int, 
        difficulty varchar(30), 
        task varchar(1), 
        complete int
        )''')

    c.execute('''CREATE TABLE current (
        number int,
        difficulty varchar(1)
        )''')

    pattern = re.compile(r"\[\d/\d{2}/\d{4}]")
    pattern2 = re.compile(r"\[\d{4}-\d{2}-\d{2}]")
    taskNumber = re.compile(r"# ?\d+| \d{2,3}")
    difficulty = re.compile(r"\[(\w*\/?\s?\w*)\]|intermediate|easy|hard")
    challenge = re.compile(r"Challenge")
    url = re.compile(r"comments\/(\w+)")

    task = 0
    for submission in reddit.subreddit("dailyprogrammer").new(limit=None):
        if pattern.match(submission.title) and challenge.findall(submission.title) or pattern2.match(submission.title) and challenge.findall(submission.title):
            try:
                difficultyEntry = difficulty.search(submission.title.lower()).group(1)
            except Exception:
                difficultyEntry = difficulty.search(submission.title.lower()).group(0)
            taskEntry = (url.search(submission.url).group(1), task, difficultyEntry, submission.selftext, 0)
            c.execute('''INSERT INTO challenges VALUES (?,?,?,?,?)''', taskEntry)
            task+=1
        
    conn.commit()
    conn.close()

def getChallengeByNumber(n):
    conn = sqlite3.connect("dailyProgrammer.db")
    c = conn.cursor()
    lines = c.execute('''SELECT number, difficulty, task, complete FROM challenges WHERE number=?''', (n,))
    challenges = Challenges()
    for line in lines:
        challenges = addChallengeToClass(challenges, line)
    
    out = challenges.returnList()
    os.system("clear")
    for chall in out:
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


    challenges.clear()

def getChallengeByNumberAndDifficulty(n, diff):
    conn = sqlite3.connect("dailyProgrammer.db")
    c = conn.cursor()
    current = c.execute('''SELECT number, difficulty, task, complete FROM challenges WHERE number=? AND difficulty=?''', (n, diff))
    currentFetch = current.fetchone()
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


def addChallengeToClass(challenges, line):
    if line[1] == "easy":
        challenges.easy = line
    elif line[1] == "intermediate":
        challenges.intermediate = line
    elif line[1] == "hard":
        challenges.hard = line
    else:
        challenges.other = line

    return challenges

def getAllChallenges():
    conn = sqlite3.connect("dailyProgrammer.db")
    c = conn.cursor()
    lines = c.execute('''SELECT number, difficulty FROM challenges LIMIT 1''')
    challengeNumber = lines.fetchone()[0]
    lines = c.execute('''SELECT number, difficulty FROM challenges''')

    challenges = Challenges()
    for line in lines:
        if line[0] == challengeNumber:
            challenges = addChallengeToClass(challenges, line)
        else:
            challenges.clear()
            challengeNumber = line[0]
            challenges = addChallengeToClass(challenges, line)
    
    conn.close()

parser = argparse.ArgumentParser(description="Reddit dailyProgrammer client")
parser.add_argument("integer", metavar='N', type=int, nargs='?', help="An integer for challenge selection")
parser.add_argument("-c", "--challenge", help="Select challenge", dest="getNum", action="store_const", const=getChallengeByNumber)
parser.add_argument("-p", "--in-progress", help="Show in-progress challenge", dest="getInProgress", action="store_const", const=getCurrentFromDatabase)
#parser.add_argument("-s", "--setCurrent", help="Set current challenge", dest="action", action="store_const", const=setCurrentChallenge)
args = parser.parse_args()
#print(args)


if args.getNum:
    args.getNum(args.integer)
if args.getInProgress:
    args.getInProgress()