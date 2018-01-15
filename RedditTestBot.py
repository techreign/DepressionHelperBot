import praw
import sys
import time
import threading
import urllib
import configparser
from random import *

config = configparser.ConfigParser()
config.read('my.ini')
# login info
proceed = False
ID = config.get('Authentication', 'Client_id')
SECRET = config.get('Authentication', 'Client_secret')
USERNAME = config.get('Authentication', 'Username')
PASSWORD = config.get('Authentication', 'Password')
USER_AGENT = config.get('Authentication', 'User_agent')
# phrases to reply with
PHRASES = ["Stay strong my friend", "I am glad you are with us", "Keep your head up",
				"Try your best to get through this!", "We are all with you", "Never give up!"]

phrases_to_look_for = ["I am depressed", "I am feeling depressed", "I want to commit suicide", 
						"thinking about suicide", "do not want to live", "I have deppresion", 
						"I'm depressed", "i have deppresion", "kill myself", "no pleasure", 
						"I can't imagine going on", "I'm really scared", "I am scared", "I'm scared"]

# creating of the praw object, logging in and continious while
def main():
	reddit = praw.Reddit(client_id=ID ,
						 client_secret=SECRET, 
						 username=USERNAME,
						 password=PASSWORD,
						 user_agent=USER_AGENT)

	print("Logged in", file=sys.stderr)

	# separate thread which will delete downvoted comments made by this bot


	# navigating through depression subreddit
	#subreddit = reddit.subreddit('depression')
	#hot_depression = subreddit.hot(limit=1000)

	# old comment scanner/deleter
	t = threading.Thread(target=delete_downvoted_posts, args=(reddit,))
	t.start()

	while (True):
		print("Beginning to look through reddit", file=sys.stderr)
		depression_scanner(reddit, phrases_to_look_for)
		print("Taking a 15 second break", file=sys.stderr)
		time.sleep(15)
		print("I've done my job", file=sys.stderr)



def depression_scanner(session, phrases):
	reddit_all1 = session.subreddit('all')
	reddit_all = reddit_all1.new(limit=1000)

	print("Fetching posts", file=sys.stderr)
	comment_count = 0
	proceed = False

	for submission in reddit_all:
	    if not submission.stickied:
	        comment_count += 1
	        if not submission.visited:
	        	for phrase in phrases_to_look_for:
	        		if phrase in submission.selftext:
	        			print("Deppressed post found", file=sys.stderr)
	        			if len(submission.comments) >= 1:
		        			for reply in submission.comments:
		        				if reply.author.name == "shokhan768" or reply.author.name == 'depressagent':
		        					print("Already posted in this thread", file=sys.stderr)
		        					proceed = False
		        					break
		        				else:
		        					proceed = True
		        		else:
		        			proceed = True

	    if proceed == True:
	     	print("Deppressed thread found", file=sys.stderr)
	     	post_motivation(submission)
	     	print("Motivation posted", file=sys.stderr)
	     	break

	if comment_count == 1000:
		return


def post_motivation(reply_to):
	try:
		print("Posting motiivational response", file=sys.stderr)
		rand_int = randint(0, len(PHRASES))
		motivation = PHRASES[rand_int]
		reply_to.reply(motivation)
	except Exception as e:
		print("Something went wrong", file=sys.stderr)


def delete_downvoted_posts(session):
	while True:
		print("Looking through old comments", file=sys.stderr)
		my_account = session.redditor(USERNAME)
		my_comments = my_account.comments.new()
		for old_comment in my_comments:
			if old_comment.score < 0:
				print("Comment taken badly... removing", file=sys.stderr)
				old_comment.delete()
		# sleep for half hour
		print("Turning off old comment scanner for 30 mins", file=sys.stderr)
		time.sleep(1800)

if __name__ == '__main__':
	main()
