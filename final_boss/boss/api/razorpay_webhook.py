import frappe
import razorpay
import json
from frappe import _
from frappe.utils import flt
from final_boss.boss.doctype.booking.booking import make_sales_order, create_invoice_and_payment


@frappe.whitelist(allow_guest=True)
def razorpay_webhook():
    """
    Handle Razorpay Webhook POST requests.
    """
    frappe.log_error("Webhook","Webhook reieved")
    try:
        # Razorpay sends JSON body
        payload = frappe.request.data
        event = json.loads(payload.decode("utf-8"))
        signature = frappe.get_request_header("X-Razorpay-Signature")

        settings = frappe.get_single("Razorpay Settings")
        client = razorpay.Client(auth=(settings.api_key, settings.api_secret))
        '''
        # ✅ Verify signature for security
        client.utility.verify_webhook_signature(
            payload, signature, settings.webhook_secret
        )
        '''
        event_type = event.get("event")
        frappe.logger("razorpay_webhook").info(f"Razorpay Webhook Event: {event_type}")

        if event_type == "payment.captured":
            handle_payment_captured(event)
        elif event_type == "payment.failed":
            handle_payment_failed(event)
        else:
            frappe.logger("razorpay_webhook").info(f"Ignored event: {event_type}")

        frappe.local.response["http_status_code"] = 200
        return "Webhook processed successfully"

    except razorpay.errors.SignatureVerificationError:
        frappe.log_error("Razorpay Webhook signature verification failed", "Razorpay Webhook Error")
        frappe.local.response["http_status_code"] = 400
        return "Invalid signature"
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Razorpay Webhook Processing Error")
        frappe.local.response["http_status_code"] = 500
        return f"Webhook error: {e}"


# ---------------------------------------------------------------------
# 🟢 Handle Successful Payment
# ---------------------------------------------------------------------
def handle_payment_captured(event):
    """
    Create Sales Order, Payment Entry, and Sales Invoice once payment is captured.
    """
    payment_entity = event.get("payload", {}).get("payment", {}).get("entity", {})
    razorpay_payment_id = payment_entity.get("id")
    razorpay_order_id = payment_entity.get("order_id")
    amount = flt(payment_entity.get("amount")) / 100

    # Get booking using Razorpay Order ID
    booking_name = frappe.db.get_value("Booking", {"razorpay_order_id": razorpay_order_id}, "name")
    if not booking_name:
        frappe.log_error(f"No Booking found for Razorpay Order {razorpay_order_id}", "Webhook Booking Lookup Failed")
        return

    booking = frappe.get_doc("Booking", booking_name)
    if booking.payment_status == "Paid":
        frappe.logger("razorpay_webhook").info(f"Booking {booking.name} already processed.")
        return  # avoid duplicate processing

    # Update Booking payment details
    booking.payment_status = "Paid"
    booking.razorpay_payment_id = razorpay_payment_id
    booking.save(ignore_permissions=True)

    # Create downstream ERPNext docs
    frappe.enqueue(
        "final_boss.boss.api.razorpay_webhook.create_sales_flow",
        booking_name=booking_name,
        now=False
    )

    frappe.logger("razorpay_webhook").info(
        f"[Webhook] Payment captured for {booking_name}, amount ₹{amount}"
    )

    frappe.logger("razorpay_webhook").info(f"Webhook booking lookup: {razorpay_order_id}")


# ---------------------------------------------------------------------
# 🔴 Handle Failed Payment
# ---------------------------------------------------------------------
def handle_payment_failed(event):
    payment_entity = event.get("payload", {}).get("payment", {}).get("entity", {})
    razorpay_order_id = payment_entity.get("order_id")

    booking_name = frappe.db.get_value("Booking", {"razorpay_order_id": razorpay_order_id}, "name")
    if not booking_name:
        frappe.log_error(f"No Booking found for failed Razorpay order {razorpay_order_id}", "Razorpay Payment Failed")
        return

    booking = frappe.get_doc("Booking", booking_name)
    booking.payment_status = "Pending"
    booking.save(ignore_permissions=True)

    frappe.logger("razorpay_webhook").info(f"[Webhook] Payment failed for Booking {booking_name}")


# ---------------------------------------------------------------------
# 🧾 Background Job: Create Sales Flow
# ---------------------------------------------------------------------
@frappe.whitelist()
def create_sales_flow(booking_name):
    """
    Creates Sales Order → Sales Invoice → Payment Entry from Booking.
    Runs in background as Administrator.
    """
    try:
        frappe.set_user("Administrator")
        booking = frappe.get_doc("Booking", booking_name)

        # Create Sales Order
        so = make_sales_order(booking_name)
        # Create Sales Invoice + Payment Request
        create_invoice_and_payment(so.name)

        frappe.logger("razorpay_webhook").info(f"[Webhook] Completed Sales Flow for {booking_name}")

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Webhook Sales Flow Creation Error")
    finally:
        frappe.set_user("Guest")
