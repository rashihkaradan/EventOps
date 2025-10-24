import frappe
from frappe.model.document import Document
import qrcode
import io
import base64

class Booking(Document):
    def validate(self):
        self.total_amount = (self.price or 0) * (self.quantity or 0) 


class Booking(Document):
    def before_save(self):
        # Generate QR code only if it doesn't exist or booking details changed
        if not self.qr_code or self.has_value_changed('event') or self.has_value_changed('attendee'):
            self.generate_qr_code()
    
    def generate_qr_code(self):
        # Data to encode
        qr_data = f"Booking ID: {self.name}"
        
        # Generate QR code
        img = qrcode.make(qr_data)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        qr_code_bytes = buf.getvalue()
        
        # Save as file
        file_name = f"qr_code_{self.name}.png"
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": file_name,
            "content": qr_code_bytes,
            "is_private": 0,
            "attached_to_doctype": self.doctype,
            "attached_to_name": self.name,
        })
        file_doc.save(ignore_permissions=True)
        
        # Set the file URL to qr_code field
        self.qr_code = file_doc.file_url
    
    