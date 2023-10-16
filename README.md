
# 0. Environment set up 
You will need to create a file called **praw.ini** in the root directory of the project and add the following lines:
```
[DEFAULT]
client_id=your_client_id_without_quotes
client_secret=your_client_secret_without_quotes
user_agent='your_user_agent_without_quotes'
```
> You can get the credentials for the Reddit API from https://www.reddit.com/prefs/apps


# 1. Start the service using docker compose
```docker compose up -d```

> Note that the service will be available on port 8080

    
# 2. Test the endpoint
```
curl "http://localhost:8080/sentiment?subreddit=sixwordstories&time=day&limit=10&sort=true"
```

# 3. Stop the service
```docker compose down```
