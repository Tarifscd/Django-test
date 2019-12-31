function init_update_office() {

    function notify(message, type) {
        $.notify({
            message: message
        }, {
            type: type,
            placement: {
                from: "bottom",
                align: "right"
            },
            offset: 60,
            delay: 5000,
            timer: 1000,
            animate: {
                enter: 'animated fadeInDown',
                exit: 'animated fadeOutUp'
            },
        });
    }


    function objectifyForm(formArray) {//serialize data function

        var returnArray = {};
        var users = [];

        for (var i = 0; i < formArray.length; i++) {

            if (formArray[i]['name'] === 'users') {
                users.push(formArray[i]['value'])
            } else {
                returnArray[formArray[i]['name']] = formArray[i]['value'];
            }
            // returnArray['users'] = users.toString();
        }
        return returnArray;
    }

    $('#update-office-form-reset-btn').click(function () {
        $("select[name='division']").val('').trigger('change.select2');
        $("select[name='region']").val('').trigger('change.select2');
        $("select[name='district']").val('').trigger('change.select2');
        $("select[name='upazila']").val('').trigger('change.select2');
        $("select[name='organization']").val('').trigger('change.select2');
        $("select[name='office_category']").val('').trigger('change.select2');
    });

    $('.select2').select2();
    $('#user_profile').addClass("active");


    $('#update-office-form').parsley().on('form:submit', function () {
        var x = $('#update-office-form').serializeArray();
        var jsonData = objectifyForm(x);

        if (jsonData['latt'] === "" || jsonData['long'] === "") {
            delete jsonData['latt'];
            delete jsonData['long'];
        }

        console.log('off upd data === ', jsonData);

        $.ajax({
            method: 'PATCH',
            url: '/lged/api/v1/office/' + id + '/',
            data: JSON.stringify(jsonData),
            dataType: "json",
            contentType: "application/json; charset=utf-8",
            done: function (data) {
            },
            complete: function () {
            },
            success: function (data) {
                notify("Office updated successfully!","success");
                setTimeout(function () {
                    window.location = '/office/list/';
                }, 300);
            },
            error: function (request, status, error) {
                notify(request.responseText, 'danger')
            }
        });
        return false; // Don't submit form for this demo
    });

    function change_region(type, office = {}) {
        var division_id = $("select[name='division']").val();
        if (division_id == "") return false;

        $.ajax({
            method: 'GET',
            url: '/lged/api/v1/region/?id=' + division_id,
            data: "",
            dataType: "json",
            contentType: "application/json; charset=utf-8",
            done: function (data) {
            },
            complete: function () {
            },
            success: function (data) {
                var select = $("select[name='region']");

                if (select.prop) {
                    var options = select.prop('options');
                }
                else {
                    var options = select.attr('options');
                }
                $('option', select).remove();

                options[options.length] = new Option("-Select Option-", "");

                $.each(data, function (index, value) {
                    options[options.length] = new Option(value['name'], value['id']);
                });
                if (type === "first_time") {
                    $("select[name='region']").val(office['region']).trigger('change.select2');
                    change_district("first_time", office);
                }
            }
        });
    }

    $("select[name='division']").change(function () {
        change_region("on_change");

    });

    function change_district(type, office = {}) {

        var region_id = $("select[name='region']").val();
        if (region_id == "") return false;

        $.ajax({
            method: 'GET',
            url: '/lged/api/v1/district/?id=' + region_id,
            data: "",
            dataType: "json",
            contentType: "application/json; charset=utf-8",
            done: function (data) {
            },
            complete: function () {
            },
            success: function (data) {
                var select = $("select[name='district']");

                if (select.prop) {
                    var options = select.prop('options');
                }
                else {
                    var options = select.attr('options');
                }
                $('option', select).remove();

                options[options.length] = new Option("-Select Option-", "");

                $.each(data, function (index, value) {
                    options[options.length] = new Option(value['name'], value['id']);
                });
                if (type === "first_time") {
                    $("select[name='district']").val(office['district']).trigger('change.select2');
                    change_upazila("first_time", office);
                }
            }
        });
    }

    $("select[name='region']").change(function () {
        change_district("on_change")
    });

    function change_upazila(type, office = {}) {
        var district_id = $("select[name='district']").val();
        if (district_id == "") return false;

        $.ajax({
            method: 'GET',
            url: '/lged/api/v1/upazila/?id=' + district_id,
            data: "",
            dataType: "json",
            contentType: "application/json; charset=utf-8",
            done: function (data) {
            },
            complete: function () {
            },
            success: function (data) {
                var select = $("select[name='upazila']");

                if (select.prop) {
                    var options = select.prop('options');
                }
                else {
                    var options = select.attr('options');
                }
                $('option', select).remove();

                options[options.length] = new Option("-Select Option-", "");

                $.each(data, function (index, value) {
                    options[options.length] = new Option(value['name'], value['id']);
                });
                if (type === "first_time") {
                    $("select[name='upazila']").val(office['upazila']).trigger('change.select2');
                }
            }
        });
    }

    $("select[name='district']").change(function () {
        change_upazila('on_change');

    });

    function change_office_category(type, office_category = "") {
        var organization_id = $("select[name='organization']").val();
        if (organization_id === "") return false;
        changeOrganization(organization_id);
        if (type === "first_time") {
            $("select[name='office_category']").val(office_category).trigger('change.select2');

            var office_category = $("select[name='office_category']").val();
            if (office_category === "PAURASHAVA OFFICES") $('#pourashava_class').css('display', 'block');
            else $('#pourashava_class').css('display', 'none');
        }
    }

    $("select[name='organization']").change(function () {
        change_office_category("on_change");
    });

    $("select[name='office_category']").change(function () {
        var office_category = $(this).val();
        if (office_category === "PAURASHAVA OFFICES") $('#pourashava_class').css('display', 'block');
        else $('#pourashava_class').css('display', 'none');
    });

    $.ajax({
        method: 'GET',
        url: '/lged/api/v1/division/',
        data: "",
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        done: function (data) {
        },
        complete: function () {
        },
        success: function (data) {
            var select = $("select[name='division']");

            if (select.prop) {
                var options = select.prop('options');
            }
            else {
                var options = select.attr('options');
            }
            $('option', select).remove();

            options[options.length] = new Option("-Select Option-", "");

            $.each(data, function (index, value) {
                options[options.length] = new Option(value['name'], value['id']);
            });

        }
    });

    // function select_office_users() {
    //     $.ajax({
    //         method: 'GET',
    //         url: '/lged/api/v1/users/?office=' + id,
    //         data: "",
    //         dataType: "json",
    //         contentType: "application/json; charset=utf-8",
    //         done: function (data) {
    //         },
    //         complete: function () {
    //         },
    //         success: function (data) {
    //             console.log("users " + data);
    //
    //             var email_arr = [];
    //             $.each(data, function (index, value) {
    //                 email_arr.push(value['email'])
    //             });
    //             console.log(email_arr);
    //             $("select[name='users']").val(email_arr).trigger('change.select2');
    //
    //         }
    //     });
    // }
    //
    // $.ajax({
    //     method: 'GET',
    //     url: '/lged/api/v1/users/',
    //     data: "",
    //     dataType: "json",
    //     contentType: "application/json; charset=utf-8",
    //     done: function (data) {
    //     },
    //     complete: function () {
    //     },
    //     success: function (data) {
    //         console.log(data);
    //         var select = $("select[name='users']");
    //
    //         if (select.prop) {
    //             var options = select.prop('options');
    //         }
    //         else {
    //             var options = select.attr('options');
    //         }
    //         $('option', select).remove();
    //
    //         $.each(data, function (index, value) {
    //             var user = value['first_name'] + ' | ' + value['email'];
    //             options[options.length] = new Option(user, value['email']);
    //         });
    //
    //         select_office_users();
    //     }
    // });
    console.log('id ======= ', id);

    $.ajax({
        method: 'GET',
        url: '/lged/api/v1/office/' + id,
        data: "",
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        done: function (data) {
        },
        complete: function () {
        },
        success: function (data) {
            $("select[name='division']").val(data['division']).trigger('change.select2');
            change_region("first_time", data);
            $('input[name="name"]').val(data['name']);
            $('input[name="post_code"]').val(data['post_code']);
            $('input[name="phone_no"]').val(data['phone_no']);
            $('input[name="fax_no"]').val(data['fax_no']);
            $('input[name="website_link"]').val(data['website_link']);
            $('input[name="email"]').val(data['email']);
            $('textarea[name="address"]').val(data['address']);
            $('input[name="latt"]').val(data['latt']);
            $('input[name="long"]').val(data['long']);
            $("select[name='organization']").val(data['organization']).trigger('change.select2');
            $("select[name='pourashava_class']").val(data['pourashava_class']).trigger('change.select2');
            change_office_category("first_time", data['office_category']);
            changeCityCorporation(data['city_corporation']);

        }
    });

}