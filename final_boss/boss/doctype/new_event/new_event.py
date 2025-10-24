from frappe.model.document import Document

class NewEvent(Document):
    # Your methods here
    pass
def get_list_context(context=None):
    return {
        "title": "Events",
        "show_sidebar": True,
        "show_search": True,
        "no_breadcrumbs": False,
        "filters": {"published": 1},
        "row_template": "templates/includes/event_row.html"
    }
