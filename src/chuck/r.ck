// Example code adapted from https://chuck.cs.princeton.edu/doc/examples/osc/r.ck

// the patch
SinOsc s => JCRev r => dac;
.5 => s.gain;
.1 => r.mix;

// create our OSC receiver
OscIn oin;
// create our OSC message
OscMsg msg;
// use port 57120 (same as SuperCollider sclang)
57120 => oin.port;
// create an address in the receiver, expect an int and a float
oin.addAddress( "/setFreq, f" );

// infinite event loop
while( true )
{
    // wait for event to arrive
    oin => now;

    // grab the next message from the queue. 
    while( oin.recv(msg) )
    { 
        float f;

        msg.getFloat(0) => f => s.freq;

        // print
        <<< "got (via OSC):", f >>>;
    }
}
