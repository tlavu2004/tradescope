package com.example.payment_service.exception;

import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
public enum ErrorCode {
	USER_NOT_FOUND(2001, "User not found", HttpStatus.NOT_FOUND),
	VIP_PACKAGE_NOT_FOUND(2002, "VIP package not found", HttpStatus.NOT_FOUND),
	PAYMENT_NOT_FOUND(2003, "Payment not found", HttpStatus.NOT_FOUND),
	PAYMENT_CREATION_FAILED(2004, "Payment creation failed", HttpStatus.INTERNAL_SERVER_ERROR),
	INVALID_PAYMENT_PROVIDER(2005, "Invalid payment provider", HttpStatus.BAD_REQUEST);

	private final int code;
	private final String message;
	private final HttpStatus httpStatus;

	ErrorCode(int code, String message, HttpStatus httpStatus) {
		this.code = code;
		this.message = message;
		this.httpStatus = httpStatus;
	}
}