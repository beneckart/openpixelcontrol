platform=$(shell uname)

RGB_LIB_DISTRIBUTION=matrix
RGB_INCDIR=$(RGB_LIB_DISTRIBUTION)/include
RGB_LIBDIR=$(RGB_LIB_DISTRIBUTION)/lib
RGB_LIBRARY_NAME=rgbmatrix
RGB_LIBRARY=$(RGB_LIBDIR)/lib$(RGB_LIBRARY_NAME).a
LDFLAGS+=-L$(RGB_LIBDIR) -l$(RGB_LIBRARY_NAME) -lrt -lm -lpthread

# was -02
CFLAGS=-O3 -g
ifeq ($(platform),Darwin)
  ALL=bin/rgbmatrix_server bin/rgbmatrix_vsync_server bin/rgbmatrix_threaded_server bin/dummy_client bin/dummy_server bin/gl_server
  GL_OPTS=-framework OpenGL -framework GLUT -Wno-deprecated-declarations
else ifeq ($(platform),Linux)
  ALL=bin/rgbmatrix_server bin/rgbmatrix_vsync_server bin/rgbmatrix_threaded_server bin/dummy_client bin/dummy_server bin/tcl_server bin/apa102_server bin/ws2801_server bin/lpd8806_server bin/gl_server
  GL_OPTS=-lGL -lglut -lGLU -lm
endif

all: $(ALL)

clean:
	rm -rf bin/*
	
# (FYI: Make sure, there is a TAB-character in front of the $(MAKE))
$(RGB_LIBRARY): 
	$(MAKE) -C $(RGB_LIBDIR)
	
bin/rgbmatrix_server: src/rgbmatrix_server.cc src/opc_server.c $(RGB_LIBRARY)
	mkdir -p bin
	$(CXX) ${CFLAGS} -I$(RGB_INCDIR) $^ -o $@ $(LDFLAGS)

bin/rgbmatrix_vsync_server: src/rgbmatrix_vsync_server.cc src/opc_server.c $(RGB_LIBRARY)
	mkdir -p bin
	$(CXX) ${CFLAGS} -I$(RGB_INCDIR) $^ -o $@ $(LDFLAGS)

bin/rgbmatrix_threaded_server: src/rgbmatrix_threaded_server.cc src/opc_server.c $(RGB_LIBRARY)
	mkdir -p bin
	$(CXX) ${CFLAGS} -I$(RGB_INCDIR) $^ -o $@ $(LDFLAGS)

bin/dummy_client: src/dummy_client.c src/opc_client.c
	mkdir -p bin
	gcc ${CFLAGS} -o $@ $^

bin/dummy_server: src/dummy_server.c src/opc_server.c
	mkdir -p bin
	gcc ${CFLAGS} -o $@ $^

bin/tcl_server: src/tcl_server.c src/opc_server.c src/spi.c src/cli.c
	mkdir -p bin
	gcc ${CFLAGS} -o $@ $^

bin/apa102_server: src/apa102_server.c src/opc_server.c src/spi.c src/cli.c
	mkdir -p bin
	gcc ${CFLAGS} -o $@ $^

bin/ws2801_server: src/ws2801_server.c src/opc_server.c src/spi.c src/cli.c
	mkdir -p bin
	gcc ${CFLAGS} -o $@ $^

bin/lpd8806_server: src/lpd8806_server.c src/opc_server.c src/spi.c src/cli.c
	mkdir -p bin
	gcc ${CFLAGS} -o $@ $^

bin/gl_server: src/gl_server.c src/opc_server.c src/cJSON.c
	mkdir -p bin
	gcc ${CFLAGS} -o $@ $^ $(GL_OPTS)
