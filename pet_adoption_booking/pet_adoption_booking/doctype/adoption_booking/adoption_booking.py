import frappe
from frappe.model.document import Document

class AdoptionBooking(Document):

    def validate(self):
        pet = frappe.get_doc("Pet", self.pet)

        if pet.status == "Adopted":
            frappe.throw("Pet already adopted")

    def on_submit(self):
        pet = frappe.get_doc("Pet", self.pet)
        pet.status = "Adopted"
        pet.save()
