package com.example.payment_service.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class VipPackageRequest {
	@NotBlank(message = "Package name is required")
	private String name;

	@NotNull(message = "Duration days is required")
	private Long durationDays;

	@NotNull(message = "Price is required")
	private Long price;

	private String description;
	private Boolean isActive;
}