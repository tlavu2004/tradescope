package com.example.ingest_service.service;

import com.example.ingest_service. configure.StorageServiceWebClient;
import com.example.ingest_service.configure.TradeProperties;
import com.example.ingest_service. dto.request. Candle;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;
import org. springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind. ObjectMapper;

import java.math.BigDecimal;
import java.net.URI;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.CompletableFuture;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class BinanceService {
	private final RedisService redisService;
	private final CandleKafkaProducer kafkaService;
	private final ObjectMapper objectMapper = new ObjectMapper();
	private final BinanceRestService binanceRestService;
	private final StorageServiceWebClient storageServiceClient;
	private final TradeProperties tradeProperties;

	@Value("${binance.ws.base-url}")
	private String baseUrl;

	private String buildStreamUrl() {
		List<String> streams = new ArrayList<>();

		for (String s : tradeProperties.getSymbols()) {
			for (String i : tradeProperties.getIntervals()) {
				streams.add(s. toLowerCase() + "@kline_" + i);
			}
		}

		return baseUrl + "?streams=" + String.join("/", streams);
	}

	@PostConstruct
	public void startBinanceWebSocket() {
		backfillOnStart();
		String url = buildStreamUrl();
		WebSocketClient client = createClient(url);
		client.connect();
		log.info("WebSocket connecting to {}", url);

	}

	private void backfillOnStart() {
		for (String symbol : tradeProperties.getSymbols()) {
			for (String interval : tradeProperties.getIntervals()) {
				try {
					backfillSymbolInterval(symbol, interval);
				} catch (Exception e) {
					log.error("Lỗi khi backfill {} {}: {}",
							symbol, interval, e.getMessage(), e);
				}
			}
		}
	}

	private void backfillSymbolInterval(String symbol, String interval) throws Exception {
		Optional<Long> lastOpenTimeOpt = storageServiceClient.getLastOpenTime(symbol, interval);
		long intervalMs = intervalToMillis(interval);
		long now = System.currentTimeMillis();
		long nowOpenTime = alignToInterval(now, intervalMs);

		List<Candle> candlesToBackfill;

		if (lastOpenTimeOpt.isEmpty()) {

			candlesToBackfill = binanceRestService.fetchLastClosedCandles(
					symbol, interval, 1000
			);
			log.info("[Backfill] {} {} lần đầu, lấy được {} nến",
					symbol, interval, candlesToBackfill.size());
		} else {
			long lastOpenTime = lastOpenTimeOpt.get();
			long missingCount = (nowOpenTime - lastOpenTime) / intervalMs;

			log.info("[Backfill] {} {}: lastOpenTime={}, nowOpenTime={}, thiếu={}",
					symbol, interval, lastOpenTime, nowOpenTime, missingCount);

			if (missingCount <= 0) {
				log.info("[Backfill] {} {}: không thiếu nến nào", symbol, interval);
				return;
			}

			int limit = (int) Math.min(missingCount, 1000);
			long startTime = nowOpenTime - (limit * intervalMs);

			if (missingCount > 1000) {
				log.warn("[Backfill] {} {}: thiếu {} nến, chỉ lấy {} nến gần nhất",
						symbol, interval, missingCount, limit);
			}

			candlesToBackfill = binanceRestService.fetchClosedCandlesAfter(
					symbol, interval, startTime, limit
			);
			log.info("[Backfill] {} {}: lấy được {} nến",
					symbol, interval, candlesToBackfill.size());
		}

		publishCandles(symbol, interval, candlesToBackfill);
	}

	private void publishCandles(String symbol, String interval, List<Candle> candles)
			throws Exception {
		if (candles.isEmpty()) {
			return;
		}

		for (Candle candle : candles) {
			String candleJson = objectMapper.writeValueAsString(candle);
			kafkaService.publishClosedCandle(symbol, interval, candleJson);
		}

		log.info("[Backfill] Đã publish {} nến lên Kafka: {} {}",
				candles.size(), symbol, interval);
	}

	private WebSocketClient createClient(String url) {
		return new WebSocketClient(URI.create(url)) {

			@Override
			public void onOpen(ServerHandshake serverHandshake) {
				log.info("WebSocket connected to {}", url);
			}

			@Override
			public void onMessage(String message) {
				try {
					JsonNode node = objectMapper.readTree(message);
					JsonNode data = node.get("data");

					if (data != null) {
						String stream = node.get("stream").asText();
						String[] streamParts = stream.split("@");
						String symbol = streamParts[0].toUpperCase();
						String interval = streamParts[1]. substring(6);
						Candle candle = parseCandle(data, symbol, interval);

						if (candle != null) {
							String candleJson = objectMapper.writeValueAsString(candle);

							redisService.publishRealtimeCandle(symbol, interval, candleJson);

							if (Boolean.TRUE.equals(candle.getIsClosed())) {
								kafkaService.publishClosedCandle(symbol, interval, candleJson);
								log.debug("Published closed candle to Kafka: {} {} at {}",
										symbol, interval, candle.getOpenTime());
							}
						}
					}
				} catch (Exception e) {
					log. error("Error processing message", e);
				}
			}

			@Override
			public void onClose(int code, String reason, boolean remote) {
				log.info("WebSocket disconnected: code = {}, reason = {}, remote = {}", code, reason, remote);
			}

			@Override
			public void onError(Exception e) {
				log.error("WebSocket error", e);
			}
		};
	}

	private Candle parseCandle(JsonNode node, String symbol, String interval) {
		JsonNode k = node.path("k");
		if (k.isMissingNode()) return null;
		return Candle.builder()
				.symbol(symbol)
				.interval(interval)
				.openTime((k.path("t").asLong(0)))
				.closeTime((k.path("T").asLong(0)))
				.open(new BigDecimal(k.path("o").asText("0")))
				.high(new BigDecimal(k.path("h").asText("0")))
				.low(new BigDecimal(k.path("l").asText("0")))
				.close(new BigDecimal(k.path("c").asText("0")))
				.volume(new BigDecimal(k.path("v").asText("0")))
				.isClosed(k.path("x").asBoolean(false))
				.build();
	}

	private long intervalToMillis(String interval) {
		return switch (interval) {
			case "1m" -> 60_000L;
			case "2m" -> 2 * 60_000L;
			case "5m" -> 5 * 60_000L;
			case "15m" -> 15 * 60_000L;
			case "1h" -> 60 * 60_000L;
			case "4h" -> 4 * 60 * 60_000L;
			case "1d" -> 24 * 60 * 60_000L;
			default -> throw new IllegalArgumentException("Unsupported interval " + interval);
		};
	}

	private long alignToInterval(long ts, long intervalMs) {
		return ts - (ts % intervalMs);
	}
}