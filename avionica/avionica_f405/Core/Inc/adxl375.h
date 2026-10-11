/* ADXL375 (Analog Devices): acelerómetro de ±200 g en SPI1, CS en PB1 (HIGHG_CS). Requiere SPI en modo 3 y ≤ 5 MHz. */
#ifndef ADXL375_H
#define ADXL375_H

#include <stdbool.h>

/* Comprueba el DEVID y configura 3200 Hz en modo medida. Devuelve false si no responde. */
bool adxl375_init(void);

/* Lee la última medida en g (ejes X, Y, Z). */
void adxl375_leer(float acc_g[3]);

#endif
