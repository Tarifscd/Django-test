function init_external_member_inclusion_history() {

    $('#settings').addClass("active");
    $('#settings').addClass("menu-open");
    $('#external-member-inclusion-tree-view').addClass("active");
    $('.select').select2();
    $('#generate-link-btn').on('click', function () {
        $('#generate-link-modal').modal('toggle');
    });
    $('select[name="case"]').on('change', function () {
        let val = $(this).val();
        if (val === '4') {
            $('#user_id_div').css('display', 'block');
            $('#user_nid_for_case4').css('display', 'block');
        }
        else {
            $('#user_id_div').css('display', 'none');
            $('#user_nid_for_case4').css('display', 'none');
        }
    });
    $('select[name="case"]').on('change', function () {
        let val = $(this).val();
        if (val === '2') {
            $('#organization_custom').css('display', 'block');
            $('#office_category_custom').css('display', 'block');
            $('#office_name_custom').css('display', 'block');
        }
        else if (val ==='3') {
            $('#organization_custom').css('display', 'block');
            $('#office_category_custom').css('display', 'block');
            $('#office_name_custom').css('display', 'block');
        }
        else {
            $('#organization_custom').css('display', 'none');
            $('#office_category_custom').css('display', 'none');
            $('#office_name_custom').css('display', 'none');
        }
    });



    // $("select[id='organization_div']").on('change', function () {
    //     $(".office-category-holder").css('display', 'block');
    if($("select[id='organization_div']").val()){
        let organization = $("select[id='organization_div']").val();
        // changeOrganization(organization,'office_category_div');
    }


    // $("select[id='organization_div'], select[id='office_category_div']").change(function () {
    $("select[id='office_category_div']").change(function () {
        $("select[name='office_name']").val('').trigger('change.select2');
        let organization = $("select[id='organization_div']").val();
        let office_category = $("select[id='office_category_div']").val();
        // console.log('office_category =========== ', office_category);
        let params = "";
        if (organization !== "") params = "organization=" + organization + '&';
        if (office_category !== "") params += "office_category=" + office_category + '&';
        commonSetDropDown('/lged/api/v1/office/?' + params+ 'fields=id,name&', 'office_name', 'name', 'id');
    });








    $('#generate-link-form').parsley().on('form:submit', function () {
        var x = $('#generate-link-form').serializeArray();
        let jsonData = commonObjectifyForm(x);
        console.log('json data === ', jsonData);
        jsonData['link'] = window.location.origin + "/lged/external-member-link/" + jsonData['case'] + '/';
        if (jsonData['case'] === '4') jsonData['link'] += '?id=' + jsonData['id'];
        else delete jsonData['id'];
        delete jsonData['user_nid'];
        // console.log('office_name =========== ', jsonData['office_name'])
        // console.log('organization_name =========== ', jsonData['organization_div'])
        // console.log('off_cat_name =========== ', jsonData['office_category_div'])
        if (jsonData['case'] === '2') jsonData['link'] += '?off=' + jsonData['office_name'];
        else if (jsonData['case'] === '3') jsonData['link'] += '?off=' + jsonData['office_name'];
        else delete jsonData['office_name'];
        delete jsonData['office_category_div'];
        delete jsonData['case'];
        console.log('json === ', jsonData);
        $.ajax({
            method: 'POST',
            url: '/lged/api/v1/expired-link/',
            data: JSON.stringify(jsonData),
            contentType: 'application/json',
            success: function (data) {
                $('#generate-link-modal').modal('toggle');
                $('#generate-link-form')[0].reset();
                prompt("Copy to clipboard: Ctrl+C, Enter", data['link']);
            },
            error: function (request, status, error) {
                showError(request);
            }
        });
        return false;
    });
    let table1 = set_case123_table('/lged/api/v1/ext-member-inclusion-history/');
    let table2 = set_case4_table('/lged/api/v1/ext-member-transfer-history/');
    $(document).on('click', '.govt-user-link, .admin-user-link', function (e) {
        // your function here
        let id = this.id;
        $('#user-detail-modal').modal('toggle');
        let jsonCallback = callAjax('/lged/api/v1/ext-member-inclusion-history/' + id, 'GET', '');
        jsonCallback.done(function (data) {
            let str;
            if ($(e.target).attr('class') === 'admin-user-link') str = 'admin_users';
            else str = 'govt_users';
            if (data[str].length === 0) $('#user-detail-table').html("No Data Found");
            else $('#user-detail-table').html("");
            $.each(data[str], function (k, v) {
                let string = "<tr><td>" + v['designation_name'] + "</td>" +
                        "<td>" + v['procurement_roles_list'] + "</td></tr>";
                $('#user-detail-table').append(string);
            });
        });
    });

    var table_ext = $('#external-member-inclusion-table').DataTable();
    var row_data = [];

    $('#external-member-inclusion-table').on( 'click', 'tbody tr', function () {
    $(".row-selected").removeClass("row-selected");
    $(".disabled").removeClass("disabled");
    row_data = table_ext.row(this).data();
    var id_selector = "#" + row_data ['id'];
    $(id_selector).addClass("row-selected");
    // console.log('table_ext_m11 === ' +row_data['first_name']);
    } );

    $('#user-add-btn').on('click', function () {
        let id = $(".row-selected")[0].id || 1;
        // let row_data = $(".row-selected")[0];
        console.log('row_dataaaaa === ', row_data);
        if (row_data['approved_status'] ===1) {
            notify('This user already has been added. You can\'t add this user again', 'danger');
            return;
        }
        else {
            add_new_office(row_data);
            // add_approval_status(row_data['id']);
        }
    });

    var table_ext_transfer = $('#external-member-inclusion-table-case-4').DataTable();
    var row_data_transfer = [];

    $('#external-member-inclusion-table-case-4').on( 'click', 'tbody tr', function () {
    $(".row-selected").removeClass("row-selected");
    $(".disabled").removeClass("disabled");
    row_data_transfer = table_ext_transfer.row(this).data();
    var id_selector = "#" + row_data_transfer ['id'];
    $(id_selector).addClass("row-selected");
    // console.log('table_ext_m11 === ' +row_data['first_name']);
    } );

    $('#transfer-btn').on('click', function () {
        let id = $(".row-selected")[0].id || 1;
        // let row_data = $(".row-selected")[0];
        console.log('row_dataaaaa === ', row_data_transfer);
        if (row_data_transfer['approved_status'] ===1) {
            notify('This user already has been Transfered. You can\'t transfer this user again', 'danger');
            return;
        }
        else {
        ext_transfer_user(row_data_transfer);
        //     // add_approval_status(row_data['id']);
        }
    });

    $('#new-user-update-btn').on('click', function () {
        let id = $(".row-selected")[0].id || 1;
        // let row_data = $(".row-selected")[0];
        // console.log('table_ext_m22 === ', row_data);
        if (row_data['approved_status'] ===1) {
            notify('This user can\'t be updated !', 'danger');
            return;
        }
        else {
            new_user_update_btn_click(row_data, row_data['case']);
        }


    });

    $('#transfer-update-btn').on('click', function () {
        let id = $(".row-selected")[0].id || 1;
        // let row_data = $(".row-selected")[0];
        // console.log('table_ext_m22 === ', row_data);
        if (row_data_transfer['approved_status'] ===1) {
            notify('This transfer history can\'t be updated !', 'danger');
            return;
        }
        else {
            ext_transfer_update_btn_click(row_data_transfer);
        }


    });

    $('input[type=radio]').change(function () {
        if (this.id === 'yes') {
            $('#ppr_training_add').css('display', 'block');
            $('#start_date_add_div').addClass('required_field');
            $('#start_date_add_div').find('input').attr('data-parsley-required', true);
            $('#venue_add_div').addClass('required_field');
            $('#venue_add_div').find('input').attr('data-parsley-required', true);
        } else if (this.id === 'no') {
            $('#ppr_training_add').css('display', 'none');
            $('#start_date_add_div').removeClass('required_field');
            $('#start_date_add_div').find('input').attr('data-parsley-required', false);
            $('#venue_add_div').removeClass('required_field');
            $('#venue_add_div').find('input').attr('data-parsley-required', false);
        }
    });

    $('input[name="user_nid"]').on('change', function () {
        let user_nid = $('input[name="user_nid"]').val();
        let jsonCallBack = callAjax('/lged/api/v1/users/?nid='+user_nid+'&', 'GET', "");
        jsonCallBack.done(function (data){
            $('input[name="id"]').val(data[0]['id']);
        });
    });

    // $('#new-update-profile-form').parsley().on('click', '.new_user_update', function () {
    $(document).on('click', '.new_user_update', function () {
        // e.preventDefault();

        // console.log('Update submitted !');
        let id;
        if ($(".row-selected")[0]) id = $(".row-selected")[0].id || 1;
        // console.log('id ========== ', id);


        var retVal = confirm('Are you sure?');
        if (retVal === false) {
            return false;
        }


        let profile_update_parsley = $("#new-update-profile-form").parsley();
        profile_update_parsley.validate();
        if (profile_update_parsley.isValid()) {
            var x = $("#new-update-profile-form").serializeArray();
            console.log('all_data x =========', x);

            var formData = objectifyFormData(x);

            // console.log('office_catttttttt ==== ', formData.get('office_category'));


            formData.append('organization', 'LGED');

            let admin_users = {}, govt_users = {};

            var j = 0;
            var no_of_govt_des = 0;
            for (j = 0; ; j++) {
                if (!(formData.get('govt_designation' + (j + 1)))) {
                    break;
                }
            }
            no_of_govt_des = j;
            // console.log('no_of_govt_des ==== ', no_of_govt_des);
            let no_of_govt_users = 0;
            for (var i = 0; i < no_of_govt_des; i++) {
                let no_of_specific_def = parseInt(formData.get('gov_user_number' + (i + 1)));
                formData.delete('gov_user_number' + (i + 1));

                for (var k = 0; k < no_of_specific_def; k++) {

                    let key = 'govt_user' + (no_of_govt_users + 1);
                    no_of_govt_users++;
                    govt_users[key] = {};
                    govt_users[key]["designation"] = parseInt(formData.get('govt_designation' + (i + 1)));
                    let roles = [6, 7];
                    govt_users[key]["procurement_roles"] = roles;
                }
                formData.delete('govt_designation' + (i + 1));
            }
            formData.append('govt_users', JSON.stringify(govt_users));


            // console.log('procurement_roles_giribiltiiiiiiii =======', formData.get('procurement_roles'))

            if (formData.get('procurement_roles') === 'val') {
                formData.delete('procurement_roles');
                formData.append('procurement_roles', '100');
                formData.append('procurement_roles', '6');
                formData.append('procurement_roles', '7');

            } else if (formData.get('procurement_roles') === 'val2') {
                formData.delete('procurement_roles');
                formData.append('procurement_roles', '6');
                formData.append('procurement_roles', '7');

            } else if (formData.get('procurement_roles') === 'no_vals') {
                formData.delete('procurement_roles');
                // formData.append('procurement_roles', null);

            }
            // console.log('procurement_roles ==== ', formData.get('procurement_roles'));
            // console.log('venue ==== ', formData.get('venue'));


            if (formData.get('start_date')) formData.set('start_date', moment(formData.get('start_date'), "MM-DD-YYYY").format('YYYY-MM-DD'));
            if (formData.get('date_of_birth')) formData.set('date_of_birth', moment(formData.get('date_of_birth'), "MM-DD-YYYY").format('YYYY-MM-DD'));

            if((formData.get('PPR_training') === 'False')){
                formData.set('start_date', '');
                formData.set('venue', '');
            }
            // console.log('start_date ==== ', formData.get('start_date'));
            // console.log('venue ==== ', formData.get('venue'));


            formData.append('url', window.location.href);
            // console.log('govt_users ==== ', formData.get('govt_users'));
            //
            // console.log('formData ==== ', formData);


            $.ajax({
                method: 'PATCH',
                url: '/lged/api/v1/ext-member-inclusion-history/'+id+'/',
                data: formData,
                contentType: false,
                cache: false,
                processData: false,
                success: function (data) {
                    // $('.select2').val('').trigger('change.select2');
                    // $('#new-update-profile-form')[0].reset();
                    notify("Data Updated successfully", "success");
                    // $('#new-update-profile-form button[type="submit"]').prop('disabled', true);
                    $('#new-user-update-modal').modal('toggle');
                    table1.ajax.url('/lged/api/v1/ext-member-inclusion-history/').load();
                },
                error: function (request, status, error) {
                    showError(request);
                }
            });

            return false;
        }
        return false;
    });

    $(document).on('click', '.ext_transfer_update', function () {
        console.log('ext transfer table id ========== ');
        let id;
        if ($(".row-selected")[0]) id = $(".row-selected")[0].id || 1;
        console.log('id ========== ', id);

        var retVal = confirm('Are you sure?');
        if (retVal === false) {
            return false;
        }

        var x = $('#ext-transfer-update-form').serializeArray();
        console.log('x ========= ', x);
        var formData = objectifyFormData(x);
        console.log('formData ========= ', formData);

        var transferInput = document.getElementById('transfer-order');
        if (transferInput.files.length !== 0) {
            var transfer = transferInput.files[0];
            if (transfer) {
                let size = transfer.size / (1000 * 1000);
                if (size > 2) {
                    notify("Size should be less than 2MB", "danger");
                    return false;
                }
                formData.set('transfer_order', transfer);
            }
        }
        if (formData.get('charge_handover_date') !== '') {
            formData.set('charge_handover_date', moment(formData.get('charge_handover_date'), "MM-DD-YYYY").format('YYYY-MM-DD'));
        } else formData.delete('charge_handover_date');
        // formData.delete('office_category');
        formData.delete('state');
        console.log('form data org =========== ', formData.get('organization'));
        console.log('form data ofc =========== ', formData.get('office_category'));
        console.log('status =========== ', formData.get('status'));
        console.log('form data ofc =========== ', formData.get('office_category'));
        console.log('transferred_office =========== ', formData.get('transferred_office'));
        console.log('new_designation =========== ', formData.get('new_designation'));
        console.log('transfer_memo_no =========== ', formData.get('transfer_memo_no'));
        console.log('state =========== ', formData.get('state'));
        console.log('charge_handover_date =========== ', formData.get('charge_handover_date'));

        $.ajax({
            method: 'PATCH',
            url: '/lged/api/v1/ext-member-transfer-history/'+id+'/',
            data: formData,
            contentType: false,
            cache: false,
            processData: false,
            success: function (data) {
                notify("Data Updated successfully", "success");
                $('#ext-transfer-update-form').modal('toggle');
                location.reload();
                // table1.ajax.url('/lged/api/v1/ext-member-inclusion-history/').load();
                // table1.ajax.url('/lged/api/v1/ext-member-transfer-history/').load();
            },
            error: function (request, status, error) {
                showError(request);
            }
        });


        return false;
    });


    $('option[value="from"]', $('#transfer_type')).remove();
    $('option[value="from"]', $('#promotion_type')).remove();
    $('select[name="status"]').on('change', function () {
        if ($(this).val() === '0') {
            $('#transfer_type_div').css('display', 'none');
            $('#promotion_type_div').css('display', 'block');
            // show_();
        } else {
            $('#transfer_type_div').css('display', 'block');
            $('#promotion_type_div').css('display', 'none');
            // hide_();
        }
    });

}

function add_new_office(userdata) {

    // console.log('user data ==== ', userdata);
    var new_office_data = {};
    // console.log('new off data111 ==== ', new_office_data);
    new_office_data.division = '4';
    console.log('off cat form ======== ', userdata['organization']);
    // console.log('off cat div ========== ', userdata['office_category_div']);
    if (userdata['organization'] !== '') {
        var organization = userdata['organization'];
        new_office_data.organization = organization;
    }
    else {
        new_office_data.organization = "LGED";
    }
    console.log('off cat ======== ', new_office_data.organization);
    var office_category = userdata['office_category'];
    new_office_data.office_category = office_category;
    var office_name = userdata['office_name'];
    new_office_data.name = office_name;
    new_office_data.users = '';
    // console.log('new off data222 ==== ', new_office_data);
    // add_new_user(userdata, 101);

    $.ajax({
            method: 'POST',
            url: '/lged/api/v1/office/',
            data: JSON.stringify(new_office_data),
            dataType: "json",
            contentType: "application/json; charset=utf-8",
            done: function (data) {
            },
            complete: function () {
            },
            success: function (data) {
                console.log('post responseeeeee ========= ', data['id']);
                var office_id = data['id'];

                add_new_user(userdata, office_id);
                notify('Office added successfully', 'success');
            },
            error: function (request, status, error) {
                // showError(request);
                notify(request.responseJSON.user[0], 'danger');
                var office_id = request.responseJSON.office;
                console.log('request === ==  ',office_id);
                add_new_user(userdata, office_id);

            }
        });
        return false;
}

function add_new_user(useralldata, office_id) {
    // console.log('user All Data = = = = = ', useralldata);
    // console.log('new office id = = = = = ', office_id);
    var userdataarr = [];

    var nomineedata = {};

    if(useralldata['focal_designation'] !== '' && useralldata['user_id_for_pro_info'] !== '') {
        var userdata = {};
        userdata.PPR_training = '';
        userdata.bangla_name = '';
        userdata.date_of_birth = null;
        userdata.designation = useralldata['focal_designation'];
        userdata.e_gp_user_id_for_govt = '';
        userdata.e_gp_user_id_for_pe_admin = '';
        userdata.first_name = '';
        userdata.nid_value = null;
        userdata.office = office_id;
        userdata.official_email = null;
        userdata.official_mobile_no = '';
        userdata.mobile_no = '';
        userdata.personal_email = null;
        userdata.procurement_role = '4';

        console.log('procurement_roles foczzz ====', userdata.procurement_role);
        userdata.procurement_role_lgis = '';
        userdata.start_date = null;
        userdata.email = useralldata['user_id_for_pro_info'];
        userdata.venue = null;
        userdata.description = '';
        // console.log('focal user data', userdata);
        // console.log("habijabi habijabi !")
        userdataarr.push(userdata);

        if(useralldata['focal_designation'] !== useralldata['designation']) {
            var admin_like_foc_data = {};
            admin_like_foc_data.PPR_training = '';
            admin_like_foc_data.bangla_name = '';
            admin_like_foc_data.date_of_birth = null;
            admin_like_foc_data.designation = useralldata['focal_designation'];
            admin_like_foc_data.e_gp_user_id_for_govt = '';
            admin_like_foc_data.e_gp_user_id_for_pe_admin = '';
            admin_like_foc_data.first_name = '';
            admin_like_foc_data.nid_value = null;
            admin_like_foc_data.office = office_id;
            admin_like_foc_data.official_email = null;
            admin_like_foc_data.official_mobile_no = '';
            admin_like_foc_data.mobile_no = '';
            admin_like_foc_data.personal_email = null;
            admin_like_foc_data.procurement_role = '3,6,7,100';
            admin_like_foc_data.procurement_role_lgis = '';
            admin_like_foc_data.start_date = null;
            admin_like_foc_data.email = null;
            admin_like_foc_data.venue = null;
            admin_like_foc_data.description = '';

            userdataarr.push(admin_like_foc_data);
        }

    }

    // var i;
    // for (i = 0; i < useralldata['admin_users'].length; i++) {
    //     var adminuserdata = {};
    //     adminuserdata.PPR_training = '';
    //     adminuserdata.bangla_name = '';
    //     adminuserdata.date_of_birth = null;
    //     adminuserdata.designation = useralldata['admin_users'][i]['designation'];
    //     adminuserdata.e_gp_user_id_for_govt = '';
    //     adminuserdata.e_gp_user_id_for_pe_admin = '';
    //     adminuserdata.first_name = '';
    //     adminuserdata.nid_value = null;
    //     adminuserdata.office = office_id;
    //     adminuserdata.official_email = null;
    //     adminuserdata.official_mobile_no = '';
    //     adminuserdata.mobile_no = '';
    //     adminuserdata.personal_email = null;
    //     adminuserdata.procurement_role = useralldata['admin_users'][i]['procurement_roles'].toString();
    //     adminuserdata.procurement_role_lgis = '';
    //     adminuserdata.start_date = null;
    //     adminuserdata.email = null;
    //     adminuserdata.venue = null;
    //     adminuserdata.description = '';
    //
    //     // console.log('xx ====  ',useralldata['admin_users'][i]['designation'], '   ', useralldata['admin_users'][i]['procurement_roles']);
    //     // console.log('user from xx === ', adminuserdata.designation,'  ', adminuserdata.procurement_role);
    //     userdataarr.push(adminuserdata);
    // }


    var x;
    for (x of useralldata['govt_users']){
        var govtuserdata = {};
        govtuserdata.PPR_training = '';
        govtuserdata.bangla_name = '';
        govtuserdata.date_of_birth = null;
        govtuserdata.designation = x['designation'];
        govtuserdata.e_gp_user_id_for_govt = '';
        govtuserdata.e_gp_user_id_for_pe_admin = '';
        govtuserdata.first_name = '';
        govtuserdata.nid_value = null;
        govtuserdata.office = office_id;
        govtuserdata.official_email = null;
        govtuserdata.official_mobile_no = '';
        govtuserdata.mobile_no = '';
        govtuserdata.personal_email = null;
        govtuserdata.procurement_role = x['procurement_roles'].toString();
        govtuserdata.procurement_role_lgis = '';
        govtuserdata.start_date = null;
        govtuserdata.email = null;
        govtuserdata.venue = null;
        govtuserdata.description = '';


        // console.log('procurement_roles prev ====', x['procurement_roles']);
        // console.log('procurement_roles toString ====', govtuserdata.procurement_role);

        // console.log('yy ====  ',x['designation'], '   ', x['procurement_roles']);
        // console.log('user from yy === ', govtuserdata.designation, '  ', govtuserdata.procurement_role);
        userdataarr.push(govtuserdata);
    }


    if (useralldata['PPR_training'] === true){
        nomineedata.PPR_training = 'True';
    }

    if (useralldata['PPR_training'] === false){
        nomineedata.PPR_training = 'False';
    }
    // nomineedata.PPR_training = '';
    nomineedata.bangla_name = useralldata['bangla_name'];
    nomineedata.date_of_birth = useralldata['date_of_birth'];
    nomineedata.designation = useralldata['designation'];
    nomineedata.e_gp_user_id_for_govt = useralldata['e_gp_user_id_for_govt'];
    nomineedata.e_gp_user_id_for_pe_admin = useralldata['e_gp_user_id_for_pe_admin'];
    nomineedata.first_name = useralldata['first_name'];
    nomineedata.nid_value = useralldata['nid'];
    nomineedata.office = office_id;
    nomineedata.official_email = useralldata['official_email'];
    nomineedata.official_mobile_no = '';
    nomineedata.mobile_no = useralldata['personal_mobile_no'];
    nomineedata.personal_email = '';
    if(useralldata['focal_designation'] === useralldata['designation']){
        let proc_roll = useralldata['procurement_roles'];
        if((proc_roll.toString()) === '') {
            console.log('procurement_rolesss ============ ', proc_roll.toString());
            proc_roll.push(3);
            proc_roll.push(6);
            proc_roll.push(7);
            proc_roll.push(100);
            console.log('procurement_rolesss2 ============ ', proc_roll.toString());
        }
        else {
            proc_roll.push(3);
            console.log('procurement_rolesss333 ============ ', proc_roll.toString());
        }
        nomineedata.procurement_role = proc_roll.toString();
    }
    else{
        nomineedata.procurement_role = useralldata['procurement_roles'].toString();
    }
    // let proc_roll = useralldata['procurement_roles'];
    // console.log('procurement_roles1 ============ ', proc_roll.toString());
    // proc_roll.push(3);
    // console.log('procurement_roles2 ============ ', proc_roll.toString());

    nomineedata.procurement_role_lgis = '';
    nomineedata.start_date = useralldata['start_date'];
    nomineedata.email = null;
    nomineedata.venue = useralldata['venue'];
    nomineedata.description = '';
    // console.log('nominee data', nomineedata);
    userdataarr.push(nomineedata);
    // console.log('aaaaalllll dataaaaa ==== ', JSON.stringify(userdataarr));

    var y;
    for (y of userdataarr) {
        console.log('data to post ==== ', y);

        $.ajax({
            method: 'POST',
            url: '/lged/api/v1/users/',
            data: JSON.stringify(y),
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

    }
    add_approval_status(useralldata['id']);


    return false;

}

function add_approval_status(id) {
    var editData = {};
    editData['approved_status'] = 1;
    $.ajax({
        method: 'PATCH',
        url: '/lged/api/v1/ext-member-inclusion-history/'+id+'/',
        data: JSON.stringify(editData),
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        cache: false,
        processData: false,
        success: function (data) {
            notify("All users has been added successfully", "success");

            // table1.ajax.url('/lged/api/v1/ext-member-inclusion-history/').load();
            location.reload();

        },
        error: function (request, status, error) {
            showError(request);
        }
    });

}

function new_user_update_btn_click(userdata, case123) {
    console.log('updating new user data', userdata);
    $('#new-user-update-modal').modal('toggle');
    console.log('case ===== ', case123);

    if (case123 === 1 || case123 === 2) {
        $('#office_name').addClass('required_field');
        $('#office_name').find('input').attr('data-parsley-required', true);
        $('#office_category').addClass('required_field');
        $('#office_category').find('input').attr('data-parsley-required', true);
        $('#focal_info_update').addClass('required_field');
        $('#focal_info_update').find('input').attr('data-parsley-required', true);
    }
    else if (case123 === 3) {
        $('#focal_info_update').css('display', 'none');
        $('#govt_info_update').css('display', 'none');
    }

    if (userdata['office_category'] === 'Additional Chief Engineer Office (HQ)') {
        $('input[id="aceo"]').attr('checked', true);
        // $('input[id="aceo"]').prop('checked', 'checked');
    }
    else if (userdata['office_category'] === 'Project Office (HQ)') {
        $('input[id="po"]').attr('checked', true);
    }
    else if (userdata['office_category'] === 'SE Office (HQ)') {
        $('input[id="seo"]').attr('checked', true);
    }
    else if (userdata['office_category'] === 'Unit (HQ)') {
        $('input[id="unit"]').attr('checked', true);
    }
    else {
        $("input[name='office_category']:checked").attr('checked', false);
    }

    $('input[name="office_name"]').val(userdata['office_name']);
    $('input[name="first_name"]').val(userdata['first_name']);

    if (userdata['designation'] === 7) {
        $('input[id="se"]').attr('checked', true);
    }
    else if (userdata['designation'] === 8) {
        $('input[id="xen"]').attr('checked', true);
    }
    else if (userdata['designation'] === 10) {
        $('input[id="sae"]').attr('checked', true);
    }
    else if (userdata['designation'] === 11) {
        $('input[id="ae"]').attr('checked', true);
    }
    else if (userdata['designation'] === 201) {
        $('input[id="pd"]').attr('checked', true);
    }
    else if (userdata['designation'] === 202) {
        $('input[id="dpd"]').attr('checked', true);
    }
    else {
        $("input[name='designation']:checked").attr('checked', false);
    }

    $('input[name="nid"]').val(userdata['nid']);
    $('input[name="personal_mobile_no"]').val(userdata['personal_mobile_no']);
    $('input[name="official_email"]').val(userdata['official_email']);

    if (userdata['date_of_birth'] === null || userdata['date_of_birth'] === '') {
                $('#date_of_birth_add').val('');
    }
    else {
                $("#date_of_birth_add").datepicker('update', new Date(userdata['date_of_birth']));
    }
    if (userdata['procurement_roles_list'] === "TOC, TEC, PE") {
        $('input[id="val"]').attr('checked', true);
    }
    else if (userdata['procurement_roles_list'] === "TOC, TEC") {
        $('input[id="val2"]').attr('checked', true);
    }
    else if (userdata['procurement_roles_list'] === "") {
        $('input[id="no_vals"]').attr('checked', true);
    }
    else {
        console.log('No proc roll !');
        console.log('procurement_roles_list ========= ', userdata['procurement_roles_list']);

        $("input[name='procurement_roles']:checked").attr('checked', false);
    }

    $('input[name="e_gp_user_id_for_govt"]').val(userdata['e_gp_user_id_for_govt']);

    if (userdata['PPR_training'] === true) {
        $('input[id="yes"]').attr('checked', true).trigger('change');
        $('input[id="yes"]').prop('checked', 'checked').trigger('change');

        $('input[name="start_date"]').val(userdata['start_date']).datepicker('update', new Date(userdata['start_date']));
        if (userdata['venue'] === 12) {
            $('input[id="venue_add1"]').attr('checked', true);
        }
        else if (userdata['venue'] === 13) {
            $('input[id="venue_add2"]').attr('checked', true);
        }

    }
    else if (userdata['PPR_training'] === false) {
        $('input[id="no"]').attr('checked', true).trigger('change');
        $('input[id="no"]').prop('checked', 'checked').trigger('change');
        $('input[name="start_date"]').val('').datepicker('update', new Date(userdata['start_date']));
        $("input[name='venue']:checked").attr('checked', false);
    }
    else {
        $('input[id="no"]').attr('checked', true);
        // $('input[id="yes_update"]').attr('checked', false).trigger('change');
        $('input[id="no_update"]').attr('checked', false);
        $('input[name="start_date"]').val('').datepicker('update', new Date(userdata['start_date']));
        $("input[name='venue']:checked").attr('checked', false);
        $('#venue_add1').val('');
        $('#venue_add2').val('');
    }

    if (userdata['focal_designation'] === 7) {
        $('input[id="f_se"]').attr('checked', true);
    }
    else if (userdata['focal_designation'] === 8) {
        $('input[id="f_xen"]').attr('checked', true);
    }
    else if (userdata['focal_designation'] === 201) {
        $('input[id="f_pd"]').attr('checked', true);
    }
    else {
        $("input[name='focal_designation']:checked").attr('checked', false);
    }

    $('input[name="user_id_for_pro_info"]').val(userdata['user_id_for_pro_info']);

    var x;
    var des_dpd = 0;
    var des_xen = 0;
    var des_sae = 0;
    var des_ae = 0;
    for (x of userdata['govt_users']){
        if(x['designation'] === 202){
            des_dpd = des_dpd + 1;
        }
        if(x['designation'] === 8){
            des_xen = des_xen + 1;
        }
        if(x['designation'] === 10){
            des_sae = des_sae + 1;
        }
        if(x['designation'] === 11){
            des_ae = des_ae + 1;
        }
    }
    // console.log('des_dpd ====== ', des_dpd);
    // console.log('des_xen ====== ', des_xen);
    // console.log('des_sae ====== ', des_sae);
    // console.log('des_ae ====== ', des_ae);

    $('input[name="gov_user_number1"]').val(des_dpd);
    $('input[name="gov_user_number2"]').val(des_xen);
    $('input[name="gov_user_number3"]').val(des_sae);
    $('input[name="gov_user_number4"]').val(des_ae);




    var gov_user_DPD = des_dpd;
    var gov_user_XEN = des_xen;
    var gov_user_SAE = des_sae;
    var gov_user_AE = des_ae;
    var gov_user_foc = $("input[name='focal_designation']:checked").val();
    var gov_user_Nom = $("input[name='designation']:checked").val();

    console.log('gov_user_DPD === ', gov_user_DPD);
    console.log('gov_user_XEN === ', gov_user_XEN);
    console.log('gov_user_SAE === ', gov_user_SAE);
    console.log('gov_user_AE === ', gov_user_AE);
    console.log('gov_user_foc === ', gov_user_foc);
    console.log('gov_user_Nom === ', gov_user_Nom);



    if(gov_user_foc === gov_user_Nom){
        if(gov_user_foc === undefined && gov_user_Nom === undefined){
            var total = gov_user_DPD + gov_user_XEN + gov_user_SAE + gov_user_AE;
        }
        else {
            var total = gov_user_DPD + gov_user_XEN + gov_user_SAE + gov_user_AE + 1;
        }

    }
    else if(gov_user_foc !== gov_user_Nom){
        if(gov_user_foc === undefined || gov_user_Nom === undefined){
            var total = gov_user_DPD + gov_user_XEN + gov_user_SAE + gov_user_AE + 1;
        }
        else if(gov_user_foc === undefined && gov_user_Nom === undefined){
            var total = gov_user_DPD + gov_user_XEN + gov_user_SAE + gov_user_AE;
        }
        else{
            var total = gov_user_DPD + gov_user_XEN + gov_user_SAE + gov_user_AE + 2;
        }

    }
    $("#total_gov_user").html(total);





    $("input[name='gov_user_number1'], input[name='gov_user_number2'], input[name='gov_user_number3'], input[name='gov_user_number4'], #nom_des, #foc_des").change(function () {

        var gov_user_DPD = $("input[name='gov_user_number1']").val();
        var gov_user_XEN = $("input[name='gov_user_number2']").val();
        var gov_user_SAE = $("input[name='gov_user_number3']").val();
        var gov_user_AE = $("input[name='gov_user_number4']").val();
        var gov_user_foc = $("input[name='focal_designation']:checked").val();
        var gov_user_Nom = $("input[name='designation']:checked").val();

        if(gov_user_DPD === ''){
            gov_user_DPD = 0;
        }
        if(gov_user_XEN === ''){
            gov_user_XEN = 0;
        }
        if(gov_user_SAE === ''){
            gov_user_SAE = 0;
        }
        if(gov_user_AE === ''){
            gov_user_AE = 0;
        }


        if(gov_user_foc === gov_user_Nom){
            if(gov_user_foc === undefined && gov_user_Nom === undefined){
                var total = parseInt(gov_user_DPD) + parseInt(gov_user_XEN) + parseInt(gov_user_SAE) + parseInt(gov_user_AE);
            }
            else {
                var total = parseInt(gov_user_DPD) + parseInt(gov_user_XEN) + parseInt(gov_user_SAE) + parseInt(gov_user_AE) + 1;
            }

        }
        else if(gov_user_foc !== gov_user_Nom){
            if(gov_user_foc === undefined || gov_user_Nom === undefined){
                var total = parseInt(gov_user_DPD) + parseInt(gov_user_XEN) + parseInt(gov_user_SAE) + parseInt(gov_user_AE) + 1;
            }
            else if(gov_user_foc === undefined && gov_user_Nom === undefined){
                var total = parseInt(gov_user_DPD) + parseInt(gov_user_XEN) + parseInt(gov_user_SAE) + parseInt(gov_user_AE);
            }
            else{
                var total = parseInt(gov_user_DPD) + parseInt(gov_user_XEN) + parseInt(gov_user_SAE) + parseInt(gov_user_AE) + 2;
            }

        }
        $("#total_gov_user").html(total);


    });
    $("#case_no").html(case123);

}

function ext_transfer_user(transferuseralldata){
    var transferuserdata = {};

    transferuserdata.transferred_db_table = transferuseralldata['id'];
    transferuserdata.transferred_office = transferuseralldata['transferred_office'];
    transferuserdata.transferred_office_name = transferuseralldata['transferred_office_name'];
    transferuserdata.new_designation = transferuseralldata['new_designation'];
    transferuserdata.new_designation_name = transferuseralldata['new_designation_name'];
    transferuserdata.nid = transferuseralldata['nid'];
    transferuserdata.user = transferuseralldata['user'];
    // transferuserdata.user_name = transferuseralldata['user_name'];

    console.log('transferuserdata ============= ', transferuserdata);


    $.ajax({
            method: 'POST',
            url: '/lged/api/v1/exttrasnferuser/',
            data: JSON.stringify(transferuserdata),
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

                notify("User transfered successfully", "success");
            },
            error: function (request, status, error) {
                // showError(request);
                notify(request.responseText, 'danger');
            }
        });


}

function ext_transfer_update_btn_click(transferdata) {
    console.log('updating ext transfer data ==== ', transferdata);
    $('#ext-transfer-update-modal').modal('toggle');
    var from = 0, flag = 0;

    $('select[name="status"]').val(transferdata['status']).trigger('change.select2');
    $('#transfer_type').val('to').trigger('change.select2');
    $('#promotion_type').val('to').trigger('change.select2');
    $('input[name="transfer_memo_no"]').val(transferdata['transfer_memo_no']);

    if(transferdata['charge_handover_date'] === null){
        transferdata['charge_handover_date'] = '';
    }
    $('input[id="charge_handover_date"]').datepicker('update', new Date(transferdata['charge_handover_date']));


    $('select[name="status"]').on('change', function () {
        if ($(this).val() === '0') {
            $('#transfer_type_div').css('display', 'none');
            $('#promotion_type_div').css('display', 'block');
            show_();
        } else {
            $('#transfer_type_div').css('display', 'block');
            $('#promotion_type_div').css('display', 'none');
            hide_();
        }
    });

    function change_office_category(type, office_category = "") {
        var organization_id = $("select[name='organization']").val();
        if (organization_id === "") return false;
        changeOrganization(organization_id);
        if (type === "first_time") {
            $("select[name='office_category']").val(office_category).trigger('change.select2');

        }
    }
    // $('select[name="office_category"]').val(transferdata['office_category']).trigger('change.select2');
    // console.log('transferdata[\'office_category\']', transferdata['office_category']);

    commonSetDropDown('/lged/api/v1/designation/', 'new_designation', 'designation', 'id');
    let id = transferdata['user'];
    // console.log('user id =========== ', id);
    commonSetDropDown('/lged/api/v1/office/?transfer=1&fields=id,name&', 'transferred_office', 'name', 'id');
    // $('#user-transfer-modal').modal('toggle');

    // $('#organization').val(transferdata['organization']).trigger('change.select2');
    // console.log('transfered off cat ========= ', transferdata['office_category']);
    // $('select[name="office_category"]').val(transferdata['office_category']).trigger('change.select2');
    // // $('#office_category').val(off_cat).trigger('change.select2');
    //
    changeOrganization(transferdata['organization']);

    $('input[name="user_id"]').val(id);
    let userCallBack = callAjax('/lged/api/v1/users/' + id, 'GET', "");
    userCallBack.done(function (data) {
        $('#previous_office_id').text(data['office_id']);
        $('#previous_designation_id').text(data['designation_id']);
        $('#previous_organization').text(data['organization']);
        $('#previous_office_category').text(data['office_category']);
        $('#previous_office').text(data['office_name']);
        $('#previous_official_email').text(data['official_email']);
        $('#previous_official_mobile').text(data['official_mobile_no']);
        $('#previous_designation').text(data['designation_name']);
        $('#previous_english_name').text(data['first_name']);
        $('#previous_bangla_name').text(data['bengali_name']);
        $('#previous_nid').text(data['nid_value']);
        // $('#previous_nid2').text(data['nid_value']);
        $('#previous_personal_email').text(data['personal_email']);
        $('#previous_personal_mobile').text(data['personal_mobile_no']);
        $('#previous_gender').text(data['gender']);
        let date_of_birth = (data['date_of_birth']) ? moment(data['date_of_birth'], "YYYY-MM-DD").format('DD-MM-YYYY') : '';
        $('#previous_date_of_birth').text(date_of_birth);
        let officeName = transferdata['transferred_office'].toString();
        console.log('officeName ========= ', officeName);
        $('#organization').val(transferdata['organization']).trigger('change.select2');
        $('#transferred_office').val(officeName).trigger('change.select2');
        change_office_category("first_time", transferdata['office_category']);

        if (data['organization'] === 'e-GP LAB') $('#office_category').val('').trigger('change.select2');
        commonSetDropDownAndSet('/lged/api/v1/designation/', $('select[name="new_designation"]'),
            'designation', 'id', '-Select Option-', 'elem', transferdata['new_designation']);
        // $("#organization").data('previous', data['organization']);
        // $("#office_category").data('previous', data['office_category']);
        // $('select[name="new_designation"]').data('previous', data['designation_id']);

        // $('#office_category').val(transferdata['office_category']).trigger('change.select2');
    });

    //






    $("select[id='organization']").change(function () {
        $(".office-category-holder").css('display', 'block');
        let organization = $("select[id='organization']").val();
        let office_category = $("select[id='office_category']").val();
        changeOrganization(organization);
    });
    $("select[id='organization'], select[id='office_category']").change(function () {
        // if (flag === 0 && $('select[name="status"]').val() !== '') {
        //     var retVal = confirm('Are you sure?');
        //     if (retVal === false) {
        //         // alert($(this).data('previous'));
        //         $(this).val($(this).data('previous')).trigger('change.select2');
        //         if ($(this).attr('id') === "organization") {
        //             changeOrganization($(this).data('previous'));
        //             $("#office_category").val($('#office_category').data('previous'));
        //         }
        //         return;
        //     }
        //     flag = 1;
        // }
        $("select[name='transferred_office']").val('').trigger('change.select2');
        let organization = $("select[id='organization']").val();
        let office_category = $("select[id='office_category']").val();
        // let region = $("select[name='region']").val();
        // let district = $("select[name='district']").val();

        let params = "";
        if (organization !== "") params = "organization=" + organization + '&';
        if (office_category !== "") params += "office_category=" + office_category + '&';
        // if (region !== "") params += "region=" + region + '&';
        // if (district !== "") params += "district=" + district + '&';
        params += 'transfer=1&fields=id,name&';

        commonSetDropDown('/lged/api/v1/office/?' + params, 'transferred_office', 'name', 'id');
    });


    $('#details').on('click', function () {
        if ($('#detail_toggle').css('display') === 'none') {
            $('#detail_toggle').css('display', 'block');
            $('#details').text('Less');
        } else {
            $('#detail_toggle').css('display', 'none');
            $('#details').text('Details');
        }
    });


    // $('#organization').val(transferdata['organization']).trigger('change');
    // if (transferdata['office_category'] !== 'e-GP LAB OFFICES') {
    //     $('#office_category').val(transferdata['office_category']).trigger('change');
    //     $('#transferred_office').val(transferdata['transferred_office']).trigger('change');
    //     console.log('off cat ========== ', transferdata['office_category']);
    //     console.log('transferred_office ========== ', transferdata['transferred_office']);
    // }
    //
    // // else $('#update_user_off_cat').val('').trigger('change');
    // else {
    //     $('#office_category').val('').trigger('change.select2');
    //     setTimeout(function () {
    //         $('#transferred_office').val(transferdata['transferred_office']).trigger('change.select2');
    //     }, 1000);
    // }

}

function set_case123_table(url) {
    var table = $('#external-member-inclusion-table').DataTable({
        "language": {
            "info": "<b style='color: #4c95a4;'>Total External Member Inclusion History: _TOTAL_</b>",
        },
        processing: true,
        serverSide: true,
        searching: false,
        ordering: true,
        ajax: $.fn.dataTable.pipeline({
            url: url,
            pages: 1 // number of pages to cache
        }),
        deferRender: true,
        scroller: true,
        scrollX: 850,
        scrollY: 500,
        scrollCollapse: true,
        rowId: "id",
        dom: '<"top"Bf>rt<"bottom"ip><"clear">',
        buttons: [
            {
                extend: 'print',
                exportOptions: {
                    columns: ':visible'
                },
                header: true,
                title: "",
                messageTop:
                    "<span class='print-table-header'>Table Name: External Member Inclusion History</span><br>" +
                    "<span class='print-table-header'>Date : " + moment(new Date().toJSON().slice(0, 10).replace(/-/g, '/', 'YYYY/MM/DD')).format('DD-MM-YYYY') + "</span><br>"
                // "<span class='print-table-header'>Date: </span><br>",
            },
            {
                extend: 'csv',
                exportOptions: {
                    columns: ':visible'
                }
            },
            // {
            //     extend: 'pdf',
            //     exportOptions: {
            //         columns: ':visible'
            //     }
            // },
            'pageLength'
        ],
        "lengthMenu": [[10, 25, 50, 1000000], [10, 25, 50, "All"]],


        "columns": [
            {"data": ""},
            {"data": "organization"},
            {"data": "office_category"},
            {"data": "office_name"},
            {"data": "bangla_name"},
            {"data": "user_id_for_pro_info"},
            {"data": "focal_designation_name"},
            // {"data": ""},
            {"data": ""},
            {"data": "first_name"},
            {"data": "designation_name"},
            {"data": "nid"},
            {"data": "personal_mobile_no"},
            {"data": "official_email"},
            {"data": "date_of_birth"},
            {"data": "procurement_roles_list"},
            {"data": "e_gp_user_id_for_govt"},
            {"data": "PPR_training"},
            {"data": "start_date"},
            {"data": "venue_name"},
            // {"data": "certificate"},
            {"data": "approved_status"}
        ],

        "columnDefs": [

            {
                "targets": 0,
                "data": '',
                "render": function (data, type, row, meta) {
                    return (table.page.info()['start'] + meta['row'] + 1);
                }
            },
            // {
            //     "targets": 7,
            //     "data": "",
            //     "render": function (data, type, row, meta) {
            //         return '<a id="' + row['id'] + '" class="admin-user-link" href="#">View</a>';
            //     }
            // },
            {
                "targets": 7,
                "data": "",
                "render": function (data, type, row, meta) {
                    return '<a id="' + row['id'] + '" class="govt-user-link" href="#">View</a>';
                }
            },
            {
                "targets": 16,
                "data": "",
                "render": function (data, type, row, meta) {
                    if (data) return 'Yes';
                    return 'No';
                }
            },
            // {
            //     "targets": 19,
            //     "data": "",
            //     "render": function (data, type, row, meta) {
            //         if (data) return '<a target="_blank" href="' + data + '">Certificate</a>';
            //         return '';
            //     }
            // },
            {
                "targets": 19,
                "data": "",
                "render": function (data, type, row, meta) {
                    // let transfer_type = row['type_display'];
                    if (row['approved_status'] === 0) return 'Pending';
                    else if (row['approved_status'] === 1 ) return 'Approved';
                }
            }

        ],
        "createdRow": function (row, data, index) {
            if (data['approved_status'] === 0) {
                $(row).addClass('f-600');
            }
        }
    });
    return table;
}


function set_case4_table(url) {
    var table = $('#external-member-inclusion-table-case-4').DataTable({
        "language": {
            "info": "<b style='color: #4c95a4;'>Total External Member Transfer History: _TOTAL_</b>",
        },
        processing: true,
        serverSide: true,
        searching: false,
        ordering: false,
        ajax: $.fn.dataTable.pipeline({
            url: url,
            pages: 1 // number of pages to cache
        }),
        deferRender: true,
        scroller: true,
        scrollX: 850,
        scrollY: 500,
        scrollCollapse: true,
        rowId: "id",
        dom: '<"top"Bf>rt<"bottom"ip><"clear">',
        buttons: [
            {
                extend: 'print',
                exportOptions: {
                    columns: ':visible'
                },
                header: true,
                title: "",
                messageTop:
                    "<span class='print-table-header'>Table Name: External Member Inclusion History</span><br>" +
                    "<span class='print-table-header'>Date : " + moment(new Date().toJSON().slice(0, 10).replace(/-/g, '/', 'YYYY/MM/DD')).format('DD-MM-YYYY') + "</span><br>"
                // "<span class='print-table-header'>Date: </span><br>",
            },
            {
                extend: 'csv',
                exportOptions: {
                    columns: ':visible'
                }
            },
            // {
            //     extend: 'pdf',
            //     exportOptions: {
            //         columns: ':visible'
            //     }
            // },
            'pageLength'
        ],
        "lengthMenu": [[10, 25, 50, 1000000], [10, 25, 50, "All"]],


        "columns": [
            {"data": ""},
            {"data": "user_name"},
            {"data": "transferred_office_name"},
            {"data": "new_designation_name"},
            {"data": "transfer_memo_no"},
            {"data": "transfer_order"},
            {"data": "charge_handover_date"},
            {"data": "approved_status"}
        ],

        "columnDefs": [
            {
                "targets": 0,
                "data": '',
                "render": function (data, type, row, meta) {
                    return (table.page.info()['start'] + meta['row'] + 1);
                }
            },
            {
                "targets": 5,
                "data": "",
                "render": function (data, type, row, meta) {
                    if (data) return '<a target="_blank" href="' + data + '">Transfer Order</a>';
                    return '';
                }
            },
            {
                "targets": 7,
                "data": "",
                "render": function (data, type, row, meta) {
                    if (row['approved_status'] === 0) return 'Pending';
                    else if (row['approved_status'] === 1 ) return 'Approved';
                }
            }
        ],
        "createdRow": function (row, data, index) {
            if (data['approved_status'] === 0) {
                $(row).addClass('f-600');
            }
        }
    });
    return table;
}