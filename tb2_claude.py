import sqlite3
from contextlib import contextmanager
from files import luf_original

DB_PATH = "sdg3_game.db"
START_CODE = "oscar"

REGION_ABBR = ['us', 'af', 'cn', 'me', 'sa', 'la', 'pa', 'ec', 'eu', 'se']
MINISTRIES = ["Poverty", "Inequality", "Empowerment", "Food", "Energy", "Future"]

# Maps each ministry to its budget key
MINISTRY_BUD_KEY = {
    'Poverty':     'pov',
    'Inequality':  'ineq',
    'Empowerment': 'emp',
    'Food':        'food',
    'Energy':      'ener',
}

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def get_pols_by_ta(m):
    """Return list of policy tags for a given ministry."""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT pol_tag FROM policies WHERE pol_ministry = ?", (m,)
        )
        return [row[0] for row in cursor.fetchall()]


def get_inv_props(game_id, current_round, region_tag, m, p):
    """Return the slider position (0–1) for a given policy decision."""
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT pd.value, pol.pol_min, pol.pol_max
            FROM policy_decisions pd
            JOIN policies pol ON pol.pol_tag = pd.pol_tag
            WHERE pd.game_id = ? AND pd.round = ? AND pd.region_tag = ?
              AND pd.ministry = ? AND pd.pol_tag = ?
            """,
            (game_id, current_round, region_tag, m, p)
        ).fetchone()

    x, mi, mx = row[0], row[1], row[2]
    return (x - mi) / (mx - mi)


def get_budget(game_id, current_round, region_tag):
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT ta, value FROM bud WHERE game_id = ? AND round = ? AND reg = ?",
            (game_id, current_round, region_tag)
        )
        return {row[0]: row[1] for row in cursor.fetchall()}


def get_tab(game_id, runde, reg):
    bud = get_budget('START', 0, reg) if runde == 1 else get_budget(game_id, runde - 1, reg)

    results = {}  # {ministry_name: {pol_tag: amount}}

    for m in MINISTRIES:
        if m == 'Future':
            continue
        bud_key = MINISTRY_BUD_KEY[m]
        tags = get_pols_by_ta(m)
        results[m] = {
            p: bud[bud_key] * get_inv_props(game_id, runde, reg, m, p)
            for p in tags
        }

    total = sum(v for ministry in results.values() for v in ministry.values())
    bud_pct = total / bud['bud'] * 100.0

    return bud, total, bud_pct, results


def print_ministry(name, data):
    print(name)
    print(f"  {'Policy':<50} {'Amount':<12}")
    print(f"  {'-'*80}")
    mt = 0.0
    for tag, amount in data.items():
        print(f"  {tag:<50}  {round(amount, 2):<12}")
        mt += amount
    print(f"  {'='*80}")
    print(f"  Ministry Total: {mt:.2f}\n")


if __name__ == "__main__":

    MINISTRY_LABELS = {
        'Poverty':     'POVERTY',
        'Inequality':  'INEQUALITY',
        'Empowerment': 'EMPOWERMENT',
        'Food':        'FOOD & AGRICULTURE',
        'Energy':      'ENERGY',
    }

    bud, tot, bud_pct, results = get_tab('NQU-240', 1, 'af')

    print("\n=== DETAILED BUDGET BREAKDOWN ===\n")
    for m, label in MINISTRY_LABELS.items():
        print_ministry(label, results[m])

    print(f"\n  Region Total: {tot:.2f}")
    print(f"  From a budget of: {bud['bud']:.2f}")
    print(f"\n  Investment Proposals are {bud_pct:.1f} % of the budget")