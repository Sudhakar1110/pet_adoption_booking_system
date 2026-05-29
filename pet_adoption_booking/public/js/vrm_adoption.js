// Pet Adoption Booking - Client-side Utilities for ERPNext v15
frappe.provide("vrm_adoption");

vrm_adoption.utils = {
    /**
     * Show a toast alert message
     */
    show_alert: function(message, indicator) {
        frappe.show_alert({
            message: message,
            indicator: indicator || "orange"
        });
    },

    /**
     * Check slot availability via API
     */
    check_slot_availability: function(pet, date, time_slot, callback) {
        frappe.call({
            method: "pet_adoption_booking.api.check_slot_availability",
            args: {
                pet: pet,
                booking_date: date,
                time_slot: time_slot
            },
            callback: function(r) {
                if (callback) callback(r.message);
            }
        });
    },

    /**
     * Get available time slots for a pet on a date
     */
    get_available_slots: function(pet, date, callback) {
        frappe.call({
            method: "pet_adoption_booking.api.get_available_time_slots",
            args: {
                pet: pet,
                booking_date: date
            },
            callback: function(r) {
                if (callback) callback(r.message);
            }
        });
    },

    /**
     * Format date to YYYY-MM-DD
     */
    format_date: function(date) {
        return date.toISOString().split('T')[0];
    },

    /**
     * Scroll to element smoothly
     */
    scroll_to: function(element_id) {
        const el = document.getElementById(element_id);
        if (el) {
            el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
};

// Initialize on DOM ready
$(document).ready(function() {
    // Auto-set minimum date for date inputs
    $('input[type="date"]').each(function() {
        if (!$(this).attr('min')) {
            $(this).attr('min', vrm_adoption.utils.format_date(new Date()));
        }
    });
});
