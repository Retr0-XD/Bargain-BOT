from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import os
import json


load_dotenv()

app = Flask(__name__)


GEMINI_API_KEY = 'your-api-key'
GEMINI_API_URL = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}'


def generate_ai_response(prompt):
    try:
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            response_data = response.json()
            return response_data['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            print(f"Request to Gemini API failed with status code {response.status_code}")
            return None

    except Exception as e:
        print(f"Error generating AI response: {e}")
        return None


def validate_reason(reason):
    prompt = f'Determine if the following reason is valid for a price drop request: "{reason}". Respond with either "valid" or "invalid".'
    ai_response = generate_ai_response(prompt)

    print(ai_response)

    if ai_response is None or ai_response.strip().lower() == "invalid":
        return False

    return "valid" in ai_response.lower()


def analyze_sentiment(reason):
    prompt = f"Analyze the sentiment of the following text: '{reason}'. Is it polite, neutral, or rude?"
    sentiment = generate_ai_response(prompt)

    if sentiment is None:
        return "neutral"  

    if "polite" in sentiment.lower():
        return "polite"
    elif "rude" in sentiment.lower():
        return "rude"
    
    return "neutral"


negotiation_state = {}


@app.route('/start-negotiation', methods=['POST'])
def start_negotiation():
    data = request.get_json()
    original_price = data.get('originalPrice')
    retail_price = data.get('retailPrice')

    if not original_price or not retail_price:
        return jsonify({'message': 'Please provide both original price and retail price.'}), 400

    
    max_discount = retail_price * 0.40
    discounted_price = retail_price - max_discount

    
    negotiation_state['original_price'] = original_price
    negotiation_state['retail_price'] = retail_price
    negotiation_state['discounted_price'] = discounted_price
    negotiation_state['max_discount'] = max_discount
    negotiation_state['offers'] = 0

    message = f'The current price is ${retail_price}. Please provide a valid reason for requesting a discount.'
    return jsonify({'message': message, 'maxDiscount': max_discount, 'discountedPrice': discounted_price})


@app.route('/propose-discount', methods=['POST'])
def propose_discount():
    data = request.get_json()
    reason = data.get('reason')
    counter_offer = data.get('counterOffer', None)

    original_price = negotiation_state.get('original_price')
    retail_price = negotiation_state.get('retail_price')
    max_discount = negotiation_state.get('max_discount')
    discounted_price = negotiation_state.get('discounted_price')

    if not reason:
        return jsonify({'message': 'Please provide a valid reason for requesting a discount.'}), 400

    
    is_valid_reason = validate_reason(reason)

    
    sentiment = analyze_sentiment(reason)
    
    if sentiment == "polite":
        
        additional_discount = max_discount * 0.05
        max_discount += additional_discount
        discounted_price = retail_price - max_discount

    if not is_valid_reason:
        return jsonify({
            'message': 'The reason provided is not valid, so no discount can be applied.',
            'finalPrice': retail_price
        })

    
    if counter_offer is not None:
        if counter_offer < discounted_price and counter_offer >= retail_price - max_discount:
            negotiation_state['offers'] += 1
            final_price = counter_offer
            message = f'Your counteroffer of ${counter_offer} is accepted.'
        else:
            return jsonify({
                'message': 'Counteroffer exceeds the maximum allowable discount. The price remains the same.',
                'finalPrice': retail_price
            })
    else:
        final_price = discounted_price
        message = f'Thank you for your valid reason. A discount has been applied.'

    return jsonify({
        'message': message,
        'originalPrice': original_price,
        'retailPrice': retail_price,
        'discountApplied': max_discount,
        'finalPrice': final_price,
        'sentiment': sentiment
    })


