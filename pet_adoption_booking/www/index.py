import frappe

def get_context(context):
    """Redirect root URL to the pets listing page."""
    frappe.local.flags.redirect_to = "/pets"
