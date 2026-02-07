package com.example.market_service.service.VipService.Impl;

import com.example.market_service.entity.User;
import com.example.market_service.entity.VipPackage;
import com.example.market_service.enums.Role;
import com.example.market_service.repository.UserRepository;
import com.example.market_service.repository.VipPackageRepository;
import com.example.market_service.service.VipService.IVipService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class VipServiceImpl implements IVipService {
	private final UserRepository userRepository;
	private final VipPackageRepository vipPackageRepository;

	@Override
	public void upgradeVip(User user, VipPackage vipPackage) {
		user.setRole(Role.VIP);
		LocalDateTime now = LocalDateTime.now();
		user.setVipStartAt(now);
		user.setVipEndAt(now.plusDays(vipPackage.getDurationDays()));
		userRepository.save(user);
	}
}
