#!/usr/bin/python

import sys
import xmlrpc.client
import ssl
import csv

username = 'admin'
pwd = 'bote66lla'
dbname = 'botelladev13ce_prod'

gcontext = ssl._create_unverified_context()

# Get the uid
sock_common = xmlrpc.client.ServerProxy ('http://localhost:8069/xmlrpc/common',context=gcontext)
uid = sock_common.login(dbname, username, pwd)

#replace localhost with the address of the server
sock = xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/object',context=gcontext)

MODEL_NAME = 'stock.quant'

# PRIMERO CARGAMOS LAS CATEGORIAS PADRES
INPUT_FILE = 'stock_quant.csv'
CSV_FILE = csv.reader(open(INPUT_FILE, 'rt'), delimiter=',')
cont = 0
for line in CSV_FILE:
    if line[0]=='name':
        continue
    #print (line)
    #continue
    product_name = line[0]
    location_name = line[1]
    if location_name=='Ajustes de Inventario':
        location_name = 'My Company: Inventory adjustment'
    quantity = line[2]
    reserved_quantity = line[3]
    product_id = sock.execute(dbname, uid, pwd, 'product.template', 'search', [('name', '=', product_name)])
    if not product_id:
        print ('No existe el product %s'%(product_name))
        continue
    location_id = sock.execute(dbname, uid, pwd, 'stock.location', 'search', [('name', '=', location_name)])
    if not location_id:
        print ('No existe location %s'%(location_name))
        continue

    quant = {
        'product_id': product_id[0],
        'location_id': location_id[0],
        'quantity': quantity,
        'reserved_quantity': reserved_quantity,
    }

    # location_id = sock.execute(dbname,uid,pwd,'stock.location','search',[('usage','=','internal')])
    # product_id = sock.execute(dbname,uid,pwd,'product.product','search',[('default_code','=','PROD_STOCK')])

    quant_id = sock.execute(dbname,uid,pwd,MODEL_NAME,'search',[
        ('product_id','=',product_id[0]),
        ('location_id','=',location_id[0])
    ])
    print ('quant', quant)
    if quant_id:
        reg_id = sock.execute(dbname, uid, pwd, MODEL_NAME, 'write', quant_id, quant)
        updates += 1
    else:
        reg_id = sock.execute(dbname, uid, pwd, MODEL_NAME, 'create', quant)
        # quant_data = sock.execute(dbname,uid,pwd,'stock.quant','read',quant_id)
        # print quant_data
        # vals_update = {
        #     'quantity': 555
        #     }
        # return_id = sock.execute(dbname,uid,pwd,'stock.quant','write',quant_id,vals_update)
        # print return_id
