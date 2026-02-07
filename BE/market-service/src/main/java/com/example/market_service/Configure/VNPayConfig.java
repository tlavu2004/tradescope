package com.example.market_service.Configure;

import lombok.Getter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
@Getter
public class VNPayConfig {
	@Value("${vnpay.tmn-code}")
	private String tmnCode;

	@Value("${vnpay.hash-secret}")
	private String hashSecret;

	@Value("${vnpay.pay-url}")
	private String payUrl;

	@Value("${vnpay.return-url}")
	private String returnUrl;


	public String getHashSecret() {
		return hashSecret != null ? hashSecret.trim() : null;
	}
}