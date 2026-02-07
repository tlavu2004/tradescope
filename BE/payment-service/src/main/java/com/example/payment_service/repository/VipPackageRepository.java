package com.example.payment_service.repository;

import com.example.payment_service.entity.VipPackage;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface VipPackageRepository extends JpaRepository<VipPackage, Long> {
	List<VipPackage> findByIsActiveTrue();
}