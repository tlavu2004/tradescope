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
public class VipPackageResponse {
	private Long id;
	private String name;
	private Long durationDays;
	private Long price;
	private String description;
	private Boolean isActive;
	private Instant createdAt;
	private Instant updatedAt;
}