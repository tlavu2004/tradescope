-- 02_tables_core.sql
-- Core tables: News, NewsSources

USE CryptoNews;
GO

-- Table: NewsSources (manage crawler sources)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'NewsSources')
BEGIN
    CREATE TABLE NewsSources (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        Name NVARCHAR(100) NOT NULL UNIQUE,
        BaseUrl NVARCHAR(255) NOT NULL,
        ListUrl NVARCHAR(255),
        Enabled BIT DEFAULT 1,
        Config NVARCHAR(MAX),  -- JSON template: selectors, heuristics
        CreatedAt DATETIME DEFAULT GETUTCDATE(),
        UpdatedAt DATETIME DEFAULT GETUTCDATE()
    );
    PRINT 'Table NewsSources created';
END
GO

-- Table: News (collected articles)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'News')
BEGIN
    CREATE TABLE News (
        Id NVARCHAR(36) PRIMARY KEY,
        Source NVARCHAR(100),
        Url NVARCHAR(1024) UNIQUE NOT NULL,
        Title NVARCHAR(MAX),
        Summary NVARCHAR(MAX),
        Content NVARCHAR(MAX),
        PublishedAt DATETIME,
        CollectedAt DATETIME DEFAULT GETUTCDATE(),
        Language NVARCHAR(10),
        Author NVARCHAR(255),
        SentimentScore FLOAT,
        SentimentLabel NVARCHAR(20),
        FOREIGN KEY (Source) REFERENCES NewsSources(Name)
    );
    PRINT 'Table News created';
END
GO

-- Indexes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_news_source' AND object_id = OBJECT_ID('News'))
BEGIN
    CREATE INDEX idx_news_source ON News(Source);
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_news_published' AND object_id = OBJECT_ID('News'))
BEGIN
    CREATE INDEX idx_news_published ON News(PublishedAt DESC);
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_news_collected' AND object_id = OBJECT_ID('News'))
BEGIN
    CREATE INDEX idx_news_collected ON News(CollectedAt DESC);
END
GO

PRINT 'Core tables initialized';
