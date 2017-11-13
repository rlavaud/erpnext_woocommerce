# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
import frappe
from frappe.utils.fixtures import sync_fixtures

def execute():
	sync_fixtures("erpnext_woocommerce")
	frappe.reload_doctype("Item")
	frappe.reload_doctype("Customer")
	frappe.reload_doctype("Sales Order")
	frappe.reload_doctype("Delivery Note")
	frappe.reload_doctype("Sales Invoice")
	
	for doctype, column in {"Customer": "woocommerce_customer_id", 
		"Item": "woocommerce_product_id", 
		"Sales Order": "woocommerce_order_id", 
		"Delivery Note": "woocommerce_order_id", 
		"Sales Invoice": "woocommerce_order_id"}.items():
		
		if "woocommerce_id" in frappe.db.get_table_columns(doctype):
			frappe.db.sql("update `tab%s` set %s=woocommerce_id" % (doctype, column))	
