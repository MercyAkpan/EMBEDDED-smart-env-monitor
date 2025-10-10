// /**
//  * @file main.cpp
//  * @brief MQ135 Calibration to determine RZERO value
//  * @note Run this outdoors in clean air for 12-24 hours
//  * @note Run this at least 20 minutes before using in a new environment
//  */

// #include <Arduino.h>
// #include "MQ135.h"

// // ============================================================================
// // CONFIGURATION - ADJUST THESE VALUES
// // ============================================================================

// // Uncomment this line to enable calibration mode
// #define CALIBRATE

// // Replace with YOUR measured RLOAD (in kOhms)
// // Example: If you measured 1000 ohms, use 1.0
// // Example: If you measured 1720 ohms, use 1.72
// #define RLOAD 1.0  // ← CHANGE THIS to your measured value in kOhms

// // Pin connected to MQ135 A0 (through voltage divider)
// #define MQ135_PIN 34

// // Voltage divider ratio (for your 5.1kΩ + 6.8kΩ setup)
// // The library expects 0-5V, but ESP32 sees 0-2.86V
// // We'll compensate for this in the reading
// #define VOLTAGE_DIVIDER_RATIO (5.0 / 2.86)  // 1.748

// // ============================================================================
// // GLOBAL OBJECTS
// // ============================================================================

// MQ135 mq135_sensor(MQ135_PIN);

// // ============================================================================
// // SETUP
// // ============================================================================

// void setup() {
//   Serial.begin(115200);
//   delay(2000);  // Wait for serial monitor to connect
  
//   Serial.println("\n========================================");
//   Serial.println("MQ135 Calibration Mode");
//   Serial.println("========================================");
//   Serial.println("Instructions:");
//   Serial.println("1. Place sensor OUTDOORS in fresh air");
//   Serial.println("2. Let sensor warm up for 12-24 hours");
//   Serial.println("3. Monitor RZERO until it stabilizes");
//   Serial.println("4. Copy the stable RZERO value");
//   Serial.println("========================================\n");
  
//   Serial.print("RLOAD configured: ");
//   Serial.print(RLOAD);
//   Serial.println(" kOhms");
  
//   Serial.print("Voltage divider ratio: ");
//   Serial.println(VOLTAGE_DIVIDER_RATIO);
  
//   Serial.println("\nWaiting 20 seconds for sensor warm-up...\n");
//   delay(20000);  // Initial warm-up
// }

// // ============================================================================
// // LOOP - CALIBRATION MODE
// // ============================================================================

// void loop() {
//   #ifdef CALIBRATE
//     // Read raw ADC value
//     int rawADC = analogRead(MQ135_PIN);
    
//     // Convert to voltage (ESP32 12-bit ADC: 0-4095 = 0-3.3V)
//     float voltage = (rawADC / 4095.0) * 3.3;
    
//     // Compensate for voltage divider to get actual sensor voltage
//     float actualVoltage = voltage * VOLTAGE_DIVIDER_RATIO;
    
//     // Calculate sensor resistance (RS)
//     // Formula: RS = [(VC × RL) / VOUT] - RL
//     // Where: VC = 5V (supply), VOUT = sensor output, RL = RLOAD
//     float resistance = ((5.0 * RLOAD) / actualVoltage) - RLOAD;
    
//     // Calculate RZERO (resistance in clean air)
//     // The library uses a default atmospheric CO2 of 399.13 ppm
//     float rzero = mq135_sensor.getRZero();
    
//     // Alternative manual calculation
//     // RZERO = RS / [(PPM/PARA)^(1/PARB)]
//     // For CO2: PARA=116.6020682, PARB=-2.769034857
//     float atmCO2 = 399.13;  // Atmospheric CO2 in ppm
//     float rzeroManual = resistance / pow((atmCO2 / 116.6020682), (1.0 / -2.769034857));
    
//     // Display results
//     Serial.println("─────────────────────────────────────");
//     Serial.print("Raw ADC: ");
//     Serial.print(rawADC);
//     Serial.print(" | Voltage (ESP32): ");
//     Serial.print(voltage, 3);
//     Serial.println("V");
    
//     Serial.print("Actual Sensor Voltage: ");
//     Serial.print(actualVoltage, 3);
//     Serial.println("V");
    
//     Serial.print("Sensor Resistance (RS): ");
//     Serial.print(resistance, 2);
//     Serial.println(" kOhms");
    
//     Serial.print("RZERO (Library): ");
//     Serial.print(rzero, 2);
//     Serial.println(" kOhms");
    
//     Serial.print("RZERO (Manual): ");
//     Serial.print(rzeroManual, 2);
//     Serial.println(" kOhms");
    
//     Serial.println("─────────────────────────────────────\n");
    
//     // Check if sensor is warmed up
//     if (resistance < 1.0) {
//       Serial.println("⚠️  WARNING: Sensor may still be warming up (RS too low)");
//     } else if (rzero < 10.0 || rzero > 100.0) {
//       Serial.println("⚠️  WARNING: RZERO outside typical range (10-100 kOhms)");
//       Serial.println("    Check RLOAD value and sensor placement");
//     } else {
//       Serial.println("✅ RZERO looks reasonable - continue monitoring");
//     }
    
//   #else
//     Serial.println("ERROR: Calibration mode not enabled!");
//     Serial.println("Uncomment '#define CALIBRATE' in code");
//   #endif
  
//   delay(10000);  // Update every 10 seconds
// }