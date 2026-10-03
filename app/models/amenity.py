from app.database import query_db

class AmenityModel:
    """Data Access Object for Master Amenities and Property mappings."""

    @staticmethod
    def get_all():
        return query_db("SELECT id, name, category, icon_code FROM amenities ORDER BY category, name")

    @staticmethod
    def get_by_property_id(property_id: int):
        query = """
            SELECT a.id, a.name, a.category, a.icon_code
            FROM amenities a
            JOIN property_amenities pa ON a.id = pa.amenity_id
            WHERE pa.property_id = %s
            ORDER BY a.name
        """
        return query_db(query, (property_id,))

    @staticmethod
    def set_property_amenities(property_id: int, amenity_ids: list):
        query_db("DELETE FROM property_amenities WHERE property_id = %s", (property_id,), commit=True)
        if amenity_ids:
            for aid in amenity_ids:
                query_db("INSERT IGNORE INTO property_amenities (property_id, amenity_id) VALUES (%s, %s)",
                         (property_id, int(aid)), commit=True)

    @staticmethod
    def create(name: str, category: str, icon_code: str):
        query = "INSERT INTO amenities (name, category, icon_code) VALUES (%s, %s, %s)"
        return query_db(query, (name.strip(), category.strip(), icon_code.strip()), commit=True)
