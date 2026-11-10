# HalfTime Chews site — HANDOFF (v2 upgrade)

## ROLE
You're Rafael's creative director + builder for a CLASS PROJECT site, "HalfTime Chews" (an electrolyte chew idea, not a real product). Run rafael-router first (site job: site-director + frontend-design + scroll-morph-hero / gsap-scrolltrigger). Read memory: /areas/halftime-chews.md, /topics/design-taste.md, /topics/lessons-sites.md, /topics/lessons-sites-2.md (has the HalfTime bugs from v1), /topics/lessons-gsap-hero.md, /topics/lessons-chrome-flow.md, /topics/lessons-docs-chrome.md (one path per memory_read).

## WHERE THINGS LIVE
- Repo: **RAFAEL14741/halftime-chews-site** (public, branch main). Live: **https://rafael14741.github.io/halftime-chews-site/** (GitHub Pages from main /root).
- Cloud chat: attach the repo with add_repo (access: push), then clone. The cloud can't reach github.io (proxy blocks it): QA locally with `python3 -m http.server` + Playwright.
- Files: `index.html`, `style.css`, `main.js` (vanilla + vendored `js/` gsap, ScrollTrigger, lenis), `fonts/` (Inter Tight 400–800, JetBrains Mono), `img/` (webp cutouts + context photos), `assets/` (2K Flow originals), `slide/` (site.jpg screenshot 2400x1350 + qr.png for the deck slide).
- Flow project with all stills: flow.google.com/project/f56053df-3c67-43d9-bfe2-2de6b2f8ee7e (the "Nov 06 - 13:06" project, Flow account in Chrome **Browser 3**, Mac).
- GitHub sign-in: **Browser 4** (Mac). School Google account (deck, /u/1): NOT in Browser 4. Ask Rafael which Chrome has it (lessons say a Mac Chrome; the one whose tabs list the old Apps Script tab).
- Deck: Google Slides 19MK1R8tHtSdWVzBEE6O8j42_V_HLBf3j8nQGRF3JeHk (school account /u/1). Apps Script project 18YsciK4ehKw_Kr0aD5OnUYsjrl80LTviE6fCZ2ol33i5KoGU_A2UvsKC.

## FACTS (only use these, never invent; flag anything new)
- Electrolyte chew, 4 soft chews per pack, heat-resistant, no water/no mixing, sold as a dietary supplement. "Tear. Chew. Keep going." Chew 2 about every 30 min of hard play/work; keep drinking water. Only claim: "helps replace electrolytes lost in sweat".
- GREEN Light 150 mg sodium (practice, gym, 14+). YELLOW Hard 250 mg (games, long runs, 14+; also 75 mg potassium, 12 mg magnesium, 20 mg calcium, ~20 cal). RED Extreme 500 mg (heat, long shifts, 16+ ONLY). "Not sure? Start on green; over an hour / hot out / salt marks on your shirt = each yes moves you up one color."
- Prices: single $1.49, box of 12 $14.99, team box of 48 $49. Team colors on 10+ boxes, same price. Fundraiser box: team keeps $5.
- Where: team orders + fundraisers (high school), campus shops (college/club), gym front desks, run shops, race expos (gyms + runners), safety managers (work crews), our site + Amazon.
- Flavors: citrus, berry, watermelon ("ideas to test"). Flavor accents: citrus #FF8A2A, berry #9D6BFF, watermelon #FF5FA2 (not green/yellow/red = strength).
- Design system: bg #0B0B0A, text #F2EEE4, soft #CFCBC0, muted #9E9B90, lime #D4F53C, strength #3DD68C / #FFD23F / #E5484D. Inter Tight 800 headlines, Inter Tight body, JetBrains Mono labels.
- Footer: "HalfTime Chews is a class project idea, not a real product. Product images are AI concepts."
- MORE FACTS ARE IN THE DECK (15 slides + speaker notes: Problem/950 mg, How it works, Lineup, Anyone who sweats + segmentation, Four criteria, Where we fit/positioning map, 4 Ps, One message per market, Growth plan, SWOT, Next 6 months, sources). STEP 1 of v2 = read the deck text: in the school-account Chrome, on a docs.google.com tab, `fetch('/presentation/u/1/d/<id>/export/txt')`, store in window var, return ≤900-char slices with URLs and [?&=] stripped. Use ONLY those facts for new sections.

## WHAT THE FIRST CHAT DID (Nov 10 2026)
- Flow (free Nano Banana 2.1): edited the deck's pack into a clean studio front shot. The label first read "ELECTROLYTE ENERGY CHEWS / 10 CHEWS" (wrong + a claim), fixed to "ELECTROLYTE CHEWS / 4 SOFT CHEWS". Flag: the DECK's own pack photos may still say "10 CHEWS"; tell Rafael. Made a torn-top version (pixel-aligned), single chews (lime, citrus orange, berry violet, watermelon pink), a mid-air shot (unused), and downloaded 3 deck context photos (soccer player, gym bag, construction worker).
- Cutouts with rembg isnet. Rip strip = closed-pack alpha minus torn-pack alpha (top 25%), so the jagged strip is exact. Tear line sits at 11.5% of the pack image height.
- 3 hero frames (A tear line / B 30:00 game clock / C black-lime split). Blind judge: A = 2nd on looks (beat LMNT, Maurten won); B best on memory; all three flagged template-ish (lime on black + 3-word slogan, both brief-mandated). Picked A for the hero and moved B's clock into "How it works". C rejected (flat color block = Rafael's hard no).
- Built v1: pinned hero (2.0 viewports desktop, 1.9 phone) → strip rips off, pack swaps to torn, 3 chews pop out, float, then fly into 3 flavor cards (same pinned stage). Then: 30:00 clock counting down on scroll (sticky 220vh), strength picker (3 yes/no → color, lineup buttons, "Order Yellow" sets checkout), "For anyone who sweats" 3 photo cards, mock checkout (size/strength/flavor/qty, team colors unlock at 10+ boxes, fundraiser $5/box, Place order → "Class demo: no real payment."), footer claim + disclaimer.
- Bugs fixed (rules in lessons-sites-2): chews landed behind cards (z-index), clock trigger made before the pin (refreshPriority -1), stretched img (height:auto), [hidden] overridden, bench crop hid CTA.
- Deploy: Netlify MCP deploy is blocked from cloud (403); `gh` not authed; repo had to be created in Browser 4, then add_repo + push + Pages.
- Rafael's reaction: "i like it" but thinks it's plain; wants more product info from the slides, every flavor its own in-depth section, more motion + more objects around.

## BLIND JUDGE OF v1 (6.5/10)
Hero strong (close to LMNT); after the hero it reads "nice dark template". Flavors = generic 3 identical cards + empty bottom; where-we-sell cards uneven + empty space; checkout box mock looks like a placeholder; tiny mono gray labels low contrast; missing: supplement-facts style panel, ingredients/allergens (ONLY if the deck has them), chews vs drinks vs gels comparison (only deck facts), FAQ. (Its "00:00 stuck" and "no footer/heading" notes were screenshot artifacts.)

## v2 PLAN (do in this order)
1. Read the deck text (above). List every new fact you'll use + its slide.
2. Flavors → 3 full-screen pinned flavor SCENES (one per flavor), each its own layout and color world: big chew rotating, floating flavor objects around it (Flow stills, free: orange slices + zest for citrus, mixed berries for berry, watermelon cubes/seeds for watermelon; cut out with rembg), accent-colored glow, short copy, "flavor idea to test". Chews from the hero fly into scene 1. Motion: parallax depth layers (near objects fast, far slow), objects drift in/out between scenes. Keep text readable, no objects over copy.
3. How it works: keep the 30:00 clock, add Tear → Chew → Go steps (3 small pack/chew renders) and the deck's sodium-loss fact (Problem slide) if it's there.
4. New "What's inside" label-style panel per strength (only the numbers we have; Green/Red show sodium only unless the deck has more).
5. New "Why a chew" section from the deck's positioning slide (Where we fit / 4 Ps). No invented competitor numbers.
6. Where we sell: even grid, add the deck's segments, fill the empty space.
7. Checkout: replace the CSS box with a real Flow render of a box of 12 (matte black, lime label) + team-color version via recolor technique (lessons-gsap-hero).
8. Raise mono label contrast (#9E9B90 → soft on dark), FAQ (from deck facts only).
9. QA (12-step contact sheets desktop+phone, overflow 320–430, page errors, landing frames), blind bench, push, check live in Browser 4.
10. THEN the deck slide: new guarded Apps Script function (NEVER build()), slide after "Pick your strength" (or before Questions; ask Rafael), insertImage from `https://raw.githubusercontent.com/RAFAEL14741/halftime-chews-site/main/slide/site.jpg` (setLinkUrl to the live site) + `slide/qr.png`; re-shoot site.jpg after v2. Renumber footers/headers, update the rehearsal scripts doc ("HalfTime Chews — Rehearsal Scripts", Claude Docs) with the new slide's lines + renumber. Rafael = 1–9, Derick = 10–15 now (ask how the split changes).
11. Delete the Flow downloads on the Mac (~/Downloads/htc/ — 10 jpgs, already on GitHub in assets/) once Rafael OKs delete permission.

## HARD RULES
- Facts only from the brief + deck; flag anything new. FDA: only "helps replace electrolytes lost in sweat".
- Ask before any paid credits (Flow video, Higgsfield). Flow stills are free.
- Generated assets go to GitHub, not left on the Mac.
- Slides/Apps Script: NEVER run build() (wipes photos); the Run dropdown resets to "build" after every editor reload: reselect + zoom-confirm. New function → save, reload, dismiss "signed in as" popup (OK ~1435,230), pick from dropdown. Every one-shot function gets a guard (slide count + "already done" text). Find slides by unique header/footer text, not titles. pres.replaceAllText covers notes; new text must not contain old text. javascript_tool output with URLs or = gets blocked. browser_batch can't act after a navigate. Check slides in slideshow (cmd+Return). Slides can't embed a live site: linked screenshot + QR.
- Hero stays SHORT with real info visible. No hard cuts. Floating objects OK, never over copy.
- Short casual progress updates; write a lessons rule for every fixed bug.

## v2 STATUS (Nov 10 2026, chat 2)
- School Google account = Browser 3 (same Chrome as Flow). Browser 2 = Access Denied on the deck.
- Steps 1–9 DONE. Blind judge: v2 7/10 looks (v1 6.5), wins Memory + "stop scrolling"; template tells it named are brief-mandated (lime on black, period headlines). Fixed all its concrete bugs.
- New assets: img/o-*.webp (fruit cutouts), img/box12.webp + box12-mask.png (t-map: out = px + t*1.2*(team - lime 185,233,19)), sources in assets/flv_*.png + box12.png.
- QA scripts used: overlap check (objects vs copy/dock/nav at every scene hold, 5 viewports), overflow 320–430, RM check.
- Step 10 DONE (chat 3, Nov 10): deck is 16 slides. New slide 15 "05  THE WEBSITE / Try it live." (Apps Script addSite + fixSite, guarded) before Sources/Questions (now 16): linked site.jpg (kept existing shot, it already shows v2 nav + torn pack) + lime QR + URL + 3 lines; footers renumbered "NN / 16"; slide 14 note now ends "then Rafael shows our website". Rehearsal Scripts doc: 16 slides, Part 5 row (Rafael, slide 15, ~0:30, total ~9:00), Slide 15 script, Sources = Slide 16.
- Step 11 DONE: ~/Downloads/htc (10 jpgs, sha1-matched to assets/) moved to Mac Trash.
- Not done / flag: agenda slide (if it lists parts) doesn't mention part 05; doc's "cream/green/black/gray" background note may be outdated after the premium rebuild.
- v2.1 (Rafael: "love it but boring, add info + ordering early"): flavor scenes now have strength pills + "Add pack · $1.49" + "box of 12" link + toast + nav cart count (fills the checkout form). Punch: fruit bursts out of the chew (expo.out from chew center), shockwave ring per landing, letter-by-letter name rise, chew lands with back.out, mouse depth parallax on fruit (CSS vars --mx/--my × --d on .ob img).
- Bug fixed: scene buttons unclickable because "active" was computed from tl.time() (scrub lags) → use ScrollTrigger progress × END.

## v3 HERO (chat 3, Nov 10) — Rafael: "hero is boring, only a black screen; improve the gummies, more details"
- 3 backdrops built (switch with ?bg=a|b|c): A night football field (Flow still assets/flv_field_b.png -> img/hero-field.webp, dark left/top grade), B faint dot-matrix "HALF 2 30:00" scoreboard + chalk lines, C studio floor + pack reflection. Blind judge: A wins looks/memory/stop-scrolling/trust; B = noise, C = flat. Default data-bg="a" on .stage-in.
- Chew detail tags (.ctag): flavor name + one line next to each floating chew (desktop), names only on phone; clamped on screen; auto-hidden if it would touch the h1 (1024px). Falling salt specks (.bgx-dust) only on the right half.
- Fixes from judge: top dark grade (glare behind nav), sub copy brighter, fact labels 13.5px, berry chew lower, phone watermelon chew inward, TEAR HERE label left of the line (hidden on phone).
- Unused but saved: assets/flv_chew_split.png (+ _floor): macro of a lime chew torn in half, idea for an "inside the chew" moment.
