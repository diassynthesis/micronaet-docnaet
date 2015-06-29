# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2001-2014 Micronaet SRL (<http://www.micronaet.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import os
import sys
import csv
import erppeek
import ConfigParser

# Read parameters:
config = ConfigParser.ConfigParser()
config.read(['config.cfg'])

server = config.get('OpenERP', 'server')
port = config.get('OpenERP', 'port')
dbname = config.get('OpenERP', 'dbname')
user = config.get('OpenERP', 'user')
password = config.get('OpenERP', 'password')

path = config.get('csv', 'path')
header = eval(config.get('csv', 'header'))
delimiter = config.get('csv', 'delimiter')

# Client erpeek:
erp = erppeek.Client(
    'http://%s:%s' % (server, port),
    db=dbname,
    user=user,
    password=password,
    )

# -----------------------------------------------------------------------------
#                             Manual importations
# -----------------------------------------------------------------------------
# Importanza 
priority = {
    0: 'highest',
    1: 'high',
    2:'normal',
    3:'low',
    4: 'lowest',
    }

# Ditte 
company = {
    1: 1, # access, openerp        
    }    

# Spedito << TODO import current

# -----------------------------------------------------------------------------
#                             Automatic migration
# -----------------------------------------------------------------------------
# Utenti
filename = 'Utenti.txt'
erp_pool = erp.ResUsers
user = {}
csv_file = os.path.expanduser(
    os.path.join(path, filename))

lines = csv.reader(open(csv_file, 'rb'), delimiter=delimiter)   
i = - header   
tot_cols = False
for line in lines:
    i += 1
    if i <= 0:
        continue # jump intestation
    if not tot_cols: # save for test 
        tot_cols = len(line)
    
    if tot_cols != len(line):
        print "%s. Jump line: different cols %s > %s" % (tot_cols, len(line))
        continue
    
    # read fields:    
    access_id = int(line[0])
    name = line[1].strip()
    password = line[2].strip()
    
    if name == "Administrator":
        name = "admin"

    item_ids = erp_pool.search([('login', '=', name)])
    if item_ids:
        openerp_id = item_ids[0]
        #erp_pool.write(openerp_id, {}) # No update
    else:        
        openerp_id = erp_pool.create({
            'login': name,
            'name': name,
            'password': password,
            })
        print "%s. Create user: %s" % (i, name)    
    user[access_id] = openerp_id

# Applicazioni 
application = {}    

# Lingue 
language = {}

# Protocolli 
csv_file = 'Protocolli.txt'

# Clienti
csv_file = 'Clienti.txt'

# Nazioni
csv_file = 'Nazioni.txt'

# Tipologie
csv_file = 'Tipologie.txt'

# Documenti 
csv_file = 'Documenti.txt'

# -----------------------------------------------------------------------------
#                                Not migration
# -----------------------------------------------------------------------------
# NOTE: not imported (see res.partner category)
# Categorie 
# Tipi 
# Supporti 
# Prodotti

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
