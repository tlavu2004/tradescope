package com.example.ingest_service.configure;

import com.example.ingest_service.dto.response.ApiResponseLong;
import com.example.ingest_service.dto.response.LastOpenTimeResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

@Component
@RequiredArgsConstructor
@Slf4j
public class StorageServiceWebClient {
	private final WebClient webClient;
	@Value("${storage-service.base-url}")
	private String storageServiceBaseUrl;
	public Long getLastOpenTime(String symbol, String interval) {
		try{
			ApiResponseLong response = webClient.get()
					.uri(uriBuilder -> uriBuilder
							.path("/candles/last-open-time")
							.queryParam("symbol", symbol)
							.queryParam("interval", interval)
							.build())
					.retrieve()
					.bodyToMono(ApiResponseLong.class)
					.block();

			if (response == null) {
				log.warn("StorageService returned null for last-open-time {} {}", symbol, interval);
				return null;
			}
			return response.getData();
		}
		catch (Exception e) {
			log.error("Error while calling StorageService for last-open-time {} {}: {}", symbol, interval, e.getMessage());
			return null;
		}

	}
}
