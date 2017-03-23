consumer_key='YOUR_KEY_HERE'
consumer_secret='YOUR_KEY_HERE'
access_token='YOUR_KEY_HERE'
access_token_secret='YOUR_KEY_HERE'

while true; do 
	
	while [ $(date +%H:%M) != "00:00" ]; do
		sleep 59
  done
  
  # Start collecting news for the next day
  pkill -f get_news_tweets_stream.py;
  python -u get_news_tweets_stream.py $consumer_key $consumer_secret $access_token $access_token_secret &
  
  # Get propositions and positive instances for the previous day, package and release a new version of the resource
  last_file=`date -d "yesterday" '+%Y_%m_%d'`;
  (python -u prop_extraction.py --in=news_stream/tweets/$last_file --out=news_stream/props/$last_file.prop > prop.log;
  python -u get_corefering_predicates.py news_stream/props/$last_file.prop news_stream/positive/$last_file;
  cat news_stream/positive/* | cut -f1,2,4,5,6,7,8,10,11,12,13,14 > resource;
  python -u package_resource.py resource resource_dir;
  zip ~/Dropbox/resource/resource.zip resource_dir/*.tsv;
  cp ~/Dropbox/resource/resource.zip P3DB/resource;
  git --git-dir=P3DB/.git --work-tree=P3DB/ commit -m "update resource" resource/*;
  git --git-dir=P3DB/.git --work-tree=P3DB/ push origin master) &
  
  # Sleep before checking again...
  sleep 60
done
