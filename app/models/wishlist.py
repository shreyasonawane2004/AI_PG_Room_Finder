from app.database import query_db

class WishlistModel:
    """Data Access Object for Tenant Wishlists (Favorites)."""

    @staticmethod
    def toggle(tenant_id: int, property_id: int):
        existing = query_db(
            "SELECT id FROM wishlists WHERE tenant_id = %s AND property_id = %s",
            (tenant_id, property_id), one=True
        )
        if existing:
            query_db("DELETE FROM wishlists WHERE id = %s", (existing["id"],), commit=True)
            return False  # Removed
        else:
            query_db("INSERT INTO wishlists (tenant_id, property_id) VALUES (%s, %s)",
                     (tenant_id, property_id), commit=True)
            return True  # Added

    @staticmethod
    def is_saved(tenant_id: int, property_id: int) -> bool:
        if not tenant_id:
            return False
        row = query_db(
            "SELECT id FROM wishlists WHERE tenant_id = %s AND property_id = %s",
            (tenant_id, property_id), one=True
        )
        return bool(row)

    @staticmethod
    def get_by_tenant(tenant_id: int):
        query = """
            SELECT p.*,
                   (SELECT image_url FROM property_images WHERE property_id = p.id AND is_cover = TRUE LIMIT 1) as cover_image,
                   (SELECT AVG(rating_overall) FROM reviews WHERE property_id = p.id) as avg_rating,
                   w.created_at as saved_at
            FROM wishlists w
            JOIN properties p ON w.property_id = p.id
            WHERE w.tenant_id = %s
            ORDER BY w.created_at DESC
        """
        return query_db(query, (tenant_id,))
