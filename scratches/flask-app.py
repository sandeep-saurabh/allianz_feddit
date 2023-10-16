import requests
from flask import Flask, request, jsonify
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:8080/callback'
AUTH_URL = 'https://www.reddit.com/api/v1/authorize'
TOKEN_URL = 'https://www.reddit.com/api/v1/access_token'

import praw
# reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent='reddit-nlp/1.0')
reddit = praw.Reddit()

@app.route('/')
def homepage():
    print(f"{request.args=}")
    """Redirect the user to Reddit's authorization page."""
    auth_params = {
        'client_id':     CLIENT_ID,
        'response_type': 'code',
        'state':         'random_string_for_state_check',
        'redirect_uri':  REDIRECT_URI,
        'duration':      'permanent',  # This ensures you get a refresh_token
        'scope':         'identity'  # Adjust the scope as needed for your app
        }
    url = requests.Request('GET', AUTH_URL, params=auth_params).prepare().url
    return f'<a href="{url}">Click here to authorize the application</a>'


@app.route('/get_subreddit_posts', methods=['GET'])
def get_subreddit_posts():
    subreddit_name = request.args.get('subreddit', 'Python')  # Default to 'Python' if no subreddit is provided
    limit = int(request.args.get('limit', 10))  # Default to 10 if no limit is provided

    subreddit = reddit.subreddit(subreddit_name)

    posts = []
    for submission in subreddit.hot(limit=limit):
        try:
            comments = [comment.body for comment in submission.comments.list() if not hasattr(comment, 'body')]
            submission.comments.replace_more(limit=0)
        except:
            comments = []

        post = {
            'title': submission.title,
            'comments': comments
            }
        posts.append(post)

    return jsonify(posts)

@app.route('/callback')
def callback():
    """Handle the callback from Reddit's authorization page."""
    code = request.args.get('code')
    state = request.args.get('state')

    # Exchange the code for an access token and refresh token
    headers = {
        'User-Agent': 'YourApp/0.1'
        }
    data = {
        'grant_type':   'authorization_code',
        'code':         code,
        'redirect_uri': REDIRECT_URI
        }
    response = requests.post(
        TOKEN_URL,
        headers=headers,
        data=data,
        auth=(CLIENT_ID, CLIENT_SECRET)
        )
    token_data = response.json()
    access_token = token_data.get('access_token')
    refresh_token = token_data.get('refresh_token')

    # return f'Access Token: {access_token}<br>Refresh Token: {refresh_token}'
    return response.json()

@app.route('/filter', methods=['GET'])
def filter_by_date():
    # Get start and end date-time from URL parameters
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    # Validate date-time parameters
    if not start_date_str or not end_date_str:
        return jsonify({"error": "start_date and end_date are required"}), 400

    # Parse date-time strings to datetime objects
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DDTHH:MM:SS"}), 400

    # Your filtering logic here. For this example, just echo the received date-time filters.
    return jsonify({
        "start_date": start_date_str,
        "end_date": end_date_str
        })


if __name__ == '__main__':
    app.run(port=8080, debug=True)