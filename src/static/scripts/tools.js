$(document).ready(function () {
  $("#textarea").keypress(function (e) {
    if (e.which === 13 && !e.shiftKey) {
      e.preventDefault();
      $('#send_message').click();
      $('#textarea').attr('rows', 1);
    }
  });

  $("#textarea").keypress(function (e) {
    if (e.which === 13 && e.shiftKey) {
      if ($('#textarea').attr('rows') < 5)
        $('#textarea').attr('rows', parseInt($('#textarea').attr('rows')) + 1);
    }
  });

  $("#textarea").on('input', function () {
    if ($('#textarea').val().length === 0)
      $('#textarea').attr('rows', 1);
  });

  $("#chat").on('scroll', function () {
    if ($('#chat').prop('scrollHeight') - $('#chat').prop('scrollTop') > 1200)
      $('.scroll-down').toggleClass('scroll-down scroll-down-flex');
    else
      $('.scroll-down-flex').toggleClass('scroll-down-flex scroll-down');
  });

  $(".scroll-down").on('click', function () {
    $('#chat').children().last()[0].scrollIntoView({
      behavior: "smooth",
      block: "end"
    });
  });

  $('.chats-header-icon').click(function(event) {
    $('.select-chat').toggleClass('active');
    $('.chats-menu').toggleClass('active');
    $('.content-back').toggleClass('active');
    $('.chats-header-menu').toggleClass('active');
  });
});
