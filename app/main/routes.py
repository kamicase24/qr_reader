from flask import render_template, request
from app.main import bp
from app.extensions import Base, db
import xmlrpc.client
from config import Config





@bp.route('/')
def index():

    return render_template('index.html')


def create_odoo_record(data:dict):
    url = Config.ODOO_URL
    db = Config.ODOO_DB
    user = Config.ODOO_USER
    odoo_key = Config.ODOO_KEY    
    common = xmlrpc.client.ServerProxy('%s/xmlrpc/2/common' % url)
    uid = common.authenticate(db, user, odoo_key, {})
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    model_name = 'product.qr.result'

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

    print(f"data_dict {data_dict}")
    qr_product_count = models.execute_kw(db, uid, odoo_key, model_name, 'search_count', [[['name', '=', data_dict['name']]]])
    if qr_product_count == 0:
        qr_product_id = models.execute_kw(db, uid, odoo_key, model_name, 'create', [data_dict])
        print("REGISTRO QR CREADO")
        return True, qr_product_id
    else:
        print("REGISTRO QR EXISTENTE")
        return False, 'QR EXISTENTE'


@bp.route('/test_odoo_con')
def test_odoo_con():
    url = Config.ODOO_URL
    db = Config.ODOO_DB
    user = Config.ODOO_USER
    odoo_key = Config.ODOO_KEY    
    common = xmlrpc.client.ServerProxy('%s/xmlrpc/2/common' % url)
    uid = common.authenticate(db, user, odoo_key, {})
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    model_name = 'product.qr.result'
    
    data_dict = {'lot_number': 'UE24160F4', 'sku': 'F641.2487', 'name': 'UE24160F4', 'qty': '1.0', 'date': 'AUG 2025'}


    print(f"data_dict {data_dict}")
    qr_product_count = models.execute_kw(db, uid, odoo_key, model_name, 'search_count', [[['name', '=', data_dict['name']]]])
    if qr_product_count == 0:
        qr_product_id = models.execute_kw(db, uid, odoo_key, model_name, 'create', [data_dict])
        print("REGISTRO QR CREADO")
        return str(qr_product_id)
    else:
        print("REGISTRO QR EXISTENTE")
        return 'QR escaneado'


@bp.route('/read_qr_result', methods=['POST'])
def read_qr_result():
    if request.method == 'POST':
        data = request.get_json()

        success, result = create_odoo_record(data)

        return {
            'success': success,
            'result': result
        }, 200
    return {'success': False}, 400