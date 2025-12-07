-- Migration: Add calibration support to simulations table
-- Run this in the Supabase SQL Editor

-- Add calibration state columns
ALTER TABLE simulations 
ADD COLUMN IF NOT EXISTS is_calibrated boolean DEFAULT false,
ADD COLUMN IF NOT EXISTS calibration_step int DEFAULT 0,
ADD COLUMN IF NOT EXISTS user_profile jsonb DEFAULT '{}',
ADD COLUMN IF NOT EXISTS opening_scenario text;

-- Verify the changes
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'simulations';
