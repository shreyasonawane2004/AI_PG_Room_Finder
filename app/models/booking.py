from app.database import query_db

class BookingModel:
    """Data Access Object for Inquiries and Visit Scheduling."""

    @staticmethod
    def create(tenant_id: int, property_id: int, room_id: int, inquiry_type: str, visit_date: str, visit_time_slot: str, message: str):
        query = """
            INSERT INTO inquiries_bookings (
                tenant_id, property_id, room_id, inquiry_type, visit_date, visit_time_slot, message, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')
        """
        params = (tenant_id, property_id, room_id, inquiry_type, visit_date, visit_time_slot, message)
        return query_db(query, params, commit=True)

    @staticmethod
    def get_by_tenant(tenant_id: int):
        query = """
            SELECT b.*, p.title as property_title, p.slug as property_slug, p.address_line, p.city,
                   r.room_type, r.monthly_rent,
                   u.full_name as owner_name, u.phone as owner_phone, u.email as owner_email,
                   (SELECT image_url FROM property_images WHERE property_id = p.id AND is_cover = TRUE LIMIT 1) as cover_image
            FROM inquiries_bookings b
            JOIN properties p ON b.property_id = p.id
            JOIN users u ON p.owner_id = u.id
            LEFT JOIN rooms r ON b.room_id = r.id
            WHERE b.tenant_id = %s
            ORDER BY b.created_at DESC
        """
        return query_db(query, (tenant_id,))

    @staticmethod
    def get_by_owner(owner_id: int):
        query = """
            SELECT b.*, p.title as property_title, p.slug as property_slug,
                   r.room_type, r.monthly_rent,
                   u.full_name as tenant_name, u.phone as tenant_phone, u.email as tenant_email
            FROM inquiries_bookings b
            JOIN properties p ON b.property_id = p.id
            JOIN users u ON b.tenant_id = u.id
            LEFT JOIN rooms r ON b.room_id = r.id
            WHERE p.owner_id = %s
            ORDER BY b.created_at DESC
        """
        return query_db(query, (owner_id,))

    @staticmethod
    def update_status(booking_id: int, status: str, owner_notes: str = None):
        query = "UPDATE inquiries_bookings SET status = %s, owner_notes = %s WHERE id = %s"
        query_db(query, (status, owner_notes, booking_id), commit=True)
