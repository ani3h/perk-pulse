import pandas as pd
import torch
from transformers import BertTokenizer, BertForSequenceClassification, pipeline
import torch.nn.functional as F
import math
import difflib

df = pd.read_csv('../data/flights.csv')
num_classes = df['Card'].nunique()

model = BertForSequenceClassification.from_pretrained(
    'bert-base-uncased', num_labels=num_classes)

model.load_state_dict(torch.load('flight_model.pth'))
model.eval()

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

sentiment_analyzer = pipeline(
    "sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

offer_type_weights = {
    'free upgrade': 10.0,
    'extra baggage': 8.0,
    'priority boarding': 7.0,
    'lounge access': 6.0,
    'discount': 5.0,
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


def scale_score(score):
    return 1 / (1 + math.exp(-10 * (score - 0.1)))


def get_score(offer):
    text = f"{offer['Card']} | {offer['Offer']} | {
        offer['Valid Till']} | {offer['Other Conditions']}"
    inputs = tokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=512,
        padding='max_length',
        return_token_type_ids=True,
        truncation=True,
        return_tensors='pt'
    )

    input_ids = inputs['input_ids'].to(device)
    attention_mask = inputs['attention_mask'].to(device)

    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)

    probs = F.softmax(outputs.logits, dim=1)
    card_index = df['Card'].unique().tolist().index(offer['Card'])
    base_score = probs[0, card_index].item()

    offer_type_score = get_offer_type_score(offer['Offer'])
    conditions_text = offer['Other Conditions']
    sentiment_score = get_sentiment_score(conditions_text)

    # Adjust the combination formula with different powers to increase differentiation
    combined_score = (base_score ** 0.5) * \
        (offer_type_score ** 1.5) * (sentiment_score ** 2)
    final_score = scale_score(combined_score)

    return final_score


def find_matching_offers(card, df):
    # Extract bank name from the card (assuming format "Bank Name Card Type")
    bank_name = ' '.join(card.split()[:2])

    # Look for an exact match first
    exact_match = df[df['Card'].str.fullmatch(card, case=False, na=False)]

    if not exact_match.empty:
        return exact_match

    # If no exact match, look for a generalized card name
    generalized_card_name = f"{bank_name} Credit Cards"
    generalized_match = df[df['Card'].str.contains(
        generalized_card_name, case=False, regex=False)]

    if not generalized_match.empty:
        return generalized_match

    # Fallback: Use similarity scoring for closest match if no exact or generalized match
    card_names = df['Card'].tolist()
    closest_match = difflib.get_close_matches(
        card, card_names, n=1, cutoff=0.7)

    if closest_match:
        # Check similarity ratio to ensure it's a reasonable match
        similarity_ratio = difflib.SequenceMatcher(
            None, card, closest_match[0]).ratio()
        if similarity_ratio >= 0.8:  # Only accept close matches
            similar_match = df[df['Card'] == closest_match[0]]
            return similar_match

    # If no valid match is found, return an empty DataFrame
    return pd.DataFrame()


def predict(card_list):
    global device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    best_offers = []
    related_banks = set()

    for card in card_list:
        matching_offers = find_matching_offers(card, df)

        if matching_offers.empty:
            best_offers.append((card, "No offer available", None))
        else:
            scored_offers = [(offer, get_score(offer))
                             for _, offer in matching_offers.iterrows()]
            best_offer = max(scored_offers, key=lambda x: x[1])
            best_offers.append((card, best_offer[0]['Offer'], best_offer[1]))

            # Get bank name from the card (assuming format "Bank Name Card Type")
            bank_name = card.split()[0]
            related_banks.add(bank_name)

    # Sort best offers by score in descending order
    best_offers = sorted(
        best_offers, key=lambda x: x[2] if x[2] is not None else 0, reverse=True)

    return best_offers


card_list = ["ICICI Bank Rubyx Credit Card",
             "HSBC Bank Credit Card", "Amazon Pay ICICI Bank Credit Card"]

print(predict(card_list))
