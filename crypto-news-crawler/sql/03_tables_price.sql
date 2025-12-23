-- 03_tables_price.sql
-- Tables for price/market data (Part 2)

USE CryptoNews;
GO

-- Table: Symbols (crypto symbols: BTC, ETH, ...)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Symbols')
BEGIN
    CREATE TABLE Symbols (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        Symbol NVARCHAR(20) UNIQUE NOT NULL,  -- BTC, ETH, DOGE, ...
        Name NVARCHAR(100),                     -- Bitcoin, Ethereum, ...
        Exchange NVARCHAR(50) DEFAULT 'binance',
        IsActive BIT DEFAULT 1,
        CreatedAt DATETIME DEFAULT GETUTCDATE()
    );
    PRINT 'Table Symbols created';
END
GO

-- Table: Candles (OHLCV data)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Candles')
BEGIN
    CREATE TABLE Candles (
        Id BIGINT IDENTITY(1,1) PRIMARY KEY,
        SymbolId INT NOT NULL,
        OpenTime DATETIME NOT NULL,
        CloseTime DATETIME NOT NULL,
        OpenPrice FLOAT NOT NULL,
        HighPrice FLOAT NOT NULL,
        LowPrice FLOAT NOT NULL,
        ClosePrice FLOAT NOT NULL,
        Volume FLOAT NOT NULL,
        QuoteAssetVolume FLOAT,
        TimeFrame NVARCHAR(10) DEFAULT '1h',  -- 1m, 5m, 1h, 1d, ...
        CreatedAt DATETIME DEFAULT GETUTCDATE(),
        FOREIGN KEY (SymbolId) REFERENCES Symbols(Id),
        CONSTRAINT uq_candle UNIQUE (SymbolId, OpenTime, TimeFrame)
    );
    PRINT 'Table Candles created';
END
GO

-- Indexes for price queries
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_candles_symbol_time' AND object_id = OBJECT_ID('Candles'))
BEGIN
    CREATE INDEX idx_candles_symbol_time ON Candles(SymbolId, OpenTime DESC);
END
GO

PRINT 'Price tables initialized';
