audioFile = "California";
[y,Fs] = audioread(audioFile + ".wav");
ECHO = audioexample.Echo;
echoed = ECHO(y);
audiowrite(audioFile + "_echoed.wav",echoed,Fs);