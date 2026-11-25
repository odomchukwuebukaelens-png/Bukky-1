// EP02 "How Russia Still Gets America's Banned Chips"
// Map scenes + full-screen cartoon clips (toons.json). Africa is always shadowed (US/EU audience).
window.HIDE_IDS = ['012','024','072','108','120','132','140','148','174','178','180','204','226','231','232','262','266','270','288','324','384','404','426','430','434','450','454','466','478','480','504','508','516','562','566','624','638','646','654','678','686','690','694','706','710','716','728','729','732','748','768','788','800','818','834','854','894'];
window.DIRECT_MOVES = true;
window.buildScenes = ({ C }) => {
  const LL = { DC: [-77.04, 38.9], TX: [-97.7, 30.3], HK: [114.17, 22.32], MOS: [37.62, 55.75], KZ: [67, 48], KG: [74.6, 41.4], AM: [44.9, 40.2], TR: [35, 39], UAE: [54.4, 24.2],
    SG: [103.82, 1.35], MY: [101.7, 3.6], CY: [33.2, 35.1], ALA: [52.05, 55.78], ZEL: [37.2, 55.98], TW: [121, 23.7], KR: [127.8, 36.4], NL: [5.3, 52.2], JP: [138.5, 36.5],
    DE: [10.4, 51.1], UA: [31.5, 49], RU: [60, 58], CN: [104, 35], US: [-98, 39], IR: [53.7, 32.4], NO: [9, 61] };
  const ID = { US: '840', RU: '643', CN: '156', UA: '804', KZ: '398', KG: '417', AM: '051', TR: '792', UAE: '784', TW: '158', KR: '410', NL: '528', JP: '392', MY: '458',
    DE: '276', UK: '826', FR: '250', CA: '124', AU: '036', IR: '364', NO: '578', BY: '112', CY: '196', IT: '380', ES: '724', PL: '616' };
  const SOVIET = ['643', '804', '112', '398', '860', '417', '762', '795', '031', '051', '268', '498', '440', '428', '233'];
  const NATO87 = ['840', '124', '826', '250', '276', '380', '528', '056', '442', '578', '208', '352', '620', '724', '300', '792'];
  const ALLIES = ['840', '124', '826', '250', '276', '380', '528', '056', '578', '208', '752', '246', '616', '724', '620', '300', '392', '410', '036', '554', '040', '203', '348', '642', '100', '191', '705', '703', '440', '428', '233', '372', '756'];
  const WORLD = [40, 32, 330], ATL = [-30, 42, 480], EURASIA = [70, 45, 520], EASTEU = [35, 52, 1200];
  const chipArrow = (from, to, at, until, extra = {}) => ({ type: 'arrow', from, to, at, until, bend: 0.18, color: '#fff', particle: 'chip', width: 7, ...extra });

  const map = [
    // ---------------- s01 HOOK ----------------
    { seg: 's01', cam: [['start', ...ATL], ['Russian', ...EASTEU], ['Today,', 33, 50, 1500], ['Washington', -10, 38, 380], ['question', ...EURASIA], ['Texas,', 10, 38, 360, 1.4]],
      items: [
        { type: 'callout', text: '2022', bg: '#0a0a0a', size: 76, at: 'start+0.2', until: 'Commerce' },
        { type: 'ring', ll: LL.DC, r: 60, at: 'Congress', until: 'Russian' },
        { type: 'tag', label: 'WASHINGTON', ll: LL.DC, at: 'Congress', until: 'Russian' },
        { type: 'fill', ids: [ID.RU], color: C.red, at: 'Russian', until: 'Today,' },
        { type: 'callout', text: 'CUT OFF FROM WESTERN TECH', bg: '#d7263d', size: 58, at: 'cut', until: 'Today,' },
        { type: 'fill', ids: [ID.UA], color: C.yellow, at: 'Today,', until: 'Washington', alpha: 0.6 },
        { type: 'dots', pts: [[36, 49.5], [33, 48], [37.5, 47.8], [30.5, 50.4], [35, 47.2], [32, 46.7]], color: C.red, at: 'wreckage', until: 'Washington', stagger: 0.12 },
        { type: 'callout', text: 'STILL FULL OF WESTERN CHIPS', bg: '#d7263d', size: 58, at: 'months', until: 'Washington' },
        { type: 'fill', ids: [ID.US], color: C.blue, at: 'Washington', until: 'question' },
        { type: 'fill', ids: [ID.CN], color: C.red, at: 'Washington', until: 'question', alpha: 0.7 },
        chipArrow([-100, 38], [100, 33], 'AI', 'question', { bend: -0.12, color: C.dollar }),
        { type: 'callout', text: 'NVIDIA’S AI CHIPS', bg: '#118c4f', size: 62, at: 'AI', until: 'question' },
        { type: 'fill', ids: [ID.RU], color: C.red, at: 'question', until: 'end+0.5' },
        { type: 'callout', text: 'HOW DO THEY STILL GET THEM?', bg: '#d7263d', size: 58, at: 'banned', until: 'answer' },
        { type: 'callout', text: 'SHELL COMPANIES · AIRPORTS · BACK ROADS', bg: '#0a0a0a', size: 46, at: 'shell', until: 'Texas,' },
        { type: 'dots', pts: [LL.TX], color: C.blue, at: 'Texas,', until: 'end+0.6', r: 11 },
        { type: 'tag', label: 'TEXAS', ll: LL.TX, at: 'Texas,', until: 'end+0.6' },
        chipArrow(LL.TX, LL.HK, 'Texas,+0.2', 'end+0.6', { bend: -0.16 }),
        { type: 'tag', label: 'HONG KONG', ll: LL.HK, at: 'Hong', until: 'end+0.6', dir: 'up' },
        chipArrow(LL.HK, [70, 52], 'Hong+0.3', 'end+0.6', { bend: -0.2 }),
        { type: 'tag', label: 'RUSSIA', ll: [70, 54], at: 'border.', until: 'end+0.6' },
      ] },
    // ---------------- s02 THE BRAIN ----------------
    { seg: 's02', cam: [['start', ...EASTEU], ['RUSI', -2, 52, 1400], ['found', ...EASTEU], ['318', -40, 44, 460]],
      items: [
        { type: 'callout', text: 'EVERY WEAPON HAS A BRAIN', bg: '#0a0a0a', size: 58, at: 'start', until: 'brain' },
        { type: 'arrow', from: [40, 53], to: [31, 49.5], at: 'hundreds', until: 'RUSI', bend: 0.25, color: C.red, width: 6 },
        { type: 'callout', text: 'LOW · FAST · UNDER THE RADAR', bg: '#d7263d', size: 52, at: 'flying', until: 'brain' },
        { type: 'fill', ids: [ID.UK], color: C.blue, at: 'RUSI', until: 'found' },
        { type: 'tag', label: 'RUSI · LONDON', ll: [-0.12, 51.5], at: 'RUSI+0.3', until: 'found' },
        { type: 'counter', from: 0, to: 450, suffix: '+', label: 'FOREIGN-MADE COMPONENTS FOUND', at: '450', until: '318', y: 200, size: 150, color: C.yellow },
        { type: 'fill', ids: [ID.US], color: C.blue, at: '318', until: 'end+0.5' },
        { type: 'counter', from: 0, to: 318, label: 'MADE BY U.S. COMPANIES', at: '318+0.6', until: 'single', y: 200, size: 150, color: '#7fb0ff' },
        { type: 'callout', text: 'ONE KH-101 MISSILE: 31 FOREIGN PARTS', bg: '#d7263d', size: 52, at: 'single', until: 'end+0.6' },
        { type: 'source', text: 'Data: RUSI, "Silicon Lifeline" (2022)', at: '450', until: 'end' },
      ] },
    // ---------------- s03 RUSSIA CAN'T MAKE THEM ----------------
    { seg: 's03', cam: [['start', 37.4, 55.9, 2600], ['world’s', 40, 32, 330], ['Russia#3', ...EURASIA]],
      items: [
        { type: 'ring', ll: LL.ZEL, r: 60, at: 'Mikron,', until: 'world’s' },
        { type: 'tag', label: 'MIKRON · ZELENOGRAD', ll: LL.ZEL, at: 'Mikron,+0.3', until: 'world’s' },
        { type: 'callout', text: '~20 YEARS BEHIND', bg: '#d7263d', size: 62, at: 'decades', until: 'world’s' },
        { type: 'fill', ids: [ID.US], color: C.blue, at: 'designed', until: 'Russia#3' },
        { type: 'tag', label: 'DESIGN', ll: [-98, 40], at: 'designed+0.2', until: 'Russia#3' },
        { type: 'fill', ids: [ID.TW, ID.KR], color: C.dollar, at: 'manufactured', until: 'Russia#3' },
        { type: 'tag', label: 'MANUFACTURING', ll: LL.TW, at: 'manufactured+0.2', until: 'Russia#3', dir: 'up' },
        { type: 'fill', ids: [ID.NL, ID.JP], color: C.purple, at: 'machines', until: 'Russia#3' },
        { type: 'tag', label: 'MACHINES', ll: LL.NL, at: 'Netherlands', until: 'Russia#3' },
        { type: 'fill', ids: [ID.RU], color: C.grey, at: 'Russia#3', until: 'end+0.5' },
        { type: 'callout', text: 'OUTSIDE THE CHAIN', bg: '#3a3d42', size: 66, at: 'outside', until: 'end+0.6' },
      ] },
    // ---------------- s04 SANCTIONS ----------------
    { seg: 's04', cam: [['start', ...WORLD], ['Common', ...EURASIA]],
      items: [
        { type: 'callout', text: 'FEBRUARY 2022', bg: '#0a0a0a', size: 66, at: 'February', until: 'America,' },
        { type: 'fill', ids: [ID.RU], color: C.red, at: 'start', until: 'end+0.5' },
        { type: 'fill', ids: ALLIES, color: C.blue, at: 'America,', until: 'Common', stagger: 0.03, alpha: 0.75 },
        chipArrow([-90, 40], [50, 56], 'banned', 'Common', { blockAt: 1.3, dur: 1.2, bend: 0.18 }),
        { type: 'callout', text: 'EXPORTS BANNED', bg: '#d7263d', size: 66, at: 'banned', until: 'Later,' },
        { type: 'callout', text: 'THE COMMON HIGH PRIORITY LIST', bg: '#0a0a0a', size: 52, at: 'Common', until: 'paper' },
        { type: 'callout', text: 'PIPELINE: CUT', bg: '#d7263d', size: 66, at: 'paper', until: 'end+0.6' },
      ] },
    // ---------------- s04b COLD WAR PRECEDENT ----------------
    { seg: 's04b', cam: [['start', 40, 50, 420], ['Toshiba', 75, 50, 380], ['Members', -77, 38.9, 2600]],
      items: [
        { type: 'callout', text: 'IT’S HAPPENED BEFORE', bg: '#0a0a0a', size: 62, at: 'start', until: 'Cold' },
        { type: 'fill', ids: SOVIET, color: C.red, at: 'Cold', until: 'Members' },
        { type: 'fill', ids: NATO87, color: C.blue, at: 'allies', until: 'Members', alpha: 0.75 },
        { type: 'callout', text: 'THE COLD WAR', bg: '#0a0a0a', size: 66, at: 'Cold', until: 'CoCom,' },
        { type: 'callout', text: 'LINE X: SOVIET TECH THEFT', bg: '#d7263d', size: 56, at: 'Line', until: '1987.' },
        { type: 'callout', text: '1987', bg: '#0a0a0a', size: 80, at: '1987.', until: 'Toshiba' },
        { type: 'fill', ids: [ID.JP, ID.NO], color: C.yellow, at: 'Toshiba', until: 'Members' },
        { type: 'arrow', from: [139, 35], to: [131.9, 43.1], at: 'sold', until: 'Members', bend: 0.3, color: C.yellow, width: 7 },
        { type: 'arrow', from: [9, 60], to: [33, 68.9], at: 'sold+0.3', until: 'Members', bend: -0.3, color: C.yellow, width: 7 },
        { type: 'tag', label: 'TOSHIBA (JAPAN)', ll: [139, 36], at: 'Toshiba+0.4', until: 'Members' },
        { type: 'tag', label: 'KONGSBERG (NORWAY)', ll: [10, 60.5], at: 'Kongsberg', until: 'Members' },
        { type: 'callout', text: 'QUIETER SOVIET SUBMARINES', bg: '#d7263d', size: 56, at: 'harder', until: 'Americans' },
        { type: 'ring', ll: LL.DC, r: 60, at: 'Members', until: 'end+0.5' },
        { type: 'callout', text: '40 YEARS LATER…', bg: '#0a0a0a', size: 62, at: 'Forty', until: 'end+0.6' },
      ] },
    // ---------------- s05 CHIPS ARE NOT TANKS ----------------
    { seg: 's05', cam: [['start', ...WORLD]],
      items: [
        { type: 'callout', text: 'SMALLER THAN A FINGERNAIL', bg: '#0a0a0a', size: 58, at: 'fingernail', until: 'cost' },
        { type: 'callout', text: 'A FEW DOLLARS EACH', bg: '#118c4f', size: 62, at: 'cost', until: 'billions' },
        { type: 'callout', text: 'BILLIONS SOLD EVERY YEAR', bg: '#0a0a0a', size: 58, at: 'billions', until: 'chip' },
        { type: 'dots', pts: [[-97, 33], [-122, 37], [8.5, 50], [2.3, 48.8], [-1, 52], [121, 31], [114, 22.5], [139.7, 35.7], [126.9, 37.5], [101.7, 3.1], [121, 14.6], [103.8, 1.3], [77.6, 13], [4.9, 52.4], [18, 59.3], [-79.4, 43.7]], color: C.dollar, at: 'distributors', until: 'chip', stagger: 0.06 },
        { type: 'callout', text: 'MISSILE = CAR = DRONE = WASHER', bg: '#d7263d', size: 50, at: 'guides', until: 'Once' },
        ...[[[-97, 33], [8.5, 50]], [[8.5, 50], [114, 22.5]], [[114, 22.5], [77, 43]], [[77, 43], [37.6, 55.7]]].map(([a, b], i) => chipArrow(a, b, `again#${i < 2 ? 1 : 2}+${i * 0.5}`, 'end+0.5', { bend: 0.2 })),
        { type: 'callout', text: 'WHO OWNS IT NOW?', bg: '#0a0a0a', size: 62, at: 'harder', until: 'end+0.6' },
      ] },
    // ---------------- s05b ONE CHIP'S JOURNEY ----------------
    { seg: 's05b', cam: [['start', ...WORLD], ['Hong', 95, 35, 520], ['Kazakhstan,', 62, 48, 760]],
      items: [
        { type: 'callout', text: 'FOLLOW ONE CHIP', bg: '#0a0a0a', size: 66, at: 'start', until: 'factory' },
        { type: 'dots', pts: [LL.TX, [101.7, 3.1], [121, 14.6]], color: C.blue, at: 'Texas,', until: 'Hong', r: 11, stagger: 0.4 },
        { type: 'tag', label: 'FACTORY', ll: LL.TX, at: 'Texas,', until: 'Hong' },
        chipArrow(LL.TX, LL.DE, 'distributor', 'Hong', { bend: -0.15 }),
        { type: 'tag', label: 'DISTRIBUTOR', ll: LL.DE, at: 'distributor+0.4', until: 'Hong' },
        chipArrow(LL.DE, LL.HK, 'Hong', 'Kazakhstan,', { bend: -0.12 }),
        { type: 'ring', ll: LL.HK, r: 60, at: 'Hong+0.6', until: 'Kazakhstan,' },
        { type: 'tag', label: 'SHELL COMPANY', ll: LL.HK, at: 'five', until: 'Kazakhstan,', dir: 'up' },
        { type: 'callout', text: '"CONSUMER ELECTRONICS"', bg: '#0a0a0a', size: 58, at: 'consumer', until: 'repacked,' },
        { type: 'callout', text: 'RELABELED: "PHONE PARTS"', bg: '#d7263d', size: 56, at: 'relabeled', until: 'cargo' },
        chipArrow(LL.HK, LL.KZ, 'Kazakhstan,', 'end+0.5', { bend: -0.15 }),
        { type: 'fill', ids: [ID.KZ], color: C.purple, at: 'Kazakhstan,', until: 'end+0.5' },
        chipArrow(LL.KZ, [50, 56], 'Russian', 'end+0.5', { bend: -0.15 }),
        { type: 'fill', ids: [ID.RU], color: C.red, at: 'Russian', until: 'end+0.5', alpha: 0.7 },
        { type: 'callout', text: 'INSIDE A RUSSIAN DRONE', bg: '#d7263d', size: 58, at: 'drone,', until: 'Nobody' },
        { type: 'callout', text: 'NO BREAK-IN NEEDED', bg: '#0a0a0a', size: 62, at: 'Nobody', until: 'end+0.6' },
      ] },
    // ---------------- s06 HONG KONG ----------------
    { seg: 's06', cam: [['start', 108, 30, 900], ['Shipments', -40, 30, 330], ['north', 100, 38, 560], ['Some', 114.17, 22.32, 9000]],
      items: [
        { type: 'fill', ids: [ID.CN], color: C.red, at: 'start', until: 'Some', alpha: 0.75 },
        { type: 'ring', ll: LL.HK, r: 55, at: 'Hong', until: 'Shipments' },
        { type: 'callout', text: 'FIRST STOP: HONG KONG', bg: '#d7263d', size: 60, at: 'Hong', until: 'Shipments' },
        chipArrow([-95, 35], LL.HK, 'Shipments', 'north', { bend: -0.14 }),
        chipArrow([8, 50], LL.HK, 'European', 'north', { bend: 0.12 }),
        { type: 'callout', text: 'RESOLD TO NEW TRADING FIRMS', bg: '#0a0a0a', size: 52, at: 'resold', until: 'north' },
        chipArrow(LL.HK, [60, 55], 'north', 'Some', { bend: -0.22 }),
        chipArrow(LL.HK, [90, 52], 'north+0.3', 'Some', { bend: 0.1, color: C.yellow }),
        { type: 'tag', label: 'BY PLANE', ll: [80, 44], at: 'plane', until: 'Some' },
        { type: 'tag', label: 'BY TRUCK', ll: [100, 45], at: 'truck,', until: 'Some', dir: 'up' },
        { type: 'callout', text: 'SAME ADDRESS, DOZENS OF FIRMS', bg: '#0a0a0a', size: 50, at: 'Some', until: 'paper.' },
        { type: 'callout', text: 'BLACKLISTED? OPEN A NEW ONE', bg: '#d7263d', size: 52, at: 'blacklisted,', until: 'end+0.6' },
      ] },
    // ---------------- s07 NEIGHBOURS ----------------
    { seg: 's07', cam: [['start', 62, 45, 640], ['Turkey', 45, 37, 760]],
      items: [
        { type: 'fill', ids: [ID.RU], color: C.red, at: 'start', until: 'end+0.5', alpha: 0.8 },
        { type: 'fill', ids: [ID.KZ, ID.KG, ID.AM, ID.BY], color: C.purple, at: 'Kazakhstan,', until: 'Turkey', stagger: 0.3 },
        { type: 'callout', text: 'EURASIAN CUSTOMS UNION', bg: '#0a0a0a', size: 58, at: 'customs', until: 'analysis' },
        { type: 'counter', from: 11, to: 3300, prefix: '€', suffix: 'K', fmt: v => v < 1000 ? Math.round(v) + '' : (v / 1000).toFixed(1) + 'M', label: 'KAZAKH CHIP-PART SALES TO RUSSIA · 2021 → 2022', at: 'eleven', until: 'Turkey', y: 200, size: 140, color: C.yellow, dur: 3 },
        { type: 'fill', ids: [ID.TR, ID.UAE], color: C.oil, at: 'Turkey', until: 'end+0.5' },
        { type: 'tag', label: 'TURKEY', ll: LL.TR, at: 'Turkey+0.2', until: 'end+0.5' },
        { type: 'tag', label: 'UAE', ll: LL.UAE, at: 'Emirates', until: 'end+0.5' },
        chipArrow(LL.TR, [44, 52], 're-shipping,', 'end+0.5', { bend: -0.2 }),
        chipArrow(LL.UAE, [47, 50], 're-shipping,+0.3', 'end+0.5', { bend: 0.2 }),
        { type: 'source', text: 'Kazakhstan figures: published trade analysis', at: 'eleven', until: 'Turkey' },
      ] },
    // ---------------- s08 THE TRICKS ----------------
    { seg: 's08', cam: [['start', 20, 40, 380]],
      items: [
        { type: 'fill', ids: [ID.RU], color: C.red, at: 'start', until: 'end+0.5', alpha: 0.7 },
        { type: 'callout', text: 'TRICK 1: SPLIT THE ORDER', bg: '#0a0a0a', size: 56, at: 'Big', until: 'declared' },
        ...[0, 1, 2, 3].map(i => chipArrow([-95 + i * 3, 33 + i], [40 + i * 4, 55 - i], `small+${i * 0.25}`, 'declared', { bend: 0.15 + i * 0.03, width: 4 })),
        { type: 'callout', text: 'TRICK 2: CALL IT “SPARE PARTS”', bg: '#0a0a0a', size: 52, at: 'declared', until: 'Ownership' },
        { type: 'callout', text: 'TRICK 3: HIDE THE OWNER', bg: '#0a0a0a', size: 56, at: 'Ownership', until: 'pays' },
        { type: 'callout', text: 'RUSSIA PAYS A STEEP MARKUP', bg: '#d7263d', size: 54, at: 'pays', until: 'end+0.6' },
        chipArrow(LL.TX, LL.MOS, 'Texas', 'end+0.6', { bend: -0.15, color: C.dollar }),
      ] },
    // ---------------- s08b THE CASES ----------------
    { seg: 's08b', cam: [['start', 33.2, 35.1, 3600], ['Marchenko,', 114.17, 22.32, 7000], ['every', 60, 45, 520]],
      items: [
        { type: 'callout', text: 'AUGUST 2023 · CYPRUS', bg: '#0a0a0a', size: 56, at: 'August', until: 'Marchenko,' },
        { type: 'fill', ids: [ID.CY], color: C.blue, at: 'start', until: 'Marchenko,' },
        { type: 'ring', ll: LL.CY, r: 70, at: 'police', until: 'Marchenko,' },
        { type: 'callout', text: 'ARRESTED AT U.S. REQUEST', bg: '#d7263d', size: 56, at: 'America’s', until: 'Prosecutors' },
        { type: 'callout', text: 'SEPTEMBER 2023 · HONG KONG FIRMS', bg: '#0a0a0a', size: 50, at: 'month', until: 'every' },
        { type: 'ring', ll: LL.HK, r: 60, at: 'Marchenko,', until: 'every' },
        { type: 'callout', text: 'MOST CASES NEVER REACH COURT', bg: '#d7263d', size: 52, at: 'every', until: 'end+0.6' },
        { type: 'source', text: 'U.S. Department of Justice (2023)', at: 'August', until: 'every' },
      ] },
    // ---------------- s09 BATTLEFIELD + ALABUGA ----------------
    { seg: 's09', cam: [['start', 33, 49, 1500], ['Many', 50, 50, 900], ['Alabuga,', 52.05, 55.78, 4000], ['inside', 40, 52, 900]],
      items: [
        { type: 'fill', ids: [ID.UA], color: C.yellow, at: 'start', until: 'Many', alpha: 0.6 },
        { type: 'dots', pts: [[36, 49.5], [33, 48], [37.5, 47.8], [30.5, 50.4], [35, 47.2], [32, 46.7], [34, 50.6]], color: C.red, at: 'drones', until: 'Many', stagger: 0.1 },
        { type: 'callout', text: 'DATE CODES: 2025 & 2026', bg: '#d7263d', size: 58, at: '2025,', until: 'These' },
        { type: 'callout', text: 'NOT OLD STOCKPILES', bg: '#0a0a0a', size: 62, at: 'These', until: 'Many' },
        { type: 'fill', ids: [ID.IR], color: C.green, at: 'Iran’s', until: 'Alabuga,' },
        { type: 'arrow', from: LL.IR, to: LL.ALA, at: 'Shahed,', until: 'Alabuga,', bend: 0.2, color: C.green, width: 6 },
        { type: 'ring', ll: LL.ALA, r: 70, at: 'Alabuga,', until: 'inside' },
        { type: 'tag', label: 'ALABUGA DRONE FACTORY', ll: LL.ALA, at: 'Alabuga,+0.3', until: 'inside' },
        { type: 'callout', text: 'THOUSANDS OF DRONES A YEAR', bg: '#d7263d', size: 54, at: 'thousands', until: 'inside' },
        chipArrow([-90, 38], LL.ALA, 'Western', 'end+0.6', { bend: 0.2 }),
        { type: 'callout', text: 'WESTERN CHIPS, AGAIN', bg: '#0a0a0a', size: 62, at: 'Western', until: 'end+0.6' },
        { type: 'source', text: 'Claims: Ukrainian officials', at: '2025,', until: 'These' },
      ] },
    // ---------------- s10 NVIDIA ----------------
    { seg: 's10', cam: [['start', -40, 35, 400], ['Washington', -10, 32, 330], ['Singapore,', 104, 3, 2600], ['American', 30, 25, 330], ['research', 100, 30, 520], ['alone', 80, 35, 420]],
      items: [
        { type: 'callout', text: 'THE NEXT PRIZE: AI CHIPS', bg: '#118c4f', size: 58, at: 'start+0.3', until: 'Nvidia’s' },
        { type: 'fill', ids: [ID.US], color: C.dollar, at: 'Washington', until: 'Singapore,' },
        { type: 'fill', ids: [ID.CN, ID.RU], color: C.red, at: 'China', until: 'Singapore,', alpha: 0.75 },
        { type: 'counter', from: 0, to: 879868, label: 'AI CHIPS APPROVED FOR CHINA IN 6 MONTHS', at: '900,000', until: 'playbook', y: 200, size: 120, color: C.yellow },
        { type: 'callout', text: 'SAME PLAYBOOK', bg: '#d7263d', size: 66, at: 'playbook', until: 'Singapore,' },
        { type: 'ring', ll: LL.SG, r: 60, at: 'Singapore,', until: 'American' },
        { type: 'tag', label: 'SINGAPORE', ll: LL.SG, at: 'Singapore,+0.2', until: 'American', dir: 'up' },
        { type: 'callout', text: 'LIED ABOUT THE DESTINATION', bg: '#0a0a0a', size: 54, at: 'lying', until: 'American' },
        { type: 'fill', ids: [ID.US], color: C.blue, at: 'American', until: 'research' },
        { type: 'counter', from: 0, to: 300, prefix: '$', suffix: 'M', label: 'NVIDIA-POWERED SERVERS (ALLEGED)', at: '300', until: 'research', y: 200, size: 130, color: C.dollar },
        chipArrow([-120, 36], [101.7, 3.6], 'routed', 'research', { bend: -0.12 }),
        { type: 'fill', ids: [ID.MY], color: C.purple, at: 'Malaysia', until: 'end+0.6' },
        chipArrow([101.7, 3.6], [110, 32], 'China.', 'research', { bend: -0.2 }),
        { type: 'callout', text: '80 NEWEST NVIDIA SERVERS', bg: '#d7263d', size: 56, at: '80', until: 'Nobody' },
        chipArrow([101.7, 3.6], LL.HK, 'stored', 'end+0.6', { bend: -0.25 }),
        chipArrow(LL.HK, [60, 56], 'Russia.', 'end+0.6', { bend: -0.2 }),
        { type: 'fill', ids: [ID.RU], color: C.red, at: 'Russia.', until: 'end+0.6', alpha: 0.75 },
        { type: 'callout', text: 'SALE NOT PROVEN', bg: '#0a0a0a', size: 62, at: 'Nobody', until: 'offer' },
        { type: 'callout', text: 'BUT THE MARKET IS THERE', bg: '#d7263d', size: 58, at: 'offer', until: 'end+0.6' },
        { type: 'source', text: 'Sources: House Foreign Affairs Committee; U.S. DOJ; Singapore AGC; WireScreen', at: '900,000', until: 'end' },
      ] },
    // ---------------- s11 THE TWIST ----------------
    { seg: 's11', cam: [['start', ...WORLD]],
      items: [
        { type: 'callout', text: 'MOST CHIPS WERE NEVER STOLEN', bg: '#d7263d', size: 56, at: 'start', until: 'sold' },
        { type: 'callout', text: 'SOLD LEGALLY', bg: '#118c4f', size: 66, at: 'sold', until: 'crime' },
        ...[[[-97, 33], [8.5, 50]], [[8.5, 50], [114, 22.5]], [[114, 22.5], [77, 43]], [[77, 43], [44, 55]]].map(([a, b], i) => chipArrow(a, b, `legally+${i * 0.6}`, 'leak', { bend: 0.2, color: i < 2 ? C.dollar : C.red })),
        { type: 'callout', text: 'THE CRIME: 3–4 SALES LATER', bg: '#0a0a0a', size: 54, at: 'crime', until: 'leak' },
        { type: 'callout', text: 'WHY SANCTIONS LEAK', bg: '#d7263d', size: 66, at: 'leak', until: 'trying#2' },
        { type: 'callout', text: 'CONTROL EVERY RESALE. FOREVER.', bg: '#0a0a0a', size: 50, at: 'control', until: 'end+0.6' },
      ] },
    // ---------------- s12 PUSHBACK ----------------
    { seg: 's12', cam: [['start', 70, 35, 380]],
      items: [
        { type: 'fill', ids: [ID.CN, ID.TR, ID.UAE, ID.KZ, ID.KG, ID.AM], color: C.red, at: 'blacklisted', until: 'Banks', stagger: 0.25 },
        { type: 'callout', text: 'HUNDREDS OF FIRMS BLACKLISTED', bg: '#d7263d', size: 52, at: 'hundreds', until: 'Banks' },
        { type: 'callout', text: 'BANKS GET NERVOUS', bg: '#0a0a0a', size: 62, at: 'Banks', until: 'codes' },
        { type: 'callout', text: 'EVERY CHIP CARRIES A DATE CODE', bg: '#0a0a0a', size: 52, at: 'codes', until: 'Russia,' },
        { type: 'fill', ids: [ID.UA], color: C.yellow, at: 'Ukraine', until: 'Russia,' },
        { type: 'fill', ids: [ID.RU], color: C.red, at: 'Russia,', until: 'end+0.5' },
        { type: 'callout', text: 'LATER · PRICIER · MAYBE FAKE', bg: '#d7263d', size: 54, at: 'Every#2', until: 'flow' },
        { type: 'callout', text: 'STILL FLOWING', bg: '#0a0a0a', size: 66, at: 'flow', until: 'end+0.6' },
      ] },
    // ---------------- s13 BIGGER PICTURE + TEASE ----------------
    { seg: 's13', cam: [['start', ...WORLD], ['Taiwan.', 121, 23.7, 2600, 1.6]],
      items: [
        { type: 'callout', text: 'BIGGER THAN RUSSIA', bg: '#0a0a0a', size: 66, at: 'start+0.3', until: 'routes' },
        ...[[[-97, 33], [60, 55]], [[8.5, 50], [53, 32]], [[114, 22.5], [127, 40]], [[101.7, 3.1], [70, 40]]].map(([a, b], i) => chipArrow(a, b, `routes+${i * 0.4}`, 'Which', { bend: 0.2, color: '#fff' })),
        { type: 'callout', text: 'SHIPPING RECORDS · CUSTOMS · WAREHOUSES', bg: '#0a0a0a', size: 44, at: 'fought#2', until: 'next' },
        { type: 'fill', ids: [ID.TW], color: C.dollar, at: 'island', until: 'end+4.2' },
        { type: 'ring', ll: LL.TW, r: 70, at: 'island', until: 'end+4.2' },
        { type: 'callout', text: 'NEXT: WHY TAIWAN IS THE MOST DANGEROUS PLACE ON THE MAP', bg: '#d7263d', size: 40, at: 'next', until: 'end+4.2' },
      ] },
  ];

  // full-screen cartoon clips from toons.json (loaded by the engine page)
  const toonsBySeg = {};
  for (const [seg, at, dur, motion, img] of window.TOONS) (toonsBySeg[seg] = toonsBySeg[seg] || []).push({ type: 'toon', img, at, dur, motion });
  for (const sc of map) sc.items.push(...(toonsBySeg[sc.seg] || []));
  return map;
};
