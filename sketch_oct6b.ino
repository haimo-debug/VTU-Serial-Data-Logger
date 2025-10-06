#include <SPI.h>
#include <SD.h>

// Set the CS pin to 10 as it's the default for the SD library
const int chipSelect = 10;

// Define the built-in LED pin
const int LED_PIN = 13; 

// Global string to hold the received message
String receivedMessage = "";

void setup() {
  // Set the LED pin as an OUTPUT
  pinMode(LED_PIN, OUTPUT); 

  // Initialize serial communication for debugging to 115200
  Serial.begin(115200);
  while (!Serial) {
    ; // Wait for the serial port to connect.
  }

}

void loop() {
  // Check if there is any data available from the Serial Monitor
  if (Serial.available() > 0) {
    // *** Activate the LED to indicate data reception ***
    digitalWrite(LED_PIN, HIGH); 
    
    char incomingChar = Serial.read();

    // 1. Check for the Carriage Return (CR) character
    if (incomingChar == '\r') {
      
      // 2. Check if the next available character is the Line Feed (LF) character
      if (Serial.peek() == '\n') {
        
        // 3. We've confirmed the <CR><LF> sequence!
        Serial.read(); // Consume the LF character
        
        // ** SAVE-TO-FILE LOGIC **
        File dataFile = SD.open("log.txt", FILE_WRITE);

        if (dataFile) {
          dataFile.println(receivedMessage); 
          dataFile.close();
          
        }
        
        // 4. Clear the string for the next message
        receivedMessage = ""; 
        
        // The LED will turn OFF at the end of loop()
      }
      // If CR without LF, treat as regular character
      else {
        receivedMessage += incomingChar;
      }
    }
    // 5. Append any other character (not '\r') to the string
    else {
      receivedMessage += incomingChar;
    }
  }

  // *** Deactivate the LED at the end of every loop iteration ***
  // This ensures the LED is only on for the short duration data is read.
  digitalWrite(LED_PIN, LOW); 
}