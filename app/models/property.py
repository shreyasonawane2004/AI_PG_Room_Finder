import re
from app.database import query_db

def slugify(text: str) -> str:
    """Generate a clean URL slug from title."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_-]+", "-", text)


class PropertyModel:
    """Data Access Object for Properties, Rooms, and Images."""

    @staticmethod
    def get_by_id(property_id: int):
        query = """
            SELECT p.*, u.full_name as owner_name, u.phone as owner_phone, u.email as owner_email
            FROM properties p
            JOIN users u ON p.owner_id = u.id
            WHERE p.id = %s
        """
        prop = query_db(query, (property_id,), one=True)
        if prop:
            prop["rooms"] = PropertyModel.get_rooms(property_id)
            prop["images"] = PropertyModel.get_images(property_id)
            prop["amenities"] = PropertyModel.get_amenities(property_id)
        return prop

    @staticmethod
    def get_by_slug(slug: str):
        query = """
            SELECT p.*, u.full_name as owner_name, u.phone as owner_phone, u.email as owner_email
            FROM properties p
            JOIN users u ON p.owner_id = u.id
            WHERE p.slug = %s
        """
        prop = query_db(query, (slug,), one=True)
        if prop:
            prop["rooms"] = PropertyModel.get_rooms(prop["id"])
            prop["images"] = PropertyModel.get_images(prop["id"])
            prop["amenities"] = PropertyModel.get_amenities(prop["id"])
        return prop

    @staticmethod
    def get_rooms(property_id: int):
        return query_db(
            "SELECT * FROM rooms WHERE property_id = %s ORDER BY monthly_rent ASC",
            (property_id,)
        )

    @staticmethod
    def get_images(property_id: int):
        return query_db(
            "SELECT * FROM property_images WHERE property_id = %s ORDER BY is_cover DESC, id ASC",
            (property_id,)
        )

    @staticmethod
    def get_amenities(property_id: int):
        query = """
            SELECT a.* FROM amenities a
            JOIN property_amenities pa ON a.id = pa.amenity_id
            WHERE pa.property_id = %s ORDER BY a.name ASC
        """
        return query_db(query, (property_id,))

    @staticmethod
    def get_by_owner(owner_id: int):
        query = """
            SELECT p.*, 
                   (SELECT COUNT(*) FROM rooms WHERE property_id = p.id) as room_count,
                   (SELECT COALESCE(SUM(available_beds), 0) FROM rooms WHERE property_id = p.id) as total_available_beds,
                   (SELECT image_url FROM property_images WHERE property_id = p.id AND is_cover = TRUE LIMIT 1) as cover_image
            FROM properties p
            WHERE p.owner_id = %s
            ORDER BY p.created_at DESC
        """
        return query_db(query, (owner_id,))

    @staticmethod
    def create(data: dict, owner_id: int):
        base_slug = slugify(data.get("title", "pg-property"))
        slug = base_slug
        # Ensure unique slug
        counter = 1
        while query_db("SELECT id FROM properties WHERE slug = %s", (slug,), one=True):
            slug = f"{base_slug}-{counter}"
            counter += 1

        query = """
            INSERT INTO properties (
                owner_id, title, slug, description, property_type, gender_preference,
                min_price, max_price, address_line, landmark, city, state, pincode,
                latitude, longitude, notice_period_days, gate_closing_time, food_available,
                food_type, rules_and_regulations, status
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        params = (
            owner_id,
            data.get("title"),
            slug,
            data.get("description", ""),
            data.get("property_type", "pg"),
            data.get("gender_preference", "unisex"),
            data.get("min_price", 0.00),
            data.get("max_price", 0.00),
            data.get("address_line", ""),
            data.get("landmark", ""),
            data.get("city", "Bangalore"),
            data.get("state", "Karnataka"),
            data.get("pincode", "560001"),
            data.get("latitude", 12.9716),
            data.get("longitude", 77.5946),
            data.get("notice_period_days", 30),
            data.get("gate_closing_time", "No Restriction"),
            data.get("food_available", False),
            data.get("food_type", "none"),
            data.get("rules_and_regulations", ""),
            "pending_approval"
        )
        prop_id = query_db(query, params, commit=True)
        return PropertyModel.get_by_id(prop_id)

    @staticmethod
    def update(property_id: int, data: dict):
        query = """
            UPDATE properties SET
                title = %s, description = %s, property_type = %s, gender_preference = %s,
                min_price = %s, max_price = %s, address_line = %s, landmark = %s,
                city = %s, state = %s, pincode = %s, latitude = %s, longitude = %s,
                notice_period_days = %s, gate_closing_time = %s, food_available = %s,
                food_type = %s, rules_and_regulations = %s
            WHERE id = %s
        """
        params = (
            data.get("title"),
            data.get("description", ""),
            data.get("property_type", "pg"),
            data.get("gender_preference", "unisex"),
            data.get("min_price", 0.00),
            data.get("max_price", 0.00),
            data.get("address_line", ""),
            data.get("landmark", ""),
            data.get("city", "Bangalore"),
            data.get("state", "Karnataka"),
            data.get("pincode", "560001"),
            data.get("latitude", 12.9716),
            data.get("longitude", 77.5946),
            data.get("notice_period_days", 30),
            data.get("gate_closing_time", "No Restriction"),
            data.get("food_available", False),
            data.get("food_type", "none"),
            data.get("rules_and_regulations", ""),
            property_id
        )
        query_db(query, params, commit=True)
        return PropertyModel.get_by_id(property_id)

    @staticmethod
    def add_room(property_id: int, room_data: dict):
        query = """
            INSERT INTO rooms (
                property_id, room_type, total_beds, available_beds, monthly_rent,
                security_deposit, has_ac, has_attached_bathroom, has_balcony
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            property_id,
            room_data.get("room_type"),
            room_data.get("total_beds", 1),
            room_data.get("available_beds", 1),
            room_data.get("monthly_rent", 5000.00),
            room_data.get("security_deposit", 10000.00),
            room_data.get("has_ac", False),
            room_data.get("has_attached_bathroom", False),
            room_data.get("has_balcony", False)
        )
        room_id = query_db(query, params, commit=True)
        PropertyModel.recalculate_price_range(property_id)
        return room_id

    @staticmethod
    def recalculate_price_range(property_id: int):
        query = "SELECT MIN(monthly_rent) as min_rent, MAX(monthly_rent) as max_rent FROM rooms WHERE property_id = %s"
        rents = query_db(query, (property_id,), one=True)
        if rents and rents["min_rent"] is not None:
            query_db(
                "UPDATE properties SET min_price = %s, max_price = %s WHERE id = %s",
                (rents["min_rent"], rents["max_rent"], property_id),
                commit=True
            )

    @staticmethod
    def add_image(property_id: int, image_url: str, is_cover: bool = False):
        if is_cover:
            query_db("UPDATE property_images SET is_cover = FALSE WHERE property_id = %s", (property_id,), commit=True)
        query = "INSERT INTO property_images (property_id, image_url, is_cover) VALUES (%s, %s, %s)"
        return query_db(query, (property_id, image_url, is_cover), commit=True)

    @staticmethod
    def search(filters: dict = None):
        """Dynamic multi-facet search for tenant discovery."""
        filters = filters or {}
        sql = """
            SELECT DISTINCT p.*, 
                   u.full_name as owner_name,
                   (SELECT image_url FROM property_images WHERE property_id = p.id AND is_cover = TRUE LIMIT 1) as cover_image,
                   (SELECT AVG(rating_overall) FROM reviews WHERE property_id = p.id) as avg_rating,
                   (SELECT COUNT(*) FROM reviews WHERE property_id = p.id) as review_count
            FROM properties p
            JOIN users u ON p.owner_id = u.id
            LEFT JOIN rooms r ON p.id = r.property_id
            WHERE p.status = 'approved'
        """
        params = []

        # City / Location
        city = filters.get("city")
        if city and city.lower() != "all":
            sql += " AND (p.city LIKE %s OR p.landmark LIKE %s OR p.address_line LIKE %s)"
            c_term = f"%{city.strip()}%"
            params.extend([c_term, c_term, c_term])

        # Gender preference
        gender = filters.get("gender")
        if gender and gender.lower() in ("male", "female", "unisex"):
            if gender.lower() == "unisex":
                sql += " AND p.gender_preference IN ('male', 'female', 'unisex')"
            else:
                sql += " AND (p.gender_preference = %s OR p.gender_preference = 'unisex')"
                params.append(gender.lower())

        # Budget range
        max_budget = filters.get("max_budget")
        if max_budget:
            try:
                sql += " AND p.min_price <= %s"
                params.append(float(max_budget))
            except ValueError:
                pass

        min_budget = filters.get("min_budget")
        if min_budget:
            try:
                sql += " AND p.max_price >= %s"
                params.append(float(min_budget))
            except ValueError:
                pass

        # Sharing type
        sharing = filters.get("sharing")
        if sharing and sharing != "all":
            sql += " AND r.room_type = %s"
            params.append(sharing)

        # Food availability
        if filters.get("food_available") is True or filters.get("food") == "1":
            sql += " AND p.food_available = TRUE"

        # AC Filter
        if filters.get("ac") == "1" or filters.get("has_ac") is True:
            sql += " AND r.has_ac = TRUE"

        # Sorting
        sort = filters.get("sort", "recommended")
        if sort == "price_low":
            sql += " ORDER BY p.min_price ASC"
        elif sort == "price_high":
            sql += " ORDER BY p.min_price DESC"
        elif sort == "rating":
            sql += " ORDER BY avg_rating DESC"
        else:
            sql += " ORDER BY p.created_at DESC"

        limit = int(filters.get("limit", 20))
        offset = int(filters.get("offset", 0))
        sql += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        results = query_db(sql, params)
        for prop in results:
            if not prop.get("cover_image"):
                prop["cover_image"] = "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?auto=format&fit=crop&w=800&q=80"
            prop["avg_rating"] = round(float(prop["avg_rating"]), 1) if prop.get("avg_rating") else 0.0
            prop["amenities"] = PropertyModel.get_amenities(prop["id"])
        return results

    @staticmethod
    def get_pending_approval():
        query = """
            SELECT p.*, u.full_name as owner_name, u.email as owner_email, u.phone as owner_phone
            FROM properties p
            JOIN users u ON p.owner_id = u.id
            WHERE p.status = 'pending_approval'
            ORDER BY p.created_at ASC
        """
        return query_db(query)

    @staticmethod
    def update_status(property_id: int, status: str, rejection_reason: str = None):
        query = "UPDATE properties SET status = %s, rejection_reason = %s WHERE id = %s"
        query_db(query, (status, rejection_reason, property_id), commit=True)
