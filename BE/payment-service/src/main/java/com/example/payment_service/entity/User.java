package com.example.payment_service.entity;

import com.example.payment_service.enums.Role;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "users")
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class User {
	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	private Long id;

	@Column(name = "email", nullable = false, unique = true)
	private String email;

	@Column(name = "user_name")
	private String userName;

	@Enumerated(EnumType.STRING)
	@Builder.Default
	private Role role = Role.USER;

	@Column(name = "vip_start_at")
	private LocalDateTime vipStartAt;

	@Column(name = "vip_end_at")
	private LocalDateTime vipEndAt;
}