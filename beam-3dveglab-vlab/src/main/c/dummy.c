#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdarg.h>
#include <errno.h>
#include <limits.h>

#define log_err(  ...)  log_xxx(stderr, 1, " [error] ", __VA_ARGS__)
#define log_info( ...)  log_xxx(stdout, 1, " [info] ",  __VA_ARGS__)
#define log_infox( ...) log_xxx(stdout, 0, "", "",      __VA_ARGS__)
#define log_debug(...)  log_xxx(stdout, 1, " [debug] ", __VA_ARGS__)

void log_xxx(FILE *str, int p, char *lvl, char *n, const char * format, ...) {
  if (p) { fprintf(str, "%s:%s", n, lvl); }
  va_list args; va_start(args, format); vfprintf(str, format, args);
  va_end(args); fflush(str);
}

void myexit(char *n, int e) {
  log_info(n, "exiting with process status=[%d]\n", e);
  if (e != EXIT_SUCCESS) { log_err(n, "exit with process status[%d]\n", e); }
  exit(e);
}

int main(int argc, char *argv[], char *envp[]) {
  int i=0, o=0, d=0, r=4;
  long e=EXIT_SUCCESS;
  char *n = argv[0], *endptr, **en;

  while ((o = getopt(argc, argv, "e:r:n:d")) != -1) {
    errno = 0;
    switch (o) {
    case 'd':
      d=1;
      break;
    case 'e':
      e = strtol(optarg, &endptr, 10);
      if ((errno == ERANGE && (e == LONG_MAX || e == LONG_MIN))
                   || (errno != 0 && e == 0) || (endptr == optarg)) {
        log_err(n, "e arg: invalid number\n");
        myexit(n, EXIT_FAILURE);
      }
      break;
    case 'n':
      n = optarg;
      break;
    case 'r':
      r = strtol(optarg, &endptr, 10);
      if ((errno == ERANGE && (r == LONG_MAX || r == LONG_MIN))
                   || (errno != 0 && e == 0) || (endptr == optarg)) {
        log_err(n, "r arg: invalid number\n");
        myexit(n, EXIT_FAILURE);
      }
      break;
    default: /* '?' */
      log_err(n, "Usage: %s [-e exit val] [-r secs] [args...]\n", argv[0]);
      myexit(n, EXIT_FAILURE);
    }
  }

  log_info(n, "command line was: ");
  for (i = 0; i<argc; i++) { log_infox("%s ", argv[i]); }
  log_infox("\n");

  if (d) { 
    log_debug(n, "env contains:\n");
    for (en = envp; *en != 0; en++) { log_debug(n, "%s\n", *en); }
  }

  for (i = 0; i<r; i++) {
    log_info(n, "progress %3d%%\n", (int)((float) i / r * 100.0));
    if (d) { log_debug(n, "sleeping...\n"); }
    sleep(1);
  }
  log_info(n, "progress %3d%%\n", 100);

  myexit(n, e);

  /*  NOTREACHED */
  return (EXIT_SUCCESS);
}
