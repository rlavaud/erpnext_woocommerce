source_link = "https://github.com/frappe/erpnext_woocommerce"
docs_base_url = "https://frappe.github.io/erpnext_woocommerce"
headline = "ERPNext woocommerce Connector"
sub_heading = "Sync transactions between woocommerce and ERPNext"
long_description = """ERPNext woocommerce Connector will sync data between your woocommerce and ERPNext accounts.
<br>
<ol>
	<li> It will sync Products and Cutomers between woocommerce and ERPNext</li>
	<li> It will push Orders from woocommerce to ERPNext
		<ul>
			<li>
				If the Order has been paid for in woocommerce, it will create a Sales Invoice in ERPNext and record the corresponding Payment Entry
			</li>
			<li>
				If the Order has been fulfilled in woocommerce, it will create a draft Delivery Note in ERPNext
			</li>
		</ul>
	</li>
</ol>"""
docs_version = "1.0.0"

def get_context(context):
	context.title = "ERPNext woocommerce Connector"
