/* The 2026 story: threads (one color each, used on every page), the year swimlanes, and JD's own words.
   Lane positions use month numbers with decimals: 3.5 = mid March, 12.9 = end of December. */
window.STORY = {
  threads: {
    ots:     { label: 'Air Force OTS', hue: 'red' },
    guard:   { label: 'Army Guard', hue: 'green' },
    job:     { label: 'Lewis School job', hue: 'emerald' },
    safety:  { label: 'Campus Safety', hue: 'slate' },
    civil:   { label: 'Civil service', hue: 'sky' },
    united:  { label: 'United', hue: 'orange' },
    mba:     { label: 'MBA', hue: 'blue' },
    jdm:     { label: 'JD Meyers Productions', hue: 'amber' },
    fitness: { label: 'Fitness', hue: 'violet' },
    faith:   { label: 'Faith', hue: 'magenta' },
    money:   { label: 'Savings', hue: 'teal' }
  },
  /* timeline text to thread, first match wins */
  rules: [
    ['AFOQT|OTS|DD-368|recruit|Line Officer|Air Force|voucher|Aim High', 'ots'],
    ['drill|Annual Training|\\bAT\\b|Camp Smith|Guard|MMCS', 'guard'],
    ['Lewis School|PT Month|White Coat', 'job'],
    ['Campus Safety', 'safety'],
    ['civil service|sheriff|agility|police', 'civil'],
    ['United', 'united'],
    ['MBA|term|semester|AC 604|OM 60|OS 603|MK 610|FN 608|IS 606|final|GPA|course', 'mba'],
    ['wedding|portrait|headshot|shoot|studio|JDM|B&H|film|TaxiZero|website|Bernal|Coogan', 'jdm'],
    ['run|5K|gym|bench|deadlift|physical', 'fitness'],
    ['CBC|sermon|Acts|Galatians|Palm Sunday|Repentance|Conviction|Forgiveness|speaker', 'faith'],
    ['tuition|reimbursement|Verizon|savings|Global Entry', 'money']
  ],
  lanes: [
    { t: 'ots', items: [
      { at: 1.3, label: 'Officer route? One call about Guard OCS' }, { at: 3.4, label: 'Chose the Air Force over OCS' },
      { at: 4.95, label: 'Recruiter + Line Officer brief' }, { at: 5.5, label: 'DD-368 requested' }, { at: 6.6, label: 'DD-368 approved' },
      { at: 8.97, label: 'AFOQT: quant 6', kind: 'flag' }, { at: 9.3, label: 'Voucher route' }, { at: 10.65, label: 'Retest booked' },
      { at: 11.97, label: 'Retest Nov 30', kind: 'next' } ] },
    { t: 'job', items: [ { from: 1, to: 7.65, label: 'Campus Safety & Security', t: 'safety' }, { at: 6.97, label: 'Interview' }, { from: 7.65, to: 11, label: 'Administrative Coordinator, Lewis School' } ] },
    { t: 'guard', items: [ { at: 1.8, label: 'Drill cancelled' }, { at: 2.7, label: 'Drill' }, { at: 3.5, label: 'MMCS training' },
      { from: 8.2, to: 8.7, label: 'Annual Training' }, { at: 10.78, label: 'Camp Smith screening' }, { at: 12.9, label: 'ETS Jun 2027', kind: 'next' } ] },
    { t: 'civil', items: [ { from: 4, to: 5.6, label: 'United, closed', t: 'united' }, { at: 5.3, label: 'Civil service exam' }, { at: 8.5, label: 'Agility test missed (AT)', kind: 'flag' }, { at: 10.97, label: 'Agility test' } ] },
    { t: 'mba', items: [ { from: 1.15, to: 3.45, label: 'Winter: 3.83' }, { from: 3.97, to: 6.4, label: 'Spring: 4.0' }, { from: 9, to: 11.35, label: 'Fall: 3 courses' } ] },
    { t: 'jdm', items: [ { at: 1.5, label: 'CU EMS headshots' }, { at: 3.5, label: 'Site + TaxiZero' }, { from: 5.25, to: 6.95, label: '9 shoots, 3 weddings' },
      { at: 8.03, label: 'Choate wedding' }, { at: 8.7, label: 'Eddy wedding' }, { at: 10.1, label: 'Ken & TaShell' }, { at: 10.42, label: 'Studio launch' } ] },
    { t: 'fitness', items: [ { from: 1, to: 11, label: 'Gym: 17 to 28 days a month' }, { at: 5.85, label: '8 mi run' }, { at: 9.2, label: '9 mi run' }, { at: 9.6, label: '5K 23:39' }, { at: 10.97, label: 'Agility test' } ] },
    { t: 'faith', items: [ { from: 1, to: 3.98, label: 'Acts' }, { from: 5.75, to: 6.95, label: 'Trust series' }, { from: 7.8, to: 8.1, label: 'Conviction' }, { from: 9.4, to: 11, label: 'Fruit of the Spirit' } ] },
    { t: 'money', items: [ { at: 6.9, label: 'Passed $10k saved', kind: 'win' }, { at: 9.3, label: 'Phone payoff' }, { at: 10.97, label: '$17.7k YTD' } ] }
  ],
  words: [
    ['The start', 'At the start of 2026 there were no set career goals. The only thing on the table was maybe a longer military career. I made one call to an O3 about Guard OCS, then decided that if I went officer, it would be the Air Force.'],
    ['The job', 'I was not planning a local career change. I was bored at work and curious what other departments on the Hill campus were paying. That is when I saw the administrative coordinator listing. Campus Safety paid $17.25 an hour on nights, and the environment was not great; I wanted better pay and normal hours.'],
    ['Proudest', 'The most productive year I have had on several fronts: the number of weddings and the JD Meyers Productions business overall, landing the administrative coordinator job, and bouncing back from a rough 2025.'],
    ['People', 'My close friends Dan, David, and Melody. And since Annual Training in August, a real kinship with the S1 group at HHC.'],
    ['Air Force', 'I realized I am not built for the Army. I am not an outdoors type; I lean intellectual. If I do eight or twenty years, it has to be the Air Force. I am now leaning toward public affairs, to bring the photography in.'],
    ['United', 'Always a long shot on the back burner, from my SkyWest days at the Ogdensburg airport. A friend in Chicago kept pushing me to join him as a crew scheduler. Unrealistic with the Guard, but I wanted to know if it was possible.'],
    ['Civil service', 'An earlier police academy run did not end in a hire. I took a break and got some life experience. The sheriff’s office or a local department would be great, but the admin job has shown me I am more geared to the background work: organization and administration.'],
    ['The Guard', 'I am glad I did it and glad to be getting out. If I did it again I would have gone Air Force. I think I had something to prove; the Army was the original flavor.'],
    ['The business', 'JD Meyers Productions has always been about stretching side income as far as it goes, never the main thing.'],
    ['The MBA', 'A redemption. Criminal investigations is a narrow degree if I am not in law enforcement; the MBA makes it broad.'],
    ['Fitness', 'Pass the AFT, stay in shape, and always do a little more than last time.'],
    ['Faith', 'Still going steady. Working on more daily Bible reading and prayer.']
  ]
};
