from flask import Blueprint, request, jsonify, current_app
from firebase_admin import firestore

emotion_blp = Blueprint("emotion", __name__, url_prefix="/api/emotion")
db = firestore.client()
