/* Driver del MS5611 por I2C. Comandos y fórmulas: datasheet MS5611-01BA03 y nota de aplicación AN520 (CRC). */
#include "ms5611.h"
#include "main.h"
#include "i2c.h"

#define DIRECCION      (0x77 << 1)  /* la HAL espera la dirección de 7 bits desplazada */
#define CMD_RESET      0x1E
#define CMD_CONV_D1    0x48         /* presión, OSR 4096 (máxima resolución) */
#define CMD_CONV_D2    0x58         /* temperatura, OSR 4096 */
#define CMD_ADC_READ   0x00
#define CMD_PROM_READ  0xA0         /* + 2*i, i = 0…7 */
#define T_CONVERSION   10           /* ms; máximo 9,04 ms con OSR 4096 */

static uint16_t prom[8];  /* C0: fábrica, C1…C6: coeficientes, C7: CRC */

static bool comando(uint8_t cmd)
{
  return HAL_I2C_Master_Transmit(&hi2c1, DIRECCION, &cmd, 1, 10) == HAL_OK;
}

static uint32_t leer_adc(void)
{
  uint8_t b[3] = { 0 };

  comando(CMD_ADC_READ);
  HAL_I2C_Master_Receive(&hi2c1, DIRECCION, b, 3, 10);
  return (uint32_t)b[0] << 16 | b[1] << 8 | b[2];
}

bool ms5611_init(void)
{
  /* Si nadie responde a la dirección (no hay ACK), la HAL devuelve error. */
  if (!comando(CMD_RESET))
    return false;
  HAL_Delay(3);  /* 2,8 ms de recarga de la PROM */

  for (int i = 0; i < 8; i++)
  {
    uint8_t b[2];
    if (!comando(CMD_PROM_READ + 2 * i) ||
        HAL_I2C_Master_Receive(&hi2c1, DIRECCION, b, 2, 10) != HAL_OK)
      return false;
    prom[i] = b[0] << 8 | b[1];
  }
  /* El MS5611 no tiene registro de identificación: se valida con el CRC de 4 bits de la PROM. */
  return ms5611_crc4(prom) == (prom[7] & 0x000F);
}

bool ms5611_actualizar(float *presion_hpa, float *temp_c)
{
  static enum { LANZAR_D1, ESPERAR_D1, ESPERAR_D2 } fase = LANZAR_D1;
  static uint32_t t0, d1;

  if (fase == LANZAR_D1)
  {
    comando(CMD_CONV_D1);
    t0 = HAL_GetTick();
    fase = ESPERAR_D1;
    return false;
  }
  if (HAL_GetTick() - t0 < T_CONVERSION)
    return false;

  if (fase == ESPERAR_D1)
  {
    d1 = leer_adc();
    comando(CMD_CONV_D2);
    t0 = HAL_GetTick();
    fase = ESPERAR_D2;
    return false;
  }
  ms5611_compensar(prom, d1, leer_adc(), presion_hpa, temp_c);
  fase = LANZAR_D1;
  return true;
}

/* CRC4 de la PROM, algoritmo de la nota de aplicación AN520. */
uint8_t ms5611_crc4(const uint16_t prom_in[8])
{
  uint16_t p[8];
  uint16_t resto = 0;

  for (int i = 0; i < 8; i++)
    p[i] = prom_in[i];
  p[7] &= 0xFF00;  /* el propio CRC no entra en el cálculo */

  for (int cnt = 0; cnt < 16; cnt++)
  {
    resto ^= (cnt % 2) ? (p[cnt >> 1] & 0x00FF) : (p[cnt >> 1] >> 8);
    for (int bit = 8; bit > 0; bit--)
      resto = (resto & 0x8000) ? (resto << 1) ^ 0x3000 : (resto << 1);
  }
  return (resto >> 12) & 0x000F;
}

/* Compensación de primer y segundo orden (datasheet, "Pressure and temperature calculation"). */
void ms5611_compensar(const uint16_t c[8], uint32_t d1, uint32_t d2, float *presion_hpa, float *temp_c)
{
  int64_t dT   = (int64_t)d2 - ((int64_t)c[5] << 8);
  int64_t temp = 2000 + dT * c[6] / (1 << 23);              /* centésimas de °C */
  int64_t off  = ((int64_t)c[2] << 16) + (c[4] * dT) / (1 << 7);
  int64_t sens = ((int64_t)c[1] << 15) + (c[3] * dT) / (1 << 8);

  if (temp < 2000)  /* segundo orden: corrige la no linealidad por debajo de 20 °C */
  {
    int64_t t2    = dT * dT / ((int64_t)1 << 31);
    int64_t off2  = 5 * (temp - 2000) * (temp - 2000) / 2;
    int64_t sens2 = 5 * (temp - 2000) * (temp - 2000) / 4;
    if (temp < -1500)
    {
      off2  += 7 * (temp + 1500) * (temp + 1500);
      sens2 += 11 * (temp + 1500) * (temp + 1500) / 2;
    }
    temp -= t2;
    off  -= off2;
    sens -= sens2;
  }

  int64_t p = ((int64_t)d1 * sens / (1 << 21) - off) / (1 << 15);  /* centésimas de mbar = Pa */
  *presion_hpa = p / 100.0f;
  *temp_c = temp / 100.0f;
}
