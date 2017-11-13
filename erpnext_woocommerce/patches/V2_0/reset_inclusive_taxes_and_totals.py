import frappe
from erpnext_woocommerce.woocommerce_requests import get_woocommerce_orders, get_request
from frappe.utils import cstr
from frappe import _

def execute():
	woocommerce_settings = frappe.db.get_value("woocommerce Settings", None,
		["enable_woocommerce", "woocommerce_url"], as_dict=1)

	if not (woocommerce_settings and woocommerce_settings.enable_woocommerce and woocommerce_settings.woocommerce_url):
		return
	
	try:
		woocommerce_orders = get_woocommerce_orders(ignore_filter_conditions=True)
		woocommerce_orders = build_woocommerce_order_dict(woocommerce_orders, key="id")
	except:
		return

	for so in frappe.db.sql("""select name, woocommerce_order_id, discount_amount from `tabSales Order` 
		where woocommerce_order_id is not null and woocommerce_order_id != '' and
		docstatus=1 and discount_amount > 0""", as_dict=1):
		
		try:
			woocommerce_order = woocommerce_orders.get(so.woocommerce_order_id) or {}
			
			if so.woocommerce_order_id not in woocommerce_orders:
				woocommerce_order = get_request("/admin/orders/{0}.json".format(so.woocommerce_order_id))["order"]
			
			if woocommerce_order.get("taxes_included"):
				so = frappe.get_doc("Sales Order", so.name)

				setup_inclusive_taxes(so, woocommerce_order)
				so.calculate_taxes_and_totals()
				so.set_total_in_words()
				db_update(so)

				update_si_against_so(so, woocommerce_order)
				update_dn_against_so(so, woocommerce_order)

				frappe.db.commit()
		except Exception:
			pass

def setup_inclusive_taxes(doc, woocommerce_order):
	doc.apply_discount_on = "Grand Total"
	woocommerce_taxes = get_woocommerce_tax_settigns(woocommerce_order)
	
	for tax in doc.taxes:
		if tax.account_head in woocommerce_taxes:
			tax.charge_type = _("On Net Total")
			tax.included_in_print_rate = 1
#
def update_si_against_so(so, woocommerce_order):
	si_name =frappe.db.sql_list("""select distinct t1.name
		from `tabSales Invoice` t1,`tabSales Invoice Item` t2
		where t1.name = t2.parent and t2.sales_order = %s and t1.docstatus = 1""", so.name)
	
	if si_name:
		si = frappe.get_doc("Sales Invoice", si_name[0])
		
		si.docstatus = 2
		si.update_prevdoc_status()
		si.make_gl_entries_on_cancel()
		
		si.docstatus = 1
		setup_inclusive_taxes(si, woocommerce_order)
		si.calculate_taxes_and_totals()
		si.set_total_in_words()
		si.update_prevdoc_status()
		si.make_gl_entries()
		
		db_update(si)
		
def update_dn_against_so(so, woocommerce_order):
	dn_name =frappe.db.sql_list("""select distinct t1.name
		from `tabDelivery Note` t1,`tabdelivery Note Item` t2
		where t1.name = t2.parent and t2.against_sales_order = %s and t1.docstatus = 0""", so.name)
	
	if dn_name:
		dn = frappe.get_doc("Delivery Note", dn_name[0])

		setup_inclusive_taxes(dn, woocommerce_order)
		dn.calculate_taxes_and_totals()
		dn.set_total_in_words()

		db_update(dn)

def db_update(doc):
	doc.db_update()
	for df in doc.meta.get_table_fields():
		for d in doc.get(df.fieldname):
			d.db_update()

def build_woocommerce_order_dict(sequence, key):
	return dict((cstr(d[key]), dict(d, index=index)) for (index, d) in enumerate(sequence))

def get_woocommerce_tax_settigns(woocommerce_order):
	woocommerce_taxes = []
	for tax in woocommerce_order.get("tax_lines"):
		woocommerce_taxes.extend(map(lambda d: d.tax_account if d.woocommerce_tax == tax["title"] else "", frappe.get_doc("woocommerce Settings").taxes))
	
	return set(woocommerce_taxes)
