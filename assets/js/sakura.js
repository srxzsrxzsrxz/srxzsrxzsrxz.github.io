// Falling Sakura Petals Animation
(function() {
  const canvas = document.createElement('canvas');
  canvas.id = 'sakura-canvas';
  document.body.appendChild(canvas);
  const ctx = canvas.getContext('2d');

  let width = canvas.width = window.innerWidth;
  let height = canvas.height = window.innerHeight;

  window.addEventListener('resize', () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  });

  const petals = [];
  const TOTAL_PETALS = 28;

  class Petal {
    constructor() {
      this.reset(true);
    }

    reset(initial = false) {
      this.x = Math.random() * width;
      this.y = initial ? Math.random() * height : -20;
      this.size = Math.random() * 8 + 8;
      this.speedX = Math.random() * 1.5 - 0.5;
      this.speedY = Math.random() * 1.2 + 0.8;
      this.rotation = Math.random() * 360;
      this.rotSpeed = (Math.random() - 0.5) * 1.5;
      this.opacity = Math.random() * 0.5 + 0.4;
      this.color = Math.random() > 0.4 ? 'rgba(255, 183, 197,' : 'rgba(244, 114, 182,';
    }

    update() {
      this.x += this.speedX + Math.sin(this.y * 0.01) * 0.6;
      this.y += this.speedY;
      this.rotation += this.rotSpeed;

      if (this.y > height + 20 || this.x > width + 20 || this.x < -20) {
        this.reset();
      }
    }

    draw() {
      ctx.save();
      ctx.translate(this.x, this.y);
      ctx.rotate((this.rotation * Math.PI) / 180);
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.bezierCurveTo(-this.size / 2, -this.size / 2, -this.size, this.size / 3, 0, this.size);
      ctx.bezierCurveTo(this.size, this.size / 3, this.size / 2, -this.size / 2, 0, 0);
      ctx.fillStyle = `${this.color} ${this.opacity})`;
      ctx.fill();
      ctx.restore();
    }
  }

  for (let i = 0; i < TOTAL_PETALS; i++) {
    petals.push(new Petal());
  }

  let animationId;
  let isRunning = true;

  function loop() {
    if (!isRunning) return;
    ctx.clearRect(0, 0, width, height);
    for (let p of petals) {
      p.update();
      p.draw();
    }
    animationId = requestAnimationFrame(loop);
  }

  loop();

  // Sakura toggle helper
  window.toggleSakura = function() {
    isRunning = !isRunning;
    if (isRunning) {
      loop();
      return true;
    } else {
      cancelAnimationFrame(animationId);
      ctx.clearRect(0, 0, width, height);
      return false;
    }
  };
})();
