/*
 * Arduino Printer Bridge
 * Receives print data from Raspberry Pi and forwards to printer
 */

#include <ArduinoJson.h>  // Make sure to install this library

// Configure based on your printer
// If using a thermal printer with hardware serial
#include <SoftwareSerial.h>
SoftwareSerial printerSerial(10, 11); // RX, TX

// Buffer for receiving data
const int BUFFER_SIZE = 256;
byte dataBuffer[BUFFER_SIZE];

// Print job metadata
struct PrintJob {
  long imageSize;
  int width;
  int height;
  bool inProgress;
  long bytesReceived;
};

PrintJob currentJob;

void setup() {
  // Initialize serial connection to Raspberry Pi
  Serial.begin(115200);
  
  // Initialize printer serial connection
  printerSerial.begin(9600); // Adjust baud rate to match your printer
  
  // Clear any existing jobs
  resetPrintJob();
  
  // Wait for all serial ports to initialize
  delay(1000);
  
  Serial.println("Arduino Printer Bridge Ready");
}

void loop() {
  // Check if there's data available from Raspberry Pi
  if (Serial.available() > 0) {
    if (!currentJob.inProgress) {
      // Try to parse a command
      String command = Serial.readStringUntil('\n');
      processCommand(command);
    } else {
      // We're in the middle of receiving an image, read chunks
      int bytesAvailable = Serial.available();
      int bytesToRead = min(bytesAvailable, BUFFER_SIZE);
      
      // Read data into buffer
      int bytesRead = Serial.readBytes(dataBuffer, bytesToRead);
      
      // Forward data to printer
      printerSerial.write(dataBuffer, bytesRead);
      
      // Update bytes received count
      currentJob.bytesReceived += bytesRead;
      
      // Send acknowledgment back to Raspberry Pi
      Serial.println("ACK");
      
      // Check if job is complete
      if (currentJob.bytesReceived >= currentJob.imageSize) {
        // Job completed
        Serial.println("PRINT_COMPLETE");
        resetPrintJob();
      }
    }
  }
}

void processCommand(String commandStr) {
  // Parse JSON command
  StaticJsonDocument<512> doc;
  DeserializationError error = deserializeJson(doc, commandStr);
  
  if (error) {
    Serial.println("ERROR_INVALID_JSON");
    return;
  }
  
  // Check if it's a print command
  const char* command = doc["command"];
  if (strcmp(command, "PRINT") == 0) {
    // Extract print job details
    currentJob.imageSize = doc["image_size"];
    currentJob.width = doc["width"];
    currentJob.height = doc["height"];
    currentJob.inProgress = true;
    currentJob.bytesReceived = 0;
    
    // Initialize printer if needed
    initializePrinter();
    
    // Apply any printer settings passed in the command
    applyPrinterSettings(doc);
    
    // Let Raspberry Pi know we're ready to receive image data
    Serial.println("READY");
  } else {
    // Unknown command
    Serial.println("ERROR_UNKNOWN_COMMAND");
  }
}

void resetPrintJob() {
  currentJob.imageSize = 0;
  currentJob.width = 0;
  currentJob.height = 0;
  currentJob.inProgress = false;
  currentJob.bytesReceived = 0;
}

void initializePrinter() {
  // Initialize printer
  // This depends on your printer type and model
  
  // Example for typical thermal printer initialization:
  // Wake up the printer
  printerSerial.write(27);  // ESC
  printerSerial.write(64);  // @
  delay(50);
  
  // Set printer mode
  printerSerial.write(27);  // ESC
  printerSerial.write(33);  // !
  printerSerial.write(0);   // Normal mode
  delay(50);
}

void applyPrinterSettings(JsonDocument& settings) {
  // Apply various printer settings based on what's provided in the command
  // This is heavily dependent on your specific printer model and requirements
  
  // Example of setting print density for thermal printers
  if (settings.containsKey("density")) {
    int density = settings["density"];
    printerSerial.write(27);     // ESC
    printerSerial.write(55);     // 7
    printerSerial.write(density); // Density value
    delay(50);
  }
  
  // Add other settings as needed for your specific printer
}
