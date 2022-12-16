# -*- coding: utf-8 -*-
{
    'name': "tecnote Po  lines sequence",

    "summary": """
   Add  Po  lines sequence
    """,
    'author': "tecnote Technology",
    'website': "https://www.tecnote.ca/",

    "category": "Purchase",
    "depends": [
        "base",
        "purchase",
    ],
    'data': [
        'views/purchase_view.xml',
    ],
    "depends": [
        "purchase",
    ],
    'post_init_hook': 'post_init_hook',
    "installable": True,
}
