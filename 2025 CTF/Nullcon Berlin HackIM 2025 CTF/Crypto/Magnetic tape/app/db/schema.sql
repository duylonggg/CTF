CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS models (
  id TEXT PRIMARY KEY,
  brand TEXT,
  model_name TEXT,
  model_number TEXT,
  capacity INTEGER
);

CREATE TABLE IF NOT EXISTS tapes (
  id TEXT PRIMARY KEY,
  model_id TEXT,
  serial_number TEXT,
  status TEXT,
  location TEXT,
  FOREIGN KEY(model_id) REFERENCES models(id)
);

