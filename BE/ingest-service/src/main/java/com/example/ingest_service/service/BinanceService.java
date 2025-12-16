package com.example.ingest_service.service;

import com.example.ingest_service.dto.Candle;
import com.fasterxml.jackson.core.JsonProcessingException;
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

@Service
@RequiredArgsConstructor
@Slf4j
public class BinanceService {
	private final RedisService redisService;
	private final ObjectMapper objectMapper = new ObjectMapper();

	@Value("${binance.ws.base-url}")
	private String baseUrl;

	@Value("${binance.ws.symbols}")
	private String symbols;

	@Value("${binance.ws.intervals}")
	private String intervals;
	@PostConstruct
	private void startBinanceWebSocket(){

		String url = baseUrl + "/" + symbols.toLowerCase() + "@kline_" + intervals;
		WebSocketClient client = createClient(url, symbols, intervals);
		client.connect();

	}
	private WebSocketClient createClient(String url, String symbol, String interval) {
		return new WebSocketClient(URI.create(url)) {


			@Override
			public void onOpen(ServerHandshake serverHandshake) {
				log.info("WebSocket connected: {} - {}", symbol, interval);
			}

			@Override
			public void onMessage(String message) {
				try {
					Candle candle = parseCandle(message, symbol, interval);
					String key = String.format("candle:%s:%s", symbol, interval);
					String candleJson = objectMapper.writeValueAsString(candle);
					redisService.publishCandle(key,candleJson);
					log.debug("Candle saved: {} at {}", symbol, candle.getOpenTime());
					log.info("message:{}",candleJson);
				} catch (JsonProcessingException e) {
					log.error("Error parsing candle data: {}", message, e);
				}
				catch (Exception e) {
					log.error("Error processing message", e);
				}
			}

			@Override
			public void onClose(int i, String s, boolean b) {

			}

			@Override
			public void onError(Exception e) {
				log.error("WebSocket error", e);
			}
		};
	}
	private Candle parseCandle(String message, String symbol, String interval) throws JsonProcessingException {
		JsonNode node = objectMapper.readTree(message);
		JsonNode k = node.get("k");
		return Candle.builder()
				.symbol(symbol)
				.interval(interval)
				.openTime(Instant.ofEpochMilli(k.get("t").asLong()))
				.closeTime(Instant.ofEpochMilli(k.get("T").asLong()))
				.open(new BigDecimal(k.get("o").asText()))
				.high(new BigDecimal(k.get("h").asText()))
				.low(new BigDecimal(k.get("l").asText()))
				.close(new BigDecimal(k.get("c").asText()))
				.volume(new BigDecimal(k.get("v").asText()))
				.isClosed(k.get("x").asBoolean())
				.build();
	}
}
