$(document).ready(function(){
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", g.csrftoken);
      }
    }
  });
  $('#captcha-change').click(function() {
    $("#captcha-code").attr("src","/captcha" + "?code=" + Math.random());
  });
  function AuthCallBack(response) {
    if (response.status === '200')
    {
      window.location = "/";
    }
    else
    {
      $("#captcha-code").attr("src","/captcha" + "?code=" + Math.random());
      $("#captcha").val("");
      if (response.description !==""){
          alert(response.description);
      } else{
          alert(response.message);
      }
    }
  }
  $('button#login').click(function() {
    $.ajax ({
      type : "POST",
      url : "/login",
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
      url : "/register",
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
      url : "/forget",
      data:JSON.stringify({
        email: $('#email').val(),
        captcha:$("#captcha").val()
      }),
      contentType: 'application/json;charset=UTF-8',
      success: function(response) {
        return AuthCallBack(response);
      }
    });
  });
});
