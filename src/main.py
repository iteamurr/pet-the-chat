"""
    This module is responsible for the configuration and launch of the chat.
"""

from decouple import config
from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask_login import LoginManager
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from flask_login import current_user
from flask_socketio import SocketIO
from flask_socketio import emit
from flask_socketio import join_room
from flask_socketio import leave_room

from api.forms import RegistrationForm
from api.forms import LoginForm
from api.models import db
from api.models import User
from api.tools import FormHandler
from api.tools import Helpers
from api.tools import get_chat_template_variables


app = Flask(__name__)
app.config["SECRET_KEY"] = config("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = config("SQLALCHEMY_DATABASE_URI")

db.init_app(app)

handler = FormHandler(db)

login_manager = LoginManager(app)
login_manager.init_app(app)

socketio = SocketIO(app)


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        handler.registration_form(form)
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = handler.login_form(form)
        login_user(user)
        return redirect(url_for("chat"))

    return render_template("login.html", form=form)


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/chat", methods=["GET", "POST"])
@login_required
def chat():
    variables = get_chat_template_variables(current_user)
    return render_template("chat.html", **variables)


@app.route("/chat/join/<chat_link>")
def join_chat(chat_link):
    hlp = Helpers(db)
    was_joined = hlp.join_chat(chat_link, current_user.id)

    if was_joined:
        variables = get_chat_template_variables(current_user)
        variables["current_chat"] = chat_link
        return render_template("chat.html", **variables)

    return redirect(url_for("chat"))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@socketio.on("send_message")
def create_message(data):
    hlp = Helpers()
    message = hlp.create_message(data)
    emit("create_message", message, room=data["chat_link"])


@socketio.on("create_chat")
def create_chat(data):
    hlp = Helpers(db)
    new_data = hlp.create_chat(data["chat_name"], current_user.id)
    emit("new_chat", new_data, room=data["current_user"])


@socketio.on("join")
def join(data):
    join_room(data["chat_link"])

    hlp = Helpers()
    new_data = hlp.create_system_message(data, "{} has joined the room {}.")
    emit("system_message", new_data, room=data["chat_link"])


@socketio.on("leave")
def leave(data):
    leave_room(data["chat_link"])

    hlp = Helpers()
    new_data = hlp.create_system_message(data, "{} has left the room {}.")
    emit("system_message", new_data, room=data["chat_link"])


if __name__ == "__main__":
    socketio.run(app)
