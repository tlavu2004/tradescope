package com.example.payment_service.config;

import lombok.Getter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;

@Configuration
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
}