package com.example.auth_service.service;

import com.example.auth_service.Exception.AppException;
import com.example.auth_service.Exception.ErrorCode;
import com.example.auth_service.dto.request.GoogleLoginRequest;
import com.example.auth_service.dto.request.LoginRequest;
import com.example.auth_service.dto.response.AuthenticationResponse;
import com.example.auth_service.entity.User;
import com.example.auth_service.repository.UserRepository;
import com.google.api.client.googleapis.auth.oauth2.GoogleIdToken;
import com.google.api.client.googleapis.auth.oauth2.GoogleIdTokenVerifier;
import com.google.api.client.http.javanet.NetHttpTransport;
import com.google.api.client.json.gson.GsonFactory;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.Collections;

@Service
@RequiredArgsConstructor
public class AuthenticationService {
	private final UserRepository userRepository;
	private final JwtService jwtService;
	@Value("${google.clientId}")
	private String googleClientId;
	public AuthenticationResponse login(LoginRequest request) {
		User user = userRepository.findByUserName(request.getUserName())
				.orElseThrow(() -> new AppException(ErrorCode.USER_NOT_FOUND));
		if(!user.getPassword().equals(request.getPassword())) {
			throw new AppException(ErrorCode.UNAUTHENTICATED);
		}
		String accessToken = jwtService.generateAccessToken(user);
		String refreshToken = jwtService.generateRefreshToken(user);
		return AuthenticationResponse.builder()
				.accessToken(accessToken)
				.refreshToken(refreshToken)
				.isAuthenticated(true)
				.build();
	}
	public AuthenticationResponse loginWithGoogle(GoogleLoginRequest googleLoginRequest) {
		GoogleIdTokenVerifier verifier = new GoogleIdTokenVerifier.Builder(new NetHttpTransport(), new GsonFactory())
				.setAudience(Collections.singletonList(googleClientId))
				.build();
		try {
			GoogleIdToken googleIdToken = verifier.verify(googleLoginRequest.getToken());
			if (googleIdToken == null) {
				throw new AppException(ErrorCode.INVALID_GOOGLE_TOKEN);
			}
			String email = googleIdToken.getPayload().getEmail();
			User user = userRepository.findByEmail(email)
					.orElseGet(() ->
							createUserFromGoogle(googleIdToken)
					);
			String accessToken = jwtService.generateAccessToken(user);
			String refreshToken = jwtService.generateRefreshToken(user);
			return AuthenticationResponse.builder()
					.accessToken(accessToken)
					.refreshToken(refreshToken)
					.isAuthenticated(true)
					.build();
		} catch (Exception e) {
			throw new AppException(ErrorCode.GOOGLE_LOGIN_FAILED);
		}
	}
	public User createUserFromGoogle(GoogleIdToken googleIdToken) {
		GoogleIdToken.Payload payload = googleIdToken.getPayload();
		User user = User.builder()
				.email(payload.getEmail())
				.userName(payload.get("name").toString())
				.avatarUrl(payload.get("picture").toString())
				.build();
		return userRepository.save(user);
	}
}
