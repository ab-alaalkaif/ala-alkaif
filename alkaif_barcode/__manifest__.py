{
    'name': 'Alkaif Barcode',
    'version': '1.0.123',
    'category': 'Sales',
    'sequence': 1,
    'depends': ['base', 'sale', 'stock', 'account', 'product'],
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
        # 'views/pos_order.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
