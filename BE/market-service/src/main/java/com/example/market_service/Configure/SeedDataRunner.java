package com.example.market_service.Configure;

import com.example.market_service.entity.User;
import com.example.market_service.entity.VipPackage;
import com.example.market_service.enums.Role;
import com.example.market_service.repository.UserRepository;
import com.example.market_service.repository.VipPackageRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class SeedDataRunner implements CommandLineRunner {
    private final UserRepository userRepository;
	private final VipPackageRepository vipPackageRepository;
    @Override
    public void run(String... args) throws Exception {
        String seedUser = "testuser";
        if (userRepository.existsByUserName(seedUser)) {
            System.out.println("Seed user already exists: " + seedUser);
        } else {
            User u = User.builder()
                    .email("testuser@example.com")
                    .userName(seedUser)
                    .password("password123")
                    .role(Role.USER)
                    .isActive(true)
                    .build();

            userRepository.save(u);
            System.out.println("Seeded user: " + seedUser + " / password123");
        }

        String seedAdmin = "admin";
        if (userRepository.existsByUserName(seedAdmin)) {
            System.out.println("Seed admin already exists: " + seedAdmin);
        } else {
            User admin = User.builder()
                    .email("admin@example.com")
                    .userName(seedAdmin)
                    .password("admin123")
                    .role(Role.ADMIN)
                    .isActive(true)
                    .build();

            userRepository.save(admin);
            System.out.println("Seeded admin: " + seedAdmin + " / admin123");
        }
        if (vipPackageRepository.count() == 0 ) {
			VipPackage vip1 = VipPackage.builder()
					.name("Silver")
					.durationDays(30L)
					.price(100000L)
					.isActive(true)
					.build();
			VipPackage vip2 = VipPackage.builder()
					.name("Gold")
					.durationDays(365L)
					.price(1000000L)
					.isActive(true)
					.build();
			vipPackageRepository.save(vip1);
			vipPackageRepository.save(vip2);
			System.out.println("Seeded VIP packages: Silver and Gold");
        }
    }
}
