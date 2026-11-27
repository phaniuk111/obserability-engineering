// jsdom smoke test: every view renders, no script errors, interactions work.
// Usage: NODE_PATH=<dir with jsdom> node course/test_page.js
const fs = require('fs');
const path = require('path');
const { JSDOM, VirtualConsole } = require('jsdom');

const site = path.join(__dirname, 'site');
const html = fs.readFileSync(path.join(site, 'index.html'), 'utf8')
  .replace('<script src="diagrams.js"></script>', `<script>${fs.readFileSync(path.join(site, 'diagrams.js'), 'utf8')}</script>`);
const data = JSON.parse(fs.readFileSync(path.join(site, 'course.json'), 'utf8'));
const errors = [];
const vc = new VirtualConsole();
vc.on('jsdomError', e => errors.push(String(e.message || e)));
vc.on('error', e => errors.push(String(e)));

const dom = new JSDOM(html, {
  runScripts: 'dangerously', url: 'https://example.test/', virtualConsole: vc, pretendToBeVisual: true,
  beforeParse(w) {
    w.fetch = () => Promise.resolve({ json: () => Promise.resolve(JSON.parse(JSON.stringify(data))) });
    w.scrollTo = () => {};
  },
});
const w = dom.window, d = w.document;
const tick = () => new Promise(r => setTimeout(r, 20));
const go = async h => { w.location.hash = h; w.dispatchEvent(new w.HashChangeEvent('hashchange')); await tick(); };
const assert = (c, m) => { if (!c) { console.error('FAIL', m); process.exitCode = 1; } else console.log('ok  ', m); };

(async () => {
  await tick(); await tick();
  assert(d.querySelectorAll('.tile').length === 32, 'home shows 32 chapter tiles');
  assert(d.querySelectorAll('.tile.unread').length === 0, 'no unread tiles');
  assert(d.querySelectorAll('.tile').length === 32, '32 chapter tiles');
  for (const l of data.lessons) {
    await go('#' + l.id);
    const h1 = d.querySelector('h1');
    assert(h1 && h1.textContent === l.title, `lesson ${l.id} renders`);
    if (l.diagram) assert(d.querySelector('figure svg'), `lesson ${l.id} has diagram`);
  }
  await go('#ch12');
  d.querySelector('[data-q="0"] [data-o="1"]').click();
  assert(d.querySelector('[data-q="0"] .right'), 'quick check marks right answer');
  d.querySelector('[data-done]').click();
  assert(d.querySelector('[data-done]').textContent.includes('✓'), 'mark done toggles');
  await go('#ch30'); assert(d.querySelector('h1').textContent.includes('Vendor engineering'), 'ch30 is a full lesson');
  assert(d.body.textContent.includes('Open the lab guide'), 'ch30 links to a lab');
  await go('#ch16'); assert(d.body.textContent.includes('Since the book') && d.body.textContent.includes('batch'), 'ch16 shows post-book changes');
  assert([...d.querySelectorAll('a[href^="https://opentelemetry.io"]')].length >= 2, 'ch16 links to official docs');
  assert(![...d.querySelectorAll('a[target="_blank"]')].some(a => a.rel !== 'noopener'), 'external links use rel=noopener');
  await go('#ch32'); assert(d.querySelector('figure svg'), 'ch32 has its diagram');
  await go('#map'); assert(d.querySelector('#app').textContent.includes('Lab 3'), 'map points to labs'); assert(!d.querySelector('#app').textContent.includes('pocs/'), 'no old POC paths on the map');
  await go('#quiz'); d.querySelector('[data-qo="0"]').click();
  assert(!d.querySelector('[data-quiz=next]').disabled, 'quiz answer enables next');
  d.querySelector('[data-quiz=next]').click(); await tick();
  assert(d.body.textContent.includes('Question 2 of'), 'quiz advances');
  await go('#flashcards'); const first = d.getElementById('card').textContent;
  d.querySelector('[data-fc=flip]').click(); await tick();
  assert(d.getElementById('card').textContent !== first, 'flashcard flips');
  await go('#drills'); assert(d.querySelectorAll('details').length === data.drills.length + data.lessons.length, 'all drills listed');
  await go('#map'); assert(d.querySelectorAll('h2').length === data.map.length, 'knowledge map themes');
  await go('#checklist'); const cb = d.querySelector('[data-req]'); cb.checked = true; cb.dispatchEvent(new w.Event('change', { bubbles: true })); await tick();
  assert(d.body.textContent.includes(`1/${data.requirements.length}`), 'checklist tick counts');
  await go('#numbers'); const nf = d.getElementById('nf'); nf.value = 'retriever'; nf.dispatchEvent(new w.Event('input', { bubbles: true }));
  assert([...d.querySelectorAll('#nt tbody tr')].some(r => !r.hidden), 'numbers filter');
  assert(errors.length === 0, 'no script errors' + (errors.length ? ': ' + errors.join(' | ') : ''));
})();
