import frappe
from frappe.utils import getdate, today, now_datetime


@frappe.whitelist(allow_guest=True)
def get_available_pets():
    """Get list of all available pets with details."""
    return frappe.get_all(
        "Pet",
        filters={"status": "Available"},
        fields=["name", "pet_name", "category", "breed", "age", "age_unit",
                "gender", "size", "color", "image", "description", "adoption_fee"],
        order_by="category asc, pet_name asc"
    )


@frappe.whitelist(allow_guest=True)
def get_pet_details(pet_name):
    """Get full details of a specific pet including child table data."""
    pet = frappe.get_doc("Pet", pet_name)
    
    # Get child table data
    medical_history = []
    if hasattr(pet, "medical_history") and pet.medical_history:
        for row in pet.medical_history:
            medical_history.append({
                "date": str(row.date) if row.date else None,
                "condition": row.condition,
                "diagnosis": row.diagnosis,
                "treatment": row.treatment,
                "veterinarian": row.veterinarian,
                "vet_contact": row.vet_contact,
                "notes": row.notes,
                "attachment": row.attachment,
            })
    
    vaccination_details = []
    if hasattr(pet, "vaccination_details") and pet.vaccination_details:
        for row in pet.vaccination_details:
            vaccination_details.append({
                "vaccine_name": row.vaccine_name,
                "vaccination_date": str(row.vaccination_date) if row.vaccination_date else None,
                "next_due_date": str(row.next_due_date) if row.next_due_date else None,
                "veterinarian": row.veterinarian,
                "administered_by": row.administered_by,
                "notes": row.notes,
            })
    
    pet_images = []
    if hasattr(pet, "pet_images_tab") and pet.pet_images_tab:
        for row in pet.pet_images_tab:
            pet_images.append({
                "image": row.image,
                "caption": row.caption,
                "is_primary": row.is_primary,
            })
    
    description_sections = []
    if hasattr(pet, "pet_description_sections") and pet.pet_description_sections:
        for row in pet.pet_description_sections:
            description_sections.append({
                "section_title": row.section_title,
                "content": row.content,
            })
    
    return {
        "name": pet.name,
        "pet_name": pet.pet_name,
        "category": pet.category,
        "breed": pet.breed,
        "age": pet.age,
        "age_unit": pet.age_unit,
        "gender": pet.gender,
        "size": pet.size,
        "color": pet.color,
        "status": pet.status,
        "description": pet.description,
        "image": pet.image,
        "adoption_fee": pet.adoption_fee,
        "health_status": pet.health_status,
        "vaccinated": pet.vaccinated,
        "neutered_spayed": pet.neutered_spayed,
        "medical_history": medical_history,
        "vaccination_details": vaccination_details,
        "pet_images": pet_images,
        "description_sections": description_sections,
    }


@frappe.whitelist(allow_guest=True)
def check_slot_availability(pet, booking_date, time_slot):
    """Check if a time slot is available for a pet."""
    clash = frappe.db.exists("Adoption Booking", {
        "pet": pet,
        "booking_date": booking_date,
        "time_slot": time_slot,
        "docstatus": ["<", 2],
        "status": ["not in", ["Cancelled", "Rejected"]]
    })
    return {"available": not bool(clash)}


@frappe.whitelist(allow_guest=True)
def get_available_time_slots(pet, booking_date):
    """Get list of available time slots for a specific pet on a date."""
    all_slots = [
        "09:00 AM - 10:00 AM",
        "10:00 AM - 11:00 AM",
        "11:00 AM - 12:00 PM",
        "02:00 PM - 03:00 PM",
        "03:00 PM - 04:00 PM",
        "04:00 PM - 05:00 PM"
    ]
    
    booked_slots = frappe.get_all(
        "Adoption Booking",
        filters={
            "pet": pet,
            "booking_date": booking_date,
            "docstatus": ["<", 2],
            "status": ["not in", ["Cancelled", "Rejected"]]
        },
        fields=["time_slot"]
    )
    
    booked_slot_values = [b.time_slot for b in booked_slots]
    available_slots = [slot for slot in all_slots if slot not in booked_slot_values]
    
    return available_slots


@frappe.whitelist(allow_guest=True)
def create_adoption_booking(**kwargs):
    """Create a new adoption booking with full validation."""
    email = kwargs.get("email")
    adopter_name = kwargs.get("adopter_name")
    phone = kwargs.get("phone")
    address = kwargs.get("address")
    housing_type = kwargs.get("housing_type") or "Apartment"
    has_children = frappe.utils.cint(kwargs.get("has_children"))
    has_other_pets = frappe.utils.cint(kwargs.get("has_other_pets"))

    adopter = _get_or_create_adopter(email, adopter_name, phone, address,
                                     housing_type, has_children, has_other_pets)

    pet = kwargs.get("pet")
    if not pet:
        frappe.throw("Please select a pet.")

    booking_date = kwargs.get("booking_date")
    time_slot = kwargs.get("time_slot")
    if not booking_date or not time_slot:
        frappe.throw("Booking Date and Time Slot are required.")

    # Validate date is not in the past
    if getdate(booking_date) < getdate(today()):
        frappe.throw("Booking date cannot be in the past.")

    # Check slot availability
    if not check_slot_availability(pet, booking_date, time_slot).get("available"):
        frappe.throw("This time slot is already booked. Please choose another slot.")

    booking = frappe.get_doc({
        "doctype": "Adoption Booking",
        "adopter": adopter,
        "pet": pet,
        "booking_date": booking_date,
        "time_slot": time_slot,
        "notes": kwargs.get("notes"),
        "status": "Draft"
    })
    
    booking.insert(ignore_permissions=True)
    booking.submit()  # Submit to move from Draft to Scheduled

    # Send confirmation notification
    _send_booking_confirmation(booking.name)

    return {
        "status": "success",
        "message": "Adoption booking submitted successfully!",
        "booking_name": booking.name
    }


@frappe.whitelist(allow_guest=True)
def get_booking_status(booking_name):
    """Get the status of an existing booking."""
    booking = frappe.get_doc("Adoption Booking", booking_name)
    adopter = frappe.get_doc("Adopter", booking.adopter)
    pet = frappe.get_doc("Pet", booking.pet)
    
    return {
        "name": booking.name,
        "status": booking.status,
        "booking_date": str(booking.booking_date),
        "time_slot": booking.time_slot,
        "pet_name": pet.pet_name,
        "adopter_name": adopter.adopter_name,
        "notes": booking.notes
    }


@frappe.whitelist(allow_guest=True)
def cancel_booking(booking_name, reason=None):
    """Cancel an existing booking."""
    booking = frappe.get_doc("Adoption Booking", booking_name)
    if booking.docstatus == 1:  # Submitted
        booking.cancel()
    booking.db_set("status", "Cancelled")
    if reason:
        booking.db_set("notes", reason)
    return {"status": "success", "message": "Booking cancelled successfully."}


@frappe.whitelist()
def get_permission_query_conditions(user=None):
    """Permission query conditions for adoption bookings."""
    if not user:
        user = frappe.session.user
    
    if user == "Administrator":
        return ""
    
    # Guests can only see their own bookings via the API
    if frappe.session.user == "Guest":
        return ""

    return ""


def _get_or_create_adopter(email, adopter_name, phone, address, 
                           housing_type, has_children, has_other_pets):
    """Helper to get or create an adopter record."""
    if frappe.session.user != "Guest":
        user_email = frappe.session.user
        adopter = frappe.db.get_value("Adopter", {"email": user_email}, "name")
        if not adopter:
            user_fullname = frappe.db.get_value("User", user_email, "full_name") or user_email.split("@")[0]
            adopter_doc = frappe.get_doc({
                "doctype": "Adopter",
                "adopter_name": user_fullname,
                "email": user_email,
                "phone": phone,
                "address": address,
                "housing_type": housing_type,
                "has_children": has_children,
                "has_other_pets": has_other_pets
            })
            adopter_doc.insert(ignore_permissions=True)
            adopter = adopter_doc.name
        return adopter
    
    if not email or not adopter_name:
        frappe.throw("Full Name and Email are required for booking.")
    
    adopter = frappe.db.get_value("Adopter", {"email": email}, "name")
    if not adopter:
        adopter_doc = frappe.get_doc({
            "doctype": "Adopter",
            "adopter_name": adopter_name,
            "email": email,
            "phone": phone,
            "address": address,
            "housing_type": housing_type,
            "has_children": has_children,
            "has_other_pets": has_other_pets
        })
        adopter_doc.insert(ignore_permissions=True)
        adopter = adopter_doc.name
    return adopter


def _send_booking_confirmation(booking_name):
    """Send booking confirmation email/notification."""
    try:
        booking = frappe.get_doc("Adoption Booking", booking_name)
        adopter = frappe.get_doc("Adopter", booking.adopter)
        pet = frappe.get_doc("Pet", booking.pet)
        
        settings = frappe.get_single("Adoption Settings")
        center_name = settings.center_name or "Happy Tails Adoption Center"
        
        # Create a ToDo notification for the system manager
        frappe.get_doc({
            "doctype": "ToDo",
            "description": f"""
                New adoption booking received!
                Pet: {pet.pet_name}
                Adopter: {adopter.adopter_name} ({adopter.email})
                Date: {booking.booking_date}
                Time: {booking.time_slot}
                Booking ID: {booking.name}
            """.strip(),
            "reference_type": "Adoption Booking",
            "reference_name": booking.name,
            "assigned_by": "Administrator",
            "priority": "Medium"
        }).insert(ignore_permissions=True)
        
    except Exception as e:
        frappe.log_error(f"Failed to send booking confirmation: {str(e)}",
                         "Adoption Booking Notification")
