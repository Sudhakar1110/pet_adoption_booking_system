import frappe

@frappe.whitelist(allow_guest=True)
def get_available_pets():
    return frappe.get_all(
        "Pet",
        filters={"status": "Available"},
        fields=["pet_name", "breed", "age"]
    )
