package com.example.ws_service.websocket;

import com.fasterxml.jackson.core.JsonProcessingException;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

@Component
@Slf4j
public class MarketWebSocketHandler extends TextWebSocketHandler {

	private final Set<WebSocketSession> sessions =
			ConcurrentHashMap.newKeySet();
	private final Map<String, Set<String>> subscriptions =
			new ConcurrentHashMap<>();
	@Override
	public void afterConnectionEstablished(WebSocketSession session) {
		sessions.add(session);
		subscriptions.put(session.getId(), ConcurrentHashMap.newKeySet());
	}
	@Override
	protected void handleTextMessage(WebSocketSession session, TextMessage message) throws JsonProcessingException {
		JsonNode node = new ObjectMapper().readTree(message.getPayload());

		if ("SUBSCRIBE".equals(node.get("type").asText())) {
			String topic = "candle:%s:%s".formatted(
					node.get("symbol").asText(),
					node.get("interval").asText()
			);
			subscriptions.get(session.getId()).add(topic);
		}
	}
	@Override
	public void afterConnectionClosed(WebSocketSession session, CloseStatus status) {
		sessions.remove(session);
		subscriptions.remove(session.getId());
	}

	public void forward(String topic, String payload) {
		subscriptions.forEach((sessionId, topics) -> {
			if (topics.contains(topic)) {
				WebSocketSession session = findSession(sessionId);
				try {
					if (session != null && session.isOpen()) {
						session.sendMessage(new TextMessage(payload));
					}
				} catch (Exception e) {
					log.error("WS send error", e);
				}
			}
		});
	}

	private WebSocketSession findSession(String sessionId) {
		return sessions.stream()
				.filter(s -> s.getId().equals(sessionId))
				.findFirst()
				.orElse(null);
	}

}
