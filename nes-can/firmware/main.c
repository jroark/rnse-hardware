/* NES / fault-tolerant CAN adapter. ATtiny1616, 20 MHz internal clock.
 * UPDI remains PA0. No fuses are written by this build. */
#define F_CPU 20000000UL
#include <avr/cpufunc.h>
#include <avr/io.h>
#include <avr/wdt.h>
#include <stdint.h>
#include <util/delay.h>
#ifndef NES_CAN_ID
#define NES_CAN_ID 0x6e3
#endif
#ifndef CAN_MODE
#define CAN_MODE 0 /* 0x40 internal loopback; 0x60 listen only */
#endif
static uint8_t spi(uint8_t b) {
  SPI0.DATA = b;
  while (!(SPI0.INTFLAGS & SPI_IF_bm))
    ;
  return SPI0.DATA;
}
static void select(void) { PORTA.OUTCLR = PIN4_bm; }
static void release(void) { PORTA.OUTSET = PIN4_bm; }
static uint8_t readreg(uint8_t a) {
  uint8_t v;
  select();
  spi(3);
  spi(a);
  v = spi(0);
  release();
  return v;
}
static void writereg(uint8_t a, uint8_t v) {
  select();
  spi(2);
  spi(a);
  spi(v);
  release();
}
static void standby(void) { PORTB.OUTCLR = PIN2_bm | PIN3_bm; }
static uint8_t init(void) {
  uint8_t i;
  standby();
  select();
  spi(0xc0);
  release();
  _delay_ms(10);
  if ((readreg(0x0e) & 0xe0) != 0x80)
    return 0;
  writereg(0x2a, 3);
  writereg(0x29, 0xbe);
  writereg(0x28, 3);
  /* Receive nothing useful: hardware queues may fill but do not block TX. */
  writereg(0x60, 0x60);
  writereg(0x70, 0x60);
  writereg(0x0f, CAN_MODE | 8); /* one-shot: bounded retries */
  for (i = 0; i < 100; i++) {
    if ((readreg(0x0e) & 0xe0) == CAN_MODE) {
      if (CAN_MODE != 0x40)
        PORTB.OUTSET = PIN2_bm | PIN3_bm;
      return 1;
    }
    _delay_ms(1);
  }
  return 0;
}
static uint8_t send(uint8_t *d) {
  uint8_t i;
  if (readreg(0x30) & 8)
    return 0;
  writereg(0x31, NES_CAN_ID >> 3);
  writereg(0x32, (NES_CAN_ID & 7) << 5);
  writereg(0x33, 0);
  writereg(0x34, 0);
  writereg(0x35, 8);
  for (i = 0; i < 8; i++) {
    writereg(0x36 + i, d[i]);
  }
  select();
  spi(0x81);
  release();
  return 1;
}
static void pads(uint8_t *a, uint8_t *b) {
  uint8_t i;
  *a = *b = 0;
  PORTC.OUTSET = PIN2_bm | PIN3_bm;
  _delay_us(12);
  PORTC.OUTCLR = PIN2_bm | PIN3_bm;
  _delay_us(6);
  for (i = 0; i < 8; i++) {
    if (!(PORTA.IN & PIN7_bm))
      *a |= 1 << i;
    if (!(PORTB.IN & PIN4_bm))
      *b |= 1 << i;
    PORTA.OUTCLR = PIN6_bm;
    PORTB.OUTCLR = PIN5_bm;
    _delay_us(6);
    PORTA.OUTSET = PIN6_bm;
    PORTB.OUTSET = PIN5_bm;
    _delay_us(6);
  }
}
int main(void) {
  uint8_t d[8] = {1, 0, 0, 0, 1, 0, 0, 0}, last0 = 0, last1 = 0, age = 50,
          tick = 0, online;
  _PROTECTED_WRITE(CLKCTRL.MCLKCTRLB, 0); /* 20 MHz; factory oscillator fuse */
  PORTB.OUTCLR = PIN2_bm | PIN3_bm;
  PORTB.DIRSET = PIN2_bm | PIN3_bm | PIN0_bm | PIN5_bm;
  PORTA.OUTSET = PIN4_bm | PIN6_bm;
  PORTA.DIRSET = PIN1_bm | PIN3_bm | PIN4_bm | PIN6_bm;
  PORTC.OUTCLR = PIN2_bm | PIN3_bm;
  PORTC.DIRSET = PIN2_bm | PIN3_bm;
  SPI0.CTRLA = SPI_ENABLE_bm | SPI_MASTER_bm | SPI_PRESC_DIV16_gc;
  SPI0.CTRLB = SPI_SSD_bm;
  _PROTECTED_WRITE(WDT.CTRLA, WDT_PERIOD_1KCLK_gc);
  online = init();
  for (;;) {
    _delay_ms(1);
    wdt_reset();
    if (age < 255)
      age++;
    if (++tick < 4)
      continue;
    tick = 0;
    if (!online) {
      standby();
      _delay_ms(100);
      online = init();
      d[4] = 1;
      continue;
    }
    if (readreg(0x2d) & 0x20) {
      standby();
      online = 0;
      continue;
    }
    pads(&d[2], &d[3]);
    if (age >= 10 && (d[4] || d[2] != last0 || d[3] != last1 || age >= 50)) {
      if (send(d)) {
        last0 = d[2];
        last1 = d[3];
        d[1]++;
        d[4] = 0;
        age = 0;
        PORTB.OUTTGL = PIN0_bm;
      }
    }
  }
}
