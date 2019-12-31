function init_base(all_training_list_url, user_email, user_id){
// ----------------------------------------------------------------------------------------------------------
// -------------------------------------- Initialization of the field ---------------------------------------
// ----------------------------------------------------------------------------------------------------------
    $('#local-history').on('click',function () {
        console.log(all_training_list_url);
        window.location = '/lged/training/list/' + user_id;
    });
    $('#change-pass-btn').on('click', function () {
        $('.change-password-modal').modal('toggle');
    });

// ----------------------------------------------------------------------------------------------------------
// ------------------------------------------- Initial Ajax call  -------------------------------------------
// ----------------------------------------------------------------------------------------------------------


// ----------------------------------------------------------------------------------------------------------
// ----------------------------------------------- Form Submit ----------------------------------------------
// ----------------------------------------------------------------------------------------------------------
    $('#change-password-form').parsley().on('form:submit', function () {
        let x = $('#change-password-form').serializeArray();
        let jsonData = objectifyForm(x);
        jsonData['email'] = user_email;
        let jsonCallBack = callAjax('/lged/api/v1/simple/change/password/', 'POST', jsonData);
        jsonCallBack.done(function (data) {
            if (data === "OK"){
                notify('Password updated successfully', 'success');
                let temp = {'id': user_id};
                callAjax('/lged/api/v1/change/stage/', 'POST', temp);
                setTimeout(function () {
                    window.location = '/';
                }, 300);
            } else if (data === "NO"){
                notify('Old password is not correct!', 'danger');
            }
            //Tarif_Update
            else if (data === "Same"){
                notify('It seems new Password is same as old password ! Try again and set a different password', 'danger');
            }
            //**
        });
        jsonCallBack.fail(function (request) {
            showError(request);
        });
        return false; // Don't submit form for this demo
    });

// ----------------------------------------------------------------------------------------------------------
//------------------------------------- Drop down change and ajax call --------------------------------------
// ----------------------------------------------------------------------------------------------------------


}


// ----------------------------------------------------------------------------------------------------------
// ------------------------------------- Required functions definition --------------------------------------
// ----------------------------------------------------------------------------------------------------------
