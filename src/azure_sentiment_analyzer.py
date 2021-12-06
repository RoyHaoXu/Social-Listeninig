import errno
import os
import signal
import functools
import pandas as pd


class TimeoutError(Exception):
    """Exception class for api timeout."""
    pass


def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    """Timeout call back function."""
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result
        return wrapper
    return decorator


def batch_information_extraction(documents, cog_client):
    """
    Given a list of documents, extract text analytics information include language, sentiment, key phrase and entities using Azure API.

    Args:
        documents (list): list of text for information extraction.
        cog_client (azure api instance): Azure text analytics client.

    Returns:
        dict: information dictionary.
    """
    information = {}
    # detect language
    detectedLanguage = cog_client.detect_language(documents)
    information['language'] = [doc.primary_language.name for doc in detectedLanguage if not doc.is_error]

    # Get sentiment
    sentimentAnalysis = cog_client.analyze_sentiment(documents, show_opinion_mining=True)
    information['sentiment'] = [{'positive': doc.confidence_scores.positive,
                                 'neutral': doc.confidence_scores.neutral,
                                 'negative': doc.confidence_scores.negative} for doc in sentimentAnalysis if
                                not doc.is_error]
    # key phrases
    keyphrase = cog_client.extract_key_phrases(documents)
    information['key_phrase'] = [doc.key_phrases for doc in keyphrase if not doc.is_error]
    # NER
    ner = cog_client.recognize_entities(documents)
    information['entities'] = [
        [{'entity': e.text, 'category': e.category, 'confidence_score': e.confidence_score} for e in doc.entities] for
        doc in ner if not doc.is_error]

    return information


@timeout(3)
def get_sentiment_azure(text, cog_client, sentiment_score_map):
    """
    Given a text string, get sentiment analysis results.

    Args:
        text (str): target text.
        cog_client (azure api instance): Azure text analytics client.
        sentiment_score_map (dict): mapping from sentiment class to quantitative score.

    Returns:
        dict: information dictionary containing sentiment class, prediction confidence and corresponding sentiment score.
    """
    sentimentAnalysis = cog_client.analyze_sentiment([text], show_opinion_mining=True)[0]
    sentiment = sentimentAnalysis.sentiment
    if sentiment == 'positive':
        confidence = sentimentAnalysis.confidence_scores.positive
    elif sentiment == 'neutral':
        confidence = sentimentAnalysis.confidence_scores.neutral
    else:
        confidence = sentimentAnalysis.confidence_scores.negative

    return {"sentiment": sentiment,
            "confidence": confidence,
            "score": sentiment_score_map[sentiment]}


@timeout(3)
def get_entity_azure(text, cog_client, blacklist):
    """
    Given a text string, get sentiment analysis results.

    Args:
        text (str): target text.
        cog_client (azure api instance): Azure text analytics client.
        blacklist (list): list of entity type that we don't want to include.

    Returns:
        list: list of extracted entity along with the entity type (separate by comma)
    """
    ner = cog_client.recognize_entities(documents=[text])
    nes = [[e.text+','+e.category for e in doc.entities if e.category not in blacklist] for doc in ner if not doc.is_error][0]

    return nes


def _get_sentiment_wrapper(text, cog_client, sentiment_score_map):
    """Wrapper for sentiment extraction to implement timeout error."""
    try:
        return get_sentiment_azure(text, cog_client, sentiment_score_map)
    except TimeoutError:
        return {'sentiment': 'timeout', 'confidence': 0, 'score': 0}


def _get_entity_wrapper(text, cog_client, blacklist):
    """Wrapper for entity extraction to implement timeout error."""
    try:
        return '|'.join(get_entity_azure(text, cog_client, blacklist))
    except TimeoutError:
        return ''


def get_text_analysis_columns_azure(data_path, POST_COL, COMMENT_COL, SENTIMENT_COL,
                                    CONFIDENCE_COL, SCORE_COL, ENTITY_POST_COL, ENTITY_COMMENT_COL,
                                    cog_client, entity_blacklist, sentiment_score_map,
                                    output_path):
    """
    Process the data to extract sentiment and entity information and store the new csv file to target.

    Args:
        data_path (str): path to data.
        POST_COL (str): post column name.
        COMMENT_COL (str): comment column name.
        SENTIMENT_COL (str): sentiment column name.
        CONFIDENCE_COL (str): sentiment prediction confidence column name.
        SCORE_COL (str): sentiment score column name.
        ENTITY_POST_COL (str): post entity column name.
        ENTITY_COMMENT_COL (str): comment entity column name.
        cog_client (azure api instance): Azure text analytics client.
        entity_blacklist (list): list of entity type that we don't want to include.
        sentiment_score_map (dict): mapping from sentiment class to quantitative score.
        output_path (str): output path.

    Returns:
        None
    """
    data = pd.read_csv(data_path)

    # extract sentiment and create corresponding columns
    data['sentiment_results'] = data[COMMENT_COL].apply(
        lambda e: _get_sentiment_wrapper(str(e), cog_client, sentiment_score_map))
    data[SENTIMENT_COL] = data['sentiment_results'].apply(lambda e: e['sentiment'])
    data[CONFIDENCE_COL] = data['sentiment_results'].apply(lambda e: e['confidence'])
    data[SCORE_COL] = data['sentiment_results'].apply(lambda e: e['score'])

    # extract entity and create corresponding columns
    data[ENTITY_POST_COL] = data[POST_COL].apply(
        lambda e: _get_entity_wrapper(str(e), cog_client, entity_blacklist))
    data[ENTITY_COMMENT_COL] = data[COMMENT_COL].apply(
        lambda e: _get_entity_wrapper(str(e), cog_client, entity_blacklist))

    # save file
    data.to_csv(output_path, index=False)
