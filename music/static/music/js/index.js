console.log("This is 1st jsssssssssss !")
function album_add() {
        console.log("This is album add function !");
        $('#album-add-modal').modal('toggle');
}

function album_add_submit() {
    console.log("This is album add function !");
    var elements = document.getElementById("album-add-form").elements;
    var obj ={};
    for(var i = 1 ; i < elements.length -1 ; i++){
        var item = elements.item(i);
        obj[item.name] = item.value;
    }
    var crf_token = $('[name="csrfmiddlewaretoken"]').attr('value');


//    document.getElementById("demo").innerHTML = JSON.stringify(obj);
    console.log('all form dataaaaaa ========= ', obj);
    console.log('all form data ========= ', JSON.stringify(obj));

//    var xhr = new XMLHttpRequest();
//    xhr.open('PUT', '/music/api/v1/albums/2/');
//    xhr.setRequestHeader('Content-Type', 'application/json');
//    xhr.onload = function() {
//        if (xhr.status === 200) {
//            var userInfo = JSON.parse(xhr.responseText);
//            console.log('response ===== ', userInfo);
//        }
//    };
//
//    xhr.send(JSON.stringify(obj));

    $.ajax({
            method: 'PATCH',
            url: '/music/api/v1/albums/2/',
            data: JSON.stringify(obj),
            headers:{"X-CSRFToken": crf_token},
            dataType: "json",
            contentType: "application/json; charset=utf-8",
            cache: false,
            processData: false,
            done: function (data) {

            },
            complete: function () {

            },
            success: function (data) {
                console.log('req response ====', data);

                notify("User added successfully", "success");
            },
            error: function (request, status, error) {
                // showError(request);
                notify(request.responseText, 'danger');
            }
        });


//    $.ajax({
//            method: 'POST',
//            url: '/music/api/v1/albums',
//            data: JSON.stringify(obj),
//            contentType: false,
//            cache: false,
//            processData: false,
//            done: function (data) {
//            alert("done!");
//
//            },
//            complete: function () {
//
//            },
//            success: function (data) {
//                console.log('req response ====', data);
//                notify("User added successfully", "success");
//                alert("succes !");
////                table.ajax.url(crud_api + '?imp_user=' + user_type).load();
//            },
//            error: function (request, status, error) {
//                // showError(request);
//                notify("User couldn't Added !", "danger");
//                alert("Failed !");
////                notify(request.responseText, 'danger');
//            }
//        });
//        alert("Hello World!");

}
