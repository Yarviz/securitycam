class Photos {
    constructor(photos) {
        this.photos = photos;
    }

    get_id(pos) {
        if (this.photos.length <= pos) return null;
        return this.photos[pos][0];
    }

    get_ts(pos) {
        if (this.photos.length <= pos) return null;
        return this.photos[pos][1];
    }
}

var photos;

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
            setTimeout(function () {
                $('#log_text').empty();
            }, 2000);
        }
    });
}

function init_listeners() {
    refresh_photos();
    document.getElementById('photolist').addEventListener("click", function(e) {
        var parent = e.target.parentElement;
        var index = Array.prototype.indexOf.call(parent.children, e.target);
        console.log(index);
        $('#timestamp').html(photos.get_ts(index));
        $('#photo_info').show();
        post_request('/get_photos', { "request": "photo", "id": photos.get_id(index) }, function(data) {
            if (data['result'] == 200) {
                $('#photo_img').attr('src', data['data']);
            }
        });
    });
}

function refresh_photos() {
    console.log("get photos")
    post_request('/get_photos', { "request": "list", "all": true }, function(data) {
        photos = new Photos(data);

        var list = document.getElementById("photolist");
        for (const entry of data) {
            var item = document.createElement("li");
            item.appendChild(document.createTextNode(entry[1]));
            list.appendChild(item);
        }
    });
}