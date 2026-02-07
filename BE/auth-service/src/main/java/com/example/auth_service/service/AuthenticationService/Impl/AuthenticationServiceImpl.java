package com.example.auth_service.service;

import com.example.auth_service.dto.request.GoogleLoginRequest;
import com.example.auth_service.dto.request.LoginRequest;
import com.example.auth_service.dto.request.LogoutRequest;
import com.example.auth_service.dto.request.RefreshTokenRequest;
import com.example.auth_service.dto.response.AuthenticationResponse;
import com.example.auth_service.entity.User;
import com.example.auth_service.exception.AppException;
import com.example.auth_service.exception.ErrorCode;
import com.example.auth_service.repository.UserRepository;
import com.example.auth_service.service.AuthenticationService.IAuthenticationService;
import com.google.api.client.googleapis.auth.oauth2.GoogleIdToken;
import com.google.api.client.googleapis.auth.oauth2.GoogleIdTokenVerifier;
import com.google.api.client.http.javanet.NetHttpTransport;
import com.google.api.client.json.gson.GsonFactory;
import io.jsonwebtoken.Claims;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.time.ZoneId;
import java.util.Collections;

@Service
@RequiredArgsConstructor
@Slf4j
public class AuthenticationServiceImpl implements IAuthenticationService {
	private final UserRepository userRepository;
	private final com.example.auth_service.service.JwtService jwtService;
	private final com.example.auth_service.service.TokenCacheService tokenCacheService;

	@Value("${google.clientId}")
	private String googleClientId;

	@Override
	public AuthenticationResponse login(LoginRequest request) {
		User user = userRepository.findByUserName(request.getUserName())
				.orElseThrow(() -> new AppException(ErrorCode.USER_NOT_FOUND));

		if (!user.getPassword().equals(request.getPassword())) {
			throw new AppException(ErrorCode.INVALID_PASSWORD);
		}

		String accessToken = jwtService.generateAccessToken(user);
		String refreshToken = jwtService.generateRefreshToken(user);

		return AuthenticationResponse.builder()
				.accessToken(accessToken)
				.refreshToken(refreshToken)
				.isAuthenticated(true)
				.role(user.getRole())
				.build();
	}

	@Override
	public AuthenticationResponse loginWithGoogle(GoogleLoginRequest googleLoginRequest) {
		GoogleIdTokenVerifier verifier = new GoogleIdTokenVerifier.Builder(
				new NetHttpTransport(),
				new GsonFactory()
		).setAudience(Collections.singletonList(googleClientId)).build();

		try {
			GoogleIdToken googleIdToken = verifier.verify(googleLoginRequest.getToken());
			if (googleIdToken == null) {
				throw new AppException(ErrorCode.INVALID_GOOGLE_TOKEN);
			}

			String email = googleIdToken.getPayload().getEmail();
			User user = userRepository.findByEmail(email)
					.orElseGet(() -> createUserFromGoogle(googleIdToken));

			String accessToken = jwtService.generateAccessToken(user);
			String refreshToken = jwtService.generateRefreshToken(user);

			return AuthenticationResponse.builder()
					.accessToken(accessToken)
					.refreshToken(refreshToken)
					.isAuthenticated(true)
					.role(user.getRole())
					.build();
		} catch (Exception e) {
			throw new AppException(ErrorCode.GOOGLE_LOGIN_FAILED);
		}
	}

	private User createUserFromGoogle(GoogleIdToken googleIdToken) {
		GoogleIdToken.Payload payload = googleIdToken.getPayload();
		User user = User.builder()
				.email(payload.getEmail())
				.userName(payload.get("name").toString())
				.avatarUrl(payload.get("picture").toString())
				.googleId(payload.getSubject())
				.build();
		return userRepository.save(user);
	}

	@Override
	public AuthenticationResponse refreshToken(RefreshTokenRequest refreshTokenRequest) {
		String refreshToken = refreshTokenRequest.getRefreshToken();
		if (refreshToken == null || refreshToken.isEmpty()) {
			throw new AppException(ErrorCode.INVALID_REFRESH_TOKEN);
		}

		Claims claims = jwtService.verifyToken(refreshToken);
		String acId = claims.get("acId", String.class);
		String refreshTokenId = claims.getId();

		if (tokenCacheService.isTokenInvalidated(refreshTokenId)) {
			throw new AppException(ErrorCode.INVALID_REFRESH_TOKEN);
		}

		tokenCacheService.invalidateTokens(
				acId,
				refreshTokenId,
				claims.getExpiration().toInstant()
						.atZone(ZoneId.systemDefault())
						.toLocalDateTime()
		);

		User user = userRepository.findById(Long.parseLong(claims.getSubject()))
				.orElseThrow(() -> new AppException(ErrorCode.USER_NOT_FOUND));

		String newAccessToken = jwtService.generateAccessToken(user);
		String newRefreshToken = jwtService.generateRefreshToken(user);

		return AuthenticationResponse.builder()
				.accessToken(newAccessToken)
				.refreshToken(newRefreshToken)
				.isAuthenticated(true)
				.role(user.getRole())
				.build();
	}

	@Override
	public void logout(LogoutRequest logoutRequest) {
		Claims claims = jwtService.verifyToken(logoutRequest.getAccessToken());
		String accessTokenId = claims.getId();
		String refreshTokenId = claims.get("rfId", String.class);

		tokenCacheService.invalidateTokens(
				accessTokenId,
				refreshTokenId,
				claims.getExpiration().toInstant()
						.atZone(ZoneId.systemDefault())
						.toLocalDateTime()
		);
	}
}