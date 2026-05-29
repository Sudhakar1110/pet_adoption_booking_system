import frappe

def get_context(context):
    context.categories = frappe.get_all("Pet Category", fields=["name", "category_name", "image"])
    context.breeds = frappe.get_all("Pet Breed", fields=["name", "breed_name", "category"])
    
    context.pets = frappe.get_all(
        "Pet",
        filters={"status": "Available"},
        fields=["name", "pet_name", "category", "breed", "age", "age_unit",
                "gender", "size", "color", "image", "description", "adoption_fee"],
        order_by="category asc, pet_name asc"
    )
    
    settings = frappe.get_single("Adoption Settings")
    context.center_name = settings.center_name or "Happy Tails Adoption Center"
    
    context.no_cache = 1
    return context
