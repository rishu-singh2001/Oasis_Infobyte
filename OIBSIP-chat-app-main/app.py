
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, leave_room, join_room
from cryptography.fernet import Fernet
import os

# Initialize the Flask app and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat_app.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)
socketio = SocketIO(app)

# Load or generate encryption key
def load_key():
    key_file = 'secret.key'
    if os.path.exists(key_file):
        with open(key_file, 'rb') as key_file:
            key = key_file.read().strip()
            if len(key) == 44:
                return key
            else:
                raise ValueError("Invalid key length.")
    else:
        key = Fernet.generate_key()
        with open(key_file, 'wb') as key_file:
            key_file.write(key)
        return key

encryption_key = load_key()
fernet = Fernet(encryption_key)

# Define database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    room = db.Column(db.String(80), nullable=False)
    message = db.Column(db.LargeBinary, nullable=False)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        return redirect(url_for('chat', username=username))
    else:
        return redirect(url_for('index'))

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    if User.query.filter_by(username=username).first():
        return redirect(url_for('index'))
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/chat/<username>')
def chat(username):
    return render_template('chat.html', username=username)

@app.route('/upload/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/history/<room>')
def history(room):
    messages = Message.query.filter_by(room=room).all()
    decrypted_messages = [
        {
            'username': msg.username,
            'message': fernet.decrypt(msg.message).decode()
        }
        for msg in messages
    ]
    return jsonify(decrypted_messages)

# Socket.IO events

@socketio.on('message')
def handle_message(data):
    username = data['username']
    room = data['room']
    message = data['message']

    # Encrypt and save the incoming message
    encrypted_message = fernet.encrypt(message.encode())
    new_message = Message(username=username, room=room, message=encrypted_message)
    db.session.add(new_message)
    db.session.commit()

    # Broadcast the incoming message to the room
    emit('message', {'username': username, 'message': message}, room=room)
    # Check for various keywords in the message and generate the appropriate reply
    if "hello" in message:
        reply_message = "Hi there! How can I help you today?"
    elif "bye" in message:
        reply_message = "Goodbye! Have a great day!"
    elif "good morning" in message:
        reply_message = "Good morning! How's your day starting off?"
    elif "time" in message:
        reply_message = "I’m not sure of the current time, but you might want to check your device for the latest update."
    elif "homework" in message:
        reply_message = "I'd be happy to help! What subject or topic do you need assistance with?"
    elif "down" in message:
        reply_message = "I'm sorry to hear that. Is there anything specific that's bothering you, or would you like to talk about it?"
    elif "weather" in message:
        reply_message = "I can't check the weather for you, but you might want to look it up on a weather website or app for the latest updates."
    elif "gym" in message:
        reply_message = "That sounds great! Hope you have a fantastic workout. Do you have a specific fitness goal you're working towards?"
    elif "recipe" in message:
        reply_message = "Sure! What type of recipe are you looking for? I can suggest something based on what you have in mind."
    elif "movie" in message:
        reply_message = "Nice! Do you need any recommendations or are you already set on what to watch?"
    elif "gift" in message:
        reply_message = "Got it! What’s your friend interested in? I can help with some gift ideas based on their hobbies or preferences."
    elif "day" in message:
        reply_message = "I don't have personal experiences, but I hope your day is going well! Anything exciting happening today?"
    elif "book" in message:
        reply_message = "That’s awesome! What book did you read? I'd love to hear more about it or discuss it with you."
    elif "overwhelmed" in message:
        reply_message = "I'm sorry to hear that. Maybe breaking your tasks into smaller steps could help manage the workload. Is there a specific part of work that's particularly challenging?"
    elif "travel" in message:
        reply_message = "Absolutely! Are you looking for tips on a specific destination, or general advice for travel?"
    elif "relax" in message:
        reply_message = "A few relaxing activities include reading a book, taking a warm bath, or doing some light stretching. What usually helps you unwind?"
    else:
        reply_message = "Thanks for your message!"



    encrypted_reply = fernet.encrypt(reply_message.encode())
    reply_entry = Message(username='Bot', room=room, message=encrypted_reply)
    db.session.add(reply_entry)
    db.session.commit()

    # Send the reply back to the room
    emit('message', {'username': 'Bot', 'message': reply_message}, room=room)

@socketio.on('join')
def handle_join(data):
    room = data['room']
    join_room(room)
    emit('message', {'username': 'System', 'message': f'{data["username"]} has joined the room.'}, room=room)

@socketio.on('leave')
def handle_leave(data):
    room = data['room']
    leave_room(room)
    emit('message', {'username': 'System', 'message': f'{data["username"]} has left the room.'}, room=room)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure this is inside the app context
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)  # For development only
