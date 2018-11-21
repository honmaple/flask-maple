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
    function AjaxRequest(url, method, data) {
        $.ajax ({
            type: method,
            url: url,
            data: data,
            contentType: 'application/json;charset=UTF-8',
        }).done(function(response) {
            window.location = "/";
        }).fail(function(error) {
            $("#captcha-code").attr("src","/captcha" + "?code=" + Math.random());
            $("#captcha").val("");
            alert(error.responseJSON.message);
        });
    }
    $('button#login').click(function() {
        AjaxRequest("/login", "POST", JSON.stringify({
            username: $('#username').val(),
            password: $('#password').val(),
            captcha:  $("#captcha").val(),
            remember:  $("#remember").is(':checked')
        }));
    });
    $('button#register').click(function() {
        AjaxRequest("/register", "POST", JSON.stringify({
            username: $('#username').val(),
            email: $('#email').val(),
            password: $('#password').val(),
            captcha:$("#captcha").val()
        }));
    });
    $('button#forget').click(function() {
        AjaxRequest("/forget", "POST", JSON.stringify({
            email: $('#email').val(),
            captcha:$("#captcha").val()
        }));
    });
});
