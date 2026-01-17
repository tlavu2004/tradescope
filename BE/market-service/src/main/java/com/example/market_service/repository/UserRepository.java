package com.example.market_service.repository;

import com.example.market_service.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
	Optional<User> findByUserName(String username);
	Optional<User> findByEmail(String email);
	boolean existsByUserName(String username);
	boolean existsByEmail(String email);
}
