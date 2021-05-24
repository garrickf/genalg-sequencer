// Processing sketch for the interactive viz
// TODO: integrate API calls, integrate React

const s = (p) => {
  /* =================== Sketch constants =================== */
  const MARGIN = 100;
  const N_WORMS = 16;
  const WORM_LENGTH = 16;
  const WORM_DIAMETER = 14;
  const WORM_RADIUS = WORM_DIAMETER / 2;
  // How far apart segments are spaced (affects smoothness of body)
  const SPACING = 4;

  const RED = p.color(255, 0, 0);
  const RED_ALPHA = p.color(255, 0, 0, 100);
  const GREEN_ALPHA = (alpha) => p.color(0, 255, 0, alpha);
  const GRAY_ALPHA = (alpha) => p.color(100, 100, 100, alpha);
  const TURN_RADIUS = p.radians(1);
  const UNIT_NORTH = new p5.Vector(0, 1);
  const randomColor = () => {
    const r = p.random(255);
    const g = p.random(255);
    const b = p.random(255);
    return [r, g, b];
  };

  class Worm {
    constructor(idx) {
      this.head = new p5.Vector(p.width / 2, p.height / 2);
      this.heading = p5.Vector.random2D();
      this.desiredHeading = this.heading.copy();

      this.body = [];
      this.bodyOrientations = [];

      // Push reference
      this.body.push(this.head);
      this.bodyOrientations.push(this.heading);

      for (let i = 0; i < WORM_LENGTH - 1; i++) {
        this.body.push(this.head.copy());
        this.bodyOrientations.push(this.heading.copy());
      }

      this.name = "Worm " + idx;

      this.hovered = false;
      this.speed = 0.7 + p.random(1);

      // TODO: choose color based on instrument
      this.bodyColor = p.color(randomColor());
      this.stripeColor = p.color(randomColor());
    }

    /* =================== Drawing =================== */
    display() {
      p.push();
      p.stroke(this.bodyColor);
      p.fill(this.bodyColor);
      p.rectMode(p.CENTER);

      for (let i = 1; i < WORM_LENGTH; i++) {
        const radius = i == WORM_LENGTH - 1 ? WORM_RADIUS : WORM_RADIUS / 1.3;
        this._drawSegment(this.body[i], this.bodyOrientations[i], radius);
      }

      let stripePositions = [8, 12, 13, 14];
      for (let i = 0; i < stripePositions.length; i++) {
        this._drawStripe(
          this.body[stripePositions[i]],
          this.bodyOrientations[stripePositions[i]],
          1,
          this.stripeColor
        );
      }

      // Always include head, as a circle
      this._drawSegment(this.head, this.heading, WORM_RADIUS);
      p.pop();

      if (debugModeOn) {
        this._displayDebugInfo();
      }
    }

    _drawSegment(position, orientation, radius) {
      p.push(); // Save current drawing styles
      const angle = UNIT_NORTH.angleBetween(orientation);
      p.translate(position.x, position.y);
      p.rotate(angle);
      p.rect(0, 0, WORM_DIAMETER, WORM_DIAMETER, radius);
      p.pop();

      // Debug for orientation
      // p.push()
      // p.stroke(RED);
      // const nextPos = p5.Vector.add(
      //   position,
      //   p5.Vector.mult(orientation, 30)
      // );
      // p.line(position.x, position.y, nextPos.x, nextPos.y);
      // p.pop()
    }

    _drawStripe(position, orientation, width, color) {
      p.push();
      const angle = UNIT_NORTH.angleBetween(orientation);
      p.translate(position.x, position.y);
      p.rotate(angle);
      p.stroke(color);
      p.fill(color);
      p.rect(0, 0, WORM_DIAMETER, width);
      p.pop();
    }

    _displayDebugInfo() {
      p.stroke(RED);
      const nextPos = p5.Vector.add(
        this.head,
        p5.Vector.mult(this.heading, 30)
      );
      p.line(this.head.x, this.head.y, nextPos.x, nextPos.y);

      const desiredPos = p5.Vector.add(
        this.head,
        p5.Vector.mult(this.desiredHeading, 10)
      );
      p.line(this.head.x, this.head.y, desiredPos.x, desiredPos.y);

      const desiredAngle = this.heading.angleBetween(this.desiredHeading);
      p.textSize(8);
      p.noStroke();
      p.fill(RED);
      p.text(
        p.degrees(desiredAngle).toFixed(2) + " deg",
        this.head.x + 10,
        this.head.y + 10,
        90,
        20
      );

      // Draw hover selection area
      p.noStroke();
      if (this.hovered) {
        p.fill(GREEN_ALPHA(150));
      } else {
        p.fill(GRAY_ALPHA(150));
      }

      p.ellipse(this.head.x, this.head.y, WORM_DIAMETER * 4, WORM_DIAMETER * 4);
    }

    /* =================== Mouse events =================== */
    handleMouseOver(loc) {
      if (p5.Vector.dist(loc, this.head) < WORM_DIAMETER * 2) {
        if (!this.hovered) {
          p.print(this.name + " was hovered over");
          this.hovered = true;
          this.speed = 0.2;

          this.bodyColor = p.color(randomColor());
          this.stripeColor = p.color(randomColor());
          p.cursor("pointer");
        }
      } else if (this.hovered) {
        p.print(this.name + " hover exit");
        this.hovered = false;
        this.speed = 1;
        p.cursor("default");
      }
    }

    /* =================== Step =================== */
    step() {
      // Update all segments, in reverse order
      for (let i = WORM_LENGTH - 1; i > 0; i--) {
        const target = this.body[i - 1];
        const curr = this.body[i];

        if (p5.Vector.dist(target, curr) < SPACING) continue;

        const direction = p5.Vector.sub(target, curr);
        direction.limit(this.speed);
        curr.add(direction);

        const angle = this.bodyOrientations[i].angleBetween(
          this.bodyOrientations[i - 1]
        );
        this.bodyOrientations[i].rotate((angle * this.speed) / SPACING);
      }

      // Update head position
      this.head.add(p5.Vector.mult(this.heading, this.speed));

      const desiredAngle = this.heading.angleBetween(this.desiredHeading);
      const turnAngle = p.min(p.abs(desiredAngle), TURN_RADIUS);
      if (desiredAngle > 0) {
        this.heading.rotate(turnAngle * this.speed);
      } else if (desiredAngle < 0) {
        this.heading.rotate(-turnAngle * this.speed);
      }
    }

    applyForces(otherWorms) {
      // Avoiding walls is weighted more than the others
      this.desiredHeading.add(p5.Vector.mult(this._avoidWalls(), 100));
      this.desiredHeading.add(this._explore());
      this.desiredHeading.add(this._avoidOthers(otherWorms));
      this.desiredHeading.limit(1);
    }

    /* =================== Behavior =================== */
    _avoidWalls() {
      let desiredX = this.head.x;
      let desiredY = this.head.y;
      if (this.head.x < MARGIN) {
        desiredX = p.width;
      } else if (this.head.x > p.width - MARGIN) {
        desiredX = 0;
      }

      if (this.head.y < MARGIN) {
        desiredY = p.height;
      } else if (this.head.y > p.height - MARGIN) {
        desiredY = 0;
      }

      if (
        this.head.x < MARGIN ||
        this.head.x > p.width - MARGIN ||
        this.head.y < MARGIN ||
        this.head.y > p.height - MARGIN
      ) {
        const target = new p5.Vector(desiredX, desiredY);
        return p5.Vector.sub(target, this.head).limit(1);
      }
      return new p5.Vector(0, 0);
    }

    _explore() {
      // With some probability, head in a different direction
      if (p.random(1) < 0.03) {
        return p5.Vector.random2D();
      }
      return new p5.Vector(0, 0);
    }

    _avoidOthers(otherWorms) {
      let away = new p5.Vector(0, 0);
      for (let i = 0; i < N_WORMS; i++) {
        if (otherWorms[i] === this) continue;

        if (p5.Vector.dist(otherWorms[i].head, this.head) < 100) {
          away.add(p5.Vector.sub(this.head, otherWorms[i].head));
        }
      }

      away.limit(1);
      return away;
    }
  }

  /* =================== Sketch draw functions =================== */
  function displayDebugInfo() {
    // Draw red boxes around borders (worms should turn around)
    p.push();
    p.noStroke();
    p.fill(RED_ALPHA);

    p.rect(0, 0, p.width, MARGIN);
    p.rect(0, p.height - MARGIN, p.width, MARGIN);
    p.rect(0, MARGIN, MARGIN, p.height - MARGIN * 2);
    p.rect(p.width - MARGIN, MARGIN, MARGIN, p.height - MARGIN * 2);

    // Draw mouse position
    p.stroke(0);
    p.line(p.mouseX, 0, p.mouseX, 50);
    p.line(0, p.mouseY, 50, p.mouseY);
    p.pop();
  }

  /* =================== Sketch input events =================== */
  // Global, propagates mouseOver events to objects which need them
  function handleMouseMoved() {
    const location = new p5.Vector(p.mouseX, p.mouseY);
    for (let i = 0; i < worms.length; i++) {
      worms[i].handleMouseOver(location);
    }
  }

  p.keyTyped = () => {
    if (p.key === "d") {
      debugModeOn = !debugModeOn;
    } else if (p.key === " ") {
      p.print("Advance generation");
    }
  };

  // Global state
  let worms = [];
  let debugModeOn = false; // TODO: set to false

  /* =================== Setup and draw =================== */
  p.setup = () => {
    p.frameRate(60);
    const cvs = p.createCanvas(1000, 1000);
    cvs.mouseMoved(handleMouseMoved);
    p.print("Sketch pixel density: " + p.pixelDensity());

    for (let i = 0; i < N_WORMS; i++) {
      worms.push(new Worm(i));
    }

    p.background(255);

    // TODO: expose getting frame rate to application
    // setInterval(() => {
    //   p.print(p.frameRate());
    // }, 1000);
  };

  p.draw = () => {
    // Clear screen
    p.background(255);

    for (let i = 0; i < worms.length; i++) {
      worms[i].applyForces(worms);
      worms[i].step();
      worms[i].display();
    }

    if (debugModeOn) {
      displayDebugInfo();
    }
  };
};

let mySketch = new p5(s);
