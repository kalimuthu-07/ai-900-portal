-- Run this SQL in your Supabase SQL Editor

-- Users table
CREATE TABLE users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password TEXT NOT NULL,
  role VARCHAR(10) CHECK (role IN ('staff', 'student')) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Marks table
CREATE TABLE marks (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  student_id UUID REFERENCES users(id) ON DELETE CASCADE,
  topic VARCHAR(200) NOT NULL,
  score FLOAT NOT NULL,
  date DATE NOT NULL,
  uploaded_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Optional: Indexes for faster queries
CREATE INDEX idx_marks_student ON marks(student_id);
CREATE INDEX idx_marks_score ON marks(score DESC);
