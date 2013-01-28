rm -f Install*class && rm -f Install.manifest && (echo "Main-Class: Install" > Install.manifest) && javac Install.java && jar cmf Install.manifest 3DVegLabInstaller.jar Install*.class
