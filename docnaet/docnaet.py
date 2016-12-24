# -*- coding: utf-8 -*-
###############################################################################
#
# ODOO (ex OpenERP) 
# Open Source Management Solution
# Copyright (C) 2001-2015 Micronaet S.r.l. (<http://www.micronaet.it>)
# Developer: Nicola Riolini @thebrush (<https://it.linkedin.com/in/thebrush>)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import os
import sys
import logging
import openerp.netsvc as netsvc
from openerp.osv import osv, orm, fields
from datetime import datetime, timedelta
from openerp.tools import (
    DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


_logger = logging.getLogger(__name__)

# TODO res.country (importabili con i partner)
class ResCompany(orm.Model):
    ''' Docnaet company extra fields
    '''
    _inherit = 'res.company'
    
    def get_docnaet_folder_path(self, cr, uid, subfolder=None, context=None):
        ''' Function for get (or create) root docnaet folder 
            (also create extra subfolder)
            subfolder: string value for sub root folder, valid value:
                > 'store'
                > 'private'
        '''
        subfolder = subfolder or 'root'
        
        # Get docnaet path from company element
        company_ids = self.search(cr, uid, [], context=context)
        company_proxy = self.browse(cr, uid, company_ids, context=context)[0]
        docnaet_path = company_proxy.docnaet_path
        
        # Folder structure:
        path = {}
        path['root'] = docnaet_path
        path['store'] = os.path.join(docnaet_path, 'store')
        path['private'] = os.path.join(docnaet_path, 'private')
        
        # Create folder structure # TODO test if present
        for folder in path:
            os.system('mkdir -p %s' % path[folder])
        
        # Check folder presence (instead create one's)
        
        # Check or create subfolder        
        return path[subfolder]
        
    _columns = {
        'docnaet_path': fields.char(
            'Docnaet path', size=64, required=True,
            help='Docnaet root path in file system for store docs'), 
        }

class DocnaetLanguage(orm.Model):
    ''' Object docnaet.language
    '''    
    
    _name = 'docnaet.language'
    _description = 'Docnaet language'
    _order = 'name'
                    
    _columns = {        
        'name': fields.char('Language', size=64, required=True),
        'code': fields.char('Code', size=16),
        'iso_code': fields.char('ISO Code', size=16),
        'note': fields.text('Note'),
        }

class DocnaetType(orm.Model):
    ''' Object docnaet.type
    '''    
    _name = 'docnaet.type'
    _description = 'Docnaet type'
    _order = 'name'
    

    _columns = {        
        'name': fields.char('Type', size=64, required=True),
        'note': fields.text('Note'),
        }

class DocnaetProtocol(orm.Model):
    ''' Object docnaet.protocol
    '''    
    _name = 'docnaet.protocol'
    _description = 'Docnaet protocol'
    _order = 'name'

    _columns = {        
        'name': fields.char('Protocol', size=64, required=True),
        'next': fields.integer('Next protocol', required=True), 
        'note': fields.text('Note'),
        # TODO default_application_id
        }
    _defaults = {
        'next': lambda *x: 1,
        }    

class DocnaetProtocolTemplateProgram(orm.Model):
    ''' Object docnaet.protocol.template.program
    '''    
    
    _name = 'docnaet.protocol.template.program'
    _description = 'Docnaet program'
    _order = 'name'
                    
    _columns = {        
        'name': fields.char('Language', size=64, required=True),
        'extension': fields.char('Extension', size=5),
        'note': fields.text('Note'),
        }

class DocnaetProtocolTemplate(orm.Model):
    ''' Object docnaet.protocol.template
    '''    
    
    _name = 'docnaet.protocol.template'
    _description = 'Docnaet protocol template'
    _rec_name = 'lang_id'
    _order = 'lang_id'

    _columns = {
        'lang_id': fields.many2one('docnaet.language', 'Language', 
            required=True),
        'protocol_id': fields.many2one('docnaet.protocol', 'Protocol'),
        'program_id': fields.many2one('docnaet.protocol.template.program', 
            'Program'),
        'note': fields.text('Note'),
        }

class DocnaetProtocol(orm.Model):
    ''' 2many fields
    '''    
    _inherit = 'docnaet.protocol'

    _columns = {
        'template_ids': fields.one2many('docnaet.protocol.template', 
            'protocol_id', 'Template'),
        }

class DocnaetDocument(orm.Model):
    ''' Object docnaet.document
    '''    
    _name = 'docnaet.document'
    _description = 'Docnaet document'
    _order = 'date desc,name'

    # -------------------------------------------------------------------------
    # Utility: 
    # -------------------------------------------------------------------------
    def move_private_file(self, cr, uid, ids, data, context=None):
        ''' check if document is in private area, so move in docnaet folder
            and mark private = False
            modify data dict for this operation
        '''
        company_pool = self.pool.get('res.company')
        doc_proxy = self.browse(cr, uid, ids, context=context)[0]
        if doc_proxy.private and not doc_proxy.imported:
            # Get source and destination folder
            private_folder = company_pool.get_docnaet_folder_path(
                cr, uid, subfolder='private', context=context)
            private_folder = os.path.join(
                private_folder, str(doc_proxy.user_id.id))
            store_folder = company_pool.get_docnaet_folder_path(
                cr, uid, subfolder='store', context=context)
            
            f_private = os.path.join(private_folder, doc_proxy.filename)
            f_store = '%s.%s' % (
                os.path.join(store_folder, str(doc_proxy.id)),
                doc_proxy.docnaet_extension,
                )
            os.rename(f_private, f_store)
            data['private'] = False
            data['imported'] = True
        return
        
    # -------------------------------------------------------------------------
    # Workflow state event: 
    # -------------------------------------------------------------------------
    def document_draft(self, cr, uid, ids, context=None):
        ''' WF draft state
        '''
        self.write(cr, uid, ids, {
            'state': 'draft',
            }, context=context)
        return True

    def document_confirmed(self, cr, uid, ids, context=None):
        ''' WF confirmed state
        '''        
        data = {'state': 'confirmed'}
        self.move_private_file(cr, uid, ids, data, context=context)        
        return self.write(cr, uid, ids, data, context=context)

    def document_suspended(self, cr, uid, ids, context=None):
        ''' WF suspended state
        '''
        data = {'state': 'suspended'}
        self.move_private_file(cr, uid, ids, data, context=context)        
        return self.write(cr, uid, ids, data, context=context)

    def document_timed(self, cr, uid, ids, context=None):
        ''' WF timed state
        '''
        data = {'state': 'timed'}
        self.move_private_file(cr, uid, ids, data, context=context)        
        return self.write(cr, uid, ids, data, context=context)

    def document_cancel(self, cr, uid, ids, context=None):
        ''' WF cancel state
        '''
        data = {'state': 'cancel'}
        self.move_private_file(cr, uid, ids, data, context=context)        
        return self.write(cr, uid, ids, data, context=context)

    # -------------------------------------------------------------------------
    # Utility:
    # -------------------------------------------------------------------------
    def call_docnaet_url(self, cr, uid, ids, mode, context=None):    
        ''' Call url in format: docnaet://[operation] cases:
            [open] protocol - id.ext > open document
            [home] folder > open personal folder (for updload)
            
            NOTE: maybe expand the services
        '''        
        doc_proxy = self.browse(cr, uid, ids, context=context)[0]

        if mode == 'open':  # TODO rimettere id e togliere docnae_id
            final_url = r"docnaet://[open]%s-%s.%s" % (
                doc_proxy.protocol_id.docnaet_id,
                doc_proxy.docnaet_id \
                    if not doc_proxy.original_id \
                    else doc_proxy.original_id.id,
                doc_proxy.docnaet_extension or 'doc', # default doc
                )
        elif mode == 'home':
            final_url = r"docnaet://[home]%s" % 'home_folder' #TODO

        return {
            'name': 'Docnaet document',
            #res_model': 'ir.actions.act_url',
            'type': 'ir.actions.act_url', 
            'url': final_url, 
            'target': 'new', # self
            }

    # -------------------------------------------------------------------------
    # Button event:
    # -------------------------------------------------------------------------
    def button_assign_fax_number(self, cr, uid, ids, context=None):
        ''' Assign fax number to document (next counter)
        '''
        return True

    def button_call_url_docnaet(self, cr, uid, ids, context=None):
        ''' Call url function for prepare address and return for open doc:
        '''
        return self.call_docnaet_url(cr, uid, ids, 'open', context=context)
                       
    _columns = {        
        'name': fields.char('Subject', size=80, required=True),
        'filename': fields.char('File name', size=200),
        'description': fields.text('Description'),
        'note': fields.text('Note'),
        
        'number': fields.char('N.', size=10),
        'fax_number': fields.char('Fax n.', size=10),

        'date': fields.date('Date', required=True),
        'deadline': fields.date('Deadline'),
        'deadline_info': fields.char('Deadline info', size=64),

        # OpenERP many2one 
        'protocol_id': fields.many2one('docnaet.protocol', 'Protocol', 
            #required=True
            ),
        'language_id': fields.many2one('docnaet.language', 'Language'),
        'type_id': fields.many2one('docnaet.type', 'Type'),
        'company_id': fields.many2one('res.company', 'Company'),
        'user_id': fields.many2one('res.users', 'User', required=True),
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
        'docnaet_extension': fields.char('Ext.', size=10),

        'original_id': fields.many2one('docnaet.document', 'Original',
            help='Parent orignal document after this duplication'),
        'imported': fields.boolean('Imported'), 
        'private': fields.boolean('Private'), 
        # Workflow date event:
        #'date_confirmed': fields.text('Confirmed event', required=True),
        #'date_suspended': fields.date('Suspended event', required=True),
        #'date_deadline': fields.date('Deadline event', required=True),

        'priority': fields.selection([
            ('lowest', 'Lowest'),
            ('low', 'Low'),
            ('normal', 'Normal'),
            ('high', 'high'),
            ('highest', 'Highest'), ], 'Priority'),
        
        'state': fields.selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('suspended', 'Suspended'),
            ('timed', 'Timed'),
            ('cancel', 'Cancel'), ], 'State', readonly=True),
        }
        
    _defaults = {
        'date': lambda *x: datetime.now().strftime(
            DEFAULT_SERVER_DATE_FORMAT),
        'priority': lambda *x: 'normal',
        'state': lambda *x: 'draft',        
        }    

class DocnaetDocument(orm.Model):
    ''' Add extra relation fileds
    '''          
    _inherit = 'docnaet.document'

    _columns = {
        'duplicated_ids': fields.one2many('docnaet.document', 'original_id',
            'duplicated', help='Child document duplicated from this'),
        }
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
