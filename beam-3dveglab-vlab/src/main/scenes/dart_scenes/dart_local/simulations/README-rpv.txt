Since a single DART simulation provides N radiance (reflectance) values for N viewing directions for a single sun direction. We suggest to generate (N_s = 50) cosine-weighted discrete ordinate within upper hemisphere to be used as sun directions. Then select the sun directions with zenith angle less than 70 degrees (sz < 70) to keep consistent with drivers.py from libradtran. 

For each sun direction, a DART simulation gives the radiance (reflectance) for 100 discrete ordinates. Then, an RPV fitting technique can be applied to the 50 Ãx 100 reflectance values.

1. Create a new DART simulation, set the number of directions to be 100 (double of N_s). Open direction.xml in the (simulation)/input/ folder, and change the following line: 

    <Directions exactDate="2" numberOfPropagationDirections="100">

to

    <Directions exactDate="2" ifCosWeighted="1" numberOfPropagationDirections="100">

2. Run direction.exe with the current configuration. Read directions.txt in (simulation)/output/. The first two columns of directions.txt are sz and sa respectively. Get those values as the input sun direction for a sequence of DART simulations. Remember to put a threshold to select sz which is less than 70 degrees.

3. Run a sequence of DART simulations with input sun direction defined from above. Set the number of directions to be 200 (double of upper hemisphere) and do the following instructions for each simulation:

Change the following line in direction.xml input folder.

    <Directions exactDate="2" numberOfPropagationDirections="200">

to

    <Directions exactDate="2" ifCosWeighted="1" numberOfPropagationDirections="200">

The first two columns of directions.txt in the output folder of each simulation are vz and vz respectively. The sequence of DART simulations will provide the BRDF for RPV inversion.
    
4. Select the values of cz less than 70 degrees in the directions.txt, and generate a file with the same format as angles.rpv.2.dat from drivers.py of libradtran. This file will be the input for libradtran to get the BRDF.

One thing to pay attention is that DART uses theta value from 0 to 180 for zenith angle (half a circle) and 0 to 360 for azimuth angle (full circle). In the upper sphere the zenith range is from 0 to 90. It is necessary to convert to libradtran zenith and azimuth range (-90 to 90 for zenith and 0-180 for azimuth).  

tiangang yin

