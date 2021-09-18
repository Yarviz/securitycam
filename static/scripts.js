
function post_request(path, json_data, callback) {
    console.log("ajax call")
    $.ajax({
        type : "POST",
        url : path,
        dataType: "json",
        data: JSON.stringify(json_data),
        contentType: 'application/json;charset=UTF-8',
        success: function(response) { callback(response); }
    });
}

function login_user() {
    console.log("login user")
    var userdata = {
        "username": document.getElementById('username').value,
        "password": document.getElementById('password').value
    }

    post_request('/login', userdata, function(data) {
        if (data['result'] == 200) {
            $('#log_text').html("Login success")
            location.href = "/browse_data";
        } else {
            $('#log_text').html(data["message"])
        }
    });
}

function refresh_photos() {
    console.log("get photos")
    post_request('/get_photos', { "all": true }, function(data) {
        var list = document.getElementById("photolist");
        for (const entry of data) {
            var item = document.createElement("li");
            item.appendChild(document.createTextNode(entry[2]));
            list.appendChild(item);
        }
        console.log("get photos2")
    });
}