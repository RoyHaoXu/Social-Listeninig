from dotenv import load_dotenv
import os
from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer
import spacy
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

# Azure analyzer init
load_dotenv()
cog_endpoint = os.getenv('COG_SERVICE_ENDPOINT')
cog_key = os.getenv('COG_SERVICE_KEY')
credential = AzureKeyCredential(cog_key)
AZURE_TEXT_ANALYZER = TextAnalyticsClient(endpoint=cog_endpoint, credential=credential)
ENTITY_BLACKLIST_AZURE = ['Url', 'Quantity', 'DateTime']
AZURE_SENTIMENT_MAP = {'positive': 1, 'neutral': 0, 'negative': -1}

# Open source analyzer init
# transformer
TRANSFORMER_SENTIMENT_ANALYZER = pipeline("sentiment-analysis",  model="nlptown/bert-base-multilingual-uncased-sentiment")
TRANSFORMER_SENTIMENT_MAP = {'1 star': 1,
                             '2 stars': 2,
                             '3 stars': 3,
                             '4 stars': 4,
                             '5 stars': 5}

# spacy ner
SPACY_NER = spacy.load("en_core_web_lg")
ENTITY_BLACKLIST_SPACY = ['DATE', 'TIME', 'QUANTITY', 'CARDINAL']


# Data columns
ID_COL = 'id'
POST_COL = 'post'
REPLY_COL = 'reply'
COMMENT_COL = 'comment'
TIME_COMMENT_COL = 'time_comment'
CONFIDENCE_COL = 'confidence'
SCORE_COL = 'score'
SENTIMENT_COL = 'sentiment'
ENTITY_POST_COL = 'entity_post'
ENTITY_COMMENT_COL = 'entity_comment'

