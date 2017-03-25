## Predicate Paraphrase Database

Important note: the resource should be updated every day. If the files in this directory are out of date, check the [Dropbox directory](https://www.dropbox.com/sh/hc1lobwcuo3pvie/AACVs2XRMEDsSlfvlz6Wa8H4a?dl=0).

<hr/>

The resource contains two files:

1. <b>Rules:</b><br/>
   Contains predicate paraphrases and their scores, as a tab separated file with the following fields:
   
   * lemmatized predicate 1
   * lemmatized predicate 2
   * number of instances
   * number of different days within joint instances
   
   The file is sorted by (number of instances) * (number of different days within joint instances), descending, 
   i.e. the confidence of a predicate paraphrase pair is determined by the number of instances and the number of different days 
   (~news events) in which the predicates co-occurred.

2. <b>Instances:</b><br/> 
   Contains the raw instances from which the predicate paraphrases were extracted, as a tab separated file with the following fields:
   
   * tweet id 1
   * predicate 1
   * lemmatized predicate 1
   * arg0 1
   * arg1 1
   * tweet id 2
   * predicate 2
   * lemmatized predicate 2
   * arg0 2
   * arg1 2
   
   To get the tweets, expand the resource by running:
   
   ```
   expand_resource.py --resource_file=instances.tsv --consumer_key=<consumer_key>
        --consumer_secret=<consumer_secret> --access_token=<access_token> 
        --access_token_secret=<access_token_secret>
   ```
   
   where `consumer_key`, `consumer_secret`, `access_token` and `access_token_secret` are obtained by registering to the Twitter API as an app, in [here](https://apps.twitter.com/).
