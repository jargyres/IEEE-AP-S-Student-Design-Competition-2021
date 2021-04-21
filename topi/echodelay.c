/* echodelay.c */


#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>

void echodelay (int chdelay, int spdelay, int nldelay, char *string);
int msleep (int millisec);
int atoipos (char *string);


int
main (int argc, char **argv)
{
  int opt;
  int chdelay = 0, spdelay = 0, nldelay = 0;


  /* parse command line */


//   while ((opt = getopt (argc, argv, "c:s:n:")) != -1)
//     {
//       switch (opt)
//         {
//         case 'c':              /* -c nnn */
//           chdelay = atoipos (optarg);
//           break;
//         case 's':              /* -s nnn */
//           spdelay = atoipos (optarg);
//           break;
//         case 'n':              /* -n nnn */
//           nldelay = atoipos (optarg);
//           break;
//         default:               /* unrecognized option */
//           fprintf (stderr, "Usage: echodelay [-c millisec]
//            ↪[-s millisec] [-n millisec] [text..]\n");
//           exit (1);
//           break;
//         }
//     }


//   /* pass all remaining options as text to echodelay() */

    echodelay(chdelay, spdelay, nldelay, "info");
//   for (opt = optind; opt < argc; opt++)
//     {
//       echodelay (chdelay, spdelay, nldelay, argv[opt]);
//       putchar (' ');
//     }


  putchar ('\n');


  exit (0);
}


void
echodelay (int chdelay, int spdelay, int nldelay, char *string)
{
  int pos = 0;


  /* add a delay between printing each character in the string,
     depending on the character */


  do
    {
      switch (string[pos])
        {
        case '\0':             /* new line */
          msleep (nldelay);
          break;
        case ' ':              /* space */
          msleep (spdelay);
          break;
        default:               /* character */
          msleep (chdelay);
          break;
        }


      putchar (string[pos]);
      fflush (stdout);
    }
  while (string[pos++] != '\0');
}


int
msleep (int millisec)
{
  useconds_t usec;
  int ret;


  /* wrapper to usleep() but values in milliseconds instead */


  usec = (useconds_t) millisec *1000;
  ret = usleep (usec);
  return (ret);
}


int
atoipos (char *string)
{
  int val;

  /* wrapper to atoi() but always a positive return value */


  val = atoi (string);


  if (val < 0)
    {
      val = 0;
    }


  return (val);
}