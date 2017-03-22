# P^3DB
## Predicate Paraphrase Database

This is the code used in the paper:

<b>"An Ever-growing Resource of Predicate Paraphrases"</b><br/>
Vered Shwartz, Gabriel Stanovsky and Ido Dagan. (TBD).

The resource can be found [here](http://u.cs.biu.ac.il/~nlp/resources/downloads/p3db/) (TBD).

***

<b>To create a similar resource:</b>

1. Obtain news tweets:
   Create a directory with tweet files (e.g. a different directory for each day), each file in the following format: `tweet_id\ttweet`.
   One way to get these are by querying the [Twitter Search API](https://dev.twitter.com/rest/public/search) for news:

   ```
   get_news_tweets_stream.py --consumer_key=<consumer_key> --consumer_secret=<consumer_secret>
        --access_token=<access_token> --access_token_secret=<access_token_secret> [--until=<until>]
   ```
   
   where `consumer_key`, `consumer_secret`, `access_token` and `access_token_secret` are obtained by registering to the Twitter API as an app, in [here](https://apps.twitter.com/). 
   The optional argument `until` is a date in the format `YYYY/MM/dd` if you'd like to retrieve tweets only until this date. The Search API only supports up to one week ago. If this argument is not specified, it will retrieve current tweets. This script will save the tweets in a file named by the date they were created at.
   
   Important note: we downloaded [TwitterSearch](https://github.com/ckoepp/TwitterSearch) and changed the code to add the
   news filter to the search URL. If you want to get news tweets, you should do the same.

2. Extract propositions: 
   ```
   prop_extraction --in=[tweet_folder] --out=[prop_folder]
   ```
   
3. Generate positive instances: for each proposition file, run: 
   ```
   get_corefering_predicates.py [tweets_file] [out_file]
   ```

5. To package the resource:

    * Generate the full resource file (remove the date field):
     ```
     cut -f2-13 positive/* > positive_instances.tsv
     ```

    * Generate a version without the tweets (only tweet IDs):
     ```
     cut -f1,3,4,5,6,7,9,10,11,12,13 positive_instances.tsv > positive_instances_without_tweets.tsv
     ```

6. To download the full resource:

   ```
   expand_resource.py --resource_file=<resource_file> --consumer_key=<consumer_key>
        --consumer_secret=<consumer_secret> --access_token=<access_token> 
        --access_token_secret=<access_token_secret>
   ```

    where `--resource_file` is the path to the resource file without tweets (e.g. `resource_without_tweets.tsv` or the file in the packaged resource you downloaded).
