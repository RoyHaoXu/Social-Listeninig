import argparse
import config
from src.data_processing import process_data_facebook, process_data_tweet
from src.open_source_sentiment_analyzer import get_text_analysis_columns
from src.azure_sentiment_analyzer import get_text_analysis_columns_azure
from src.dashboard_data_prepare import entity_summerize, sentiment_summerize

if __name__ == '__main__':
    # arguments
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('step', help='Which step to run',
                        choices=['process', 'extraction', 'summarize_entity', 'summarize_sentiment'])
    parser.add_argument('--path_post', help='Local path of post data')
    parser.add_argument('--path_comment', help='Local path of comment data')
    parser.add_argument('--path_both', help='Local path of comment and post data')
    parser.add_argument('--channel', help='social media channel')
    parser.add_argument('--entity', help='where to extract entity')
    parser.add_argument('--api', help='text analytics api to use')
    parser.add_argument('--input', help='Path to data')
    parser.add_argument('--output', help='Path to save output')
    parser.add_argument('--info_files', help='Path to information dfs')
    parser.add_argument('--companies', help='corresponding company names')
    parser.add_argument('--channels', help='corresponding channel names')

    args = parser.parse_args()

    # pipeline

    # process data
    if args.step == 'process':
        if args.channel == 'facebook':
            process_data_facebook(args.path_comment, args.path_post, config.ID_COL, config.POST_COL,
                                  config.REPLY_COL, config.COMMENT_COL, config.TIME_COMMENT_COL, args.output)
        elif args.channel == 'tweet':
            process_data_tweet(args.path_both, config.ID_COL, config.POST_COL,
                               config.REPLY_COL, config.COMMENT_COL, config.TIME_COMMENT_COL, args.output)

    # extract sentiment and entity information
    elif args.step == 'extraction':
        if args.api == 'open_source':
            get_text_analysis_columns(args.input, config.POST_COL, config.COMMENT_COL, config.SENTIMENT_COL,
                                      config.CONFIDENCE_COL, config.SCORE_COL, config.ENTITY_POST_COL,
                                      config.ENTITY_COMMENT_COL,
                                      config.TRANSFORMER_SENTIMENT_ANALYZER, config.SPACY_NER,
                                      config.ENTITY_BLACKLIST_SPACY,
                                      config.TRANSFORMER_SENTIMENT_MAP,
                                      args.output)
        elif args.api == 'azure':
            get_text_analysis_columns_azure(args.input, config.POST_COL, config.COMMENT_COL, config.SENTIMENT_COL,
                                            config.CONFIDENCE_COL, config.SCORE_COL, config.ENTITY_POST_COL,
                                            config.ENTITY_COMMENT_COL,
                                            config.AZURE_TEXT_ANALYZER,
                                            config.ENTITY_BLACKLIST_AZURE,
                                            config.AZURE_SENTIMENT_MAP,
                                            args.output)

    # prepare dashboard data
    elif args.step == 'summarize_entity':
        data_files = [(company, channel, path) for company, channel, path in
                      zip(args.companies.split(','), args.channels.split(','), args.info_files.split(','))]

        if args.entity == 'comment':
            entity_summerize(data_files,
                             config.ENTITY_COMMENT_COL,
                             config.SENTIMENT_COL,
                             config.SCORE_COL,
                             config.TIME_COMMENT_COL,
                             args.output)

        elif args.entity == 'post':
            entity_summerize(data_files,
                             config.ENTITY_POST_COL,
                             config.SENTIMENT_COL,
                             config.SCORE_COL,
                             config.TIME_COMMENT_COL,
                             args.output)

    elif args.step == 'summarize_sentiment':
        data_files = [(company, channel, path) for company, channel, path in
                      zip(args.companies.split(','), args.channels.split(','), args.info_files.split(','))]
        sentiment_summerize(data_files,
                            config.POST_COL,
                            config.REPLY_COL,
                            config.COMMENT_COL,
                            config.SENTIMENT_COL,
                            config.SCORE_COL,
                            config.TIME_COMMENT_COL,
                            args.output)