package com.example.auth_service.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.concurrent.TimeUnit;

@Service
@RequiredArgsConstructor
@Slf4j
public class TokenCacheService {
	private final RedisTemplate<String, String> redisTemplate;
	private static final String INVALIDATED_TOKEN_PREFIX = "auth:invalidated:";

	public void invalidateTokens(String accessTokenId, String refreshTokenId, LocalDateTime expiration) {
		long ttl = Duration.between(LocalDateTime.now(), expiration).getSeconds();
		if (ttl > 0) {
			redisTemplate.opsForValue().set(
					INVALIDATED_TOKEN_PREFIX + accessTokenId,
					"true",
					ttl,
					TimeUnit.SECONDS
			);
			redisTemplate.opsForValue().set(
					INVALIDATED_TOKEN_PREFIX + refreshTokenId,
					"true",
					ttl,
					TimeUnit.SECONDS
			);
			log.info("Invalidated tokens: {} and {}", accessTokenId, refreshTokenId);
		}
	}

	public boolean isTokenInvalidated(String tokenId) {
		String key = INVALIDATED_TOKEN_PREFIX + tokenId;
		Boolean exists = redisTemplate.hasKey(key);
		return exists != null && exists;
	}
}