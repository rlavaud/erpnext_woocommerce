# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import requests.exceptions
from frappe.model.document import Document
from erpnext_woocommerce.woocommerce_requests import get_request
from erpnext_woocommerce.exceptions import woocommerceSetupError

class woocommerceSettings(Document):
	def validate(self):
		if self.enable_woocommerce == 1:
			self.validate_access_credentials()
			self.validate_access()

	def validate_access_credentials(self):
		if self.app_type == "Private":
			if not (self.get_password(raise_exception=False) and self.api_key and self.woocommerce_url):
				frappe.msgprint(_("Missing value for Password, API Key or woocommerce URL"), raise_exception=woocommerceSetupError)

		else:
			if not (self.access_token and self.woocommerce_url):
				frappe.msgprint(_("Access token or woocommerce URL missing"), raise_exception=woocommerceSetupError)

	def validate_access(self):
		try:
			get_request('/admin/products.json', {"api_key": self.api_key,
				"password": self.get_password(raise_exception=False), "woocommerce_url": self.woocommerce_url,
				"access_token": self.access_token, "app_type": self.app_type})

		except requests.exceptions.HTTPError:
			# disable woocommerce!
			frappe.db.rollback()
			self.set("enable_woocommerce", 0)
			frappe.db.commit()

			frappe.throw(_("""Invalid woocommerce app credentials or access token"""), woocommerceSetupError)


@frappe.whitelist()
def get_series():
		return {
			"sales_order_series" : frappe.get_meta("Sales Order").get_options("naming_series") or "SO-woocommerce-",
			"sales_invoice_series" : frappe.get_meta("Sales Invoice").get_options("naming_series")  or "SI-woocommerce-",
			"delivery_note_series" : frappe.get_meta("Delivery Note").get_options("naming_series")  or "DN-woocommerce-"
		}
