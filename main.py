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

list_of_subs = [
  'all',
  '321',
  'AdrenalinePorn',
  'Android',
  'aquaponics',
  'ArtisanVideos',
  'Backcountry',
  'baseball',
  'basejumping',
  'bicycletouring',
  'BlackLivesMatter',
  'CatsAreAssholes',
  'CFB',
  'COclimbing',
  'Colorado',
  'ColoradoRockies',
  'Coronavirus',
  'COsnow',
  'dadjokes',
  'darknetdiaries',
  'Denver',
  'denvermusic',
  'DenverProtests',
  'DIY',
  'energy',
  'environment',
  'florida',
  'freeflight',
  'freefolk',
  'fsusports',
  'Fullmoviesonvimeo',
  'funny',
  'geek',
  'gifs',
  'HistoryPorn',
  'hockey',
  'InfowarriorRides',
  'MTB',
  'Music',
  'newretrowave',
  'ODroid',
  'oldfreefolk',
  'OnePunchMan',
  'OpenArgs',
  'overlanding',
  'pics',
  'politics',
  'programming',
  'RenewableEnergy',
  'restofthefuckingowl',
  'sailing',
  'science',
  'SkyDiving',
  'snowboarding',
  'Spliddit',
  'Stargate',
  'StarWarsleftymemes',
  'TampaBayLightning',
  'tampabayrays',
  'TeardropTrailers',
  'technology',
  'THE_PACK',
  'TheDollop',
  'TheFulmerCup',
  'TinyHouses',
  'todayilearned',
  'TrailGuides',
  'TunnelFlight',
  'vandwellers',
  'videos',
  'woodworking',
  'worldcup',
  'worldnews',
  'WTF',
]

# Get a list of subs for the bot. This could also be done just with an array.
# The array method is probably the best. That way you can just modify the code.
# list_of_subs = list(reddit.user.subreddits(limit=None))

num_downvotes = 0

# Loop dem subs
for sub in list_of_subs:
  subreddit = reddit.subreddit(sub)
  print(f'Scanning r/{subreddit.display_name}')
  # Get the n top submissions from that sub
  if sub != 'all':
    limit = 15
  else:
    limit = 50
  # top_subs = subreddit.top(time_filter='day', limit=limit)
  hot_subsmissions = subreddit.hot(limit=limit)
  for submission in hot_subsmissions:
    # https://praw.readthedocs.io/en/stable/tutorials/comments.html#the-replace-more-method
    submission.comments.replace_more(limit=7)
    all_comments = submission.comments.list()
    print(f'{submission.subreddit_name_prefixed}: {submission.title} has {len(all_comments)} comments.')
    
    # Check if this comment starts with "this is the way"
    for comment in all_comments:
      if comment.body.lower().startswith('this is the way'):
        print(f'WE GOT ONE!!! {comment.author.name} is a clown.') # Ghostbusters
        comment.downvote()
        num_downvotes = num_downvotes + 1

print(f'Downvoted {num_downvotes} comments for being useless.')