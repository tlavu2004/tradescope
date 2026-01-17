package com.example.market_service.dto.response;

import com.example.market_service.Exception.ErrorCode;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class ApiResponse<T> {
	private T data;
	@Builder.Default
	private int code = ErrorCode.SUCCESS.getCode();
	@Builder.Default
	private String message = ErrorCode.SUCCESS.getMessage();
}
