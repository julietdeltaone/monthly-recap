"""One front door for the monthly recap. Never pushes anything and never approves anything.

  python3 tools/recap.py status 2026-11 [inputs_dir]   which inputs are present, what is missing, which stage the month is at
  python3 tools/recap.py draft  2026-11 [inputs_dir]   build what the inputs allow into draft/<month>.json (figures with sources)
  python3 tools/recap.py ready  2026-11                exit 0 only if JD's approval record matches the current draft

Approval is written only by JD's click in the hub (or Council Desk): draft/<month>.approved holds the draft fingerprint and time.
This script and any AI only read it. If the draft changes after approval the fingerprint no longer matches and the month
drops back to awaiting approval.

Inputs folder (default ./inputs/<month>/), the same files the Drive folder 'Recap Inputs/<month>' holds:
  origin.csv          Origin transactions export            -> Financial   (tools/finance.py)
  workouts.csv        hub Workouts tab as FitNotes CSV      -> Physical    (tools/hub_workouts.py, tools/gym.py)
  ledger.csv          Notion/JDM ledger export              -> Creative    (build_month.ledger)
  faith.txt           Calvary voice-note transcripts        -> Spiritual   (data/sermons-2026.js)
  moodle.txt          grades / course notes (paste)         -> Intellectual
  career.txt          OTS stage + dated events              -> Career
Stages: waiting on inputs -> awaiting approval -> approved -> published.
"""
import sys, os, json, hashlib, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = [('financial', 'Financial', 'origin.csv'), ('physical', 'Physical', 'workouts.csv'), ('creative', 'Creative', 'ledger.csv'),
        ('spiritual', 'Spiritual', 'faith.txt'), ('intellectual', 'Intellectual', 'moodle.txt'), ('career', 'Career', 'career.txt')]


def paths(m, inputs):
    return (inputs or os.path.join(ROOT, 'inputs', m)), os.path.join(ROOT, 'draft')


def present(folder):
    out = {}
    for key, label, fn in SPEC:
        p = os.path.join(folder, fn)
        ok = os.path.exists(p)
        out[key] = {'label': label, 'file': fn, 'present': ok,
                    'modified': dt.datetime.fromtimestamp(os.path.getmtime(p)).isoformat(timespec='minutes') if ok else None}
    return out


def digest(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest() if os.path.exists(p) else ''


def stage(m, inputs):
    folder, dd = paths(m, inputs)
    have = present(folder)
    draft = os.path.join(dd, m + '.json')
    appr = os.path.join(dd, m + '.approved')
    if not os.path.exists(draft):
        return ('published' if os.path.exists(os.path.join(ROOT, 'data', m + '.js')) else 'waiting on inputs'), have
    if os.path.exists(appr) and open(appr).read().split()[0] == digest(draft):
        return 'approved', have
    return 'awaiting approval', have


def physical(folder, m):
    import gym
    g = gym.month(gym.load(os.path.join(folder, 'workouts.csv')), m)
    src = 'Command Center Workouts tab (FitNotes via Orion Delta)'
    return [['Training days', g['days'], src], ['Lifting volume (lb)', g['volume'], src], ['Cardio sessions', g['cardioSessions'], src],
            ['Cardio minutes', g['cardioMin'], src],
            ['Distance (mi, unit assumed)', round(g['miles'], 1), src + '; the hub tab has no distance unit']]


def draft(m, inputs):
    folder, dd = paths(m, inputs)
    os.makedirs(dd, exist_ok=True)
    have = present(folder)
    figs = {}
    if have['physical']['present']:
        figs['physical'] = physical(folder, m)
    miss = [v['label'] + ' (' + v['file'] + ')' for v in have.values() if not v['present']]
    d = {'month': m, 'built': dt.datetime.now().isoformat(timespec='minutes'), 'figures': figs, 'missing': miss,
         'note': 'Draft only. Nothing is published until JD approves and it is pushed.'}
    json.dump(d, open(os.path.join(dd, m + '.json'), 'w'), indent=1)
    return d


if __name__ == '__main__':
    cmd, m = sys.argv[1], sys.argv[2]
    inputs = sys.argv[3] if len(sys.argv) > 3 else None
    if cmd == 'status':
        s, have = stage(m, inputs)
        print(json.dumps({'month': m, 'stage': s, 'inputs': have}, indent=1))
    elif cmd == 'draft':
        print(json.dumps(draft(m, inputs), indent=1))
    elif cmd == 'ready':
        s, _ = stage(m, inputs)
        print(s)
        sys.exit(0 if s == 'approved' else 1)
