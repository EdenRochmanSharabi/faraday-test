/* MAX-M10S (u-blox): GPS por USART2 (PA2 TX → RX del GPS, PA3 RX ← TX del GPS), 9600 baudios 8N1.
 * El módulo envía frases NMEA de texto una vez por segundo; aquí se lee la frase GGA (posición y altitud). */
#ifndef GPS_H
#define GPS_H

#include <stdbool.h>
#include <stdint.h>

typedef struct
{
  float lat_deg;           /* + norte, − sur */
  float lon_deg;           /* + este, − oeste */
  float alt_m;             /* sobre el nivel del mar */
  uint8_t calidad;         /* 0 = sin posición, 1 = GPS, 2 = DGPS */
  uint8_t satelites;
  uint32_t frases_validas; /* frases NMEA con checksum correcto */
} gps_t;

/* Espera hasta 2 s una frase NMEA válida. Devuelve false si no llega: cable, baudios o módulo. */
bool gps_init(gps_t *g);

/* Procesa todos los bytes recibidos desde la última llamada. No bloquea. */
void gps_actualizar(gps_t *g);

/* Procesa un byte. Pública para poder probarla en el ordenador (avionica/test). */
void gps_procesar_byte(char c, gps_t *g);

#endif
