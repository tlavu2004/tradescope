package com.example.payment_service.config;

import com.example.payment_service.entity.VipPackage;
import com.example.payment_service.repository.VipPackageRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class SeedDataRunner implements CommandLineRunner {
	private final VipPackageRepository vipPackageRepository;

	@Override
	public void run(String... args) throws Exception {
		if (vipPackageRepository.count() == 0) {
			VipPackage silver = VipPackage.builder()
					.name("Silver")
					.durationDays(30L)
					.price(100000L)
					.description("1 month VIP access")
					.isActive(true)
					.build();

			VipPackage gold = VipPackage.builder()
					.name("Gold")
					.durationDays(365L)
					.price(1000000L)
					.description("1 year VIP access")
					.isActive(true)
					.build();

			vipPackageRepository.save(silver);
			vipPackageRepository.save(gold);
			System.out.println("✅ Seeded VIP packages: Silver and Gold");
		}
	}
}