// Nov 12 (round 33): the card data arrives in two parts (cards.js, cards2.<hash>.js). Every club must be present
// and merged, and the count must match the number the build wrote (CARD_CLUBS).
import { open, report } from './_common.mjs';
const {browser, page, errors} = await open();
const r = await page.evaluate(() => {
  const D = window.CARD_DETAIL || {}, n = Object.keys(D).length;
  const ids = new Set([...AUTO_REGIMES, ...LB_HIST].map(x => x.id));
  return {
    bothPartsRan: window.CARD_PARTS === 2,
    allClubsPresent: n === window.CARD_CLUBS && n === 152,
    cardsReady: window.CARDS_READY === true,
    everyClubHasARegime: Object.keys(D).every(k => ids.has(k)),
    everyCardMerged: Object.keys(D).every(k => { const x = [...AUTO_REGIMES, ...LB_HIST].find(y => y.id === k); return x && Object.keys(D[k]).every(f => f in x); }),
    noFailBanner: !document.getElementById('cards-fail'),
  };
});
await browser.close();
report('t_cards', r, errors);
