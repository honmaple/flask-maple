$(document).ready(function(){
  $('a#clickCode').click(function() {
    $("#changeCode").attr("src",url.captcha + "?code=" + Math.random());
  });
  $('button#login').click(function() {
    $.ajax ({
      type : "POST",
      url : url.login,
      data:JSON.stringify({
        username: $('#username').val(),
        password: $('#password').val(),
        captcha:  $("#captcha").val()
      }),
      contentType: 'application/json;charset=UTF-8',
      success: function(result) {
        if (result.judge == true)
        {
          window.location = url.index;
        }
        else
        {
          $("#showerror").show();
          $("#error").text(result.error);
          $("#changeCode").attr("src",url.captcha + "?code=" + Math.random());
        }
      }
    });
  });
  $('button#register').click(function() {
    $.ajax ({
      type : "POST",
      url : url.register,
      data:JSON.stringify({
        username: $('#username').val(),
        email: $('#email').val(),
        password: $('#password').val(),
        captcha:$("#captcha").val()
      }),
      contentType: 'application/json;charset=UTF-8',
      success: function(result) {
        if (result.judge == true)
        {
          window.location = url.index;
        }
        else
        {
          $("#showerror").show();
          $("#error").text(result.error);
          $("#changeCode").attr("src",url.captcha + "?code=" + Math.random());

        }
      }
    });
  });
  $('button#forget').click(function() {
    $.ajax ({
      type : "POST",
      url : url.forget,
      data:JSON.stringify({
        confirm_email: $('#confirm_email').val(),
        captcha:$("#captcha").val()
      }),
      contentType: 'application/json;charset=UTF-8',
      success: function(result) {
        if (result.judge == true)
        {
          window.location = url.index;
        }
        else
        {
          $("#showerror").show();
          $("#error").text(result.error);
          $("#changeCode").attr("src",url.captcha + "?code=" + Math.random());
        }
      }
    });
  });
});
