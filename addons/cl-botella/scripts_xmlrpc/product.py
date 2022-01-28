import xmlrpc.client
import csv
import sys
import time
import configparser
# import search_create_or_write as x

# HOST = 'localhost'
# PORT=8069
# HOST = '34.70.230.20'
# PORT=80
HOST = 'localhost'
PORT=8069
USER = 'admin'
PASS = 'bote66lla'
DB = 'botelladev13ce_prod'


INPUT_FILE = 'products_faltantes.csv'

URL = 'http://%s:%d/xmlrpc/common' % (HOST, PORT)
SOCK = xmlrpc.client.ServerProxy(URL)
UID = SOCK.login(DB, USER, PASS)
print("Logged in as %s (UID:%d)" % (USER, UID))
URL = 'http://%s:%d/xmlrpc/object' % (HOST, PORT)
SOCK = xmlrpc.client.ServerProxy(URL)
CSV_FILE = csv.reader(open(INPUT_FILE, 'rt'), delimiter=',')
next(CSV_FILE)
MODEL_NAME = 'product.template'
cont = 0
updates = 0
creations = 0
ultimo_agente = 0
seq = 30
START_TIME = time.time()

## paso productos a publicados en la web
product_id = SOCK.execute(DB, UID, PASS, MODEL_NAME, 'search', [('is_published','=',False)])
if product_id:
    product = {
        'is_published': True
    }
    reg_id = SOCK.execute(DB, UID, PASS, MODEL_NAME, 'write', product_id, product)


for line in CSV_FILE:
    if line[0]=='name':
        continue
    cont += 1
    name = line[0]

    # default_code = line[1]
    # active = bool(line[2])
    # barcode = line[4]
    # name = line[15]
    # sequence = int(line[16])
    # type = line[20]
    # category_id = line[22]
    # list_price = float(line[23])
    # sale_ok = bool(line[26])
    # purchase_ok = bool(line[27])
    # uom_id = int(line[28])
    # uom_po_id = int(line[29])
    # has_configurable_attributes = bool(line[35])
    # website_sequence = int(line[65])

    categ_id = SOCK.execute(DB, UID, PASS, 'product.category', 'search', [('name', '=', 'All')])
    if not categ_id:
        print ('No existe la categoria %s'%(categ_id))

    product = {
        #'default_code': default_code,
        'active': True,
        #'barcode': barcode,
        'name': name,
        'sequence': 1,
        'type': 'product',
        'categ_id': categ_id[0],
        #'list_price': list_price,
        'sale_ok': True,
        'purchase_ok': True,
        'is_published': False,
        #'uom_id': uom_id,
        #'uom_po_id': uom_po_id,
        #'has_configurable_attributes': has_configurable_attributes,
        #'website_sequence': website_sequence,
        'tracking': 'none',
        # 'purchase_method': 'receive',
        # 'purchase_line_warn': 'no-message',
        'service_type': 'manual',
        'sale_line_warn': 'no-message',
        'expense_policy': 'no',
        'invoice_policy': 'order',
        'inventory_availability': 'never',
    }

    sys.stdout.write("\rLoading %s: #%s" % (MODEL_NAME, cont))
    sys.stdout.flush()
    args = [('name', '=', name)]
    product_id = SOCK.execute(DB, UID, PASS, MODEL_NAME, 'search', args)
    if product_id:
        reg_id = SOCK.execute(DB, UID, PASS, MODEL_NAME, 'write', product_id, product)
        updates += 1
    else:
        reg_id = SOCK.execute(DB, UID, PASS, MODEL_NAME, 'create', product)
        creations += 1
print("\nElapsed time: %.2f seg." % (time.time() - START_TIME))
print("%d records created, %d records updated\n" % (creations, updates))

## paso productos consumibles a almacenables
product_id = SOCK.execute(DB, UID, PASS, MODEL_NAME, 'search', [('type','=','consu')])
if product_id:
    product = {
        'type': 'product'
    }
    reg_id = SOCK.execute(DB, UID, PASS, MODEL_NAME, 'write', product_id, product)
