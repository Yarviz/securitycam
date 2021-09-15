
function login_user()
{
    var userdata = {
        "username": document.getElementById('username').value,
        "password": document.getElementById('password').value
    }

    $.ajax({
    type : "POST",
    url : '/login',
    dataType: "json",
    data: JSON.stringify(userdata),
    contentType: 'application/json;charset=UTF-8',
    success: function (data) {
            if (data['result'] == 200) {
                $('#log_text').html("Login success")
                location.href = "/browse_data";
            } else {
                $('#log_text').html(data["message"])
            }
        }
    });
}