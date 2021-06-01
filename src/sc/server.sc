/* SupercCollider Server */
// NOTE: all play calls are passed quant: 8 to start at the top of the next
// 16/2 time steps (all durs are 1/2). Would be nice to schedule this transition
// right when the move to a new bar happens.

(
// Globals
~expressionDim = 16;
~timingDim = 16;
~basePath = thisProcess.nowExecutingPath.dirname;

Routine({
	// NOTE: shifted to using mostly globals
	~partCtr = 0;
	~currentParts = List.new;

	// Load in any buffers
	~buffers = List.new;
	[
		"../data/kick.wav",
		"../data/snare.wav",
		"../data/snare-hop.wav",
		"../data/hihat.wav",
		"../data/hihat-open.wav"
	].do({
		arg item, i;
		~buffers.add(
			Buffer.read(s, ~basePath +/+ item)
		);
	});

	// Server startup message
	( "Server listening on" + NetAddr.localAddr.ip ++ ", port" + NetAddr.langPort ).postln;

	// Helper functions

	// Updates timing information associated with pattern instance stored at petternRef
	~updateTiming = { | patternRef, timing |
		Pbindef(patternRef, \amp, Pseq(timing, inf));
	};

	~updateBufref = { | patternRef, bufref |
		Pbindef(patternRef, \bufref, bufref);
	};

	~updateInstrument = { | patternRef, instrument |
		(instrument < ~buffers.size).if ({
			( "DEBUG instrument is a buffer" ).postln;
			Pbindef(patternRef, \instrument, \playBufMono);
			~updateBufref.value(patternRef, ~buffers[instrument.asInteger]);
		}, {
			// TODO: handle non-buffer instruments: instrument must change.
			(
				"DEBUG instrument is a unique SynthDef" +
				~synthDefs[instrument.asInteger - ~buffers.size]
			).postln;
			Pbindef(patternRef, \instrument, ~synthDefs[instrument.asInteger - ~buffers.size]);
		});
	};

	~interpolateValue = { | lo, hi, amt |
		var diff = hi - lo;
		diff * amt + lo;
	};

	~updateExpression = { | patternRef, expression |
		// Pbindef(patternRef, \modFreq, [7, 9, 10, 15, 20, 30].choose);
		Pbindef(patternRef, \modFreq, ~interpolateValue.value(5, 40, expression[0]));
		Pbindef(patternRef, \carFreq, ~interpolateValue.value(400, 1200, expression[0]));
	};

	~initPattern = { | patternRef |
		var pattern;
		pattern = Pbind(
			\note, 1,
			\dur, 1/2,
			\amp, Pseq([0], inf),
		);
		Pdef(patternRef, pattern);
	};

	~getNumInstruments = {
		~buffers.size + ~synthDefs.size;
	};

	// Needs to be initialized in here for the timing to work, for whatever reason.
	~tclock = TempoClock(220/60);
	~tclock.permanent_(true);
	~initPattern.value(\cur); // Initialize our first pattern. XXX where to put this
	Pdef(\cur).play(~tclock, quant: 8);

	// Map instrument num to synthdef symbol
	~synthDefs = [
		\zaps,
	];

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

	// FM-style
	// From Giles Bowkett TODO: paste source/attribution. migrate to another file?
	SynthDef(\zaps, { arg amp = 1, modFreq = 15, carFreq = 880, modDepth = 3250;
		var car, mod, env;

		env = Env.perc(releaseTime: 0.3).kr(doneAction: 2);
		mod = Pulse.ar(freq: modFreq * [1, 1.14, 0.97, 6, 7, 8, 9, 10, 1.04, 1.2], mul: modDepth);
		car = Pulse.ar(freq: carFreq + mod * [1, 1.41, 0.99, 2.4921, 5, 6, 1.397], mul: env);
		car = Splay.ar(car);
		Out.ar(
			0,
			FreeVerb.ar(HPF.ar(car, freq: 5274), mix: 0.05, room: 0.1, damp: 0.9, mul: amp * 0.5)
		);
	}).add;

	// Ensures SynthDefs are added to the server
	// s.sync(); // TODO: this prevents the rest of the code from running. Misunderstanding with sync.

	// Create OSCFuncs to listen for commands
	OSCFunc({ | msg, time, addr, port |
		var instrument, timing, expression;
		instrument = msg[1].asInteger;
		( "DEBUG 'next' received, instrument:" + instrument ).postln;

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

		~updateInstrument.value(\cur, instrument);
		~updateExpression.value(\cur, expression);
		~updateTiming.value(\cur, timing);
	}, "/next");

	/*
	push
	----

	Copies \cur to a globally increasing partCtr.asSymbol, then resets \cur
	to accept a new pattern.
	*/
	OSCFunc({ | msg, time, addr, port |
		"DEBUG 'push' received".postln;
		Pdef(\cur).copy(~partCtr.asSymbol);
		~currentParts.add(~partCtr.asSymbol);

		Pdef(~partCtr.asSymbol).play(~tclock, quant: 8);
		~partCtr = ~partCtr + 1;

		// Schedule for the top
		/*~tclock.schedAbs(~tclock.beats.ceil + (16 - ~tclock.beats.ceil % 8),
			{*/
				"Clear cur".postln;
				Pdef(\cur).clear; // NOTE: not necessary
				~initPattern.value(\cur);
				Pdef(\cur).play(~tclock, quant: 8);
		/*	}
		);*/
	}, "/push");

	/*
	clear
	-----

	Clears all patterns currently playing. Resets \cur.
	*/
	OSCFunc({ | msg, time, addr, port |
		"DEBUG: 'clear' received".postln;
		Pdef.clear;

		~initPattern.value(\cur);
		Pdef(\cur).play(~tclock, quant: 8);
	}, "/clear");

	/*
	startRecording
	--------------

	Starts recording to file.
	*/
	OSCFunc({ | msg, time, addr, port |
		"DEBUG: 'startRecording' received".postln;
		// TODO: pass a file path through?
		s.record;
	}, "/startRecording");

	/*
	stopRecording
	-------------

	Stops recording.
	*/
	OSCFunc({ | msg, time, addr, port |
		"DEBUG: 'startRecording' received".postln;
		s.stopRecording;
	}, "/stopRecording");
}).play;
)

// Testing region...

Pdef.clear
Pdef.all
Pdef(\0).isPlaying
Pbindef(\0, \bufref, ~buffers[0]);
~buffers
~initPattern.value(\0)
~getNumInstruments.value
~interpolateValue.value(4, 8, 0.5)

Pdef(\0).set

(
Pbindef(\0,
	\amp, Pseq([
		1, 0, 1, 1,
		0, 1, 1, 1,
		0, 0, 1, 1,
		1, 1, 1, 1,
	], inf)
)
)


(
Pdef(\a);
~kickBuffer
b = List.new
b.add(1).
b.size
(1 == b.size).if({
	"That was true bb".postln;
}, {})
)

~tclock.schedAbs(~tclock.beats.ceil + (16 - ~tclock.beats.ceil % 8), { "New bar".postln;  1 });
~tclock.beats % 16
Pdef(\cur).stop

// May need to set out device
ServerOptions.outDevices;
Server.default.options.outDevice_("MacBook Pro Speakers");
Server.default.options.outDevice_("External Headphones");

