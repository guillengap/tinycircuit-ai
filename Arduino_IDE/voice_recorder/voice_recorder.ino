#include "DFRobot_VoiceRecorder.h"
#define VOICE_ADDRESS  (0x30)
const int BUTTON_PIN1 = 2; // Resistor
const int BUTTON_PIN2 = 3; // Capacitor
const int BUTTON_PIN3 = 4; // Transistor

DFRobot_VoiceRecorder_I2C voicerecorder(&Wire, VOICE_ADDRESS);

void play(void)
{
  // release the button
  if(digitalRead(BUTTON_PIN1)==HIGH)
  {
    voicerecorder.setVoiceNumber(VOICE_NUMBER_4); // Select Audio NO.1 = RESISTOR
    voicerecorder.playVoiceStart();
    Serial.println("play recording");
    for (int8_t n = 22; n > 0; n--){
      Serial.println(n);
      delay(500);
    }
    //playing=true;
  }

  else if(digitalRead(BUTTON_PIN2)==HIGH)
  {
    voicerecorder.setVoiceNumber(VOICE_NUMBER_5); // Select Audio NO.2 = CAPACITOR
    voicerecorder.playVoiceStart();
    Serial.println("play recording");
    for (int8_t n = 22; n > 0; n--){
      Serial.println(n);
      delay(500);
    }
  }

  else if(digitalRead(BUTTON_PIN3)==HIGH)
  {
    voicerecorder.setVoiceNumber(VOICE_NUMBER_6); // Select Audio NO.3 = TRANSISTOR
    voicerecorder.playVoiceStart();
    Serial.println("play recording");
    for (int8_t n = 22; n > 0; n--){
      Serial.println(n);
      delay(500);
    }
  }

  else
  {
    Serial.println("none");
      delay(500);    
  }

}

void setup()
{
  pinMode(BUTTON_PIN1,INPUT);
  pinMode(BUTTON_PIN2,INPUT);
  pinMode(BUTTON_PIN3,INPUT);  
  Serial.begin(115200);
  while (voicerecorder.begin() != 0)
  {
    Serial.println("i2c device number error!");
    delay(1000);
  }
  Serial.println("i2c connect success!");
}

void loop()
{
//  record();
  play();
}