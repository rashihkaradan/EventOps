frappe.ui.form.on('Booking', {
  ticket_type: function(frm) {
      if (frm.doc.ticket_type) {
          frappe.call({
              method: "frappe.client.get_list",
              args: {
                  doctype: "Item Price",
                  filters: {
                      item_code: frm.doc.ticket_type, // this must match Item.item_code
                      price_list: "Standard Selling"
                  },
                  fields: ["price_list_rate"],
                  limit_page_length: 1
              },
              callback: function(r) {
                  if (r.message && r.message.length > 0) {
                      frm.set_value('price', r.message[0].price_list_rate);
                  } else {
                      frm.set_value('price', 0);
                      frappe.msgprint(__('No price found for this ticket type.'));
                  }
              }
          });
      }
  }
});

/*frappe.ui.form.on('Booking', {
  price: function(frm) {
      frm.set_value('total_amount', (frm.doc.price || 0) * (frm.doc.quantity || 0));
  },
  quantity: function(frm) {
      frm.set_value('total_amount', (frm.doc.price || 0) * (frm.doc.quantity || 0));
  }
});
*/
