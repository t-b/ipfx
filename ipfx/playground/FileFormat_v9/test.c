#include "windows.h"
#include <stdio.h>
#include <stdlib.h>

#define MAC_BASE   9561652096.0
#define HIGH_DWORD 4294967296.0
#define JanFirst1990 1580970496.0

// Function PatchMasterSecondsToFileTime
//    Convert seconds to FILETIME.
//    In converting double to DWORD we must be carefull because the
//    double will first be converted to a signed int.
//    Do the operations modulo 2^31.
//    Get the next bit from the high DWORD and then shift high DWORD
//    throwing away the highest bit.

void PatchMasterSecondsToFileTime( double time, FILETIME* file_time )
{
   time -= JanFirst1990;

   if (time < 0.0)
      time += HIGH_DWORD;

   time += MAC_BASE;

   time *= 10000000.0;

   file_time->dwHighDateTime = (DWORD) (time / (HIGH_DWORD / 2.0));

   file_time->dwLowDateTime = (DWORD)
      (time - (double) file_time->dwHighDateTime * (HIGH_DWORD / 2.0));

   file_time->dwLowDateTime |= ((file_time->dwHighDateTime & 1) << 31);

   file_time->dwHighDateTime >>= 1;
}

void PatchMasterSecondsToDate( double storedTime, SYSTEMTIME* system_time)
{
   FILETIME file_time;
   PatchMasterSecondsToFileTime( storedTime, &file_time );
   FileTimeToSystemTime( &file_time, system_time );
}

int main(int argc, char** argv)
{
    double val = atof(argv[1]);
    SYSTEMTIME s;
    PatchMasterSecondsToDate(val, &s);

    printf("%d-%d-%d %d:%d:%d.%d", s.wYear, s.wMonth, s.wDay, s.wHour, s.wMinute, s.wSecond, s.wMilliseconds);

}
