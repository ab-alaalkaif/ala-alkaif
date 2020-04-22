{
    'name': 'Alkaif Barcode',
    'version': '1.0.148',
    'category': 'Sales',
    'sequence': 1,
    'depends': ['base', 'sale', 'stock', 'account', 'product', 'website', 'website_sale', 'website_sale_stock'],
    'description': """
Add multiple barcodes per products
    """,
    'data': [
        # security
        'security/ir.model.access.csv',

        # views
        'views/assets.xml',
        'views/product.xml',
        'views/sale_order.xml',
        'views/purchase_order.xml',
        'views/pricelist.xml',
        'views/stock_move.xml',
        'views/account_move.xml',
        'views/website_product.xml',
        'views/cart.xml',
        'views/address.xml',
        # 'views/pos_order.xml',
    ],
    'qweb': ['static/src/xml/pos_barcode.xml'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
