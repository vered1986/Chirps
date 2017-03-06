# TwitterPA
## A Dataset of Predicate-Argument Coreference from Twitter

This is the code used in the paper:

<b>"In Other Words: Analyzing Lexical Variability in Event Coreference"</b><br/>
Vered Shwartz, Gabriel Stanovsky and Ido Dagan. (TBD).

The dataset can be found [here](http://u.cs.biu.ac.il/~nlp/resources/downloads/twitter-pa/) (TBD).

***

<b>To create a similar dataset:</b>

1. Create a directory with tweet files (e.g. a different directory for each day), each file in the following format: `tweet_id\ttweet`

2. Extract propositions: 
   ```
   prop_extraction --in=[tweet_folder] --out=[prop_folder]`
   ```
   
3. Generate positive instances: for each proposition file, run: 
   ```
   get_corefering_predicates.py [tweets_file] [out_file]
   ```
   
4. Generate negative instances: 
   ```
   create_negative_sampling_svo_instances.py [positive_instances_file] [negative_instances_file] 
   [actions_log_file] [ratio_neg_pos]
   ```
   
  * `positive_instances_file` is the concatenated output from step 3, a file of positive instances with dates.
  * `negative_instances_file` is the output file containing the negative instances.
  * `actions_log_file` is the output file documenting the changes done to the tweets (needed when downloading the tweets again from Twitter).
  * `ratio_neg_pos` is the required ratio of negative to positive instances (e.g. 4).

5. To package the dataset:

  1. Generate the full dataset file:
     ```
     cut -f2,3,4,5,6,7,8,9,10,11,12,13 positive/* > positive_instances.tsv
     sed -i "s/$/\tTrue/" positive_instances.tsv
     sed -i "s/$/\tFalse/" negative_instances.tsv
     cat positive_instances.tsv negative_instances.txt | shuf > dataset.tsv
     ```

  2. Generate a version without the tweets (only tweet IDs):
     ```
     cut -f1,3,4,5,6,7,9,10,11,12,13 dataset.tsv > dataset_without_tweets.tsv
     ```

  3. Generate the script to download the full dataset from Twitter:
     ```
     create_download_dataset_script.py dataset.tsv [negative_instances_log_file] [out_script_file]
     ```

6. To download the full dataset:

  1. Register to the [Twitter API](https://apps.twitter.com/) and obtain consumer key, consumer secret, access token and access token secret.

  2. Download the full dataset using the script `[out_script_file]` (e.g. `expand_dataset.py`) with the following arguments:

    * `--dataset_file` the dataset file without tweets (`dataset_without_tweets.tsv` or the dataset file in the TwitterPA dataset you downloaded)
    * `--consumerkey` the Twitter app consumer key
    * `--consumersecret` the Twitter app consumer secret
    * `--accesstoken` the Twitter app API token
    * `--accesstokensecret` the Twitter app API token secret
