import json
from app.database import query_db

class ReviewModel:
    """Data Access Object for Tenant Reviews and AI Summaries."""

    @staticmethod
    def get_by_property(property_id: int):
        query = """
            SELECT r.*, u.full_name as author_name, u.avatar_url as author_avatar
            FROM reviews r
            JOIN users u ON r.tenant_id = u.id
            WHERE r.property_id = %s
            ORDER BY r.created_at DESC
        """
        return query_db(query, (property_id,))

    @staticmethod
    def create(property_id: int, tenant_id: int, rating_overall: int,
               rating_cleanliness: int, rating_food: int, rating_safety: int, comment: str):
        query = """
            INSERT INTO reviews (
                property_id, tenant_id, rating_overall, rating_cleanliness,
                rating_food, rating_safety, comment, sentiment_label
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'positive')
            ON DUPLICATE KEY UPDATE
                rating_overall = VALUES(rating_overall),
                rating_cleanliness = VALUES(rating_cleanliness),
                rating_food = VALUES(rating_food),
                rating_safety = VALUES(rating_safety),
                comment = VALUES(comment),
                created_at = CURRENT_TIMESTAMP
        """
        params = (property_id, tenant_id, rating_overall, rating_cleanliness, rating_food, rating_safety, comment)
        return query_db(query, params, commit=True)

    @staticmethod
    def get_ai_summary(property_id: int):
        query = "SELECT * FROM ai_review_summaries WHERE property_id = %s"
        row = query_db(query, (property_id,), one=True)
        if row:
            if isinstance(row.get("pros_list"), str):
                try:
                    row["pros_list"] = json.loads(row["pros_list"])
                except Exception:
                    row["pros_list"] = []
            if isinstance(row.get("cons_list"), str):
                try:
                    row["cons_list"] = json.loads(row["cons_list"])
                except Exception:
                    row["cons_list"] = []
        return row

    @staticmethod
    def save_ai_summary(property_id: int, pros: list, cons: list, summary: str, sentiment: float):
        query = """
            INSERT INTO ai_review_summaries (
                property_id, pros_list, cons_list, overall_summary, average_sentiment_score
            ) VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                pros_list = VALUES(pros_list),
                cons_list = VALUES(cons_list),
                overall_summary = VALUES(overall_summary),
                average_sentiment_score = VALUES(average_sentiment_score),
                last_generated_at = CURRENT_TIMESTAMP
        """
        params = (property_id, json.dumps(pros), json.dumps(cons), summary, sentiment)
        query_db(query, params, commit=True)
