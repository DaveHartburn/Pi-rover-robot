// Basic Pi -> Pico communication test in C++
// This part to be run on the pico
// UART reference at https://raspberrypi.github.io/pico-sdk-doxygen/group__hardware__uart.html

#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/uart.h"

// Define the UART and the standard UART pins
#define UART uart0
#define BAUD_RATE 115200
#define UART_TX_PIN 0
#define UART_RX_PIN 1

#define LED LED_BUILTIN

void setup() {
  Serial.begin(115200);
  Serial.println("Pico UART test");

  // Initialise the UART
  uart_init(UART, BAUD_RATE);
  // Convert line feeds to carriage returns to avoid
  // hello
  //      hello
  //           hello
  uart_set_translate_crlf(UART, true);
  // The first few characters are often corrupt. Send two lines to indicate start
  uart_puts(UART, "INIT\n\n");
  uart_puts(UART, "Hello from Pico\n");
  
  // Set the TX and RX pins by using the function select on the GPIO
  // Set datasheet for more information on function select
  gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
  gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);

  // Init the onboard LED
  gpio_init(LED);
  gpio_set_dir(LED, GPIO_OUT);
}

bool l=0;
char msgOut[255];
char msgIn[255];

void loop() {
  // Check for input
  if(uart_is_readable(UART)) {
    Serial.println("Data received");
    uart_puts(UART, "Data received\n");
    int i=0;
    while (uart_is_readable(UART) && i<255) {
      char ch = uart_getc(UART);
      msgIn[i++]=ch;
      Serial.print('.');
    }
    Serial.print("\n");
    Serial.print("Message in:");
    Serial.print(msgIn);
    uart_puts(UART,"Message in:");
    uart_puts(UART,msgIn);
  }
  // Toggle LED value
  l=!l;
  gpio_put(LED, l);

  // Prepare outgoing message
  sprintf(msgOut, "LED status = %d\n", l);

  // To standard serial console (string has new line)
  Serial.print(msgOut);
  // Send a UART string
  uart_puts(UART, msgOut);
  delay(500);

}
