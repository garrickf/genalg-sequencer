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

# Starting Client

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
