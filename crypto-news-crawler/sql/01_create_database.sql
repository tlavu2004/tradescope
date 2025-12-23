-- 01_create_database.sql
-- Create database CryptoNews if not exists

USE master;
GO

IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'CryptoNews')
BEGIN
    CREATE DATABASE CryptoNews;
END
GO

USE CryptoNews;
GO

PRINT 'Database CryptoNews initialized';
