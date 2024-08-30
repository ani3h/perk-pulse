import pandas as pd
import torch
from transformers import BertTokenizer, BertForSequenceClassification, pipeline
import torch.nn.functional as F

# Load the CSV data to determine the number of unique cards (classes)
df = pd.read_csv('../data/movies.csv')
num_classes = df['Card'].nunique()

# Initialize the model with the correct number of classes
model = BertForSequenceClassification.from_pretrained(
    'bert-base-uncased', num_labels=num_classes)
model.load_state_dict(torch.load('credit_card_model.pth'))
model.eval()

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

sentiment_analyzer = pipeline(
    "sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

offer_type_weights = {
    'free': 10.0,
    'complimentary': 10.0,
    'discount': 5.0,
    'reward points': 3.0,
}


def get_sentiment_score(text):
    result = sentiment_analyzer(text)[0]
    if result['label'] == 'POSITIVE':
        return 0.7 + (result['score'] / 3)
    else:
        return 0.7 - (result['score'] / 3)


def get_offer_type_score(offer_text):
    offer_text = offer_text.lower()
    for keyword, weight in offer_type_weights.items():
        if keyword in offer_text:
            return weight
    return 1.0


def scale_score(score, factor=1.5):
    return score ** factor


def predict(card_names):
    predictions = []

    for card_name in card_names:
        # Filter the DataFrame to get offers for the current card
        card_offers = df[df['Card'] == card_name]['Offer'].tolist()

        if not card_offers:  # Check if there are no offers for the card
            print(f"No offer available for {card_name}")
            predictions.append(
                {'card': card_name, 'offer': None, 'score': None})
            continue

        best_offer = None
        best_score = -float('inf')

        for offer_text in card_offers:
            sentiment_score = get_sentiment_score(offer_text)
            offer_type_score = get_offer_type_score(offer_text)
            combined_score = scale_score(sentiment_score * offer_type_score)

            if combined_score > best_score:
                best_score = combined_score
                best_offer = offer_text

        if best_offer:
            predictions.append(
                {'card': card_name, 'offer': best_offer, 'score': best_score})

    return predictions
