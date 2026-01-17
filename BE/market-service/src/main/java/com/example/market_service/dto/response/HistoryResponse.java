package com.example.market_service.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class HistoryResponse {
	private String symbol;
	private String interval;
	private Integer count;
	private List<CandleResponse> candles;
}
