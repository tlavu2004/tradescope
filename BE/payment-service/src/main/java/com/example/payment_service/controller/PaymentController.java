package com.example.payment_service.controller;

import com.example.payment_service.dto.request.PaymentCreationRequest;
import com.example.payment_service.dto.response.ApiResponse;
import com.example.payment_service.service.PaymentService.IPaymentService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/payments")
@RequiredArgsConstructor
@Slf4j
public class PaymentController {
	private final IPaymentService paymentService;

	@PostMapping
	public ApiResponse<String> createPayment(@RequestBody PaymentCreationRequest request) {
		log.info("Received payment creation request: {}", request);
		Long userId = Long.parseLong(SecurityContextHolder.getContext().getAuthentication().getName());
		return ApiResponse.<String>builder()
				.message("Payment created successfully")
				.data(paymentService.createPayment(userId, request.getVipPackageId(), request.getPaymentMethod()))
				.build();
	}

	@PostMapping("/finalize")
	public ApiResponse<String> finalizePayment(@RequestParam String responseCode, @RequestParam String orderId) {
		paymentService.finalizePayment(responseCode, orderId);
		return ApiResponse.<String>builder()
				.message("Payment finalized successfully")
				.build();
	}
}
