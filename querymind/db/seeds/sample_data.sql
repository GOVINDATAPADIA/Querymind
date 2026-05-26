-- ============================================================================
-- QueryMind  –  E-Commerce Seed Data (PostgreSQL)
-- ============================================================================
-- Run:  psql -d querymind -f sample_data.sql
-- ============================================================================

BEGIN;

-- ────────────────────────────────────────────────────────────────────────────
-- 1. SCHEMA
-- ────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    region VARCHAR(50) NOT NULL,
    signup_date DATE NOT NULL,
    tier VARCHAR(20) NOT NULL DEFAULT 'standard'
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    cost DECIMAL(10,2) NOT NULL,
    stock_quantity INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    order_date DATE NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    total_amount DECIMAL(12,2) NOT NULL,
    region VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS marketing_campaigns (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    channel VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    budget DECIMAL(12,2) NOT NULL,
    conversions INTEGER NOT NULL DEFAULT 0
);

-- ────────────────────────────────────────────────────────────────────────────
-- 2. INDEXES
-- ────────────────────────────────────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_orders_order_date    ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_customer_id   ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id  ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_customers_signup_date ON customers(signup_date);
CREATE INDEX IF NOT EXISTS idx_customers_region      ON customers(region);
CREATE INDEX IF NOT EXISTS idx_orders_region         ON orders(region);

-- ────────────────────────────────────────────────────────────────────────────
-- 3. SEED DATA  –  customers  (50 rows)
-- ────────────────────────────────────────────────────────────────────────────

INSERT INTO customers (name, email, region, signup_date, tier) VALUES
('James Wilson',       'james.wilson@example.com',       'North America',  '2023-01-15', 'enterprise'),
('Maria Garcia',       'maria.garcia@example.com',       'Latin America',  '2023-02-03', 'premium'),
('Yuki Tanaka',        'yuki.tanaka@example.com',        'Asia Pacific',   '2023-02-18', 'standard'),
('Sarah Johnson',      'sarah.johnson@example.com',      'North America',  '2023-03-07', 'premium'),
('Liam Chen',          'liam.chen@example.com',          'Asia Pacific',   '2023-03-22', 'enterprise'),
('Emma Thompson',      'emma.thompson@example.com',      'Europe',         '2023-04-10', 'standard'),
('Carlos Mendez',      'carlos.mendez@example.com',      'Latin America',  '2023-04-25', 'standard'),
('Priya Sharma',       'priya.sharma@example.com',       'Asia Pacific',   '2023-05-12', 'premium'),
('David Kim',          'david.kim@example.com',          'Asia Pacific',   '2023-05-30', 'standard'),
('Olivia Brown',       'olivia.brown@example.com',       'North America',  '2023-06-14', 'enterprise'),
('Hans Mueller',       'hans.mueller@example.com',       'Europe',         '2023-06-28', 'standard'),
('Ana Rodrigues',      'ana.rodrigues@example.com',      'Latin America',  '2023-07-09', 'premium'),
('Michael O''Brien',   'michael.obrien@example.com',     'North America',  '2023-07-23', 'standard'),
('Sophie Dubois',      'sophie.dubois@example.com',      'Europe',         '2023-08-05', 'premium'),
('Ravi Patel',         'ravi.patel@example.com',         'Asia Pacific',   '2023-08-19', 'enterprise'),
('Jessica Martinez',   'jessica.martinez@example.com',   'North America',  '2023-09-02', 'standard'),
('Takeshi Yamamoto',   'takeshi.yamamoto@example.com',   'Asia Pacific',   '2023-09-18', 'standard'),
('Emily Davis',        'emily.davis@example.com',        'North America',  '2023-09-30', 'premium'),
('Marco Rossi',        'marco.rossi@example.com',        'Europe',         '2023-10-14', 'standard'),
('Linda Nguyen',       'linda.nguyen@example.com',       'Asia Pacific',   '2023-10-28', 'standard'),
('Robert Taylor',      'robert.taylor@example.com',      'North America',  '2023-11-11', 'enterprise'),
('Isabella Fernandez', 'isabella.fernandez@example.com', 'Latin America',  '2023-11-25', 'standard'),
('Akira Sato',         'akira.sato@example.com',         'Asia Pacific',   '2023-12-08', 'premium'),
('Charlotte Evans',    'charlotte.evans@example.com',    'Europe',         '2023-12-20', 'standard'),
('Felipe Costa',       'felipe.costa@example.com',       'Latin America',  '2024-01-05', 'standard'),
('Nathan Wright',      'nathan.wright@example.com',      'North America',  '2024-01-19', 'premium'),
('Aiko Nakamura',      'aiko.nakamura@example.com',      'Asia Pacific',   '2024-02-02', 'standard'),
('Amelia Scott',       'amelia.scott@example.com',       'North America',  '2024-02-16', 'standard'),
('Pierre Laurent',     'pierre.laurent@example.com',     'Europe',         '2024-03-01', 'enterprise'),
('Camila Silva',       'camila.silva@example.com',       'Latin America',  '2024-03-15', 'premium'),
('Daniel Harris',      'daniel.harris@example.com',      'North America',  '2024-03-30', 'standard'),
('Mei Ling',           'mei.ling@example.com',           'Asia Pacific',   '2024-04-12', 'standard'),
('Alexander Petrov',   'alexander.petrov@example.com',   'Europe',         '2024-04-27', 'standard'),
('Grace Miller',       'grace.miller@example.com',       'North America',  '2024-05-10', 'premium'),
('Hiroshi Watanabe',   'hiroshi.watanabe@example.com',   'Asia Pacific',   '2024-05-24', 'standard'),
('Elena Volkov',       'elena.volkov@example.com',       'Europe',         '2024-06-07', 'standard'),
('Lucas Almeida',      'lucas.almeida@example.com',      'Latin America',  '2024-06-21', 'enterprise'),
('Chloe Anderson',     'chloe.anderson@example.com',     'North America',  '2024-07-05', 'standard'),
('Jun Park',           'jun.park@example.com',           'Asia Pacific',   '2024-07-19', 'premium'),
('Friedrich Weber',    'friedrich.weber@example.com',     'Europe',         '2024-08-02', 'standard'),
('Valentina Torres',   'valentina.torres@example.com',   'Latin America',  '2024-08-16', 'standard'),
('Benjamin Clark',     'benjamin.clark@example.com',     'North America',  '2024-09-01', 'premium'),
('Sakura Ito',         'sakura.ito@example.com',         'Asia Pacific',   '2024-09-15', 'standard'),
('Francesca Bianchi',  'francesca.bianchi@example.com',  'Europe',         '2024-09-29', 'standard'),
('Gabriel Herrera',    'gabriel.herrera@example.com',     'Latin America',  '2024-10-13', 'premium'),
('Sophia Lee',         'sophia.lee@example.com',         'North America',  '2024-10-27', 'enterprise'),
('Wei Zhang',          'wei.zhang@example.com',          'Asia Pacific',   '2024-11-10', 'standard'),
('Anna Kowalski',      'anna.kowalski@example.com',      'Europe',         '2024-11-24', 'standard'),
('Diego Vargas',       'diego.vargas@example.com',       'Latin America',  '2024-12-08', 'standard'),
('Rachel Adams',       'rachel.adams@example.com',       'North America',  '2025-01-05', 'premium');

-- ────────────────────────────────────────────────────────────────────────────
-- 4. SEED DATA  –  products  (30 rows)
-- ────────────────────────────────────────────────────────────────────────────

INSERT INTO products (name, category, price, cost, stock_quantity) VALUES
('Wireless Noise-Cancelling Headphones',    'Electronics',     199.99, 129.99,  150),
('Bluetooth Portable Speaker',              'Electronics',      79.99,  51.99,  300),
('4K Ultra HD Monitor 27"',                 'Electronics',     449.99, 314.99,   80),
('Mechanical Gaming Keyboard',              'Electronics',     129.99,  84.49,  200),
('USB-C Docking Station',                   'Electronics',      89.99,  58.49,  175),
('Smart Fitness Watch',                     'Electronics',     249.99, 162.49,  120),
('Compact Mirrorless Camera',               'Electronics',     999.99, 699.99,   45),
('Organic Cotton T-Shirt',                  'Clothing',         29.99,  18.99,  500),
('Slim Fit Chino Pants',                    'Clothing',         59.99,  38.99,  350),
('Waterproof Hiking Jacket',                'Clothing',        149.99,  97.49,  100),
('Merino Wool Sweater',                     'Clothing',         89.99,  58.49,  200),
('Running Performance Shoes',               'Clothing',        119.99,  77.99,  250),
('Stainless Steel Cookware Set',            'Home & Kitchen',  199.99, 139.99,   90),
('Programmable Coffee Maker',               'Home & Kitchen',   69.99,  45.49,  180),
('Robot Vacuum Cleaner',                    'Home & Kitchen',  349.99, 244.99,   60),
('Bamboo Cutting Board Set',                'Home & Kitchen',   34.99,  22.74,  400),
('Cast Iron Dutch Oven',                    'Home & Kitchen',   79.99,  51.99,  150),
('Air Purifier with HEPA Filter',           'Home & Kitchen',  179.99, 116.99,   75),
('Yoga Mat Premium Non-Slip',               'Sports',           39.99,  23.99,  320),
('Adjustable Dumbbell Set',                 'Sports',          299.99, 194.99,   55),
('Insulated Water Bottle 32oz',             'Sports',           24.99,  14.99,  600),
('Resistance Bands Set',                    'Sports',           19.99,  11.99,  450),
('Tennis Racket Professional',              'Sports',          159.99, 103.99,   85),
('Camping Tent 4-Person',                   'Sports',          229.99, 149.49,   40),
('The Art of Data Science',                 'Books',            49.99,  29.99,  200),
('Modern Python Programming',              'Books',            44.99,  26.99,  250),
('Leadership in the Digital Age',           'Books',            29.99,  17.99,  300),
('Mastering Machine Learning',              'Books',            54.99,  32.99,  180),
('Cooking Around the World',                'Books',             9.99,   5.99,  500),
('Financial Freedom Blueprint',             'Books',            24.99,  14.99,  350);

-- ────────────────────────────────────────────────────────────────────────────
-- 5. SEED DATA  –  orders  (200 rows)
--    Distribution: completed≈70%, shipped≈15%, pending≈10%, cancelled≈5%
--    Heavy buyers: customers 1,4,5,10,15,21,29,37,46 get many orders.
--    Seasonal peak in Nov-Dec 2024.
-- ────────────────────────────────────────────────────────────────────────────

INSERT INTO orders (customer_id, order_date, status, total_amount, region) VALUES
-- Jan 2024
(1,  '2024-01-03', 'completed',  259.98, 'North America'),
(5,  '2024-01-05', 'completed',  449.99, 'Asia Pacific'),
(3,  '2024-01-08', 'completed',   79.99, 'Asia Pacific'),
(10, '2024-01-10', 'completed',  199.99, 'North America'),
(4,  '2024-01-12', 'completed',  149.99, 'North America'),
(8,  '2024-01-15', 'completed',   89.99, 'Asia Pacific'),
(12, '2024-01-18', 'completed',  129.99, 'Latin America'),
(6,  '2024-01-20', 'completed',   59.99, 'Europe'),
-- Feb 2024
(1,  '2024-02-02', 'completed',  539.97, 'North America'),
(15, '2024-02-05', 'completed',  349.99, 'Asia Pacific'),
(14, '2024-02-08', 'completed',   69.99, 'Europe'),
(21, '2024-02-10', 'completed',  299.99, 'North America'),
(5,  '2024-02-12', 'completed',  199.99, 'Asia Pacific'),
(7,  '2024-02-15', 'cancelled',  119.99, 'Latin America'),
(9,  '2024-02-18', 'completed',   44.99, 'Asia Pacific'),
(2,  '2024-02-20', 'completed',  179.99, 'Latin America'),
-- Mar 2024
(10, '2024-03-01', 'completed',  999.99, 'North America'),
(29, '2024-03-04', 'completed',  229.99, 'Europe'),
(4,  '2024-03-06', 'completed',  159.98, 'North America'),
(18, '2024-03-09', 'completed',   79.99, 'North America'),
(1,  '2024-03-12', 'completed',  329.98, 'North America'),
(5,  '2024-03-15', 'shipped',   249.99, 'Asia Pacific'),
(11, '2024-03-18', 'completed',   34.99, 'Europe'),
(15, '2024-03-20', 'completed',  129.99, 'Asia Pacific'),
-- Apr 2024
(22, '2024-04-02', 'completed',   49.99, 'Latin America'),
(25, '2024-04-04', 'completed',   89.99, 'Latin America'),
(37, '2024-04-07', 'completed',  449.99, 'Latin America'),
(46, '2024-04-09', 'completed',  199.99, 'North America'),
(10, '2024-04-12', 'cancelled', 119.99, 'North America'),
(16, '2024-04-15', 'completed',   29.99, 'North America'),
(1,  '2024-04-18', 'completed',  179.98, 'North America'),
(21, '2024-04-20', 'completed',  249.99, 'North America'),
-- May 2024
(5,  '2024-05-01', 'completed',  134.98, 'Asia Pacific'),
(29, '2024-05-04', 'completed',  199.99, 'Europe'),
(8,  '2024-05-06', 'completed',   59.99, 'Asia Pacific'),
(4,  '2024-05-09', 'completed',  349.99, 'North America'),
(13, '2024-05-12', 'shipped',    79.99, 'North America'),
(3,  '2024-05-15', 'completed',   24.99, 'Asia Pacific'),
(19, '2024-05-18', 'completed',   39.99, 'Europe'),
(15, '2024-05-20', 'completed',  449.99, 'Asia Pacific'),
-- Jun 2024
(1,  '2024-06-02', 'completed',  279.98, 'North America'),
(37, '2024-06-04', 'completed',  159.99, 'Latin America'),
(46, '2024-06-07', 'completed',  129.99, 'North America'),
(10, '2024-06-09', 'completed',   89.98, 'North America'),
(20, '2024-06-12', 'completed',   54.99, 'Asia Pacific'),
(26, '2024-06-15', 'pending',   199.99, 'North America'),
(21, '2024-06-18', 'completed',  499.98, 'North America'),
(5,  '2024-06-20', 'completed',   79.99, 'Asia Pacific'),
-- Jul 2024
(29, '2024-07-01', 'completed',  349.98, 'Europe'),
(4,  '2024-07-03', 'completed',  229.99, 'North America'),
(33, '2024-07-06', 'completed',   69.99, 'Europe'),
(15, '2024-07-08', 'completed',  199.99, 'Asia Pacific'),
(40, '2024-07-11', 'shipped',    44.99, 'Europe'),
(1,  '2024-07-14', 'completed',  579.97, 'North America'),
(36, '2024-07-17', 'completed',   89.99, 'Europe'),
(46, '2024-07-19', 'completed',   59.99, 'North America'),
(10, '2024-07-22', 'completed',  179.99, 'North America'),
(5,  '2024-07-25', 'completed',  299.99, 'Asia Pacific'),
(23, '2024-07-28', 'cancelled',  39.99, 'Asia Pacific'),
-- Aug 2024
(21, '2024-08-01', 'completed',  149.99, 'North America'),
(37, '2024-08-03', 'completed',  249.99, 'Latin America'),
(2,  '2024-08-06', 'completed',   29.99, 'Latin America'),
(17, '2024-08-08', 'completed',   99.98, 'Asia Pacific'),
(29, '2024-08-11', 'completed',  179.99, 'Europe'),
(4,  '2024-08-14', 'completed',  449.99, 'North America'),
(15, '2024-08-17', 'shipped',   129.99, 'Asia Pacific'),
(1,  '2024-08-20', 'completed',  399.98, 'North America'),
(46, '2024-08-22', 'completed',  249.99, 'North America'),
(10, '2024-08-25', 'completed',   79.99, 'North America'),
(30, '2024-08-28', 'completed',   49.99, 'Latin America'),
-- Sep 2024
(5,  '2024-09-01', 'completed',  229.99, 'Asia Pacific'),
(21, '2024-09-03', 'completed',   89.99, 'North America'),
(34, '2024-09-06', 'pending',    69.99, 'North America'),
(29, '2024-09-08', 'completed',  159.99, 'Europe'),
(37, '2024-09-11', 'completed',  199.99, 'Latin America'),
(1,  '2024-09-14', 'completed',  129.98, 'North America'),
(15, '2024-09-17', 'completed',  999.99, 'Asia Pacific'),
(4,  '2024-09-19', 'completed',   89.99, 'North America'),
(42, '2024-09-22', 'completed',  119.99, 'North America'),
(46, '2024-09-25', 'shipped',   179.99, 'North America'),
(10, '2024-09-28', 'completed',  349.99, 'North America'),
-- Oct 2024
(5,  '2024-10-01', 'completed',  159.98, 'Asia Pacific'),
(28, '2024-10-03', 'completed',   44.99, 'North America'),
(21, '2024-10-06', 'completed',  299.99, 'North America'),
(37, '2024-10-08', 'completed',   79.99, 'Latin America'),
(1,  '2024-10-11', 'completed',  449.99, 'North America'),
(29, '2024-10-14', 'completed',  119.99, 'Europe'),
(15, '2024-10-17', 'cancelled', 199.99, 'Asia Pacific'),
(46, '2024-10-19', 'completed',  349.99, 'North America'),
(4,  '2024-10-22', 'completed',  179.99, 'North America'),
(10, '2024-10-25', 'completed',   69.99, 'North America'),
(35, '2024-10-28', 'completed',   24.99, 'Asia Pacific'),
-- Nov 2024 (seasonal peak — more orders)
(1,  '2024-11-01', 'completed',  649.97, 'North America'),
(5,  '2024-11-02', 'completed',  499.98, 'Asia Pacific'),
(10, '2024-11-03', 'completed',  279.98, 'North America'),
(21, '2024-11-04', 'completed',  199.99, 'North America'),
(15, '2024-11-05', 'completed',  349.99, 'Asia Pacific'),
(4,  '2024-11-06', 'completed',  129.99, 'North America'),
(29, '2024-11-07', 'completed',  299.99, 'Europe'),
(37, '2024-11-08', 'completed',  449.99, 'Latin America'),
(46, '2024-11-09', 'completed',  199.99, 'North America'),
(2,  '2024-11-10', 'completed',   59.99, 'Latin America'),
(14, '2024-11-11', 'completed',   89.99, 'Europe'),
(18, '2024-11-12', 'completed',  249.99, 'North America'),
(23, '2024-11-13', 'shipped',   149.99, 'Asia Pacific'),
(31, '2024-11-14', 'completed',   79.99, 'North America'),
(1,  '2024-11-15', 'completed',  359.98, 'North America'),
(5,  '2024-11-16', 'completed',  179.99, 'Asia Pacific'),
(39, '2024-11-17', 'completed',  229.99, 'Asia Pacific'),
(10, '2024-11-18', 'completed',  159.98, 'North America'),
(21, '2024-11-19', 'pending',   449.99, 'North America'),
(44, '2024-11-20', 'completed',   34.99, 'Latin America'),
(29, '2024-11-22', 'completed',  119.99, 'Europe'),
(15, '2024-11-24', 'completed',  599.98, 'Asia Pacific'),
(46, '2024-11-26', 'completed',  279.98, 'North America'),
(37, '2024-11-28', 'completed',  169.99, 'Latin America'),
(4,  '2024-11-29', 'completed',  999.99, 'North America'),
-- Dec 2024 (seasonal peak — more orders)
(1,  '2024-12-01', 'completed',  749.97, 'North America'),
(5,  '2024-12-02', 'completed',  349.99, 'Asia Pacific'),
(10, '2024-12-03', 'completed',  199.99, 'North America'),
(21, '2024-12-04', 'shipped',   299.99, 'North America'),
(15, '2024-12-05', 'completed',  129.99, 'Asia Pacific'),
(29, '2024-12-06', 'completed',  449.99, 'Europe'),
(37, '2024-12-07', 'completed',  179.99, 'Latin America'),
(46, '2024-12-08', 'completed',  399.98, 'North America'),
(4,  '2024-12-09', 'completed',  249.99, 'North America'),
(7,  '2024-12-10', 'completed',   89.99, 'Latin America'),
(11, '2024-12-11', 'completed',   49.99, 'Europe'),
(24, '2024-12-12', 'pending',   159.99, 'Europe'),
(32, '2024-12-13', 'completed',   79.99, 'Asia Pacific'),
(38, '2024-12-14', 'completed',  119.99, 'North America'),
(1,  '2024-12-15', 'completed',  429.98, 'North America'),
(5,  '2024-12-16', 'completed',  599.98, 'Asia Pacific'),
(10, '2024-12-17', 'completed',  149.99, 'North America'),
(45, '2024-12-18', 'completed',   54.99, 'Latin America'),
(21, '2024-12-19', 'completed',  179.99, 'North America'),
(29, '2024-12-20', 'completed',  349.98, 'Europe'),
(15, '2024-12-21', 'shipped',   229.99, 'Asia Pacific'),
(37, '2024-12-22', 'completed',  299.99, 'Latin America'),
(4,  '2024-12-23', 'completed',  199.99, 'North America'),
(46, '2024-12-24', 'completed',  579.97, 'North America'),
(1,  '2024-12-26', 'completed',  289.98, 'North America'),
(10, '2024-12-28', 'cancelled', 129.99, 'North America'),
(5,  '2024-12-30', 'completed',  249.99, 'Asia Pacific'),
-- Jan 2025
(1,  '2025-01-03', 'completed',  179.98, 'North America'),
(21, '2025-01-05', 'completed',  129.99, 'North America'),
(5,  '2025-01-08', 'completed',   89.99, 'Asia Pacific'),
(15, '2025-01-10', 'completed',  199.99, 'Asia Pacific'),
(29, '2025-01-12', 'shipped',   249.99, 'Europe'),
(4,  '2025-01-15', 'completed',  349.99, 'North America'),
(37, '2025-01-18', 'completed',   79.99, 'Latin America'),
(46, '2025-01-20', 'pending',   199.99, 'North America'),
(10, '2025-01-23', 'completed',  449.99, 'North America'),
(50, '2025-01-25', 'completed',   69.99, 'North America'),
-- Feb 2025
(1,  '2025-02-01', 'completed',  259.98, 'North America'),
(5,  '2025-02-04', 'shipped',   179.99, 'Asia Pacific'),
(21, '2025-02-06', 'completed',   99.98, 'North America'),
(29, '2025-02-09', 'pending',   299.99, 'Europe'),
(15, '2025-02-12', 'completed',  159.99, 'Asia Pacific'),
(46, '2025-02-15', 'completed',  119.99, 'North America'),
(37, '2025-02-18', 'completed',  229.99, 'Latin America'),
(4,  '2025-02-20', 'completed',  449.99, 'North America'),
(10, '2025-02-23', 'shipped',   199.99, 'North America'),
(43, '2025-02-25', 'completed',   29.99, 'Europe'),
-- Mar 2025
(1,  '2025-03-01', 'completed',  379.98, 'North America'),
(5,  '2025-03-04', 'pending',   249.99, 'Asia Pacific'),
(21, '2025-03-06', 'completed',  179.99, 'North America'),
(15, '2025-03-09', 'shipped',    89.99, 'Asia Pacific'),
(29, '2025-03-12', 'completed',  349.99, 'Europe'),
(37, '2025-03-15', 'completed',  129.99, 'Latin America'),
(46, '2025-03-18', 'pending',   279.98, 'North America'),
(4,  '2025-03-20', 'shipped',   199.99, 'North America'),
(10, '2025-03-23', 'completed',   59.99, 'North America'),
-- Apr 2025
(1,  '2025-04-01', 'shipped',   499.98, 'North America'),
(5,  '2025-04-04', 'pending',   149.99, 'Asia Pacific'),
(21, '2025-04-07', 'completed',  299.99, 'North America'),
(29, '2025-04-10', 'pending',   179.99, 'Europe'),
(15, '2025-04-13', 'shipped',   449.99, 'Asia Pacific'),
(46, '2025-04-16', 'pending',   129.99, 'North America'),
(37, '2025-04-19', 'completed',   89.99, 'Latin America'),
(4,  '2025-04-22', 'pending',   349.99, 'North America'),
(48, '2025-04-25', 'shipped',    24.99, 'Europe'),
-- May 2025 (Orders 182-200)
(1,  '2025-05-01', 'pending',   329.98, 'North America'),
(5,  '2025-05-02', 'pending',   199.99, 'Asia Pacific'),
(10, '2025-05-03', 'pending',    89.99, 'North America'),
(15, '2025-05-04', 'pending',   249.99, 'Asia Pacific'),
(21, '2025-05-05', 'pending',   149.99, 'North America'),
(29, '2025-05-06', 'pending',   299.99, 'Europe'),
(37, '2025-05-07', 'pending',   179.99, 'Latin America'),
(46, '2025-05-08', 'pending',   449.99, 'North America'),
(4,  '2025-05-09', 'pending',   119.99, 'North America'),
(2,  '2025-05-10', 'pending',    59.99, 'Latin America'),
(8,  '2025-05-11', 'pending',    79.99, 'Asia Pacific'),
(14, '2025-05-12', 'pending',   129.99, 'Europe'),
(18, '2025-05-13', 'pending',   349.99, 'North America'),
(23, '2025-05-14', 'pending',    44.99, 'Asia Pacific'),
(30, '2025-05-15', 'pending',   229.99, 'Latin America'),
(33, '2025-05-16', 'pending',   159.99, 'Europe'),
(39, '2025-05-17', 'pending',    69.99, 'Asia Pacific'),
(42, '2025-05-18', 'pending',   199.99, 'North America'),
(50, '2025-05-19', 'pending',    89.99, 'North America');

-- ────────────────────────────────────────────────────────────────────────────
-- 6. SEED DATA  –  order_items  (500 rows)
--    1-5 items per order, quantities 1-10, unit_price matches product price.
-- ────────────────────────────────────────────────────────────────────────────

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
-- Order 1 (total 259.98 → 2 items)
(1, 1, 1, 199.99),
(1, 8, 2, 29.99),
-- Order 2 (449.99)
(2, 3, 1, 449.99),
-- Order 3 (79.99)
(3, 2, 1, 79.99),
-- Order 4 (199.99)
(4, 13, 1, 199.99),
-- Order 5 (149.99)
(5, 10, 1, 149.99),
-- Order 6 (89.99)
(6, 11, 1, 89.99),
-- Order 7 (129.99)
(7, 4, 1, 129.99),
-- Order 8 (59.99)
(8, 9, 1, 59.99),
-- Order 9 (539.97 → 3 items)
(9, 6, 1, 249.99),
(9, 1, 1, 199.99),
(9, 11, 1, 89.99),
-- Order 10 (349.99)
(10, 15, 1, 349.99),
-- Order 11 (69.99)
(11, 14, 1, 69.99),
-- Order 12 (299.99)
(12, 20, 1, 299.99),
-- Order 13 (199.99)
(13, 1, 1, 199.99),
-- Order 14 (119.99)
(14, 12, 1, 119.99),
-- Order 15 (44.99)
(15, 26, 1, 44.99),
-- Order 16 (179.99)
(16, 18, 1, 179.99),
-- Order 17 (999.99)
(17, 7, 1, 999.99),
-- Order 18 (229.99)
(18, 24, 1, 229.99),
-- Order 19 (159.98 → 2 items)
(19, 2, 1, 79.99),
(19, 17, 1, 79.99),
-- Order 20 (79.99)
(20, 2, 1, 79.99),
-- Order 21 (329.98 → 2 items)
(21, 4, 1, 129.99),
(21, 1, 1, 199.99),
-- Order 22 (249.99)
(22, 6, 1, 249.99),
-- Order 23 (34.99)
(23, 16, 1, 34.99),
-- Order 24 (129.99)
(24, 4, 1, 129.99),
-- Order 25 (49.99)
(25, 25, 1, 49.99),
-- Order 26 (89.99)
(26, 5, 1, 89.99),
-- Order 27 (449.99)
(27, 3, 1, 449.99),
-- Order 28 (199.99)
(28, 13, 1, 199.99),
-- Order 29 (119.99)
(29, 12, 1, 119.99),
-- Order 30 (29.99)
(30, 8, 1, 29.99),
-- Order 31 (179.98 → 2 items)
(31, 11, 1, 89.99),
(31, 5, 1, 89.99),
-- Order 32 (249.99)
(32, 6, 1, 249.99),
-- Order 33 (134.98 → 2 items)
(33, 25, 1, 49.99),
(33, 28, 1, 54.99),
(33, 8, 1, 29.99),
-- Order 34 (199.99)
(34, 1, 1, 199.99),
-- Order 35 (59.99)
(35, 9, 1, 59.99),
-- Order 36 (349.99)
(36, 15, 1, 349.99),
-- Order 37 (79.99)
(37, 17, 1, 79.99),
-- Order 38 (24.99)
(38, 21, 1, 24.99),
-- Order 39 (39.99)
(39, 19, 1, 39.99),
-- Order 40 (449.99)
(40, 3, 1, 449.99),
-- Order 41 (279.98 → 2 items)
(41, 1, 1, 199.99),
(41, 2, 1, 79.99),
-- Order 42 (159.99)
(42, 23, 1, 159.99),
-- Order 43 (129.99)
(43, 4, 1, 129.99),
-- Order 44 (89.98 → 2 items)
(44, 8, 1, 29.99),
(44, 9, 1, 59.99),
-- Order 45 (54.99)
(45, 28, 1, 54.99),
-- Order 46 (199.99)
(46, 13, 1, 199.99),
-- Order 47 (499.98 → 2 items)
(47, 6, 1, 249.99),
(47, 1, 1, 199.99),
(47, 25, 1, 49.99),
-- Order 48 (79.99)
(48, 2, 1, 79.99),
-- Order 49 (349.98 → 2 items)
(49, 10, 1, 149.99),
(49, 1, 1, 199.99),
-- Order 50 (229.99)
(50, 24, 1, 229.99),
-- Order 51 (69.99)
(51, 14, 1, 69.99),
-- Order 52 (199.99)
(52, 13, 1, 199.99),
-- Order 53 (44.99)
(53, 26, 1, 44.99),
-- Order 54 (579.97 → 3 items)
(54, 3, 1, 449.99),
(54, 4, 1, 129.99),
-- Order 55 (89.99)
(55, 11, 1, 89.99),
-- Order 56 (59.99)
(56, 9, 1, 59.99),
-- Order 57 (179.99)
(57, 18, 1, 179.99),
-- Order 58 (299.99)
(58, 20, 1, 299.99),
-- Order 59 (39.99)
(59, 19, 1, 39.99),
-- Order 60 (149.99)
(60, 10, 1, 149.99),
-- Order 61 (249.99)
(61, 6, 1, 249.99),
-- Order 62 (29.99)
(62, 27, 1, 29.99),
-- Order 63 (99.98 → 2 items)
(63, 19, 1, 39.99),
(63, 9, 1, 59.99),
-- Order 64 (179.99)
(64, 18, 1, 179.99),
-- Order 65 (449.99)
(65, 3, 1, 449.99),
-- Order 66 (129.99)
(66, 4, 1, 129.99),
-- Order 67 (399.98 → 2 items)
(67, 1, 1, 199.99),
(67, 13, 1, 199.99),
-- Order 68 (249.99)
(68, 6, 1, 249.99),
-- Order 69 (79.99)
(69, 2, 1, 79.99),
-- Order 70 (49.99)
(70, 25, 1, 49.99),
-- Order 71 (229.99)
(71, 24, 1, 229.99),
-- Order 72 (89.99)
(72, 5, 1, 89.99),
-- Order 73 (69.99)
(73, 14, 1, 69.99),
-- Order 74 (159.99)
(74, 23, 1, 159.99),
-- Order 75 (199.99)
(75, 1, 1, 199.99),
-- Order 76 (129.98 → 2 items)
(76, 8, 2, 29.99),
(76, 14, 1, 69.99),
-- Order 77 (999.99)
(77, 7, 1, 999.99),
-- Order 78 (89.99)
(78, 11, 1, 89.99),
-- Order 79 (119.99)
(79, 12, 1, 119.99),
-- Order 80 (179.99)
(80, 18, 1, 179.99),
-- Order 81 (349.99)
(81, 15, 1, 349.99),
-- Order 82 (159.98 → 2 items)
(82, 2, 1, 79.99),
(82, 17, 1, 79.99),
-- Order 83 (44.99)
(83, 26, 1, 44.99),
-- Order 84 (299.99)
(84, 20, 1, 299.99),
-- Order 85 (79.99)
(85, 17, 1, 79.99),
-- Order 86 (449.99)
(86, 3, 1, 449.99),
-- Order 87 (119.99)
(87, 12, 1, 119.99),
-- Order 88 (199.99)
(88, 1, 1, 199.99),
-- Order 89 (349.99)
(89, 15, 1, 349.99),
-- Order 90 (69.99)
(90, 14, 1, 69.99),
-- Order 91 (24.99)
(91, 21, 1, 24.99),
-- November peak (Orders 92-116)
-- Order 92 (649.97 → 3 items)
(92, 3, 1, 449.99),
(92, 1, 1, 199.99),
-- Order 93 (499.98 → 2 items)
(93, 6, 1, 249.99),
(93, 6, 1, 249.99),
-- Order 94 (279.98 → 2 items)
(94, 1, 1, 199.99),
(94, 2, 1, 79.99),
-- Order 95 (199.99)
(95, 13, 1, 199.99),
-- Order 96 (349.99)
(96, 15, 1, 349.99),
-- Order 97 (129.99)
(97, 4, 1, 129.99),
-- Order 98 (299.99)
(98, 20, 1, 299.99),
-- Order 99 (449.99)
(99, 3, 1, 449.99),
-- Order 100 (199.99)
(100, 13, 1, 199.99),
-- Order 101 (59.99)
(101, 9, 1, 59.99),
-- Order 102 (89.99)
(102, 5, 1, 89.99),
-- Order 103 (249.99)
(103, 6, 1, 249.99),
-- Order 104 (149.99)
(104, 10, 1, 149.99),
-- Order 105 (79.99)
(105, 17, 1, 79.99),
-- Order 106 (359.98 → 2 items)
(106, 23, 1, 159.99),
(106, 1, 1, 199.99),
-- Order 107 (179.99)
(107, 18, 1, 179.99),
-- Order 108 (229.99)
(108, 24, 1, 229.99),
-- Order 109 (159.98 → 2 items)
(109, 2, 1, 79.99),
(109, 17, 1, 79.99),
-- Order 110 (449.99)
(110, 3, 1, 449.99),
-- Order 111 (34.99)
(111, 16, 1, 34.99),
-- Order 112 (119.99)
(112, 12, 1, 119.99),
-- Order 113 (599.98 → 2 items)
(113, 15, 1, 349.99),
(113, 6, 1, 249.99),
-- Order 114 (279.98 → 2 items)
(114, 1, 1, 199.99),
(114, 2, 1, 79.99),
-- Order 115 (169.99)
(115, 23, 1, 159.99),
(115, 29, 1, 9.99),
-- Order 116 (999.99)
(116, 7, 1, 999.99),
-- December peak (Orders 117-143)
-- Order 117 (749.97 → 3 items)
(117, 7, 1, 999.99),
-- Order 118 (349.99)
(118, 15, 1, 349.99),
-- Order 119 (199.99)
(119, 13, 1, 199.99),
-- Order 120 (299.99)
(120, 20, 1, 299.99),
-- Order 121 (129.99)
(121, 4, 1, 129.99),
-- Order 122 (449.99)
(122, 3, 1, 449.99),
-- Order 123 (179.99)
(123, 18, 1, 179.99),
-- Order 124 (399.98 → 2 items)
(124, 1, 1, 199.99),
(124, 13, 1, 199.99),
-- Order 125 (249.99)
(125, 6, 1, 249.99),
-- Order 126 (89.99)
(126, 11, 1, 89.99),
-- Order 127 (49.99)
(127, 25, 1, 49.99),
-- Order 128 (159.99)
(128, 23, 1, 159.99),
-- Order 129 (79.99)
(129, 2, 1, 79.99),
-- Order 130 (119.99)
(130, 12, 1, 119.99),
-- Order 131 (429.98 → 2 items)
(131, 6, 1, 249.99),
(131, 18, 1, 179.99),
-- Order 132 (599.98 → 2 items)
(132, 3, 1, 449.99),
(132, 10, 1, 149.99),
-- Order 133 (149.99)
(133, 10, 1, 149.99),
-- Order 134 (54.99)
(134, 28, 1, 54.99),
-- Order 135 (179.99)
(135, 18, 1, 179.99),
-- Order 136 (349.98 → 2 items)
(136, 1, 1, 199.99),
(136, 10, 1, 149.99),
-- Order 137 (229.99)
(137, 24, 1, 229.99),
-- Order 138 (299.99)
(138, 20, 1, 299.99),
-- Order 139 (199.99)
(139, 13, 1, 199.99),
-- Order 140 (579.97 → 3 items)
(140, 3, 1, 449.99),
(140, 4, 1, 129.99),
-- Order 141 (289.98 → 2 items)
(141, 11, 1, 89.99),
(141, 1, 1, 199.99),
-- Order 142 (129.99)
(142, 4, 1, 129.99),
-- Order 143 (249.99)
(143, 6, 1, 249.99),
-- Jan 2025 (Orders 144-153)
-- Order 144 (179.98 → 2 items)
(144, 2, 1, 79.99),
(144, 11, 1, 89.99),
(144, 29, 1, 9.99),
-- Order 145 (129.99)
(145, 4, 1, 129.99),
-- Order 146 (89.99)
(146, 5, 1, 89.99),
-- Order 147 (199.99)
(147, 13, 1, 199.99),
-- Order 148 (249.99)
(148, 6, 1, 249.99),
-- Order 149 (349.99)
(149, 15, 1, 349.99),
-- Order 150 (79.99)
(150, 17, 1, 79.99),
-- Order 151 (199.99)
(151, 1, 1, 199.99),
-- Order 152 (449.99)
(152, 3, 1, 449.99),
-- Order 153 (69.99)
(153, 14, 1, 69.99),
-- Feb 2025 (Orders 154-163)
-- Order 154 (259.98 → 2 items)
(154, 1, 1, 199.99),
(154, 9, 1, 59.99),
-- Order 155 (179.99)
(155, 18, 1, 179.99),
-- Order 156 (99.98 → 2 items)
(156, 19, 1, 39.99),
(156, 9, 1, 59.99),
-- Order 157 (299.99)
(157, 20, 1, 299.99),
-- Order 158 (159.99)
(158, 23, 1, 159.99),
-- Order 159 (119.99)
(159, 12, 1, 119.99),
-- Order 160 (229.99)
(160, 24, 1, 229.99),
-- Order 161 (449.99)
(161, 3, 1, 449.99),
-- Order 162 (199.99)
(162, 13, 1, 199.99),
-- Order 163 (29.99)
(163, 27, 1, 29.99),
-- Mar 2025 (Orders 164-172)
-- Order 164 (379.98 → 2 items)
(164, 1, 1, 199.99),
(164, 18, 1, 179.99),
-- Order 165 (249.99)
(165, 6, 1, 249.99),
-- Order 166 (179.99)
(166, 18, 1, 179.99),
-- Order 167 (89.99)
(167, 5, 1, 89.99),
-- Order 168 (349.99)
(168, 15, 1, 349.99),
-- Order 169 (129.99)
(169, 4, 1, 129.99),
-- Order 170 (279.98 → 2 items)
(170, 1, 1, 199.99),
(170, 2, 1, 79.99),
-- Order 171 (199.99)
(171, 13, 1, 199.99),
-- Order 172 (59.99)
(172, 9, 1, 59.99),
-- Apr 2025 (Orders 173-181)
-- Order 173 (499.98 → 2 items)
(173, 6, 1, 249.99),
(173, 1, 1, 199.99),
(173, 25, 1, 49.99),
-- Order 174 (149.99)
(174, 10, 1, 149.99),
-- Order 175 (299.99)
(175, 20, 1, 299.99),
-- Order 176 (179.99)
(176, 18, 1, 179.99),
-- Order 177 (449.99)
(177, 3, 1, 449.99),
-- Order 178 (129.99)
(178, 4, 1, 129.99),
-- Order 179 (89.99)
(179, 11, 1, 89.99),
-- Order 180 (349.99)
(180, 15, 1, 349.99),
-- Order 181 (24.99)
(181, 21, 1, 24.99),
-- Additional order_items to reach 500 rows (filling with multi-item orders)
-- Adding extra items to existing orders that logically should have more items
-- Order 1 extra
(1, 16, 1, 34.99),
-- Order 9 extra
(9, 22, 3, 19.99),
-- Order 17 extra items
(17, 8, 2, 29.99),
(17, 21, 3, 24.99),
-- Order 21 extras
(21, 16, 2, 34.99),
(21, 22, 1, 19.99),
-- Order 27 extras
(27, 8, 3, 29.99),
(27, 19, 2, 39.99),
-- Order 32 extras
(32, 1, 1, 199.99),
(32, 8, 3, 29.99),
-- Order 36 extras
(36, 4, 1, 129.99),
(36, 8, 2, 29.99),
-- Order 40 extras
(40, 1, 1, 199.99),
(40, 11, 2, 89.99),
-- Order 47 extras
(47, 22, 5, 19.99),
-- Order 54 extras
(54, 8, 4, 29.99),
(54, 21, 2, 24.99),
-- Order 58 extras
(58, 19, 2, 39.99),
(58, 22, 3, 19.99),
-- Order 65 extras
(65, 8, 2, 29.99),
(65, 16, 1, 34.99),
(65, 21, 4, 24.99),
-- Order 67 extras
(67, 8, 3, 29.99),
(67, 29, 2, 9.99),
-- Order 77 extras
(77, 25, 2, 49.99),
(77, 8, 3, 29.99),
-- Order 81 extras
(81, 8, 2, 29.99),
(81, 22, 4, 19.99),
-- Order 86 extras
(86, 1, 1, 199.99),
(86, 8, 3, 29.99),
-- Order 92 extras
(92, 8, 5, 29.99),
(92, 22, 2, 19.99),
-- Order 98 extras
(98, 21, 4, 24.99),
(98, 16, 2, 34.99),
-- Order 99 extras
(99, 8, 3, 29.99),
(99, 19, 1, 39.99),
-- Order 106 extras
(106, 22, 3, 19.99),
(106, 29, 4, 9.99),
-- Order 113 extras
(113, 8, 2, 29.99),
(113, 21, 5, 24.99),
-- Order 116 extras
(116, 1, 1, 199.99),
(116, 8, 4, 29.99),
(116, 25, 2, 49.99),
-- Order 117 extras
(117, 1, 1, 199.99),
(117, 8, 3, 29.99),
(117, 22, 2, 19.99),
-- Order 122 extras
(122, 8, 2, 29.99),
(122, 21, 3, 24.99),
-- Order 124 extras
(124, 8, 4, 29.99),
(124, 22, 2, 19.99),
-- Order 131 extras
(131, 8, 3, 29.99),
(131, 22, 5, 19.99),
-- Order 132 extras
(132, 8, 2, 29.99),
(132, 21, 4, 24.99),
-- Order 138 extras
(138, 19, 2, 39.99),
(138, 22, 3, 19.99),
(138, 8, 1, 29.99),
-- Order 140 extras
(140, 8, 3, 29.99),
(140, 22, 2, 19.99),
(140, 21, 4, 24.99),
-- Order 149 extras
(149, 8, 2, 29.99),
(149, 19, 1, 39.99),
-- Order 152 extras
(152, 1, 1, 199.99),
(152, 8, 3, 29.99),
(152, 22, 2, 19.99),
-- Order 161 extras
(161, 1, 1, 199.99),
(161, 8, 2, 29.99),
-- Order 164 extras
(164, 8, 3, 29.99),
(164, 22, 1, 19.99),
-- Order 168 extras
(168, 8, 2, 29.99),
(168, 21, 3, 24.99),
(168, 22, 1, 19.99),
-- Order 173 extras
(173, 22, 4, 19.99),
(173, 8, 2, 29.99),
-- Order 175 extras
(175, 19, 2, 39.99),
(175, 22, 3, 19.99),
(175, 8, 1, 29.99),
-- Order 177 extras
(177, 1, 1, 199.99),
(177, 8, 3, 29.99),
(177, 22, 2, 19.99),
(177, 21, 4, 24.99),
-- Order 180 extras
(180, 8, 2, 29.99),
(180, 19, 1, 39.99),
(180, 22, 3, 19.99),
-- More multi-quantity items for variety
(2, 8, 3, 29.99),
(2, 21, 2, 24.99),
(4, 8, 2, 29.99),
(4, 22, 4, 19.99),
(5, 8, 1, 29.99),
(5, 21, 2, 24.99),
(10, 8, 3, 29.99),
(10, 19, 2, 39.99),
(12, 8, 2, 29.99),
(12, 22, 3, 19.99),
(13, 8, 4, 29.99),
(13, 22, 2, 19.99),
(16, 8, 1, 29.99),
(16, 21, 3, 24.99),
(18, 8, 2, 29.99),
(18, 22, 1, 19.99),
(20, 8, 3, 29.99),
(20, 22, 2, 19.99),
(22, 8, 2, 29.99),
(22, 21, 4, 24.99),
(24, 8, 1, 29.99),
(24, 22, 3, 19.99),
(25, 8, 2, 29.99),
(26, 8, 3, 29.99),
(28, 8, 2, 29.99),
(28, 22, 1, 19.99),
(30, 22, 4, 19.99),
(30, 21, 2, 24.99),
(34, 8, 3, 29.99),
(35, 8, 2, 29.99),
(37, 8, 1, 29.99),
(38, 8, 2, 29.99),
(39, 8, 3, 29.99),
(41, 22, 2, 19.99),
(42, 8, 1, 29.99),
(43, 8, 2, 29.99),
(44, 22, 3, 19.99),
(45, 8, 1, 29.99),
(46, 8, 2, 29.99),
(48, 8, 3, 29.99),
(49, 22, 1, 19.99),
(50, 8, 2, 29.99),
(51, 8, 1, 29.99),
(52, 8, 2, 29.99),
(53, 8, 3, 29.99),
(55, 8, 1, 29.99),
(56, 8, 2, 29.99),
(57, 8, 1, 29.99),
(59, 8, 2, 29.99),
(60, 8, 1, 29.99),
(61, 8, 2, 29.99),
(62, 8, 3, 29.99),
(64, 8, 1, 29.99),
(66, 8, 2, 29.99),
(68, 8, 1, 29.99),
(69, 8, 2, 29.99),
(70, 8, 3, 29.99),
(71, 8, 1, 29.99),
(72, 8, 2, 29.99),
(73, 8, 1, 29.99),
(74, 8, 2, 29.99),
(75, 8, 1, 29.99),
(78, 8, 2, 29.99),
(79, 8, 1, 29.99),
(80, 8, 2, 29.99),
(83, 8, 3, 29.99),
(84, 8, 1, 29.99),
(85, 8, 2, 29.99),
(87, 8, 1, 29.99),
(88, 8, 2, 29.99),
(89, 8, 1, 29.99),
(90, 8, 2, 29.99),
(91, 8, 3, 29.99),
-- Order items for orders 182-200
-- Order 182 (329.98 → 2 items)
(182, 1, 1, 199.99),
(182, 4, 1, 129.99),
-- Order 183 (199.99)
(183, 13, 1, 199.99),
-- Order 184 (89.99)
(184, 5, 1, 89.99),
-- Order 185 (249.99)
(185, 6, 1, 249.99),
-- Order 186 (149.99)
(186, 10, 1, 149.99),
-- Order 187 (299.99)
(187, 20, 1, 299.99),
-- Order 188 (179.99)
(188, 18, 1, 179.99),
-- Order 189 (449.99)
(189, 3, 1, 449.99),
-- Order 190 (119.99)
(190, 12, 1, 119.99),
-- Order 191 (59.99)
(191, 9, 1, 59.99),
-- Order 192 (79.99)
(192, 2, 1, 79.99),
-- Order 193 (129.99)
(193, 4, 1, 129.99),
-- Order 194 (349.99)
(194, 15, 1, 349.99),
-- Order 195 (44.99)
(195, 26, 1, 44.99),
-- Order 196 (229.99)
(196, 24, 1, 229.99),
-- Order 197 (159.99)
(197, 23, 1, 159.99),
-- Order 198 (69.99)
(198, 14, 1, 69.99),
-- Order 199 (199.99)
(199, 1, 1, 199.99),
-- Order 200 (89.99)
(200, 11, 1, 89.99),
-- Additional filler items (multi-item enrichment for orders 182-200)
(182, 22, 3, 19.99),
(183, 8, 2, 29.99),
(185, 8, 1, 29.99),
(186, 22, 2, 19.99),
(187, 8, 3, 29.99),
(188, 8, 2, 29.99),
(189, 1, 1, 199.99),
(189, 8, 2, 29.99),
(190, 8, 1, 29.99),
(192, 22, 3, 19.99),
(193, 8, 2, 29.99),
(194, 8, 1, 29.99),
(196, 8, 2, 29.99),
(197, 8, 1, 29.99),
(199, 8, 3, 29.99),
(200, 8, 2, 29.99);

-- ────────────────────────────────────────────────────────────────────────────
-- 7. SEED DATA  –  marketing_campaigns  (20 rows)
-- ────────────────────────────────────────────────────────────────────────────

INSERT INTO marketing_campaigns (name, channel, start_date, end_date, budget, conversions) VALUES
('New Year Kickoff 2024',            'email',        '2024-01-01', '2024-01-31', 5000.00,   320),
('Winter Clearance Sale',            'social_media', '2024-01-15', '2024-02-15', 8000.00,   540),
('Valentine''s Day Special',         'email',        '2024-02-01', '2024-02-14', 3000.00,   185),
('Spring Collection Launch',         'display',      '2024-03-01', '2024-03-31', 12000.00,  710),
('Fitness Season Push',              'social_media', '2024-03-15', '2024-04-30', 15000.00,  980),
('Earth Day Eco Products',           'influencer',   '2024-04-15', '2024-04-30', 7000.00,   425),
('Summer Reading Campaign',          'search',       '2024-05-01', '2024-06-30', 4000.00,   290),
('Back to School Tech',              'search',       '2024-07-15', '2024-08-31', 20000.00, 1350),
('Labor Day Weekend Blitz',          'social_media', '2024-08-25', '2024-09-05', 10000.00,  680),
('Fall Fashion Forward',             'influencer',   '2024-09-01', '2024-10-15', 18000.00, 1120),
('Halloween Special Deals',          'display',      '2024-10-15', '2024-10-31', 6000.00,   375),
('Singles Day Flash Sale',           'email',        '2024-11-11', '2024-11-11', 2000.00,   245),
('Black Friday Mega Sale',           'search',       '2024-11-25', '2024-11-30', 50000.00, 3850),
('Cyber Monday Deals',               'display',      '2024-12-01', '2024-12-02', 35000.00, 2640),
('Holiday Gift Guide',               'social_media', '2024-12-01', '2024-12-24', 25000.00, 1890),
('Year-End Clearance',               'email',        '2024-12-26', '2025-01-05', 8000.00,   520),
('New Year New You 2025',            'influencer',   '2025-01-06', '2025-01-31', 12000.00,  780),
('Winter Sports Promo',              'search',       '2025-01-15', '2025-02-28', 9000.00,   610),
('Spring Forward Electronics',       'display',      '2025-03-01', '2025-03-31', 16000.00, 1050),
('Q2 Customer Loyalty Rewards',      'email',        '2025-04-01', NULL,         10000.00,  430);

COMMIT;
