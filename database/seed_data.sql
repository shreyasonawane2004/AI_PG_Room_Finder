-- =======================================================
-- AI-Powered PG & Room Finder - Initial Seed Data (MySQL)
-- =======================================================

USE ai_pg_room_finder;

-- Disable FK checks for clean seeding
SET FOREIGN_KEY_CHECKS = 0;

-- 1. Master Amenities
INSERT INTO amenities (id, name, category, icon_code) VALUES
(1, 'High-Speed Wi-Fi', 'Utilities', 'fa-wifi'),
(2, 'Air Conditioning (AC)', 'Comfort', 'fa-snowflake'),
(3, 'Three Meals Included', 'Food', 'fa-utensils'),
(4, 'Daily Housekeeping', 'Hygiene', 'fa-broom'),
(5, 'Power Backup (Inverter/DG)', 'Utilities', 'fa-bolt'),
(6, 'RO Purified Drinking Water', 'Food', 'fa-tint'),
(7, 'Washing Machine / Laundry', 'Utilities', 'fa-tshirt'),
(8, 'Attached Private Bathroom', 'Comfort', 'fa-bath'),
(9, '24/7 CCTV & Security Guard', 'Safety', 'fa-shield-alt'),
(10, 'Geyser / Hot Water', 'Comfort', 'fa-fire'),
(11, 'Fitness Gym', 'Lifestyle', 'fa-dumbbell'),
(12, 'Two-Wheeler Parking', 'Convenience', 'fa-motorcycle'),
(13, 'Four-Wheeler Parking', 'Convenience', 'fa-car'),
(14, 'Balcony / Terrace', 'Comfort', 'fa-sun'),
(15, 'Biometric / Smart Lock Access', 'Safety', 'fa-fingerprint')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 2. Seed Users
-- Password for all accounts: password123 (hashed with werkzeug scrypt format)
-- Format: scrypt:32768:8:1$uH... or we can update when app boots
INSERT INTO users (id, full_name, email, password_hash, phone, role, avatar_url, is_verified, is_active) VALUES
(1, 'System Administrator', 'admin@roomfinder.com', 'scrypt:32768:8:1$K5zQ7k8D6WlH3r4Y$4578b9b47e85c2c770d189b88960a5e840a454d6fa7830cb8ea10738472f75471136b6f7eef6eb28117eb8a2e5d996162391696144e548810237fa9a3d460e5a', '+91 9876543210', 'admin', '/static/images/default-avatar.png', TRUE, TRUE),
(2, 'Rajesh Sharma (Owner)', 'rajesh.owner@example.com', 'scrypt:32768:8:1$K5zQ7k8D6WlH3r4Y$4578b9b47e85c2c770d189b88960a5e840a454d6fa7830cb8ea10738472f75471136b6f7eef6eb28117eb8a2e5d996162391696144e548810237fa9a3d460e5a', '+91 9811223344', 'owner', '/static/images/default-avatar.png', TRUE, TRUE),
(3, 'Priya Nair (Owner)', 'priya.owner@example.com', 'scrypt:32768:8:1$K5zQ7k8D6WlH3r4Y$4578b9b47e85c2c770d189b88960a5e840a454d6fa7830cb8ea10738472f75471136b6f7eef6eb28117eb8a2e5d996162391696144e548810237fa9a3d460e5a', '+91 9822334455', 'owner', '/static/images/default-avatar.png', TRUE, TRUE),
(4, 'Amit Verma (Tenant)', 'amit.tenant@example.com', 'scrypt:32768:8:1$K5zQ7k8D6WlH3r4Y$4578b9b47e85c2c770d189b88960a5e840a454d6fa7830cb8ea10738472f75471136b6f7eef6eb28117eb8a2e5d996162391696144e548810237fa9a3d460e5a', '+91 9833445566', 'tenant', '/static/images/default-avatar.png', TRUE, TRUE),
(5, 'Sneha Patel (Tenant)', 'sneha.tenant@example.com', 'scrypt:32768:8:1$K5zQ7k8D6WlH3r4Y$4578b9b47e85c2c770d189b88960a5e840a454d6fa7830cb8ea10738472f75471136b6f7eef6eb28117eb8a2e5d996162391696144e548810237fa9a3d460e5a', '+91 9844556677', 'tenant', '/static/images/default-avatar.png', TRUE, TRUE)
ON DUPLICATE KEY UPDATE email=VALUES(email);

-- 3. Seed Properties
INSERT INTO properties (
    id, owner_id, title, slug, description, property_type, gender_preference,
    min_price, max_price, address_line, landmark, city, state, pincode,
    latitude, longitude, notice_period_days, gate_closing_time, food_available, food_type,
    rules_and_regulations, status
) VALUES
(
    1, 2, 'Greenfield Luxury PG for Men', 'greenfield-luxury-pg-koramangala',
    'Premium modern gents PG in the heart of Koramangala 4th Block. Fully furnished with high-speed 200 Mbps fiber internet, South & North Indian hygienic food, biometric security, and power backup.',
    'pg', 'male', 7500.00, 14000.00,
    '#42, 12th Main Road, 4th Block, Koramangala', 'Near Sony World Signal', 'Bangalore', 'Karnataka', '560034',
    12.93524200, 77.62446100, 30, '11:00 PM', TRUE, 'both',
    'No smoking inside rooms. Guests permitted in lobby only.', 'approved'
),
(
    2, 3, 'Serene Oasis Girls Coliving & PG', 'serene-oasis-girls-pg-hsr-layout',
    'Safe, upscale and vibrant PG for female tech professionals and students in HSR Layout Sector 1. Includes 3 home-style meals, 24/7 CCTV surveillance, biometric access, and gym facility.',
    'pg', 'female', 8500.00, 16500.00,
    'Plot 18, 19th Main, Sector 1, HSR Layout', 'Near Agara Lake & NIFT', 'Bangalore', 'Karnataka', '560102',
    12.91214000, 77.64455400, 30, '10:30 PM', TRUE, 'both',
    'Strictly girls only. Biometric check-in after 10 PM. Quiet hours after 11 PM.', 'approved'
),
(
    3, 2, 'Skyline Urban Unisex Coliving Spaces', 'skyline-urban-coliving-whitefield',
    'Contemporary co-living hub close to ITPL and major tech parks in Whitefield. Features private studio rooms, double sharing, co-working breakout spaces, terrace garden, and high-speed Wi-Fi.',
    'pg', 'unisex', 9000.00, 18000.00,
    'Tower 4, Prestige Tech Zone Road, Whitefield', 'Opposite ITPL Main Gate', 'Bangalore', 'Karnataka', '560066',
    12.98561000, 77.73142000, 15, 'No Restriction', TRUE, 'veg',
    'Open-minded community. Pet friendly on terrace floors. No loud music post midnight.', 'approved'
),
(
    4, 3, 'Zenith Premium PG & Rooms for Students', 'zenith-premium-pg-hinjewadi-pune',
    'Designed for IT employees and students near Phase 1 Hinjewadi. Fully air conditioned rooms, individual work desks, hygienic cafeteria, and regular maintenance.',
    'pg', 'unisex', 6000.00, 12000.00,
    'Lane 3, Behind Rajiv Gandhi Infotech Park, Hinjewadi Phase 1', 'Near Blue Ridge', 'Pune', 'Maharashtra', '411057',
    18.59127000, 73.73891000, 30, '11:00 PM', TRUE, 'both',
    'Valid ID card and corporate/college affiliation required.', 'approved'
)
ON DUPLICATE KEY UPDATE title=VALUES(title);

-- 4. Seed Rooms
INSERT INTO rooms (id, property_id, room_type, total_beds, available_beds, monthly_rent, security_deposit, has_ac, has_attached_bathroom, has_balcony) VALUES
-- Greenfield PG (Property 1)
(1, 1, 'single', 5, 2, 14000.00, 20000.00, TRUE, TRUE, TRUE),
(2, 1, 'double_sharing', 10, 3, 9500.00, 15000.00, TRUE, TRUE, FALSE),
(3, 1, 'triple_sharing', 12, 4, 7500.00, 10000.00, FALSE, TRUE, FALSE),

-- Serene Oasis Girls PG (Property 2)
(4, 2, 'single', 4, 1, 16500.00, 25000.00, TRUE, TRUE, TRUE),
(5, 2, 'double_sharing', 8, 2, 11000.00, 18000.00, TRUE, TRUE, TRUE),
(6, 2, 'triple_sharing', 9, 3, 8500.00, 12000.00, FALSE, TRUE, FALSE),

-- Skyline Coliving (Property 3)
(7, 3, 'single', 6, 2, 18000.00, 25000.00, TRUE, TRUE, TRUE),
(8, 3, 'double_sharing', 12, 5, 12000.00, 18000.00, TRUE, TRUE, FALSE),
(9, 3, 'four_sharing', 8, 3, 9000.00, 12000.00, FALSE, TRUE, FALSE),

-- Zenith Pune PG (Property 4)
(10, 4, 'single', 4, 2, 12000.00, 15000.00, TRUE, TRUE, FALSE),
(11, 4, 'double_sharing', 10, 4, 8000.00, 12000.00, TRUE, TRUE, FALSE),
(12, 4, 'triple_sharing', 12, 5, 6000.00, 9000.00, FALSE, TRUE, FALSE)
ON DUPLICATE KEY UPDATE monthly_rent=VALUES(monthly_rent);

-- 5. Map Amenities to Properties
INSERT IGNORE INTO property_amenities (property_id, amenity_id) VALUES
-- Greenfield (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12)
(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (1, 12),
-- Serene Oasis (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15)
(2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10), (2, 11), (2, 14), (2, 15),
-- Skyline Coliving (1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14)
(3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 11), (3, 12), (3, 13), (3, 14),
-- Zenith Pune (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12)
(4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9), (4, 10), (4, 12);

-- 6. Property Images
INSERT INTO property_images (id, property_id, image_url, is_cover) VALUES
(1, 1, 'https://images.unsplash.com/photo-1555854877-bab0e564b8d5?auto=format&fit=crop&w=800&q=80', TRUE),
(2, 1, 'https://images.unsplash.com/photo-1595526114035-0d45ed16cfbf?auto=format&fit=crop&w=800&q=80', FALSE),
(3, 2, 'https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?auto=format&fit=crop&w=800&q=80', TRUE),
(4, 2, 'https://images.unsplash.com/photo-1540518614846-7ede433c4ef0?auto=format&fit=crop&w=800&q=80', FALSE),
(5, 3, 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80', TRUE),
(6, 3, 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80', FALSE),
(7, 4, 'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80', TRUE)
ON DUPLICATE KEY UPDATE image_url=VALUES(image_url);

-- 7. Seed Reviews
INSERT INTO reviews (id, property_id, tenant_id, rating_overall, rating_cleanliness, rating_food, rating_safety, comment, sentiment_label) VALUES
(1, 1, 4, 5, 5, 4, 5, 'Lived here for 6 months! Outstanding Wi-Fi speed, quiet environment for work from home, and the owner Rajesh is extremely helpful.', 'positive'),
(2, 1, 5, 4, 4, 4, 5, 'Great location in Koramangala. Food quality is consistently decent and rooms are cleaned daily. Highly recommended for professionals.', 'positive'),
(3, 2, 5, 5, 5, 5, 5, 'Super safe PG for women! The biometric security and CCTV give complete peace of mind. Food tastes just like home.', 'positive'),
(4, 3, 4, 4, 4, 4, 4, 'Modern vibe and very lively community. Great terrace garden and fast internet. A bit pricey but worth the amenities.', 'positive')
ON DUPLICATE KEY UPDATE comment=VALUES(comment);

-- 8. Seed AI Summaries
INSERT INTO ai_review_summaries (id, property_id, pros_list, cons_list, overall_summary, average_sentiment_score) VALUES
(
    1, 1,
    JSON_ARRAY('High-speed 200 Mbps Wi-Fi ideal for remote work', 'Polite, supportive owner and responsive warden', 'Daily room sanitization and prompt maintenance'),
    JSON_ARRAY('Limited two-wheeler parking spots during peak hours', 'Gate closing strictly at 11:00 PM'),
    'Consistently rated top-tier for remote working professionals in Koramangala. High hygiene standards and responsive property management.',
    0.88
),
(
    2, 2,
    JSON_ARRAY('Robust 24/7 CCTV and biometric access for security', 'Delicious home-style food cooked fresh 3 times daily', 'Peaceful ambiance next to Agara Lake park'),
    JSON_ARRAY('Strict biometric curfew after 10:30 PM'),
    'Highly recommended for female students and corporate workers prioritizing personal safety, cleanliness, and nutritious food.',
    0.95
)
ON DUPLICATE KEY UPDATE overall_summary=VALUES(overall_summary);

-- Re-enable FK checks
SET FOREIGN_KEY_CHECKS = 1;
