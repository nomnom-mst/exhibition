FILENAME=$1
INPUT_SAMPLE_FREQ=44100
PITCH_FRAME=80

for prefix in 0 s1_ s2_ s3_ s4_ s5_;
do
    if [ $prefix = 0 ]; then
	wav2raw data/$FILENAME/$FILENAME.wav
	x2x +sf data/$FILENAME/$FILENAME.raw | pitch -a 1 -p $PITCH_FRAME -s `expr $INPUT_SAMPLE_FREQ / 1000` -L 10 -H 500 > data/$FILENAME/$FILENAME.pitch
    else
	wav2raw data/$FILENAME/$prefix$FILENAME.wav
	x2x +sf data/$FILENAME/$prefix$FILENAME.raw | pitch -a 1 -p $PITCH_FRAME -s `expr $INPUT_SAMPLE_FREQ / 1000` -L 10 -H 500 > data/$FILENAME/$prefix$FILENAME.pitch
    fi
done
