from django.conf.urls import url, include
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^api/', include('lged.api.urls', 'api')),

    # user profile
    url(r'^office/list/$', views.user_profile, name='user_profile'),
    url(r'^add/office/$', views.add_office, name='add_office'),
    url(r'^update/office/(?P<id>\d+)/$', views.update_office, name='update_office'),
    url(r'^office/users/(?P<id>\d+)/$', views.office_users, name='office_users'),
    url(r'^users/$', views.users, name='users'),
    url(r'^users/(?P<type>\w{0,50})/$', views.filter_users, name='filter_users'),
    # url(r'^add/user/$', views.add_user, name='add_user'),
    # url(r'^update/user/(?P<id>\d+)/$', views.update_user, name='update_user'),
    url(r'^profile/details/(?P<id>\d+)/$', views.profile_details, name='profile_details'),
    # url(r'^update/profile/$', views.update_profile, name='update_profile'),
    url(r'^transfer/history/$', views.transfer_history, name='transfer_history'),
    url(r'^transfer/user/$', views.transfer_user, name='transfer_user'),
    url(r'^multi_assign/user/$', views.multi_assign_user, name='multi_assign'),
    url(r'^password/requests/$', views.password_requests, name='password_requests'),
    url(r'^request/password/(?P<id>\d+)/$', views.request_password, name='request_password'),
    url(r'^password_request/report/$', views.password_request_report, name='request_password_report'),

    # project profile
    url(r'^project/profile/$', views.project_profile, name='project_profile'),
    url(r'^add/project/$', views.add_project, name='add_project'),
    url(r'^update/project/(?P<id>\d+)/$', views.update_project, name='update_project'),
    url(r'^project/details/(?P<id>\d+)/$', views.project_details, name='project_details'),

    # error
    url(r'^404/$', views.not_found, name='not_found'),
    url(r'^custom/error/$', views.custom_error, name='custom_error'),

    # tender/contract
    url(r'^app-common/$', views.app_common_list, name='app_common_list'),
    url(r'^all-tender/$', views.all_tender_list, name='all_tender_list'),
    url(r'^tender-status/detail/(?P<id>\d+)/$', views.tender_status_detail, name='tender_status_detail'),
    # url(r'^app/$', views.app_list, name='app_list'),
    # url(r'^package/$', views.package_list, name='package_list'),
    # url(r'^lot/$', views.lot_list, name='lot_list'),
    url(r'^tender/$', views.tender_list, name='tender_list'),
    url(r'^contract/$', views.contract_list, name='contract_list'),
    url(r'^tender_report/$', views.tender_report, name='tender_report'),

    # budget
    url(r'^budget/$', views.budget_list, name='budget_list'),
    url(r'^budget/csv/$', views.budget_csv, name='budget_csv'),
    url(r'^budget/report/$', views.budget_report, name='budget_report'),

    # url(r'^tender/list/$', views.tender_list, name='tender_list'),
    url(r'^add/tender/$', views.add_tender, name='add_tender'),
    url(r'^update/tender/(?P<id>\d+)/$', views.update_tender, name='update_tender'),

    # inventory
    url(r'^inventory/list/$', views.inventory_list, name='inventory_list'),
    # url(r'^add/inventory/$', views.add_inventory, name='add_inventory'),
    url(r'^update/inventory/(?P<id>\d+)/$', views.update_inventory, name='update_inventory'),
    # url(r'^add/asset-code/$', views.add_asset_code, name='add_asset_code'),
    # url(r'^asset-code/(?P<id>\d+)/$', views.asset_code, name='asset_code'), [Has been used one time, but not now !]

    # training
    # url(r'^training/list/(?P<category_id>\d+)/$', views.training_list, name='training_list'),
    url(r'^training/list/(?P<user_id>\d+)/$', views.training_list_for_user, name='training_list_for_user'),
    url(r'^training/list/$', views.all_training_list, name='all_training_list'),
    url(r'^training/report/$', views.training_report, name='training_report'),
    url(r'^training/trainers-pool/$', views.trainers_pool, name='trainers_pool'),
    url(r'^users/training/list/$', views.users_training_list, name='users_training_list'),
    url(r'^single-user/training/list/$', views.single_user_training_list, name='single_user_training_list'),
    url(r'^training/details/(?P<id>\d+)$', views.training_details, name='training_details'),
    url(r'^training/update/(?P<id>\d+)$', views.training_update, name='training_update'),
    url(r'^training/update/local/(?P<id>\d+)$', views.local_training_update, name='local_training_update'),
    url(r'^add/training/$', views.add_training, name='add_training'),
    url(r'^add/local-training/$', views.add_local_training, name='add_local_training'),

    # nominated lged officials
    url(r'^external-member/$', views.external_member, name='external_member'),
    url(r'^external-member-link/(?P<case>\d+)/$', views.external_member_link, name='external_member_link'),
    url(r'^external-member-organization/$', views.external_member_organization, name='external_member_organization'),
    url(r'^committee-type/$', views.committee_type, name='committee_type'),
    url(r'^invitee-office/$', views.invitee_office, name='invitee-office'),
    url(r'^audit-trail/$', views.audit_trail, name='audit_trail'),

    # Publications
    url(r'^publication/list/$', views.publication_list1, name='publication_list'),
    url(r'^publication/list/(?P<parent>\d+)/$', views.publication_list2, name='publication_list'),
    url(r'^add/publication/$', views.add_publication1, name='add_publication'),
    url(r'^add/publication/(?P<parent>\d+)/$', views.add_publication2, name='add_gallery'),
    url(r'^update/publication/(?P<id>\d+)/$', views.update_publication, name='update_publication'),

    # Photo Gallery
    url(r'^gallery/list/$', views.gallery_list1, name='gallery_list'),
    url(r'^gallery/list/(?P<parent>\d+)/$', views.gallery_list2, name='gallery_list'),
    url(r'^add/gallery/$', views.add_gallery1, name='add_gallery'),
    url(r'^add/gallery/(?P<parent>\d+)/$', views.add_gallery2, name='add_gallery'),
    url(r'^gallery/add/title/$', views.gallery_add_title1, name='gallery_add_title'),
    url(r'^gallery/add/title/(?P<parent>\d+)/$', views.gallery_add_title2, name='gallery_add_title'),

    # Resource Centers
    # url(r'^resource/centers/$', views.resource_centers, name='resource_centers'),

    # Settings
    url(r'^designation/$', views.designation, name='designation'),
    url(r'^fund-disburse-from/$', views.fund_disburse_from, name='fund_disburse_from'),
    url(r'^procurement-role/$', views.procurement_role, name='procurement_role'),
    url(r'^inventory-type/$', views.inv_type, name='inv_type'),
    url(r'^inventory-type-category/$', views.inv_type_category, name='inv_type_category'),
    url(r'^inventory-status/$', views.inv_status, name='inv_status'),
    url(r'^inventory/update-supplied-quantity/(?P<id>\d+)$', views.update_supplied_quantity, name='update_supplied_quantity'),
    url(r'^inventory-file-type/$', views.inv_file_type, name='inv_file_type'),
    url(r'^inventory-package/$', views.inv_package, name='inv_package'),
    url(r'^inventory-package/devices/(?P<id>\d+)$', views.inv_package_devices, name='inv_package_devices'),
    url(r'^division/$', views.division, name='division'),
    url(r'^region/$', views.region, name='region'),
    url(r'^district/$', views.district, name='district'),
    url(r'^upazila/$', views.upazila, name='upazila'),
    url(r'^training_name/$', views.training_name, name='training_name'),
    url(r'^training_category/$', views.training_category, name='training_category'),
    url(r'^batch_number/$', views.batch_number, name='batch_number'),
    url(r'^from_announcement/$', views.from_announcement, name='from_announcement'),
    url(r'^funded-by/$', views.funded_by, name='funded_by'),
    url(r'^venue/$', views.venue, name='venue'),
    url(r'^home-page-image/$', views.home_page_image, name='home_page_image'),
    url(r'^home-page-writing/(?P<category>\w{0,50})$', views.home_page_writing, name='home_page_writing'),
    url(r'^imp-link/$', views.important_link, name='imp_link'),
    url(r'^responsive-bidder/$', views.responsive_bidder, name='responsive_bidder'),
    url(r'^publication-type/$', views.publication_type, name='publication_type'),
    url(r'^read-more/$', views.read_more, name='read_more'),
    url(r'^e_gp_trainers_pool/$', views.e_gp_trainers_pool, name='e_gp_trainers_pool'),
    url(r'^about-dimapp/$', views.about_dimapp, name='about_dimapp'),
    url(r'^about-lgis/$', views.about_lgis, name='about_lgis'),
    url(r'^contacts/$', views.contacts, name='contacts'),
    url(r'^LGIs/(?P<category>\w{0,50})/$', views.lgis_category, name='lgis_category'),
    url(r'^role-permission/$', views.role_permission, name='role_permission'),
    url(r'^external-member-inclusion/$', views.external_member_inclusion, name='external_member_inclusion'),

    url(r'^budget-type/$', views.budget_type, name='budget_type'),
    url(r'^proc-nature/$', views.procurement_nature, name='proc_nature'),
    url(r'^type-of-emergency/$', views.type_of_emergency, name='type_of_emergency'),
    url(r'^proc-method/$', views.proc_method, name='proc_method'),
    url(r'^proc-type/$', views.proc_type, name='proc_type'),
    url(r'^source-of-fund/$', views.source_of_fund, name='source_of_fund'),
    url(r'^approving-authority/$', views.approving_authority, name='approving_authority'),
    url(r'^contract-status/$', views.contract_status, name='contract_status'),
    url(r'^payment/$', views.payment, name='payment'),
    url(r'^add/payment/$', views.add_payment, name='add-payment'),
    url(r'^edit/payment/(?P<id>\d+)/$', views.edit_payment, name='edit-payment'),

    # account verification
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate,
        name='activate'),

    # announcement
    url(r'^create_announcement/$', views.create_announcement, name='create_announcement'),
    url(r'^announcements/$', views.announcements, name='announcements'),
    url(r'^announcements/(?P<id>\d+)/$', views.announcement_detail, name='announcement_detail'),
    url(r'^create_announcement_for_homepage/$', views.create_announcement_for_homepage,
        name='create_announcement_for_homepage'),

    # issue
    url(r'^issue-title/$', views.issue_title, name='issue_title'),
    url(r'^pending-issues/$', views.pending_issue_list, name='pending_issues'),
    url(r'^solved-issues/$', views.solved_issue_list, name='solved_issues'),
    url(r'^item-issue/(?P<category>\w{0,50})/(?P<item_id>\d+)/$', views.item_issue, name='item_issues'),
    url(r'^issue/issue-report1/$', views.issue_report1, name='issue_report1'),
    url(r'^issue/issue-report2/$', views.issue_report2, name='issue_report2'),

    # report
    url(r'^inventory/update-report/$', views.inv_report, name='inv_report'),
    url(r'^app/report/$', views.app_report, name='app_report'),
    url(r'^tender/report/$', views.tender_report, name='tender_report'),
    url(r'^office/designation/$', views.specific_office_designation, name='specific_designation'),
    url(r'^office/information/$', views.get_district_from_office_info, name='office_districts'),
    url(r'^notify/$', views.notify_training_batch_participants, name='Notify')

]
