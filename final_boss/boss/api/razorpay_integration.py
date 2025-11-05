import frappe
import razorpay
from frappe import _
from frappe.utils import flt, nowdate
from final_boss.boss.api.booking import make_sales_order, create_invoice_and_payment


# ---------------------------------------------------------------------
# GET PAYMENT GATEWAY CONTROLLER
# ---------------------------------------------------------------------
@frappe.whitelist(allow_guest=True)
def get_payment_gateway_controller(payment_gateway_name: str):
    """Safely load the configured payment gateway controller."""
    try:
        gateway_doc = frappe.get_doc("Payment Gateway", payment_gateway_name)
    except Exception as e:
        frappe.throw(f"Payment Gateway '{payment_gateway_name}' not found: {e}")

    if gateway_doc.gateway_controller:
        try:
            return frappe.get_doc(gateway_doc.gateway_settings, gateway_doc.gateway_controller)
        except Exception as e:
            frappe.throw(f"Error loading gateway controller: {e}")

    settings_doctype = f"{payment_gateway_name} Settings"
    if frappe.db.exists("DocType", settings_doctype):
        return frappe.get_doc(settings_doctype)

    frappe.throw(f"Payment Gateway controller/settings not found for '{payment_gateway_name}'")


# ---------------------------------------------------------------------
# 1️⃣ CREATE RAZORPAY ORDER
# ---------------------------------------------------------------------
@frappe.whitelist(allow_guest=True)
def create_razorpay_order(booking_name):
    """
    Create a Razorpay Order for a Booking and ensure the Order ID
    is saved before redirecting to the payment form.
    """
    booking = frappe.get_doc("Booking", booking_name)

    if not booking.total_amount:
        frappe.throw(_("Booking must have a total amount."))

    # Load Razorpay API credentials
    settings = frappe.get_single("Razorpay Settings")
    client = razorpay.Client(auth=(settings.api_key, settings.api_secret))

    # Create order in Razorpay
    order_data = {
        "amount": int(flt(booking.total_amount) * 100),  # in paise
        "currency": "INR",
        "receipt": booking.name,
        "payment_capture": 1,
    }

    order = client.order.create(order_data)
    razorpay_order_id = order.get("id")

    if not razorpay_order_id:
        frappe.throw(_("Failed to create Razorpay order."))

    # ✅ Save immediately before returning (critical!)
    booking.db_set("razorpay_order_id", razorpay_order_id, update_modified=False)
    booking.db_set("payment_status", "Pending", update_modified=False)
    frappe.db.commit()

    frappe.logger("razorpay_debug").info(
        f"[Razorpay] Created order for Booking {booking.name}: {razorpay_order_id}"
    )

    # Return order details to frontend
    return {
        "order_id": razorpay_order_id,
        "amount": order_data["amount"],
        "currency": order_data["currency"],
        "booking_name": booking.name,
    }



# ---------------------------------------------------------------------
# 2️⃣ VERIFY PAYMENT + CREATE SALES FLOW
# ---------------------------------------------------------------------
@frappe.whitelist(allow_guest=True)
def verify_razorpay_payment(razorpay_payment_id, razorpay_order_id, razorpay_signature, booking_name):
    """Verify Razorpay payment and create Sales Order → Invoice → Payment."""
    settings = frappe.get_single("Razorpay Settings")
    client = razorpay.Client(auth=(settings.api_key, settings.api_secret))

    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature
        })

        booking = frappe.get_doc("Booking", booking_name)
        booking.payment_status = "Paid"
        booking.razorpay_payment_id = razorpay_payment_id
        booking.razorpay_order_id = razorpay_order_id
        booking.save(ignore_permissions=True)

        # Create ERPNext docs as system user (avoid guest permission issue)
        frappe.enqueue(
            "final_boss.boss.api.razorpay_integration.create_sales_flow",
            queue="short",
            booking_name=booking_name,
            now=False
        )

        return {"status": "success", "message": "Payment verified. Sales flow will be created."}

    except razorpay.errors.SignatureVerificationError:
        frappe.throw(_("Payment signature verification failed."))
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Razorpay Verification Error")
        frappe.throw(_("Error verifying Razorpay payment: {0}").format(str(e)))


# ---------------------------------------------------------------------
# 3️⃣ CREATE SALES FLOW (SYSTEM JOB)
# ---------------------------------------------------------------------
@frappe.whitelist()
def create_sales_flow(booking_name):
    """Create Sales Order → Invoice → Payment Entry from Booking (runs as Administrator)."""
    try:
        frappe.set_user("Administrator")
        booking = frappe.get_doc("Booking", booking_name)

        so = make_sales_order(booking_name)
        create_invoice_and_payment(so["name"])

        frappe.logger().info(f"[Razorpay Flow] Booking {booking_name} completed.")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Razorpay Create Sales Flow Error")
    finally:
        frappe.set_user("Guest")
