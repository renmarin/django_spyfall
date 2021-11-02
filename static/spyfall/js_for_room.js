//If for some reasons you need to provide data from template to JS, you need to do the next:
//
//{% block extrascripts %}
//    <script>
//        var my_var_1 = "{{ some_template_data.var_1 }}",
//            my_var_2 = "{{ some_template_data.var_12 }}";
//    </script>
//    <script type="text/JavaScript" src="{%  static 'js/hand_made.js' %}"></script>
//{% endblock %}


var myVar = setInterval(foo, 1000);
function foo() {
    fetch(control_room)
    .then(function (response) {
        return response.json(); // But parse it as JSON this time
    })
    .then(function (json) {
//        console.log('GET response as JSON:');
//        console.log(json); // Here’s our JSON object
//        console.log(`json is of type ${typeof json}`);
//        console.log(`name_value is of type ${typeof json[room_id][0]}`);
//        console.log(`key=${Object.keys(json)[0]} : value=${json[room_id]}`);
        document.getElementById("js_u").innerHTML = `<div id='js_u'>Players: ${json[room_id][0]}</div>`;
        document.getElementById("players_in_game").innerHTML = `<ul>Players in game: ${json[room_id][1]}</ul>`;

        if (new Date().getTime().toString().slice(0, -3) == json[room_id][4].slice(0, 10)) {
//            console.log(`${new Date().getTime().toString().slice(0, -3)} == ${var_time.slice(0, 10)}`);
//            console.log('Game Over!');
//            location.href = new_game;
            alert('Time is up! Choose who is a SPY!')
        } else if (new Date().getTime().toString().slice(0, -3) < json[room_id][4].slice(0, 10)) {
//            a = new Date().getTime().toString().slice(0, -3);
//            b = json[room_id][4].slice(0, 10)
//            console.log(typeof a, a);
//            console.log(typeof b, b);
//            console.log(a == b);
            var now = new Date().getTime();
            var distance = parseInt(json[room_id][4]) - now;  // + json[room_id][5]  ==pause_time
            var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            var seconds = Math.floor((distance % (1000 * 60)) / 1000);
            if (json[room_id][3] == true) {
                document.getElementById("timer").innerHTML = minutes + "m " + seconds + "s ";
                document.getElementById("start/end").value = "Pause";
                if (parseInt(new Date().getTime().toString().slice(0, -3)) == parseInt(json[room_id][4].slice(0, 10)) - 1) {
                    document.getElementById("start/end").disabled = true;
                }
            } else if (json[room_id][3] == false && !json[room_id][4]) {
                document.getElementById("timer").innerHTML = ''
            } else {
                document.getElementById("timer").innerHTML = minutes + "m " + seconds + "s ";
                document.getElementById("start/end").value = "Start";
            };
        };
        if (json[room_id][2] == true) {
            location.href = room;
        };
    });
};

// ----------- Acquiring the token | Getting cookie value

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// new request with POST

const request = new Request(
    control_room,
    {headers: {'X-CSRFToken': csrftoken}}
);
fetch(request, {
    method: 'POST',
    mode: 'same-origin'  // Do not send CSRF token to another domain.
}).then(function(response) {
    return response.text();
}).then(function (text) {
        console.log('POST response as TEXT:');
        console.log(text);
});
