// import logo from './logo.svg';
// import './App.css';
import React, { useEffect, useRef, useState } from "react";
import P5Wrapper from "react-p5-wrapper";
import wormSketch from "./worm/worm";

function App() {
  const [obsFrameRate, setObsFrameRate] = useState();
  const [testState, setTestState] = useState(false);

  // Be able to reference the sketch wrapper
  const sketchRef = useRef();

  useEffect(() => {
    // TODO: probably want to tear down the setInterval call when the component unmounts
    const handle = setInterval(() => {
      if (sketchRef && sketchRef.current.state.canvas) {
        const fr = sketchRef.current.state.canvas.frameRate();
        setObsFrameRate(fr);
      }
    }, 1000);

    return function cleanup() {
      clearInterval(handle);
    };
  }, [sketchRef]);

  const handleClick = () => {
    console.log("Clicked");
    setTestState(!testState);

    // A lil hacky... the canvas is where P5 wrapper stuffs the canvas object
    // TODO: shift to a global context pattern. Sketch component should be able
    // to dispatch updates to the context, which we can read
    console.log(sketchRef.current.state.canvas.frameRate());
  };

  // Callback example (sketch calls this)
  const handleWormHover = (idx) => {
    console.log("REACT APP: worm " + idx + "hovered");
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Worms Demo</h1>
        <p>Frame rate: {obsFrameRate && obsFrameRate}</p>
        <button onClick={handleClick}>Next Generation</button>

        <P5Wrapper
          sketch={wormSketch}
          ref={sketchRef}
          testProp={testState}
          handleWormHover={handleWormHover}
        />
      </header>
    </div>
  );
}

export default App;
