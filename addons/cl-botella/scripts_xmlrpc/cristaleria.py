#!/usr/bin/python
import sys
import xmlrpc.client
import ssl
import csv

## DATOS NECESARIOS PARA LA CONEXION
username = 'admin'
pwd = 'bote66lla'
dbname = 'botelladev_prod'
gcontext = ssl._create_unverified_context()
sock_common = xmlrpc.client.ServerProxy ('http://localhost:8069/xmlrpc/common',context=gcontext)
uid = sock_common.login(dbname, username, pwd)
sock = xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/object',context=gcontext)

products = sock.execute(dbname,uid,pwd,'product.template','search',[('area','=','Cristaleria')])
print ('products', products, len(products))
for product in products:
    read = sock.execute(dbname,uid,pwd,'product.template','read',product,['uom_po_id'])
    uom_po_id = read[0]['uom_po_id'][0]
    reads = sock.execute(dbname,uid,pwd,'uom.uom','read',uom_po_id,['factor_inv'])
    print ('read', read)
    vals = {
        'name': 'Caja',
        'product_tmpl_id': product,
        'uom_id': uom_po_id,
        'factor': reads[0]['factor_inv'],
        'is_published': True
    }
    secondary_id = sock.execute(dbname,uid,pwd,'product.secondary.unit','create',vals)
    update = {
        'sale_secondary_uom_id': secondary_id,
        'allow_uom_sell': False
    }
    secondary_id = sock.execute(dbname,uid,pwd,'product.template','write', product,update)

