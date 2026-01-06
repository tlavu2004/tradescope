package com.example.ingest_service.dto.response;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class ApiResponseLong {
	private Long data;
	private Integer code;
	private String message;
}
