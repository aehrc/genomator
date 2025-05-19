CC = g++ -Wall -O5 -DDEBUG
#CC = g++ -Wall -g #-DUPDEBUG  -ltermcap
HEADERS = SatSolver.h IntPool.h
OBJS = SatSolver.o main.o IntPool.o

tinicard: $(OBJS) 
	$(CC) $(OBJS) -o tinicard  

$(OBJS): $(HEADERS) Makefile

.cpp.o: 
	$(CC) -c $< 

clean:
	rm *.o tinicard
