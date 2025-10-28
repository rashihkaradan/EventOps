import frappe
from frappe.website.doctype.web_form.web_form import WebForm

def patched_get_payment_gateway_url(self, doc):
    """Recreate missing method to fix Accept Payments flow"""
    from payments.utils import create_payment_gateway_url
    return create_payment_gateway_url(doc)

# Apply patch dynamically
WebForm.get_payment_gateway_url = patched_get_payment_gateway_url
