from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_API_URL = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}'

hashponse =""

def generate_ai_response(prompt, context=""):

    print(prompt+" "+context)
    try:
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        },
                        {

                            "text": context
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


def validate_reason(reason, context):
    
    prompt = f'Determine if the following reason is valid for a price drop request: "{reason}". Respond with either "valid" or "invalid" and decide according to the reason'

    ai_response = generate_ai_response(prompt,context)
   
    print(ai_response)

    if ai_response is None or ai_response.strip().lower() == "invalid":
        return False

    return "valid" in ai_response.lower()

def explain_reason(reason):
    prompt = f'provide a one line reason why this reason: "{reason}" is not enough for discount'
    ai_response = generate_ai_response(prompt)
   
    return ai_response
   

def analyze_sentiment(reason):
    prompt = f'Analyze the sentiment of the following text: "{reason}". Respond with either "neutral", "polite" and "rude"  only no other words needed '
    sentiment = generate_ai_response(prompt)

    print(sentiment)

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
    product_name = data.get('productName')
    product_pricing = data.get('productPricing')  
    max_discount_input = data.get('maxDiscount')  
    retail_price = data.get('retailPrice')  

    if not product_name or not product_pricing or not max_discount_input or not retail_price:
        return jsonify({'message': 'Please provide product name, product pricing, max discount, and retail price.'}), 400

    
    max_discount = retail_price * (max_discount_input / 100)
    discounted_price = retail_price - max_discount

    
    negotiation_state['product_name'] = product_name
    negotiation_state['original_price'] = product_pricing
    negotiation_state['retail_price'] = retail_price
    negotiation_state['discounted_price'] = discounted_price
    negotiation_state['max_discount'] = max_discount
    negotiation_state['offers'] = 0

    message = f'The current price of {product_name} is ${retail_price}. Please provide a valid reason for requesting a discount.'
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

    
    if 'reasons' not in negotiation_state:
        negotiation_state['reasons'] = []  

    
    if 'validated_reasons' not in negotiation_state:
        negotiation_state['validated_reasons'] = []  

    if reason not in negotiation_state['validated_reasons']:
        
        is_valid_reason = validate_reason(reason, json.dumps(negotiation_state['reasons']))

        if is_valid_reason:
            
            negotiation_state['validated_reasons'].append(reason)
        else:
            
            negotiation_state['reasons'].append(reason)
            return jsonify({
                'message': 'The reason provided is not valid, so no discount can be applied.',
                'reason': explain_reason(reason),
                'finalPrice': retail_price,
                'allReasons': negotiation_state['reasons']  
            })

    
    negotiation_state['reasons'].append(reason)

    
    sentiment = analyze_sentiment(reason)

    
    
    previous_valid_reason_count = len(negotiation_state['validated_reasons']) - 1  

    
    if previous_valid_reason_count > 1:
        additional_discount = max_discount * 0.05  
        max_discount += additional_discount
        discounted_price = retail_price - max_discount

    
    if sentiment == "polite":
        additional_discount = max_discount * 0.05
        max_discount += additional_discount
        discounted_price = retail_price - max_discount

    
    if counter_offer is not None:
        if counter_offer < discounted_price and counter_offer >= retail_price - max_discount:
            negotiation_state['offers'] += 1
            final_price = counter_offer
            message = f'Your counteroffer of ${counter_offer} is accepted.'
        else:
            return jsonify({
                'message': 'Counteroffer exceeds the maximum allowable discount. The price remains the same.',
                'finalPrice': retail_price,
                'allReasons': negotiation_state['reasons']  
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
        'sentiment': sentiment,
        'allReasons': negotiation_state['reasons']  
    })



@app.route('/accept-offer', methods=['POST'])
def accept_offer():
    final_price = negotiation_state.get('discounted_price', negotiation_state.get('retail_price'))
    return jsonify({
        'message': 'Offer accepted. Thank you for your purchase!',
        'finalPrice': final_price
    })


@app.route('/reject-offer', methods=['POST'])
def reject_offer():
    return jsonify({
        'message': 'Offer rejected. No discount will be applied.',
        'finalPrice': negotiation_state.get('retail_price')
    })


if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
