class Photos {
    constructor(photos) {
        this.photos = photos;
        console.log(this.photos);
        this.entry = -1;
    }

    add_entries(entries) {
        for (const entry of entries) {
            this.photos.push(entry);
        }
        console.log(this.photos)
    }

    get_id(pos) {
        if (this.photos.length <= pos) return null;
        return this.photos[pos][0];
    }

    get_ts(pos) {
        if (this.photos.length <= pos) return null;
        return this.photos[pos][1];
    }

    set_entry(entry) {
        this.entry = entry;
    }

    get_entry() {
        return this.entry;
    }

    delete_entry(entry) {
        this.photos.splice(entry, 1);
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

async function get_hash(data) {
    const encoder = new TextEncoder();
    const encoded = encoder.encode(data);
    const hash = await window.crypto.subtle.digest('SHA-256', encoded);
    return hash;
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
    refresh_photos(true);
    document.getElementById('photolist').addEventListener("click", function(e) {
        var parent = e.target.parentElement;
        var index = Array.prototype.indexOf.call(parent.children, e.target);
        photos.set_entry(index);
        console.log(index);
        $('#timestamp').html(photos.get_ts(index));
        $('#photo_info').show();
        post_request('/photos', { "request": "get", "id": photos.get_id(index) }, function(data) {
            if (data['result'] == 200) {
                $('#photo_img').attr('src', data['data']);
            }
        });
    });
}

function refresh_photos(get_all) {
    console.log("get photos");
    post_request('/photos', { "request": "list", "all": get_all }, function(data) {
        if (data[0] === undefined) return;
        if (photos === undefined) photos = new Photos(data);
        else photos.add_entries(data);

        var list = document.getElementById("photolist");
        for (const entry of data) {
            var item = document.createElement("li");
            item.appendChild(document.createTextNode(entry[1]));
            list.appendChild(item);
        }
    });
    setTimeout(function() { refresh_photos(false) }, 5000);
}

function remove_photo() {
    console.log("remove photo");
    var entry = photos.get_entry();
    if (entry > -1) {
        post_request('/photos', { "request": "delete", "id": photos.get_id(entry) }, function(data) {
            var list = document.getElementById("photolist");
            photos.delete_entry(entry);
            list.removeChild(list.children[entry]);
            $('#photo_img').attr('src', '');
            $('#photo_info').hide();
        });
    }
}