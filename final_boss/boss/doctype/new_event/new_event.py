import frappe
from frappe.model.document import Document

class NewEvent(Document):
    website = frappe._dict(
        condition_field="name"   # change to "route" if you have a route field
    )

def get_list_context(context=None):
    return {
        "title": "Events",
        "show_sidebar": True,
        "show_search": True,
        "no_breadcrumbs": False,
        "filters": {"published": 1},
        "row_template": "templates/includes/event_row.html"
    }
