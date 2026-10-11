/* BMI088 (Bosch): IMU de 6 ejes en SPI1. Acelerómetro con CS en PA4 (IMU_CS), giroscopio con CS en PB0 (GYRO_CS). */
#ifndef BMI088_H
#define BMI088_H

#include <stdbool.h>

/* Reinicia y configura el sensor (±24 g a 1600 Hz, ±2000 °/s a 2000 Hz).
 * Devuelve false si algún CHIP_ID no coincide: sensor ausente o bus mal configurado. */
bool bmi088_init(void);

/* Lee la última medida: aceleración en g y velocidad angular en °/s (ejes X, Y, Z). */
void bmi088_leer(float acc_g[3], float giro_dps[3]);

#endif
