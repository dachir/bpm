from . import __version__ as app_version

app_name = "bpm"
app_title = "Business Process Management"
app_publisher = "Kossivi"
app_description = "Business Process Management App"
app_email = "dodziamouzou@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/bpm/css/bpm.css"
# app_include_js = "/assets/bpm/js/bpm.js"

# include js, css files in header of web template
# web_include_css = "/assets/bpm/css/bpm.css"
# web_include_js = "/assets/bpm/js/bpm.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "bpm/public/scss/website"

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

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "bpm.utils.jinja_methods",
#	"filters": "bpm.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "bpm.install.before_install"
# after_install = "bpm.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "bpm.uninstall.before_uninstall"
# after_uninstall = "bpm.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "bpm.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "BPM Supplier Master Creation": {
        "validate": "erpmco.utils.purchase_receipt.share_document",
    },
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"bpm.tasks.all"
#	],
#	"daily": [
#		"bpm.tasks.daily"
#	],
#	"hourly": [
#		"bpm.tasks.hourly"
#	],
#	"weekly": [
#		"bpm.tasks.weekly"
#	],
#	"monthly": [
#		"bpm.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "bpm.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "bpm.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "bpm.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["bpm.utils.before_request"]
# after_request = ["bpm.utils.after_request"]

# Job Events
# ----------
# before_job = ["bpm.utils.before_job"]
# after_job = ["bpm.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"bpm.auth.validate"
# ]
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "Business Process Management"]]},
    {"dt": "Client Script", "filters": [["enabled", "=", 1],["module", "=", "Business Process Management"]]},
    {"dt": "Server Script", "filters": [["disabled", "=", 0],["module", "=", "Business Process Management"]]},
]