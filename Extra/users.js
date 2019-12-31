function set_user_list_table(url, office_name, user_type, office_category, organization, admin_user) {

    // console.log(url)
    var table = $('#user_list_table').DataTable({
        //here is the solution
        "infoCallback": function (settings, start, end, max, total, pre) {
            let info = "";
            if (!admin_user && user_type === "other") {
                info = "<b style='color: #4c95a4;'>Note: Not According to Seniority/Grade</b><br>";
            }
            info += "<b style='color: #4c95a4;'>Total Users: " + total + "</b>";
            return info;
        },
        "language": {
            // "info": "<b style='color: #4c95a4;'>Total Users: _TOTAL_</b>",
        },
        processing: true,
        serverSide: true,
        ordering: false,
        info: true,
        ajax: $.fn.dataTable.pipeline({
            url: url,
            pages: 1 // number of pages to cache
        }),
        // scrollY: 350,
        // colReorder: true,
        deferRender: true,
        scroller: true,
        scrollX: 850,
        scrollY: 500,
        scrollCollapse: true,
        rowId: "id",
        dom: '<"top"Bfp>rt<"bottom"ip><"clear">',
        buttons: [
            {
                extend: 'print',
                exportOptions: {
                    columns: ':visible th:not(.no-print)',
                    stripHtml: false,
                },
                header: true,
                title: "",
                className: 'btn btn-sm btn-default',
                messageTop: function () {
                    let temp = "<span class='print-table-header'>Office Name: " + office_name + "</span><br>" +
                        "<span class='print-table-header'>Table Name: User</span><br>" +
                        "<span class='print-table-header'>Date : " + moment(new Date().toJSON().slice(0, 10).replace(/-/g, '/', 'YYYY/MM/DD')).format('DD-MM-YYYY') + "</span><br>";
                    if (admin_user) temp += "<span class='print-table-header'>Search Fields: " + $('#search_users').text() + "</span>";
                    return temp;

                }
                // "<span class='print-table-header'>Date: </span><br>",
            },
            {
                extend: 'csv',
                exportOptions: {
                    columns: ':visible'
                },
                className: 'btn btn-sm btn-default',
            },
            // {
            //     extend: 'pdf',
            //     exportOptions: {
            //         columns: ':visible'
            //     },
            //     className: 'btn btn-sm btn-default',
            //     orientation: 'landscape',
            //     pageSize: 'LEGAL',
            //     messageTop: function () {
            //         return "Office Name: " + office_name + "\n" +
            //             "Table Name: User \n" +
            //             "Date : " + moment(new Date().toJSON().slice(0, 10).replace(/-/g, '/', 'YYYY/MM/DD')).format('DD-MM-YYYY') + "\n" +
            //             "Search Fields: " + $('#search_users').text() + "\n";
            //     }
            // },
            {
                extend: 'pageLength',
                className: 'btn btn-sm btn-default',
            }
            // 'colvis'
        ],
        "lengthMenu": [[10, 25, 50, 1000000], [10, 25, 50, "All"]],
        "columns": [
            {"data": ""},
            {"data": "office_name"},
            {"data": "division"},
            {"data": "region"},
            {"data": "district"},
            {"data": "upazila"},
            {"data": ""},
            {"data": "first_name"},
            {"data": "bengali_name"},
            {"data": "designation_name"},
            {"data": "personal_mobile_no"},
            {"data": "profile_official_mobile_no"},
            {"data": "email"},
            {"data": "official_email"},
            {"data": "personal_email"},
            {"data": "nid_value"},
            {"data": "gender"},
            {"data": "date_of_birth"},
            {"data": "PPR_training"},
            {"data": "procurement_role_list"},
            {"data": "procurement_role_list_lgis"},
            {'data': ""},
            {'data': "id"}
            // {"data": "e_gp_user_id_value"},
            // {"data": "e_gp_user_id_lgis_value"},
        ],
        "columnDefs": [
            {
                "targets": 0, // SL

                "render": function (data, type, row, meta) {
                    return (table.page.info()['start'] + meta['row'] + 1);
                }
            },

            // {
            //     "targets": 1, // SL
            //
            //     "render": function (data, type, row, meta) {
            //         console.log(row)
            //     }
            // },

            {
                "targets": 6, // Picture
                "render": function (data, type, row, meta) {
                    // if (row['floating']) return '';
                    if (row['profile_avatar'] !== null) {
                        return '<img class="attachment-img small-user-img" src="' + row['profile_avatar'] + '" alt="">';
                    } else {
                        return '<img class="attachment-img small-user-img" src="' + '/media/avatars/default_profile_pic.jpg' + '" alt="">';
                    }

                }
            },
            {
                "targets": 7, // First Name
                "data": "",
                "render": function (data, type, row, meta) {
                    // if (user_type !== "floating" && row['floating']) return '';
                    return data;
                }
            },
            {
                "targets": 8, // Bengali Name
                "data": "",
                "render": function (data, type, row, meta) {
                    // if (user_type !== "floating" && row['floating']) return '';
                    return data;
                }
            },
            {
                "targets": 10, // Personal Mobile No
                "data": "",
                "render": function (data, type, row, meta) {
                    // if (user_type !== "floating" && row['floating']) return '';
                    return data;
                }
            },
            {
                "targets": [14], // Personal Email
                "data": "",
                "render": function (data, type, row, meta) {
                    // if (user_type !== "floating" && row['floating']) return '';
                    return data;
                }
            },
            {
                "targets": 15, // NID
                "visible": (user_type !== "focal_point"),
                "data": "",
                "render": function (data, type, row, meta) {
                    // if (user_type !== "floating" && row['floating']) return '';
                    return data;
                }
            },
            {
                "targets": 12, // E-mail
                "visible": (user_type === "focal_point" || user_type === "all"),
                "data": "",
                "render": function (data, type, row, meta) {
                    return data;
                }
            },
            {
                "targets": 16, // Gender
                "data": "",
                "render": function (data, type, row, meta) {
                    // if (user_type !== "floating" && row['floating']) return '';
                    return data;
                }
            },
            {
                "targets": 17, // Date of Birth
                "data": "",
                "render": function (data, type, row, meta) {
                    // if (user_type !== "floating" && row['floating']) return '';
                    if (data === '') return '';
                    if (data) return moment(data, "YYYY-MM-DD").format("DD-MM-YYYY");
                    else return '';
                }
            },
            {
                "targets": 18, // PPR Training Attendance
                "visible": (admin_user || (!admin_user && user_type !== 'focal_point')),
                "orderable": false,
                "render": function (data, type, row, meta) {
                    // if (user_type !== "floating" && row['floating']) return '';
                    return data;
                }
            },
            {
                "targets": 19, // Procurement Role for LGED Tenders
                "visible": (admin_user || (!admin_user && user_type !== 'focal_point')),
                "render": function (data, type, row, meta) {
                    // if (user_type !== "floating" && row['floating']) return '';
                    var roles = "<span style='color: #940505;'>Procurement Role: </span>";
                    let array = [];
                    data.forEach(function (item) {
                        if (user_type === "admin" && item['role'] === "Organization Admin") {
                            roles += item['role'];
                            roles += ',';
                        } else if (user_type === "admin" && item['role'] === "PE Admin") {
                            roles += item['role'];
                            roles += ',';
                        } else if (user_type === "focal_point" && item['role'] === "Focal Point") {
                            roles += item['role'];
                            roles += ',';
                        } else if (user_type === "other" && item['role'] !== "Organization Admin" &&
                            item['role'] !== "PE Admin" && item['role'] !== "Focal Point") {
                            roles += item['role'];
                            roles += ',';
                        } else if (user_type === "all") {
                            roles += item['role'];
                            roles += ',';
                        }
                        let innerText = item['role'];
                        if (innerText !== "Organization Admin" && innerText !== "PE Admin" && innerText !== "Focal Point")
                            innerText = "Other";
                        array.push(innerText);
                    });
                    if (roles[roles.length - 1] === ',' || roles[roles.length - 1] === ';') roles = roles.slice(0, roles.length - 1);
                    // roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + row['e_gp_user_id_value'];

                    if ((user_type === "admin" && $.inArray("Organization Admin", array) !== -1) || (user_type === "all" && row['e_gp_user_id_for_org_admin'])) {
                        if (row['e_gp_user_id_for_org_admin']) roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + row['e_gp_user_id_for_org_admin'];
                        else roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + '';
                    }
                    if ((user_type === "admin" && $.inArray("PE Admin", array) !== -1) || (user_type === "all" && row['e_gp_user_id_for_pe_admin'])) {
                        if (row['e_gp_user_id_for_pe_admin']) roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + row['e_gp_user_id_for_pe_admin'];
                        else roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + '';
                    }
                    if ((user_type === "other" && $.inArray("Other", array) !== -1) || (user_type === "all" && row['e_gp_user_id_for_govt'])) {
                        if (row['e_gp_user_id_for_govt']) roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + row['e_gp_user_id_for_govt'];
                        else roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + '';
                    }
                    // console.log(row);
                    return roles;
                }
            },
            {
                "targets": 20, // Procurement Role for LGIs Tenders
                "visible": ((admin_user) || (!admin_user && user_type !== 'focal_point' && organization !== 'LGED')),
                "render": function (data, type, row, meta) {
                    // if (user_type !== "floating" && row['floating']) return '';
                    var roles = "<span style='color: #940505;'>Procurement Role: </span>";
                    let array = [];
                    data.forEach(function (item) {
                        if (user_type === "admin" && item['role'] === "Organization Admin") {
                            roles += item['role'];
                            roles += ',';
                        } else if (user_type === "admin" && item['role'] === "PE Admin") {
                            roles += item['role'];
                            roles += ',';
                        } else if (user_type === "focal_point" && item['role'] === "Focal Point") {
                            roles += item['role'];
                            roles += ',';
                        } else if (user_type === "other" && item['role'] !== "Organization Admin" &&
                            item['role'] !== "PE Admin" && item['role'] !== "Focal Point") {
                            roles += item['role'];
                            roles += ',';
                        } else if (user_type === "all") {
                            roles += item['role'];
                            roles += ',';
                        }
                        let innerText = item['role'];
                        if (innerText !== "Organization Admin" && innerText !== "PE Admin" && innerText !== "Focal Point")
                            innerText = "Other";
                        array.push(innerText);
                    });
                    if (roles[roles.length - 1] === ',' || roles[roles.length - 1] === ';') roles = roles.slice(0, roles.length - 1);
                    // roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + row['e_gp_user_id_lgis_value'];

                    if ((user_type === "admin" && $.inArray("Organization Admin", array) !== -1) || (user_type === "all" && row['e_gp_user_id_lgis_for_org_admin'])) {
                        if (row['e_gp_user_id_lgis_for_org_admin']) roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + row['e_gp_user_id_lgis_for_org_admin'];
                        else roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + '';
                    }
                    if (user_type === "admin" && $.inArray("PE Admin", array) !== -1) {
                        if (row['e_gp_user_id_lgis_for_pe_admin']) roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + row['e_gp_user_id_lgis_for_pe_admin'];
                        else roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + '';
                    }
                    if ((user_type === "other" && $.inArray("Other", array) !== -1) || (user_type === "all" && row['e_gp_user_id_lgis_for_govt'])) {
                        if (row['e_gp_user_id_lgis_for_govt']) roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + row['e_gp_user_id_lgis_for_govt'];
                        else roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + '';
                    }
                    // console.log("roles " + roles);
                    return roles;
                }
            },
            {
                "targets": 21, // Training History
                "orderable": false,
                "visible": (admin_user || (!admin_user && user_type !== 'focal_point')),
                "render": function (data, type, row, meta) {
                    // if (user_type !== "floating" && row['floating']) return '';
                    // if (row['existing_user'] === false) return '';
                    // console.log('row', row);
                    let str = '/lged/training/list/' + row['id'];
                    let button = "<a href=\"" + str + "\" type=\"submit\" id=\"batch-details-btn\" class=\"btn-xs\">" +
                        "<i class=\"fa fa-fw fa-external-link text-green\"></i>View</a>"
                    return button;
                }
            },
            {

                "targets": 22, // Audit Trail
                "visible": (admin_user),
                "orderable": false,
                "render": function (data, type, row, meta) {
                    // if (user_type !== "floating" && row['floating']) return '';
                    var text = "Detail";
                    return '<button  class="app-approve-btn btn btn-success btn-xs" value="' + row['id'] + '">' + text + '</button>';

                }
            }

        ],
        "drawCallback": function () {
            $('.app-approve-btn').on('click', function () {
                var par = '?module_id=' + $(this).val() + '&module=USER PROFILE';
                window.location = "/lged/audit-trail/" + par;
            });

        },
        "createdRow": function (row, data, index) {
            if (data['existing_user'] === false) {
                $(row).addClass('f-600');
            }
        }

    });
    return table;
}

function set_user_list_temp_office_table(urlx, office_name, user_type, office_category, organization, admin_user) {

    console.log(urlx)
    var table = $('#user_list_temp_office_table').DataTable({
        //here is the solution
        "infoCallback": function (settings, start, end, max, total, pre) {
            let info = "";
            if (!admin_user && user_type === "other") {
                info = "<b style='color: #4c95a4;'>Note: Not According to Seniority/Grade</b><br>";
            }
            info += "<b style='color: #4c95a4;'>Total Users: " + total + "</b>";
            return info;
        },
        "language": {
            // "info": "<b style='color: #4c95a4;'>Total Users: _TOTAL_</b>",
        },
        processing: true,
        serverSide: true,
        ordering: true,
        info: true,
        ajax: $.fn.dataTable.pipeline({
            url: urlx,
            pages: 1 // number of pages to cache
        }),
        // scrollY: 350,
        // colReorder: true,
        deferRender: true,
        scroller: true,
        scrollX: 850,
        scrollY: 500,
        scrollCollapse: true,
        rowId: "id",
        dom: '<"top"Bfp>rt<"bottom"ip><"clear">',
        buttons: [
            {
                extend: 'print',
                exportOptions: {
                    columns: ':visible th:not(.no-print)',
                    stripHtml: false,
                },
                header: true,
                title: "",
                className: 'btn btn-sm btn-default',
                messageTop: function () {
                    let temp = "<span class='print-table-header'>Office Name: " + office_name + "</span><br>" +
                        "<span class='print-table-header'>Table Name: User</span><br>" +
                        "<span class='print-table-header'>Date : " + moment(new Date().toJSON().slice(0, 10).replace(/-/g, '/', 'YYYY/MM/DD')).format('DD-MM-YYYY') + "</span><br>";
                    if (admin_user) temp += "<span class='print-table-header'>Search Fields: " + $('#search_users').text() + "</span>";
                    return temp;
                }
                // "<span class='print-table-header'>Date: </span><br>",
            },
            // {
            //     extend: 'csv',
            //     exportOptions: {
            //         columns: ':visible'
            //     },
            //     className: 'btn btn-sm btn-default',
            // },
            // {
            //     extend: 'pdf',
            //     exportOptions: {
            //         columns: ':visible'
            //     },
            //     className: 'btn btn-sm btn-default',
            //     orientation: 'landscape',
            //     pageSize: 'LEGAL',
            //     messageTop: function () {
            //         return "Office Name: " + office_name + "\n" +
            //             "Table Name: User \n" +
            //             "Date : " + moment(new Date().toJSON().slice(0, 10).replace(/-/g, '/', 'YYYY/MM/DD')).format('DD-MM-YYYY') + "\n" +
            //             "Search Fields: " + $('#search_users').text() + "\n";
            //     }
            // },
            {
                extend: 'pageLength',
                className: 'btn btn-sm btn-default',
            }
            // 'colvis'
        ],
        "lengthMenu": [[10, 25, 50, 1000000], [10, 25, 50, "All"]],
        "columns": [
            {"data": "id"},
            {"data": "office_name"},
            {"data": "division"},
            {"data": "region"},
            {"data": "district"},
            {"data": "upazila"},
            {"data": ""},
            {"data": "first_name"},
            {"data": "bengali_name"},
            {"data": "designation_name"},
            {"data": "personal_mobile_no"},
            {"data": "official_mobile_no"},
            //{"data": "email"},
            {"data": "official_email"},
            {"data": "personal_email"},
            {"data": "nid_value"},
            {"data": "gender"},
            {"data": "date_of_birth"},
            {"data": "PPR_training"},
            {"data": "procurement_role_list"},
            {"data": "procurement_role_list_lgis"},
            {'data': ""},
            {'data': "user"}
            // {"data": "e_gp_user_id_value"},
            // {"data": "e_gp_user_id_lgis_value"},
        ],
        "columnDefs": [
            {
                "targets": 0, // SL

                "render": function (data, type, row, meta) {
                    $('#'+data).attr('data-blank_user_id', row['blank_user_id']);
                    return (table.page.info()['start'] + meta['row'] + 1);
                }
            },

            // {
            //     "targets": 1, // SL
            //
            //     "render": function (data, type, row, meta) {
            //         console.log(row)
            //     }
            // },

            {
                "targets": 6, // Picture
                "render": function (data, type, row, meta) {


                    // if (row['floating']) return '';
                    if (row['profile_avatar'] !== null) {
                        return '<img class="attachment-img small-user-img" src="' + row['profile_avatar'] + '" alt="">';
                    } else {
                        return '<img class="attachment-img small-user-img" src="' + '/media/avatars/default_profile_pic.jpg' + '" alt="">';
                    }

                }
            },
            {
                "targets": 7, // First Name
                "data": "",
                "render": function (data, type, row, meta) {
                    // if (user_type !== "floating" && row['floating']) return '';
                    return data;
                }
            },
            {
                "targets": 8, // Bengali Name
                "data": "",
                "render": function (data, type, row, meta) {
                    // if (user_type !== "floating" && row['floating']) return '';
                    return data;
                }
            },
            {
                "targets": 10, // Personal Mobile No
                "data": "",
                "render": function (data, type, row, meta) {
                    // if (user_type !== "floating" && row['floating']) return '';
                    return data;
                }
            },
            {
                "targets": [13], // Personal Email
                "data": "",
                "render": function (data, type, row, meta) {
                    // if (user_type !== "floating" && row['floating']) return '';
                    return data;
                }
            },
            {
                "targets": 14, // NID
                "visible": (user_type !== "focal_point"),
                "data": "",
                "render": function (data, type, row, meta) {
                    // if (user_type !== "floating" && row['floating']) return '';
                    return data;
                }
            },
            // {
            //     "targets": 12, // E-mail
            //     "visible": (user_type === "focal_point" || user_type === "all"),
            //     "data": "",
            //     "render": function (data, type, row, meta) {
            //         return data;
            //     }
            // },
            {
                "targets": 15, // Gender
                "data": "",
                "render": function (data, type, row, meta) {
                    // if (user_type !== "floating" && row['floating']) return '';
                    return data;
                }
            },
            {
                "targets": 16, // Date of Birth
                "data": "",
                "render": function (data, type, row, meta) {
                    // if (user_type !== "floating" && row['floating']) return '';
                    if (data === '') return '';
                    if (data) return moment(data, "YYYY-MM-DD").format("DD-MM-YYYY");
                    else return '';
                }
            },
            {
                "targets": 17, // PPR Training Attendance
                "visible": (admin_user || (!admin_user && user_type !== 'focal_point')),
                "orderable": false,
                "render": function (data, type, row, meta) {
                    // if (user_type !== "floating" && row['floating']) return '';
                    return data;
                }
            },
            {
                "targets": 18, // Procurement Role for LGED Tenders
                "visible": (admin_user || (!admin_user && user_type !== 'focal_point')),
                "render": function (data, type, row, meta) {
                    // if (user_type !== "floating" && row['floating']) return '';
                    var roles = "<span style='color: #940505;'>Procurement Role: </span>";
                    let array = [];
                    console.log("data", data);
                    console.log("row", row.procurement_roles);
                    data.forEach(function (item) {
                        if (user_type === "admin" && item['role'] === "Organization Admin") {
                            roles += item['role'];
                            roles += ',';
                        } else if (user_type === "admin" && item['role'] === "PE Admin") {
                            roles += item['role'];
                            roles += ',';
                        } else if (user_type === "focal_point" && item['role'] === "Focal Point") {
                            roles += item['role'];
                            roles += ',';
                        } else if (user_type === "other" && item['role'] !== "Organization Admin" &&
                            item['role'] !== "PE Admin" && item['role'] !== "Focal Point") {
                            roles += item['role'];
                            roles += ',';
                        } else if (user_type === "all") {
                            roles += item['role'];
                            roles += ',';
                        }
                        let innerText = item['role'];
                        if (innerText !== "Organization Admin" && innerText !== "PE Admin" && innerText !== "Focal Point")
                            innerText = "Other";
                        array.push(innerText);
                    });
                    if (roles[roles.length - 1] === ',' || roles[roles.length - 1] === ';') roles = roles.slice(0, roles.length - 1);
                    // roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + row['e_gp_user_id_value'];

                    if (user_type === "admin" && $.inArray("Organization Admin", array) !== -1) {
                        if (row['e_gp_user_id_for_org_admin']) roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + row['e_gp_user_id_for_org_admin'];
                        else roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + '';
                    }
                    if (user_type === "admin" && $.inArray("PE Admin", array) !== -1) {
                        if (row['e_gp_user_id_for_pe_admin']) roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + row['e_gp_user_id_for_pe_admin'];
                        else roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + '';
                    }
                    if (user_type === "other" && $.inArray("Other", array) !== -1) {
                        if (row['e_gp_user_id_for_govt']) roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + row['e_gp_user_id_for_govt'];
                        else roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + '';
                    }
                    // console.log(row);
                    return roles;
                    // return "";
                }
            },
            {
                "targets": 19, // Procurement Role for LGIs Tenders
                "visible": ((admin_user) || (!admin_user && user_type !== 'focal_point' && organization !== 'LGED')),
                "render": function (data, type, row, meta) {
                    // if (user_type !== "floating" && row['floating']) return '';
                    var roles = "<span style='color: #940505;'>Procurement Role: </span>";
                    let array = [];
                    data.forEach(function (item) {
                        if (user_type === "admin" && item['role'] === "Organization Admin") {
                            roles += item['role'];
                            roles += ',';

                        } else if (user_type === "admin" && item['role'] === "PE Admin") {
                            roles += item['role'];
                            roles += ',';
                        } else if (user_type === "focal_point" && item['role'] === "Focal Point") {
                            roles += item['role'];
                            roles += ',';
                        } else if (user_type === "other" && item['role'] !== "Organization Admin" &&
                            item['role'] !== "PE Admin" && item['role'] !== "Focal Point") {
                            roles += item['role'];
                            roles += ',';
                        } else if (user_type === "all") {
                            roles += item['role'];
                            roles += ',';
                        }
                        let innerText = item['role'];
                        if (innerText !== "Organization Admin" && innerText !== "PE Admin" && innerText !== "Focal Point")
                            innerText = "Other";
                        array.push(innerText);
                    });
                    if (roles[roles.length - 1] === ',' || roles[roles.length - 1] === ';') roles = roles.slice(0, roles.length - 1);
                    // roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + row['e_gp_user_id_lgis_value'];

                    if (user_type === "admin" && $.inArray("Organization Admin", array) !== -1) {
                        if (row['e_gp_user_id_lgis_for_org_admin']) roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + row['e_gp_user_id_lgis_for_org_admin'];
                        else roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + '';
                    }
                    if (user_type === "admin" && $.inArray("PE Admin", array) !== -1) {
                        if (row['e_gp_user_id_lgis_for_pe_admin']) roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + row['e_gp_user_id_lgis_for_pe_admin'];
                        else roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + '';
                    }
                    if (user_type === "other" && $.inArray("Other", array) !== -1) {
                        if (row['e_gp_user_id_lgis_for_govt']) roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + row['e_gp_user_id_lgis_for_govt'];
                        else roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + '';
                    }
                    // console.log("roles " + roles);
                    return roles;
                }
            }
            ,
            {
                "targets": 20, // Training History
                "orderable": false,
                "visible": (admin_user || (!admin_user && user_type !== 'focal_point')),
                "render": function (data, type, row, meta) {
                    // if (user_type !== "floating" && row['floating']) return '';
                    // if (row['existing_user'] === false) return '';
                    // console.log('row', row);
                    let str = '/lged/training/list/' + row['user'];
                    let button = "<a href=\"" + str + "\" type=\"submit\" id=\"batch-details-btn\" class=\"btn-xs\">" +
                        "<i class=\"fa fa-fw fa-external-link text-green\"></i>View</a>"
                    return button;
                }
            },
            {

                "targets": 21, // Audit Trail
                "visible": (admin_user),
                "orderable": false,
                "render": function (data, type, row, meta) {
                    // if (user_type !== "floating" && row['floating']) return '';
                    var text = "Detail";
                    return '<button  class="app-approve-btn btn btn-success btn-xs" value="' + row['id'] + '">' + text + '</button>';

                }
            }

        ],
        "drawCallback": function () {
            $('.app-approve-btn').on('click', function () {
                var par = '?module_id=' + $(this).val() + '&module=USER PROFILE';
                window.location = "/lged/audit-trail/" + par;
            });

        },
        "createdRow": function (row, data, index) {
            if (data['existing_user'] === false) {
                $(row).addClass('f-600');
            }
        }

    });
    return table;
}

function set_imp_user_list_table(url) {

    // console.log(url)

    var table = $('#imp_user_list_table').DataTable({
        processing: true,
        serverSide: true,
        "info": false,
        "searching": false,
        "ordering": false,
        "paging": false,
        ajax: {
            "url": url,
            "dataSrc": "",
        },
        // scrollY: 350,
        // colReorder: true,
        deferRender: true,
        scroller: true,
        scrollX: 850,
        scrollY: 500,
        scrollCollapse: true,
        rowId: "id",
        dom: '<"top"Bfip>rt<"bottom"ip><"clear">',
        buttons: [
            {
                extend: 'print',
                exportOptions: {
                    columns: ':visible'
                }
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
            {"data": "office_name"},
            {"data": "division"},
            {"data": "region"},
            {"data": "district"},
            {"data": "upazila"},
            {"data": ""},
            {"data": "first_name"},
            {"data": "bengali_name"},
            {"data": "designation_name"},
            {"data": "personal_mobile_no"},
            {"data": "profile_official_mobile_no"},
            {"data": "email"},
            {"data": "official_email"},
            {"data": "personal_email"},
            {"data": "nid_value"},
            {"data": "gender"},
            {"data": "date_of_birth"},
            {"data": "procurement_role_list"},
            {"data": "procurement_role_list_lgis"},
            {"data": ""},
            {"data": "id"}
            // {"data": "e_gp_user_id_value"},
            // {"data": "e_gp_user_id_lgis_value"},
        ],
        "columnDefs": [
            {
                "targets": 0,
                "data": '',
                "render": function (data, type, row, meta) {
                    //console.log(row);
                    return (table.page.info()['start'] + meta['row'] + 1);
                }
            },
            {
                "targets": 6,
                "render": function (data, type, row, meta) {
                    // {% if user.profile is not none and user.profile.image_name %}
                    //     <img src="{{ MEDIA_URL }}avatars/{{ user.profile.image_name }}"
                    //          class="user-image"
                    //          alt="">
                    // {% else %}
                    //     <img src="{{ MEDIA_URL }}avatars/default_profile_pic.jpg"
                    //          class="user-image"
                    //          alt="">
                    // {% endif %}
                    if (row['profile_avatar'] !== null) {
                        return '<img class="attachment-img small-user-img" src="' + row['profile_avatar'] + '" alt="">';
                    } else {
                        return '<img class="attachment-img small-user-img" src="' + '/media/avatars/default_profile_pic.jpg' + '" alt="">';
                    }

                }
            },
            {
                "targets": 17,
                "render": function (data, type, row, meta) {
                    var roles = "<span style='color: #940505;'>Procurement Role: </span>";
                    let array = [];
                    data.forEach(function (item) {
                        roles += item['role'];
                        roles += ',';
                        let innerText = item['role'];
                        if (innerText !== "Organization Admin" && innerText !== "PE Admin" && innerText !== "Focal Point")
                            innerText = "Other";
                        array.push(innerText);
                    });
                    if (roles[roles.length - 1] === ',') roles = roles.slice(0, roles.length - 1);
                    // roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + row['e_gp_user_id_value'];

                    if ($.inArray("Organization Admin", array) !== -1) roles +=
                        '<br><span style=\'color: #940505;\'>e-GP ID for Organization Admin: </span>' + row['e_gp_user_id_for_org_admin'];
                    if ($.inArray("PE Admin", array) !== -1) roles +=
                        '<br><span style=\'color: #940505;\'>e-GP ID for PE Admin: </span>' + row['e_gp_user_id_for_pe_admin'];
                    if ($.inArray("Other", array) !== -1) roles +=
                        '<br><span style=\'color: #940505;\'>e-GP ID for Govt. Users: </span>' + row['e_gp_user_id_for_govt'];
                    // console.log(row);
                    return roles;
                }
            },
            {
                "targets": 18,
                "render": function (data, type, row, meta) {
                    var roles = "<span style='color: #940505;'>Procurement Role: </span>";
                    let array = [];
                    data.forEach(function (item) {
                        roles += item['role'];
                        roles += ',';
                        let innerText = item['role'];
                        if (innerText !== "Organization Admin" && innerText !== "PE Admin" && innerText !== "Focal Point")
                            innerText = "Other";
                        array.push(innerText);
                    });
                    if (roles[roles.length - 1] === ',') roles = roles.slice(0, roles.length - 1);
                    // roles += '<br><span style=\'color: #940505;\'>e-GP ID: </span>' + row['e_gp_user_id_lgis_value'];

                    if ($.inArray("Organization Admin", array) !== -1) roles +=
                        '<br><span style=\'color: #940505;\'>e-GP ID for Organization Admin: </span>' + row['e_gp_user_id_lgis_for_org_admin'];
                    if ($.inArray("PE Admin", array) !== -1) roles +=
                        '<br><span style=\'color: #940505;\'>e-GP ID for PE Admin: </span>' + row['e_gp_user_id_lgis_for_pe_admin'];
                    if ($.inArray("Other", array) !== -1) roles +=
                        '<br><span style=\'color: #940505;\'>e-GP ID for Govt. Users: </span>' + row['e_gp_user_id_lgis_for_govt'];
                    // console.log("roles " + roles);
                    return roles;
                }
            },
            {
                "targets": 19,
                "orderable": false,
                "render": function (data, type, row, meta) {
                    // console.log('row', row);
                    let str = '/lged/training/list/' + row['id'];
                    let button = "<a href=\"" + str + "\" type=\"submit\" id=\"batch-details-btn\" class=\"btn-xs\">" +
                        "<i class=\"fa fa-fw fa-external-link text-green\"></i>View</a>";
                    return button;
                }
            },
            {

                "targets": 20,
                "orderable": false,
                "render": function (data, type, row, meta) {
                    var text = "Detail";
                    return '<button  class="app-approve-btn btn btn-success btn-xs" value="' + row['id'] + '">' + text + '</button>';

                }
            }
        ],
        "drawCallback": function () {
            $('.app-approve-btn').on('click', function () {
                var par = '?module_id=' + $(this).val() + '&module=USER PROFILE';
                window.location = "/lged/audit-trail/" + par;
            });
        }
    });
    return table;
}

// function setSearchTableForTransfer(url) {
//     var table = $('#search-table-for-transfer').DataTable({
//         processing: true,
//         serverSide: true,
//         "info": false,
//         "searching": false,
//         "ordering": false,
//         "paging": false,
//         ajax: {
//             "url": url,
//             "dataSrc": "",
//         },
//         // scrollY: 350,
//         // colReorder: true,
//         deferRender: true,
//         scroller: true,
//         scrollX: 850,
//         scrollY: 500,
//         scrollCollapse: true,
//         rowId: "id",
//         dom: '<"top"ip>rt<"bottom"ip><"clear">',
//         "columns": [
//             {"data": "office_name"},
//             {"data": "region"},
//             {"data": "district"},
//             {"data": ""},
//             {"data": "first_name"},
//             {"data": "bengali_name"},
//             {"data": "designation_name"},
//             {"data": "personal_mobile_no"},
//             {"data": "profile_official_mobile_no"},
//             {"data": "email"},
//             {"data": "personal_email"},
//         ],
//         "columnDefs": [
//             {
//                 "targets": 3,
//                 "render": function (data, type, row, meta) {
//                     if (row['profile_avatar'] !== null) {
//                         return '<img class="attachment-img small-user-img" src="' + row['profile_avatar'] + '" alt="">';
//                     } else {
//                         return '<img class="attachment-img small-user-img" src="' + '/media/avatars/default_profile_pic.jpg' + '" alt="">';
//                     }
//
//                 }
//             },
//         ],
//     });
//     return table;
// }

function delete_user(id) {
    console.log("Delete this user");
    $('.confirm-delete-input-modal').modal('toggle');
}

function delete_additional_user(id) {
    console.log("Delete this additional user");
    $('#additional-user-delete-modal').modal('toggle');
}

function init_users(office_category, logged_in_office, media_url, bool_data, office_name, user_type, transfer,
                    column_customization_form, organization, user_permissions) {
    $.fn.modal.Constructor.prototype.enforceFocus = function () {
    };
    let govt_flag = 0;
    if(user_type === "other"){
        govt_flag = 1;
        console.log('user_type pr ========== ', user_type);
        user_type = 'all';
    }
    console.log('user_type af ========== ', user_type);

    console.log(logged_in_office);

    let admin_user = false;
    if (user_permissions.includes('user_admin')) admin_user = true;
    let update_user_office_id = '';
    let row_selected_id = 1;
    let designation_url = '';
    let crud_api = '/lged/api/v1/users/';
    let temp_api = '/lged/api/v1/temporaryoffice/';
    let paramglobe = ''
    $('#users-ul').addClass("active");
    $('#users-ul').addClass("menu-open");
    $('#users').addClass("active");
    commonSetDropDown('/lged/api/v1/roles/', 'role', 'name', 'id');
    commonSetDropDown('/lged/api/v1/procurement/role/', 'update_procurement_roles', 'role', 'id', '-Select Option-');
    commonSetDropDown('/lged/api/v1/designation/', 'add_designation', 'short_form', 'id');
    $('#user-update-modal').modal({
        backdrop: 'static',
        keyboard: false,
        show: false,
    });




    $('#user-add-modal').modal({
        backdrop: 'static',
        keyboard: false,
        show: false,
    });

    $('#user-transfer-modal').modal({
        backdrop: 'static',
        keyboard: false,
        show: false,
    });

    function objectifyForm(formArray) {//serialize data function
        var returnArray = {};
        var procurementArr = [];

        for (var i = 0; i < formArray.length; i++) {

            if (formArray[i]['name'] === 'procurement_roles') {
                procurementArr.push(formArray[i]['value'])
            } else {
                returnArray[formArray[i]['name']] = formArray[i]['value'];
            }
            returnArray['procurement_role'] = procurementArr.toString();
            returnArray['description'] = "";
        }
        return returnArray;
    }

    $('select[name="procurement_roles"]').on('change', function () {
        let object = $(this).find('option:selected');
        let array = [];
        for (var i = 0; i < object.length; i++) {
            let innerText = object[i].innerText;
            if (innerText !== "Organization Admin" && innerText !== "PE Admin" && innerText !== "Focal Point")
                innerText = "Other";
            array.push(innerText);
        }
        if ($.inArray("Organization Admin", array) !== -1) $('#add-e-gp-id-org-admin-lged-holder').css('display', 'block');
        else $('#add-e-gp-id-org-admin-lged-holder').css('display', 'none');
        if ($.inArray("PE Admin", array) !== -1) $('#add-e-gp-id-pe-admin-lged-holder').css('display', 'block');
        else $('#add-e-gp-id-pe-admin-lged-holder').css('display', 'none');
        if ($.inArray("Other", array) !== -1) $('#add-e-gp-id-govt-lged-holder').css('display', 'block');
        else $('#add-e-gp-id-govt-lged-holder').css('display', 'none');
    });

    $('select[name="procurement_roles_lgis"]').on('change', function () {
        let object = $(this).find('option:selected');
        let array = [];
        for (var i = 0; i < object.length; i++) {
            let innerText = object[i].innerText;
            if (innerText !== "Organization Admin" && innerText !== "PE Admin" && innerText !== "Focal Point")
                innerText = "Other";
            array.push(innerText);
        }
        if ($.inArray("Organization Admin", array) !== -1) $('#add-e-gp-id-org-admin-lgis-holder').css('display', 'block');
        else $('#add-e-gp-id-org-admin-lgis-holder').css('display', 'none');
        if ($.inArray("PE Admin", array) !== -1) $('#add-e-gp-id-pe-admin-lgis-holder').css('display', 'block');
        else $('#add-e-gp-id-pe-admin-lgis-holder').css('display', 'none');
        if ($.inArray("Other", array) !== -1) $('#add-e-gp-id-govt-lgis-holder').css('display', 'block');
        else $('#add-e-gp-id-govt-lgis-holder').css('display', 'none');
    });
    $('select[name="update_procurement_roles"]').on('change', function () {
        let object = $(this).find('option:selected');
        let array = [];
        for (var i = 0; i < object.length; i++) {
            let innerText = object[i].innerText;
            if (innerText !== "Organization Admin" && innerText !== "PE Admin" && innerText !== "Focal Point")
                innerText = "Other";
            array.push(innerText);
        }
        if ($.inArray("Organization Admin", array) !== -1) $('#update-e-gp-id-org-admin-lged-holder').css('display', 'block');
        else $('#update-e-gp-id-org-admin-lged-holder').css('display', 'none');
        if ($.inArray("PE Admin", array) !== -1) $('#update-e-gp-id-pe-admin-lged-holder').css('display', 'block');
        else $('#update-e-gp-id-pe-admin-lged-holder').css('display', 'none');
        if ($.inArray("Other", array) !== -1) $('#update-e-gp-id-govt-lged-holder').css('display', 'block');
        else $('#update-e-gp-id-govt-lged-holder').css('display', 'none');
    });

    $('select[name="update_procurement_roles_lgis"]').on('change', function () {
        let object = $(this).find('option:selected');
        let array = [];
        for (var i = 0; i < object.length; i++) {
            let innerText = object[i].innerText;
            if (innerText !== "Organization Admin" && innerText !== "PE Admin" && innerText !== "Focal Point")
                innerText = "Other";
            array.push(innerText);
        }
        if ($.inArray("Organization Admin", array) !== -1) $('#update-e-gp-id-org-admin-lgis-holder').css('display', 'block');
        else $('#update-e-gp-id-org-admin-lgis-holder').css('display', 'none');
        if ($.inArray("PE Admin", array) !== -1) $('#update-e-gp-id-pe-admin-lgis-holder').css('display', 'block');
        else $('#update-e-gp-id-pe-admin-lgis-holder').css('display', 'none');
        if ($.inArray("Other", array) !== -1) $('#update-e-gp-id-govt-lgis-holder').css('display', 'block');
        else $('#update-e-gp-id-govt-lgis-holder').css('display', 'none');
    });

    $('.select2').select2();
    $('.date').datepicker({
        autoclose: true,
        format: 'dd-mm-yyyy',
        todayHighlight: true
    });
    $('#user-column-customization-btn').on('click', function () {
        $('#column-customization-modal').modal('toggle');
        $('#column-customization-modal-body').html('');
        let columnCustomizationCallback = callAjax('/lged/api/v1/column-customization/', 'GET', '');
        columnCustomizationCallback.done(function (data) {
            $.each(data, function (k, v) {
                let temp = column_customization_form.replace('column-customization-form', 'column-customization-form' + (k + 1));
                $('#column-customization-modal-body').append(temp);
                $('.select2').select2();
                $('#column-customization-form' + (k + 1) + ' input[name="pk"]').val(v['id']);
                $('#column-customization-form' + (k + 1) + ' input[name="report_for"]').val(v['report_for']);
                $('#column-customization-form' + (k + 1) + ' select[name="columns"]').val(v['columns']).trigger('change.select2');
            });
            let temp = column_customization_form.replace('column-customization-form', 'column-customization-form' + (data.length + 1));
            $('#column-customization-modal-body').append(temp);
            $('#column-customization-form' + (data.length + 1) + ' input[name="pk"]').val("-1");
            $('.select2').select2();
        });
    });
    let jsonCallback = callAjax('/lged/api/v1/resource/center/', "GET", '');
    jsonCallback.done(function (data) {
        // console.log('first', data);
        let indices = [];
        $.each(data, function (k, v) {
            // console.log(v);
            if (v["name"] === "BIMS" || v["name"] === "ESCB") {
            } else {
                indices.push(k);
            }
        });
        for (var i = indices.length - 1; i >= 0; i--) {
            data.splice(indices[i], 1);
        }
        // console.log('second', data);
        commonSetDropDownWithJson(data, 'venue_update', 'name', 'id');
        commonSetDropDownWithJson(data, 'venue_add', 'name', 'id');
    });
    // commonSetDropDownWithID('/lged/api/v1/resource/center/', 'venue_update', 'name', 'id');
    // commonSetDropDownWithID('/lged/api/v1/resource/center/', 'venue_add', 'name', 'id');
    $('#updated_at_from').datepicker({
        autoclose: true,
        format: 'dd-mm-yyyy',
        todayHighlight: true
    });
    $('#date_of_birth_add').datepicker({
        autoclose: true,
        format: 'dd-mm-yyyy',
        todayHighlight: true,
        clearBtn: true,
    });
    $('#date_of_birth_update').datepicker({
        autoclose: true,
        format: 'dd-mm-yyyy',
        todayHighlight: true,
        clearBtn: true,
    });
    $('#updated_at_to').datepicker({
        autoclose: true,
        format: 'dd-mm-yyyy',
        todayHighlight: true
    });
    let select1 = $("select[name='gender']");
    select1.select2({
        allowClear: true,
    });
    if (user_type === 'admin') {
        $("#admin-user").addClass('active');
    } else if (govt_flag === 1) {
        $("#other-user").addClass('active');
    } else if (user_type === 'focal_point') {
        $("#focal-point-user").addClass('active');
    } else if (user_type === 'all') {
        $("#all-user").addClass('active');
    } else if (user_type === 'floating') {
        $("#floating-user").addClass('active');
    }

    // if (user_type === 'admin') {
    //     var table = set_user_list_table('/lged/api/v1/users/?imp_user=admin', office_name);
    // } else if (user_type === 'other') {
    //     var table = set_user_list_table('/lged/api/v1/users/?imp_user=other', office_name);
    // } else if (user_type === 'focal_point') {
    //     var table = set_user_list_table('/lged/api/v1/users/?imp_user=focal_point', office_name);
    // } else if (user_type === 'all') {
    //     var table = set_user_list_table('/lged/api/v1/users/?imp_user=all', office_name);
    // }
    if (transfer) var table = set_user_list_table(crud_api + '?transfer=1&imp_user=' + user_type, office_name, user_type, office_category, organization, admin_user);
    else var table = set_user_list_table(crud_api + '?imp_user=' + user_type, office_name, user_type, office_category, organization, admin_user);

    if (transfer) var table2 = set_user_list_temp_office_table(temp_api + '?imp_user=' + user_type + '&office_id=' + logged_in_office, office_name, user_type, office_category, organization, admin_user);
    else var table2 = set_user_list_temp_office_table(temp_api + '?imp_user=' + user_type + '&office_id=' + logged_in_office, office_name, user_type, office_category, organization, admin_user);

    function load_report_options() {
        let columnCustomizationCallback = callAjax('/lged/api/v1/column-customization/', 'GET', '');
        columnCustomizationCallback.done(function (data) {
            var select = $("#user_report");
            if (select.prop) {
                var options = select.prop('options');
            } else {
                var options = select.attr('options');
            }
            $('option', select).remove();
            options[options.length] = new Option("-Select Option-", "");
            $.each(data, function (k, v) {
                // new $.fn.dataTable.Buttons( table, {
                //     name: 'commands',
                //     buttons: [
                //         {
                //             extend: 'print',
                //             exportOptions: {
                //                 columns: v['columns']
                //             },
                //             header: true,
                //             title: "",
                //             messageTop: "<span class='print-table-header'>Office Name: " + office_name + "</span><br>" +
                //                     "<span class='print-table-header'>Table Name: User</span><br>" +
                //                     "<span class='print-table-header'>Date : " + new Date().toJSON().slice(0, 10).replace(/-/g, '/') + "</span><br>",
                //             text: 'Report for ' + v['report_for'],
                //             className: 'btn btn-sm btn-default'
                //         },
                //     ]
                // } );
                // table.buttons( 0, null ).containers().appendTo( 'body #toggle_column_list' );
                options[options.length] = new Option(v['report_for'], v['columns']);
            });
        });
    }

    if (admin_user) load_report_options();

    $('#user_report').on('change', function () {
        var columns = table.columns().visible(false);
        columns = table.columns($(this).val());
        columns.visible(true);
        let arr = $(this).val().split(',');
        $('a.toggle-vis').toggleClass('custom-toggle-hide-btn');
        // $('a.toggle-vis').removeClass('custom-toggle-btn');
        for (var i = 0; i < arr.length; i++) {
            // console.log($('[data-column=' + arr[i] + ']'));
            $('[data-column=' + arr[i] + ']').addClass('custom-toggle-btn');
            $('[data-column=' + arr[i] + ']').removeClass('custom-toggle-hide-btn');
        }
        //
    });

    $(document).on('hidden.bs.modal', '#column-customization-modal', function () {
        load_report_options();
    });
    if (!admin_user) {
        // var imp_table = set_imp_user_list_table('/lged/api/v1/users/?imp_user=focal_point');
        table.buttons(['.buttons-csv',]).remove();
        // imp_table.buttons(['.buttons-csv',]).remove();
        // $(".imp_user_table_holder").css("margin-bottom", "30px");
        $(".imp_user_table_holder").css('display', 'none');
    }
    // if (office_category !== 'LGED HQ' && user_type === 'admin') {
    //     $("#user-list-table-holder").css('display', 'none');
    // } else if (office_category !== "LGED HQ" && user_type === 'other') {
    //     $(".imp_user_table_holder").css('display', 'none');
    // } else if (office_category !== "LGED HQ" && user_type === 'focal_point') {
    //     $("#user-list-table-holder").css('display', 'none');
    // }


    $('a.toggle-vis').on('click', function (e) {
        e.preventDefault();

        // Get the column API object
        var column = table.column($(this).attr('data-column'));
        $(this).toggleClass('custom-toggle-hide-btn');

        // Toggle the visibility
        column.visible(!column.visible());
    });
    if (!admin_user) {
        let hide_arr = [1, 2, 3, 4, 5];
        for (var col in hide_arr) {
            let column = table.column(hide_arr[col]);
            column.visible(!column.visible());
        }
        // for (var col in hide_arr) {
        //     let column = imp_table.column(hide_arr[col]);
        //     column.visible(!column.visible());
        // }
    }
    if (!admin_user) {
        let hide_arr = [1, 2, 3, 4, 5];
        for (var col in hide_arr) {
            let column = table2.column(hide_arr[col]);
            column.visible(!column.visible());
            console.log('test')
        }

    }

    $('#user_list_table').on('click', 'tbody tr', function () {
        $(".row-selected").removeClass("row-selected");
        $(".disabled").removeClass("disabled");
        var row_data = table.row(this).data();
        var id_selector = "#" + row_data ['id'];
        $(id_selector).addClass("row-selected");
    });
    $('#user_list_temp_office_table').on('click', 'tbody tr', function () {
        $(".row-selected").removeClass("row-selected");
        $(".disabled").removeClass("disabled");
        var row_data = table2.row(this).data();
        var id_selector = "#" + row_data ['id'];
        $(id_selector).addClass("row-selected");
    });

    $('#imp_user_list_table').on('click', 'tbody tr', function () {
        $(".row-selected").removeClass("row-selected");
        $(".disabled").removeClass("disabled");
        var row_data = imp_table.row(this).data();
        console.log(row_data);
        var id_selector = "#" + row_data ['id'];
        $(id_selector).addClass("row-selected");
        console.log($(".row-selected")[0].id);
    });

    $('#confirm-del-btn').on('click', function () {
        console.log("del" + $(".row-selected")[0].id);
        var id = $(".row-selected")[0].id;
        $('.confirm-delete-input-modal').modal('toggle');
        $.ajax({
            method: "DELETE",
            url: crud_api + id,
            data: JSON.stringify({
                user: id,
            }),
            contentType: "application/json; charset=utf-8",
            success: function (data) {
                notify("User removed successfully", 'success');
                table.ajax.url(crud_api + '?imp_user=' + user_type).load();
                // imp_table.ajax.url('/lged/api/v1/users/?imp_user=' + user_type).load();

            },
            error: function (request, status, error) {
                console.log(request.responseJSON);
                var message = "";

                if (request.status === 400) {

                    $.each(request.responseJSON, function (index, value) {
                        message += value[0];
                    });

                    notify(message, 'danger')
                }
            }
        });
    });
    $('#cancel-del-btn').on('click', function () {
        $('.confirm-delete-input-modal').modal('toggle');
    });

    $('#confirm-del-additional-user-btn').on('click', function () {
        console.log("del" + $(".row-selected")[0].id);
        var id = $(".row-selected")[0].id;
        $('#additional-user-delete-modal').modal('toggle');
        $.ajax({
            method: "DELETE",
            url: temp_api + id,
            data: JSON.stringify({
                user: id,
            }),
            contentType: "application/json; charset=utf-8",
            success: function (data) {
                notify("Additional user removed successfully", 'success');
                if (user_type) {
                    table2.ajax.url(temp_api + '?imp_user=' + user_type).load();
                    table.ajax.url(crud_api + '?imp_user=' + user_type).load();
                    location.reload();
                }

                // imp_table.ajax.url('/lged/api/v1/users/?imp_user=' + user_type).load();

            },
            error: function (request, status, error) {
                console.log(request.responseJSON);

                var message = "";

                if (request.status === 400) {

                    $.each(request.responseJSON, function (index, value) {
                        message += value[0];
                    });

                    notify(message, 'danger')
                }
            }
        });
    });
    $('#cancel-del-additional-user-btn').on('click', function () {
        $('#additional-user-delete-modal').modal('toggle');
    });


    $('#reset_filter').on('click', function () {
        $('.select2').val('').trigger('change.select2');
        $('input').val('');
    });
    $('#user-add-btn').on('click', function () {
        $('#user-add-modal').modal('toggle');
        $('#add-user-form')[0].reset();
        $("select[name='designation']").val('').trigger('change.select2');
        $("select[name='gender']").val('').trigger('change.select2');
        $("input[name='date_of_birth']").val('');
        $("select[name='procurement_roles']").val('').trigger('change.select2');
        $("select[name='office']").val(logged_in_office).trigger('change.select2');
    });
    $('#floating-user-btn').on('click', function () {
        // table.ajax.url(crud_api + '?floating=true').load();
        window.location = '/lged/users/floating';
    });

    $('#user-transfer-to-another-office-btn').on('click', function () {
        let id = $(".row-selected")[0].id || 1;

        let jsonCallBack = callAjax('/lged/api/v1/users/' + id + '/?fields=id,floating', 'GET', "");
        jsonCallBack.done(function (data) {
            // console.log('ashiq'+ ' '+ data);
            if (data['floating']) notify('Transfer of this user is awaiting admin approval', 'success');
            else window.location = '/lged/transfer/user/?id=' + id;
        });
        jsonCallBack.fail(function (request) {
            showError(request)
        });
        // let data = callAjax('/lged/api/v1/users/' + id + '/?fields=id,floating');
        // console.log('ashiq', data);
        // window.location = '/lged/transfer/user/?id=' + id;
    });

    $('#user-multi-assign-to-other-office-btn').on('click', function () {

        let id = $(".row-selected")[0].id || 1;
        //console.log(id)
        let jsonCallBack = callAjax('/lged/api/v1/users/' + id + '/?fields=id,floating', 'GET', "");
        jsonCallBack.done(function (data) {
            // console.log('ashiq'+ ' '+ data);
            if (data['floating']) notify('Multiple assigning of this user is awaiting admin approval', 'success');
            else window.location = '/lged/multi_assign/user/?id=' + id;
        });
        jsonCallBack.fail(function (request) {
            showError(request)
        });
    });

    // $('#search-table-for-transfer').on('click', 'tbody tr', function () {
    //     $(".row-selected").removeClass("row-selected");
    //     $(".disabled").removeClass("disabled");
    //     var row_data = table.row(this).data();
    //     var id_selector = "#" + row_data ['id'];
    //     $(id_selector).addClass("row-selected");
    //     console.log($(".row-selected")[0].id);
    // });

    var search_table_for_transfer;
    $('#user-transfer-here-btn').on('click', function () {
        $('#date_of_birth_search').datepicker({
            autoclose: true,
            format: 'yyyy-mm-dd',
            todayHighlight: true,
            allowClear: true,
        });
        if (!transfer) {
            $('#user-transfer-modal').modal('toggle');
            search_table_for_transfer = setSearchTableForTransfer('/lged/api/v1/users/?date_of_birth=1900-12-12');
            // $(this).addClass('disabled');
            // window.location = '/lged/users/all/?transfer=1';
        }
        $('#transfer-here-btn').on('click', function () {
            let user_id = $("#search-table-for-transfer").closest('table').find('tbody tr:first').attr('id');
            if (user_id) window.location = '/lged/transfer/user/?id=' + user_id + '&to=1';
        });
        $("#date_of_birth_search, #nid_search, #mobile_no_search").change(function () {
            let date_of_birth = $("#date_of_birth_search").val();
            let nid = $("#nid_search").val();
            let mobile_no = $("#mobile_no_search").val();
            let params = "";
            params += "?transfer=1&";
            params += "date_of_birth=" + date_of_birth;
            params += "&nid=" + nid;
            params += "&mobile_no=" + mobile_no;
            search_table_for_transfer.ajax.url('/lged/api/v1/users/' + params).load();
        });
    });
    if (window.location.href.split('?').pop().split('&')[0] === 'from_transfer_update') {
        row_selected_id = parseInt(window.location.href.split('?').pop().split('&')[1]);
        user_edit_btn_click(row_selected_id);
    } else if (isNaN(window.location.href.split('?').pop()) === false) {
        row_selected_id = parseInt(window.location.href.split('?').pop());
        user_edit_btn_click(row_selected_id);
    }

    function user_edit_btn_click(id) {
        let userCallBack = callAjax(crud_api + id, 'GET', "");
        userCallBack.done(function (data) {
            $("#designation_name").html(data['designation_name']);
            if (data['floating'] === true) {
                notify("Floating users can't be updated", 'success');
                return;
            }
            console.log()
            if (data['designation_name'] === 'Mayor' || data['designation_name'] ===  'Secretary' || data['designation_name'] ===  'Chief Executive Officer' || data['designation_name'] ===  'Chairman (Zila Parishad)' || data['designation_name'] ===  'Chairman (Upazila Parishad)' || data['designation_name'] ===  'Upazila Nirbahi Officer' || data['designation_name'] ===  'Accountant' || data['designation_name'] === 'Administrative Officer') {
                $('#proc-role-div').css('display', 'none');
                $('#date_of_birth_edit').css('display', 'none');
                $('#date_of_birth_edit').removeClass('required_field');
                $('#date_of_birth_edit input').attr('data-parsley-required', 'false');


            }

            $('#user-update-modal').modal('toggle');
            update_user_office_id = data['office_id'];
            // console.log('user off ================= ', update_user_office_id);
            if (admin_user) {

                $('input[name="nid"]').attr('data-parsley-required', false);
                $('select[name="gender"]').attr('data-parsley-required', false);
                $('input[name="date_of_birth"]').attr('data-parsley-required', false);
                $('input[name="mobile_no"]').attr('data-parsley-required', false);
                $('input[name="PPR_training"]').attr('required', false);


                $('.form-group').each(function () {
                    if($(this).hasClass('required_field')){
                        $(this).removeClass('required_field');
                    }
                });
                $('#update_user_org').val(data['organization']).trigger('change');
                if (data['office_category'] !== 'e-GP LAB OFFICES') $('#update_user_off_cat').val(data['office_category']).trigger('change');
                // else $('#update_user_off_cat').val('').trigger('change');
                else {
                    $('#update_user_off_cat').val('').trigger('change.select2');
                    setTimeout(function () {
                        $('#update_user_office').val(update_user_office_id).trigger('change.select2');
                    }, 1000);
                }
            } else {
                check_for_duplicate_proc_role(update_user_office_id);
            }

            if (!admin_user) {
                $('#proc-role-div select').attr('readonly', true);
            }

            $('input[type="file"]').val('');
            $('input[name="first_name"]').val(data['first_name']);
            $('input[name="bengali_name"]').val(data['bengali_name']);
            if (data['official_email']) $('input[name="official_email"]').val(data['official_email']);
            $('#fixed-off-email').val(data['official_email']);
            if (data['email']) $('input[name="email"]').val(data['email']);
            if (admin_user || !data['official_email']) {
                $("#fixed-off-email").attr("readonly", false);
                $("#fixed-off-email").removeClass('fixed-form');
                $(".fixed-user-div").css('display', 'none');
            } else {
                // $("#fixed-off-email").attr("readonly", true);
                $("#fixed-off-email").attr("readonly", false);
                $("#fixed-off-email").removeClass('fixed-form');
            }
            $('input[name="personal_email"]').val(data['personal_email']);
            $('input[name="mobile_no"]').val(data['personal_mobile_no']);
            $('input[name="official_mobile_no"]').val(data['profile_official_mobile_no']);
            $('input[name="nid"]').val(data['nid_value']);
            if (data['PPR_training'] === 'Yes') {
                if (user_type === 'focal_point' && !admin_user) {
                    $('input[id="yes_update"]').attr('checked', true);
                    $('input[id="yes_update"]').prop('checked', 'checked');
                } else {
                    $('input[id="yes_update"]').attr('checked', true).trigger('change');
                    $('input[id="yes_update"]').prop('checked', 'checked').trigger('change');
                }
                $('input[name="start_date"]').val(data['training_start_date']).datepicker('update', new Date(data['training_start_date']));
                $('#venue_update').val(data['training_venue']).trigger('change.select2');
                // $('input[id="no_update"]').attr('checked', false).trigger('change');

            } else if (data['PPR_training'] === 'No') {
                $('input[id="no_update"]').attr('checked', true).trigger('change');
                $('input[id="no_update"]').prop('checked', 'checked').trigger('change');
                $('input[name="start_date"]').val('');
                $('#venue_update').val('').trigger('change.select2');
                // $('input[id="yes_update"]').attr('checked', false).trigger('change');
            } else {
                $('input[id="no_update"]').attr('checked', true).trigger('change');
                // $('input[id="yes_update"]').attr('checked', false).trigger('change');
                $('input[id="no_update"]').attr('checked', false);
                $('input[name="start_date"]').val('');
                $('#venue_update').val('').trigger('change.select2');
            }
            // $('input[name="e_gp_user_id"]').val(data['e_gp_user_id_value']);
            $('#lged-e-gp-id').html(data['e_gp_user_id_value']);
            $('#lgi-e-gp-id').html(data['e_gp_user_id_lgis_value']);
            $('#e_gp_user_id_govt_for_update').val(data['e_gp_user_id_for_govt']);
            $('#e_gp_user_id_org_admin_for_update').val(data['e_gp_user_id_for_org_admin']);
            $('#e_gp_user_id_pe_admin_for_update').val(data['e_gp_user_id_for_pe_admin']);
            $('#e_gp_user_id_govt_lgis_for_update').val(data['e_gp_user_id_lgis_for_govt']);
            $('#e_gp_user_id_org_admin_lgis_for_update').val(data['e_gp_user_id_lgis_for_org_admin']);
            $('#e_gp_user_id_pe_admin_lgis_for_update').val(data['e_gp_user_id_lgis_for_pe_admin']);

            // $('input[id="e_gp_user_id_lgis_for_update"]').val(data['e_gp_user_id_lgis_value']);
            // $('input[id="e_gp_user_id_for_update"]').val(data['e_gp_user_id_value']);

            var role_arr_str = "";
            $.each(data['procurement_role_list'], function (index, value) {
                role_arr_str += value['role'] + ", ";
            });
            $('#lged-proc-role').html(role_arr_str);
            //    ------------- lgis --------------
            var role_arr_lgis_str = "";
            $.each(data['procurement_role_list_lgis'], function (index, value) {
                role_arr_lgis_str += value['role'] + ", ";
            });
            $('#lgi-proc-role').html(role_arr_lgis_str);


            // $("select[name='designation']").val(data['designation_id']).trigger('change.select2');
            // designation_url = '/lged/api/v1/designation/?office_category=' + data['office_category'];
            designation_url = '/lged/api/v1/designation/';
            commonSetDropDownAndSet(designation_url, $('select[name="designation"]'), 'designation', 'id', '-Select Option-',
                'elem', data['designation_id']);
            if (data['date_of_birth'] === null || data['date_of_birth'] === '') {
                $('#date_of_birth_update').val('');
            } else {
                // let date_of_birth = moment(data['date_of_birth'], "YYYY-MM-DD").format('DD-MM-YYYY');
                // $("#date_of_birth_update").val(date_of_birth).trigger('change.select2');
                $("#date_of_birth_update").datepicker('update', new Date(data['date_of_birth']));
            }
            $("select[name='gender']").val(data['gender']).trigger('change.select2');

            if (admin_user) {
                $("select[name='update_designation']").val(data['designation_id']).trigger('change.select2');
            }
            let flag = 0;
            if (bool_data.proc_role_lged) {
                var role_arr = [];
                $.each(data['procurement_role_list'], function (index, value) {
                    role_arr.push(value['id']);
                    if (!admin_user && value['role'] === 'Focal Point') $('c').attr('readonly', false);
                    if (value['role'] === 'Focal Point') {
                        flag = 1;
                    }
                    // if (value['role'] === 'Focal Point') $('#official_email_label_update').text('User ID for Pro Info');
                });
                $("select[name='update_procurement_roles']").val(role_arr).trigger('change.select2').trigger('change');
            }
            if (bool_data.proc_role_lgi) {
                var role_arr_lgis = [];
                $("#update-proc-role-lgi-holder").css('display', 'block');
                $("#update-e-gp-id-lgi-holder").css('display', 'block');
                $.each(data['procurement_role_list_lgis'], function (index, value) {
                    // if (office_category !== 'LGED HQ' && (value['role'] === 'Focal Point' || value['role'] === 'Organization Admin' || value['role'] === 'PE Admin')) {
                    //     $("#update-proc-role-lgi-holder").css('display', 'none');
                    //     $("#update-e-gp-id-lgi-holder").css('display', 'none');
                    // }
                    role_arr_lgis.push(value['id']);
                    //Tarif_Updated
                    // if (!admin_user && value['role'] === 'Focal Point') $('select[name="designation"]').attr('readonly', false);
                    //**
                    if (value['role'] === 'Focal Point') {
                        flag = 1;
                    }
                    // if (value['role'] === 'Focal Point') $('#official_email_label_update').text('User ID for Pro Info');
                });
                $("select[name='update_procurement_roles_lgis']").val(role_arr_lgis).trigger('change.select2').trigger('change');
            }
            if (flag === 2) {
                $('#nid_edit').css('display', 'none');
                $('#nid_edit').removeClass('required_field');
                $('#nid_edit input').attr('data-parsley-required', 'false');
                $('#date_of_birth_edit').css('display', 'none');
                $('#date_of_birth_edit').removeClass('required_field');
                $('#date_of_birth_edit input').attr('data-parsley-required', 'false');
            }
            else if(data['designation_name'] === 'Mayor' || data['designation_name'] ===  'Secretary' || data['designation_name'] ===  'Chief Executive Officer' || data['designation_name'] ===  'Chairman (Zila Parishad)' || data['designation_name'] ===  'Chairman (Upazila Parishad)' || data['designation_name'] ===  'Upazila Nirbahi Officer' || data['designation_name'] ===  'Accountant' || data['designation_name'] === 'Administrative Officer'){
                    $('#nid_edit').css('display', 'none');
                    $('#nid_edit').removeClass('required_field');
                    $('#nid_edit input').attr('data-parsley-required', 'false');
            }
            else {
                $('#nid_edit').css('display', 'block');
                if(!admin_user){
                       $('#nid_edit').addClass('required_field');
                       $('#nid_edit input').attr('data-parsley-required', 'true');
                }
            }
            if (flag === 2) {
                $('#ppr_training_div_update').css('display', 'none');
                $('input[id="no_update"]').attr('checked', true).trigger('change');
                $('input[id="no_update"]').prop('checked', 'checked').trigger('change');
            } else {
                if (data['designation_name'] === 'Mayor' || data['designation_name'] ===  'Secretary' || data['designation_name'] ===  'Chief Executive Officer' || data['designation_name'] ===  'Chairman (Zila Parishad)' || data['designation_name'] ===  'Chairman (Upazila Parishad)' || data['designation_name'] ===  'Upazila Nirbahi Officer' || data['designation_name'] ===  'Accountant' || data['designation_name'] === 'Administrative Officer') {
                    $('#ppr_training_div_update').css('display', 'none');
                    $('input[id="no_update"]').attr('checked', true).trigger('change');
                    $('input[id="no_update"]').prop('checked', 'checked').trigger('change');
                }
                else {
                    $('#ppr_training_div_update').css('display', 'block');
                }
            }

        });
        userCallBack.fail(function (request) {
            showError(request);
        });
    }

    $('#user-edit-btn').on('click', function () {
        let id = $(".row-selected")[0].id || 1;
        console.log('user id ===== ======= ', id);
        user_edit_btn_click(id);
    });

    $('#user-role-btn').on('click', function () {
        $('#assign-role-modal').modal('toggle');
        let id = $(".row-selected")[0].id || 1;
        let userRoleCallback = callAjax(crud_api + id + '?fields=role', 'GET', '');
        userRoleCallback.done(function (data) {
            $('#selected_role').val(data['role']).trigger('change.select2');
        });
    });

    $(document).on('click', '.role_assign', function () {
        let id = $(".row-selected")[0].id || 1;
        let jsonData = {};
        jsonData['role'] = $('select[name="role"]').val();
        $.ajax({
            method: 'PATCH',
            url: crud_api + id + '/',
            data: JSON.stringify(jsonData),
            contentType: "application/json",
            success: function (data) {
                $('#assign-role-modal').modal('toggle');
                notify('Role assigned successfully', 'success');
            },
            error: function (request, status, error) {
                notify(request.responseText, 'danger');
            }
        });
    });


    // $('#column-customization-reset-btn').on('click', function () {
    //     let form = this.form.id;
    //     console.log(form);
    //     $("select[name='columns']").val('').trigger('change.select2');
    // });
    $('#update-user-reset-btn').on('click', function () {
        $('#update-profile-form')[0].reset();
        $("#update_user_org").val('').trigger('change.select2');
        $("#update_user_off_cat").val('').trigger('change.select2');
        $("select[name='update_user_office']").val('').trigger('change.select2');
        $("select[name='designation']").val('').trigger('change.select2');
        $("select[name='update_procurement_roles']").val([]).trigger('change.select2');
        $("select[name='update_procurement_roles_lgis']").val([]).trigger('change.select2');
        $("select[name='gender']").val('').trigger('change.select2');
        $("#no_update").prop('checked', true).trigger('change');
        $("#yes_update").prop('checked', false);
    });

    $('#add-user-reset-btn').on('click', function () {
        $('#add-user-form')[0].reset();
        $("#add_user_org").val('').trigger('change.select2');
        $("#add_user_off_cat").val('').trigger('change.select2');
        $("select[name='add_user_office']").val('').trigger('change.select2');
        $("select[name='add_designation']").val('').trigger('change.select2');
        $("select[name='procurement_roles']").val([]).trigger('change.select2');
        $("select[name='procurement_roles_lgis']").val([]).trigger('change.select2');
        $("select[name='gender']").val('').trigger('change.select2');
        $("input[name='date_of_birth']").val('');
        $("#no").prop('checked', true).trigger('change');
        $("#yes").prop('checked', false);
    });
    /*
    $("#updated_at_from , #updated_at_to").change(function () {

        let updated_at_from = $("#updated_at_from").val();
        let updated_at_to = $("#updated_at_to").val();
        //console.log(updated_at_from);
        //console.log(updated_at_to);

        let params = "";
        if (updated_at_from !== "") params += "updated_at_from=" + updated_at_from + '&';
        if (updated_at_to !== "") params += "updated_at_to=" + updated_at_to + '&';

        table.ajax.url('/lged/api/v1/users/?' + params).load();

        //console.log(params);

    });*/

    $(document).on('click', '.column-customization-submit-btn', function () {
        let form_id = $(this).closest('form').attr('id');
        // console.log(form_id);
        let form_valid = $('#' + form_id).parsley();
        form_valid.validate();
        if (!form_valid.isValid()) {
            return false;
        }
        let jsonData = {}, method = "POST", url = "/lged/api/v1/column-customization/";
        // console.log($("#" + form_id + " input[name='pk']").val());
        if ($("#" + form_id + " input[name='pk']").val() !== "-1") {
            method = "PATCH";
            jsonData["id"] = $("#" + form_id + " input[name='pk']").val();
            url = url + jsonData["id"] + '/';
        }
        jsonData['columns'] = $("#" + form_id + " select[name='columns']").val();
        jsonData['report_for'] = $("#" + form_id + " input[name='report_for']").val();
        console.log(jsonData);
        $.ajax({
            method: method,
            url: url,
            data: JSON.stringify(jsonData),
            contentType: "application/json",
            success: function (data) {
                // $("select[name='columns']").val('').trigger('change.select2');
                // $("input[name='report_for']").val('');
                notify('Report for ' + data['report_for'] + ' updated successfully', 'success');
                // $('#column-customization-modal').modal('toggle');
                // window.location.reload();
            },
            error: function (request, status, error) {
                notify(request.responseText, 'danger');
            }
        });
        return false;
    });

    $(document).on('click', '.column-customization-remove-btn', function () {
        let form_id = $(this).closest('form').attr('id');
        let jsonData = {}, method = "DELETE", url = "/lged/api/v1/column-customization/", id;
        if ($("#" + form_id + " input[name='pk']").val() !== "-1") {
            id = $("#" + form_id + " input[name='pk']").val();
            url = url + id + '/';
        } else {
            notify('Please select a valid row', 'danger');
        }
        $.ajax({
            method: method,
            url: url,
            data: jsonData,
            contentType: "application/json",
            success: function (data) {
                console.log(data);
                notify('Report for ' + id + ' removed successfully', 'success');
                // window.location.reload();
            },
            error: function (request, status, error) {
                notify(request.responseText, 'danger');
            }
        });
        return false;
    });


    // $('select[name="add_designation"]').on('change', function () {
    //             let add_designation = $('select[name="add_designation"]').val();
    //             console.log('add_designation ===== '+add_designation);
    //
    //         });


    $('#add-user-form').parsley().on('form:submit', function () {

        var x = $("#add-user-form").serializeArray();
        console.log('user data ========================= ', x);
        var formData = objectifyFormDataWithPRole(x);
        if (formData.get('PPR_training') === null){
            formData.set('PPR_training', 'False');
        }

        console.log('ppr ========== ', formData.get('PPR_training'));
        let designation = formData.get('add_designation');
        delete formData['add_designation'];
        formData.append('designation', designation);
        if (admin_user) {
            let office = formData.get('add_user_office');
            delete formData['add_user_office'];
            formData.append('office', office);
        }
        if (formData.get('procurement_role') === '' && formData.get('procurement_role_lgis') === '') {
            notify("You have to provide at least one procurement role", "danger");
            return false;
        }
        if (formData.get('email') === '') formData.delete('email');

        //     delete formData['validity'];
        // }
        //
        // let package_no = formData.get('package_no');
        // if (package_no === "Local Purchase") {
        //     formData.delete('package_no');
        //     formData.append('source_value', 'Local Purchase');

        var avatarInput = document.getElementById('avatar_for_insert');
        console.log(avatarInput);
        var avatar = avatarInput.files[0];
        if (avatar) {
            console.log(avatar.size / (1000 * 1000));
            let size = avatar.size / (1000 * 1000);
            console.log(avatar);
            console.log(size);
            if (size > 5) {
                console.log(size + " > " + 5);
                notify("Image size should be less than 5MB", "danger");
                return false;
            }
            if (avatar.type !== 'image/jpeg' && avatar.type !== 'image/png') {
                notify("Image type should be jpg or png", "danger");
                return false;
            }
            if (avatar) {
                formData.append('avatar', avatar);
            }
        }
        var certificateInput = document.getElementById('certificate_for_training');
        var certificate = certificateInput.files[0];
        if (certificate) {
            let size = certificate.size / (1000 * 1000);
            if (size > 2) {
                // console.log(size + " > " + 5);
                notify("Size should be less than 2MB", "danger");
                return false;
            }
            formData.append('certificate', certificate);
        }
        if (formData.get('date_of_birth') !== '') {
            formData.set('date_of_birth', moment(formData.get('date_of_birth'), "DD-MM-YYYY").format('YYYY-MM-DD'));
        } else formData.delete('date_of_birth');
        if (formData.get('start_date') !== '') {
            formData.set('start_date', moment(formData.get('start_date'), "DD-MM-YYYY").format('YYYY-MM-DD'));
        } else formData.delete('start_date');
        console.log('formdata === ', formData);

        $.ajax({
            method: 'POST',
            url: crud_api,
            data: formData,
            contentType: false,
            cache: false,
            processData: false,
            done: function (data) {

            },
            complete: function () {

            },
            success: function (data) {
                console.log('req response ====', data);
                $('#add-user-form')[0].reset();
                $("#add_user_org").val('').trigger('change.select2');
                $("#add_user_off_cat").val('').trigger('change.select2');
                $("select[name='add_user_office']").val('').trigger('change.select2');
                $("select[name='add_designation']").val('').trigger('change.select2');
                $("select[name='procurement_roles']").val([]).trigger('change.select2');
                $("select[name='procurement_roles_lgis']").val([]).trigger('change.select2');
                $("select[name='gender']").val('').trigger('change.select2');
                $("input[name='date_of_birth']").val('');
                $("#no").prop('checked', true).trigger('change');
                $("#yes").prop('checked', false);
                $('#user-add-modal').modal('toggle');
                notify("User added successfully", "success");
                table.ajax.url(crud_api + '?imp_user=' + user_type).load();
            },
            error: function (request, status, error) {
                // showError(request);
                notify(request.responseText, 'danger');
            }
        });



        //--------------
        // var x = $('#add-user-form').serializeArray();
        // console.log(x);
        // var jsonData = objectifyForm(x);
        // console.log(jsonData);
        //
        // $.ajax({
        //     method: 'POST',
        //     url: '/lged/api/v1/users/',
        //     data: JSON.stringify(jsonData),
        //     dataType: "json",
        //     contentType: "application/json; charset=utf-8",
        //     done: function (data) {
        //     },
        //     complete: function () {
        //     },
        //     success: function (data) {
        //         console.log('success');
        //         $('#add-user-form')[0].reset();
        //         $("select[name='designation']").val('').trigger('change.select2');
        //         $("select[name='procurement_roles']").val('').trigger('change.select2');
        //         $('#user-add-modal').modal('toggle');
        //         notify("User added successfully", "success");
        //         table.ajax.url('/lged/api/v1/users/').load();
        //     },
        //     error: function (request, status, error) {
        //         showError(request);
        //     }
        // });
        return false; // Don't submit form for this demo
    });



    $(document).on('click', '.profile_update', function (e) {
        e.preventDefault();
        let id;
        if ($(".row-selected")[0]) id = $(".row-selected")[0].id || 1;
        else id = row_selected_id;
        var x = $("#update-profile-form").serializeArray();
        let profile_update_parsley = $("#update-profile-form").parsley();
        profile_update_parsley.validate();
        // if (!profile_update_parsley.isValid() && !admin_user) {
        //     $('#proc-role-div select').attr('disabled', true);
        //     return false;
        // }
        // if ($('#proc-role-div select').attr('disabled') === 'disabled') {
        //     $('#proc-role-div select').attr('disabled', false);
        //     $('#proc-role-div select').attr('readonly', true);
        // }
        if (profile_update_parsley.isValid()) {
            var x = $("#update-profile-form").serializeArray();
            console.log('x ====== ', x);
            var formData = objectifyFormDataWithPRole(x);

            if (admin_user) {
                let office = formData.get('update_user_office');
                delete formData['update_user_office'];
                if (office !== '') formData.append('office', office);
            }
            // if (formData.get('official_email') === '') {
            //     formData.set('official_email', null);
            // }

            if (!bool_data.proc_role_lged) formData.delete('procurement_role');
            if (!bool_data.proc_role_lgi) formData.delete('procurement_role_lgis');
            if (formData.get('email') === '') formData.delete('email');

            var avatarInput = document.getElementById('avatar');
            var avatar = avatarInput.files[0];
            if (avatar) {
                let size = avatar.size / (1000 * 1000);
                if (size > 2) {
                    notify("Image size should be less than 2MB", "danger");
                    return false;
                }
                if (avatar.type !== 'image/jpeg' && avatar.type !== 'image/png') {
                    notify("Image type should be jpg or png", "danger");
                    return false;
                }
                if (avatar) {
                    formData.append('avatar', avatar);
                }
            }

            var certificateInput = document.getElementById('certificate_for_training_update');
            var certificate = certificateInput.files[0];
            if (certificate) {
                let size = certificate.size / (1000 * 1000);
                if (size > 2) {
                    notify("Size should be less than 2MB", "danger");
                    return false;
                }
                formData.append('certificate', certificate);
            }
            if (formData.get('date_of_birth') !== '') {
                formData.set('date_of_birth', moment(formData.get('date_of_birth'), "DD-MM-YYYY").format('YYYY-MM-DD'));
            } else {
                formData.delete('date_of_birth');
            }
            if (formData.get('start_date') !== '') {
                formData.set('start_date', moment(formData.get('start_date'), "DD-MM-YYYY").format('YYYY-MM-DD'));
            } else formData.delete('start_date');
            if (formData.get('procurement_role') === '' && formData.get('procurement_role_lgis') === '') {
                notify("You have to provide at least one procurement role", "danger");
                return false;
            }

            if (formData.get('pass_condition') === 'pass reset'){
                formData.append('password_reset', true);
            }
            else if (formData.get('pass_condition') === 'fully reset'){
                formData.append('stage', -1);
            }
            else {
                formData.delete('password');
            }

            console.log('formData === = ', formData);

            $.ajax({
                method: 'PATCH',
                url: crud_api + id + '/',
                data: formData,
                contentType: false,
                cache: false,
                processData: false,
                done: function (data) {

                },
                complete: function () {

                },
                success: function (data) {
                    notify("Profile has been updated successfully!", "success");
                    // table.ajax.url(crud_api + '?imp_user=' + user_type).load();

                    if(admin_user){
                        console.log('User Type ==== ===== '+ user_type+' , Admin' );
                        table.ajax.url(crud_api + '?' + paramglobe).load();
                    }
                    else {
                        console.log('User Type ==== ===== '+ user_type+' , not Admin' );
                        table.ajax.url(crud_api + '?imp_user=' + user_type).load();
                    }




                    let temp = {'id': id};
                    callAjax('/lged/api/v1/change/stage/', 'POST', temp);


                    // if (!admin_user) {
                    //     $('#proc-role-div select').attr('readonly', true);
                    // }
                    $('#user-update-modal').modal('toggle');

                },
                error: function (request, status, error) {
                    // showError(request);
                    // if (!admin_user) {
                    //     $('#proc-role-div select').attr('readonly', true);
                    // }
                    notify(request.responseJSON["message"][0], 'danger');
                }
            });
            return false;
        }
        return false;
    });


    // $('#transfer-user-form').parsley().on('form:submit', function () {
    //
    //     // return false;
    //     var x = $('#transfer-user-form').serializeArray();
    //     console.log(x);
    //     var jsonData = commonObjectifyForm(x);
    //     console.log(jsonData);
    //
    //     let jsonCallBack = callAjax('/lged/api/v1/transfer/history/', 'POST', jsonData);
    //     jsonCallBack.done(function (data) {
    //         console.log(data);
    //         $('#user-transfer-modal').modal('toggle');
    //         notify("User was successfully transferred!", 'success');
    //         table.ajax.url(crud_api).load();
    //     });
    //     jsonCallBack.fail(function (request) {
    //         showError(request);
    //     });
    //     return false; // Don't submit form for this demo
    // });

    // $.ajax({
    //     method: 'GET',
    //     url: '/lged/api/v1/designation/',
    //     data: "",
    //     dataType: "json",
    //     contentType: "application/json; charset=utf-8",
    //     done: function (data) {
    //     },
    //     complete: function () {
    //     },
    //     success: function (data) {
    //         var select = $("select[name='designation']");
    //         var select_add = $("select[name='add_designation']");
    //         // if (office_category === 'LGED HQ') var update_select = $("select[name='update_designation']");
    //
    //         if (select.prop) {
    //             var options = select.prop('options');
    //         } else {
    //             var options = select.attr('options');
    //         }
    //         $('option', select).remove();
    //
    //
    //         if (select_add.prop) {
    //             var options_add = select_add.prop('options');
    //         } else {
    //             var options_add = select_add.attr('options');
    //         }
    //         $('option', select_add).remove();
    //
    //         //---
    //         // if (office_category === 'LGED HQ') {
    //         //     if (update_select.prop) {
    //         //         var update_options = update_select.prop('options');
    //         //     }
    //         //     else {
    //         //         var update_options = update_select.attr('options');
    //         //     }
    //         //     $('option', update_select).remove();
    //         // }
    //         //------
    //
    //         // options[options.length] = new Option("-Select Option-", "");
    //         options_add[options_add.length] = new Option("-Select Option-", "");
    //         // if (office_category === 'LGED HQ') update_options[update_options.length] = new Option("-Select Option-", "");
    //
    //         $.each(data, function (index, value) {
    //             // options[options.length] = new Option(value['short_form'], value['id']);
    //             options_add[options_add.length] = new Option(value['short_form'], value['id']);
    //             // if (office_category === 'LGED HQ') update_options[update_options.length] = new Option(value['designation'], value['id']);
    //         });
    //
    //     }
    // });

    $.ajax({
        method: 'GET',
        url: '/lged/api/v1/procurement/role/',
        data: "",
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        done: function (data) {
        },
        complete: function () {
        },
        success: function (data) {

            var select = $("select[name='procurement_roles']");
            var select_lgis = $("select[name='procurement_roles_lgis']");

            var update_select = $("select[name='update_procurement_roles']");
            var update_select_lgis = $("select[name='update_procurement_roles_lgis']");

            if (select.prop) {
                var options = select.prop('options');
            } else {
                var options = select.attr('options');
            }
            $('option', select).remove();

            //-----------lgis-----------
            if (select_lgis.prop) {
                var options_lgis = select_lgis.prop('options');
            } else {
                var options_lgis = select_lgis.attr('options');
            }
            $('option', select_lgis).remove();
            if (bool_data.proc_role_lged) {
                if (update_select.prop) {
                    var update_options = update_select.prop('options');
                } else {
                    var update_options = update_select.attr('options');
                }
                $('option', update_select).remove();
            }

            if (bool_data.proc_role_lgi) {
                //-----------lgis-----------
                if (select_lgis.prop) {
                    var update_options_lgis = update_select_lgis.prop('options');
                } else {
                    var update_options_lgis = update_select_lgis.attr('options');
                }
                $('option', update_select_lgis).remove();
                //-------------------------------
            }


            $.each(data, function (index, value) {

                options[options.length] = new Option(value['role'], value['id']);
                options_lgis[options_lgis.length] = new Option(value['role'], value['id']);
                //    ----------- Update -------------
                if (bool_data.proc_role_lged) update_options[update_options.length] = new Option(value['role'], value['id']);
                if (bool_data.proc_role_lgi) {
                    update_options_lgis[update_options_lgis.length] = new Option(value['role'], value['id']);
                }
                //    --------------------------------
            });
            // console.log('here ');
            // console.log($("select[name='procurement_roles_lgis'] option[value='1']"));
            // $("select[name='procurement_roles_lgis'] option[value=" + 1 + "]").remove();
            let jsonCallBack = callAjax(crud_api, 'GET', "");
            jsonCallBack.done(function (data) {
                let cur_lged_proc_role = [];
                let cur_lgi_proc_role = [];
                $.each(data, function (index, user) {
                    $.each(user['procurement_role_list'], function (index, role) {
                        // console.log(role);
                        cur_lged_proc_role.push(role);
                    });
                    $.each(user['procurement_role_list_lgis'], function (index, role) {
                        // console.log(role);
                        cur_lgi_proc_role.push(role);
                    });
                });
                // console.log(cur_lged_proc_role);
                // $.each(cur_lged_proc_role, function (index, value) {
                //     if (value.role === 'Hope' || value.role === 'Focal Point' || value.role === 'PE' || value.role === 'PE Admin' || value.role === 'Account Officer' || value.role === 'Organization Admin') {
                //         $("select[name='procurement_roles'] option[value=" + value.id + "]").remove();
                //     }
                // });
                // // console.log(cur_lgi_proc_role);
                // $.each(cur_lgi_proc_role, function (index, value) {
                //     if (value.role === 'Hope' || value.role === 'Focal Point' || value.role === 'PE' || value.role === 'PE Admin' || value.role === 'Account Officer' || value.role === 'Organization Admin') {
                //         $("select[name='procurement_roles_lgis'] option[value=" + value.id + "]").remove();
                //     }
                // });
            });
            jsonCallBack.fail(function (request) {
                showError(request)
            });

        }
    });

    if (admin_user) {

        commonSetDropDown('/lged/api/v1/designation/', 'designation_adv', 'designation', 'id', '-Select Option-');

        $("select[name='organization']").change(function () {
            var organization_id = $("select[name='organization']").val();
            changeOrganization(organization_id);
        });
        $("select[name='region']").change(function () {
            $("select[name='district']").val('').trigger('change.select2');
            let region = $("select[name='region']").val();

            let params = "";
            if (region !== "") params += "region=" + region + '&';

            commonSetDropDown('/lged/api/v1/district/?' + params, 'district', 'name', 'id', '-Select Option-');
        });

        $("select[name='organization'], select[name='office_category'], select[name='region'], select[name='district']").change(function () {
            $("select[name='office']").val('').trigger('change.select2');
            let organization = $("select[name='organization']").val();
            let office_category = $("select[name='office_category']").val();
            let region = $("select[name='region']").val();
            let district = $("select[name='district']").val();

            let params = "";
            if (organization !== "") params = "organization=" + organization + '&';
            if (office_category !== "") params += "office_category=" + office_category + '&';
            if (region !== "") params += "region=" + region + '&';
            if (district !== "") params += "district=" + district + '&';

            commonSetDropDown('/lged/api/v1/office/?' + params + 'fields=id,name&', 'office', 'name', 'id', '-Select Option-');
        });

        function filterUser() {
            console.log("Entered.....")
            let organization = $("select[name='organization']").val();
            let office_category = $("select[name='office_category']").val();
            let region = $("select[name='region']").val();
            let district = $("select[name='district']").val();
            let region_name = $("select[name='region'] :selected").text();
            let designation_name = $("select[name='designation_adv'] :selected").text();
            let district_name = $("select[name='district'] :selected").text();
            let office_name1 = $("select[name='office'] :selected").text();
            let office = $("select[name='office']").val();
            let designation_adv = $("select[name='designation_adv']").val();
            let gender_adv = $("select[name='gender_adv']").val();
            let ppr_training_adv = $("select[name='ppr_training_adv']").val();

            let name_adv = $("input[name='name_adv']").val();
            let bang_name_adv = $("input[name='bang_name_adv']").val();
            let mobile_no_adv = $("input[name='mobile_no_adv']").val();
            let off_mobile_no_adv = $("input[name='off_mobile_no_adv']").val();
            let email_adv = $("input[name='email_adv']").val();
            let off_email_adv = $("input[name='off_email_adv']").val();
            let nid_adv = $("input[name='nid_adv']").val();
            let e_gp_id_lged_adv = $("input[name='e_gp_id_lged_adv']").val();
            let e_gp_id_lgi_adv = $("input[name='e_gp_id_lgi_adv']").val();
            //let updated_at_from = $("#updated_at_from").val();
            //let updated_at_to = $("#updated_at_to").val();

            var date1 = $("#updated_at_from").val().split('-');
            var date2 = $("#updated_at_to").val().split('-');
            var updated_at_from = $("#updated_at_from").val();
            var updated_at_to = $("#updated_at_to").val();
            if (date1.length === 3) {
                updated_at_from = date1[2] + '-' + date1[1] + '-' + date1[0];
            }
            if (date2.length === 3) {
                updated_at_to = date2[2] + '-' + date2[1] + '-' + date2[0];
            }

            let params = "";
            if (organization !== "") params = "organization=" + organization + '&';
            if (office_category !== "") params += "office_category=" + office_category + '&';
            if (region !== "") params += "region=" + region + '&';
            if (district !== "") params += "district=" + district + '&';
            if (office !== "") params += "office=" + office + '&';

            if (designation_adv !== "") params += "designation_adv=" + designation_adv + '&';
            if (gender_adv !== "") params += "gender_adv=" + gender_adv + '&';
            if (ppr_training_adv !== "") params += "ppr_training_adv=" + ppr_training_adv + '&';
            if (name_adv !== "") params += "name_adv=" + name_adv + '&';
            if (bang_name_adv !== "") params += "bang_name_adv=" + bang_name_adv + '&';
            if (mobile_no_adv !== "") params += "mobile_no_adv=" + mobile_no_adv + '&';
            if (off_mobile_no_adv !== "") params += "off_mobile_no_adv=" + off_mobile_no_adv + '&';
            if (email_adv !== "") params += "email_adv=" + email_adv + '&';
            if (off_email_adv !== "") params += "off_email_adv=" + off_email_adv + '&';
            if (nid_adv !== "") params += "nid_adv=" + nid_adv + '&';
            if (e_gp_id_lged_adv !== "") params += "e_gp_id_lged_adv=" + e_gp_id_lged_adv + '&';
            if (e_gp_id_lgi_adv !== "") params += "e_gp_id_lgi_adv=" + e_gp_id_lgi_adv + '&';

            if (updated_at_from !== "") params += "updated_at_from=" + updated_at_from + '&';
            if (updated_at_to !== "") params += "updated_at_to=" + updated_at_to + '&';
            if (user_type === "admin") params += "imp_user=admin&";
            if (user_type === "other") params += "imp_user=other&";
            if (user_type === "focal_point") params += "imp_user=focal_point&";
            if (user_type === "all") params += "imp_user=all&";
            if (user_type === "floating") params += "imp_user=floating&";
            if (transfer) params += "transfer=1&";

            let par = params;
            par = par.replace('imp_user=', 'User Type=');
            par = par.replace(/-Select Option-/g, '');
            par = par.replace('region=' + region, 'region=' + region_name);
            par = par.replace('district=' + district, 'district=' + district_name);
            par = par.replace('designation_adv=' + designation_adv, 'designation_adv=' + designation_name);
            par = par.replace('office=' + office, 'office=' + office_name1);
            par = par.replace(/_adv/g, '');
            par = par.replace('?', '');
            par = par.replace(/&/g, ', ');
            par = par.replace(/=/g, ': ');
            par = par.replace(/_/g, ' ');
            par = par.toUpperCase();
            console.log('params ---- ---- ====== ', par);
            $('#search_users').text(par);
            paramglobe = params;
            table.ajax.url(crud_api + '?' + params).load();
        }

        $("select[name='organization'],select[name='office_category'] ,select[name='region'] , select[name='district'], select[name='office'], select[name='designation_adv'], select[name='gender_adv'], select[name='ppr_training_adv'], #updated_at_from , #updated_at_to").change(function () {
            filterUser();
        });
        $("input[name='name_adv'], input[name='bang_name_adv'], input[name='mobile_no_adv'], input[name='off_mobile_no_adv'], input[name='email_adv'], input[name='off_email_adv'], input[name='nid_adv'], input[name='e_gp_id_lged_adv'], input[name='e_gp_id_lgi_adv']").on('input', function () {
            filterUser();
        });
        commonSetDropDown('/lged/api/v1/district/', 'district', 'name', 'id', '-Select Option-');
        commonSetDropDown('/lged/api/v1/region/', 'region', 'name', 'id', '-Select Option-');
        commonSetDropDown('/lged/api/v1/office/?fields=id,name', 'office', 'name', 'id', '-Select Option-');

        let office_id_value;
        $("select[name='office']").change(function () {
            office_id_value = $("select[name='office']").val();
            commonSetDropDownAndSet('/lged/api/v1/designation/?office_id=' + office_id_value, $('select[name="designation_adv"]'),
               'designation', 'id', '-Select Option-', 'elem', '---');
        });

        $("#add_user_org").change(function () {
            var organization_id = $("#add_user_org").val();
            changeOrganizationWithId(organization_id, "add_user_off_cat");
        });

        $("#add_user_org, #add_user_off_cat").change(function () {
            let office_category = $("#add_user_off_cat").val();
            let organization = $("#add_user_org").val();
            let designation_url = '/lged/api/v1/designation/?office_category=' + office_category;
            commonSetDropDown(designation_url, 'add_designation', 'short_form', 'id');
            let params = "";
            if (organization !== "") params += "organization=" + organization + '&';
            if (office_category !== "") params += "office_category=" + office_category + '&';
            // if (office_category === "") return false;
            params += 'fields=id,name&';
            commonSetDropDown('/lged/api/v1/office/?' + params, 'add_user_office', 'name', 'id');
        });
        $("select[name='add_user_office']").change(function () {
            let val = $(this).val();
            let organization_id = $("#add_user_org").val();
            let office_category = $("#add_user_off_cat").val();
            if (organization_id === 'LGIS') {
                let designation_url = '/lged/api/v1/designation/?office_category=' + office_category + '&not_office_id=' + val;
                commonSetDropDown(designation_url, 'add_designation', 'short_form', 'id');
            }
            let jsonCallback = callAjax('/lged/api/v1/office/' + val, 'GET', '');
            jsonCallback.done(function (data) {
                data = data['role_exist'];
                if (data['focal_point'] !== false) {
                    $("select[name='procurement_roles'] option[value=" + data['focal_point'] + "]").remove();
                    $("select[name='procurement_roles_lgis'] option[value=" + data['focal_point'] + "]").remove();
                }
                if (data['org_admin'] !== false) {
                    $("select[name='procurement_roles'] option[value=" + data['org_admin'] + "]").remove();
                    $("select[name='procurement_roles_lgis'] option[value=" + data['org_admin'] + "]").remove();
                }
                if (data['pe_admin'] !== false) {
                    $("select[name='procurement_roles'] option[value=" + data['pe_admin'] + "]").remove();
                    $("select[name='procurement_roles_lgis'] option[value=" + data['pe_admin'] + "]").remove();
                }
            });
            jsonCallback.fail(function (request) {
                showError(request);
            });
        });
        $("select[name='update_user_office']").change(function () {
            let val = $(this).val();
            if (val) {
                let jsonCallback = callAjax('/lged/api/v1/office/' + val, 'GET', '');
                jsonCallback.done(function (data) {
                    data = data['role_exist'];
                    if (data['focal_point'] !== false) {
                        $("select[name='update_procurement_roles'] option[value=" + data['focal_point'] + "]").remove();
                        $("select[name='update_procurement_roles_lgis'] option[value=" + data['focal_point'] + "]").remove();
                    }
                    if (data['org_admin'] !== false) {
                        $("select[name='update_procurement_roles'] option[value=" + data['org_admin'] + "]").remove();
                        $("select[name='update_procurement_roles_lgis'] option[value=" + data['org_admin'] + "]").remove();
                    }
                    if (data['pe_admin'] !== false) {
                        $("select[name='update_procurement_roles'] option[value=" + data['pe_admin'] + "]").remove();
                        $("select[name='update_procurement_roles_lgis'] option[value=" + data['pe_admin'] + "]").remove();
                    }
                });
                jsonCallback.fail(function (request) {
                    showError(request);
                });
            }
        });

        $("#update_user_org").change(function () {
            var organization_id = $("#update_user_org").val();
            changeOrganizationWithId(organization_id, "update_user_off_cat");
        });

        $("#update_user_org, #update_user_off_cat").change(function () {
            let organization = $("#update_user_org").val();
            let office_category = $("#update_user_off_cat").val();
            // designation_url = '/lged/api/v1/designation/?office_category=' + office_category;
            // commonSetDropDown(designation_url, 'designation', 'short_form', 'id');
            let params = "";
            if (organization !== "") params += "organization=" + organization + '&';
            if (office_category !== "") params += "office_category=" + office_category + '&';
            // if (office_category === "") return false;
            params += 'fields=id,name&';
            commonSetDropDownAndSet('/lged/api/v1/office/?' + params, $("select[name='update_user_office']"), 'name', 'id', '-Select Option-',
                'elem', update_user_office_id);
        });

    }

    function check_for_duplicate_proc_role(val) {
        let jsonCallback = callAjax('/lged/api/v1/office/' + val, 'GET', '');
        jsonCallback.done(function (data) {
            data = data['role_exist'];
            let lged_roles = [], lgis_roles = [];
            let lged_select = $("select[name='update_procurement_roles'] option:selected");
            let lgis_select = $("select[name='update_procurement_roles_lgis'] option:selected");
            lged_select.each(function () {
                var option = $(this);
                var label = option.text();
                lged_roles.push(label);
            });
            lgis_select.each(function () {
                var option = $(this);
                var label = option.text();
                lgis_roles.push(label);
            });
            if (data['focal_point'] !== false) {
                if (!lged_roles.includes('Focal Point')) $("select[name='update_procurement_roles'] option[value=" + data['focal_point'] + "]").remove();
                if (!lgis_roles.includes('Focal Point')) $("select[name='update_procurement_roles_lgis'] option[value=" + data['focal_point'] + "]").remove();
            }
            if (data['org_admin'] !== false) {
                if (!lged_roles.includes('Organization Admin')) $("select[name='update_procurement_roles'] option[value=" + data['org_admin'] + "]").remove();
                if (!lgis_roles.includes('Organization Admin')) $("select[name='update_procurement_roles_lgis'] option[value=" + data['org_admin'] + "]").remove();
            }
            if (data['pe_admin'] !== false) {
                if (!lged_roles.includes('PE Admin')) $("select[name='update_procurement_roles'] option[value=" + data['pe_admin'] + "]").remove();
                if (!lgis_roles.includes('PE Admin')) $("select[name='update_procurement_roles_lgis'] option[value=" + data['pe_admin'] + "]").remove();
            }
        });
        jsonCallback.fail(function (request) {
            showError(request);
        });
    }


}
