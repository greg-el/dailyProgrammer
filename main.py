import sqlite3
import praw
import re


reddit = praw.Reddit(client_id="5KuYf2bGxU1HHA",
                    client_secret="kMMQi7d0lMyTd1jqw3Hx32NR4es",
                    user_agent="dailyProgrammer print to stdout - Kamoda")


def initialDataDump():
    conn = sqlite3.connect("dailyProgrammer.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS challenges (code CHAR(6) PRIMARY KEY, number int, difficulty varchar(30), task varchar(1), complete int)''')

    pattern = re.compile(r"\[\d/\d{2}/\d{4}]")
    pattern2 = re.compile(r"\[\d{4}-\d{2}-\d{2}]")
    taskNumber = re.compile(r"# ?\d+| \d{2,3}")
    difficulty = re.compile(r"\[(\w*\/?\s?\w*)\]|Intermediate|Easy|Hard")
    challenge = re.compile(r"Challenge")
    url = re.compile(r"comments\/(\w+)")


    for submission in reddit.subreddit("dailyprogrammer").new(limit=None):
        if pattern.match(submission.title) and challenge.findall(submission.title) or pattern2.match(submission.title) and challenge.findall(submission.title):
            taskEntry = (url.search(submission.url).group(1), int(taskNumber.search(submission.title).group(0)[1:]), difficulty.search(submission.title).group(1), submission.selftext, 0)
            c.execute("INSERT INTO challenges VALUES (?,?,?,?,?)", taskEntry)
        
    conn.commit()
    conn.close()

def getChallengeByNumber(n):
    conn = sqlite3.connect("dailyProgrammer.db")
    c = conn.cursor()
    c.execute('''SELECT * FROM challenges WHERE number=?''', (n,))
    print(c.fetchall())

getChallengeByNumber(41)