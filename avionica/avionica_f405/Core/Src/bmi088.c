/* Driver del BMI088 por SPI. Registros y secuencias: datasheet BST-BMI088-DS000-19. */
#include "bmi088.h"
#include "main.h"
#include "spi.h"
#include <string.h>

/* Registros del acelerómetro */
#define ACC_CHIP_ID     0x00
#define ACC_DATA        0x12  /* X_LSB, X_MSB, Y_LSB, Y_MSB, Z_LSB, Z_MSB */
#define ACC_CONF        0x40
#define ACC_RANGE       0x41
#define ACC_PWR_CONF    0x7C
#define ACC_PWR_CTRL    0x7D
#define ACC_SOFTRESET   0x7E

/* Registros del giroscopio */
#define GYRO_CHIP_ID    0x00
#define GYRO_DATA       0x02
#define GYRO_RANGE      0x0F
#define GYRO_BANDWIDTH  0x10
#define GYRO_SOFTRESET  0x14

#define ACC_ID_ESPERADO   0x1E
#define GYRO_ID_ESPERADO  0x0F
#define SOFTRESET_CMD     0xB6

#define ACC   IMU_CS_GPIO_Port, IMU_CS_Pin
#define GYRO  GYRO_CS_GPIO_Port, GYRO_CS_Pin

static void escribir(GPIO_TypeDef *puerto, uint16_t pin, uint8_t reg, uint8_t valor)
{
  uint8_t tx[2] = { reg & 0x7F, valor };  /* bit 7 = 0: escritura */

  HAL_GPIO_WritePin(puerto, pin, GPIO_PIN_RESET);
  HAL_SPI_Transmit(&hspi1, tx, 2, 10);
  HAL_GPIO_WritePin(puerto, pin, GPIO_PIN_SET);
}

/* Lee n bytes a partir de reg. El acelerómetro envía un byte basura antes de los datos
 * (datasheet, sección 6.1.2), así que para él basura = 1; para el giroscopio, 0. */
static void leer(GPIO_TypeDef *puerto, uint16_t pin, uint8_t reg, uint8_t *dato, uint8_t n, uint8_t basura)
{
  uint8_t tx[8] = { reg | 0x80 };  /* bit 7 = 1: lectura */
  uint8_t rx[8];

  HAL_GPIO_WritePin(puerto, pin, GPIO_PIN_RESET);
  HAL_SPI_TransmitReceive(&hspi1, tx, rx, 1 + basura + n, 10);
  HAL_GPIO_WritePin(puerto, pin, GPIO_PIN_SET);
  memcpy(dato, &rx[1 + basura], n);
}

bool bmi088_init(void)
{
  uint8_t id;

  /* El acelerómetro arranca en modo I2C y pasa a SPI con un flanco de subida en su CS:
   * se hace una lectura de prueba cuyo resultado se descarta (datasheet, sección 3). */
  leer(ACC, ACC_CHIP_ID, &id, 1, 1);
  escribir(ACC, ACC_SOFTRESET, SOFTRESET_CMD);
  HAL_Delay(2);                            /* 1 ms tras el reset */
  leer(ACC, ACC_CHIP_ID, &id, 1, 1);       /* vuelve a modo SPI tras el reset */
  leer(ACC, ACC_CHIP_ID, &id, 1, 1);
  if (id != ACC_ID_ESPERADO)
    return false;

  escribir(ACC, ACC_PWR_CONF, 0x00);       /* modo activo (sale de suspensión) */
  HAL_Delay(1);
  escribir(ACC, ACC_PWR_CTRL, 0x04);       /* enciende el acelerómetro */
  HAL_Delay(1);                            /* 450 µs según el datasheet */
  escribir(ACC, ACC_RANGE, 0x03);          /* ±24 g */
  escribir(ACC, ACC_CONF, 0xAC);           /* filtro normal (0xA), ODR 1600 Hz (0xC) */

  escribir(GYRO, GYRO_SOFTRESET, SOFTRESET_CMD);
  HAL_Delay(30);                           /* 30 ms tras el reset */
  leer(GYRO, GYRO_CHIP_ID, &id, 1, 0);
  if (id != GYRO_ID_ESPERADO)
    return false;

  escribir(GYRO, GYRO_RANGE, 0x00);        /* ±2000 °/s */
  escribir(GYRO, GYRO_BANDWIDTH, 0x00);    /* ODR 2000 Hz, filtro de 532 Hz */
  return true;
}

void bmi088_leer(float acc_g[3], float giro_dps[3])
{
  uint8_t b[6];

  /* Escala del acelerómetro: valor / 32768 * 2^(ACC_RANGE + 1) * 1,5 = valor / 32768 * 24 g */
  leer(ACC, ACC_DATA, b, 6, 1);
  for (int i = 0; i < 3; i++)
    acc_g[i] = (int16_t)(b[2 * i + 1] << 8 | b[2 * i]) * (24.0f / 32768.0f);

  /* Escala del giroscopio en ±2000 °/s: 16,384 LSB por °/s */
  leer(GYRO, GYRO_DATA, b, 6, 0);
  for (int i = 0; i < 3; i++)
    giro_dps[i] = (int16_t)(b[2 * i + 1] << 8 | b[2 * i]) / 16.384f;
}
