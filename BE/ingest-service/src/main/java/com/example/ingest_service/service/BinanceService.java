package com.example.ingest_service.service;

import com.example.ingest_service.dto.Candle;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.ObjectMapper;

import java.math.BigDecimal;
import java.net.URI;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class BinanceService {
	private final RedisService redisService;
	private final ObjectMapper objectMapper = new ObjectMapper();

	@Value("${binance.ws.base-url}")
	private String baseUrl;

	private final List<String> symbols = List.of(
			"BTCUSDT",
			"ETHUSDT",
			"BNBUSDT",
			"XRPUSDT",
			"ADAUSDT"
	);

	private final List<String> intervals = List.of(
			"1m",
			"5m",
			"15m",
			"1h",
			"4h",
			"1d"
	);
	private String buildStreamUrl() {
		List<String> streams = new ArrayList<>();

		for (String s : symbols) {
			for (String i : intervals) {
				streams.add(s.toLowerCase() + "@kline_" + i);
			}
		}

		return baseUrl + "?streams=" + String.join("/", streams);
	}
	@PostConstruct
	public void startBinanceWebSocket() {
		String url = buildStreamUrl();
		WebSocketClient client = createClient(url);
		client.connect();
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
					log.info("Received message: {}", message);
					JsonNode node = objectMapper.readTree(message);
					JsonNode data = node.get("data");

					if (data != null) {
						String stream = node.get("stream").asText();
						String[] streamParts = stream.split("@");
						String symbol = streamParts[0].toUpperCase();
						String interval = streamParts[1].substring(6); // Removes "kline_"
						Candle candle = parseCandle(data, symbol, interval);

						String key = String.format("candle:%s:%s", symbol, interval);
						String candleJson = objectMapper.writeValueAsString(candle);
						log.info("Publishing to key: {}, candle: {}", key, candleJson);
						redisService.publishCandle(key, candleJson);

						log.debug("Candle saved: {} - {}", symbol, candle.getOpenTime());
					}
				} catch (Exception e) {
					log.error("Error processing message", e);
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
		JsonNode k = node.path("k"); // safe
		if(k.isMissingNode()) return null; // skip nếu k không tồn tại

		return Candle.builder()
				.symbol(symbol)
				.interval(interval)
				.openTime(Instant.ofEpochMilli(k.path("t").asLong(0)))
				.closeTime(Instant.ofEpochMilli(k.path("T").asLong(0)))
				.open(new BigDecimal(k.path("o").asText("0")))
				.high(new BigDecimal(k.path("h").asText("0")))
				.low(new BigDecimal(k.path("l").asText("0")))
				.close(new BigDecimal(k.path("c").asText("0")))
				.volume(new BigDecimal(k.path("v").asText("0")))
				.isClosed(k.path("x").asBoolean(false))
				.build();
	}

}
