package com.example.payment_service.dto.request;

import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class PaymentCreationRequest {
	@NotNull(message = "VIP package ID is required")
	private Long vipPackageId;

	@NotNull(message = "Payment method is required")
	private String paymentMethod; // VNPAY, MOMO, etc.
}