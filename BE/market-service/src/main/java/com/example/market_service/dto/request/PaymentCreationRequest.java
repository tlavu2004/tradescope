package com.example.market_service.dto.request;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
public class PaymentCreationRequest {
	private Long vipPackageId;
	@NotBlank(message = "Payment method is required")
	private String paymentMethod;
}
