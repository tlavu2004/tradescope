package com.example.market_service.Utils;

import org.springframework.stereotype.Component;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.stream.Collectors;

@Component
public class VNPayUtil {
	public String hmacSHA512(String key, String data) {
		try {
			// Trim key để tránh khoảng trắng thừa
			key = key.trim();

			Mac hmac = Mac.getInstance("HmacSHA512");
			SecretKeySpec secretKey =
					new SecretKeySpec(key.getBytes(StandardCharsets.UTF_8), "HmacSHA512");
			hmac.init(secretKey);
			byte[] bytes = hmac.doFinal(data.getBytes(StandardCharsets.UTF_8));

			StringBuilder hash = new StringBuilder();
			for (byte b : bytes) {
				hash.append(String.format("%02x", b));
			}
			return hash.toString();
		} catch (Exception e) {
			throw new RuntimeException("Error while hashing", e);
		}
	}

	// ✅ FIX: buildHashData phải URL encode giống buildQueryString
	public String buildHashData(Map<String, String> params) {
		return params.entrySet().stream()
				.filter(e -> e.getValue() != null && !e.getValue().isEmpty())
				.sorted(Map.Entry.comparingByKey())
				.map(e -> {
					try {
						return e.getKey() + "=" +
								URLEncoder.encode(e.getValue(), StandardCharsets.UTF_8.toString());
					} catch (Exception ex) {
						throw new RuntimeException(ex);
					}
				})
				.collect(Collectors.joining("&"));
	}

	public String buildQueryString(Map<String, String> params) {
		return params.entrySet().stream()
				.filter(e -> e.getValue() != null && !e.getValue().isEmpty())
				.sorted(Map.Entry.comparingByKey())
				.map(e -> {
					try {
						return e.getKey() + "=" +
								URLEncoder.encode(e.getValue(), StandardCharsets.UTF_8.toString());
					} catch (Exception ex) {
						throw new RuntimeException(ex);
					}
				})
				.collect(Collectors.joining("&"));
	}
}