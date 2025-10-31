frappe.web_form.on('after_save', async function() {
    const totalAmount = frappe.web_form.get_value('total_amount');
    const attendeeEmail = frappe.web_form.get_value('attendee_email');
    const attendee = frappe.web_form.get_value('attendee');

    // Create Payment Request using built-in API
    const r = await frappe.call({
        method: "frappe.website.doctype.web_form.web_form.create_payment_request",
        args: {
            reference_doctype: "Booking",  // replace with your Doctype name
            reference_name: frappe.web_form.doc.name,
            party_type: "Customer",
            party: attendee,
            email: attendeeEmail,
            amount: totalAmount,
            payment_gateway: "Razorpay"
        }
    });

    if (r.message) {
        window.location.href = r.message;  // Redirects to Razorpay payment page
    } else {
        frappe.msgprint("Payment could not be initiated.");
    }
});
    