from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/charge', methods=['POST'])
def charge_card():
    # Get credit card and amount details from POST data
    payment_data = request.get_json()
    # Process mock payment
    transaction_id = process_payment(payment_data)  # Define this function
    return jsonify({"transaction_id": transaction_id})
