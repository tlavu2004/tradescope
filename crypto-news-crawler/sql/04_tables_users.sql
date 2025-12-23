-- 04_tables_users.sql
-- Tables for users, roles, preferences (Part 2/3)

USE CryptoNews;
GO

-- Table: Roles
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Roles')
BEGIN
    CREATE TABLE Roles (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        Name NVARCHAR(50) UNIQUE NOT NULL,  -- admin, user, analyst
        Description NVARCHAR(255),
        CreatedAt DATETIME DEFAULT GETUTCDATE()
    );
    PRINT 'Table Roles created';
END
GO

-- Table: Users
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Users')
BEGIN
    CREATE TABLE Users (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        Username NVARCHAR(100) UNIQUE NOT NULL,
        Email NVARCHAR(255) UNIQUE NOT NULL,
        PasswordHash NVARCHAR(255),
        RoleId INT DEFAULT 1,
        IsActive BIT DEFAULT 1,
        CreatedAt DATETIME DEFAULT GETUTCDATE(),
        UpdatedAt DATETIME DEFAULT GETUTCDATE(),
        FOREIGN KEY (RoleId) REFERENCES Roles(Id)
    );
    PRINT 'Table Users created';
END
GO

-- Table: UserPreferences (e.g., watched symbols, settings)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'UserPreferences')
BEGIN
    CREATE TABLE UserPreferences (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        UserId INT NOT NULL,
        WatchedSymbols NVARCHAR(MAX),  -- JSON array: ["BTC", "ETH", ...]
        NewsLanguage NVARCHAR(10) DEFAULT 'en',
        AlertThreshold FLOAT,
        UpdatedAt DATETIME DEFAULT GETUTCDATE(),
        FOREIGN KEY (UserId) REFERENCES Users(Id) ON DELETE CASCADE
    );
    PRINT 'Table UserPreferences created';
END
GO

-- Insert default roles
IF NOT EXISTS (SELECT * FROM Roles WHERE Name = 'admin')
BEGIN
    INSERT INTO Roles (Name, Description) VALUES ('admin', 'Administrator');
    INSERT INTO Roles (Name, Description) VALUES ('user', 'Regular User');
    PRINT 'Default roles inserted';
END
GO

PRINT 'User tables initialized';
