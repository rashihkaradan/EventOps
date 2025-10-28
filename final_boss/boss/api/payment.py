# ---------------------------------------------------------------------
#  PAYMENT CREATION FOR BOOKING WEB FORM
# ---------------------------------------------------------------------
import frappe

@frappe.whitelist(allow_guest=True)
def create_payment_for_booking(booking_name):
    frappe.logger().info(f"Received booking_name: {booking_name}")

    if not booking_name:
        return "Error: Missing booking_name"

    booking = frappe.get_doc("Booking", booking_name)
    if not booking:
        return "Error: Booking not found"

    # Example Razorpay link (replace with your real order creation)
    return f"/razorpay-checkout?booking={booking_name}"


    try:
        booking = frappe.get_doc("Booking", booking_name)

        # Validate amount and customer
        if not booking.total_amount:
            frappe.throw("Booking total amount is missing.")
        if not booking.attendee:
            frappe.throw("Booking attendee/customer not set.")

        # Create a payment request (Razorpay gateway must exist)
        payment_request = frappe.get_doc({
            "doctype": "Payment Request",
            "payment_gateway": "Razorpay",
            "party_type": "Customer",
            "party": booking.attendee,
            "reference_doctype": "Booking",
            "reference_name": booking.name,
            "currency": "INR",
            "grand_total": booking.total_amount,
            "message": f"Payment for booking {booking.name}",
            "redirect_to": get_url("/payment-success")
        })
        payment_request.insert(ignore_permissions=True)
        payment_request.submit()

        # Return payment URL for redirect
        return payment_request.get_payment_url()

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Payment Creation Failed")
        return f"Error: {str(e)}"


    # ✅ Create Payment Request
    payment_request = frappe.get_doc({
        "doctype": "Payment Request",
        "payment_gateway_account": "Razorpay - INR",  # Must exist in Payments → Payment Gateway Account
        "party_type": "Customer",
        "party": booking.customer or booking.attendee,
        "reference_doctype": "Booking",
        "reference_name": booking.name,
        "currency": "INR",
        "grand_total": booking.total_amount,
        "message": f"Payment for Booking {booking.name}",
        "redirect_to": "/payment-success",  # Web page after successful payment
    })
    payment_request.insert(ignore_permissions=True)
    payment_request.submit()

    # ✅ Link back to Booking
    booking.db_set("payment_request", payment_request.name)

    # ✅ Return Payment URL
    return payment_request.get_payment_url()


