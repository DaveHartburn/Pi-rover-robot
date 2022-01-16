// Multithredded comms test
#include <stdio.h>
#include "pico/stdlib.h"
#include "pico/multicore.h"
#include "hardware/uart.h"

// Define the UART and the standard UART pins
#define UART uart0
#define BAUD_RATE 115200
#define UART_TX_PIN 0
#define UART_RX_PIN 1
#define BUFSIZE 255
#define R_TIMEOUT 1500

#define LED LED_BUILTIN
int l=0;        // Tracks LED status
#define numSensors 6
int sensorData[numSensors];
int sensorInterval = 500;
bool checkSensors=true;

void sensorThread() {
  // Sensor thread, this will simulate the sensors by filling the array with
  // random values

  int nextCheck=0;
  while(checkSensors) {
    if(millis()>nextCheck) {
      //toggleLED();        // Uncomment for activity debugging
      for(int i=0; i<numSensors; i++) {
        sensorData[i]=random(255);
      }
      nextCheck=millis()+sensorInterval;
    }
  }
}

void toggleLED() {
  gpio_put(LED, l);
  l=!l;
}

void receiveUart( char *inarr, int maxIn) {
  // Receive data from UART. Data should terminate with end of line
  // or a timeout or a full buffer
  int i=0;
  bool terminateR=false;
  int long timeout=millis()+R_TIMEOUT;
  while(!terminateR) {
    if(uart_is_readable(UART)) {
      char ch = uart_getc(UART);
      // Strip newline
      if(ch!='\n' && ch!='\r') {
        inarr[i++]=ch;
      } else {
        // Also terminate receive on new line
        terminateR=true;
      }
    }
    // Terminate receive conditions
    if(millis()>timeout) {
      terminateR=true;
    }
    if(i==maxIn) {
      terminateR;
    }
  }
  // Null terminate string
  inarr[i]=0;
}

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

  // Turn on LED and wait 5 seconds for us to open the serial monitor
  gpio_put(LED, 1);
  delay(5000);
  Serial.println("Pico multithredding test");
  Serial.println("Starting sensorThread");
  multicore_launch_core1(sensorThread);
  Serial.println("Started");
  toggleLED();
}

char msgIn[BUFSIZE];
char msgOut[BUFSIZE];

void loop() {
  if(uart_is_readable(UART)) {
    receiveUart(msgIn, BUFSIZE);
    Serial.print("Incoming message: ");
    Serial.println(msgIn);
    if(!strcmp(msgIn, "dataRequest")) {
      // Compose JSON string manually (libraries exist for more complicated)
      strcpy(msgOut,"'[");
      char tmpStr[10];
      for(int i=0;i<numSensors;i++) {
        sprintf(tmpStr, "%d", sensorData[i]);
        strcat(msgOut,tmpStr);
        if(i!=numSensors-1) {
          strcat(msgOut, ", ");
        }
      }
      strcat(msgOut, "]'\n");
      // Send data
      Serial.print("Sending data: ");
      Serial.print(msgOut);
      uart_puts(UART,msgOut);
      // End of if dataRequest
    } else if (!strcmp(msgIn, "toggleLED")) {
      toggleLED();
    } else if (!strcmp(msgIn, "quit")) {
      checkSensors=false;
      uart_puts(UART, "Quitting thread\n");
    } else if (!strcmp(msgIn, "start")) {
      // Start the other thread
      if(checkSensors==true) {
        uart_puts(UART, "Sensor thread already running\n");
      } else {
        // Start sensor stread
        checkSensors=true;
        Serial.println("Starting sensor thread");
        multicore_reset_core1();
        multicore_launch_core1(sensorThread);
        Serial.println("Started sensor thread");
        uart_puts(UART, "Launched sensor thread\n");
      }
    }
    // Do nothing with other messages

  }
}
