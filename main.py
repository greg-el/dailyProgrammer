import sqlite3
import praw
import re

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
    c.execute('''CREATE TABLE IF NOT EXISTS challenges (
        code CHAR(6) PRIMARY KEY, 
        number int, 
        difficulty varchar(30), 
        task varchar(1), 
        complete int
        )''')

    pattern = re.compile(r"\[\d/\d{2}/\d{4}]")
    pattern2 = re.compile(r"\[\d{4}-\d{2}-\d{2}]")
    taskNumber = re.compile(r"# ?\d+| \d{2,3}")
    difficulty = re.compile(r"\[(\w*\/?\s?\w*)\]|intermediate|easy|hard")
    challenge = re.compile(r"Challenge")
    url = re.compile(r"comments\/(\w+)")


    for submission in reddit.subreddit("dailyprogrammer").new(limit=None):
        if pattern.match(submission.title) and challenge.findall(submission.title) or pattern2.match(submission.title) and challenge.findall(submission.title):
            print(difficulty.search(submission.title.lower()))
            try:
                difficultyEntry = difficulty.search(submission.title.lower()).group(1)
            except Exception:
                difficultyEntry = difficulty.search(submission.title.lower()).group(0)
            taskEntry = (url.search(submission.url).group(1), int(taskNumber.search(submission.title).group(0)[1:]), difficultyEntry, submission.selftext, 0)
            c.execute('''INSERT INTO challenges VALUES (?,?,?,?,?)''', taskEntry)
        
    conn.commit()
    conn.close()

def getChallengeByNumber(n):
    conn = sqlite3.connect("dailyProgrammer.db")
    c = conn.cursor()
    c.execute('''SELECT number, difficulty FROM challenges WHERE number=?''', (n,))
    print(c.fetchall())


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
    lines = c.execute('''SELECT number, difficulty FROM challenges''')
    challengeNumber = lines.fetchone()[0]
    lines = c.execute('''SELECT number, difficulty FROM challenges''')

    challenges = Challenges()
    for line in lines:
        if line[0] == challengeNumber:
            challenges = addChallengeToClass(challenges, line)
        else:
            print()
            challenges.clear()
            challengeNumber = line[0]
            challenges = addChallengeToClass(challenges, line)
    
    conn.close()


getAllChallenges()