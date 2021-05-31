# AA222/MUSIC220A Final Project

I'll put something here, eventually...

# Installing dependencies

This project uses Node to run the React web application, Python (with Anaconda
to manage dependencies), and SuperCollider/ChucK to handle audio synthesis.

If you want to reproduce the work, it's advised to get Anaconda (conda) to
install the exact same dependencies I used whilst developing this project. With
conda installed, from the base directory of this project, you can run:

```zsh
conda env create -f environment.yml
```

This will create a conda environment with the prefix `gen_music`. Now you can
activate the environment:

```zsh
conda activate gen_music
```

# Starting REPL Client

> _The REPL client program and SuperCollider audio server code were done for my
> final project in AA222/CS361: Engineering Design Optimization._

The REPL Client is a simple terminal-based client that allows a user to provide
feedback to the music genetic algorithm, monitor and manipulate its progress,
and listen to and record the resulting sound.

Unfortunately, I haven't yet produced a script for the SuperCollider server.
You'll need to run it inside the SuperCollider IDE, which require some minimal
knowledge to get started. I hope in the future to be able to initialize the
server simply by invoking the `scsynth` and `sclang` executables.

To start the client, you'll first need to make sure the SuperCollider server
`sc/server.sc` is running. Then, navigate to the `src` directory and run:

```zsh
python genetic_demo.py
```

In the client, you can type the command "help" (or "h" for short) to see a list
of the available commands. An (incomplete!) reproduction follows:

```plaintext
['-', 'd', 'dis']
  Dislike the currently playing Chromosome.
['', 'n', 'next']
  Play the next Chromosome in the current population.
['+', 'l', 'like']
  Like the currently playing Chromosome.
['a', 'adv']   Advance a generation.
['clr']        Clear all playing Parts.
['h', 'help']  Display helptext.
['p', 'push']  Commit the currently playing Chromosome and start a new Part.
['pop']        Remove the most recently added Chromosome.
['q', 'quit']  Quits the program.
['r', 'rec']   Toggles recording.
```

# 🐛 Starting Audiovisual Client (Wormfood)

> _The audiovisual client program and ChucK code were done for my final project
> for MUSIC 220a._

To start the web client, navigate to the `src/client` directory. From there, you
can run:

```zsh
npm start
```

The web client sends requests via loopback to the port specified in `api.js` and
`app.py`. You can boot the Flask web server by navigating to the the `src`
directory and running:

```zsh
flask run
```

The Flask server sends messages using the Open Sound Control (OSC) standard to
an audio server, which produces the audio. To start a (demo) ChucK server,
navigate to the `src/chuck` directory. From there, you can run:

```zsh
chuck r.ck
```

# Testing

To run tests, navigate to the `src` directory and run:

```zsh
python -m pytest
```
