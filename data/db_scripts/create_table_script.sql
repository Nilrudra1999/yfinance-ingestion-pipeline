/*----------------------------------------------------------------------------------
  CREATE TABLES T-SQL SCRIPT
  Database: Financial Market Data
  Contains a collection of stock, fund, and etf data collected over a large time 
  period. Can be used for ML model training or economic/financial market studies.
----------------------------------------------------------------------------------*/
USE financial_market_data;
GO


-- drop table guard if the tables already exist
-- (used during schema testing)
DROP TABLE IF EXISTS fundamental_metrics;
DROP TABLE IF EXISTS price_metrics;
DROP TABLE IF EXISTS assets;
GO


-- 1. Create Assets Table
CREATE TABLE assets (
    tickerID    INT IDENTITY(1, 1) NOT NULL,
    symbol      VARCHAR(10)        NOT NULL,
    asset_name  VARCHAR(50)        NULL,
    sector      VARCHAR(50)        NULL,
    CONSTRAINT UQ_asset_symbols
        UNIQUE (symbol),
    CONSTRAINT PK_asset_table
        PRIMARY KEY (tickerID)
);


-- 2. Create Price Metrics Table
CREATE TABLE price_metrics (
    priceID         INT IDENTITY(1, 1) NOT NULL,
    tickerID        INT                NOT NULL,
    lookup_date     DATE               NOT NULL,
    high_price      DECIMAL(18, 4)     NULL,
    low_price       DECIMAL(18, 4)     NULL,
    close_price     DECIMAL(18, 4)     NULL,
    CONSTRAINT UQ_ticker_lookup_date    
        UNIQUE (tickerID, lookup_date),
    CONSTRAINT PK_price_table
        PRIMARY KEY (priceID),
    CONSTRAINT FK_price_ticker
        FOREIGN KEY (tickerID)
        REFERENCES assets (tickerID)
        ON DELETE CASCADE
);


-- 3. Create Fundamental Metrics Table
CREATE TABLE fundamental_metrics (
    tickerID        INT            NOT NULL,
    priceID         INT            NOT NULL,
    pe_ratio        DECIMAL(18, 4) NULL,
    eps             DECIMAL(18, 4) NULL,
    ytd_return      DECIMAL(18, 4) NULL,
    dividend        DECIMAL(18, 4) NULL,
    CONSTRAINT PK_fundamental_table 
        PRIMARY KEY (priceID),
    CONSTRAINT FK_fundamental_Price
        FOREIGN KEY (priceID) 
        REFERENCES price_metrics (priceID)
        ON DELETE CASCADE,
    CONSTRAINT FK_fundamental_ticker
        FOREIGN KEY (tickerID) 
        REFERENCES assets (tickerID)
);


-- Indexes to improve ETL lookup performance
CREATE INDEX IX_price_tickerID
ON price_metrics(tickerID);

CREATE INDEX IX_fundamental_tickerID
ON fundamental_metrics(tickerID);
