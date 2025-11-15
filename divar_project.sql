-- ========================================
-- 1) Price per meter standardization
-- ========================================

-- Preview current values in original table
SELECT price_per_meter
FROM divar_db
ORDER BY price_per_meter DESC;

-- Create a staging table (clean copy of raw data)
CREATE TABLE divar_db_staging LIKE divar_db;

-- Copy all data into staging table
INSERT INTO divar_db_staging
SELECT *
FROM divar_db;

-- Fix invalid entries (non-numeric placeholder)
UPDATE divar_db_staging
SET price_per_meter = '0'
WHERE price_per_meter = 'wyly';

-- Remove commas so MySQL can cast to DOUBLE
UPDATE divar_db_staging
SET price_per_meter = REPLACE(price_per_meter, ',', '');

-- Change column type to DOUBLE
ALTER TABLE divar_db_staging
MODIFY COLUMN price_per_meter DOUBLE;

-- Final check
SELECT price_per_meter
FROM divar_db_staging
WHERE price_per_meter
ORDER BY 1 DESC;

-- ========================================
-- 2) Total price standardization
-- ========================================

-- Preview current values
SELECT total_price
FROM divar_db_staging
ORDER BY total_price DESC;

-- Remove commas
UPDATE divar_db_staging
SET total_price = REPLACE(total_price, ',', '');

-- Change column type to DOUBLE
ALTER TABLE divar_db_staging
MODIFY COLUMN total_price DOUBLE;

-- Final check
SELECT total_price
FROM divar_db_staging
WHERE total_price
ORDER BY 1 DESC;


-- ========================================
-- 3) Remove invalid rows
-- ========================================

-- Count how many rows have latitude = 0
SELECT COUNT(*) AS number_of_zero_latitudes
FROM divar_db_staging
WHERE latitude = 0;

-- Remove listings with unrealistic prices
DELETE 
FROM divar_db_staging
WHERE total_price < 1000000000;     -- total price too low

DELETE 
FROM divar_db_staging
WHERE price_per_meter > 150000000;  -- price per meter too high

-- Quick preview after cleanup
SELECT *
FROM divar_db_staging;


-- ========================================
-- 4) Data Cleaning Steps
-- ========================================

-- 1. Detect duplicates using ROW_NUMBER()
SELECT *,
       ROW_NUMBER() OVER (
            PARTITION BY latitude, longitude, title, house_size, manufacture_year,
                         rooms, total_price, price_per_meter, token
       ) AS row_num
FROM divar_db_staging;

-- Use a CTE for readability
WITH duplicate_detector AS (
    SELECT *,
           ROW_NUMBER() OVER (
                PARTITION BY latitude, longitude, title, house_size, manufacture_year,
                             rooms, total_price, price_per_meter, token
           ) AS row_num
    FROM divar_db_staging
)
SELECT *
FROM duplicate_detector
WHERE row_num > 1;   -- Shows duplicates only


-- 2. Detect zero or null values in coordinates
SELECT COUNT(*) AS bad_longitudes
FROM divar_db_staging
WHERE longitude = 0 AND latitude != 0;

SELECT COUNT(*) AS bad_latitudes
FROM divar_db_staging
WHERE latitude = 0 AND longitude != 0;

SELECT COUNT(*) AS total_zero_latitudes
FROM divar_db_staging
WHERE latitude = 0;

-- drop rows with latitude(longitude will be droped with it) = 0 (e.g. 237 of 1783 rows)
DELETE 
FROM divar_db_staging
WHERE latitude = 0;

-- Confirm deletion
SELECT COUNT(*) AS total_zero_latitudes
FROM divar_db_staging
WHERE latitude = 0;


-- 3. Drop unnecessary columns (title, token)
ALTER TABLE divar_db_staging DROP COLUMN title;
ALTER TABLE divar_db_staging DROP COLUMN token;


-- ========================================
-- 5) Final dataset size
-- ========================================

SELECT COUNT(*) AS size_of_dataset
FROM divar_db_staging;
