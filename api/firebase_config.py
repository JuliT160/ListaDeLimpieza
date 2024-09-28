import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("api/lista-de-limpieza-353d33339f47.json")
firebase_admin.initialize_app(cred)

db = firestore.client()