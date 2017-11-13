# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext_woocommerce.utils import is_woocommerce_enabled
from frappe.utils.fixtures import sync_fixtures

def execute():
	if not is_woocommerce_enabled():
		return
	
	sync_fixtures('erpnext_woocommerce')
	
	fieldnames = frappe.db.sql("select fieldname from `tabCustom Field`", as_dict=1)	
	
	if not any(field['fieldname'] == 'woocommerce_supplier_id' for field in fieldnames):
		return 
			
	frappe.db.sql("""update tabSupplier set woocommerce_supplier_id=supplier_name """)
	frappe.db.commit()
			