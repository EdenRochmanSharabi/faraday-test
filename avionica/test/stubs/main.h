#pragma once
/* Sustituto mínimo de la HAL para compilar los drivers en el ordenador. */
#include <stdint.h>
typedef enum { HAL_OK, HAL_ERROR } HAL_StatusTypeDef;
static inline uint32_t HAL_GetTick(void) { return 0; }
static inline void HAL_Delay(uint32_t ms) { (void)ms; }
