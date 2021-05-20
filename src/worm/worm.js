const MARGIN = 100;
const N_WORMS = 25;
const WORM_LENGTH = 50;
const WORM_DIAMETER = 10;

// These constants use p5 functions and need to be set up in a function of their own
let RED;
let RED_ALPHA;
let TURN_RADIUS;

function setupConstants() {
  RED = color(255, 0, 0);
  RED_ALPHA = color(255, 0, 0, 100);
  TURN_RADIUS = radians(1);
}

const TurnState = {
  TURN_LEFT: "turn_left",
  TURN_RIGHT: "turn_right",
  GO_STRAIGHT: "go_straight",
};

class Worm {
  constructor(idx) {
    this.head = new p5.Vector(width / 2, height / 2);
    this.heading = p5.Vector.random2D();
    this.turnState = TurnState.GO_STRAIGHT;
    this.turnAround = false;
    this.body = [];
    this.name = "Worm " + idx;

    // TODO: choose color based on instrument
    this.r = random(255);
    this.g = random(255);
    this.b = random(255);
  }

  display() {
    stroke(this.r, this.g, this.b);
    fill(this.r, this.g, this.b);

    // TODO: change to rounded rect, add stripey genes
    for (let i = 0; i < this.body.length; i += 10) {
      const segment = this.body[i];
      ellipse(segment.x, segment.y, WORM_DIAMETER, WORM_DIAMETER);
    }
    
    // Always include head
    ellipse(this.head.x, this.head.y, WORM_DIAMETER, WORM_DIAMETER);

    this._displayDebugInfo();
  }

  _displayDebugInfo() {
    stroke(RED);
    const nextPos = p5.Vector.add(this.head, p5.Vector.mult(this.heading, 30));
    line(this.head.x, this.head.y, nextPos.x, nextPos.y);
  }

  startTurnAround() {
    if (!this.turnAround) {
      if (random(1) < 0.5) {
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

  step() {
    // With small probability, change turn state.
    // If turning, can only switch to going forward.
    // If forward, more likely to turn?

    if (
      this.head.x < MARGIN ||
      this.head.x > width - MARGIN ||
      this.head.y < MARGIN ||
      this.head.y > height - MARGIN
    ) {
      this.startTurnAround();
    } else {
      this.endTurnAround();
    }

    // Probabilisitc is nice, want a more "turn every" time approach
    // Does not change direction if turnAround is active
    if (!this.turnAround && random(1) < 0.03) {
      if (this.turnState != TurnState.GO_STRAIGHT) {
        this.turnState = TurnState.GO_STRAIGHT;
      } else {
        if (random(1) < 0.5) {
          this.turnState = TurnState.TURN_LEFT;
        } else {
          this.turnState = TurnState.TURN_RIGHT;
        }
      }
    }

    // Update head position
    const PIXELS_PER_STEP = 1;
    this.head = p5.Vector.add(this.head, p5.Vector.mult(this.heading, PIXELS_PER_STEP));
    this.body.push(this.head);
    if (this.body.length > WORM_LENGTH) {
      this.body.shift(); // Remove from front
    }

    // Update heading
    if (this.turnState == TurnState.TURN_LEFT) {
      this.heading.rotate(-TURN_RADIUS);
    } else if (this.turnState == TurnState.TURN_RIGHT) {
      this.heading.rotate(TURN_RADIUS);
    }
  }
}

function displayDebugInfo() {
  // Draw red boxes around borders (worms should turn around)
  noStroke();
  fill(RED_ALPHA);
  rect(0, 0, width, MARGIN);
  rect(0, height - MARGIN, width, MARGIN);
  rect(0, MARGIN, MARGIN, height - MARGIN * 2);
  rect(width - MARGIN, MARGIN, MARGIN, height - MARGIN * 2);

  // Draw mouse position
  stroke(0);
  line(mouseX, 0, mouseX, 50);
  line(0, mouseY, 50, mouseY);
}

let worms = [];

function setup() {
  createCanvas(1000, 1000);
  setupConstants();
  print("Sketch pixel density: " + pixelDensity());

  for (let i = 0; i < N_WORMS; i++) {
    worms.push(new Worm(i));
  }

  background(255);
}

function draw() {
  // Clear screen
  background(255);

  for (let i = 0; i < N_WORMS; i++) {
    worms[i].step();
    worms[i].display();
  }

  displayDebugInfo();
}
