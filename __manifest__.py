# -*- coding: utf-8 -*-
{
    'name': "jt_lead_task",

    'summary': "Create tasks in a preconfigured project from a lead.",

    'description': "",

    'author': "jaco",
    'website': "https://jaco.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales/CRM',
    'version': '15.0.1.0.2',

    # any module necessary for this one to work correctly
    'depends': ["crm", "project"],

    # always loaded
    'data': [
        "wizard/jt_lead_task_wizard_views.xml",
        "views/crm_lead_views.xml",
        "views/settings.xml",
        "views/project_task_views.xml",
        "security/ir.model.access.csv",
    ],

}