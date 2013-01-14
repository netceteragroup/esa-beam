@echo off
setlocal
rem data is the only place I could write to
set beaminstpath="C:\data\Program Files (x86)\beam-4.10.3"
echo %beaminstpath%
if not exist %beaminstpath% (
  if exist "%ProgramFiles(x86)%\beam-4.10.3" (
    set beaminstpath "%ProgramFiles(x86)%\beam-4.10.3"
  ) else (
    echo "%ProgramFiles(x86)%\beam-4.10.3" did not exist
    if exist "%ProgramFiles%\beam-4.10.3" (
      set beaminstpath "%ProgramFiles%\beam-4.10.3"
    ) else (
      echo "%ProgramFiles%\beam-4.10.3" did not exist
      echo Can't find BEAM installation path
      goto :eof
    )
  )
)
set beamdata=%HOMEDRIVE%%HOMEPATH%\.beam\
set helper=%HOMEDRIVE%%HOMEPATH%\.beam\beam-vlab\auxdata\doshelper.jar
if not exist %helper% (
  echo .beam\beam-vlab\ausdata\doshlper.jar wasn't found
  goto :eof
)
cd "%beamdata%"
mkdir beam-vlab.new
cd beam-vlab.new
mkdir auxdata
cd auxdata
%beaminstpath%\jre\bin\java -jar %helper% fetch dummy_windows32-20130103.zip
%beaminstpath%\jre\bin\java -jar %helper% unzip dummy_windows32-20130103.zip
endlocal
