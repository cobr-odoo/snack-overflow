{
    'name': 'Snack Overflow: Lunch',
    'summary': 'Discord integration for lunch statistics',
    'description': """
        This module integrates Discord with Odoo to manage lunch menus and collect statistics on lunch preferences through polls.
        It allows users to create weekly lunch menus, specify allergens, and gather responses from the community about their lunch choices.
        The bot posts the menu in a designated Discord channel and collects votes on which days users will eat lunch, providing insights into dietary preferences and needs.
        Authors: Cobr, Deni, Adru
    """,
    'author': 'cobr, deni, adru',
    'website': "https://www.odoo.com/",
    'version': '1.0',
    'icon': '/snack/static/description/icon.png',
    'license': 'OPL-1',
    'depends': ['base'],
    'data': [
        'data/bot_data.xml',
        'security/ir.model.access.csv',
        'views/lunch_menus.xml',
        'views/lunch_week_view.xml',
        'views/snack_bot_view.xml',
    ],
    'application': True,
}
