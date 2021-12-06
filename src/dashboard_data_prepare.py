import pandas as pd
import unicodedata
import numpy as np


def _remove_non_ascii(entity):
    """Helper to remove special characters."""
    entity = unicodedata.normalize('NFKD', entity).encode('ascii', 'ignore').decode('utf-8', 'ignore')
    return entity


def _to_lowercase(entity):
    """Helper to convert to lower case."""
    return entity.lower()


def _entity_normalization(entity):
    """Helper to normalize entities."""
    entity = _to_lowercase(entity)
    entity = _remove_non_ascii(entity)
    if entity=='':
        return np.nan
    return entity


def _generate_entity_dict(row, sentiment_col, score_col, time_comment_col, entity_col, company, channel):
    """Helper to generate entity information list."""
    return [(_entity_normalization(e.split(',')[0]),
             e.split(',')[1],
             row[time_comment_col],
             row[sentiment_col],
             row[score_col],
             company,
             channel
             ) for e in row[entity_col].split('|')]


def entity_summerize(data_files, entity_col, sentiment_col, score_col, time_comment_col, output_path):
    """Generate entity csv file for dashboard using."""

    entity_sentiment_df = pd.DataFrame()
    # merge all the entity data files and add company/channel tags
    for data_file in data_files:
        company = data_file[0]
        channel = data_file[1]
        path = data_file[2]

        data = pd.read_csv(path)
        data = data.dropna(subset=[entity_col])

        entities = list(
            data.apply(lambda row: _generate_entity_dict(row, sentiment_col, score_col, time_comment_col, entity_col, company, channel), axis=1))
        entities = [item for sublist in entities for item in sublist]
        df = pd.DataFrame(entities, columns=['entity', 'type', 'time', 'sentiment', 'score', 'company', 'channel'])
        df = df.dropna(subset=['entity'])
        entity_sentiment_df = entity_sentiment_df.append(df)

    entity_sentiment_df.to_csv(output_path, index=False)


def sentiment_summerize(data_files, post_col, reply_col, comment_col, sentiment_col, score_col, time_comment_col, output_path):
    """Generate sentiment csv file for dashboard using."""

    sentiment_df = pd.DataFrame()
    # merge all the sentiment data files and add company/channel tags
    for data_file in data_files:
        company = data_file[0]
        channel = data_file[1]
        path = data_file[2]

        data = pd.read_csv(path)
        data = data[[post_col, reply_col, comment_col, sentiment_col, score_col, time_comment_col]]
        data['company'] = company
        data['channel'] = channel
        sentiment_df = sentiment_df.append(data)

    sentiment_df.to_csv(output_path, index=False)