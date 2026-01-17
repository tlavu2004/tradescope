package com.example.market_service.Mapper;

import com.example.market_service.dto.request.CandleCreationRequest;
import com.example.market_service.dto.response.CandleResponse;
import com.example.market_service.entity.Candle;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface CandleMapper {
	Candle toCandle(CandleCreationRequest request);
	CandleResponse toCandleResponse(Candle candle);
}
