/* HalfTime Chews v2: scroll + interactions */
(() => {
  const RM = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const TEAR = 0.115;          // tear line, fraction of pack image height

  if (RM) document.documentElement.classList.add('rm');

  /* ---------- smooth scroll ---------- */
  let lenis = null;
  if (!RM && window.Lenis) {
    lenis = new Lenis({ lerp: 0.11, smoothWheel: true });
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add(t => lenis.raf(t * 1000));
    gsap.ticker.lagSmoothing(0);
  }
  gsap.registerPlugin(ScrollTrigger);

  const goTo = (sel) => {
    const el = $(sel); if (!el) return;
    if (lenis) lenis.scrollTo(el, { offset: -70, duration: 1.2 });
    else el.scrollIntoView({ behavior: RM ? 'auto' : 'smooth' });
  };
  $$('a[href^="#"]').forEach(a => a.addEventListener('click', e => {
    const h = a.getAttribute('href'); if (h.length < 2) return;
    e.preventDefault();
    // #flavors lives inside the pinned stage: jump to the start of scene 1
    if (h === '#flavors' && tl && tl.scrollTrigger) {
      const st = tl.scrollTrigger, y = st.start + (st.end - st.start) * (SC[0] + 0.02) / tl.duration();
      if (lenis) lenis.scrollTo(y, { duration: 1.4 }); else window.scrollTo(0, y);
      return;
    }
    goTo(h);
  }));

  const nav = $('.nav');
  ScrollTrigger.create({ start: 40, onToggle: s => nav.classList.toggle('solid', s.isActive) });

  /* ---------- HERO + FLAVOR STAGE ---------- */
  const stage = $('#stage'), inner = $('.stage-in');
  const packw = $('.packw'), closed = $('.pk-closed'), torn = $('.pk-torn'), strip = $('.pk-strip');
  const tearLine = $('.tear-line'), heroCopy = $('.hero-copy'), heroInfo = $('.hero-info');
  const gHero = $('.g-hero'), gS = $$('.g-s'), scenes = $$('.scene'), dock = $('.dock'), dks = $$('.dk');
  const chews = $$('.chew'), objsBox = $('.objs');
  let tl = null;
  const ring = $('.ring');
  // hero backdrop: ?bg=a|b|c for testing, default set on .stage-in
  const bgq = new URLSearchParams(location.search).get('bg');
  if (bgq) inner.dataset.bg = bgq;
  const bgx = $('.bgx'), ctags = $$('.ctag');
  { const d = $('.bgx-dust'); for (let i = 0; i < 26; i++) { const e = document.createElement('i'); const r = Math.random;
      e.style.cssText = `left:${(48 + r() * 52).toFixed(1)}%;--s:${(1.5 + r() * 2.5).toFixed(1)}px;--t:${(7 + r() * 9).toFixed(1)}s;--dl:${(-r() * 16).toFixed(1)}s;--dx:${(-30 + r() * 60).toFixed(0)}px;--o:${(0.15 + r() * 0.4).toFixed(2)}`;
      d.appendChild(e); } }
  $$('.sc-name').forEach(h => {
    const t = h.textContent; h.setAttribute('aria-label', t);
    h.innerHTML = [...t].map(c => `<span class="ch" aria-hidden="true">${c}</span>`).join('');
  });
  // mouse depth parallax on the floating fruit (desktop)
  if (!RM) inner.addEventListener('pointermove', e => {
    if (e.pointerType !== 'mouse') return;
    const r = inner.getBoundingClientRect();
    inner.style.setProperty('--mx', ((e.clientX - r.left) / r.width - 0.5) * 2);
    inner.style.setProperty('--my', ((e.clientY - r.top) / r.height - 0.5) * 2);
  });

  // scene start times (timeline units; hero = 0 to ~0.6)
  const SC = [0.62, 1.16, 1.70], END = 2.24;

  // flavor objects: [file, x, y, size, depth, rot]; desktop size = fraction of H, phone = fraction of W
  const OB = {
    d: [
      [['citrus-0', .87, .28, .22, 1.2, -12], ['citrus-1', .55, .74, .19, 1, 18], ['citrus-2', .89, .74, .17, .8, -20], ['citrus-3', .57, .24, .14, .6, 10], ['citrus-4', .74, .9, .1, .5, 30]],
      [['berry-0', .1, .28, .16, 1.1, -15], ['berry-2', .47, .25, .14, .8, 12], ['berry-4', .13, .8, .13, 1.25, 0], ['berry-1', .42, .8, .13, .6, 25], ['berry-3', .64, .2, .08, .45, -10], ['berry-5', .03, .52, .09, .5, 0], ['berry-6', .86, .9, .08, .4, 0]],
      [['watermelon-0', .2, .5, .2, 1.15, -14], ['watermelon-1', .8, .48, .19, .9, 16], ['watermelon-2', .11, .78, .16, 1.25, 8], ['watermelon-3', .33, .72, .06, .7, 20], ['watermelon-4', .67, .76, .065, 1.05, -30], ['watermelon-5', .9, .72, .055, .55, 40], ['watermelon-6', .76, .87, .05, .45, 0], ['watermelon-1', .07, .15, .08, .4, -30]]
    ],
    p: [
      [['citrus-0', .15, .57, .26, 1.1, -12], ['citrus-2', .86, .56, .24, .9, -20], ['citrus-1', .84, .8, .26, 1.2, 18], ['citrus-3', .15, .8, .22, .65, 10]],
      [['berry-0', .13, .57, .22, 1.1, -15], ['berry-2', .87, .56, .2, .8, 12], ['berry-4', .85, .8, .18, 1.2, 0], ['berry-1', .16, .8, .2, .65, 25]],
      [['watermelon-0', .15, .57, .25, 1.1, -14], ['watermelon-1', .86, .58, .24, .9, 16], ['watermelon-2', .83, .83, .24, 1.2, 8], ['watermelon-3', .18, .82, .09, .7, 20]]
    ]
  };
  // where the big chew sits in each scene: [x, y, size factor]
  const BIG = { d: [[.69, .5, 1], [.3, .5, 1], [.5, .7, .7]], p: [[.5, .68, 1], [.5, .68, 1], [.5, .68, 1]] };

  function layout() {
    const W = inner.clientWidth, H = inner.clientHeight, phone = W < 820;
    let h, x, y;
    if (phone) {
      const h1b = $('.hero-copy h1').getBoundingClientRect().bottom - inner.getBoundingClientRect().top;
      const infoTop = heroInfo.getBoundingClientRect().top - inner.getBoundingClientRect().top;
      y = h1b + 10;
      h = Math.max(220, Math.min(H * 0.46, infoTop - 8 - y));
      x = W - h * 0.714 * 0.96;
    } else {
      h = H * 0.76;
      x = W - W * 0.08 - h * 0.714;
      y = H * 0.12;
    }
    const w = h * 0.714;
    const cw = phone ? Math.min(96, w * 0.42) : Math.min(180, Math.max(110, w * 0.3));
    const big = phone ? Math.min(W * 0.5, H * 0.26) : Math.min(H * 0.42, W * 0.3);
    return { W, H, phone, x, y, w, h, cw, big };
  }

  function placeStatic(L) {
    gsap.set(packw, { left: L.x, top: L.y, width: L.w, height: L.h, rotation: L.phone ? -3 : -5 });
    tearLine.style.top = (L.y + L.h * TEAR) + 'px';
    tearLine.style.left = Math.max(0, L.x - (L.phone ? 24 : L.W * 0.07)) + 'px';
    chews.forEach(c => c.style.setProperty('--cw', L.cw + 'px'));
  }

  function makeObjects(L) {
    objsBox.replaceChildren();
    return OB[L.phone ? 'p' : 'd'].map(list => list.map(([f, x, y, s, d, r]) => {
      const el = document.createElement('div');
      el.className = 'ob' + (d < 0.66 ? ' far' : '');
      const im = document.createElement('img'); im.src = 'img/o-' + f + '.webp'; im.alt = ''; im.decoding = 'async';
      el.appendChild(im);
      const size = s * (L.phone ? L.W : L.H);
      el.style.width = size + 'px';
      el.style.zIndex = d > 1 ? 6 : 2; el.style.setProperty('--d', d);          // near objects pass in front of the chew, never over copy (placed away from it)
      objsBox.appendChild(el);
      gsap.set(el, { left: x * L.W, top: y * L.H, xPercent: -50, yPercent: -50, rotation: r, opacity: 0 });
      return { el, d, r, ox: x * L.W, oy: y * L.H };
    }));
  }

  function build() {
    if (tl) { tl.scrollTrigger && tl.scrollTrigger.kill(); tl.kill(); tl = null; }
    gsap.set([strip, closed, torn, packw, heroCopy, heroInfo, tearLine, gHero, bgx, ...ctags, ...gS, ...scenes, dock, ...chews], { clearProps: 'transform,opacity,zIndex' });
    const L = layout();
    placeStatic(L);
    if (RM) return;

    const objs = makeObjects(L);
    const mouthX = L.x + L.w / 2, drop = L.phone ? L.H * 0.06 : L.H * 0.13;
    const mouthY = L.y + L.h * TEAR + drop;
    const c = L.cw / 2;
    const floatPos = L.phone
      ? [[mouthX - L.w * 0.62, mouthY - L.h * 0.2], [mouthX + L.w * 0.02, mouthY - L.h * 0.42], [mouthX + L.w * 0.2, mouthY - L.h * 0.14]]
      : [[mouthX - L.w * 0.78, mouthY + L.h * 0.04], [mouthX - L.w * 0.14, mouthY - L.h * 0.14], [mouthX + L.w * 0.4, mouthY - L.h * 0.1]];
    const rots = [-14, 9, 18];

    // dock slot centers (dock is static; only its opacity animates)
    const ir = inner.getBoundingClientRect();
    const slot = $$('.dk i').map(i => { const r = i.getBoundingClientRect(); return [r.left - ir.left + r.width / 2, r.top - ir.top + r.height / 2, r.width]; });
    const B = BIG[L.phone ? 'p' : 'd'];
    const toBig = (i, rot) => ({ x: B[i][0] * L.W - c, y: B[i][1] * L.H - c, scale: L.big * B[i][2] / L.cw, rotation: rot });
    const cxy = i => [B[i][0] * L.W, B[i][1] * L.H];
    const toDock = i => ({ x: slot[i][0] - c, y: slot[i][1] - c, scale: (slot[i][2] * 0.92) / L.cw, rotation: 0 });

    chews.forEach(ch => gsap.set(ch, { x: mouthX - c, y: mouthY + L.h * 0.06 - c, scale: 0.35, opacity: 0, zIndex: 2 }));

    tl = gsap.timeline({
      defaults: { ease: 'sine.inOut' },
      scrollTrigger: {
        trigger: stage, start: 'top top', end: () => '+=' + Math.round(L.H * (L.phone ? 1.9 : 2.0) * END),
        scrub: 0.9, pin: true, anticipatePin: 1, invalidateOnRefresh: false,
        onUpdate: s => {
          // use scroll progress, not tl.time(): the scrubbed time lags and the last onUpdate can fire before it catches up
          const t = s.progress * END; let on = -1;
          if (t > SC[0] - 0.04) on = t < SC[1] - 0.05 ? 0 : t < SC[2] - 0.05 ? 1 : 2;
          dks.forEach((d, i) => d.classList.toggle('on', i === on));
          scenes.forEach((s, i) => s.classList.toggle('active', i === on && t > SC[i] + 0.02));
          stage.classList.toggle('in-flavors', on >= 0);
        }
      }
    });

    // 0.00–0.08 hold, info readable. RIP: strip tears up and away.
    tl.set(closed, { opacity: 0 }, 0.08).set(torn, { opacity: 1 }, 0.08)
      .to(packw, { rotation: L.phone ? -1 : -2.5, duration: 0.06, ease: 'power2.out' }, 0.08)
      .to(strip, { y: -L.h * 0.07, x: L.w * 0.05, rotation: 7, duration: 0.06, ease: 'power2.out' }, 0.08)
      .to(strip, { y: -L.h * 0.7, x: L.w * 0.75, rotation: 48, duration: 0.14, ease: 'power2.in' }, 0.14)
      .to(strip, { opacity: 0, duration: 0.05 }, 0.23)
      .to(tearLine, { opacity: 0, duration: 0.06 }, 0.12)
      .to(packw, { y: drop, duration: 0.14, ease: 'power2.inOut' }, 0.16);
    if (L.phone) tl.to(heroCopy, { opacity: 0, y: -30, duration: 0.08 }, 0.12);

    // POP: chews rise out of the opening and float
    chews.forEach((ch, i) => {
      const t0 = 0.24 + i * 0.035;
      tl.to(ch, { opacity: 1, y: mouthY - L.h * 0.1 - c, scale: 0.7, duration: 0.05, ease: 'power2.out' }, t0)
        .set(ch, { zIndex: 4 }, t0 + 0.05)
        .to(ch, { x: floatPos[i][0] - c, y: floatPos[i][1] - c, scale: 1, rotation: rots[i], duration: 0.1, ease: 'back.out(1.6)' }, t0 + 0.05);
    });

    // DETAIL TAGS: each floating chew gets its flavor name + one line
    // [dx, dy, side] from the chew center, in units of the chew half-size c
    const TG = L.phone ? [[-1, 1.15, 'l'], [-1.1, -0.2, 'r'], [0, -1.7, 'c']] : [[-1.15, -0.3, 'r'], [-1.25, -0.35, 'r'], [-0.9, -1.75, 'l']];
    ctags.forEach((tg, i) => {
      const [dx, dy, side] = TG[i]; tg.classList.toggle('r', side === 'r');
      // anchor, then keep the whole tag on screen (12px margin)
      const w = tg.offsetWidth, ax = floatPos[i][0] + dx * c;
      const lx = Math.min(Math.max(12, side === 'r' ? ax - w : side === 'c' ? ax - w / 2 : ax), L.W - 12 - w);
      const ty = floatPos[i][1] + dy * c;
      gsap.set(tg, { left: lx, top: ty, xPercent: 0, opacity: 0, y: 10 });
      // never over the headline: if it would touch an h1 line, this tag stays hidden
      const ir2 = inner.getBoundingClientRect(), th = tg.offsetHeight;
      const hit = !L.phone && $$('.hero-copy h1 span').some(sp => { const g = document.createRange(); g.selectNodeContents(sp); const r = g.getBoundingClientRect();
        return lx < r.right - ir2.left + 8 && lx + w > r.left - ir2.left - 8 && ty < r.bottom - ir2.top && ty + th > r.top - ir2.top; });
      if (hit) return;
      tl.to(tg, { opacity: 1, y: 0, duration: 0.05, ease: 'power2.out' }, 0.32 + i * 0.015)
        .to(tg, { opacity: 0, y: -10, duration: 0.04, ease: 'power1.in' }, 0.46);
    });
    tl.to(bgx, { opacity: 0, duration: 0.1 }, 0.5);

    // HAND-OFF: hero leaves, pack drops away, citrus world comes in
    tl.to([heroCopy, heroInfo], { opacity: 0, y: -40, duration: 0.08, ease: 'power1.in' }, 0.48)
      .to(packw, { y: drop + L.H * 0.7, rotation: 8, opacity: 0, duration: 0.1, ease: 'power2.in' }, 0.47)
      .to(gHero, { opacity: 0, duration: 0.1 }, 0.52)
      .to(dock, { opacity: 1, duration: 0.06 }, 0.56);
    // chew 1 grows into scene 1, chews 2 + 3 wait in the dock
    chews.forEach(ch => tl.set(ch, { zIndex: 5 }, 0.53));
    tl.to(chews[0], { ...toBig(0, -10), duration: 0.14, ease: 'back.out(1.25)' }, 0.53)
      .to(chews[1], { ...toDock(1), duration: 0.13, ease: 'power3.inOut' }, 0.55)
      .to(chews[2], { ...toDock(2), duration: 0.13, ease: 'power3.inOut' }, 0.57);

    // SCENES
    scenes.forEach((sc, i) => {
      const S = SC[i], next = SC[i + 1];
      tl.fromTo(gS[i], { opacity: 0 }, { opacity: 1, duration: 0.12, immediateRender: false }, S - 0.08)
        .fromTo(sc, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.08, ease: 'power2.out', immediateRender: false }, S - 0.01)
        .fromTo($$('.ch', sc), { yPercent: 70, opacity: 0, rotation: 8 }, { yPercent: 0, opacity: 1, rotation: 0, duration: 0.06, stagger: 0.008, ease: 'back.out(1.6)', immediateRender: false }, S - 0.01);
      // shockwave ring where the chew lands
      const [rx, ry] = cxy(i), rs = L.big * B[i][2] * 1.25;
      tl.set(ring, { left: rx - rs / 2, top: ry - rs / 2, width: rs, height: rs, borderColor: sc.style.getPropertyValue('--c') }, S - 0.05)
        .fromTo(ring, { scale: 0.55, opacity: 0.9 }, { scale: 1.9, opacity: 0, duration: 0.1, ease: 'power2.out', immediateRender: false }, S - 0.04);
      // the big chew turns slowly while the scene holds
      const hold = (next ?? END) - S;
      tl.to(chews[i], { rotation: 10, duration: hold - 0.06, ease: 'none' }, S + 0.02);
      // objects: rise in from below (near ones travel further), drift, then leave upward
      objs[i].forEach((o, k) => {
        const j = k * 0.012;
        const [bx, by] = cxy(i);
        tl.fromTo(o.el, { x: bx - o.ox, y: by - o.oy, scale: 0.15, opacity: 0, rotation: o.r - 160 * o.d },
          { x: 0, y: 0, scale: 1, opacity: o.d < 0.66 ? 0.75 : 1, rotation: o.r, duration: 0.11, ease: 'expo.out', immediateRender: false }, S - 0.04 + j * 0.4)
          .to(o.el, { y: -L.H * 0.07 * o.d, rotation: o.r + 8 * o.d, duration: hold - 0.12, ease: 'none' }, S + 0.06 + j);
        if (next) tl.to(o.el, { x: (o.ox - bx) * 0.6, y: -L.H * 0.95 * o.d, opacity: 0, duration: 0.12, ease: 'power2.in' }, next - 0.1 + j);
      });
      if (next) {
        tl.to(sc, { opacity: 0, y: -30, duration: 0.06, ease: 'power1.in' }, next - 0.09)
          .to(gS[i], { opacity: 0, duration: 0.12 }, next - 0.08)
          // swap: this chew goes back to its dock slot, the next one grows out of the dock
          .to(chews[i], { ...toDock(i), duration: 0.13, ease: 'power3.inOut' }, next - 0.1)
          .to(chews[i + 1], { ...toBig(i + 1, -10), duration: 0.14, ease: 'back.out(1.25)' }, next - 0.08);
      }
    });
    tl.to({}, { duration: 0.04 }, END - 0.04);
  }

  let rt;
  const rebuild = () => { build(); ScrollTrigger.refresh(); };
  window.addEventListener('resize', () => {
    clearTimeout(rt);
    rt = setTimeout(() => { if (Math.abs(window.innerWidth - (rebuild.w || 0)) > 40 || !rebuild.w) { rebuild.w = window.innerWidth; rebuild(); } }, 200);
  });
  const start = () => { rebuild.w = window.innerWidth; build(); ScrollTrigger.refresh(); window.__ready = true; };
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => requestAnimationFrame(start)); else window.addEventListener('load', start);

  /* ---------- reveal-on-view helpers ---------- */
  const onView = (el, fn, th = 0.35) => {
    if (!el) return;
    if (RM || !('IntersectionObserver' in window)) { fn(); return; }
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { fn(); io.disconnect(); } }), { threshold: th });
    io.observe(el);
  };

  /* ---------- PROBLEM: 950 counts up, the old fixes get crossed out ---------- */
  const prob = $('.prob'), n950 = $('.n950');
  if (!RM) n950.textContent = '0';
  onView(prob, () => {
    prob.classList.add('in');
    if (RM) { n950.textContent = '950'; return; }
    const t0 = performance.now(), D = 1300;
    const step = now => { const p = Math.min(1, (now - t0) / D), e = 1 - Math.pow(1 - p, 3); n950.textContent = Math.round(950 * e); if (p < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  });

  /* ---------- HOW: 30:00 clock drives the steps ---------- */
  const clock = $('.clock'), mm = $('.clock .mm'), ss = $('.clock .ss'), stps = $$('.stp');
  const pad = n => String(n).padStart(2, '0');
  const setClock = p => {
    const left = Math.max(0, Math.round(1800 * (1 - p / 0.82)));
    mm.textContent = pad(Math.floor(left / 60)); ss.textContent = pad(left % 60);
    clock.classList.toggle('zero', left === 0);
    const k = p < 0.3 ? 0 : p < 0.62 ? 1 : 2;
    stps.forEach((s, i) => s.classList.toggle('on', RM || i === k));
  };
  ScrollTrigger.create({ trigger: '.how', start: 'top top', end: 'bottom bottom', refreshPriority: -1, onUpdate: s => setClock(s.progress), onRefresh: s => setClock(s.progress) });

  /* ---------- INSIDE THE CHEW: halves part, numbers count up in the seam ---------- */
  const insRows = $$('.ins-row'), insCnt = $$('.ins-row .cnt');
  if (!RM) {
    const phone = () => innerWidth <= 720;
    insRows.forEach(r => { r.style.opacity = 0; });
    const it = gsap.timeline({ scrollTrigger: { trigger: '.inside', start: 'top top', end: 'bottom bottom', scrub: 0.6, refreshPriority: -1, invalidateOnRefresh: true } });
    it.fromTo('.ins-l', { x: () => phone() ? '1.5vw' : '2.2vw', rotate: 0 }, { x: () => phone() ? '-8vw' : '-19vw', rotate: -7, scale: () => phone() ? 1 : 0.94, ease: 'power2.inOut', duration: 1 }, 0)
      .fromTo('.ins-r', { x: () => phone() ? '-1.5vw' : '-2.2vw', rotate: 0 }, { x: () => phone() ? '8vw' : '19vw', rotate: 7, scale: () => phone() ? 1 : 0.94, ease: 'power2.inOut', duration: 1 }, 0)
      .fromTo('.ins-glow', { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, ease: 'power1.out', duration: 0.7 }, 0.25)
      .to({}, { duration: 0.35 });
    insRows.forEach((r, i) => it.fromTo(r, { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.18, ease: 'power2.out', immediateRender: false }, 0.45 + i * 0.09));
    const cnt = { p: 0 };
    it.fromTo(cnt, { p: 0 }, { p: 1, duration: 0.55, ease: 'power2.out', onUpdate: () => insCnt.forEach(el => { el.textContent = Math.round(+el.dataset.v * cnt.p); }) }, 0.45);
  }

  /* ---------- STRENGTH PICKER + WHAT'S INSIDE ---------- */
  const S = [
    { name: 'Green · Light', short: 'Green', mg: 150, use: 'Practice and the gym. Ages 14+.', age: '14+', c: '#3DD68C' },
    { name: 'Yellow · Hard', short: 'Yellow', mg: 250, use: 'Games and long runs. Ages 14+.', age: '14+', c: '#FFD23F' },
    { name: 'Red · Extreme', short: 'Red', mg: 500, use: 'Heat and long shifts. Ages 16+ only. Double the sodium of yellow, for salty sweaters.', age: '16+ only', c: '#E5484D' }
  ];
  const strengthSec = $('#strength');
  let level = 0, manual = null;
  const qs = $$('.q');
  function renderStrength() {
    const lv = manual ?? level, s = S[lv];
    strengthSec.style.setProperty('--cur', s.c);
    $('.res-name').textContent = s.name;
    $('.res-use').textContent = s.use;
    const b = $('.res-btn'); b.textContent = 'Order ' + s.short; b.dataset.s = lv;
    $$('.lu').forEach(l => l.classList.toggle('on', +l.dataset.s === lv));
    const rows = [
      `<div><span class="sod"><span><dt>Sodium</dt><dd>${s.mg} mg</dd></span><span class="bar"><i style="--w:${s.mg / 5}%"></i></span></span></div>`
    ];
    if (lv === 1) {
      rows.push('<div><dt>Potassium</dt><dd>75 mg</dd></div>', '<div><dt>Magnesium</dt><dd>12 mg</dd></div>', '<div><dt>Calcium</dt><dd>20 mg</dd></div>', '<div><dt>Calories</dt><dd>about 20</dd></div>');
    } else {
      rows.push(`<div class="na"><dt>Potassium, magnesium, calcium</dt><dd>${lv === 0 ? 'lighter than yellow' : 'amounts on yellow'}</dd></div>`);
    }
    rows.push(`<div><dt>Ages</dt><dd>${s.age}</dd></div>`);
    $('.fp-rows').innerHTML = rows.join('');
  }
  qs.forEach(q => q.addEventListener('click', () => {
    q.setAttribute('aria-pressed', q.getAttribute('aria-pressed') !== 'true');
    level = Math.min(2, qs.filter(x => x.getAttribute('aria-pressed') === 'true').length);
    manual = null; renderStrength();
  }));
  $$('.lu').forEach(l => l.addEventListener('click', () => { manual = +l.dataset.s; renderStrength(); }));
  $('.res-btn').addEventListener('click', () => {
    const r = $(`input[name=strength][value="${$('.res-btn').dataset.s}"]`); if (r) { r.checked = true; updateOrder(true); }
  });
  renderStrength();

  /* ---------- WHY: map dots pop in ---------- */
  onView($('.map'), () => $('.map').classList.add('in'), 0.4);

  /* ---------- WHERE: photo parallax ---------- */
  if (!RM) $$('.wh img').forEach(img => gsap.fromTo(img, { yPercent: -15 }, { yPercent: 0, ease: 'none', scrollTrigger: { trigger: img.closest('.wh'), start: 'top bottom', end: 'bottom top', scrub: true, refreshPriority: -1 } }));

  /* ---------- MOCK CHECKOUT ---------- */
  const form = $('#orderForm');
  const PRICE = { single: 1.49, box12: 14.99, team48: 49 };
  const LABEL = { single: 'Single pack', box12: 'Box of 12', team48: 'Team box of 48' };
  const teamColors = $('#teamColors'), fundraiser = $('#fundraiser'), colorPick = $('#colorPick');
  const qtyOut = $('#qty'), cartN = $('.cart-n');
  let qty = 1, color = null, touched = false;
  const money = n => '$' + n.toFixed(2);

  // box render + team-color recolor (label pixels: out = pixel + t * (team - lime))
  const boxCv = $('.sum-box'), bctx = boxCv.getContext('2d', { willReadFrequently: true });
  const LIME = [185, 233, 19];
  let boxBase = null, boxMask = null, boxColor = 'x';
  const loadImg = src => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.onerror = () => r(null); i.src = src; });
  async function ensureBox() {
    if (boxBase) return true;
    const [b, m] = await Promise.all([loadImg('img/box12.webp'), loadImg('img/box12-mask.png')]);
    if (!b) return false;
    boxCv.width = b.naturalWidth; boxCv.height = b.naturalHeight;
    bctx.drawImage(b, 0, 0); boxBase = bctx.getImageData(0, 0, boxCv.width, boxCv.height);
    if (m) { const t = document.createElement('canvas'); t.width = boxCv.width; t.height = boxCv.height; const tc = t.getContext('2d'); tc.drawImage(m, 0, 0, t.width, t.height); boxMask = tc.getImageData(0, 0, t.width, t.height).data; }
    return true;
  }
  async function paintBox(hex) {
    if (!(await ensureBox())) return;
    if (hex === boxColor) return; boxColor = hex;
    if (!hex || !boxMask) { bctx.putImageData(boxBase, 0, 0); return; }
    const k = [1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16));
    const src = boxBase.data, out = bctx.createImageData(boxBase), o = out.data;
    for (let p = 0; p < src.length; p += 4) {
      const t = boxMask[p] / 255 * 1.2;
      o[p] = src[p] + t * (k[0] - LIME[0]); o[p + 1] = src[p + 1] + t * (k[1] - LIME[1]); o[p + 2] = src[p + 2] + t * (k[2] - LIME[2]); o[p + 3] = src[p + 3];
    }
    bctx.putImageData(out, 0, 0);
  }

  function updateOrder(touch) {
    if (touch) touched = true;
    const size = form.size.value, lv = +form.strength.value, flavor = form.flavor.value;
    const isBox = size !== 'single';
    const teamOk = isBox && qty >= 10;
    teamColors.disabled = !teamOk; if (!teamOk) teamColors.checked = false;
    fundraiser.disabled = !isBox; if (!isBox) fundraiser.checked = false;
    colorPick.hidden = !teamColors.checked;
    if (teamColors.checked && !color) { color = $$('.cc')[0]; }
    $$('.cc').forEach(cc => cc.classList.toggle('on', teamColors.checked && cc === color));

    const total = PRICE[size] * qty;
    const lines = [
      [LABEL[size] + ' × ' + qty, money(total)],
      ['Strength', S[lv].short + ', ' + S[lv].mg + ' mg'],
      ['Flavor', flavor]
    ];
    if (teamColors.checked) lines.push(['Team colors', color.dataset.n]);
    if (fundraiser.checked) lines.push(['Your team keeps', money(5 * qty)]);
    $('.sum-lines').innerHTML = lines.map(([a, b]) => `<dt>${a}</dt><dd>${b}</dd>`).join('');
    $('#total').textContent = money(total);
    $('#sumNote').textContent = lv === 2 ? 'Red is for ages 16+ only.' : (isBox && qty < 10 ? 'Team colors unlock at 10+ boxes.' : '');
    $('.or-sum').style.setProperty('--cur', S[lv].c);
    boxCv.hidden = !isBox; $('.sum-pack').hidden = isBox;
    $('.sum-cap').hidden = !teamColors.checked;
    if (isBox) paintBox(teamColors.checked ? getComputedStyle(color).getPropertyValue('--k').trim() : '');
    qtyOut.textContent = qty;
    cartN.textContent = touched ? qty : 0; cartN.classList.toggle('on', touched);
    $('#done').hidden = true; const p = $('.place'); p.disabled = false; p.textContent = 'Place order';
  }
  form.addEventListener('change', () => updateOrder(true));
  $$('.qb').forEach(b => b.addEventListener('click', () => { qty = Math.max(1, Math.min(99, qty + +b.dataset.d)); updateOrder(true); }));
  $$('.cc').forEach(cc => cc.addEventListener('click', () => { color = cc; updateOrder(true); }));
  form.addEventListener('submit', e => {
    e.preventDefault();
    $('#done').hidden = false; const p = $('.place'); p.disabled = true; p.textContent = 'Order placed (demo)';
  });
  updateOrder(false);

  /* ---------- BUY RIGHT IN THE FLAVOR SCENES ---------- */
  const toast = $('.toast'), toastT = $('.toast-t'); let tt;
  $$('.sc-buy').forEach(box => {
    const pills = $$('.sp', box);
    pills.forEach(p => p.addEventListener('click', () => pills.forEach(x => { const on = x === p; x.classList.toggle('on', on); x.setAttribute('aria-pressed', on); })));
    $('.sc-add', box).addEventListener('click', e => {
      const fl = box.dataset.flavor, lv = +$('.sp.on', box).dataset.s;
      const same = form.size.value === 'single' && form.flavor.value === fl && +form.strength.value === lv && touched;
      $('input[name=size][value=single]').checked = true;
      $(`input[name=flavor][value="${fl}"]`).checked = true;
      $(`input[name=strength][value="${lv}"]`).checked = true;
      qty = same ? Math.min(99, qty + 1) : 1;
      updateOrder(true);
      const b = e.currentTarget; b.classList.remove('pop'); void b.offsetWidth; b.classList.add('pop');
      toastT.textContent = `Added ${fl} · ${S[lv].short}${lv === 2 ? ' 16+' : ''} ×${qty} · ${money(PRICE.single * qty)}`;
      toast.classList.add('on'); clearTimeout(tt); tt = setTimeout(() => toast.classList.remove('on'), 3600);
    });
  });
  $$('.sc-box').forEach(a => a.addEventListener('click', () => {
    const box = a.closest('.sc-buy'), lv = +$('.sp.on', box).dataset.s;
    $('input[name=size][value=box12]').checked = true;
    $(`input[name=flavor][value="${box.dataset.flavor}"]`).checked = true;
    $(`input[name=strength][value="${lv}"]`).checked = true;
    qty = 1; updateOrder(true);
  }));
})();
