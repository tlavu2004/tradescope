package com.example.payment_service.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.Instant;

@Entity
@Table(name = "vip_packages")
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class VipPackage {
	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	private Long id;

	@Column(name = "name", nullable = false, unique = true)
	private String name;

	@Column(name = "duration_days", nullable = false)
	private Long durationDays;

	@Column(name = "price", nullable = false)
	private Long price;

	@Column(name = "description", columnDefinition = "TEXT")
	private String description;

	@Builder.Default
	@Column(name = "is_active")
	private Boolean isActive = true;

	@CreationTimestamp
	@Column(name = "created_at", nullable = false, updatable = false)
	private Instant createdAt;

	@UpdateTimestamp
	@Column(name = "updated_at")
	private Instant updatedAt;
}