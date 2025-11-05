frappe.web_form.on('booking-form', (field, value) => {
    if (value) {
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Item Price",
                filters: {
                    item_code: value,
                    price_list: "Standard Selling"
                },
                fields: ["price_list_rate"],
                limit_page_length: 1
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    frappe.web_form.set_value('price', r.message[0].price_list_rate);
                } else {
                    frappe.web_form.set_value('price', 0);
                    frappe.msgprint(__('No price found for this ticket type.'));
                }
            }
        });
    }
});
