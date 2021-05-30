/* SupercCollider Server */

(
// Globals
~expressionDim = 16;
~timingDim = 16;
~basePath = thisProcess.nowExecutingPath.dirname;

Routine({
	// Declare helper functions and variables
	var updateTiming, updateInstrument, updateBufref, initPattern,
	buffers;

	// Load in any buffers
	buffers = List.new;
	[
		"../data/kick.wav",
		"../data/snare.wav",
		"../data/snare-hop.wav",
		"../data/hihat.wav",
		"../data/hihat-open.wav"
	].do({
		arg item, i;
		buffers.add(
			Buffer.read(s, ~basePath +/+ item)
		);
	});

	// Server startup message
	( "Server listening on" + NetAddr.localAddr.ip ++ ", port" + NetAddr.langPort ).postln;


	// Map instrument num to synthdef symbol

	// Helper functions

	// Updates timing information associated with pattern instance stored at petternRef
	updateTiming = { | patternRef, timing |
		Pbindef(patternRef, \amp, Pseq(timing, inf));
	};

	updateBufref = { | patternRef, bufref |
		Pbindef(patternRef, \bufref, bufref);
	};

	updateInstrument = { | patternRef, instrument |
		(instrument < buffers.size).if ({
			( "DEBUG instrument is a buffer" ).postln;
			Pbindef(patternRef, \instrument, \playBufMono);
			updateBufref.value(patternRef, buffers[instrument.asInteger]);
		}, {
			// TODO: handle non-buffer instruments: instrument must change.
			( "DEBUG instrument is a unique SynthDef" ).postln;
		});
	};

	initPattern = { | patternRef |
		var pattern;
		pattern = Pbind(
			\note, 1,
			\dur, 1/2,
			\amp, Pseq([0], inf),
		);
		Pdef(patternRef, pattern);
	};

	// Needs to be initialized in here for the timing to work, for whatever reason.
	~tclock = TempoClock(220/60);
	~tclock.permanent_(true);
	initPattern.value(\a); // Initialize our first pattern. XXX where to put this
	Pdef(\a).play(~tclock);

	// SynthDefs
	SynthDef(\playBufMono, { arg
		out = 0,
		bufref,
		amp,
		pan;

		var sig;
		sig = PlayBuf.ar(1, bufref, BufRateScale.kr(bufref), doneAction: 2);

		// sig = sig * env;
		sig = Pan2.ar(sig, pan, amp);
		Out.ar(out, sig);
	}).add;

	// Ensures SynthDefs are added to the server
	// s.sync(); // TODO: this prevents the rest of the code from running. Misunderstanding with sync.

	// Create OSCFuncs to listen for commands
	OSCFunc({ | msg, time, addr, port |
		var instrument, timing, expression;
		instrument = msg[1].asInteger;
		( "DEBUG instrument:" + instrument ).postln;

		expression = Array(~expressionDim);
		for (0, 15, {
			arg i;
			expression.add(msg[i + 2]);
		});

		timing = Array(~timingDim);
		for (0, 15, {
			arg i;
			timing.add(msg[i + ~expressionDim + 2]);
		});

		// TODO: instead of symbol \a, get symbol programmatically
		updateInstrument.value(\a, instrument);
		updateTiming.value(\a, timing);
	}, "/playInstrument" );
}).play;
)

// Testing region...
(
// Declare helper functions
var updateTiming, buffers;

// Load in any buffers
buffers = List.new;
buffers.postln;
[
	"../data/kick.wav",
	"../data/snare.wav",
	"../data/snare-hop.wav",
	"../data/hihat.wav",
	"../data/hihat-open.wav"
].do({
	arg item, i;
	buffers.add(
		Buffer.read(s, ~basePath +/+ item)
	);
});
buffers.postln;
)


(
Pdef(\a);
~kickBuffer
b = List.new
b.add(1)
b.size
(1 == b.size).if({
	"That was true bb".postln;
}, {})
)

// May need to set out device
ServerOptions.outDevices;
Server.default.options.outDevice_("MacBook Pro Speakers");
Server.default.options.outDevice_("External Headphones");

