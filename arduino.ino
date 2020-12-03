//
//18B20 sense pin connected to pin 2 of arduino (with 4.7K pullup), 5v and gnd supplied from arduino
//FDC1004 connected to SCL-SDA pins of arduino,  5v and gnd supplied from arduino uno
//FDC1004 protocentral breakout that I am using already has bi-di level shifter, so compatiable with 5V
//

#include <Wire.h>
#include <Protocentral_FDC1004.h>
#include "LowPower.h"
#include <OneWire.h>
#include <DallasTemperature.h>

#define UPPER_BOUND  0X4000                 // max readout capacitance
#define LOWER_BOUND  (-1 * UPPER_BOUND)
#define CHANNEL 0                          // channel to be read
#define MEASURMENT 0                       // measurment channel
#define CHANNEL1 1                          // channel to be read

// Data wire is plugged into port 2 on the Arduino
#define ONE_WIRE_BUS 2
#define TEMPERATURE_PRECISION 9

// Setup a oneWire instance to communicate with any OneWire devices (not just Maxim/Dallas temperature ICs)
OneWire oneWire(ONE_WIRE_BUS);

// Pass our oneWire reference to Dallas Temperature.
DallasTemperature sensors(&oneWire);

// arrays to hold device addresses
DeviceAddress temp1 = { 0x28, 0xAA, 0x6C, 0x04, 0x53, 0x14, 0x01, 0xA5 };
DeviceAddress temp2 = { 0x28, 0xAA, 0x12, 0x2A, 0x53, 0x14, 0x01, 0x0F };
DeviceAddress temp3 = { 0x28, 0x0F, 0x05, 0x3D, 0x05, 0x00, 0x00, 0x08 };
DeviceAddress temp4 = { 0x28, 0xAF, 0x58, 0x3C, 0x05, 0x00, 0x00, 0xA2 };


int capdac = 0;
char result[100];

FDC1004 FDC;

void setup()
{
  Wire.begin();         //i2c begin
  Serial.begin(115200); // serial baud rate
  // Start up the DS18B20 library
  sensors.begin();
  if (!sensors.getAddress(temp1, 0)) Serial.println("Unable to find address for Device 0");
  if (!sensors.getAddress(temp2, 1)) Serial.println("Unable to find address for Device 1");
  if (!sensors.getAddress(temp3, 2)) Serial.println("Unable to find address for Device 2");
  if (!sensors.getAddress(temp4, 3)) Serial.println("Unable to find address for Device 3");
  sensors.setResolution(temp1, TEMPERATURE_PRECISION);
  sensors.setResolution(temp2, TEMPERATURE_PRECISION);
  sensors.setResolution(temp3, TEMPERATURE_PRECISION);
  sensors.setResolution(temp4, TEMPERATURE_PRECISION);
}

void printTemperature(DeviceAddress deviceAddress)
{
  float tempC = sensors.getTempC(deviceAddress);
  if(tempC == DEVICE_DISCONNECTED_C) 
  {
    Serial.println("Error: Could not read temperature data");
    return;
  }
  //Serial.print("Temp C: ");
  Serial.print(tempC);
  Serial.print(",");
}



void loop()
{
  // send each output seperated by commas
  LowPower.idle(SLEEP_8S, ADC_OFF, TIMER2_OFF, TIMER1_OFF, TIMER0_OFF, 
                SPI_OFF, USART0_OFF, TWI_OFF);
  
  //Serial.print("Requesting temperatures...");
  sensors.requestTemperatures();
  //Serial.println("DONE");
  printTemperature(temp1);
  printTemperature(temp2);
  printTemperature(temp3);
  printTemperature(temp4);
    

  FDC.configureMeasurementSingle(MEASURMENT, CHANNEL, capdac);
  FDC.triggerSingleMeasurement(MEASURMENT, FDC1004_100HZ);

  //wait for completion
  delay(25);
  uint16_t value[2];
  if (! FDC.readMeasurement(MEASURMENT, value))
  {
    int16_t msb = (int16_t) value[0];
    int32_t capacitance = ((int32_t)457) * ((int32_t)msb); //in attofarads
    capacitance /= 1000;   //in femtofarads
    capacitance += ((int32_t)3028) * ((int32_t)capdac);

    Serial.print((((float)capacitance/1000)),4);
    Serial.print(",");
    //Serial.print("\n");

    if (msb > UPPER_BOUND)               // adjust capdac accordingly
  {
      if (capdac < FDC1004_CAPDAC_MAX)
    capdac++;
    }
  else if (msb < LOWER_BOUND)
  {
      if (capdac > 0)
    capdac--;
    }
  }
  FDC.configureMeasurementSingle(MEASURMENT, CHANNEL1, capdac);
  FDC.triggerSingleMeasurement(MEASURMENT, FDC1004_100HZ);

  //wait for completion
  delay(25);
  //uint16_t value[2];
  if (! FDC.readMeasurement(MEASURMENT, value))
  {
    int16_t msb = (int16_t) value[0];
    int32_t capacitance = ((int32_t)457) * ((int32_t)msb); //in attofarads
    capacitance /= 1000;   //in femtofarads
    capacitance += ((int32_t)3028) * ((int32_t)capdac);

    Serial.print((((float)capacitance/1000)),4);
    //Serial.print(",");
    Serial.print("\n");

    if (msb > UPPER_BOUND)               // adjust capdac accordingly
  {
      if (capdac < FDC1004_CAPDAC_MAX)
    capdac++;
    }
  else if (msb < LOWER_BOUND)
  {
      if (capdac > 0)
    capdac--;
    }
  }
  //delay(500);
  Serial.flush();
  //
}
