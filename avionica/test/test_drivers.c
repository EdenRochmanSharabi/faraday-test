/* Pruebas en el ordenador de las partes de cálculo de los drivers (sin placa).
 * Ejecutar desde avionica/:  cc -Itest/stubs -Iavionica_f405/Core/Inc test/test_drivers.c -o /tmp/t && /tmp/t */
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include "../avionica_f405/Core/Src/ms5611.c"
#include "../avionica_f405/Core/Src/gps.c"

static void enviar(const char *s, gps_t *g)
{
  while (*s)
    gps_procesar_byte(*s++, g);
}

int main(void)
{
  /* Ejemplo de cálculo del datasheet del MS5611: 2007 → 20,07 °C y 100009 → 1000,09 mbar. */
  uint16_t c[8] = { 0, 40127, 36924, 23317, 23282, 33464, 28312, 0 };
  float p, t;
  ms5611_compensar(c, 9085466, 8569150, &p, &t);
  assert(fabsf(t - 20.07f) < 0.01f);
  assert(fabsf(p - 1000.09f) < 0.01f);

  /* El CRC acepta la PROM con su CRC correcto y detecta un bit cambiado. */
  c[7] = ms5611_crc4(c);
  assert(ms5611_crc4(c) == (c[7] & 0xF));
  c[3] ^= 0x0100;
  assert(ms5611_crc4(c) != (c[7] & 0xF));

  /* Frase GGA real de ejemplo (checksum 0x47), troceada como llega por la UART. */
  gps_t g = { 0 };
  enviar("$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47\r\n", &g);
  assert(g.frases_validas == 1 && g.calidad == 1 && g.satelites == 8);
  assert(fabsf(g.lat_deg - 48.1173f) < 1e-4f);
  assert(fabsf(g.lon_deg - 11.5167f) < 1e-4f);
  assert(fabsf(g.alt_m - 545.4f) < 1e-3f);

  /* Un checksum incorrecto se descarta. */
  enviar("$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*48\r\n", &g);
  assert(g.frases_validas == 1);

  /* Sin posición (calidad 0): se cuenta como frase válida pero no cambia las coordenadas. */
  enviar("$GNGGA,,,,,,0,00,99.99,,,,,,*56\r\n", &g);
  assert(g.frases_validas == 2 && g.calidad == 0 && fabsf(g.lat_deg - 48.1173f) < 1e-4f);

  printf("OK: MS5611 %.2f hPa %.2f °C, GPS %.4f %.4f %.1f m\n", p, t, g.lat_deg, g.lon_deg, g.alt_m);
  return 0;
}
