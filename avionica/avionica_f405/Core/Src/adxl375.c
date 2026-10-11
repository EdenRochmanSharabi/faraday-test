/* Driver del ADXL375 por SPI. Registros: datasheet de Analog Devices, tabla de registros. */
#include "adxl375.h"
#include "main.h"
#include "spi.h"
#include <string.h>

#define DEVID        0x00
#define BW_RATE      0x2C
#define POWER_CTL    0x2D
#define DATA_FORMAT  0x31
#define DATAX0       0x32  /* X0, X1, Y0, Y1, Z0, Z1 */

#define DEVID_ESPERADO  0xE5
#define LECTURA         0x80  /* bit 7: lectura */
#define MULTIBYTE       0x40  /* bit 6: varios bytes seguidos */
#define G_POR_LSB       0.049f

static void escribir(uint8_t reg, uint8_t valor)
{
  uint8_t tx[2] = { reg & 0x3F, valor };

  HAL_GPIO_WritePin(HIGHG_CS_GPIO_Port, HIGHG_CS_Pin, GPIO_PIN_RESET);
  HAL_SPI_Transmit(&hspi1, tx, 2, 10);
  HAL_GPIO_WritePin(HIGHG_CS_GPIO_Port, HIGHG_CS_Pin, GPIO_PIN_SET);
}

static void leer(uint8_t reg, uint8_t *dato, uint8_t n)
{
  uint8_t tx[7] = { reg | LECTURA | (n > 1 ? MULTIBYTE : 0) };
  uint8_t rx[7];

  HAL_GPIO_WritePin(HIGHG_CS_GPIO_Port, HIGHG_CS_Pin, GPIO_PIN_RESET);
  HAL_SPI_TransmitReceive(&hspi1, tx, rx, 1 + n, 10);
  HAL_GPIO_WritePin(HIGHG_CS_GPIO_Port, HIGHG_CS_Pin, GPIO_PIN_SET);
  memcpy(dato, &rx[1], n);
}

bool adxl375_init(void)
{
  uint8_t id;

  /* No tiene comando de reset: reintentar es volver a leer y reconfigurar. */
  leer(DEVID, &id, 1);
  if (id != DEVID_ESPERADO)
    return false;

  escribir(DATA_FORMAT, 0x0B);  /* SPI de 4 hilos, alineado a la derecha (bits D3, D1, D0 fijos a 1) */
  escribir(BW_RATE, 0x0F);      /* 3200 Hz */
  escribir(POWER_CTL, 0x08);    /* bit Measure: empieza a medir */
  return true;
}

void adxl375_leer(float acc_g[3])
{
  uint8_t b[6];

  leer(DATAX0, b, 6);
  for (int i = 0; i < 3; i++)
    acc_g[i] = (int16_t)(b[2 * i + 1] << 8 | b[2 * i]) * G_POR_LSB;
}
