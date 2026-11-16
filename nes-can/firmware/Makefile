# Supply Microchip ATtiny_DFP gcc/dev/attiny1616 and include directories.
DFP ?= /opt/attiny
CC = avr-gcc
CFLAGS = -std=gnu11 -Os -Wall -Wextra -mmcu=attiny1616 -B$(DFP)/gcc/dev/attiny1616/ -I$(DFP)/include $(EXTRA_CFLAGS)
# Recompile when selecting loopback/listen-only through EXTRA_CFLAGS.
.PHONY: all FORCE
all: build/nes-can.hex
FORCE:
build/nes-can.elf: main.c FORCE
	mkdir -p build
	$(CC) $(CFLAGS) $< -o $@
	avr-size $@
build/nes-can.hex: build/nes-can.elf
	avr-objcopy -O ihex -R .eeprom $< $@
