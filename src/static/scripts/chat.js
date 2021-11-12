$(document).ready(function () {
  var socket = io();

  var scroll = 0;
  var chat_link = main_chat_link;
  var username_color = "#9ACD32";
  joinChat(chat_link);

  socket.on("create_message", function (data) {
    var username_div = `<div class="username" style="color: ${data["username_color"]};">${data["username"]}:</div>`;
    var message_div = `<div class="message-items">${data["data"]}</div>`;
    var user_message = `<div class="user-message">${username_div}${message_div}</div>`;
    $(".chat-messages").append(user_message);
    scrollChat();
  });

  socket.on("system_message", function (data) {
    var message_div = `<div class="system-items">${data["data"]}</div>`;
    var system_message = `<div class="system-message">${message_div}</div>`;
    $(".chat-messages").append(system_message);
    scrollChat();
    $(".chat-header-name").children("span").eq(0).text(data["chat_name"]);
  });

  socket.on("new_chat", function (data) {
    var chat_name_p = `<p class="chat-name" id="${data["chat_link"]}">${data["chat_name"]}</p>`;
    var chat_div = `<div class="select-chat">${chat_name_p}</div>`;
    $(".chats-content").append(chat_div);
    joinChat(data["chat_link"]);
  });

  $("#send-message").on("click", function () {
    if ($.trim($("#textarea").val()).length > 0) {
      socket.emit("send_message", {
        msg: $("#textarea").val(),
        username: username,
        chat_link: chat_link,
        username_color: username_color,
      });
      $("#textarea").val("");
    }
    return false;
  });

  $("#submit-chat-creation").on("click", function () {
    if ($("#enter-chat-name").val().length > 0) {
      socket.emit("create_chat", {
        chat_name: $("#enter-chat-name").val(),
        admin: username,
        current_user: socket.id,
      });
      $("#enter-chat-name").val("");
      $("#cancel-chat-creation").click();
    } else $(".create-chat-form-content").children("small").eq(0).attr("style", "visibility: visible");
    return false;
  });

  $(".chats").on("click", ".select-chat", function () {
    selected_chat = $(this).children(".chat-name").attr("id");
    if (selected_chat !== chat_link) {
      leaveChat(chat_link);
      joinChat(selected_chat);
    }
    return false;
  });

  function joinChat(chat) {
    $(".chat-messages").empty();
    username_color = getNewUsernameColor();
    socket.emit("join", {
      username: username,
      chat_link: chat,
      username_color: username_color,
    });
    chat_link = chat;
  }

  function leaveChat(chat) {
    socket.emit("leave", {
      username: username,
      chat_link: chat,
      username_color: username_color,
    });
  }

  function scrollChat() {
    var new_scroll = $(".chat-messages").prop("scrollTop");
    if (new_scroll >= scroll) {
      $(".chat-messages").children().last()[0].scrollIntoView({
        behavior: "smooth",
        block: "end",
      });
      scroll = new_scroll;
    }
  }

  function getNewUsernameColor() {
    const colors = [
      "#FF0000",
      "#008000",
      "#B22222",
      "#FF7F50",
      "#9ACD32",
      "#FF4500",
      "#2E8B57",
      "#DAA520",
      "#D2691E",
      "#5F9EA0",
      "#1E90FF",
      "#FF69B4",
      "#8A2BE2",
      "#00FF7F",
    ];
    const random = Math.floor(Math.random() * colors.length);
    return colors[random];
  }
});
