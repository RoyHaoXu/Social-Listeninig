import pandas as pd
import datetime
import json
from dateutil.parser import parse
import re
import string


def _strip_all_entities(text):
    """Helper to delete all the @ and hashtags from text."""
    entity_prefixes = ['@', '#']
    for separator in string.punctuation:
        if separator not in entity_prefixes:
            text = text.replace(separator, ' ')
    words = []
    for word in text.split():
        word = word.strip()
        if word:
            if word[0] not in entity_prefixes:
                words.append(word)
    return ' '.join(words)


def _text_cleanup(text):
    """Helper to clean up the text."""
    # remove urls
    text = re.sub(r"http\S+", "", text)
    # delete entity
    text = _strip_all_entities(text)

    return text


def process_data_facebook(path_comment, path_post, ID_COL, POST_COL, REPLY_COL, COMMENT_COL, TIME_COMMENT_COL,
                          output_path):
    """
    Function to parse the post and comment json file for facebook data to get cleaned structured data.

    Args:
        path_comment (str): path to comment json file.
        path_post (str): path to post json file.
        ID_COL (str): id column name.
        POST_COL (str): post column name.
        REPLY_COL (str): reply number column name.
        COMMENT_COL (str): comment column name.
        TIME_COMMENT_COL (str): time of comment column name.
        output_path (str): output path

    Returns:
        pd.DataFrame: cleaned structured data with post joined by their comments.

    """
    # facebook data
    comment_data = json.load(open(path_comment, 'r'))
    posts_data = json.load(open(path_post, 'r'))

    # posts
    all_posts = []
    ids = []
    replys = []
    for posts in posts_data:
        for post in posts['data']['node']['timeline_feed_units']['edges']:
            try:
                post_id = post['node']['feedback']['id']
                text = \
                    post['node']['comet_sections']['content']['story']['comet_sections']['message']['story']['message'][
                        'text']
                text = _text_cleanup(text)
                reply = post['node']['comet_sections']['feedback']['story']['feedback_context'][
                    'feedback_target_with_context']['ufi_renderer']['feedback']['comment_count']['total_count']
                all_posts.append(text)
                ids.append(post_id)
                replys.append(reply)
            except (KeyError, TypeError) as exception:
                pass
    fb_posts_df = pd.DataFrame(list(zip(ids, all_posts, replys)), columns=[ID_COL, POST_COL, REPLY_COL])

    # comments
    all_comments = []
    times = []
    ids = []
    for post in comment_data:
        comments = post["data"]["feedback"]["display_comments"]["edges"]
        for comment in comments:
            try:
                text = comment["node"]["body"]["text"]
                text = _text_cleanup(text)
                time = datetime.datetime.fromtimestamp(comment["node"]["created_time"]).date()
                post_id = comment["node"]["parent_feedback"]["id"]
                all_comments.append(text)
                times.append(time)
                ids.append(post_id)
            except (KeyError, TypeError) as exception:
                pass
    fb_comments_df = pd.DataFrame(list(zip(ids, all_comments, times)), columns=[ID_COL, COMMENT_COL, TIME_COMMENT_COL])

    # join the post and comment by the id
    fb_data = pd.merge(fb_posts_df, fb_comments_df, how='outer', on=ID_COL)
    fb_data.to_csv(output_path, index=False)


def process_data_tweet(path, ID_COL, POST_COL, REPLY_COL, COMMENT_COL, TIME_COMMENT_COL, output_path):
    """
    Function to parse the post and comment json file for tweet data to get cleaned structured data.

    Args:
        path (str): path to input tweet json data.
        ID_COL (str): id column name.
        POST_COL (str): post column name.
        REPLY_COL (str): reply number column name.
        COMMENT_COL (str): comment column name.
        TIME_COMMENT_COL (str): time of comment column name.
        output_path (str): output path

    Returns:
        pd.DataFrame: cleaned structured data with post joined by their comments.
    """

    data = json.load(open(path, 'r'))
    all_posts = []
    post_ids = []
    replys = []

    all_comments = []
    comment_times = []
    comment_ids = []

    for i, tweet in enumerate(data):
        try:
            post = tweet['data']['threaded_conversation_with_injections']['instructions'][0]['entries'][0]['content'][
                'itemContent']['tweet_results']['result']['legacy']['full_text']
        except KeyError:
            try:
                post = tweet['data']['user']['result']['timeline']['timeline']['instructions'][0]['entries'][0]['content'][
                    'itemContent']['tweet_results']['result']['legacy']['full_text']
            except KeyError:
                continue

        post = _text_cleanup(post)

        try:
            reply = tweet['data']['threaded_conversation_with_injections']['instructions'][0]['entries'][0]['content'][
                'itemContent']['tweet_results']['result']['legacy']['reply_count']
        except KeyError:
            try:
                reply = tweet['data']['user']['result']['timeline']['timeline']['instructions'][0]['entries'][0]['content'][
                    'itemContent']['tweet_results']['result']['legacy']['reply_count']
            except KeyError:
                continue

        all_posts.append(post)
        post_ids.append(i)
        replys.append(reply)

        try:
            comments = tweet['data']['threaded_conversation_with_injections']['instructions'][0]['entries'][1:]
        except KeyError:
            try:
                comments = tweet['data']['user']['result']['timeline']['timeline']['instructions'][0]['entries'][1:]
            except KeyError:
                continue

        for comment in comments:
            try:
                text = comment['content']['items'][0]['item']['itemContent']['tweet_results']['result']['legacy'][
                    'full_text']
                text = _text_cleanup(text)
                time = parse(
                    comment['content']['items'][0]['item']['itemContent']['tweet_results']['result']['legacy'][
                        'created_at']).date()
                all_comments.append(text)
                comment_times.append(time)
                comment_ids.append(i)
            except KeyError as exception:
                pass
    tw_posts_df = pd.DataFrame(list(zip(post_ids, all_posts, replys)),
                               columns=[ID_COL, POST_COL, REPLY_COL])
    tw_comments_df = pd.DataFrame(list(zip(comment_ids, all_comments, comment_times)),
                                  columns=[ID_COL, COMMENT_COL, TIME_COMMENT_COL])
    tw_data = pd.merge(tw_posts_df, tw_comments_df, how='outer', on=ID_COL)
    tw_data = tw_data.dropna(subset=[COMMENT_COL])
    tw_data.to_csv(output_path, index=False)
