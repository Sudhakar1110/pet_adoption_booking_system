import frappe
from frappe.model.document import Document

class Pet(Document):
    def validate(self):
        if self.age and self.age < 0:
            frappe.throw("Age cannot be negative")
