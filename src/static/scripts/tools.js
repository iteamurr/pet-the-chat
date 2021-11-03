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
});
