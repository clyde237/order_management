# -*- coding: utf-8 -*-
{
    'name': "order_management",

    'summary': "Module1 de la partie 1 formation janvier",

    'description': """
ce module pert de gerer des commandes en envoyant des notifications mails et sous formes d'activité de facon
automatique aux utilisateurs à chaque etape.
    """,

    'author': "Clyde",
    'website': "clyde.inov.cm",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/order_groups.xml',
        'data/order_sequence.xml',
        'data/email_template.xml',
        'views/order.xml',
        'views/order_line.xml',
        'views/menus.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}

