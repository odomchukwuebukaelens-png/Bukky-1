// Demo short (9:16): cut-outs on the map + real archive footage inserts + snow VFX
// Shorts for US/EU audience: never show Africa (darkened into shadow) and fly camera directly
window.HIDE_IDS = ['012','024','072','108','120','132','140','148','174','178','180','204','226','231','232','262','266','270','288','324','384','404','426','430','434','450','454','466','478','480','504','508','516','562','566','624','638','646','654','678','686','690','694','706','710','716','728','729','732','748','768','788','800','818','834','854','894'];
window.DIRECT_MOVES = true;
window.buildScenes = ({ C }) => {
  const PARIS = [2.35, 48.86], MOSCOW = [37.62, 55.75];
  return [
    { seg: 'd1', cam: [['start', 110, 56, 480], ['bear', 110, 56, 520], ['1812', 21, 62, 1450, 1.6], ['burned', 37.6, 56.5, 2400, 1.4], ['winter', 21, 62, 1450, 1.4]],
      items: [
        { type: 'fill', ids: ['643'], color: C.red, at: 'Russia', until: '1812' },
        { type: 'callout', text: 'BIGGEST COUNTRY ON EARTH', bg: '#d7263d', size: 56, at: 'biggest', until: 'bear', y: 170 },
        { type: 'callout', text: 'SYMBOL: THE BEAR', bg: '#0a0a0a', size: 60, at: 'bear', until: '1812', y: 170 },
        { type: 'cutout', img: 'bear', ll: [100, 58], size: 440, at: 'bear', until: '1812+0.3' },

        { type: 'callout', text: '1812', bg: '#0a0a0a', size: 80, at: '1812', until: 'Moscow', y: 170 },
        { type: 'fill', ids: ['250'], color: C.blue, at: '1812', until: 'burned' },
        { type: 'cutout', img: 'napoleon', ll: [7.5, 52.5], size: 380, at: 'Napoleon', until: 'burned', enter: 'pop' },
        { type: 'arrow', from: PARIS, to: MOSCOW, at: 'marched', until: 'burned', bend: -0.12, width: 10, color: C.blue },
        { type: 'tag', label: 'MOSCOW', ll: MOSCOW, at: 'Moscow', until: 'burned' },
        { type: 'counter', from: 0, to: 400000, suffix: '+', label: 'SOLDIERS', at: 'four', until: 'Russians', x: 540, y: 300, size: 130, color: C.yellow },
        { type: 'footage', clip: 'army', caption: 'The Grande Armée', at: 'with', until: 'Russians', y: 860, size: 470 },

        { type: 'fill', ids: ['643'], color: C.red, at: 'Russians', until: 'end+1', alpha: 0.55 },
        { type: 'ring', ll: MOSCOW, r: 70, at: 'burned', until: 'winter' },
        { type: 'callout', text: 'MOSCOW BURNS', bg: '#d7263d', size: 66, at: 'burned', until: 'winter', y: 170 },
        { type: 'footage', clip: 'moscow', caption: 'Moscow on fire, 1812', at: 'burned', until: 'winter+0.2', y: 860, size: 470 },

        { type: 'snow', at: 'winter-0.3', until: 'end+4' },
        { type: 'callout', text: 'THE RUSSIAN WINTER', bg: '#0a0a0a', size: 64, at: 'winter', until: 'Only', y: 170 },
        { type: 'footage', clip: 'winter', caption: 'The retreat', at: 'winter', until: 'home+0.3', y: 860, size: 470 },
        { type: 'arrow', from: MOSCOW, to: [4, 49.5], at: 'Only', until: 'end+4', bend: 0.14, width: 6, color: '#fff' },
        { type: 'callout', text: 'ONLY A FRACTION CAME HOME', bg: '#d7263d', size: 52, at: 'Only', until: 'end+4', y: 170 },
      ] },
  ];
};
