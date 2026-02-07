package com.example.market_service.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "vip_packages")
@Builder
@Data
@AllArgsConstructor
@NoArgsConstructor
public class VipPackage {
	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	private Long id;

	private String name;
	private Long durationDays;
	private Long price;
	@Builder.Default
	private Boolean isActive = true;
}
