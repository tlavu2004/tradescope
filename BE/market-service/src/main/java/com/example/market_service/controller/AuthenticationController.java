package com.example.market_service.controller;

import com.example.market_service.dto.response.ApiResponse;
import com.example.market_service.dto.response.AuthenticationResponse;
import com.example.market_service.dto.response.IntrospectResponse;
import com.example.market_service.service.AuthenticationService.IAuthenticationService;
import com.example.market_service.service.AuthenticationService.Impl.AuthenticationServiceImpl;
import com.example.market_service.service.JwtService;
import com.example.market_service.dto.request.GoogleLoginRequest;
import com.example.market_service.dto.request.IntrospectRequest;
import com.example.market_service.dto.request.LoginRequest;
import com.example.market_service.dto.request.LogoutRequest;
import com.example.market_service.dto.request.RefreshTokenRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/auth")
public class AuthenticationController {
	private final IAuthenticationService authenticationServiceImpl;
	private final JwtService jwtService;
	@PostMapping("/login")
	public ApiResponse<AuthenticationResponse> login(@RequestBody @Valid LoginRequest request) {
		return ApiResponse.<AuthenticationResponse>builder()
				.message("Login successful")
				.data(authenticationServiceImpl.login(request))
				.build();
	}
	@PostMapping("/login/google")
	public ApiResponse<AuthenticationResponse> loginWithGoogle(@RequestBody GoogleLoginRequest request) {
		return ApiResponse.<AuthenticationResponse>builder()
				.message("Login with Google successful")
				.data(authenticationServiceImpl.loginWithGoogle(request))
				.build();
	}
	@PostMapping("/refresh-token")
	public ApiResponse<AuthenticationResponse> refreshToken(@RequestBody RefreshTokenRequest refreshToken) {
		return ApiResponse.<AuthenticationResponse>builder()
				.message("Token refreshed successfully")
				.data(authenticationServiceImpl.refreshToken(refreshToken))
				.build();
	}
	@PostMapping("/logout")
	public ApiResponse<Void> logout(@RequestBody LogoutRequest request) {
		authenticationServiceImpl.logout(request);
		return ApiResponse.<Void>builder()
				.message("Logout successful")
				.build();
	}
	@PostMapping("/introspect")
	public ApiResponse<IntrospectResponse> introspectToken(@RequestBody IntrospectRequest request) {
		return ApiResponse.<IntrospectResponse>builder()
				.message("Token introspection successful")
				.data(jwtService.introspectToken(request))
				.build();
	}

}
