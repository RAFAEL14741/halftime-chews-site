/* HalfTime Chews: scroll + interactions */
(() => {
  const RM = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const TEAR = 0.115;          // tear line, fraction of pack image height
  const VIS = { x0: 0.059, x1: 0.94, y0: 0.042 }; // visible pack box in the image

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
    e.preventDefault(); goTo(h);
  }));

  /* nav background after leaving the very top */
  const nav = $('.nav');
  ScrollTrigger.create({ start: 40, onToggle: s => nav.classList.toggle('solid', s.isActive) });

  /* ---------- HERO STAGE ---------- */
  const stage = $('#stage'), inner = $('.stage-in');
  const packw = $('.packw'), closed = $('.pk-closed'), torn = $('.pk-torn'), strip = $('.pk-strip');
  const tearLine = $('.tear-line'), heroCopy = $('.hero-copy'), heroInfo = $('.hero-info'), glow = $('.glow');
  const chews = $$('.chew'), slots = $$('.slot'), cards = $$('.flv'), flvHead = $('.flv-head'), flavors = $('.flavors');
  let tl = null, st = null;

  function layout() {
    const W = inner.clientWidth, H = inner.clientHeight, phone = W < 820;
    let h, x, y;
    if (phone) {
      const h1b = $('.hero-copy h1').getBoundingClientRect().bottom - inner.getBoundingClientRect().top;
      const infoTop = heroInfo.getBoundingClientRect().top - inner.getBoundingClientRect().top;
      y = h1b + 10;
      h = Math.max(220, Math.min(H * 0.46, infoTop - 8 - y));
      const w = h * 0.714;
      x = W - w * 0.96;
    } else {
      h = H * 0.76;
      const w = h * 0.714;
      x = W - W * 0.08 - w;
      y = H * 0.12;
    }
    const w = h * 0.714;
    const cw = phone ? Math.min(96, w * 0.42) : Math.min(180, Math.max(110, w * 0.3));
    return { W, H, phone, x, y, w, h, cw };
  }

  function placeStatic(L) {
    gsap.set(packw, { left: L.x, top: L.y, width: L.w, height: L.h, rotation: L.phone ? -3 : -5 });
    // dashed line across the pack's tear point, starting just left of the pack
    const ty = L.y + L.h * TEAR;
    tearLine.style.top = ty + 'px';
    tearLine.style.left = Math.max(0, L.x - (L.phone ? 24 : L.W * 0.07)) + 'px';
    chews.forEach(c => c.style.setProperty('--cw', L.cw + 'px'));
  }

  function build() {
    if (tl) { tl.scrollTrigger && tl.scrollTrigger.kill(); tl.kill(); }
    gsap.set([strip, closed, torn, packw, heroCopy, heroInfo, tearLine, glow, flvHead, ...cards, ...chews], { clearProps: 'transform,opacity,zIndex' });
    flavors.classList.remove('live');
    const L = layout();
    placeStatic(L);

    if (RM) {
      slots.forEach((sl, i) => { if (!sl.firstChild) sl.innerHTML = `<img src="${chews[i].querySelector('img').src}" alt="">`; });
      return;
    }

    const mouthX = L.x + L.w / 2, drop = L.phone ? L.H * 0.06 : L.H * 0.13;
    const mouthY = L.y + L.h * TEAR + drop;
    const c = L.cw / 2;
    // where the chews float after popping out (centers)
    const floatPos = L.phone
      ? [[mouthX - L.w * 0.62, mouthY - L.h * 0.2], [mouthX + L.w * 0.02, mouthY - L.h * 0.42], [mouthX + L.w * 0.3, mouthY - L.h * 0.14]]
      : [[mouthX - L.w * 0.78, mouthY + L.h * 0.04], [mouthX - L.w * 0.14, mouthY - L.h * 0.19], [mouthX + L.w * 0.4, mouthY - L.h * 0.1]];
    const rots = [-14, 9, 18];

    chews.forEach(ch => gsap.set(ch, { x: mouthX - c, y: mouthY + L.h * 0.06 - c, scale: 0.35, opacity: 0, zIndex: 2 }));

    tl = gsap.timeline({
      defaults: { ease: 'sine.inOut' },
      scrollTrigger: {
        trigger: stage, start: 'top top', end: () => '+=' + Math.round(L.H * (L.phone ? 1.9 : 2.0)),
        scrub: 0.9, pin: true, anticipatePin: 1, invalidateOnRefresh: false,
        onUpdate: s => flavors.classList.toggle('live', s.progress > 0.86)
      }
    });

    // 0.00–0.08 hold, info readable
    // RIP: closed -> torn swap hidden under the strip, strip rips up and away
    tl.set(closed, { opacity: 0 }, 0.08).set(torn, { opacity: 1 }, 0.08)
      .to(packw, { rotation: L.phone ? -1 : -2.5, duration: 0.06, ease: 'power2.out' }, 0.08)
      .to(strip, { y: -L.h * 0.07, x: L.w * 0.05, rotation: 7, duration: 0.06, ease: 'power2.out' }, 0.08)
      .to(strip, { y: -L.h * 0.7, x: L.w * 0.75, rotation: 48, duration: 0.14, ease: 'power2.in' }, 0.14)
      .to(strip, { opacity: 0, duration: 0.05 }, 0.23)
      .to(tearLine, { opacity: 0, duration: 0.06 }, 0.12)
      // pack settles lower to make room for the chews
      .to(packw, { y: drop, duration: 0.14, ease: 'power2.inOut' }, 0.16);
    if (L.phone) tl.to(heroCopy, { opacity: 0, y: -30, duration: 0.08 }, 0.12);

    // POP: chews rise out of the opening, then come in front and float
    chews.forEach((ch, i) => {
      const t0 = 0.24 + i * 0.035;
      tl.to(ch, { opacity: 1, y: mouthY - L.h * 0.1 - c, scale: 0.7, duration: 0.05, ease: 'power2.out' }, t0)
        .set(ch, { zIndex: 4 }, t0 + 0.05)
        .to(ch, { x: floatPos[i][0] - c, y: floatPos[i][1] - c, scale: 1, rotation: rots[i], duration: 0.1, ease: 'back.out(1.6)' }, t0 + 0.05);
    });

    // HAND-OFF: hero leaves, pack drops away, flavor grid comes in
    tl.to([heroCopy, heroInfo], { opacity: 0, y: -40, duration: 0.08, ease: 'power1.in' }, 0.5)
      .to(packw, { y: drop + L.H * 0.65, rotation: 8, opacity: 0, duration: 0.14, ease: 'power2.in' }, 0.52)
      .to(glow, { opacity: 0.35, duration: 0.1 }, 0.52)
      .to(flvHead, { opacity: 1, duration: 0.08 }, 0.64);
    cards.forEach((cd, i) => tl.fromTo(cd, { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.12, ease: 'power2.out', immediateRender: false }, 0.66 + i * 0.03));

    // FLY: each chew lands in its flavor slot (slot rects are static inside the pinned stage)
    const ir = inner.getBoundingClientRect();
    chews.forEach((ch, i) => {
      const r = slots[i].getBoundingClientRect();
      const sx = r.left - ir.left + r.width / 2, sy = r.top - ir.top + r.height / 2;
      tl.set(ch, { zIndex: 8 }, 0.59)
        .to(ch, { x: sx - c, y: sy - c, scale: r.width / L.cw, rotation: 0, duration: 0.22, ease: 'power3.inOut' }, 0.6 + i * 0.03);
    });
    tl.to({}, { duration: 0.06 }, 0.94); // short hold at the end
  }

  let rt;
  const rebuild = () => { build(); ScrollTrigger.refresh(); };
  window.addEventListener('resize', () => {
    clearTimeout(rt);
    rt = setTimeout(() => { if (Math.abs(window.innerWidth - (rebuild.w || 0)) > 40 || !rebuild.w) { rebuild.w = window.innerWidth; rebuild(); } }, 200);
  });
  const start = () => { rebuild.w = window.innerWidth; build(); ScrollTrigger.refresh(); window.__ready = true; };
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => requestAnimationFrame(start)); else window.addEventListener('load', start);

  /* ---------- HOW: 30:00 clock ---------- */
  const clock = $('.clock'), mm = $('.clock .mm'), ss = $('.clock .ss');
  const pad = n => String(n).padStart(2, '0');
  const setClock = p => {
    const left = Math.max(0, Math.round(1800 * (1 - p / 0.82)));
    mm.textContent = pad(Math.floor(left / 60)); ss.textContent = pad(left % 60);
    clock.classList.toggle('zero', left === 0);
  };
  ScrollTrigger.create({ trigger: '.how', start: 'top top', end: 'bottom bottom', refreshPriority: -1, onUpdate: s => setClock(s.progress), onRefresh: s => setClock(s.progress) });

  /* ---------- STRENGTH PICKER ---------- */
  const S = [
    { name: 'Green · Light', short: 'Green', mg: '150 mg', use: 'Practice and the gym. Ages 14+.', extra: '', c: '#3DD68C' },
    { name: 'Yellow · Hard', short: 'Yellow', mg: '250 mg', use: 'Games and long runs. Ages 14+.', extra: 'Also 75 mg potassium, 12 mg magnesium, 20 mg calcium, about 20 calories.', c: '#FFD23F' },
    { name: 'Red · Extreme', short: 'Red', mg: '500 mg', use: 'Heat and long shifts. Ages 16+ only.', extra: '', c: '#E5484D' }
  ];
  const strengthSec = $('#strength');
  let level = 0, manual = null;
  const qs = $$('.q');
  function renderStrength() {
    const lv = manual ?? level, s = S[lv];
    strengthSec.style.setProperty('--cur', s.c);
    $('.res-name').textContent = s.name;
    $('.res-mg').innerHTML = '<b>' + s.mg + '</b> sodium';
    $('.res-use').textContent = s.use;
    $('.res-extra').textContent = s.extra;
    const b = $('.res-btn'); b.textContent = 'Order ' + s.short; b.dataset.s = lv;
    $$('.lu').forEach(l => l.classList.toggle('on', +l.dataset.s === lv));
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

  /* ---------- MOCK CHECKOUT ---------- */
  const form = $('#orderForm');
  const PRICE = { single: 1.49, box12: 14.99, team48: 49 };
  const LABEL = { single: 'Single pack', box12: 'Box of 12', team48: 'Team box of 48' };
  const teamColors = $('#teamColors'), fundraiser = $('#fundraiser'), colorPick = $('#colorPick');
  const qtyOut = $('#qty'), cartN = $('.cart-n');
  let qty = 1, color = null, touched = false;
  const money = n => '$' + n.toFixed(2);

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
      ['Strength', S[lv].short + ', ' + S[lv].mg],
      ['Flavor', flavor]
    ];
    if (teamColors.checked) lines.push(['Team colors', color.dataset.n]);
    if (fundraiser.checked) lines.push(['Your team keeps', money(5 * qty)]);
    $('.sum-lines').innerHTML = lines.map(([a, b]) => `<dt>${a}</dt><dd>${b}</dd>`).join('');
    $('#total').textContent = money(total);
    $('#sumNote').textContent = lv === 2 ? 'Red is for ages 16+ only.' : (isBox && qty < 10 ? 'Team colors unlock at 10+ boxes.' : '');
    $('.or-sum').style.setProperty('--cur', S[lv].c);
    $('.sum-box').hidden = !isBox;
    $('.sum-pack').style.height = isBox ? '120px' : '';
    $('.sum-box-band').style.background = teamColors.checked ? getComputedStyle(color).getPropertyValue('--k') : '';
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
})();
