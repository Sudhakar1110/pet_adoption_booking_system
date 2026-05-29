import frappe
from frappe.utils import getdate, today, add_days


def send_booking_reminders():
    """Daily task: Send reminders for upcoming bookings (next day)."""
    tomorrow = add_days(today(), 1)
    
    bookings = frappe.get_all(
        "Adoption Booking",
        filters={
            "booking_date": tomorrow,
            "status": "Scheduled",
            "docstatus": 1
        },
        fields=["name", "adopter", "pet"]
    )
    
    for booking in bookings:
        try:
            adopter = frappe.get_doc("Adopter", booking.adopter)
            pet = frappe.get_doc("Pet", booking.pet)
            
            # Create a reminder ToDo
            frappe.get_doc({
                "doctype": "ToDo",
                "description": f"""
                    Reminder: Adoption visit tomorrow!
                    Pet: {pet.pet_name}
                    Adopter: {adopter.adopter_name} ({adopter.email})
                    Booking: {booking.name}
                """.strip(),
                "reference_type": "Adoption Booking",
                "reference_name": booking.name,
                "assigned_by": "Administrator",
                "priority": "High"
            }).insert(ignore_permissions=True)
            
        except Exception as e:
            frappe.log_error(f"Failed to send reminder for booking {booking.name}: {str(e)}",
                             "Adoption Booking Reminder")


def auto_cancel_expired_bookings():
    """Daily task: Auto-cancel bookings past their date that are still in Draft."""
    today_date = getdate(today())
    
    expired = frappe.get_all(
        "Adoption Booking",
        filters={
            "booking_date": ["<", today_date],
            "status": ["in", ["Draft", "Scheduled"]],
            "docstatus": ["<", 2]
        },
        fields=["name", "booking_date", "time_slot"]
    )
    
    for booking in expired:
        try:
            frappe.db.set_value("Adoption Booking", booking.name, "status", "Cancelled")
            frappe.db.set_value("Adoption Booking", booking.name, "notes",
                                f"Auto-cancelled: Booking date {booking.booking_date} has passed.")
        except Exception as e:
            frappe.log_error(f"Failed to auto-cancel booking {booking.name}: {str(e)}",
                             "Adoption Booking Auto-Cancel")
