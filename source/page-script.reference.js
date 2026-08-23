
(function(){
  "use strict";
  var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------------------------------------------------------
     1. reveals
     --------------------------------------------------------- */
  var revealables = document.querySelectorAll(".rv");
  if (reduce || !("IntersectionObserver" in window)) {
    revealables.forEach(function(el){ el.classList.add("in"); });
  } else {
    var ro = new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if (e.isIntersecting) { e.target.classList.add("in"); ro.unobserve(e.target); }
      });
    }, { threshold: 0.18, rootMargin: "0px 0px -8% 0px" });
    revealables.forEach(function(el){ ro.observe(el); });
  }

  /* ---------------------------------------------------------
     2. the garden wipe — dead to alive
     --------------------------------------------------------- */
  var wipe = document.getElementById("wipe");
  if (wipe) {
    var pos = 0, dragging = false, swept = false;

    function paint(v){
      pos = Math.max(0, Math.min(100, v));
      wipe.style.setProperty("--x", pos + "%");
      wipe.setAttribute("aria-valuenow", Math.round(pos));
      wipe.setAttribute("aria-valuetext",
        pos < 8 ? "grey" : pos > 92 ? "fully in colour" : Math.round(pos) + "% back in colour");
    }
    function fromEvent(clientX){
      var r = wipe.getBoundingClientRect();
      paint(((clientX - r.left) / r.width) * 100);
    }
    function touched(){ wipe.classList.add("is-touched"); }

    wipe.addEventListener("pointerdown", function(e){
      dragging = true; swept = true; touched();
      wipe.setPointerCapture(e.pointerId);
      fromEvent(e.clientX);
    });
    wipe.addEventListener("pointermove", function(e){
      if (dragging) { e.preventDefault(); fromEvent(e.clientX); }
    });
    ["pointerup","pointercancel"].forEach(function(t){
      wipe.addEventListener(t, function(){ dragging = false; });
    });
    wipe.addEventListener("keydown", function(e){
      var step = e.shiftKey ? 12 : 4, handled = true;
      if (e.key === "ArrowRight" || e.key === "ArrowUp") paint(pos + step);
      else if (e.key === "ArrowLeft" || e.key === "ArrowDown") paint(pos - step);
      else if (e.key === "Home") paint(0);
      else if (e.key === "End") paint(100);
      else handled = false;
      if (handled) { e.preventDefault(); swept = true; touched(); }
    });

    /* auto-sweep once, when it first comes into view */
    function sweep(){
      var start = null, from = pos, to = 64, dur = 2000;
      function frame(t){
        if (swept) return;                 /* hand over the moment they touch it */
        if (start === null) start = t;
        var p = Math.min(1, (t - start) / dur);
        var eased = 1 - Math.pow(1 - p, 3);
        paint(from + (to - from) * eased);
        if (p < 1) requestAnimationFrame(frame);
      }
      requestAnimationFrame(frame);
    }

    if (reduce) {
      paint(55); touched();
    } else if ("IntersectionObserver" in window) {
      var wo = new IntersectionObserver(function(entries){
        entries.forEach(function(e){
          if (e.isIntersecting) { wo.disconnect(); setTimeout(sweep, 420); }
        });
      }, { threshold: 0.45 });
      wo.observe(wipe);
    } else {
      paint(55);
    }
  }

  /* ---------------------------------------------------------
     3. parallax + scroll progress
     --------------------------------------------------------- */
  var layers = [].slice.call(document.querySelectorAll(".mv__bg img"));
  var bar = document.getElementById("progress");
  var ticking = false;

  function onScroll(){
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function(){
      var vh = window.innerHeight;

      if (bar) {
        var doc = document.documentElement;
        var max = doc.scrollHeight - vh;
        bar.style.transform = "scaleX(" + (max > 0 ? Math.min(1, doc.scrollTop / max) : 0) + ")";
      }

      if (!reduce) {
        for (var i = 0; i < layers.length; i++) {
          var el = layers[i];
          var r = el.parentNode.getBoundingClientRect();
          if (r.bottom < -200 || r.top > vh + 200) continue;
          /* -1 .. 1 across the viewport */
          var t = (r.top + r.height / 2 - vh / 2) / vh;
          el.style.transform = "translate3d(0," + (t * -5.5).toFixed(2) + "%,0) scale(1.14)";
        }
      }
      ticking = false;
    });
  }
  addEventListener("scroll", onScroll, { passive: true });
  addEventListener("resize", onScroll, { passive: true });
  onScroll();

  /* ---------------------------------------------------------
     4. ambient particles — embers by the fire, starlight after
     --------------------------------------------------------- */
  var cv = document.getElementById("amb");
  var ctx = cv.getContext("2d");
  var W = 0, H = 0, DPR = 1, parts = [], mode = "star", running = false;

  function size(){
    DPR = Math.min(window.devicePixelRatio || 1, 2);
    W = cv.width  = Math.floor(innerWidth  * DPR);
    H = cv.height = Math.floor(innerHeight * DPR);
    cv.style.width  = innerWidth + "px";
    cv.style.height = innerHeight + "px";
  }
  size();
  addEventListener("resize", function(){ size(); parts = []; }, { passive: true });

  function rnd(a, b){ return a + Math.random() * (b - a); }

  function spawn(kind){
    if (kind === "ember") {
      return { k:"ember",
        x: rnd(0, W), y: rnd(H * 0.75, H * 1.1),
        vx: rnd(-0.14, 0.14) * DPR, vy: rnd(-0.5, -0.16) * DPR,
        r: rnd(0.7, 2.1) * DPR, life: 0, max: rnd(320, 720),
        ph: rnd(0, 6.28), sway: rnd(0.004, 0.014) };
    }
    return { k:"star",
      x: rnd(0, W), y: rnd(0, H),
      vx: rnd(-0.05, 0.05) * DPR, vy: rnd(-0.035, 0.035) * DPR,
      r: rnd(0.4, 1.25) * DPR, life: 0, max: rnd(600, 1400),
      ph: rnd(0, 6.28), sway: 0 };
    }

  function target(){
    if (mode === "off") return 0;
    return mode === "ember" ? 74 : 120;
  }

  function step(){
    running = true;
    ctx.clearRect(0, 0, W, H);

    var want = target();
    if (parts.length < want) {
      for (var n = 0; n < 2 && parts.length < want; n++) parts.push(spawn(mode));
    }

    for (var i = parts.length - 1; i >= 0; i--) {
      var p = parts[i];
      p.life++;
      if (p.life > p.max || p.y < -40 || parts.length > want + 40) { parts.splice(i, 1); continue; }

      p.ph += 0.03;
      p.x += p.vx + (p.sway ? Math.sin(p.ph) * p.sway * DPR * 6 : 0);
      p.y += p.vy;

      /* fade in, hold, fade out */
      var q = p.life / p.max;
      var a = q < 0.14 ? q / 0.14 : (q > 0.7 ? (1 - q) / 0.3 : 1);

      if (p.k === "ember") {
        a *= 0.55 + Math.sin(p.ph * 1.7) * 0.28;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, 6.2832);
        ctx.fillStyle = "rgba(255," + Math.round(rnd(130, 178)) + "," + Math.round(rnd(70, 108)) + "," + Math.max(0, a).toFixed(3) + ")";
        ctx.shadowBlur = 9 * DPR;
        ctx.shadowColor = "rgba(255,122,69,.85)";
        ctx.fill();
        ctx.shadowBlur = 0;
      } else {
        a *= 0.4 + Math.sin(p.ph * 0.5) * 0.3;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, 6.2832);
        ctx.fillStyle = "rgba(226,238,250," + Math.max(0, a).toFixed(3) + ")";
        ctx.fill();
      }
    }

    if (parts.length === 0 && target() === 0) { running = false; return; }
    requestAnimationFrame(step);
  }

  /* which movement owns the screen decides the particles */
  if (!reduce && "IntersectionObserver" in window) {
    var sections = document.querySelectorAll("[data-mode]");
    var mo = new IntersectionObserver(function(entries){
      var best = null, bestRatio = 0;
      entries.forEach(function(e){
        if (e.intersectionRatio > bestRatio) { bestRatio = e.intersectionRatio; best = e.target; }
      });
      if (best && bestRatio > 0.34) {
        mode = best.getAttribute("data-mode");
        if (!running && mode !== "off") requestAnimationFrame(step);
      }
    }, { threshold: [0.35, 0.6, 0.9] });
    sections.forEach(function(s){ mo.observe(s); });
    requestAnimationFrame(step);
  } else if (reduce) {
    /* one still starfield, no motion */
    for (var s = 0; s < 90; s++) {
      var x = rnd(0, W), y = rnd(0, H), r = rnd(0.4, 1.3) * DPR;
      ctx.beginPath(); ctx.arc(x, y, r, 0, 6.2832);
      ctx.fillStyle = "rgba(226,238,250," + rnd(0.15, 0.5).toFixed(3) + ")";
      ctx.fill();
    }
  }
})();
