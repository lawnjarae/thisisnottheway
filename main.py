from dotenv import load_dotenv
load_dotenv()

import praw
import os

reddit = praw.Reddit(
    client_id=os.environ.get("REDDIT_CLIENT_ID"),
    client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
    password=os.environ.get("REDDIT_PASSWORD"),
    user_agent=os.environ.get("USER_AGENT"),
    username=os.environ.get("REDDIT_USERNAME")
)

# Get a list of subs for the bot. This could also be done just with an array.
# The array method is probably the best. That way you can just modify the code.
subbed_to = list(reddit.user.subreddits(limit=None))

# Loop dem subs
for subreddit in subbed_to:
  print(f'Scanning {subreddit.display_name_prefixed}')
  # Get the n top submissions from that sub
  hot_subs = subreddit.top(time_filter='day', limit=15)
  for submission in hot_subs:
    # https://praw.readthedocs.io/en/stable/tutorials/comments.html#the-replace-more-method
    submission.comments.replace_more(limit=7)
    all_comments = submission.comments.list()
    print(f'Submission: {submission.title} has {len(all_comments)} comments.')
    
    # Check if this comment starts with "this is the way"
    for comment in all_comments:
      if comment.body.lower().startswith('this is the way'):
        print('WE GOT ONE!!!') # Ghostbusters
        print(comment)
        comment.downvote()