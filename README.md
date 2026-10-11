# Faraday Rocketry UPV · Prueba de acceso 2026-2027

Eden Rochman Sharabi

Ejercicios de los departamentos de **Aviónica Software** y **Aerodinámica**.

## Aviónica

| Archivo | Contenido |
|---|---|
| [`memoria_avionica.pdf`](avionica/memoria_avionica.pdf) | Respuestas a los ejercicios 1 y 2 y Ejercicio Personal |
| [`comparativa_stm32.xlsx`](avionica/comparativa_stm32.xlsx) | Ejercicio 1a: comparativa de microcontroladores y estimación de carga de CPU |
| [`avionica_f405/`](avionica/avionica_f405/) | Ejercicios 1b y 2b: proyecto de STM32CubeIDE para el STM32F405 |
| [`seleccion_sensores.xlsx`](avionica/seleccion_sensores.xlsx) | Ejercicio 2a: comparativa y selección de sensores |
| [`test/`](avionica/test/) | Pruebas en el ordenador de los drivers del barómetro y del GPS |

- Microcontrolador: STM32F405RGT6 a 168 MHz, con SPI1, I2C1, USART2 y depuración por SWD.
- Sensores: IMU BMI088 y acelerómetro ADXL375 (SPI1), barómetro MS5611 (I2C1) y GPS MAX-M10S (USART2).
- Los drivers están en `avionica_f405/Core/Src/` (`bmi088.c`, `adxl375.c`, `ms5611.c`, `gps.c`) y se integran en `main.c` con una comprobación de arranque.

Pruebas:

```
cd avionica
cc -Itest/stubs -Iavionica_f405/Core/Inc test/test_drivers.c -o test_drivers -lm && ./test_drivers
```

## Aerodinámica

| Archivo | Contenido |
|---|---|
| [`memoria_aerodinamica.pdf`](aerodinamica/memoria_aerodinamica.pdf) | Respuestas a los ejercicios 1 y 2 |
| [`cp_barrowman.py`](aerodinamica/cp_barrowman.py) | Ejercicio 1: centro de presiones con el método de Barrowman |
| [`graficos_cohete.py`](aerodinamica/graficos_cohete.py) | Figuras del CP frente al Mach y al ángulo de ataque |
| [`figuras/cohete/`](aerodinamica/figuras/cohete/) | Figuras generadas |

El cálculo usa la geometría del cohete Camões (EuRoC 2023), publicada en los ejemplos de RocketPy. Requiere Python 3 con `numpy` y `matplotlib`:

```
cd aerodinamica
python3 graficos_cohete.py
```
