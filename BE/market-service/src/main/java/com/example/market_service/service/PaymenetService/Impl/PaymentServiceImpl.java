package com.example.market_service.service.PaymenetService.Impl;

import com.example.market_service.Exception.AppException;
import com.example.market_service.Exception.ErrorCode;
import com.example.market_service.entity.Payment;
import com.example.market_service.entity.User;
import com.example.market_service.entity.VipPackage;
import com.example.market_service.repository.PaymentRepository;
import com.example.market_service.repository.UserRepository;
import com.example.market_service.repository.VipPackageRepository;
import com.example.market_service.service.PaymenetService.Factory.PaymentProviderFactory;
import com.example.market_service.service.PaymenetService.IPaymentService;
import com.example.market_service.service.PaymenetService.Provider.IPaymentProvider;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class PaymentServiceImpl implements IPaymentService {
	private final UserRepository userRepository;
	private final VipPackageRepository vipPackageRepository;
	private final PaymentRepository paymentRepository;
	private final PaymentProviderFactory paymentProviderFactory;

	@Override
	@Transactional
	public String createPayment(Long userId, Long vipPackageId, String method) {
		User user = userRepository.findById(userId)
				.orElseThrow(() -> new AppException(ErrorCode.USER_NOT_FOUND));
		VipPackage vipPackage = vipPackageRepository.findById(vipPackageId)
				.orElseThrow(() -> new AppException(ErrorCode.VIP_PACKAGE_NOT_FOUND));
		String orderCode = "VIP-" + System.currentTimeMillis() + "-" + userId;
		Payment payment = Payment.builder()
				.user(user)
				.vipPackage(vipPackage)
				.paymentProvider(method)
				.amount(vipPackage.getPrice())
				.orderId(orderCode)
				.paymentStatus("PENDING")
				.build();
		paymentRepository.save(payment);
		IPaymentProvider paymentProvider = paymentProviderFactory.getProvider(method);
		return paymentProvider.createPaymentUrl(payment);

	}
}
