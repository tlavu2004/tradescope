package com.example.payment_service.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class PaymentResponse {
	private Long id;
	private Long userId;
	private Long vipPackageId;
	private String orderId;
	private String paymentProvider;
	private Long amount;
	private String paymentStatus;
	private Instant createdAt;
}