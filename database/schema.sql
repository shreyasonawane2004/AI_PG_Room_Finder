-- =======================================================
-- AI-Powered PG & Room Finder - Database Schema (MySQL)
-- =======================================================

CREATE DATABASE IF NOT EXISTS ai_pg_room_finder CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ai_pg_room_finder;

-- Disable foreign key checks during initialization
SET FOREIGN_KEY_CHECKS = 0;

-- 1. Users Table
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    role ENUM('tenant', 'owner', 'admin') NOT NULL DEFAULT 'tenant',
    avatar_url VARCHAR(255) DEFAULT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_role (role),
    INDEX idx_user_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Properties Table
DROP TABLE IF EXISTS properties;
CREATE TABLE properties (
    id INT AUTO_INCREMENT PRIMARY KEY,
    owner_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    slug VARCHAR(180) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    property_type ENUM('pg', 'independent_room', 'hostel', 'flat') NOT NULL DEFAULT 'pg',
    gender_preference ENUM('male', 'female', 'unisex') NOT NULL DEFAULT 'unisex',
    min_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    max_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    address_line VARCHAR(255) NOT NULL,
    landmark VARCHAR(120) DEFAULT NULL,
    city VARCHAR(80) NOT NULL,
    state VARCHAR(80) NOT NULL,
    pincode VARCHAR(10) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    notice_period_days INT DEFAULT 30,
    gate_closing_time VARCHAR(50) DEFAULT 'No Restriction',
    food_available BOOLEAN DEFAULT FALSE,
    food_type ENUM('none', 'veg', 'non_veg', 'both') DEFAULT 'none',
    rules_and_regulations TEXT DEFAULT NULL,
    status ENUM('pending_approval', 'approved', 'rejected', 'inactive') DEFAULT 'pending_approval',
    rejection_reason VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_property_city (city),
    INDEX idx_property_gender (gender_preference),
    INDEX idx_property_status (status),
    INDEX idx_property_price (min_price, max_price),
    INDEX idx_property_coords (latitude, longitude)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Rooms Table
DROP TABLE IF EXISTS rooms;
CREATE TABLE rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    property_id INT NOT NULL,
    room_type ENUM('single', 'double_sharing', 'triple_sharing', 'four_sharing') NOT NULL,
    total_beds INT NOT NULL DEFAULT 1,
    available_beds INT NOT NULL DEFAULT 1,
    monthly_rent DECIMAL(10, 2) NOT NULL,
    security_deposit DECIMAL(10, 2) NOT NULL,
    has_ac BOOLEAN DEFAULT FALSE,
    has_attached_bathroom BOOLEAN DEFAULT FALSE,
    has_balcony BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE,
    INDEX idx_room_type (room_type),
    INDEX idx_room_rent (monthly_rent)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Master Amenities Table
DROP TABLE IF EXISTS amenities;
CREATE TABLE amenities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(60) NOT NULL UNIQUE,
    category VARCHAR(40) DEFAULT 'General',
    icon_code VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Property-Amenities Mapping Table
DROP TABLE IF EXISTS property_amenities;
CREATE TABLE property_amenities (
    property_id INT NOT NULL,
    amenity_id INT NOT NULL,
    PRIMARY KEY (property_id, amenity_id),
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE,
    FOREIGN KEY (amenity_id) REFERENCES amenities(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Property Images Table
DROP TABLE IF EXISTS property_images;
CREATE TABLE property_images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    property_id INT NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    is_cover BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Inquiries and Bookings Table
DROP TABLE IF EXISTS inquiries_bookings;
CREATE TABLE inquiries_bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id INT NOT NULL,
    property_id INT NOT NULL,
    room_id INT DEFAULT NULL,
    inquiry_type ENUM('schedule_visit', 'direct_booking_inquiry') NOT NULL,
    visit_date DATE DEFAULT NULL,
    visit_time_slot VARCHAR(50) DEFAULT NULL,
    message TEXT DEFAULT NULL,
    status ENUM('pending', 'confirmed', 'completed', 'declined', 'cancelled') DEFAULT 'pending',
    owner_notes VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE SET NULL,
    INDEX idx_inquiry_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Reviews Table
DROP TABLE IF EXISTS reviews;
CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    property_id INT NOT NULL,
    tenant_id INT NOT NULL,
    rating_overall TINYINT NOT NULL CHECK (rating_overall BETWEEN 1 AND 5),
    rating_cleanliness TINYINT DEFAULT 5,
    rating_food TINYINT DEFAULT 5,
    rating_safety TINYINT DEFAULT 5,
    comment TEXT NOT NULL,
    sentiment_label ENUM('positive', 'neutral', 'negative') DEFAULT 'neutral',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_tenant_property_review (property_id, tenant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. AI Review Summaries Table
DROP TABLE IF EXISTS ai_review_summaries;
CREATE TABLE ai_review_summaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    property_id INT NOT NULL UNIQUE,
    pros_list JSON DEFAULT NULL,
    cons_list JSON DEFAULT NULL,
    overall_summary TEXT DEFAULT NULL,
    average_sentiment_score DECIMAL(4, 2) DEFAULT 0.00,
    last_generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. Wishlists / Saved Properties Table
DROP TABLE IF EXISTS wishlists;
CREATE TABLE wishlists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id INT NOT NULL,
    property_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_favorite (tenant_id, property_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 11. User Search Preferences Table
DROP TABLE IF EXISTS user_search_preferences;
CREATE TABLE user_search_preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id INT NOT NULL,
    preferred_city VARCHAR(80) DEFAULT NULL,
    max_budget DECIMAL(10, 2) DEFAULT NULL,
    preferred_sharing VARCHAR(50) DEFAULT NULL,
    preferred_gender VARCHAR(20) DEFAULT NULL,
    preferred_amenities JSON DEFAULT NULL,
    last_search_query VARCHAR(255) DEFAULT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;
