{
    'name': 'HACCP',
    'version': '20.0.1.0.0',
    'summary': 'Track cold storage temperatures for food safety',
    'category': 'Supply Chain/Maintenance',
    'author': 'Bilal Saidi',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/bs_haccp_groups.xml',
        'security/ir.access.csv',
        'views/bs_haccp_location_views.xml',
        'views/bs_haccp_equipment_views.xml',
        'views/bs_haccp_reading_views.xml',
        'views/bs_haccp_menus.xml',
    ],
    'demo': [
        'data/bs_haccp_demo.xml',
    ],
    'application': True,
}
