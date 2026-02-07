package com.example.auth_service.service.AuthenticationService;

import com.example.auth_service.dto.request.GoogleLoginRequest;
import com.example.auth_service.dto.request.LoginRequest;
import com.example.auth_service.dto.request.LogoutRequest;
import com.example.auth_service.dto.request.RefreshTokenRequest;
import com.example.auth_service.dto.response.AuthenticationResponse;

public interface IAuthenticationService {
	public AuthenticationResponse login(LoginRequest request);
	public AuthenticationResponse loginWithGoogle(GoogleLoginRequest googleLoginRequest);
	public AuthenticationResponse refreshToken(RefreshTokenRequest refreshTokenRequest);
	public void logout(LogoutRequest logoutRequest);
}
