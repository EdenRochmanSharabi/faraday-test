/* MS5611 (TE Connectivity): barómetro en I2C1. Dirección 0x77 con el pin CSB a GND (0x76 con CSB a VDD). */
#ifndef MS5611_H
#define MS5611_H

#include <stdbool.h>
#include <stdint.h>

/* Reinicia el sensor, lee su calibración de fábrica (PROM) y comprueba su CRC.
 * Devuelve false si no responde por I2C o el CRC no coincide. */
bool ms5611_init(void);

/* Avanza la medida sin bloquear: cada conversión tarda ~9 ms, así que se lanza y se recoge en
 * llamadas posteriores. Devuelve true cuando hay presión (hPa) y temperatura (°C) nuevas. */
bool ms5611_actualizar(float *presion_hpa, float *temp_c);

/* Funciones de cálculo, públicas para poder probarlas en el ordenador (avionica/test). */
uint8_t ms5611_crc4(const uint16_t prom[8]);
void ms5611_compensar(const uint16_t c[8], uint32_t d1, uint32_t d2, float *presion_hpa, float *temp_c);

#endif
