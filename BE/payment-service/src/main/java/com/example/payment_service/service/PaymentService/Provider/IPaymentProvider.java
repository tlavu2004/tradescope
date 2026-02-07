package com.example.payment_service.service.PaymentService.Provider;

import com.example.payment_service.entity.Payment;

public interface IPaymentProvider {
	String getType();
	String createPaymentUrl(Payment payment);
}
