import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today

class AdoptionBooking(Document):
    def validate(self):
        self.check_date()
        self.check_pet_availability()
        self.check_slot_clash()

    def check_date(self):
        if getdate(self.booking_date) < getdate(today()):
            frappe.throw("Booking date cannot be in the past.")

    def check_pet_availability(self):
        pet_status = frappe.db.get_value("Pet", self.pet, "status")
        if pet_status in ["Adopted", "Not Available"]:
            frappe.throw(f"Pet {self.pet} is already adopted or not available.")

    def check_slot_clash(self):
        clash = frappe.db.exists("Adoption Booking", {
            "pet": self.pet,
            "booking_date": self.booking_date,
            "time_slot": self.time_slot,
            "docstatus": ["<", 2],
            "status": ["not in", ["Cancelled", "Rejected"]],
            "name": ["!=", self.name or ""]
        })
        if clash:
            frappe.throw(f"This pet already has a meeting scheduled at {self.time_slot} on {self.booking_date}.")

    def on_update(self):
        if self.status == "Completed" and not self.sales_invoice:
            self.complete_adoption()

    def on_submit(self):
        # When submitted, change status from Draft to Scheduled
        if self.status == "Draft":
            self.db_set("status", "Scheduled")

    def complete_adoption(self):
        # Update Pet status to Adopted
        frappe.db.set_value("Pet", self.pet, "status", "Adopted")

        # Check if there is an adoption fee
        fee = frappe.db.get_value("Pet", self.pet, "adoption_fee") or 0
        if fee > 0:
            self.create_sales_invoice(fee)

    def create_sales_invoice(self, fee):
        email = frappe.db.get_value("Adopter", self.adopter, "email")
        adopter_name = frappe.db.get_value("Adopter", self.adopter, "adopter_name")

        customer = self.get_or_create_customer(email, adopter_name)
        item = self.get_or_create_service_item()

        si = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": customer,
            "due_date": today(),
            "items": [{
                "item_code": item,
                "qty": 1,
                "rate": fee,
                "description": f"Pet Adoption Fee for booking {self.name} ({self.pet})"
            }]
        })
        si.insert(ignore_permissions=True)
        si.submit()
        self.db_set("sales_invoice", si.name)

    def get_or_create_customer(self, email, adopter_name):
        customer = frappe.db.get_value("Customer", {"email_id": email}, "name")
        if not customer:
            cust = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": adopter_name,
                "customer_type": "Individual",
                "email_id": email
            })
            cust.insert(ignore_permissions=True)
            customer = cust.name
        return customer

    def get_or_create_service_item(self):
        settings = frappe.get_single("Adoption Settings")
        item = settings.fee_item_code or "ADOPTION-SERVICE"

        if not frappe.db.exists("Item", item):
            frappe.get_doc({
                "doctype": "Item",
                "item_code": item,
                "item_group": "All Item Groups",
                "stock_uom": "Nos",
                "is_stock_item": 0,
                "item_name": "Pet Adoption Service Fee"
            }).insert(ignore_permissions=True)

        return item
