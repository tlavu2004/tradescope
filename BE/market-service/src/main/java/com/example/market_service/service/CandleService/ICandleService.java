package com.example.market_service.service.CandleService;

import com.example.market_service.dto.request.CandleCreationRequest;
import com.example.market_service.dto.response.CandleResponse;
import com.example.market_service.entity.Candle;

import java.util.List;

public interface ICandleService {
	public Long getLastOpenTime(String symbol, String interval);
	public CandleResponse createCandle(CandleCreationRequest request);
	public List<Candle> getRecentCandles(
			String symbol,
			String interval,
			boolean isVip
	);
	public List<Candle> getRecentCandlesFromDb(
			String symbol,
			String interval,
			int limit
	);
	public List<Candle> getCandlesBeforeOpenTime(
			String symbol,
			String interval,
			long openTime
	);
	public List<Candle> batchInsertIdempotent (List<Candle> candles);
	public List<Candle> getCandlesBetweenOpenTimes(String symbol, String interval, long startTime, long endTime);
	public List<Candle> getLatestPrice(String interval);
}
