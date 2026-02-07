package com.example.market_service.controller;

import com.example.market_service.Configure.VNPayConfig;
import com.example.market_service.Utils.VNPayUtil;
import com.example.market_service.entity.Payment;
import com.example.market_service.repository.PaymentRepository;
import com.example.market_service.service.UserService.IUserService;
import com.example.market_service.service.VipService.IVipService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/v1/vnpay")
@RequiredArgsConstructor
public class VNPayCallbackController {
	private final PaymentRepository paymentRepository;
	private final IVipService vipService;
	private final VNPayConfig config;
	private final VNPayUtil vNPayUtil;
	@GetMapping("/ipn")
	public ResponseEntity<?> handleReturn(@RequestParam Map<String, String> params) {

		String secureHash = params.remove("vnp_SecureHash");
		params.remove("vnp_SecureHashType");

		String hashData = vNPayUtil.buildQueryString(params);
		String checkHash = vNPayUtil.hmacSHA512(
				config.getHashSecret(), hashData);

		if (!checkHash.equals(secureHash)) {
			return ResponseEntity.badRequest().body("Invalid signature");
		}

		String responseCode = params.get("vnp_ResponseCode");
		String orderCode = params.get("vnp_TxnRef");

		Payment payment = paymentRepository
				.findByOrderId(orderCode)
				.orElseThrow( () -> new RuntimeException("Payment not found"));

		if ("00".equals(responseCode)) {
			payment.setPaymentStatus("SUCCESS");
			vipService.upgradeVip(payment.getUser(), payment.getVipPackage());
		} else {
			payment.setPaymentStatus("FAILED");
		}

		paymentRepository.save(payment);

		return ResponseEntity.ok("Payment processed");
	}
}
