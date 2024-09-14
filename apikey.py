from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

print(GEMINI_API_KEY)