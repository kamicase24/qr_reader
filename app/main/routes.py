from flask import render_template, request
from app.main import bp
import shopify
from dotenv import load_dotenv
import os
load_dotenv('.env')


SHOPIFY_API_TOKEN = os.getenv('SHOPIFY_API_TOKEN', False)
SHOPIFY_API_KEY = os.getenv('SHOPIFY_API_KEY', False)
SHOPIFY_API_SECRET = os.getenv('SHOPIFY_API_SECRET', False)
SHOPIFY_SHOP_NAME = os.getenv('SHOPIFY_SHOP_NAME', False)


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/read_qr_result', methods=['POST'])
def read_qr_result():
    if request.method == 'POST':
        qr_data = request.get_json()
        # {
        #     'decodeResult': {
        #         'decodedText': '~102 SB24130C2 ~100 F632.1207 ~101 SB24130C2 ~104 16.000000',
        #         'result': {
        #             'debugData': {'decoderName': 'zxing-js'},
        #             'format': {'format': 0, 'formatName': 'QR_CODE'},
        #             'text': '~102SB24130C2~100F632.1207~101SB24130C2~10416.000000'
        #         }
        #     },
        #     'decodeText': '~102SB24130C2~100F632.1207~101SB24130C2~10416.000000'
        # }
        data = process_qr_data(qr_data)
        # {
        #     'name': 'SB24130C2', 
        #     'sku': 'F632.1207', 
        #     'lot_number': 'SB24130C2', 
        #     'qty': 16.0
        # }
        
        result, success = send_to_shopify(data)
        return {
            'success': success,
            'result': result,
            'info': data
        }, 200
    return {'success': False}, 400


def process_qr_data(data:dict):
    print(data)
    raw_data_dict = {dt[:3]: dt[3:]for dt in data['decodeText'].split('~') if dt != ''}
    key_mapping = {
        '100': 'sku',
        '101': 'lot_number',
        '102': 'name', # Batch Number
        '104': 'qty',
        '105': 'date'
    }
    data_dict = {key_mapping[key]: value for key, value in raw_data_dict.items()}
    data_dict['qty'] = float(data_dict['qty'])

    print(f"data_dict {data_dict}")
    return data_dict




def send_to_shopify(data:dict):
    shopify_url = f'https://{SHOPIFY_API_KEY}:{SHOPIFY_API_TOKEN}@{SHOPIFY_SHOP_NAME}.myshopify.com/admin'
    shopify.ShopifyResource.set_site(shopify_url)
    
    shop = shopify.Shop.current()

    locations = shopify.Location.find()
    location_id = locations[0].id
    
    # product_title = data['sku']
    product_title = 'DEV PRODUCT 6'
    lot_number = data['lot_number']
    
    products = shopify.Product.find(title=product_title)
    if len(products) > 0:
        product = products[0]
        inventory_item_id = product.variants[0].inventory_item_id
    else:
        new_product = shopify.Product()
        new_product.title = product_title
        new_product.body_html = f"<h1>{product_title}"
        # new_product.lot_ = lot_number
        new_product.variants = [shopify.Variant(
            {
                "sku": product_title,
                "inventory_management": "shopify"  # Habilitar la gestión de inventario por Shopify
            }
        )]
        is_saved = new_product.save()
        
        print(f'is saved? {is_saved}')
        if is_saved:
            print('New product created')
            inventory_item_id = new_product.variants[0].inventory_item_id
    
    metafield = shopify.Metafield()
    metafield.lot_ = lot_number

    inventory_level = shopify.InventoryLevel.adjust(
        location_id=location_id,
        inventory_item_id=inventory_item_id,
        available_adjustment=int(data['qty'])
    )
    inv_level_dict = inventory_level.to_dict()
    
    shopify.ShopifyResource.clear_session()
    return inv_level_dict, True


