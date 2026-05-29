# Pet Adoption System

A comprehensive Pet Adoption Application built for **ERPNext v15** and **Frappe Framework v15**.

## Features

### 🐾 Pet Management
- Complete pet profiles (name, breed, age, gender, size, color, health status)
- Pet categories (Dogs, Cats, Birds, etc.) and breeds
- Image uploading with gallery support
- Status tracking (Available, Adopted, Fostered, Pending Meeting, Not Available)

### 📅 Booking System
- Online adoption meeting scheduling with date/time selection
- Real-time slot availability checking
- Adopter profile creation and management
- Housing environment assessment
- Booking lifecycle (Draft → Scheduled → Completed/Cancelled)

### 💰 ERPNext Integration
- Automatic Sales Invoice creation on adoption completion
- Customer creation from adopter data
- Configurable adoption fees and service items
- Accounting integration with ERPNext

### 🌐 Website Features
- **Pets Catalog** (`/pets`) - Browse available pets with search, filter by category/gender
- Responsive design for mobile and desktop
- Beautiful, modern UI with smooth animations

### 🔧 Admin Features
- Single Settings doctype for center configuration
- Scheduled tasks for booking reminders and auto-cancellation
- Permissions for Guest (public) and System Manager roles
- Fixtures for pre-loading default data

## Installation

```bash
# Get the app
bench get-app pet_adoption_booking

# Install on your site
bench --site your-site.local install-app pet_adoption_booking

# Build assets
bench build
```

## Usage

### For Visitors (Public)
1. Browse available pets at `/pets`
2. Click "Book Adoption Visit" on any pet
3. Fill in your details and select a time slot
4. Receive booking confirmation

### For Admins
1. Navigate to the **Pet Adoption** module
2. Manage pets, categories, breeds, and adopters
3. Configure settings under **Adoption Settings**
4. Approve/reject bookings and manage status

## Configuration

Navigate to **Adoption Settings** (Single doctype) to configure:
- Center name
- Default adoption fee
- Default tax rate
- Adoption service item for invoicing
- Terms and conditions

## Dependencies

- Frappe v15+
- ERPNext v15+

## License

MIT
