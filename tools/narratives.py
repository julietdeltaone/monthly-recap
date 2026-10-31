"""Month-by-month story for Jan to Aug 2026. Numbers are computed; this file holds only what happened.
Career threads are written knowing how they turned out, so the year reads start to finish."""

# OTS thread stages, used for the progress bar on every Career tab
OTS_STAGES = ['Considering', 'Recruiter', 'DD-368 sent', 'DD-368 approved', 'AFOQT taken', 'Retest route', 'Retest booked', 'Board']

N = {}

N['2026-01'] = dict(
    brief=['January set the baselines: Campus Safety & Security at Clarkson, two MBA courses, and the gym habit started in earnest. Global Entry came through on Jan 8.',
           'The annual physical on Jan 14 flagged right knee overuse from running, so cardio stayed light. The January drill in Syracuse was cancelled for weather.'],
    timeline=[['Jan 4', 'Acts series opens at CBC'], ['Jan 5', 'MBA term starts: AC 604, OM 607'], ['Jan 8', 'Global Entry approved'],
              ['Jan 14', 'Annual physical'], ['Jan 15', 'CU EMS headshots, 13 subjects'], ['Jan 24', 'Drill cancelled for weather']],
    phys='Knee overuse flagged at the Jan 14 physical; running was cut back and cross-training took its place.',
    career=dict(stage=0, brief='Working Campus Safety & Security at Clarkson. No career moves yet; the officer question was still a someday question.',
                rows=[['Jan 24', 'Drill weekend in Syracuse cancelled for weather.']],
                paths=[['Clarkson', 'Campus Safety & Security', 'Active'], ['Guard', 'HHC, 27th IBCT; ETS June 2027', ''], ['OTS', 'Not started', '']]),
    intel=dict(brief='Winter term of the online MBA: AC 604 Financial & Managerial Accounting and OM 607 Global Supply Chain Management, Jan 5 to Mar 13.',
               courses=[['AC 604', 'Financial & Managerial Accounting', 'DeJoy. Statements, costing, budgeting, CVP.', 'Winter'],
                        ['OM 607', 'Global Supply Chain Management', 'Kauffman. Sourcing, logistics, inventory, risk.', 'Winter']],
               study='Monthly focus: personal finance. Read The Practical Money Handbook; takeaway was that fixed costs hard-code fragility before problems show up.'),
    creative=dict(brief='CU EMS came back for a second headshot session on Jan 15: 13 subjects, six of them new staff. A Jan 2 session fell through when the client never confirmed.',
                  rows=[['Jan 2', 'Headshot session, client no-show.'], ['Jan 10', 'Waugg wedding cancelled.'], ['Jan', 'Bookings on the calendar: McGrath Jun 6, Niles Jun 27, Eddy Aug 22.']]),
    refl=dict(quote='Baselines set. The habit started.', items=[['a. Start', 'January was about starting things and writing down where they began: money, gym, church, school.'],
              ['b. Knee', 'The knee note mattered. Less running now so there could be more later.']],
              line='The baseline month.', carry=['Keep the gym streak', 'Finish the winter MBA term', 'Fill the 2026 wedding calendar']),
)

N['2026-02'] = dict(
    brief=['February was consistency over intensity: 18 gym days, spending well under the $2,500 cap, and the MBA term past its midpoint.',
           'Drill weekend ran Feb 20 to 22. The monthly study goal (STEM) was missed, and the JDM website was renewed on Squarespace.'],
    timeline=[['Feb 1', 'Acts 3 to 4 at CBC'], ['Feb 20', 'Drill weekend, Feb 20 to 22'], ['Feb 22', 'Squarespace renewed']],
    phys='Volume up about a quarter from January. Best run: 3.11 mi outdoors at 8:28 per mile.',
    career=dict(stage=0, brief='Still on Campus Safety & Security. Drill weekend Feb 20 to 22.',
                rows=[['Feb 20', 'Drill weekend, Feb 20 to 22.']],
                paths=[['Clarkson', 'Campus Safety & Security', 'Active'], ['Guard', 'Drill Feb 20 to 22', ''], ['OTS', 'Not started', '']]),
    intel=dict(brief='AC 604 midterm 92.1% with modules at 100%. OM 607 running 95.8% with the final still ahead.',
               courses=[['AC 604', 'Financial & Managerial Accounting', 'Midterm 92.1%; modules 100%.', '92%'],
                        ['OM 607', 'Global Supply Chain Management', 'Midterm 95%; inventory case 100%.', '96%']],
               study='Monthly focus was STEM fundamentals. It did not happen, and it is logged that way.'),
    creative=dict(brief='No shoots in February. The website was renewed and the 2026 wedding calendar held: McGrath, Niles, and Eddy signed.',
                  rows=[['Feb 22', 'Squarespace renewal, $192.']]),
    refl=dict(quote='Consistency over intensity.', items=[['a. Steady', 'Nothing spectacular, nothing dropped except the study goal. That is a fine February.']],
              line='The steady month.', carry=['Finish the term strong', 'Pick a March study focus that fits']),
)

N['2026-03'] = dict(
    brief=['March shipped real work: the TaxiZero fare estimator went live, the JDM website and intake form were rebuilt, and an LMSW documentary short was finished with M. Maurer.',
           'The winter term closed with a 3.83 GPA. At drill, MMCS digital mission command training replaced the planned study topic. The career question started to take shape.'],
    timeline=[['Mar 1', 'Acts 6 at CBC'], ['Mar', 'TaxiZero fare estimator live'], ['Mar 13', 'Winter term ends, 3.83 GPA'], ['Mar 22', 'Acts 9 at CBC'], ['Mar 28', 'Kodak Center show, Rochester'], ['Mar 29', 'Palm Sunday']],
    phys='Bench reached 215 for reps twice and a 6-mile outdoor run went 56:22. Plank was the weak AFT event.',
    career=dict(stage=0, brief='With the Guard contract ending June 2027, the officer route versus the business route became a real question. Three paths came into view: Air Force OTS, civil service, and United Airlines.',
                rows=[['Mar', 'MMCS digital mission command training at drill, Fort Drum.'], ['Mar', 'Decided to cancel the Amex Platinum and keep the Chase Sapphire Reserve.']],
                paths=[['Clarkson', 'Campus Safety & Security', 'Active'], ['OTS', 'Considering', ''], ['United', 'Applying', ''], ['Civil service', 'Exam ahead', '']]),
    intel=dict(brief='Winter term closed with A grades in both courses, a 3.83 term GPA.',
               courses=[['AC 604', 'Financial & Managerial Accounting', 'Closed with an A.', 'A'],
                        ['OM 607', 'Global Supply Chain Management', 'Closed with an A.', 'A']],
               study='The history goal was swapped for Army work: MMCS operator notes, verified against the system in the field. Also learned APIs, keys, and GitHub Pages by building TaxiZero.'),
    creative=dict(brief='Three finished projects: the LMSW documentary short, the rebuilt JDM website with a service-specific intake form, and the TaxiZero fare estimator using the Google Maps API.',
                  rows=[['Mar', 'LMSW video project with M. Maurer.'], ['Mar', 'JDM website and intake form rebuilt.'], ['Mar', 'TaxiZero fare estimator, live on GitHub Pages.'], ['Mar', 'Signed: McGrath Jun 6, Niles Jun 27, Eddy Aug 22.']]),
    refl=dict(quote='Finished, not just started.', items=[['a. Shipping', 'Three projects went live. Finishing is the habit worth keeping.'],
              ['b. June 2027', 'The Guard contract ends June 2027. Deliberate beats default, so the decision starts now.']],
              line='The shipping month.', carry=['Talk to an Air Force recruiter', 'Spring term: OS 603, MK 610', 'Fix the plank']),
)

N['2026-04'] = dict(
    brief=['April was the widest the picture got: all three career paths were open at once. The Air Force recruiter conversation started, United moved to a recorded pre-interview, and the civil service exam was set for May 9.',
           '24 gym days, the most of the spring, and a $1,250 Army tuition reimbursement landed through SUNY Potsdam.'],
    timeline=[['Mar 30', 'Spring term starts: OS 603, MK 610'], ['Apr 7', '$1,250 tuition reimbursement'], ['Apr', 'United recorded pre-interview'], ['Apr 30', 'Line Officer brief, 318th RCS']],
    phys='Trap bar deadlift reached 335 for 4. Most training days of the spring.',
    career=dict(stage=1, brief='All three paths active. Recruiter contact made with the 318th Recruiting Squadron, and on Apr 30 the Line Officer program brief. The DD-368 conditional release was the next step.',
                rows=[['Apr', 'Air Force recruiter contact; Ashley Araya at 318th RCS handling the file.'], ['Apr 30', 'Attended the 318th RCS Line Officer brief.'], ['Apr', 'United crew scheduler application, recorded pre-interview.'], ['Apr', 'Civil service exam scheduled for May 9.']],
                paths=[['OTS', 'Recruiter engaged', 'Active'], ['United', 'Pre-interview', 'Active'], ['Civil service', 'Exam May 9', 'Active'], ['Clarkson', 'Campus Safety & Security', '']]),
    intel=dict(brief='Spring term: OS 603 Leadership & Organizational Behavior and MK 610 Marketing Management, Mar 30 to mid June. Army tuition assistance covered both at $750 each.',
               courses=[['OS 603', 'Leadership & Organizational Behavior', 'Zeigler. Weekly assignments, leadership development plan.', 'Spring'],
                        ['MK 610', 'Marketing Management', 'Carlson. White Claw case due Apr 29.', 'Spring']],
               study='Leadership and organizational behavior, through OS 603.'),
    creative=dict(brief='A quiet month for shoots while spring bookings built for May and June.', rows=[]),
    refl=dict(quote='Every lane open at once.', items=[['a. Wide', 'April is the widest the picture gets: recruiter, United, civil service, and the business all live.'],
              ['b. Ahead', 'Something would close first. It turned out to be United, in May.']],
              line='The open-field month.', carry=['DD-368 to SSG Wilson', 'Civil service exam May 9', 'May shoots']),
)

N['2026-05'] = dict(
    brief=['May is when the field narrowed. United went with other candidates. The civil service exam was taken May 9. The DD-368 request went to SSG Wilson, making OTS the live path.',
           'JD Meyers Productions had its busiest month yet: four portrait sessions, a wedding, and a wedding film.'],
    timeline=[['May 3', 'Forgiveness, CBC'], ['May 9', 'Civil service exam'], ['May', 'United closed'], ['May 10', 'Mother’s Day; two portrait shoots'], ['May 19', 'Gerow wedding'], ['May 30', 'Zufall wedding film']],
    phys='Bench hit 215 for 4 on May 26 and an 8-mile outdoor run went 1:17.',
    career=dict(stage=2, brief='United closed after the pre-interview. The civil service exam was done, but the agility test fell during Annual Training, so an accommodation request went in with orders. The DD-368 email went to SSG Wilson.',
                rows=[['May 9', 'Police officer and deputy sheriff exam taken.'], ['May', 'United went with other candidates.'], ['May', 'DD-368 request sent to SSG Wilson.'], ['May', 'Civil service accommodation request filed for the AT conflict.']],
                paths=[['OTS', 'DD-368 requested', 'Active'], ['Civil service', 'Exam done; agility test conflicts with AT', 'Active'], ['United', 'Closed', ''], ['Clarkson', 'Campus Safety & Security', '']]),
    intel=dict(brief='OS 603 at 92.5% and MK 610 at 94% heading into June finals.',
               courses=[['OS 603', 'Leadership & Organizational Behavior', 'Running 92.5%.', '92.5%'], ['MK 610', 'Marketing Management', 'Running 94%.', '94%']],
               study='Psychology and marketing, through MK 610.'),
    creative=dict(brief='Six paid jobs in May: senior and family portraits plus two weddings.', rows=[]),
    refl=dict(quote='The field narrowed, and that is clarity.', items=[['a. Closed doors', 'United saying no was a closed door, not a verdict. It made the OTS path obvious.'],
              ['b. Business', 'The photography business delivered when the career picture was uncertain.']],
              line='The narrowing month.', carry=['Get the DD-368 approved before Jul 4', 'Finish the spring term']),
)

N['2026-06'] = dict(
    brief=['The DD-368 cleared the chain and reached the Air Force recruiter before the Jul 4 deadline. The spring semester closed with a 4.0.',
           'A new thread opened on Jun 30: an interview for the Administrative Coordinator role at the Lewis School. Both outdoor runs came back faster than May.'],
    timeline=[['Jun 6', 'McGrath wedding'], ['Jun 10', 'MK 610 ends'], ['Jun 12', 'OS 603 ends'], ['Jun 27', 'JuliaKia wedding film'], ['Jun 30', 'Lewis School interview']],
    phys='Trap bar deadlift 355 for 6 on Jun 23. An 8-mile run at 8:37 per mile, a minute per mile faster than May.',
    career=dict(stage=3, brief='DD-368 approved and forwarded to the Air Force recruiter, meeting the Jul 4 deadline. The portal set an AFOQT due date. Civil service stayed quiet on the AT accommodation.',
                rows=[['Jun', 'DD-368 approved and sent to the Air Force recruiter.'], ['Jun', 'AFOQT due date set in the portal.'], ['Jun 30', 'Interviewed for Administrative Coordinator, Lewis School; PT and OT directors on the panel.']],
                paths=[['OTS', 'DD-368 approved', 'Active'], ['Lewis School', 'Interviewed Jun 30', 'Active'], ['Civil service', 'Waiting on accommodation', ''], ['Clarkson', 'Campus Safety & Security', '']]),
    intel=dict(brief='Spring semester closed with a 4.000 term GPA and a 3.917 cumulative. Winter tuition reimbursement was resolved with HR and Finance.',
               courses=[['OS 603', 'Leadership & Organizational Behavior', 'Closed Jun 12.', 'A'], ['MK 610', 'Marketing Management', 'Closed Jun 10.', 'A']],
               study='Military history and doctrine, ahead of the officer board.'),
    creative=dict(brief='Two weddings: the McGrath photos on Jun 6 and a JuliaKia wedding film on Jun 27.', rows=[]),
    refl=dict(quote='The deadline that mattered got met.', items=[['a. Out of my hands', 'The DD-368 is with the recruiter now.'],
              ['b. Cardio', 'Quietly the best cardio month of the year so far.']],
              line='The deadline month.', carry=['Start at the Lewis School', 'Annual Training Aug 6 to 21', 'AFOQT prep']),
)

N['2026-07'] = dict(
    brief=['The job changed. Campus Safety & Security ended and the Administrative Coordinator role at the Lewis School started on Jul 20, under Richard Tacchino.',
           'Training shifted to cardio: frisbee, soccer, and outdoor running took most of the hours. Between semesters, reading on military strategy filled the study slot.'],
    timeline=[['Jul 5', 'Guest speaker, 1 Samuel'], ['Jul 20', 'Started at the Lewis School'], ['Jul 26', 'Conviction vs. condemnation'], ['Jul 29', 'Martha portraits']],
    phys='Cardio took over: pickup frisbee and soccer most evenings plus outdoor runs. Lifting held but set no new maxes.',
    career=dict(stage=3, brief='Started as Administrative Coordinator at the Lewis School on Jul 20. OTS was waiting on the AFOQT.',
                rows=[['Jul 20', 'Administrative Coordinator, Lewis School of Health Sciences.'], ['Jul', 'Campus Safety & Security resignation effective.']],
                paths=[['Lewis School', 'Administrative Coordinator', 'Active'], ['OTS', 'Waiting on AFOQT', 'Active'], ['Civil service', 'Waiting', ''], ['Guard', 'AT Aug 6 to 21', '']]),
    intel=dict(brief='Between semesters. Spring closed at 4.000; fall starts in September with FN 608, IS 606, and OM 603.', courses=[],
               study='Self-directed: modern military strategy and doctrine, from the levels of war to lessons from Ukraine.'),
    creative=dict(brief='A quiet month while the August weddings approached.', rows=[]),
    refl=dict(quote='New job, same habits.', items=[['a. Transition', 'The month’s real story is the job. Everything else held steady around it.']],
              line='The transition month.', carry=['Annual Training', 'Two August weddings', 'AFOQT Aug 31']),
)

N['2026-08'] = dict(
    brief=['Annual Training at Fort Drum ran Aug 6 to 21, two weddings were delivered, and the AFOQT was taken on Aug 31.',
           'Quant came back at 6 against a minimum of 10, so a retest after the 90-day wait became the next step. The camera overheated at the Eddy wedding; the bride got a direct explanation and a $150 refund.'],
    timeline=[['Aug 1', 'Choate wedding'], ['Aug 2', 'Repentance & confession, CBC'], ['Aug 6', 'Annual Training, Aug 6 to 21'], ['Aug 22', 'Eddy wedding'], ['Aug 31', 'AFOQT']],
    phys='Training restarted Aug 24 after AT. Trap bar deadlift 315 for 8 on Aug 28.',
    career=dict(stage=4, brief='The one and only Annual Training with the unit: S1 work and a rotation to the TAC as RTO. The AFOQT on Aug 31 passed every section except quant.',
                rows=[['Aug 6', 'Annual Training at Fort Drum through Aug 21.'], ['Aug', 'Sheriff’s agility test missed; it fell during AT.'], ['Aug 31', 'AFOQT: verbal 61, quant 6 (minimum 10).']],
                paths=[['OTS', 'Retest needed (quant)', 'Active'], ['Lewis School', 'Administrative Coordinator', 'Active'], ['Civil service', 'Agility test missed', ''], ['Guard', 'AT complete', '']],
                afoqt=True),
    intel=dict(brief='Fall term starts in September. August’s center of gravity was a single exam.', courses=[],
               study='AFOQT prep. The gap turned out to be math, not overall aptitude: verbal 61, quant 6.'),
    creative=dict(brief='Two weddings delivered. The camera overheated as the bride walked in at the Eddy wedding; coverage resumed for the vows and the bride got a direct explanation and a $150 refund.',
                  rows=[['Aug', 'Lesson: backup bodies and heat management are non-negotiable on wedding days.']]),
    refl=dict(quote='Backup bodies, cold cameras, drilled math.', items=[['a. Cadence', 'AT, two weddings, and the AFOQT back to back is not sustainable, but it showed what is possible.'],
              ['b. Systems', 'The camera and the quant score get fixed the same way: preparation, not willpower.']],
              line='The stress-test month.', carry=['Find the retest voucher route', 'Fall MBA term', 'Settle the Megan Eddy delivery']),
)
