"""
    This module provides tools for working with user data and user sessions.
"""

import re
from json import load
from uuid import uuid4
from hashlib import md5
from typing import Any
from typing import Dict
from typing import Optional

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound

from .forms import RegistrationForm
from .forms import LoginForm
from .models import User
from .models import Room
from .models import Chat


def get_chat_template_variables(user) -> Dict[str, Any]:
    """Get chat template variables from the database.

    :param user: Current authorized user.
    """
    all_chats = Room.query.filter_by(user_id=user.id).all()
    user_chats = {
        chat.chat_link: Chat.query.filter_by(link=chat.chat_link).first().name
        for chat in all_chats
    }
    emotes = get_emotes()
    connection_chat_link = Chat.query.get(1).link

    data = {
        "username": user.username,
        "chats": user_chats,
        "emotes": emotes,
        "current_chat": connection_chat_link,
    }
    return data


def get_emotes() -> Dict[str, str]:
    """Get a dictionary of emotes from a file."""
    with open("./api/emotes.json", "r", encoding="utf8") as emotes_json:
        emotes = load(emotes_json)

    return emotes


def create_connection_chat(db: SQLAlchemy) -> None:
    """Create the first chat that the user will connect to.

    :param db: Current database.
    """
    db.create_all()

    try:
        Chat.query.get(1).link
    except (AttributeError, NoResultFound):
        chat = Chat(name="Connection", link=str(uuid4()))
        db.session.add(chat)
        db.session.commit()


class FormHandler:
    """This class is responsible for getting information from forms
    and working with it. Through this class there is interaction
    with the database, writing and reading from it.
    """

    def __init__(self, db: SQLAlchemy) -> None:
        self.db = db

    def registration_form(self, form: RegistrationForm) -> None:
        """Get information from the registration form. Write the user
        to the database and automatically add him to the first chat.

        :param form: Registration form with user data.
        """
        username = str(form.username.data)
        password = str(form.password.data)
        hash_pswd = md5(password.encode("utf-8")).hexdigest()

        # Add a user to the database.
        user = User(username=username, password=hash_pswd)
        self.db.session.add(user)
        self.db.session.commit()

        # Add a user to his first chat.
        user_id = User.query.filter_by(username=username).first().id
        connection_chat = Chat.query.get(1)
        connection_room = Room(
            chat_id=connection_chat.id,
            user_id=user_id,
            chat_link=connection_chat.link,
        )
        self.db.session.add(connection_room)
        self.db.session.commit()

    @staticmethod
    def login_form(form: LoginForm) -> User:
        """Get a user, with the name obtained from the form,
        from the database.

        :param form: Login form with user data.
        """
        username = form.username.data
        user = User.query.filter_by(username=username).first()
        return user


class Helpers:
    """This object contains tools that process information received
    from the user or from a system that reports on the user's status.
    """

    _usr_msg_templ = '<div class="user-message">{}{}</div>'
    _username_templ = '<div class="username" style="color: {};">{}:</div>'
    _msg_content_templ = '<div class="message-items">{}</div>'
    _msg_item_templ = '<span class="user-message-item">{}</span>'
    _msg_emote_templ = '<img src="{}" class="user-message-emote">'

    _system_msg_templ = '<div class="system-message">{}</div>'
    _system_msg_item_templ = '<div class="system-items">{}</div>'

    _chat_templ = '<div class="select-chat">{}</div>'
    _chat_name_templ = '<p class="chat-name" id="{}">{}</p>'

    def __init__(self, db: Optional[SQLAlchemy] = None) -> None:
        self.db = db

    def _create_message_content(self, user_message: str) -> str:
        """Create an object containing emotes and user text
        from the user's message text.

        :param user_message: The user's original unaltered message.
        """
        content = ""
        message_items = re.split(r"(:\w+:)", user_message)
        emotes = re.findall(r"(:\w+:)", user_message)
        emotes_json = get_emotes()

        for item in message_items:
            if item in emotes:
                emote = item[1:-1]
                if emote in emotes_json:
                    emote_src = emotes_json[emote]
                    content += self._msg_emote_templ.format(emote_src)
                else:
                    content += self._msg_item_templ.format(item)
            else:
                content += self._msg_item_templ.format(item)

        return content

    def create_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an object from the user's text containing the
        original text, but with text emotes changed to images.

        :param data: Information received from the frontend.
                     It must contain the user's name, his
                     nickname color and the user's message.
        """
        msg_content = self._create_message_content(data["msg"])

        username = self._username_templ.format(
            data["username_color"], data["username"]
        )
        content = self._msg_content_templ.format(msg_content)
        user_message = self._usr_msg_templ.format(username, content)
        message = {"message": user_message}
        return message

    def create_system_message(
        self, data: Dict[str, Any], msg_templ: str
    ) -> Dict[str, Any]:
        """Create an object that will be displayed as a system message.
        The (1) username and (2) chat name will be inserted into the message.

        :param data: Information received from the frontend.
                     It must contain the user's nickname and a link
                     to the chat with which the interaction was made.
        :param msg_templ: The message that should be displayed.
        """
        chat_name = Chat.query.filter_by(link=data["chat_link"]).first().name
        msg_content = msg_templ.format(data["username"], chat_name)

        system_msg_item = self._system_msg_item_templ.format(msg_content)
        system_message = self._system_msg_templ.format(system_msg_item)
        data = {"message": system_message, "chat_name": chat_name}
        return data

    def create_chat(self, chat_name: str, user_id: int) -> Dict[str, Any]:
        """Create a chat and add the user to this chat.

        :param chat_name: Name of the chat to create.
        :param user_id: ID of the current authorized user.
        """
        chat_link = str(uuid4())

        # Add the user to a new chat.
        new_room = Room(user_id=user_id, chat_link=chat_link)
        self.db.session.add(new_room)
        self.db.session.commit()

        # Create a new chat.
        new_chat = Chat(name=chat_name, link=chat_link)
        new_chat.child.append(new_room)
        self.db.session.add(new_chat)
        self.db.session.commit()

        # Create an html chat object.
        chat_name = self._chat_name_templ.format(chat_link, chat_name)
        new_chat = self._chat_templ.format(chat_name)
        data = {"chat": new_chat, "chat_link": chat_link}
        return data

    def join_chat(self, chat_link: str, user_id: int) -> bool:
        """Add a user to the chat, if this chat exists.

        :param chat_link: Link to the chat that the user wants to join.
        :param user_id: ID of the current authorized user.
        """

        exists = Room.query.filter_by(chat_link=chat_link).first()
        is_unavailable = Room.query.filter_by(
            chat_link=chat_link, user_id=user_id
        ).first()

        if exists and not is_unavailable:
            current_chat_id = Chat.query.filter_by(link=chat_link).first().id
            new_room = Room(
                chat_id=current_chat_id, user_id=user_id, chat_link=chat_link
            )
            self.db.session.add(new_room)
            self.db.session.commit()
            return True

        return False
