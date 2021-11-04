from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for

from decouple import config

from hashlib import md5

from flask_login import LoginManager
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from flask_login import current_user

from flask_socketio import SocketIO
from flask_socketio import emit
from flask_socketio import join_room
from flask_socketio import leave_room

from uuid import uuid4

from .api.forms import RegistrationForm
from .api.forms import LoginForm
from .api.models import db
from .api.models import User
from .api.models import Room
from .api.models import Chat
from .api.tools import create_chat_message


app = Flask(__name__)
app.config['SECRET_KEY'] = config('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = config('SQLALCHEMY_DATABASE_URI')

db.init_app(app)

login_manager = LoginManager(app)
login_manager.init_app(app)

socketio = SocketIO(app)

@app.route('/')
def index():
  return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
  form = RegistrationForm()

  if form.validate_on_submit():
    username = form.username.data
    hash_pswd = md5(str(form.password.data).encode('utf-8')).hexdigest()

    user = User(username=username, password=hash_pswd)
    db.session.add(user)
    db.session.commit()

    user_id = User.query.filter_by(username=username).first().id
    first_user_chat = Chat.query.get(1).link
    first_user_room = Room(user_id=user_id, chat_link=first_user_chat)
    db.session.add(first_user_room)
    db.session.commit()

    return redirect(url_for('login'))

  return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm()

  if form.validate_on_submit():
    username = form.username.data
    user = User.query.filter_by(username=username).first()
    login_user(user)
    return redirect(url_for('chat'))

  return render_template('login.html', form=form)

@app.route('/logout', methods=['GET'])
@login_required
def logout():
  logout_user()
  return redirect(url_for('login'))

@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
  chat_links = Room.query.filter_by(user_id=current_user.id).all()
  main_chat_link = Chat.query.get(1).link
  user_chats = {
    chat.chat_link: Chat.query.filter_by(link=chat.chat_link).first().name
    for chat in chat_links
  }

  return render_template(
    'chat.html',
    username=current_user.username,
    chats=user_chats,
    main_chat=main_chat_link
  )

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)

@socketio.on('send_message')
def create_message(data):
  message = create_chat_message(data['msg'])
  new_data = {
    'data': message,
    'username': data['username'],
    'username_color': data['username_color']
  }
  emit('create_message', new_data, room=data['chat_link'])

@socketio.on('create_chat')
def create_chat(data):
  chat_link = str(uuid4())
  new_chat = Chat(name=data['chat_name'], link=chat_link)
  db.session.add(new_chat)
  db.session.commit()

  new_room = Room(user_id=current_user.id, chat_link=chat_link)
  db.session.add(new_room)
  db.session.commit()

  new_data = {'chat_link': chat_link,'chat_name': data['chat_name'],}
  emit('new_chat', new_data, room=data['current_chat'])

@socketio.on('join')
def join(data):
  join_room(data['chat_link'])

  room_name = Chat.query.filter_by(link=data['chat_link']).first().name
  message = f'{data["username"]} has joined the room {room_name}.'
  new_data = {
    'data': message,
    'username': data['username'],
    'username_color': data['username_color']
  }

  emit('create_message', new_data, room=data['chat_link'])

@socketio.on('leave')
def leave(data):
  leave_room(data['chat_link'])

  room_name = Chat.query.filter_by(link=data['chat_link']).first().name
  message = f'{data["username"]} has left the room {room_name}.'
  new_data = {
    'data': message,
    'username': data['username'],
    'username_color': data['username_color']
  }

  emit('create_message', new_data, room=data['chat_link'])

if __name__ == '__main__':
  app.run()
