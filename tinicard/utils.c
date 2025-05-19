#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>

char skip_to_new_line(FILE* f) {
	char c;
	do {
		c = getc(f);
	} while ((c!=EOF) && (c!='\n'));
	ungetc(c,f);
	return c;
}
char skip_whitespace(FILE* f) {
	char c;
	do {
		c = getc(f);
	} while (isspace(c));
	ungetc(c,f);
	return c;
}
bool abs_compare (int a,int b) {
	int absa = abs(a);
	int absb = abs(b);
	if (absa==absb) return a<b;
	else return absa<absb;
}
