package com.example.market_service.controller;

import com.example.market_service.dto.request.CandleCreationRequest;
import com.example.market_service.dto.response.ApiResponse;
import com.example.market_service.dto.response.CandleResponse;
import com.example.market_service.entity.Candle;
import com.example.market_service.service.CandleService;
import com.example.market_service.service.SecurityUtils;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.bind.annotation.CrossOrigin;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/candles")
@Slf4j
public class CandleController {
	private final CandleService candleService;
	private final SecurityUtils securityUtils;
	@PostMapping
	public ApiResponse<CandleResponse> createCandle(@RequestBody CandleCreationRequest request) {
		log.info("Received request to create candle: {}", request);
		CandleResponse candleResponse = candleService.createCandle(request);
		return ApiResponse.<CandleResponse>builder()
				.data(candleResponse)
				.message("Candle created successfully")
				.build();
	}

	@GetMapping("/last-open-time")
	public ApiResponse<Long> getLastOpenTime(
			@RequestParam("symbol") String symbol,
			@RequestParam("interval") String interval) {
		Long lastOpenTime = candleService.getLastOpenTime(symbol, interval);
		return ApiResponse.<Long>builder()
				.data(lastOpenTime)
				.message("Last open time retrieved successfully")
				.build();
	}
	@GetMapping("/recent")
	public ApiResponse<List<Candle>> getRecentCandles(
			@RequestParam("symbol") String symbol,
			@RequestParam("interval") String interval
	) {
		boolean isVip = securityUtils.hasRole("VIP");
		List<Candle> candles =
				candleService.getRecentCandles(symbol, interval, isVip);

		return ApiResponse.<List<Candle>>builder()
				.data(candles)
				.message("Fetched recent candles successfully")
				.build();
	}
}
