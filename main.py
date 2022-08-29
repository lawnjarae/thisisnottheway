import os
import praw
from functools import wraps
from pymongo import MongoClient
from flask import Flask, request as flask_request, Response as Flask_Response, abort
from threading import Thread
from dotenv import load_dotenv
load_dotenv()

# Set up Flask
app = Flask(__name__)

reddit = praw.Reddit(
    client_id=os.environ.get("REDDIT_CLIENT_ID"),
    client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
    password=os.environ.get("REDDIT_PASSWORD"),
    user_agent=os.environ.get("USER_AGENT"),
    username=os.environ.get("REDDIT_USERNAME")
)

# Connect to MongoDB
client = MongoClient(
    f'mongodb+srv://{os.environ.get("MONGODB_USER")}:{os.environ.get("MONGODB_PASSWORD")}@{os.environ.get("MONGODB_CLUSTER")}/{os.environ.get("MONGODB_DB")}?retryWrites=true&w=majority')
db = client.thisisnottheway


def add_downvote_to_db(comment):
    downvote = {
        'submissionId': comment.submission.id,
        'subreddit': comment.subreddit_name_prefixed,
        'commentId': comment.id
    }
    db.downvotes.update_one(
        {'_id': comment.author.name},
        {'$push': {'comments': downvote}},
        upsert=True
    )

list_of_subs = [
    '321',
    'AdrenalinePorn',
    'Android',
    'aquaponics',
    'ArtisanVideos',
    'AskReddit',
    'aww',
    'Backcountry',
    'baseball',
    'basejumping',
    'bicycletouring',
    'CatsAreAssholes',
    'CFB',
    'Colorado',
    'ColoradoRockies',
    'Coronavirus',
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
    'funny',
    'gaming',
    'geek',
    'gifs',
    'HistoryPorn',
    'hockey',
    'InfowarriorRides',
    'MTB',
    'Music',
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
    'TinyHouses',
    'todayilearned',
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


def downvote(type: str, subs: list) -> None:
    num_downvotes = 0
    total_comments = 0

    # Loop dem subs
    for sub in subs:
        subreddit = reddit.subreddit(sub)
        print(f'Scanning r/{subreddit.display_name}')
        # Get the n top submissions from that sub
        if sub != 'all':
            limit = 15
        else:
            limit = 100

        submissions = []
        if type == 'top':
            submissions = subreddit.top(time_filter='day', limit=limit)
        elif type == 'hot':
            submissions = subreddit.hot(limit=limit)

        for submission in submissions:
            # https://praw.readthedocs.io/en/stable/tutorials/comments.html#the-replace-more-method
            submission.comments.replace_more(limit=7)
            all_comments = submission.comments.list()
            total_comments = total_comments + len(all_comments)
            print(
                f'{submission.subreddit_name_prefixed}: {submission.title} has {len(all_comments)} comments.')

            # Check if this comment starts with "this is the way"
            for comment in all_comments:
                if comment.body.lower().startswith('this is the way'):
                    # There aren't that many of these so we can afford the call to the db to see if we've
                    # already downvoted this comment before. The API doesn't care, but I don't want to create
                    # duplicates in the db
                    author = db.downvotes.find_one(
                        {'_id': comment.author.name, 'comments.commentId': comment.id})
                    if author is None:
                        # Ghostbusters
                        print(
                            f'WE GOT ONE!!! {comment.author.name} is a clown.')
                        comment.downvote()
                        add_downvote_to_db(comment)
                        num_downvotes = num_downvotes + 1

    print(
        f'Scanned {total_comments} comments and downvoted {num_downvotes} for being useless.')


def require_api_key(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        """Wrapper function for every endpoint to force an API key be used."""

        if flask_request.headers.get('x-api-key') and flask_request.headers.get('x-api-key') == os.environ.get('REALM_API_KEY'):
            return view_function(*args, **kwargs)
        else:
            abort(401)

    return decorated_function


@app.route('/hot', methods=['POST'])
@require_api_key
def hot_endpoint():
    thread = Thread(target=downvote, args=('hot', ['all'],))
    thread.start()
    return Flask_Response({}, mimetype='application/json')


@app.route('/top', methods=['POST'])
@require_api_key
def all_top_endpoint():
    top_subs = ['all']
    top_subs.extend(list_of_subs)
    thread = Thread(target=downvote, args=('top', top_subs,))
    thread.start()
    return Flask_Response({}, mimetype='application/json')

if __name__ == '__main__':
    app.run(threaded=True, ssl_context='adhoc')