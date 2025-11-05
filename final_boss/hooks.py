app_name = "final_boss"
app_title = "boss"
app_publisher = "rashih"
app_description = "for manage"
app_email = "rashi@gmail.com"
app_license = "mit"

# Apps
# ------------------
web_methods = {
    # Razorpay sends a POST request with the webhook payload
    "POST": {
        # The key is the URL path segment, the value is the full function path
        "razorpay_webhook": "final_boss.boss.api.razorpay_webhook"
}
}
# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "final_boss",
# 		"logo": "/assets/final_boss/logo.png",
# 		"title": "boss",
# 		"route": "/final_boss",
# 		"has_permission": "final_boss.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/final_boss/css/final_boss.css"
# app_include_js = "/assets/final_boss/js/final_boss.js"

# include js, css files in header of web template
# web_include_css = "/assets/final_boss/css/final_boss.css"
# web_include_js = "/assets/final_boss/js/final_boss.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "final_boss/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "final_boss/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "final_boss.utils.jinja_methods",
# 	"filters": "final_boss.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "final_boss.install.before_install"
# after_install = "final_boss.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "final_boss.uninstall.before_uninstall"
# after_uninstall = "final_boss.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "final_boss.utils.before_app_install"
# after_app_install = "final_boss.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "final_boss.utils.before_app_uninstall"
# after_app_uninstall = "final_boss.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "final_boss.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"final_boss.tasks.all"
# 	],
# 	"daily": [
# 		"final_boss.tasks.daily"
# 	],
# 	"hourly": [
# 		"final_boss.tasks.hourly"
# 	],
# 	"weekly": [
# 		"final_boss.tasks.weekly"
# 	],
# 	"monthly": [
# 		"final_boss.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "final_boss.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "final_boss.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "final_boss.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["final_boss.utils.before_request"]
# after_request = ["final_boss.utils.after_request"]

# Job Events
# ----------
# before_job = ["final_boss.utils.before_job"]
# after_job = ["final_boss.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"final_boss.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
# def on_submit(self):
#     from final_boss.boss.api.payment import send_booking_email_with_qr
#     send_booking_email_with_qr(self.name)

    
# doc_events = {
#   "Booking": {
#     "on_submit": "final_boss.boss.doctype.booking.make_sales_order"
#   }
# }




