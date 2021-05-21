const s = (sketch) => {
  // Constants
  const MARGIN = 100;
  const N_WORMS = 4;
  const WORM_LENGTH = 50;
  const WORM_DIAMETER = 10;

  // These constants use p5 functions and need to be set up in a function of their own
  let RED;
  let RED_ALPHA;
  const GREEN_ALPHA = (alpha) => sketch.color(0, 255, 0, alpha);
  const GRAY_ALPHA = (alpha) => sketch.color(100, 100, 100, alpha);
  let TURN_RADIUS;
  let UNIT_NORTH;

  const setupConstants = () => {
    RED = sketch.color(255, 0, 0);
    RED_ALPHA = sketch.color(255, 0, 0, 100);
    TURN_RADIUS = sketch.radians(2);
    UNIT_NORTH = new p5.Vector(0, 1);
  };

  const TurnState = {
    TURN_LEFT: "turn_left",
    TURN_RIGHT: "turn_right",
    GO_STRAIGHT: "go_straight",
  };

  class Worm {
    constructor(idx) {
      this.head = new p5.Vector(sketch.width / 2, sketch.height / 2);
      this.heading = p5.Vector.random2D();
      this.turnState = TurnState.GO_STRAIGHT;
      this.turnAround = false;

      this.body = [];
      this.bodyOrientations = [];

      this.name = "Worm " + idx;

      this.hovered = false;
      this.speed = 1;

      // TODO: choose color based on instrument
      this.r = sketch.random(255);
      this.g = sketch.random(255);
      this.b = sketch.random(255);
    }

    /* Draws the worm on-screen */
    display() {
      sketch.push();
      sketch.stroke(this.r, this.g, this.b);
      sketch.fill(this.r, this.g, this.b);
      sketch.rectMode(sketch.CENTER);

      const drawEvery = sketch.int(WORM_DIAMETER / 2 / this.speed);

      // TODO: change to rounded rect, add stripey genes
      for (let i = 0; i < this.body.length; i += drawEvery) {
        const radius =
          i > this.body.length - drawEvery || i < drawEvery
            ? WORM_DIAMETER / 2
            : WORM_DIAMETER / 4;
        this._drawWormSegment(this.body[i], this.bodyOrientations[i], radius);
      }
      // Always include head, as a circle
      this._drawWormSegment(this.head, this.heading, WORM_DIAMETER / 2);
      sketch.pop();

      this._displayDebugInfo();
    }

    _drawWormSegment(position, orientation, radius) {
      sketch.push(); // Save current drawing styles
      const angle = UNIT_NORTH.angleBetween(orientation);
      sketch.translate(position.x, position.y);
      sketch.rotate(angle);
      sketch.rect(0, 0, WORM_DIAMETER, WORM_DIAMETER, radius);
      sketch.pop();
    }

    _displayDebugInfo() {
      sketch.stroke(RED);
      const nextPos = p5.Vector.add(
        this.head,
        p5.Vector.mult(this.heading, 30)
      );
      sketch.line(this.head.x, this.head.y, nextPos.x, nextPos.y);

      // Draw hover selection area
      sketch.noStroke();
      if (this.hovered) {
        sketch.fill(GREEN_ALPHA(150));
      } else {
        sketch.fill(GRAY_ALPHA(150));
      }

      sketch.ellipse(
        this.head.x,
        this.head.y,
        WORM_DIAMETER * 4,
        WORM_DIAMETER * 4
      );
    }

    startTurnAround() {
      if (!this.turnAround) {
        if (sketch.random(1) < 0.5) {
          this.turnState = TurnState.TURN_LEFT;
        } else {
          this.turnState = TurnState.TURN_RIGHT;
        }

        this.turnAround = true;
      }
    }

    endTurnAround() {
      if (this.turnAround) {
        this.turnState = TurnState.GO_STRAIGHT;
        this.turnAround = false;
      }
    }

    handleMouseOver(loc) {
      if (p5.Vector.dist(loc, this.head) < WORM_DIAMETER * 2) {
        if (!this.hovered) {
          sketch.print(this.name + " was hovered over");
          this.hovered = true;

          this.r = sketch.random(255);
          this.g = sketch.random(255);
          this.b = sketch.random(255);
        }
      } else if (this.hovered) {
        sketch.print(this.name + " hover exit");
        this.hovered = false;
      }
    }

    step() {
      // With small probability, change turn state.
      // If turning, can only switch to going forward.
      // If forward, more likely to turn?

      if (
        this.head.x < MARGIN ||
        this.head.x > sketch.width - MARGIN ||
        this.head.y < MARGIN ||
        this.head.y > sketch.height - MARGIN
      ) {
        this.startTurnAround();
      } else {
        this.endTurnAround();
      }

      // Probabilisitc is nice, want a more "turn every" time approach
      // Does not change direction if turnAround is active
      if (!this.turnAround && sketch.random(1) < 0.03) {
        if (this.turnState != TurnState.GO_STRAIGHT) {
          this.turnState = TurnState.GO_STRAIGHT;
        } else {
          if (sketch.random(1) < 0.5) {
            this.turnState = TurnState.TURN_LEFT;
          } else {
            this.turnState = TurnState.TURN_RIGHT;
          }
        }
      }

      // Update head position
      this.head = p5.Vector.add(
        this.head,
        p5.Vector.mult(this.heading, this.speed)
      );
      this.body.push(this.head);
      if (this.body.length > WORM_LENGTH) {
        this.body.shift(); // Remove from front
      }

      // Update heading
      if (this.turnState == TurnState.TURN_LEFT) {
        this.heading = p5.Vector.rotate(this.heading, -TURN_RADIUS);
      } else if (this.turnState == TurnState.TURN_RIGHT) {
        this.heading = p5.Vector.rotate(this.heading, TURN_RADIUS);
      }

      this.bodyOrientations.push(this.heading);
      if (this.bodyOrientations.length > WORM_LENGTH) {
        this.bodyOrientations.shift();
      }
    }
  }

  function displayDebugInfo() {
    // Draw red boxes around borders (worms should turn around)
    sketch.push();
    sketch.noStroke();
    sketch.fill(RED_ALPHA);

    sketch.rect(0, 0, sketch.width, MARGIN);
    sketch.rect(0, sketch.height - MARGIN, sketch.width, MARGIN);
    sketch.rect(0, MARGIN, MARGIN, sketch.height - MARGIN * 2);
    sketch.rect(sketch.width - MARGIN, MARGIN, MARGIN, sketch.height - MARGIN * 2);

    // Draw mouse position
    sketch.stroke(0);
    sketch.line(sketch.mouseX, 0, sketch.mouseX, 50);
    sketch.line(0, sketch.mouseY, 50, sketch.mouseY);
    sketch.pop();
  }

  // Global, propagates mouseOver events to objects which need them
  function handleMouseMoved() {
    const location = new p5.Vector(sketch.mouseX, sketch.mouseY);
    for (let i = 0; i < worms.length; i++) {
      worms[i].handleMouseOver(location);
    }
  }

  // Global state
  let worms = [];

  sketch.setup = () => {
    const cvs = sketch.createCanvas(1000, 1000);
    cvs.mouseMoved(handleMouseMoved);
    setupConstants();
    sketch.print("Sketch pixel density: " + sketch.pixelDensity());

    for (let i = 0; i < N_WORMS; i++) {
      worms.push(new Worm(i));
    }

    sketch.background(255);
  };

  sketch.draw = () => {
    // Clear screen
    sketch.background(255);

    for (let i = 0; i < worms.length; i++) {
      worms[i].step();
      worms[i].display();
    }

    displayDebugInfo();
  };
};

let mySketch = new p5(s);
