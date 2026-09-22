
# Unit 1 Summative: Motion Activated Sound and Light Source

## Overview

For this project I built a Motion Activated Sound and Light Source, a Arudino Uno device that uses a Ultrasonic Distance Sensor to figure out how close a is, and then reacts with different lights and sounds depending on that distance. If I were to put my hand farther or close the device reacts differently and changes what is it doing, making it feel like more of a interaction.

## The Process

### What It Built On

This project helped me build on my engineering and problem solving skills. The process of figuring out on how to take a sensor and make it into something that is responsive and fun to play with, instead of just a basic on and off switch. I wanted to make something that reacted differently based on the interaction.

### New Component

I used HC-SR04 ultrasonic distance sensor. I learned how to wire it and code it using Arduino tutorials online, also some help from AI along the way.

### What I tired

The hardest part for me throughout this project was getting the LEDs, buzzer, and the sensor to all work together at the same time without having errors with anything. At first some of the combinations of the code did not work for me and didn't run correctly. With the help of artifical intelligence, I was able to establish a clear code that made all of the components of the device work. Also, the use of tone and noTone got everything to run smoothly.

## Final Result

### Photos

<img width="626" height="792" alt="Screenshot 2026-09-17 at 1 35 54 PM" src="https://github.com/user-attachments/assets/0ff8364c-c1d1-4eb5-94dc-a7687c15e4dc" />

<img width="592" height="783" alt="image" src="https://github.com/user-attachments/assets/1c55d2de-9a80-4a6e-9913-08965a92c728" />


### Code

```cpp
// /*
 * HC-SR04 Two-Zone Sound Box
 *
 * FAR zone  (motion farther away): LED1 lights up, arcade laser sounds play
 * CLOSE zone (motion very close):  LED2 lights up, plays the ABC song melody
 */

const int trigPin = 9;
const int echoPin = 10;
const int buzzerPin = 12;
const int led1Pin = 11;   // "far" LED — arcade sounds
const int led2Pin = 6;    // "close" LED — ABC song

float duration, distance;

// Distance threshold (cm) — below this = "close", above = "far"
const int closeThreshold = 15;
const int maxRange = 50;

bool songPlayed = false; // so the song plays once per approach, not every loop

// ---- ABC Song melody (same tune as Twinkle Twinkle) ----
int abcNotes[] = {
  262, 262, 392, 392, 440, 440, 392,
  349, 349, 330, 330, 294, 294, 262
};
int abcDurations[] = {
  300, 300, 300, 300, 300, 300, 600,
  300, 300, 300, 300, 300, 300, 600
};
int abcLength = 14;

void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(buzzerPin, OUTPUT);
  pinMode(led1Pin, OUTPUT);
  pinMode(led2Pin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  // --- Read distance ---
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH, 30000);
  distance = (duration * 0.0343) / 2;

  // Nothing detected / out of range -> everything off
  if (duration == 0 || distance > maxRange) {
    noTone(buzzerPin);
    digitalWrite(buzzerPin, LOW);
    digitalWrite(led1Pin, LOW);
    digitalWrite(led2Pin, LOW);
    songPlayed = false;
    delay(50);
    return;
  }

  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  if (distance <= closeThreshold) {
    // ---- CLOSE ZONE: LED2 + ABC song ----
    digitalWrite(led1Pin, LOW);
    digitalWrite(led2Pin, HIGH);

    if (!songPlayed) {
      playABC();
      songPlayed = true;
    }
  } else {
    // ---- FAR ZONE: LED1 + arcade laser sound ----
    digitalWrite(led2Pin, LOW);
    digitalWrite(led1Pin, HIGH);
    songPlayed = false; // reset so song can play again next time hand gets close

    int freq = map((int)distance, maxRange, closeThreshold, 150, 900);
    playTone(freq, 40);
    delay(30);
  }
}

// ---- Core tone generator (square wave, works on active or passive buzzers) ----
void playTone(int frequency, int durationMs) {
  if (frequency <= 0) return;
  long periodMicros = 1000000L / frequency;
  long halfPeriod = periodMicros / 2;
  long cycles = (durationMs * 1000L) / periodMicros;

  for (long i = 0; i < cycles; i++) {
    digitalWrite(buzzerPin, HIGH);
    delayMicroseconds(halfPeriod);
    digitalWrite(buzzerPin, LOW);
    delayMicroseconds(halfPeriod);
  }
}

// ---- Plays the full ABC song melody, flashing LED2 with each note ----
void playABC() {
  for (int i = 0; i < abcLength; i++) {
    digitalWrite(led2Pin, HIGH);
    playTone(abcNotes[i], abcDurations[i] * 0.9);
    digitalWrite(led2Pin, LOW);
    delay(abcDurations[i] * 0.1);
  }
}
```

## Technical Tidbit

The HC-SR04 ultrasonic distance sensor measures distance by sending out sound waves while measuring how long it takes for those waves to bounce back from an object. The sensor has two silver cylinders, these cylinders are the transmitter and receiver that allow the sensor to measure the distance. The sensor is overall connceted to the Arduino Uno. If you refer to the picture of my device, the orange and blue wires connect the ultrasonic sensor to digital pins on the Arduino. The Arduino sends a electrical singal through the Trig pin. Overall telling the sensor to send out a burst of sound at about 40kHz, which is above the area that humans can hear. 

## Peer Support

There was times where I recived support from my peers. For example, at the beginning of the project when everyone was building their devices, me and my peer were working together unaware that it was an indidviudal project. After we knew this we did not panic, we simply helped eachother build another model so we can equally distribute our work. We both suppported eachother in a positive way overall helping us with the final product of our project.  

## Use-Case Reflection

This device could be useful to someone who needs to know if something is nearby without being able to hear or be able to see it. At the moment, my device only can detect movement and how far it is, it can't tell the difference between different movments like a hand wave, an object, or someone walking by. To make it useful for real life situations, I would need to find out a way to filter unintentional, maybe by add a small camera or studying the distance patterns or movement patterns. If I kept developing this idea I would rely on wiring. Since adding more complex systems and trigger systems, this would overall mean more complex wiring and foucus on specfic components. Even when building this, this was a struggle I faced through the building process. 
