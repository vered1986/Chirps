# Chirps
## Predicate Paraphrases From Twitter

This is the code used in the paper:

<b>"Acquiring Predicate Paraphrases from News Tweets"</b><br/>
Vered Shwartz, Gabriel Stanovsky and Ido Dagan. *SEM 2017. [link](http://u.cs.biu.ac.il/~havivv/papers/twitter_pred.pdf)
***

<b>The steps performed to create the resource:</b>

We executed the script `get_daily_news_stream.sh` and now we can sit back and relax while the job is performed automatically for us... But if you want a detailed explanation step-by-step:

1. <b>Obtain news tweets:</b></br>
   Querying the [Twitter Search API](https://dev.twitter.com/rest/public/search) for news:

   ```
   get_news_tweets_stream.py --consumer_key=<consumer_key> --consumer_secret=<consumer_secret>
        --access_token=<access_token> --access_token_secret=<access_token_secret> [--until=<until>]
   ```
   
   where `consumer_key`, `consumer_secret`, `access_token` and `access_token_secret` are obtained by registering to the Twitter API as an app, in [here](https://apps.twitter.com/). 
   The optional argument `until` is a date in the format `YYYY/MM/dd` if you'd like to retrieve tweets only until this date. The Search API only supports up to one week ago. If this argument is not specified, it will retrieve current tweets. This script will save the tweets in a file named by the date they were created at.
   
   Important note: we downloaded [TwitterSearch](https://github.com/ckoepp/TwitterSearch) and changed the code to add the
   news filter to the search URL. If you want to get news tweets, you should do the same.

2. <b>Extract propositions:</b></br>
   ```
   prop_extraction --in=[tweet_folder] --out=[prop_folder]
   ```
   
3. <b>Generate positive instances:</b></br>
   ```
   get_corefering_predicates.py [tweets_file] [out_file]
   ```

5. <b>Package the resource:</b></br>

    ```
    cat news_stream/positive/* | cut -f1,2,4,5,6,7,8,10,11,12,13,14 > resource
    python -u package_resource.py resource [repository_dir]
    ```
    where `news_stream/positive/` is where we keep all the positive instances files. `cut` is used to remove the tweets, to comply with Twitter policy. `package_resource.py` updates the resource file under `[repository_dir]\resource` and pushes the changes.
