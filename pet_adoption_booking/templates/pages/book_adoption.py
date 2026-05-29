import frappe

def get_context(context):
    pet_name = frappe.form_dict.get("pet")
    if pet_name:
        context.pet = frappe.get_doc("Pet", pet_name)
    else:
        context.pet = None

    context.pets = frappe.get_all(
        "Pet",
        filters={"status": "Available"},
        fields=["name", "pet_name", "breed"]
    )
    
    context.user_logged_in = frappe.session.user != "Guest"
    if context.user_logged_in:
        context.user_email = frappe.session.user
        adopter = frappe.get_all("Adopter", filters={"email": frappe.session.user}, 
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
            context.adopter_name = frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user.split("@")[0]
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
