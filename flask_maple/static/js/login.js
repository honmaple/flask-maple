$(document).ready(function(){
  $('a#clickCode').click(function() {
    $("#changeCode").attr("src",url.captcha + "?code=" + Math.random());
  });
  function AuthCallBack(response) {
    if (response.status === '200')
    {
      window.location = url.index;
    }
    else
    {
      $("#showerror").show();
      $("#changeCode").attr("src",url.captcha + "?code=" + Math.random());
      $("#captcha").val("");
      if (response.description !==""){
        $("#error").text(response.description);
      }
      else{
        $("#error").text(response.message);
      }
    }
  }
  $('button#login').click(function() {
    $.ajax ({
      type : "POST",
      url : url.login,
      data:JSON.stringify({
        username: $('#username').val(),
        password: $('#password').val(),
        captcha:  $("#captcha").val(),
        remember:  $("#remember").is(':checked')
      }),
      contentType: 'application/json;charset=UTF-8',
      success: function(response) {
        return AuthCallBack(response);
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
      success: function(response) {
        return AuthCallBack(response);
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
      success: function(response) {
        return AuthCallBack(response);
      }
    });
  });
});
