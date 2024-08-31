from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import model.flight_nlp as flight_nlp
import model.movies_nlp as movies_nlp

app = Flask(__name__)
CORS(app, resources={r"/predict": {"origins": "http://127.0.0.1:5500"}})


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json

        # Extract prediction type and credit cards list
        prediction_type = data.get('type', '').lower()
        credit_card_dicts = data.get('credit_cards', [])

        # Validate data
        if not credit_card_dicts:
            return jsonify({'error': 'No credit cards provided for prediction.'}), 400

        # Convert list of dictionaries to list of credit card names
        credit_cards = [card.get('name', '')
                        for card in credit_card_dicts if 'name' in card]

        # Validate that credit card names were extracted
        if not credit_cards:
            return jsonify({'error': 'Invalid credit card data provided.'}), 400

        # Select model based on prediction type
        if prediction_type == 'movie':
            predictions = movies_nlp.predict(credit_cards)
        elif prediction_type == 'flight':
            predictions = flight_nlp.predict(credit_cards)
        else:
            return jsonify({'error': 'Invalid prediction type. Must be "movie" or "flight".'}), 400

        # Return the predictions in a JSON response
        return jsonify({'predictions': predictions})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
