{
    'name': 'Alkaif Website',
    'version': '1.0.125',
    'category': 'Sales',
    'sequence': 1,
    'depends': ['base', 'website', 'website_sale'],
    'description': """
Alkaif Website
    """,
    'data': [
        # views
        'views/website_product.xml',
        'views/cart.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
