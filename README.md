# twitoff-app
Web application to compare tweets between two different users.
The app is live at [http://twitoff.stromsy.com](http://twitoff.stromsy.com).


### Adding Users

The right hand of the home page contains a list of loaded twitter accounts and an option
to add or update twitter accounts. Adding a new twitter account will retrieve up to 200 of the account's
most recent tweets (the most recent 200 tweets minus replies) and then call
basilica.ai's API to get embeddings (that is, convert each tweet into an array
of floats). The text and embedding of each tweet is stored in a postgresql db.
If the user enters the name of a twitter account that is already added, the app does the
same thing but adds more tweets in addition to the ones already loaded.

### Comparing Users

The left hand of the homepage allows the user to select two twitter accounts
(out of the loaded accounts), and also enter text of a hypothetical tweet.
The app will train an sklearn LogisticRegression on the embeddings of the
two twitter accounts' tweets. It will then call the basilica.ai API to retrieve
embeddings for the hypothetical tweet, and use the embeddings to predict which
twitter account would be more likely to tweet it. The results are then returned
to the user.

### Cache

Since training models is a relatively expensive operation, we cache
models using Redis. The redis key is the username of the account with the lesser twitter
id, concatenated with an "@", concatenated with the username of the account with the greater.
twitter id.
```
if user1.id > user2.id:
    user1, user2 = user2, user1
key = user1.username + "@" + user2.username
```

When a model is stored, it is simply pickled and stored as a bytes object. A list of cached
models is shown on the home page of the app.

### Nature of the Project

This is a toy prototype for instructional purposes.
