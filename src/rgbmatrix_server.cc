//https://github.com/hzeller/rpi-rgb-led-matrix/blob/master/examples-api-use/minimal-example.cc

//

#include <math.h>
#include <signal.h>
#include <stdio.h>
#include <time.h>
#include <unistd.h>

//#include <stdio.h>
//#include <stdlib.h>
//#include <signal.h>

#include "led-matrix.h"
#include "opc.h"

using rgb_matrix::GPIO;
using rgb_matrix::RGBMatrix;
using rgb_matrix::Canvas;

Canvas *canvas;

volatile bool interrupt_received = false;
static void InterruptHandler(int signo) {
  interrupt_received = true;
}

void handler(uint8_t channel, uint16_t count, pixel* pixels) {
  int i = 0;
  int x = 0;
  int y = 0;
  //printf("-> channel %d: %d pixel%s\n", channel, count, count == 1 ? "" : "s");
  
  //canvas->Clear();
  //canvas->Fill(0, 0, 0);
  
  // expect a full frame each time
  // rgbmatrix data payload should be 64*64*3 = 12288 bytes
  if(count < 4000) return; // bad data?

  for (i = 0; i < count; i++) {
    x = i % canvas->width();
    y = i / canvas->width();
    if (interrupt_received)
      return;
    canvas->SetPixel(x, y, pixels[i].r, pixels[i].g, pixels[i].b);
  }
  
  /*for (int y = 0; y < canvas->height(); y++) {
    for (int x = 0; x < canvas->width(); x++) {
      i = y * canvas->width() + x;
      canvas->SetPixel(x, y, pixels[i].r, pixels[i].g, pixels[i].b);
    }
  }*/
  
  //usleep(1 * 1000);  // wait a little to slow down things.
  
}

  
int main(int argc, char *argv[]) {
  uint16_t port = 7890; //argc > 1 ? atoi(argv[1]) : OPC_DEFAULT_PORT;
   
  RGBMatrix::Options defaults;
  defaults.hardware_mapping = "adafruit-hat";  // or e.g. "adafruit-hat"
  defaults.rows = 64;
  defaults.cols = 64;
  defaults.chain_length = 1;
  defaults.parallel = 1;
  defaults.show_refresh_rate = false;
  canvas = rgb_matrix::CreateMatrixFromFlags(&argc, &argv, &defaults);
  if (canvas == NULL)
    return 1;

  //canvas->SetBrightness(10);

  // It is always good to set up a signal handler to cleanly exit when we
  // receive a CTRL-C for instance. The DrawOnCanvas() routine is looking
  // for that.
  signal(SIGTERM, InterruptHandler);
  signal(SIGINT, InterruptHandler);
  
  opc_source s = opc_new_source(port);
  while (s >= 0) {
    opc_receive(s, handler, 5000); 
    if (interrupt_received)
      return 0;
  }
  
  canvas->Clear();
  delete canvas;

  return 0;
}