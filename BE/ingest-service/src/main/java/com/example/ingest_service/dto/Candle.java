package com.example.ingest_service.dto;

import lombok.*;

import java.math.BigDecimal;
import java.time.Instant;
@Builder
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Candle {

	private String symbol;

	private String interval;

	private Instant openTime;

	private Instant closeTime;

	private BigDecimal open;

	private BigDecimal high;

	private BigDecimal low;

	private BigDecimal close;

	private BigDecimal volume;

	private Boolean isClosed;
}



