#!/usr/bin/python
import sys
import xmlrpc.client
import ssl
import csv

## DATOS NECESARIOS PARA LA CONEXION
username = 'admin'
pwd = '66admin66'
dbname = 'botelladev_prod'
gcontext = ssl._create_unverified_context()
sock_common = xmlrpc.client.ServerProxy ('http://localhost:8069/xmlrpc/common',context=gcontext)
uid = sock_common.login(dbname, username, pwd)
sock = xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/object',context=gcontext)


# PRIMERO CARGAMOS LAS CATEGORIAS PADRES
f = open('carga_categorias.csv','rt')
csv_reader = csv.DictReader(f,delimiter=',')
for line in csv_reader:
	category = sock.execute(dbname,uid,pwd,'product.public.category','search',[('name','=',line['CATEGORIA_PADRE'])]) #//buscamos el NOMBRE en odoo y devuelve un array donde en posicion [0] esta su id.
	if not category:
		print('No existe la categoria:  %s'%(line['CATEGORIA_PADRE']))
		vals = {
			'name': line['CATEGORIA_PADRE']
			}
		category_id = sock.execute(dbname,uid,pwd,'product.public.category','create',vals)
		print('-> Categoria creada exitosamente, id referente: %s'%category_id)
		continue

	else:
		print('Error, ya existe la categoria que desea cargar! de nombre: %s'%(line['CATEGORIA_PADRE']));



# SEGUNDO CARGAMOS LAS CATEGORIAS HIJAS
f = open('carga_categorias.csv','rt')
csv_reader = csv.DictReader(f,delimiter=',')
for line in csv_reader:
	category_hija = sock.execute(dbname,uid,pwd,'product.public.category','search',[('name','=',line['CATEGORIA_HIJA'])])
	if not category_hija:
		print('No existe la categoria:  %s'%(line['CATEGORIA_HIJA']))
		categoria_padre_id = sock.execute(dbname,uid,pwd,'product.public.category','search',[('name','=',line['CATEGORIA_PADRE'])])
		vals = {
			'name': line['CATEGORIA_HIJA']	,
			'parent_id': categoria_padre_id[0]
			}
		category_id = sock.execute(dbname,uid,pwd,'product.public.category','create',vals)
		print('-> Categoria hija creada exitosamente, id referente: %s'%category_id)
		continue

	else:
		print('Error, ya existe la categoria hija  que desea cargar! de nombre: %s'%(line['CATEGORIA_HIJA']));

#FALTARIA VER SI SE PUEDE CARGAR DOS HIJAS DEL MIMSMO NOMBRE PERO QUE TENGAN DISTINTOS PADRES, ADEMAS DE CARGAR LAS VARIANTES SI ASI LO REQUIEREN
