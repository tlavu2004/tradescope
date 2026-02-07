package com.example.payment_service.service.VipService;

import com.example.payment_service.entity.User;
import com.example.payment_service.entity.VipPackage;

public interface IVipService {
	void upgradeVip(User user, VipPackage vipPackage);

	void checkExpiredVip(User user);
}
