package com.example.ingest_service.service;

import com.example.ingest_service.dto.Candle;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class RedisService {
	private final StringRedisTemplate redisTemplate;
	private String key (String symbol, String interval) {
		return "candles:" + symbol + ":" + interval;
	}
	public void pushCandle(String symbol, String interval, String candleJson) {
		String key = key(symbol, interval);
		redisTemplate.opsForList().leftPush(key, candleJson);
		redisTemplate.opsForList().trim(key, 0, 499);
	}
	public void publishCandle(String channel, String candleJson) {
		redisTemplate.convertAndSend(channel, candleJson);
	}
}
