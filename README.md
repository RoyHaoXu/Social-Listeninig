### Social Listening
#### Medusa Team I


### Get Started


---
#### 0. Install Dependencies and Models
```shell script
pip install -r requirments
python -m spacy download en_core_web_lg
```


---
#### 1. Data Preparation

---

1.1 Put data json files into the ```./data``` directory

```
Put:

a. facebook comment file (XX_comments.json) and post file (XX_posts.json) for each company into the folder

b. tweet file for each company (XX_tw_twit.json) into the folder
```

Right now, te pipeline is only setup to take the Facebook and Twitter json data. Config the  ```src.data_processing.py```
file to add additional json parsing function for other channels.

---
1.2 Process the data for each channel and each company

This part of the pipeline will parse and clean the json files to generate structured data for each channel of the social media data. 
It will extract the posts and the corresponding comments along with the commenting time.

Facebook:
```shell script
python pipeline.py process --path_post=[PATH_TO_POSTS] --path_comment=[PATH_TO_POSTS] --channel="facebook" --output=[OUTPUT_PATH]
```
Example:
```shell script
python pipeline.py process --path_post="data/fb_posts_spacex.json" --path_comment="data/fb_comments_spacex.json" --channel="facebook" --output="./data/facebook_data_spaceX.csv"
python pipeline.py process --path_post="data/fb_posts_bo.json" --path_comment="data/fb_comments_bo.json" --channel="facebook" --output="./data/facebook_data_bo.csv"
python pipeline.py process --path_post="data/fb_posts_vg.json" --path_comment="data/fb_comments_vg.json" --channel="facebook" --output="./data/facebook_data_vg.csv"
```

Twitter:
```shell script
python pipeline.py process --path_both=[PATH_TO_TWEET_FILE] --channel="tweet" --output=[OUTPUT_PATH]
```
Example:
```shell script
python pipeline.py process --path_both="data/tweet_spacex.json" --channel="tweet" --output="./data/tweet_data_spaceX.csv"
python pipeline.py process --path_both="data/tweet_bo.json" --channel="tweet" --output="./data/tweet_data_vg.csv"
python pipeline.py process --path_both="data/tweet_vg.json" --channel="tweet" --output="./data/tweet_data_bo.csv"
```


---
#### 2. Information Extraction

---
2.1  Extract sentiment and entity

This part of the pipeline will take the cleaned data from the previous part as input, then process the posts and comments and extract sentiment score for the comments as well as mentioned entities from both the comments and the posts.

Using open source solution:
```shell script
python pipeline.py extraction --api=open_source --input=[CLEANED_DATA_PATH]  --output=[OUTPUT_PATH]
```

Example:
```shell script
python pipeline.py extraction --api=open_source --input="./data/tweet_data_spaceX.csv"  --output="./results/tw_spacex_extracted.csv"      
python pipeline.py extraction --api=open_source --input="./data/tweet_data_vg.csv"  --output="./results/tw_vg_extracted.csv"  
python pipeline.py extraction --api=open_source --input="./data/tweet_data_bo.csv"  --output="./results/tw_bo_extracted.csv" 

python pipeline.py extraction --api=open_source --input="./data/facebook_data_spaceX.csv"  --output="./results/fb_spacex_extracted.csv" 
python pipeline.py extraction --api=open_source --input="./data/facebook_data_vg.csv"  --output="./results/fb_vg_extracted.csv" 
python pipeline.py extraction --api=open_source --input="./data/facebook_data_bo.csv"  --output="./results/fb_bo_extracted.csv"
```

Using Azure solution:
```shell script
python pipeline.py extraction --api=azure --input=[CLEANED_DATA_PATH]  --output=[OUTPUT_PATH]
```

Example:
```shell script
python pipeline.py extraction --api=azure --input="./data/tweet_data_spaceX.csv"  --output="./results/tw_spacex_extracted.csv"      
python pipeline.py extraction --api=azure --input="./data/tweet_data_vg.csv"  --output="./results/tw_vg_extracted.csv"  
python pipeline.py extraction --api=azure --input="./data/tweet_data_bo.csv"  --output="./results/tw_bo_extracted.csv" 

python pipeline.py extraction --api=azure --input="./data/facebook_data_spaceX.csv"  --output="./results/fb_spacex_extracted.csv" 
python pipeline.py extraction --api=azure --input="./data/facebook_data_vg.csv"  --output="./results/fb_vg_extracted.csv" 
python pipeline.py extraction --api=azure --input="./data/facebook_data_bo.csv"  --output="./results/fb_bo_extracted.csv"
```

---
#### 3. Dashboard data preparation

---

This part of the pipeline will take the processed data and turn it into dashboard ready data. There will be two output file:

- ```Sentiment.csv``` which contains the sentiment for all company's & channel's posts and comments
- ```Entity.csv``` which contains the entity information for all company's & channel's posts and comments

The files will then be used by PowerBI to visualize the insights.

Get entity csv: 

(Note that the entity extraction target can either be from the posts or the comments, change the entity flag to ```--entity=post``` to use posts as target)

```shell script
python pipeline.py summarize_entity \
--entity=comment \
--info_files=[FILE_PATHS_SEPARATE_BY_COMMA] \
--channels=[CHANNEL_NAMES_SEPARATE_BY_COMMA] \
--companies=[COMPANY_NAMES_SEPARATE_BY_COMMA] \
--output=[OUTPUT_PATH]
```

Example:
```shell script
python pipeline.py summarize_entity \
--info_files="./results/tw_spacex_extracted.csv,./results/tw_vg_extracted.csv,./results/tw_bo_extracted.csv,./results/fb_spacex_extracted.csv,./results/fb_vg_extracted.csv,./results/fb_bo_extracted.csv" \
--channels="tweet,tweet,tweet,facebook,facebook,facebook" \
--companies="spacex,vg,bo,spacex,vg,bo" \
--output="./results/entity.csv"
```

Get sentiment csv:
```shell script
python pipeline.py summarize_sentiment \
--info_files=[FILE_PATHS_SEPARATE_BY_COMMA] \
--channels=[CHANNEL_NAMES_SEPARATE_BY_COMMA] \
--companies=[COMPANY_NAMES_SEPARATE_BY_COMMA] \
--output=[OUTPUT_PATH]
```

Example:
```shell script
python pipeline.py summarize_sentiment \
--info_files="./results/tw_spacex_extracted.csv,./results/tw_vg_extracted.csv,./results/tw_bo_extracted.csv,./results/fb_spacex_extracted.csv,./results/fb_vg_extracted.csv,./results/fb_bo_extracted.csv" \
--channels="tweet,tweet,tweet,facebook,facebook,facebook" \
--companies="spacex,vg,bo,spacex,vg,bo" \
--output="./results/sentiment.csv"
```



