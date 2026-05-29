import frappe

app_name = "pet_adoption_booking"
app_title = "Pet Adoption"
app_publisher = "Sudhakar"
app_description = "Online Pet Adoption Application for ERPNext v15"
app_email = "sudhakar@gmail.com"
app_license = "MIT"
app_version = "0.0.1"

# ---------------------------------------------------
# Assets
# ---------------------------------------------------
app_include_css = "/assets/pet_adoption_booking/css/vrm_adoption.css"
app_include_js = "/assets/pet_adoption_booking/js/vrm_adoption.js"
web_include_css = "/assets/pet_adoption_booking/css/vrm_adoption.css"
web_include_js = "/assets/pet_adoption_booking/js/vrm_adoption.js"

# ---------------------------------------------------
# Website Routes
# ---------------------------------------------------
website_route_rules = [
    {"from_route": "/pets", "to_route": "pets"},
    {"from_route": "/book-adoption", "to_route": "book_adoption"},
]

# ---------------------------------------------------
# Website context data (available on all web pages)
# ---------------------------------------------------
def get_website_context(context):
    """Add global context for all web pages."""
    if not hasattr(context, "center_name"):
        try:
            settings = frappe.get_single("Adoption Settings")
            context.center_name = settings.center_name or "Happy Tails Adoption Center"
        except Exception:
            context.center_name = "Happy Tails Adoption Center"

# ---------------------------------------------------
# Boot Session - data to include in every page boot
# ---------------------------------------------------
def boot_session(bootinfo):
    """Add adoption settings to boot info."""
    try:
        settings = frappe.get_single("Adoption Settings")
        bootinfo.adoption_settings = {
            "center_name": settings.center_name or "Happy Tails Adoption Center",
            "default_adoption_fee": settings.default_adoption_fee or 0,
        }
    except Exception:
        bootinfo.adoption_settings = {}

# ---------------------------------------------------
# Scheduled Tasks
# ---------------------------------------------------
scheduler_events = {
    "daily": [
        "pet_adoption_booking.tasks.send_booking_reminders"
    ],
    "daily_long": [
        "pet_adoption_booking.tasks.auto_cancel_expired_bookings"
    ]
}

# ---------------------------------------------------
# Fixtures for default data
# ---------------------------------------------------
fixtures = [
    {"dt": "Pet Category"},
    {"dt": "Pet Breed"},
    {"dt": "Adoption Settings"},
]

# ---------------------------------------------------
# Permissions
# ---------------------------------------------------
permission_query_conditions = {
    "Adoption Booking": "pet_adoption_booking.api.get_permission_query_conditions",
}

