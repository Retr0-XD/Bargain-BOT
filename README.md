# Bargain-BOT
this bot will be used to bargain a product's price use generative AI


# Usage Guide for the Negotiation Chatbot Project

## Overview

This document provides instructions on how to set up and use the negotiation chatbot project. The chatbot uses the Gemini language model to evaluate discount requests, analyze sentiments, and respond to user inputs.

## Prerequisites

- Python 3.x
- Flask
- Requests
- Dotenv

## Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install Dependencies**:
   Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Environment Variables**:
   Create a `.env` file in the root directory and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   ```

## Running the Project

1. **Start the Flask App**:
   Run the Flask application using the following command:
   ```bash
   python app.py
   ```
   The app will start on the default port `5000`. You can change the port in the `app.py` file.

2. **Interacting with the API**:
   Use tools like `curl`, `Postman`, or any HTTP client to interact with the API.

### API Endpoints

#### 1. Start Negotiation

- **Endpoint**: `/start-negotiation`
- **Method**: POST
- **Payload**:
  ```json
  {
    "productName": "Example Product",
    "productPricing": 100,
    "maxDiscount": 20,
    "retailPrice": 120
  }
  ```
- **Response**:
  ```json
  {
    "message": "The current price of Example Product is $120. Please provide a valid reason for requesting a discount.",
    "maxDiscount": 24,
    "discountedPrice": 96
  }
  ```

#### 2. Propose Discount

- **Endpoint**: `/propose-discount`
- **Method**: POST
- **Payload**:
  ```json
  {
    "reason": "I'm a loyal customer.",
    "counterOffer": 110
  }
  ```
- **Response**:
  ```json
  {
    "message": "Your counteroffer of $110 is accepted.",
    "originalPrice": 100,
    "retailPrice": 120,
    "discountApplied": 10,
    "finalPrice": 110,
    "sentiment": "polite",
    "allReasons": ["I'm a loyal customer."]
  }
  ```

#### 3. Accept Offer

- **Endpoint**: `/accept-offer`
- **Method**: POST
- **Response**:
  ```json
  {
    "message": "Offer accepted. Thank you for your purchase!",
    "finalPrice": 96
  }
  ```

#### 4. Reject Offer

- **Endpoint**: `/reject-offer`
- **Method**: POST
- **Response**:
  ```json
  {
    "message": "Offer rejected. No discount will be applied.",
    "finalPrice": 120
  }
  ```

## Summary

This project provides a negotiation chatbot using the Gemini language model to intelligently interact with users. Follow the steps outlined to set up and run the project, and use the API endpoints to simulate negotiation scenarios.
