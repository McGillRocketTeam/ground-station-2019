#define XTENDSERIAL Serial1
int RSSIPin = A0;
char incomingChar;
int RSSIdB;
void setup() {
  Serial.begin(38400);  //38400? or 19200?
  //enable cts and rts?
  XTENDSERIAL.attachRts(2);
  XTENDSERIAL.attachCts(18);
  XTENDSERIAL.begin(19200);
}
void loop() {
  if (XTENDSERIAL.available() > 0){
    char incomingChar = XTENDSERIAL.read();
    if (incomingChar == 'E'){
      RSSIdB = map(analogRead(RSSIPin), 0, 853, 0, 70) - 110; //563 (5) or 853 (3.3) need to check
      Serial.print(RSSIdB);
      Serial.print(",");
    }
    Serial.print(incomingChar);
  }
}