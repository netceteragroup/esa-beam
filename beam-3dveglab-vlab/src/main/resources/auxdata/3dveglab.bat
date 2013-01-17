@echo off
set BEAM4_HOME=C:\Program Files (x86)\beam-4.10.3

"%BEAM4_HOME%\jre\bin\java.exe" ^
    -Xmx1024M ^
    -Dceres.context=beam ^
    "-Dbeam.mainClass=org.esa.beam.framework.processor.ProcessorRunner" ^
    "-Dbeam.processorClass=com.netcetera.vlab.VLabProcessor" ^
    "-Dbeam.home=%BEAM4_HOME%" ^
    "-Dncsa.hdf.hdflib.HDFLibrary.hdflib=%BEAM4_HOME%\modules\lib-hdf-2.7\lib\jhdf.dll" ^
    "-Dncsa.hdf.hdf5lib.H5.hdf5lib=%BEAM4_HOME%\modules\lib-hdf-2.7\lib\jhdf5.dll" ^
    -jar "%BEAM4_HOME%\bin\ceres-launcher.jar" %*

exit /B %ERRORLEVEL%
