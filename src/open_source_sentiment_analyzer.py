import re
import pandas as pd


def _give_emoji_free_text(text):
    """
    Get rid of emojis from text.

    Args:
        text (str): input text.

    Returns:
        str: cleaned text.
    """
    emoji_pattern = re.compile(r""" [\U0001F600-\U0001F64F] # emoticons \
                                     |\
                                     [\U0001F300-\U0001F5FF] # symbols & pictographs\
                                     |\
                                     [\U0001F680-\U0001F6FF] # transport & map symbols\
                                     |\
                                     [\U0001F1E0-\U0001F1FF] # flags (iOS)\
                              """, re.VERBOSE)

    return emoji_pattern.sub('', text)


def get_sentiment(text, model, sentiment_score_map):
    """
    Given a text string, get sentiment analysis results.

    Args:
        text (str): target text.
        model (transformer sentiment model): sentiment model.
        sentiment_score_map (dict): mapping from sentiment class to quantitative score.

    Returns:
        dict: information dictionary containing sentiment class, prediction confidence and corresponding sentiment score.
    """
    # if api failed, returned failed record
    try:
        result = model(text)[0]
    except:
        return {"sentiment": 'N/A',
                "confidence": 0,
                "score": 0}

    return {"sentiment": result['label'],
            "confidence": result['score'],
            "score": sentiment_score_map[result['label']]}


def get_entity(text, ner, blacklist):
    """
    Given a text string, get sentiment analysis results.

    Args:
        text (str): target text.
        ner (spacy ner pipeline): ner model.
        blacklist (list): list of entity type that we don't want to include.

    Returns:
        list: list of extracted entity along with the entity type (separate by comma)
    """
    text = ner(_give_emoji_free_text(text))
    return '|'.join(list(set([e.text + ',' + e.label_ for e in text.ents if e.label_ not in blacklist])))


def get_text_analysis_columns(data_path, POST_COL, COMMENT_COL, SENTIMENT_COL,
                              CONFIDENCE_COL, SCORE_COL, ENTITY_POST_COL, ENTITY_COMMENT_COL,
                              transformer_sentiment_analyzer, spacy_ner, entity_blacklist, sentiment_score_map,
                              output_path):
    """

    Args:
        data_path (str): path to data.
        POST_COL (str): post column name.
        COMMENT_COL (str): comment column name.
        SENTIMENT_COL (str): sentiment column name.
        CONFIDENCE_COL (str): sentiment prediction confidence column name.
        SCORE_COL (str): sentiment score column name.
        ENTITY_POST_COL (str): post entity column name.
        ENTITY_COMMENT_COL (str): comment entity column name.
        transformer_sentiment_analyzer (transformer sentiment model): sentiment model.
        spacy_ner (spacy ner pipeline): ner model.
        entity_blacklist (list): list of entity type that we don't want to include.
        sentiment_score_map (dict): mapping from sentiment class to quantitative score.
        output_path (str): output path.

    Returns:
        None
    """
    data = pd.read_csv(data_path)
    data['sentiment_results'] = data[COMMENT_COL].apply(
        lambda e: get_sentiment(str(e), transformer_sentiment_analyzer, sentiment_score_map))
    data[SENTIMENT_COL] = data['sentiment_results'].apply(lambda e: e['sentiment'])
    data[CONFIDENCE_COL] = data['sentiment_results'].apply(lambda e: e['confidence'])
    data[SCORE_COL] = data['sentiment_results'].apply(lambda e: e['score'])

    data[ENTITY_POST_COL] = data[POST_COL].apply(
        lambda e: get_entity(str(e), spacy_ner, entity_blacklist))
    data[ENTITY_COMMENT_COL] = data[COMMENT_COL].apply(
        lambda e: get_entity(str(e), spacy_ner, entity_blacklist))

    data.to_csv(output_path, index=False)
