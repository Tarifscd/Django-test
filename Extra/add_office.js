function init_add_office() {
    $('.select2').select2();
    commonSetDropDown('/lged/api/v1/division/', 'division', 'name', 'id');
    commonSetDropDown('/lged/api/v1/region/', 'region', 'name', 'id');
    commonSetDropDown('/lged/api/v1/district/', 'district', 'name', 'id');
    commonSetDropDown('/lged/api/v1/upazila', 'upazila', 'name', 'id');
    changeCityCorporation();

    function objectifyForm(formArray) {//serialize data function

        var returnArray = {};
        var users = [];

        for (var i = 0; i < formArray.length; i++) {

            if (formArray[i]['name'] === 'users') {
                users.push(formArray[i]['value'])
            } else {
                returnArray[formArray[i]['name']] = formArray[i]['value'];
            }
            returnArray['users'] = users.toString();
        }
        return returnArray;
    }

    $('#add-office-form-reset-btn').click(function () {
        $("select").val('').trigger('change.select2');
    });

    $('#add-office-form').parsley().on('form:submit', function () {
        var x = $('#add-office-form').serializeArray();
        var jsonData = objectifyForm(x);
        if (jsonData['latt'] === "") {
            delete jsonData['latt'];
        }
        if (jsonData['long'] === "") {
            delete jsonData['long'];
        }
        console.log('add office ========= ',jsonData);
        $.ajax({
            method: 'POST',
            url: '/lged/api/v1/office/',
            data: JSON.stringify(jsonData),
            dataType: "json",
            contentType: "application/json; charset=utf-8",
            done: function (data) {
            },
            complete: function () {
            },
            success: function (data) {
                console.log('post resp ============ ',data['id'], '   ', data['name']);
                $('#add-office-form')[0].reset();
                $("select").val('').trigger('change.select2');
                notify('Office added successfully', 'success');
            },
            error: function (request, status, error) {
                showError(request);
            }
        });
        return false; // Don't submit form for this demo
    });

    $("select[name='division']").change(function () {
        var division_id = $("select[name='division']").val();
        if (division_id == "") return false;
        commonSetDropDown('/lged/api/v1/region/?id=' + division_id, 'region', 'name', 'id');
    });

    $("select[name='region']").change(function () {
        var region_id = $("select[name='region']").val();
        if (region_id == "") return false;
        commonSetDropDown('/lged/api/v1/district/?id=' + region_id, 'district', 'name', 'id');
    });

    $("select[name='district']").change(function () {
        var district_id = $("select[name='district']").val();
        if (district_id == "") return false;
        commonSetDropDown('/lged/api/v1/upazila/?id=' + district_id, 'upazila', 'name', 'id');
    });

    $("select[name='organization']").change(function () {
        var organization_id = $("select[name='organization']").val();
        if (organization_id === "") return false;
        changeOrganization(organization_id);
    });

    $("select[name='office_category']").change(function () {
        var office_category = $(this).val();
        if (office_category === "PAURASHAVA OFFICES") $('#pourashava_class').css('display', 'block');
        else $('#pourashava_class').css('display', 'none');
    });
}