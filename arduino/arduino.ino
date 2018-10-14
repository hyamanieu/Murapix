#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif

#define PIN            A0
#define NUMPIXELS      348
#define BRIGHTNESS 100
Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
int delayval = 10;
int values[] = { 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 102, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 68, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };


void setup() {
#if defined (__AVR_ATtiny85__)
  if (F_CPU == 16000000) clock_prescale_set(clock_div_1);
#endif
  // End of trinket special code

  pixels.setBrightness(BRIGHTNESS);
  pixels.begin(); // This initializes the NeoPixel library.

  //Serial.begin(9600);
}

void clean(int a, int b) {
  for(int i=a;i<b;i++) {
    pixels.setPixelColor(i, pixels.Color(0,0,0));
  }
  pixels.show();
}

void setscore1(int s) {
  int jj = 7 * s;
  for(int i=288;i<288+jj;i++) {
    pixels.setPixelColor(i, pixels.Color(255,0,0));
  }
  for(int i=288+jj;i<318;i++) {
    pixels.setPixelColor(i, pixels.Color(0,0,0));
  }
  pixels.show();
}

void setscore2(int s) {
  int jj = 7 * s;
  for(int i=348-1;i>=348-jj;i--) {
    pixels.setPixelColor(i, pixels.Color(0,255,0));
  }
  for(int i=318;i<318+(30-jj);i++) {
    pixels.setPixelColor(i, pixels.Color(0,0,0));
  }
  pixels.show();
}

void resetGameState() {
  int r, g, b;
  for(int i=0;i<NUMPIXELS/2 - 30;i++) {
    r = (values[i] & 0x01)*255;
    g = (values[i] & 0x02)*255;
    b = (values[i] & 0x04)*255;
    pixels.setPixelColor(i*2, pixels.Color(r,g,b));
    r = (values[i] & 0x10)*255;
    g = (values[i] & 0x20)*255;
    b = (values[i] & 0x40)*255;
    pixels.setPixelColor(i*2+1, pixels.Color(r,g,b));
    
  }
  pixels.show();
  delay(1000);
}

void p1progress(int p) {
  int offset = p * 36;
  clean(offset,offset + 36);
}

void p2progress(int p) {
  int offset = p * 36;
  clean(288 - offset - 36, 288 - offset);
}

void scoreBlink() {
  clean(288, 348);
  delay(200);
  setscore1(4);
  delay(300);
}

void game() {
  resetGameState();
  
  //clean(0,36);
  p1progress(0);
  delay(250);

  p2progress(0);
  //clean(144,180);
  delay(250);

  p1progress(1);
  //clean(36,72);
  delay(1000);
  
  p1progress(2);
  //clean(72,108);
  delay(250);
  
  p2progress(1);
  //clean(180,216);
  delay(500);

  p1progress(3);
}


void game3() {
  resetGameState();
  p2progress(0);
  delay(100);

  p1progress(0);
  delay(250);

  p2progress(1);
  delay(150);
  
  p1progress(1);
  delay(250);
  
  p1progress(2);
  delay(100);

  p2progress(2);
  delay(300);

  p1progress(3);
}


void game2() {
  resetGameState();
  
  p1progress(0);
  delay(250);
 p2progress(0);
  delay(250);
   p2progress(1);
  delay(500);
   p1progress(1);
  delay(250);
  p2progress(2);
  delay(100);
   p1progress(2);
  delay(250);
  p2progress(3);
}


void loop() {
  int r, g, b, value;
    
  for(int i=0;i<NUMPIXELS/2;i++) {
    r = (values[i] & 0x01)*255;
    g = (values[i] & 0x02)*255;
    b = (values[i] & 0x04)*255;
    pixels.setPixelColor(i*2, pixels.Color(r,g,b));
    r = (values[i] & 0x10)*255;
    g = (values[i] & 0x20)*255;
    b = (values[i] & 0x40)*255;
    pixels.setPixelColor(i*2+1, pixels.Color(r,g,b));
    
  }
  pixels.show();
  delay(3000);

  game();
  setscore1(1);
  delay(2000);

  game3();
  setscore1(2);
  delay(2000);

  game2();
  setscore2(1);
  delay(2000);

  game();
  setscore1(3);
  delay(2000);

  game2();
  setscore2(2);
  delay(2000);

  game3();
  setscore1(4);

  setscore2(4);
  while (true) {
    scoreBlink();
  }
}
