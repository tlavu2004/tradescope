package com.example.market_service.Mapper;

import com.example.market_service.dto.request.GoogleUserCreationRequest;
import com.example.market_service.dto.request.UserCreationRequest;
import com.example.market_service.dto.response.UserResponse;
import com.example.market_service.entity.User;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface UserMapper {
	User toEntity(GoogleUserCreationRequest request);
	User toEntity(UserCreationRequest request);
	UserResponse toResponse(User user);
}
