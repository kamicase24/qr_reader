from datetime import datetime
from flask import render_template, request
from app.main import bp
import shopify
from dotenv import load_dotenv
import os
load_dotenv('.env')

MONTH_ALPHABET = {
    'A': ['Enero', '01'],
    'B': ['Febrero', '02'],
    'C': ['Marzo', '03'],
    'D': ['Abril', '04'],
    'E': ['Mayo', '05'],
    'F': ['Junio', '06'],
    'G': ['Julio', '07'],
    'H': ['Agosto', '08'],
    'I': ['Septiembre', '09'],
    'J': ['Octubre', '10'],
    'K': ['Noviembre', '11'],
    'L': ['Diciembre', '12']
}

SHOPIFY_API_TOKEN = os.getenv('SHOPIFY_API_TOKEN', False)
SHOPIFY_API_KEY = os.getenv('SHOPIFY_API_KEY', False)
SHOPIFY_API_SECRET = os.getenv('SHOPIFY_API_SECRET', False)
SHOPIFY_SHOP_NAME = os.getenv('SHOPIFY_SHOP_NAME', False)
PASSWORD = os.getenv('PASSWORD', False)


@bp.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        password = request.form.to_dict().get('password', False)
        if password:
            if password == PASSWORD:
                return render_template('index.html')
    return render_template('auth.html')

@bp.route('/auth', methods=['POST', 'GET'])
def auth():
    if request.method == 'POST':
        return render_template('auth.html')


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
    # U-B-2-4-193F1
    # 0-1-2-3-4....
    qr_name = data_dict['name']
    month = MONTH_ALPHABET.get(qr_name[1], False)
    if month:
        if not data_dict.get('date', False):
            year = qr_name[2:4]
            lot_date = datetime.strptime(f'{year}/{month[1]}', '%y/%m')
            lot_str_date = lot_date.strftime('%Y/%m')
            data_dict.update({'date': lot_str_date})

    print(f"data_dict {data_dict}")
    return data_dict





def send_to_shopify(data: dict):
    shopify_url = f'https://{SHOPIFY_API_KEY}:{SHOPIFY_API_TOKEN}@{SHOPIFY_SHOP_NAME}.myshopify.com/admin/api/2023-07'
    shopify.ShopifyResource.set_site(shopify_url)
    
    try:
        shop = shopify.Shop.current()
        locations = shopify.Location.find()
        location_id = locations[0].id

        product_title = data['sku']
        lot_number = data['lot_number']+'XX1'
        lot_date = data['date']
        qty = int(data['qty'])

        products = shopify.Product.find(title=product_title)
        if products:
            product = products[0]
            product_image = product.images[0].src if product.images else None

            # Buscar variante por SKU
            variant = next((v for v in product.variants if v.sku == lot_number), None)

            if not variant:
                # Crear nueva variante
                new_variant = shopify.Variant({
                    "product_id": product.id,
                    "title": f'{product_title}-{lot_number}',
                    "option1": lot_number,
                    "sku": lot_number,
                    "inventory_management": "shopify"
                })
                new_variant.save()
                
                if new_variant.errors:
                    return {'error': f'Error creating variant: {new_variant.errors.full_messages()}'}, False
                
                # Asociar imagen si existe
                if product_image:
                    shopify.Image.create({
                        "product_id": product.id,
                        "src": product_image
                    })

                inventory_item_id = new_variant.inventory_item_id
                variant = new_variant
            else:
                inventory_item_id = variant.inventory_item_id

            # Agregar o actualizar metafield en la variante
            metafield = shopify.Metafield({
                "namespace": "custom",
                "key": "custom_date",
                "value": lot_date,
                "value_type": "string",
                "owner_resource": "variant",
                "owner_id": variant.id
            })
            metafield.save()

            if metafield.errors:
                return {'error': f'Error creating metafield: {metafield.errors.full_messages()}'}, False

        else:
            # Crear nuevo producto
            product = shopify.Product({
                "title": product_title,
                "body_html": f"<h1>{product_title}</h1>",
                "variants": [shopify.Variant({
                    "sku": lot_number,
                    "title": f'{product_title}-{lot_number}',
                    "option1": lot_number,
                    "inventory_management": "shopify"
                })]
            })
            product.save()
            
            if product.errors:
                return {'error': f'Error creating product: {product.errors.full_messages()}'}, False

            # Agregar metafield a la primera variante del nuevo producto
            metafield = shopify.Metafield({
                "namespace": "custom",
                "key": "custom_date",
                "value": lot_date,
                "value_type": "string",
                "owner_resource": "variant",
                "owner_id": product.variants[0].id
            })
            metafield.save()

            if metafield.errors:
                return {'error': f'Error creating metafield: {metafield.errors.full_messages()}'}, False

            inventory_item_id = product.variants[0].inventory_item_id

        # Ajustar el nivel de inventario
        inventory_level = shopify.InventoryLevel.adjust(
            location_id=location_id,
            inventory_item_id=inventory_item_id,
            available_adjustment=qty
        )
        
        if inventory_level.errors:
            return {'error': f'Error adjusting inventory: {inventory_level.errors.full_messages()}'}, False

        # Obtener el stock total
        total_stock = 0
        for variant in product.variants:
            variant_inventory_item_id = variant.inventory_item_id
            variant_inventory_levels = shopify.InventoryLevel.find(inventory_item_ids=variant_inventory_item_id, location_ids=location_id)
            total_stock += sum(v.available for v in variant_inventory_levels) if variant_inventory_levels else 0

        inv_level_dict = inventory_level.to_dict()
        inv_level_dict.update({'total_product_stock': total_stock})

        return inv_level_dict, True

    except Exception as e:
        return {'error': str(e)}, False

    finally:
        shopify.ShopifyResource.clear_session()
