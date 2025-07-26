import os
import jwt
from datetime import datetime, timedelta
from flask import Flask, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config.config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(100), unique=True, nullable=False)
    provider = db.Column(db.String(20), nullable=False)
    nickname = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)

with app.app_context():
    db.create_all()

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
KAKAO_REDIRECT_URI = f"http://{Config.AUTH_HOST}:{Config.AUTH_PORT}/auth/kakao/callback"

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
NAVER_REDIRECT_URI = f"http://{Config.AUTH_HOST}:{Config.AUTH_PORT}/auth/naver/callback"

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = f"http://{Config.AUTH_HOST}:{Config.AUTH_PORT}/auth/google/callback"

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

@app.route('/')
def index():
    return "Social Login Test"

@app.route('/auth/kakao')
def kakao_login():
    kakao_auth_url = (
        f"https://kauth.kakao.com/oauth/authorize"
        f"?client_id={KAKAO_REST_API_KEY}"
        f"&redirect_uri={KAKAO_REDIRECT_URI}"
        f"&response_type=code"
    )
    return redirect(kakao_auth_url)

@app.route('/auth/kakao/callback')
def kakao_callback():
    code = request.args.get('code')
    if not code:
        return "인증 코드가 없습니다.", 400

    token_url = "https://kauth.kakao.com/oauth/token"
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': KAKAO_REST_API_KEY,
        'redirect_uri': KAKAO_REDIRECT_URI,
        'code': code,
    }
    token_response = requests.post(token_url, data=token_data)
    token_json = token_response.json()

    if 'error' in token_json:
        return jsonify(error=token_json['error']), 500

    access_token = token_json.get("access_token")

    user_info_url = "https://kapi.kakao.com/v2/user/me"
    headers = {'Authorization': f'Bearer {access_token}'}
    user_info_response = requests.get(user_info_url, headers=headers)
    user_info_json = user_info_response.json()

    social_id = f"kakao_{user_info_json['id']}"
    user = User.query.filter_by(social_id=social_id).first()

    if not user:
        new_user = User(
            social_id=social_id,
            provider='kakao',
            nickname=user_info_json['properties']['nickname'],
            email=user_info_json.get('kakao_account', {}).get('email'),
            profile_image=user_info_json['properties'].get('profile_image')
        )
        db.session.add(new_user)
        db.session.commit()
        user = new_user

    token = generate_token(user.id)
    return jsonify(access_token=token)

@app.route('/auth/naver')
def naver_login():
    naver_auth_url = (
        f"https://nid.naver.com/oauth2.0/authorize"
        f"?response_type=code"
        f"&client_id={NAVER_CLIENT_ID}"
        f"&redirect_uri={NAVER_REDIRECT_URI}"
        f"&state=STATE_STRING"
    )
    return redirect(naver_auth_url)

@app.route('/auth/naver/callback')
def naver_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    if not code:
        return "인증 코드가 없습니다.", 400

    token_url = "https://nid.naver.com/oauth2.0/token"
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': NAVER_CLIENT_ID,
        'client_secret': NAVER_CLIENT_SECRET,
        'redirect_uri': NAVER_REDIRECT_URI,
        'code': code,
        'state': state,
    }
    token_response = requests.post(token_url, data=token_data)
    token_json = token_response.json()

    if 'error' in token_json:
        return jsonify(error=token_json['error']), 500

    access_token = token_json.get("access_token")

    user_info_url = "https://openapi.naver.com/v1/nid/me"
    headers = {'Authorization': f'Bearer {access_token}'}
    user_info_response = requests.get(user_info_url, headers=headers)
    user_info_json = user_info_response.json()['response']

    social_id = f"naver_{user_info_json['id']}"
    user = User.query.filter_by(social_id=social_id).first()

    if not user:
        new_user = User(
            social_id=social_id,
            provider='naver',
            nickname=user_info_json.get('nickname'),
            email=user_info_json.get('email'),
            profile_image=user_info_json.get('profile_image')
        )
        db.session.add(new_user)
        db.session.commit()
        user = new_user

    token = generate_token(user.id)
    return jsonify(access_token=token)

@app.route('/auth/google')
def google_login():
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=email%20profile"
    )
    return redirect(google_auth_url)

@app.route('/auth/google/callback')
def google_callback():
    code = request.args.get('code')
    if not code:
        return "인증 코드가 없습니다.", 400

    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code',
    }
    token_response = requests.post(token_url, data=token_data)
    token_json = token_response.json()

    if 'error' in token_json:
        return jsonify(error=token_json['error']), 500

    access_token = token_json.get("access_token")

    user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    headers = {'Authorization': f'Bearer {access_token}'}
    user_info_response = requests.get(user_info_url, headers=headers)
    user_info_json = user_info_response.json()

    social_id = f"google_{user_info_json['id']}"
    user = User.query.filter_by(social_id=social_id).first()

    if not user:
        new_user = User(
            social_id=social_id,
            provider='google',
            nickname=user_info_json.get('name'),
            email=user_info_json.get('email'),
            profile_image=user_info_json.get('picture')
        )
        db.session.add(new_user)
        db.session.commit()
        user = new_user

    token = generate_token(user.id)
    return jsonify(access_token=token)

if __name__ == '__main__':
    app.run(host=Config.AUTH_HOST, port=Config.AUTH_PORT)
