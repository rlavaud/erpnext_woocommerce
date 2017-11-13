# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext_woocommerce.woocommerce_requests import get_woocommerce_items
from erpnext_woocommerce.sync_products import get_supplier
from erpnext_woocommerce.utils import is_woocommerce_enabled
from frappe.utils.fixtures import sync_fixtures

def execute():
	if not is_woocommerce_enabled():
		return

	sync_fixtures('erpnext_woocommerce')
	
	for index, woocommerce_item in enumerate(get_woocommerce_items(ignore_filter_conditions=True)):
		name = frappe.db.get_value("Item", {"woocommerce_product_id": woocommerce_item.get("id")}, "name")
		supplier = get_supplier(woocommerce_item)
	
		if name and supplier:
			frappe.db.set_value("Item", name, "default_supplier", supplier, update_modified=False)
					
		if (index+1) % 100 == 0:
			frappe.db.commit()
		
		