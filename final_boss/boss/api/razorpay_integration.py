import frappe
import razorpay
from frappe import _
from frappe.utils import flt
from frappe.integrations.utils import create_request_log, create_payment_gateway, make_post_request

@frappe.whitelist(allow_guest=True)
def get_payment_gateway_controller(payment_gateway_name: str):
    """
    Safely get payment gateway controller for the given gateway name.
    """
    try:
        gateway_doc = frappe.get_doc("Payment Gateway", payment_gateway_name)
    except Exception as e:
        frappe.throw(f"Payment Gateway '{payment_gateway_name}' not found: {e}")

    if gateway_doc.gateway_controller:
        try:
            return frappe.get_doc(gateway_doc.gateway_settings, gateway_doc.gateway_controller)
        except Exception as e:
            frappe.throw(f"Error loading gateway controller: {e}")

    # fallback to <Payment Gateway> Settings doc
    settings_doctype = f"{payment_gateway_name} Settings"
    if frappe.db.exists("DocType", settings_doctype):
        try:
            return frappe.get_doc(settings_doctype)
        except Exception as e:
            frappe.throw(f"Error loading settings doc '{settings_doctype}': {e}")

    frappe.throw(f"Payment Gateway controller/settings not found for '{payment_gateway_name}'")


@frappe.whitelist()
def create_razorpay_order(booking_name):
    """Create a Razorpay Order for the given Booking"""
    booking = frappe.get_doc("Booking", booking_name)
    if not booking.total_amount:
        frappe.throw(_("Booking must have a total amount."))

    settings = frappe.get_single("Razorpay Settings")
    client = razorpay.Client(auth=(settings.api_key, settings.api_secret))

    amount_paise = int(flt(booking.total_amount) * 100)
    order_data = {
        "amount": amount_paise,
        "currency": "INR",
        "payment_capture": 1
    }

    order = client.order.create(order_data)

    booking.razorpay_order_id = order.get("id")
    booking.save(ignore_permissions=True)

    return {
        "order_id": order.get("id"),
        "amount": amount_paise,
        "currency": "INR",
        "booking_name": booking.name
    }


@frappe.whitelist(allow_guest=True)
def verify_razorpay_payment(razorpay_payment_id, razorpay_order_id, razorpay_signature, booking_name):
    """Verify Razorpay payment signature"""
    settings = frappe.get_single("Razorpay Settings")
    client = razorpay.Client(auth=(settings.api_key, settings.api_secret))

    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature
        })

        # update booking
        booking = frappe.get_doc("Booking", booking_name)
        booking.payment_status = "Paid"
        booking.razorpay_payment_id = razorpay_payment_id
        booking.save(ignore_permissions=True)

        frappe.db.commit()
        return {"status": "success", "message": "Payment verified successfully"}

    except razorpay.errors.SignatureVerificationError:
        frappe.throw(_("Payment signature verification failed."))
