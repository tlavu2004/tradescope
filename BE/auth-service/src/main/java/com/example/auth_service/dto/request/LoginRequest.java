package com.example.auth_service.dto.request;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
public class LoginRequest {
	@NotBlank(message = "REQUIRED_USER_NAME")
	private String userName;
	@NotBlank(message = "REQUIRED_PASSWORD")
	private String password;
}
