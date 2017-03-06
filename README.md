# TwitterPA
## A Dataset of Predicate-Argument Coreference from Twitter

This is the code used in the paper:

<b>"In Other Words: Analyzing Lexical Variability in Event Coreference"</b><br/>
Vered Shwartz, Gabriel Stanovsky and Ido Dagan. ACL 2017. [link](???) (TBD).

The dataset can be found [here](http://u.cs.biu.ac.il/~nlp/resources/downloads/twitter-pa/) (TBD).

***

<b>To create a similar dataset:</b>

1. Create a directory with tweet files (e.g. a different directory for each day), each file in the following format: `tweet_id\ttweet`
2. Extract propositions: `prop_extraction --in=[tweet_folder] --out=[prop_folder]`
3. Generate positive instances: for each proposition file, run `get_corefering_predicates.py [tweets_file] [out_file]`
4. Generate negative instances: 

`create_negative_sampling_svo_instances.py [positive_instances_file] [negative_instances_file] [actions_log_file] [ratio_neg_pos]`

* `positive_instances_file` is the concatenated output from step 3, a file of positive instances with dates.
* `negative_instances_file` is the output file containing the negative instances.
* `actions_log_file` is the output file documenting the changes done to the tweets (needed when downloading the tweets again from Twitter).
* `ratio_neg_pos` is the required ratio of negative to positive instances (e.g. 4).

5. To package the dataset:

