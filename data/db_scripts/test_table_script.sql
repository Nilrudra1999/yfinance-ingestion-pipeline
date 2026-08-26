/*----------------------------------------------------------------------------------
  DATABASE TABLES TESTING T-SQL SCRIPT
  Database: Financial Market Data
  Contains a series of SQL queries designed to test the etl pipeline runs during
  the development phase, all testing records (records inserted during testing)
  will be erased from the database before launch.
----------------------------------------------------------------------------------*/
USE financial_market_data;
GO


-- SECTION 1: VERIFY LOADED DATA
------------------------------------------------------------------------------------
SELECT tickerID, symbol, asset_name, sector
FROM assets;


SELECT priceID, tickerID, lookup_date, high_price, low_price, close_price
FROM price_metrics
ORDER BY tickerID, lookup_date;


SELECT priceID, tickerID, pe_ratio, eps, ytd_return, dividend
FROM fundamental_metrics
ORDER BY priceID;


SELECT a.tickerID, a.symbol, a.asset_name,
	   pm.priceID, pm.lookup_date, pm.high_price, pm.low_price, pm.close_price,
	   fm.pe_ratio, fm.eps, fm.ytd_return, fm.dividend
FROM assets a
INNER JOIN price_metrics pm
	ON a.tickerID = pm.tickerID
LEFT JOIN fundamental_metrics fm 
    ON pm.priceID = fm.priceID AND pm.tickerID = fm.tickerID
ORDER BY a.symbol, pm.lookup_date;
GO



-- SECTION 2: CLEANUP TEST DATA (UNCOMMENT BELOW TO EXECUTE RESET)
------------------------------------------------------------------------------------
BEGIN TRANSACTION;

BEGIN TRY
    DELETE FROM fundamental_metrics;
    DELETE FROM price_metrics;
    DELETE FROM assets;
    DBCC CHECKIDENT ('assets', RESEED, 0);
    DBCC CHECKIDENT ('price_metrics', RESEED, 0);
    COMMIT TRANSACTION;
    PRINT 'SUCCESS: All test data has been cleared and identity seeds reset to 0.';
END TRY
BEGIN CATCH
    ROLLBACK TRANSACTION;
    PRINT 'ERROR: Failed to clean test data. Transaction rolled back.';
    THROW;
END CATCH;

