import praw
import re

reddit = praw.Reddit(client_id="5KuYf2bGxU1HHA",
                    client_secret="kMMQi7d0lMyTd1jqw3Hx32NR4es",
                    user_agent="dailyProgrammer print to stdout - Kamoda")


pattern = re.compile(r"\[\d/\d{2}/\d{4}]")
pattern2 = re.compile(r"\[\d{4}-\d{2}-\d{2}]")
pattern3 = re.compile(r"#\d{2}")
num = "41"
for submission in reddit.subreddit("dailyprogrammer").new(limit=None):
    if (pattern.match(submission.title) or pattern2.match(submission.title)):
        m = re.findall(pattern3, submission.title)
        #print(str(m)[3:5])
        if (str(m)[3:5] == num):
            print(submission.title)
            print(submission.selftext)
        