/* Lectura del MAX-M10S: recepción por UART y análisis de la frase NMEA GGA. */
#include "gps.h"
#include "main.h"
#include "usart.h"
#include <stdlib.h>
#include <string.h>

#define T_ESPERA_INIT  2000  /* ms; el módulo envía frases cada segundo */

static char linea[100];
static uint8_t largo;

/* Comprueba el checksum NMEA: XOR de los caracteres entre '$' y '*', escrito en hexadecimal tras '*'. */
static bool checksum_ok(const char *s)
{
  uint8_t x = 0;

  for (s++; *s && *s != '*'; s++)
    x ^= (uint8_t)*s;
  return *s == '*' && strtoul(s + 1, NULL, 16) == x;
}

/* Devuelve el campo k (0 = tipo de frase), o NULL si la frase tiene menos campos. */
static const char *campo(const char *s, int k)
{
  while (k-- > 0 && s)
  {
    s = strchr(s, ',');
    if (s)
      s++;
  }
  return s;
}

/* NMEA escribe las coordenadas como gggmm.mmmm (grados y minutos). */
static float a_grados(const char *s, const char *hemisferio)
{
  float v = strtof(s, NULL);
  int grados = (int)(v / 100);
  float resultado = grados + (v - grados * 100) / 60.0f;

  return (*hemisferio == 'S' || *hemisferio == 'W') ? -resultado : resultado;
}

/* $GNGGA,hora,lat,N/S,lon,E/W,calidad,satélites,hdop,altitud,M,... */
static void leer_gga(gps_t *g)
{
  const char *f[10];

  for (int k = 1; k < 10; k++)
    if ((f[k] = campo(linea, k)) == NULL)
      return;

  g->calidad = (uint8_t)atoi(f[6]);
  g->satelites = (uint8_t)atoi(f[7]);
  if (g->calidad == 0)
    return;  /* sin posición: los campos llegan vacíos */
  g->lat_deg = a_grados(f[2], f[3]);
  g->lon_deg = a_grados(f[4], f[5]);
  g->alt_m = strtof(f[9], NULL);
}

void gps_procesar_byte(char c, gps_t *g)
{
  if (c == '$')
    largo = 0;
  if (c == '\r' || c == '\n')
  {
    if (largo > 6 && linea[0] == '$')
    {
      linea[largo] = '\0';
      if (checksum_ok(linea))
      {
        g->frases_validas++;
        if (strncmp(&linea[3], "GGA", 3) == 0)  /* $GPGGA, $GNGGA… según las constelaciones */
          leer_gga(g);
      }
    }
    largo = 0;
    return;
  }
  if (largo < sizeof(linea) - 1)
    linea[largo++] = c;
}

/* Simplificación: lectura por sondeo del registro de datos; a 9600 baudios llega un byte cada ~1 ms,
 * así que el bucle principal debe dar una vuelta en menos de 1 ms. Con FreeRTOS (Ej. 3) pasaría a DMA. */
void gps_actualizar(gps_t *g)
{
  while (__HAL_UART_GET_FLAG(&huart2, UART_FLAG_RXNE))
    gps_procesar_byte((char)(huart2.Instance->DR & 0xFF), g);
}

bool gps_init(gps_t *g)
{
  uint32_t t0 = HAL_GetTick();
  uint32_t antes = g->frases_validas;

  while (HAL_GetTick() - t0 < T_ESPERA_INIT)
  {
    gps_actualizar(g);
    if (g->frases_validas > antes)
      return true;
  }
  return false;
}
