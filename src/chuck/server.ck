// The server

// Logging utilty
class LoggingSingleton {
    20 => int LOG_LEVEL_INFO;
    10 => int LOG_LEVEL_DEBUG;
    LOG_LEVEL_DEBUG => int debugLevel;

    fun void debug(string msg) {
        if (debugLevel <= LOG_LEVEL_DEBUG) {
            <<<"DEBUG:", msg>>>;
        }
    }

    fun void info(string msg) {
        if (debugLevel <= LOG_LEVEL_INFO) {
            <<<"INFO:", msg>>>;
        }
    }
}

LoggingSingleton logging; // Only need a singleton instance
logging.LOG_LEVEL_INFO => logging.debugLevel;

// Array utility functions
fun string arrayToString(int arr[]) {
    "" => string result;
    for (0 => int i; i < arr.size(); i++) {
        arr[i] +=> result;
        if (i != arr.size() - 1) {
            ", " +=> result;
        }
    }
    return "[" + result + "]";
}

fun string arrayToString(float arr[]) {
    "" => string result;
    for (0 => int i; i < arr.size(); i++) {
        arr[i] +=> result;
        if (i != arr.size() - 1) {
            ", " +=> result;
        }
    }
    return "[" + result + "]";
}

// Helpers for interpolating between values, given an expression value in [0, 1]
fun float interpolateFloat(float lo, float hi, float amt) {
    return lo + amt * (hi - lo);
};

fun int interpolateInt(int lo, int hi, float amt) {
    lo + amt * (hi - lo) => float res;
    return Math.round(res) $ int;
};

fun dur interpolateDur(dur lo, dur hi, float amt) {
    return lo + amt * (hi - lo);
};

// Global timing information and control
16 => int beatsPerMeasure;
0.5 => float noteLength; // Each note is 1/2 a beat
dur T;
int _curBeat;

fun void setTempo(float bpm) {
    60::second / bpm * noteLength => T;
}

setTempo(220);

// Buffers
[
    "../data/kick.wav",
    "../data/snare.wav",
    "../data/snare-hop.wav",
    "../data/hihat.wav",
    "../data/hihat-open.wav"
] @=> string BUFFERS[];

// Workers handle playing music. This stores metadata
class WorkerMeta {
    0 => int isPlaying;
    [
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0
    ] @=> int timing[];
    [
        0., 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0
    ] @=> float expression[];
    0 => int instrument;
}

// Would be nice to have ArrayList (see lick library)
// Up to 10 voices
10 => int N_WORKERS;
WorkerMeta workerMetas[N_WORKERS];

fun void worker(int workerId) {
  // Looks in its spot in array for metadata. Plays sounds based on metadata
  while (true) {
    if (workerMetas[workerId].isPlaying) {
        playSoundSwitch(
            workerMetas[workerId].instrument,
            workerMetas[workerId].expression,
            workerMetas[workerId].timing
        );
    }

    // Wait for the next beat
    T => now;
  }
}

for (0 => int i; i < N_WORKERS; i++) {
    spork ~ worker(i);
}

// Configure a sound played by workerId. Make sure to set isPlaying to hear it!
fun void configSound(int workerId, int instrument, float expression[], int timing[]) {
    instrument => workerMetas[workerId].instrument;
    // Just copy reference and garbage-collect (right?) the old instance
    expression @=> workerMetas[workerId].expression;
    timing @=> workerMetas[workerId].timing;
}

// Switchboard to playSound for a specific instrument...
fun void playSoundSwitch(int instrument, float expression[], int timing[]) {
    // Compare global curBeat with timing information
    if (!timing[_curBeat]) {
        return;
    }
    
    // Instrument is a buffer, use unified playBuffer function
    if (instrument < BUFFERS.size()) {
        spork ~ playBuffer(instrument, expression);
        return;
    }

    // Otherwise, switch to the correct instrument
    BUFFERS.size() - instrument => instrument;
    if (instrument == 0) {
        spork ~ playInstrument0(expression);
    } else {
        return;
    }
}

// My sounds!

fun void playBuffer(int bufIdx, float expression[]) {
    SndBuf kickBuf => Gain g1 => dac;
    me.dir() + BUFFERS[bufIdx] => kickBuf.read;
    0.5 => g1.gain;

    Math.random2f(0.8, 0.9) => kickBuf.gain; // randomize gain a bit
    500::ms => now;
}
// TODO: may be able to save on compute by preloading buffers into instances

fun void playInstrument0(float expression[]) {
    SinOsc c => ADSR adsr => LPF f => dac;
    // modulator
    SinOsc m => blackhole;
    adsr.set(10::ms, 40::ms, 0.5, 100::ms);

    0.2 => c.gain;
    200 => f.freq; // only let low in
    7 => f.Q;

    // carrier frequency
    440 => float cf;
    // modulator frequency
    15 => float mf => m.freq;
    // index of modulation
    300 => float index;
    // modulate (additive)
    cf + (index * m.last()) => c.freq;
    // advance time by 1 samp
    
    spork ~ instrument0_ctrlShred(cf, c, m, index);
    
    adsr.keyOn();
    adsr.attackTime() + adsr.decayTime() + 100::ms => now; // TODO: this can be configurable
    adsr.keyOff();
    adsr.releaseTime() * 2 => now; // x2 to avoid audio clipping
}

fun void instrument0_ctrlShred(float cf, SinOsc c, SinOsc m, float index) {
    while (true) {
        cf + (index * m.last()) => c.freq;
        1::samp => now;
    }
}

// Constants used for the OSC server
57120 => int PORT;
16 => int EXPRESSION_DIM;
16 => int TIMING_DIM;

fun void osc_nextHandler() {
    OscIn oin;
    OscMsg msg;
    PORT => oin.port;
    oin.addAddress("/next");

    while (true) {
        oin => now;
        while (oin.recv(msg)) {
            msg.getInt(0) => int instrument;
            float expression[EXPRESSION_DIM];
            for (0 => int i; i < EXPRESSION_DIM; i++) {
                msg.getFloat(1 + i) => expression[i];
            }

            int timing[TIMING_DIM];
            for (0 => int i; i < TIMING_DIM; i++) {
                msg.getInt(1 + EXPRESSION_DIM + i) => timing[i];
            }

            logging.info("got /next");
            logging.debug("instrument " + instrument);
            logging.debug("expression " + arrayToString(expression));
            logging.debug("timing " + arrayToString(timing));

            // 0 is always the index of the "currently playing" voice
            configSound(0, instrument, expression, timing);
            1 => workerMetas[0].isPlaying;
        }
    }
}

fun void osc_clearHandler() {
    OscIn oin;
    OscMsg msg;
    PORT => oin.port;
    oin.addAddress("/clear");

    while (true) {
        oin => now;
        while (oin.recv(msg)) {
            logging.info("got /clear");

            for (0 => int i; i < N_WORKERS; i++) {
                0 => workerMetas[i].isPlaying;
            }
        }
    }
}

1 => int _pushIdx; // Used for push and pop

fun void osc_pushHandler() {
    OscIn oin;
    OscMsg msg;
    PORT => oin.port;
    oin.addAddress("/push");

    while (true) {
        oin => now;
        while (oin.recv(msg)) {
            logging.info("got /push");
            if (_pushIdx == N_WORKERS) {
                continue;
            }

            workerMetas[0] @=> WorkerMeta curMeta;
            configSound(
                _pushIdx,
                curMeta.instrument,
                curMeta.expression,
                curMeta.timing
            );
            1 => workerMetas[_pushIdx].isPlaying;
            1 +=> _pushIdx;

            // Mute current track
            0 => workerMetas[0].isPlaying;
        }
    }
}

fun void osc_popHandler() {
    OscIn oin;
    OscMsg msg;
    PORT => oin.port;
    oin.addAddress("/pop");

    while (true) {
        oin => now;
        while (oin.recv(msg)) {
            logging.info("got /pop");
            if (_pushIdx == 1) {
                continue;
            }

            1 -=> _pushIdx;
            0 => workerMetas[_pushIdx].isPlaying;
        }
    }
}

fun void osc_startRecordHandler() {
    OscIn oin;
    OscMsg msg;
    PORT => oin.port;
    oin.addAddress("/startRecording");

    while (true) {
        oin => now;
        while (oin.recv(msg)) {
            logging.info("got /startRecording");
            // TODO: implement
        }
    }
}

fun void osc_stopRecordHandler() {
    OscIn oin;
    OscMsg msg;
    PORT => oin.port;
    oin.addAddress("/stopRecording");

    while (true) {
        oin => now;
        while (oin.recv(msg)) {
            logging.info("got /stopRecording");
            // TODO: implement
        }
    }
}

fun void osc_setTempoHandler() {
    OscIn oin;
    OscMsg msg;
    PORT => oin.port;
    oin.addAddress("/setTempo");

    while (true) {
        oin => now;
        while (oin.recv(msg)) {
            logging.info("got /setTempo");
            // TODO: implement
        }
    }
}

spork ~ osc_nextHandler();
spork ~ osc_clearHandler();
spork ~ osc_pushHandler();
spork ~ osc_popHandler();
spork ~ osc_startRecordHandler();
spork ~ osc_stopRecordHandler();

// Orchestration loop
logging.info("starting orchestration loop");
while (true) {
    for (0 => int beat; beat < beatsPerMeasure; beat++) {
        beat => _curBeat;
        // <<<_curBeat>>>;
        T => now;
    }
    logging.debug("new measure");
}
