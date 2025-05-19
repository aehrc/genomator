
#ifndef _TINICARDEXTENSION_CONSTANTS
#define _TINICARDEXTENSION_CONSTANTS

//#define UPDEBUG
#ifdef UPDEBUG
#define D(X) X
#else
#define D(X)
#endif

#define _ULL_ unsigned long long
#define _ULLONES_ (~0ULL)
#define _ULLONE_ (1ULL)
#define _ULLZERO_ (0ULL)
#define _ULLBITS_ (8*sizeof(_ULL_))

#define PRINT_ULL(a) {_ULL_ aa = a; for (int asdf1234=0; asdf1234<64; asdf1234++) {printf("%lli",aa&1);aa = aa>>1;}}
#define ERROR(msg)  {fprintf(stderr,"ERROR: ");fprintf(stderr,msg);fprintf(stderr,"\n");exit(1);}


#endif
