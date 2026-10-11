#pragma once
typedef struct { int unused; } I2C_HandleTypeDef;
static I2C_HandleTypeDef hi2c1;
static inline HAL_StatusTypeDef HAL_I2C_Master_Transmit(I2C_HandleTypeDef *h, uint16_t a, uint8_t *d, uint16_t n, uint32_t t) { (void)h; (void)a; (void)d; (void)n; (void)t; return HAL_ERROR; }
static inline HAL_StatusTypeDef HAL_I2C_Master_Receive(I2C_HandleTypeDef *h, uint16_t a, uint8_t *d, uint16_t n, uint32_t t) { (void)h; (void)a; (void)d; (void)n; (void)t; return HAL_ERROR; }
