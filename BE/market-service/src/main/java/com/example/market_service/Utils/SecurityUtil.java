package com.example.market_service.Utils;

import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;

import java.util.Set;
import java.util.stream.Collectors;

@Component
public class SecurityUtil {
	public Authentication getAuthentication() {
		return SecurityContextHolder.getContext().getAuthentication();
	}
	public Long getCurrentUserId() {
		Authentication auth = getAuthentication();
		if (auth == null || !auth.isAuthenticated()) {
			return null;
		}
		return Long.parseLong(auth.getName());
	}
	public Set<String> getCurrentUserRoles() {
		Authentication auth = getAuthentication();
		if (auth == null) return Set.of();

		return auth.getAuthorities().stream()
				.map(GrantedAuthority::getAuthority)
				.collect(Collectors.toSet());
	}
	public boolean hasRole(String role) {
		return getCurrentUserRoles().contains("ROLE_" + role);
	}
}
