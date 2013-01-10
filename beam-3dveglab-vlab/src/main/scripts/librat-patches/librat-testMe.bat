@echo off
ratstart < starttest.ip -sensor_wavebands wavebands.dat -m 100 -sun_position 0 0 10 test.obj 1> testMe.this.op 2>&1 

echo "this result"
echo "==========="
type testMe.this.op

echo "diff of file:"
echo "============="
type testMe.op


