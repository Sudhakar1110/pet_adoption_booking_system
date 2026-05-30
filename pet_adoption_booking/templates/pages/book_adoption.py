import frappe


def get_context(context):
    """Get context for the booking page with safe error handling."""
    pet_name = frappe.form_dict.get("pet")
    if pet_name:
        try:
            context.pet = frappe.get_doc("Pet", pet_name)
        except Exception:
            context.pet = None
    else:
        context.pet = None

    try:
        context.pets = frappe.get_all(
            "Pet",
            filters={"status": "Available"},
            fields=["name", "pet_name", "breed"]
        )
    except Exception:
        context.pets = []

    context.user_logged_in = frappe.session.user != "Guest"
    if context.user_logged_in:
        user_email = frappe.session.user
        context.user_email = user_email
        try:
            adopter = frappe.get_all("Adopter", filters={"email": user_email},
                                     fields=["adopter_name", "phone", "address", "housing_type",
                                             "has_children", "has_other_pets"], limit=1)
            if adopter:
                context.adopter_name = adopter[0].adopter_name
                context.adopter_phone = adopter[0].phone or ""
                context.adopter_address = adopter[0].address or ""
                context.housing_type = adopter[0].housing_type or "Apartment"
                context.has_children = adopter[0].has_children or 0
                context.has_other_pets = adopter[0].has_other_pets or 0
            else:
                context.adopter_name = frappe.db.get_value("User", user_email, "full_name") or user_email.split("@")[0]
                context.adopter_phone = ""
                context.adopter_address = ""
                context.housing_type = "Apartment"
                context.has_children = 0
                context.has_other_pets = 0
        except Exception:
            context.adopter_name = frappe.db.get_value("User", user_email, "full_name") or user_email.split("@")[0]
            context.adopter_phone = ""
            context.adopter_address = ""
            context.housing_type = "Apartment"
            context.has_children = 0
            context.has_other_pets = 0
    else:
        context.user_email = ""
        context.adopter_name = ""
        context.adopter_phone = ""
        context.adopter_address = ""
        context.housing_type = "Apartment"
        context.has_children = 0
        context.has_other_pets = 0

    context.no_cache = 1
    return context
