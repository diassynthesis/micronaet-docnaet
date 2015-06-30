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

# ----------------
# Read parameters:
# ----------------
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

# --------------
# Client erpeek:
# --------------
erp = erppeek.Client(
    'http://%s:%s' % (server, port),
    db=dbname,
    user=user,
    password=password,
    )

# -----------------------------------------------------------------------------
#                             Convertion function:
# -----------------------------------------------------------------------------
def prepare_string(value):
    ''' Return formatted string
    '''
    try:
        return value.strip()
    except:
        print "Convert error: %s" % value

def prepare_bool(value):
    ''' Return formatted boolean
    '''
    return value.strip() == 1 # True

def prepare_int(value):
    ''' Return formatted int
    '''
    try: 
        return int(value.strip())
    except:
        return 0    

def prepare_float(value):
    ''' Return formatted float
    '''
    try: 
        return float(value.strip())
    except:
        return 0.0

def prepare_date(value):
    ''' Return formatted date from dd/mm/yy in yyyy/mm/dd
    '''    
    value = value.strip()    
    if len (value) < 8:
        res = False
    else:    
        res = "%s/%s/%s" % (
            "20%s" % value[6:8] if value[6:8] < '50' else "19%s" % value[6:8],
            value[0:2],
            value[3:5],
            )
    return res        

# -----------------------------------------------------------------------------
#                             Manual importations:
# -----------------------------------------------------------------------------
# Priority (not used in real docnaet)
priority = {
    1: 'highest',
    2: 'high',
    3: 'normal',
    4: 'low',
    5: 'lowest',
    }

# Ditte 
company = {
    6: 1, # docnaet, openerp        
    }    

# Spedito << TODO import current

# -----------------------------------------------------------------------------
#                             Automatic migration
# -----------------------------------------------------------------------------
# ------
# Utenti
# ------
filename = 'Utenti.txt'
user = {}
erp_pool = erp.ResUsers
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
    docnaet_id = int(line[0])
    name = line[1].strip()
    password = line[2].strip()
    
    if name == "Administrator":
        name = "admin"

    item_ids = erp_pool.search([('login', '=', name)])
    data = {
        'login': name,
        'name': name,
        'password': password,
        'docnaet_id': docnaet_id,  
        }
    if item_ids:
        openerp_id = item_ids[0]
        #erp_pool.write(openerp_id, data) # No update
    else:        
        openerp_id = erp_pool.create(data)
        print "%s. Create %s: %s" % (i, csv_file.split('.')[0], name)    
    user[docnaet_id] = openerp_id

# ------------
# Applicazioni 
# ------------
application = {}    


# ------
# Lingue 
# ------
filename = 'Lingue.txt'
language = {}
erp_pool = erp.DocnaetLanguage
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
    docnaet_id = int(line[0])
    name = line[1].strip()
    note = line[2].strip()
    
    item_ids = erp_pool.search([('name', '=', name)])
    data = {
        'name': name,
        'note': note,
        'docnaet_id': docnaet_id,
        }
    if item_ids:
        openerp_id = item_ids[0]
        #erp_pool.write(openerp_id, data) # No update
    else:
        openerp_id = erp_pool.create(data)            
        print "%s. Create %s: %s" % (i, csv_file.split('.')[0], name)    
    language[docnaet_id] = openerp_id

# ----------
# Protocolli 
# ----------
filename = 'Protocolli.txt'
protocol = {}
erp_pool = erp.DocnaetProtocol
csv_file = os.path.expanduser(
    os.path.join(path, filename))

lines = csv.reader(open(csv_file, 'rb'), delimiter=delimiter)   
i = - header   
tot_cols = False
for line in lines:
    try:
        i += 1
        if i <= 0:
            continue # jump intestation
        if not tot_cols: # save for test 
            tot_cols = len(line)
        
        if tot_cols != len(line):
            print "%s. Jump line: different cols %s > %s" % (tot_cols, len(line))
            continue
        
        # read fields:    
        docnaet_id = int(line[0])
        name = line[1].strip()
        next = eval(line[2].strip())
        note = line[3].strip()
        #company_id = eval(line[4].strip())
        #application_id = eval(line[5].strip())
        
        item_ids = erp_pool.search([('name', '=', name)])
        data = {
            'name': name,
            'note': note,
            'docnaet_id': docnaet_id,
            'next': next,
            }
        if item_ids:
            openerp_id = item_ids[0]
            erp_pool.write(openerp_id, data) # TODO No update
        else:        
            openerp_id = erp_pool.create(data)            
            print "%s. Create %s: %s" % (i, csv_file.split('.')[0], name)    
        protocol[docnaet_id] = openerp_id
    except:
        print "%s. Error %s: %s" % (i, csv_file.split('.')[0], name)    

# ---------
# Tipologie
# ---------
filename = 'Tipologie.txt'
tipology = {}
erp_pool = erp.DocnaetType
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
    docnaet_id = int(line[0])
    name = line[1].strip()
    note = line[2].strip()
    
    item_ids = erp_pool.search([('name', '=', name)])
    data = {
        'name': name,
        'note': note,
        'docnaet_id': docnaet_id,
        }
    if item_ids:
        openerp_id = item_ids[0]
        #erp_pool.write(openerp_id, data) # No update
    else:        
        openerp_id = erp_pool.create(data)            
        print "%s. Create %s: %s" % (i, csv_file.split('.')[0], name)    
    tipology[docnaet_id] = openerp_id

# -------
# Nazioni
# -------
# TODO create a dict for name converter (IT > EN)
filename = 'Nazioni.txt'
jump = True
country = {}
erp_pool = erp.ResCountry
csv_file = os.path.expanduser(
    os.path.join(path, filename))

lines = csv.reader(open(csv_file, 'rb'), delimiter=delimiter)   
i = - header   
tot_cols = False
for line in lines:
    if jump:
        break
    
    i += 1
    if i <= 0:
        continue # jump intestation
    if not tot_cols: # save for test 
        tot_cols = len(line)
    
    if tot_cols != len(line):
        print "%s. Jump line: different cols %s > %s" % (tot_cols, len(line))
        continue
    
    # read fields:    
    docnaet_id = int(line[0])
    name = line[1].strip()
    
    item_ids = erp_pool.search([('name', '=', name)])
    data = {
        'name': name,
        'docnaet_id': docnaet_id,
        }
    if item_ids:
        openerp_id = item_ids[0]
        erp_pool.write(openerp_id, data) # No update
    else:        
        opener_id = False # TODO
        #openerp_id = erp_pool.create(data) # No creation only update: IT vs EN
        print "%s. To create %s: %s" % (i, csv_file.split('.')[0], name)    
        
    country[docnaet_id] = openerp_id

# -------
# Clienti
# -------
filename = 'Clienti.txt'
jump = True
partner = {}
erp_pool = erp.ResPartner
csv_file = os.path.expanduser(
    os.path.join(path, filename))

lines = csv.reader(open(csv_file, 'rb'), delimiter=delimiter)   
i = -header   
tot_cols = False
for line in lines:
    if jump:
        break

    i += 1
    if i <= 0:
        continue # jump intestation
    if not tot_cols: # save for test 
        tot_cols = len(line)
    
    if tot_cols != len(line):
        print "%s. Jump line: different cols %s > %s" % (tot_cols, len(line))
        continue
    
    # read fields:    
    docnaet_id = int(line[0])
    name = line[1].strip()
    
    item_ids = erp_pool.search([('name', '=', name)])
    data = {
        'name': name,
        'docnaet_id': docnaet_id,
        }
    if item_ids:
        openerp_id = item_ids[0]
        erp_pool.write(openerp_id, data) # No update
    else:        
        opener_id = False # TODO
        #openerp_id = erp_pool.create(data) # No creation only update: IT vs EN
        print "%s. To create %s: %s" % (i, csv_file.split('.')[0], name)    
        
    partner[docnaet_id] = openerp_id

# ---------
# Documenti 
# ---------
filename = 'Documenti.txt'
document = {}
erp_pool = erp.DocnaetDocument
csv_file = os.path.expanduser(
    os.path.join(path, filename))

# TODO Attenzione ai documenti puntatori (doppio ciclo per assegnazione parent)
lines = csv.reader(open(csv_file, 'rb'), delimiter=delimiter)   
i = -header   
tot_cols = False
for line in lines:
    try:
        i += 1    
        if i <= 0:
            continue # jump intestation
        if not tot_cols: # save for test 
            tot_cols = len(line)
        
        if tot_cols != len(line):
            print "%s. Jump line: different cols %s > %s" % (tot_cols, len(line))
            continue
        
        if i%200 == 0:
            break    
        
        # read fields:    
        docnaet_id = prepare_int(line[0])     
        protocol_code = prepare_int(line[1])
        language_code = prepare_int(line[2])
        type_code = prepare_int(line[3])
        support_code = prepare_int(line[4])
        partner_code = prepare_int(line[5])
        name = prepare_string(line[6])
        description = prepare_string(line[7])
        note = line[8].strip() #prepare_string(line[8])
        date = prepare_date(line[9])
        file_name = prepare_string(line[10])
        deadline = prepare_date(line[11])
        deadlined = prepare_bool(line[12])
        deadline_reason = prepare_string(line[13])
        suspended = prepare_bool(line[14])
        access = prepare_int(line[15])
        company_code = prepare_int(line[16])
        number = prepare_int(line[17])
        fax = prepare_int(line[18])
        user_code = prepare_int(line[19])
        date_create = prepare_date(line[20])
        #control = line[21].strip()
        extension = prepare_string(line[22])
        product_code = prepare_int(line[23])
        ## NO old_id = line[24].strip()
        
        # Convert code in ID:
        protocol_id = protocol.get(protocol_code, False)
        if not protocol_id:
            print "%s. Error protocol docnaet ID: %s" % (i, protocol_code)    
            continue # TODO use a "Not found" protocol

        language_id = language.get(language_code, False) # no warn if error

        type_id = tipology.get(type_code, False) # no warn if error

        user_id = protocol.get(user_code, 1) # No warning or error (set admin)
        
        company_id = company.get(company_code, 1)    
        
        # Create / Update operations:
        item_ids = erp_pool.search([('name', '=', name)])
        data = {
            'company_id': company_id,
            'user_id': user_id,
            'protocol_id': protocol_id,
            'language_id': language_id,
            'type_id': type_id,
            'name': name,
            'date': date,
            #'deadline': deadline, # not implemented in docnaet
            #'deadline_info': deadline_reason, # not implemented in docnaet
            'description': description,
            'note': note,
            'number': number,
            'fax_number': fax,
            'docnaet_extension': extension,
            'filename': file_name,
            'docnaet_id': docnaet_id,
            
            # TODO:
            'partner_id': 1,
            }
        if item_ids:
            openerp_id = item_ids[0]
            erp_pool.write(openerp_id, data) # No update
            print "%s. Updte %s: %s" % (i, csv_file.split('.')[0], name)    
        else:        
            openerp_id = erp_pool.create(data)            
            print "%s. Create %s: %s" % (i, csv_file.split('.')[0], name)    
        document[docnaet_id] = openerp_id
    except:
        print "%s. Error document import: %s" % (i, data)
        print sys.exc_info()
            

# -----------------------------------------------------------------------------
#                                Not migration
# -----------------------------------------------------------------------------
# NOTE: not imported (see res.partner category)
# Categorie 
# Tipi 
# Supporti 
# Prodotti

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: