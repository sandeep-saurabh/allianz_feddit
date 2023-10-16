from flask import Flask, request, jsonify, render_template
import praw
from flask_cors import CORS
from textblob import TextBlob

app = Flask(__name__)

# CORS(app, origins=['http://localhost:3006'])
CORS(app, origins='*')
reddit = praw.Reddit()


def get_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    return polarity, 'positive' if polarity > 0 else 'negative' if polarity < 0 else 'neutral'


@app.route('/sentiment', methods=['GET'])
def analyze_subreddit():
    subreddit_name = request.args.get('subreddit')
    if not subreddit_name:
        return jsonify({'error': 'subreddit parameter is required'}), 400

    time_filter = request.args.get('time', 'all')  # Default to 'all' if no time filter is provided
    limit = int(request.args.get('limit', 25))  # Default to 25 if no limit is provided
    sort_by_polarity = request.args.get('sort', 'false').lower() == 'true'  # Default to false

    subreddit = reddit.subreddit(subreddit_name)

    comments_data = []
    for submission in subreddit.top(time_filter, limit=limit):
        submission.comments.replace_more(limit=3)  # Replace MoreComments objects to get all comments
        for comment in submission.comments.list():
            polarity, sentiment = get_sentiment(comment.body)
            comments_data.append({
                'id':        comment.id,
                'text':      comment.body,
                'polarity':  polarity,
                'sentiment': sentiment
                })

    if sort_by_polarity:
        comments_data.sort(key=lambda x: x['polarity'], reverse=True)

    # return render_template('results.html', comments=comments_data)
    return jsonify(comments_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)