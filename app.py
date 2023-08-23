from flask import Flask, render_template, redirect, url_for, session, request, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

CLIENT_ID = 'your-client-ID'
CLIENT_SECRET = 'your-client-Secret'
REDIRECT_URI = 'http://localhost:5000/google-callback'
TOKEN_URI = 'https://oauth2.googleapis.com/token'

@app.route('/')
def index():
    return render_template('login.html', google_login_url=url_for('google_login'))

@app.route('/google-login')
def google_login():
    auth_url = (
        f'https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=email profile openid https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile&prompt=consent'
    )
    return redirect(auth_url)

@app.route('/google-callback')
def google_callback():
    code = request.args.get('code')
    data = {
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Use the requests library for making HTTP requests
    token_response = requests.post(
        TOKEN_URI,
        data=data,
        headers=headers
    )

    token_data = token_response.json()

    # Verify the ID token's authenticity
    id_token_info = id_token.verify_oauth2_token(token_data['id_token'], google_requests.Request(), CLIENT_ID)

    # Store user information in the session
    session['user'] = {
        'id': id_token_info['sub'],
        'name': id_token_info['name'],
        'email': id_token_info['email']
    }

    return redirect(url_for('profile'))

@app.route('/Chatroom')
def profile():
    user = session.get('user')
    if user:
        return render_template('chatroom.html')
    else:
        return 'Not logged in'

chat_messages = []

@app.route('/send-message', methods=['POST'])
def send_message():
    user = session.get('user')
    if user:
        data = request.get_json()
        message = data.get('message')
        if message:
            chat_messages.append({'sender': user['name'], 'text': message})
            return '', 200
    return '', 403  # Forbidden

@app.route('/fetch-messages', methods=['GET'])
def fetch_messages():
    return jsonify(chat_messages)
    
if __name__ == '__main__':
    app.run(debug=True)
