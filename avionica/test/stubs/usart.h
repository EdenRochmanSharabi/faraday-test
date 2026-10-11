#pragma once
typedef struct { uint32_t DR; } USART_TypeDef;
typedef struct { USART_TypeDef *Instance; } UART_HandleTypeDef;
static UART_HandleTypeDef huart2;
#define UART_FLAG_RXNE 0
#define __HAL_UART_GET_FLAG(h, f) 0
