$(document).ready(function () {
  $("#textarea").keypress(function (e) {
    if (e.which === 13 && !e.shiftKey) {
      e.preventDefault();
      $("#send-message").click();
      $("#textarea").css("height", "50px");
    }
  });

  $("#textarea").on("input", function () {
    $("#textarea").css("height", "50px");
    $("#textarea").css("height", $("#textarea").prop("scrollHeight") + "px");
  });

  $(".chat-messages-field").on("scroll", function () {
    if (
      $(".chat-messages-field").prop("scrollHeight") -
        $(".chat-messages-field").prop("scrollTop") >
      1200
    )
      $(".scroll-down").addClass("active");
    else $(".scroll-down").removeClass("active");
  });

  $(".scroll-down").on("click", function () {
    $(".chat-messages-field")
      .children(".chat-messages")
      .children()
      .last()[0]
      .scrollIntoView({
        behavior: "smooth",
        block: "end",
      });
  });

  $(".chats-header-icon").click(function (event) {
    $(".select-chat").toggleClass("active");
    $(".chats").toggleClass("active");
    $(".content-back").toggleClass("active");
    $(".chats-header").toggleClass("active");
  });

  $(".emote-btn").on("click", function (event) {
    $(".emotes-menu").toggleClass("active");
  });

  $(".emotes-menu").on("click", ".get-emote", function () {
    text = $(this).children("span").text();
    if ($("#textarea").val().length > 0)
      $("#textarea")
        .val($("#textarea").val() + ` ${text} `)
        .trigger("input");
    else $("#textarea").val(`${text} `).trigger("input");
  });

  $(".create-chat").on("click", function (e) {
    $(".create-chat-form").toggleClass("active");
    $(".create-chat-form-content-back").toggleClass("active");
  });
});
