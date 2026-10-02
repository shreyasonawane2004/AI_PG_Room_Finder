# AI-Powered PG & Room Finder

An intelligent, full-stack web application designed to help tenants find Paying Guest (PG) accommodations, co-living spaces, and independent rooms based on location, budget, sharing type, gender preference, and facilities.

---

## 1. Project Plan & Architecture

### System Overview
- **Frontend Architecture**: Built using clean, modern Vanilla HTML5, CSS3, and ES6+ JavaScript. Features glassmorphism, responsive grid/flexbox layouts, instant filter reactivity, and accessible UI controls.
- **Backend Architecture**: Python Flask utilizing the Application Factory pattern (`create_app`) and modular Blueprints (`auth`, `tenant`, `owner`, `admin`, `api`).
- **Database**: MySQL relational database (3NF normalized schema) with indexes optimized for spatial and price-range queries.
- **AI Engine**:
  - **Natural Language Query Parser**: Converts queries like *"Looking for single room PG in Koramangala with food under 10k for girls"* into structured filter constraints.
  - **Smart Recommendation Engine**: Content-based and preference-driven scoring calculating multi-criteria cosine similarity (price tolerance, amenity overlap, distance, gender).
  - **Review Summarizer & Sentiment Analyzer**: Analyzes tenant feedback to automatically extract pros, cons, and bottom-line sentiment.
- **Geospatial Mapping**: Leaflet.js with OpenStreetMap (OSM) for zero-cost, high-performance interactive maps, pin clusters, radius queries, and a drag-and-drop location picker for owners.
- **Version Control**: Git & GitHub repository.

---

## 2. Directory & Folder Structure

```text
AI_PG_Room_Finder/
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore configurations
├── README.md                     # Project documentation & architectural plan
├── requirements.txt              # Python dependencies
├── run.py                        # Flask server bootstrap entry point
│
├── app/
│   ├── __init__.py               # Flask application factory
│   ├── config.py                 # Configuration settings (Dev/Prod)
│   ├── database.py               # MySQL connection pooling & cursor helpers
│   │
│   ├── models/                   # Database data access objects (DAOs)
│   │   ├── __init__.py
│   │   ├── user.py               # User and authentication queries
│   │   ├── property.py           # Property and room inventory queries
│   │   ├── amenity.py            # Amenity catalog queries
│   │   ├── booking.py            # Visit scheduling & booking inquiries
│   │   ├── review.py             # Reviews and rating calculations
│   │   └── wishlist.py           # Tenant saved properties
│   │
│   ├── routes/                   # Flask Blueprints
│   │   ├── __init__.py
│   │   ├── auth_routes.py        # Authentication & profile management
│   │   ├── tenant_routes.py      # Tenant search, detail, and bookings
│   │   ├── owner_routes.py       # Owner dashboard and listing manager
│   │   ├── admin_routes.py       # Admin verification and moderation
│   │   └── api_routes.py         # REST endpoints for map & AI search
│   │
│   ├── services/                 # Business logic and AI engines
│   │   ├── __init__.py
│   │   ├── auth_service.py       # Password hashing & session auth
│   │   ├── property_service.py   # Filtering and spatial search logic
│   │   ├── map_service.py        # Geocoding & coordinate calculations
│   │   ├── ai_search_service.py  # NLP natural language query parser
│   │   ├── ai_recommender.py     # Multi-criteria recommendation engine
│   │   └── ai_review_service.py  # Review sentiment & pros/cons extraction
│   │
│   ├── static/                   # Static client assets
│   │   ├── css/
│   │   │   ├── main.css          # Design system, CSS variables & typography
│   │   │   ├── navbar.css        # Responsive navigation bar
│   │   │   ├── card.css          # Listing cards & hover states
│   │   │   ├── map.css           # Leaflet pins, popups & map frame
│   │   │   ├── forms.css         # Form elements, toggles & sliders
│   │   │   └── dashboard.css     # Tables & metric cards for Owner/Admin
│   │   ├── js/
│   │   │   ├── main.js           # Global UI utils & toast alerts
│   │   │   ├── map.js            # Leaflet map rendering & marker sync
│   │   │   ├── location_picker.js# Drag-and-drop map pin coordinate picker
│   │   │   ├── search_filter.js  # Dynamic AJAX search & filter state
│   │   │   └── ai_search.js      # Natural language search bar handler
│   │   ├── images/               # Default avatars, banners & SVG icons
│   │   └── uploads/              # Uploaded property & room images
│   │
│   └── templates/                # Jinja2 HTML templates
│       ├── base.html             # Base layout template
│       ├── components/           # Reusable partials (navbar, footer, cards)
│       ├── auth/                 # Login, register, profile
│       ├── tenant/               # Home, search results, property detail, bookings, wishlist
│       ├── owner/                # Dashboard, add listing, manage listings, inquiries
│       └── admin/                # Platform KPIs, listing verification, user management
│
├── database/
│   ├── schema.sql                # Complete MySQL DDL schema
│   └── seed_data.sql             # Realistic demo data (users, PGs, rooms, reviews)
│
└── tests/
    ├── test_auth.py              # Authentication test cases
    ├── test_properties.py        # Property CRUD & filter tests
    └── test_ai_services.py       # NLP & recommendation test cases
```

---

## 3. Database Tables & Relationships

The relational model consists of 11 core tables designed in 3rd Normal Form (3NF) with full foreign key constraints and query indexes:

| Table | Purpose | Key Columns & Relations |
| :--- | :--- | :--- |
| `users` | Accounts for all 3 roles (`tenant`, `owner`, `admin`) | `id`, `email` (UNIQUE), `password_hash`, `role`, `is_verified`, `is_active` |
| `properties` | Primary PG & room listings | `id`, `owner_id` (FK -> `users`), `title`, `slug`, `property_type`, `gender_preference`, `city`, `latitude`, `longitude`, `min_price`, `max_price`, `status` |
| `rooms` | Specific room sharing options & pricing | `id`, `property_id` (FK -> `properties`), `room_type`, `total_beds`, `available_beds`, `monthly_rent`, `security_deposit`, `has_ac`, `has_attached_bathroom` |
| `amenities` | Master amenities catalog | `id`, `name`, `category`, `icon_code` |
| `property_amenities`| Many-to-many junction | `property_id`, `amenity_id` (Composite Primary Key) |
| `property_images` | Gallery images for listings | `id`, `property_id` (FK -> `properties`), `image_url`, `is_cover` |
| `inquiries_bookings`| Visit schedules & inquiries | `id`, `tenant_id`, `property_id`, `room_id`, `inquiry_type`, `visit_date`, `status` (`pending`, `confirmed`, `declined`) |
| `reviews` | Tenant ratings & comments | `id`, `property_id`, `tenant_id`, `rating_overall`, `rating_cleanliness`, `rating_food`, `rating_safety`, `comment`, `sentiment_label` |
| `ai_review_summaries`| Precomputed AI feedback summaries | `id`, `property_id` (UNIQUE), `pros_list` (JSON), `cons_list` (JSON), `overall_summary`, `average_sentiment_score` |
| `wishlists` | Tenant saved listings | `id`, `tenant_id`, `property_id` (UNIQUE pair) |
| `user_search_preferences`| User search behavior & profile | `id`, `tenant_id`, `preferred_city`, `max_budget`, `preferred_sharing`, `last_search_query` |

---

## 4. List of Pages & Features

### Tenant Features
1. **Homepage (`/`)**: Hero section with AI NLP search bar, popular cities grid, verified PG badges, and personalized recommendation carousel.
2. **Search & Map Discovery (`/search`)**: Interactive dual-pane view: listing cards on the left synchronized with dynamic Leaflet OpenStreetMap markers on the right. Instant filters for budget, gender, sharing, and facilities.
3. **Property Details (`/property/<slug>`)**: Photo carousel, room options with live availability, amenities checklist, interactive map location, AI-generated Pros & Cons review summary, and verified tenant reviews.
4. **Visit Scheduler / Booking Modal**: Pick visit date, preferred time slot, and submit inquiry to property owner.
5. **My Bookings (`/tenant/bookings`)**: Real-time status tracker for scheduled visits (Pending, Confirmed, Declined).
6. **Wishlist (`/tenant/wishlist`)**: Collection of bookmarked PGs for quick comparison.

### Property Owner Features
1. **Owner Dashboard (`/owner/dashboard`)**: Metric cards for active listings, available beds, pending visit inquiries, and average ratings.
2. **Add / Edit Property Wizard (`/owner/property/new`)**: Multi-step form with basic info, room configurations, amenities picker, photo upload, and **Leaflet drag-and-drop pin selector** to pinpoint exact coordinates.
3. **Manage Listings (`/owner/properties`)**: View all listings with live status (`Approved`, `Pending Verification`), edit details, and toggle bed availability.
4. **Inquiry Manager (`/owner/inquiries`)**: View tenant visit requests with one-click "Accept", "Reschedule", or "Decline".
5. **Reviews & Sentiment Analytics (`/owner/analytics`)**: Detailed feedback breakdowns and AI summary of what tenants appreciate most.

### Admin Features
1. **Admin Master Dashboard (`/admin/dashboard`)**: Platform-wide metrics: total tenants, owners, active listings, pending verifications, and recent activity log.
2. **Listing Verification Queue (`/admin/listings/verify`)**: Review owner submissions and approve or reject listings with reason notes.
3. **User Management (`/admin/users`)**: Search, filter, and activate/deactivate user accounts.
4. **Master Amenities Management (`/admin/amenities`)**: Add or edit platform-wide amenities and icons.

---

## 5. Development Steps & Roadmap

- **Phase 1: Environment & Database Setup** *(In Progress)*
  - Initialize Git repo, directory scaffolding, dependencies, MySQL DDL schema (`database/schema.sql`), and sample data (`database/seed_data.sql`).
- **Phase 2: Authentication & Design System**
  - Application factory, database connection pool, session-based auth (Tenant, Owner, Admin), and responsive base layout with modern CSS tokens.
- **Phase 3: Owner Listing & Inventory Module**
  - Multi-step property creation, Leaflet pin picker, room pricing, photo management, and owner dashboard.
- **Phase 4: Tenant Discovery & Interactive Maps**
  - Homepage, split-pane search with Leaflet map synchronization, multi-facet filtering, and booking/visit request flow.
- **Phase 5: AI Engine Integration**
  - Natural Language search parser, recommendation engine (cosine similarity scoring), and review summarization pipeline.
- **Phase 6: Admin Dashboard & Governance**
  - Listing approval queue, user moderation, and master amenities manager.
- **Phase 7: Testing, Polish & Documentation**
  - Unit tests, responsive UI verification, security checks, and final deployment documentation.
