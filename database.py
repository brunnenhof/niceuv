"""
Database schema and operations for SDG3 game
Phase 1 Update: Correct regions, policies, plot variables, AI support
"""
import sqlite3
import datetime
from contextlib import contextmanager
from typing import Optional, Dict, List, Tuple
import random
import string
from pathlib import Path
from files import luf_original
from nicegui import app

DB_PATH = str(Path(__file__).parent / "sdg3_game.db")

# Start code for game creation
START_CODE = "oscar"

REGION_ABBR = ['us', 'af', 'cn', 'me', 'sa', 'la', 'pa', 'ec', 'eu', 'se']

MINISTRIES = ["Poverty", "Inequality", "Empowerment", "Food", "Energy", "Future"]


@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# In database.py - add functions to save/load preferences

def save_player_preferences(username, lang, langx):
    """Save user language preferences (UPSERT-safe)."""
    with get_db() as conn:
        conn.execute(
            "UPDATE players SET lang = ?, langx = ? WHERE username = ?",
            (lang, langx, username)
        )
        conn.commit()


def upsert_player_lang(game_id: str, username: str, region_tag: str,
                       ministry: str, lang: str, dark: int = 0):
    """Create or update the players row with correct lang/mode — called at join time."""
    langx = 0
    _map = {"en": 0, "de": 1, "de2": 2, "fr": 3, "no": 4}
    langx = _map.get(lang, 0)
    mode = "dark" if dark else "normal"
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO players (game_id, username, region_tag, ministry, lang, langx, mode)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                lang  = excluded.lang,
                langx = excluded.langx,
                mode  = excluded.mode
            """,
            (game_id, username, region_tag, ministry, lang, langx, mode)
        )
        conn.commit()


def has_player_decisions(game_id: str, round_num: int,
                         region_tag: str, ministry: str) -> bool:
    """True if the minister has saved any slider decisions for this round."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT 1 FROM policy_decisions "
            "WHERE game_id=? AND round=? AND region_tag=? AND ministry=? LIMIT 1",
            (game_id, round_num, region_tag, ministry)
        ).fetchone()
    return row is not None


def get_players_advanced(game_id: str, round_num: int) -> set:
    """Usernames of players who have opened their dashboard for round_num."""
    field = f"is_logged_in_round{round_num}"
    with get_db() as conn:
        rows = conn.execute(
            f"SELECT username FROM players WHERE game_id=? AND {field}=1",
            (game_id,)
        ).fetchall()
    return {r["username"] for r in rows}


def get_player_preferences(username):
    """Load user preferences"""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT lang, langx, mode 
            FROM players 
            WHERE username = ?
        """, (username,))
        row = cursor.fetchone()
        if row:
            return {
                'lang': row['lang'],
                'langx': row['langx'],
                'mode': row['mode']
            }
    return None


def generate_game_id() -> str:
    """
    Generate a simple game ID: 3 uppercase letters + dash + 3 digits
    Example: ADJ-932
    """
    letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    digits = ''.join(random.choices(string.digits, k=3))
    return f"{letters}-{digits}"


def create_unique_game_id() -> str:
    """Generate a unique game_id (check database for uniqueness)"""
    with get_db() as conn:
        while True:
            game_id = generate_game_id()
            cursor = conn.execute("SELECT game_id FROM games WHERE game_id = ?", (game_id,))
            if not cursor.fetchone():
                return game_id


def init_database():
    """Initialize database schema"""
    with get_db() as conn:
        # Games table - always 3 rounds, added accept_decisions
        conn.execute("""
            CREATE TABLE IF NOT EXISTS games (
                game_id TEXT PRIMARY KEY,
                gm_username TEXT NOT NULL,
                num_rounds INTEGER DEFAULT 3,
                current_round INTEGER DEFAULT 0,
                state TEXT DEFAULT 'setup',
                accept_decisions BOOLEAN DEFAULT 0,
                lang TEXT DEFAULT 'en',
                langx INTEGER DEFAULT 0,
                mode TEXT DEFAULT 'normal',
                state_x INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # AI regions table - track which regions are AI-controlled
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ai_regions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id TEXT NOT NULL,
                region_tag TEXT NOT NULL,
                FOREIGN KEY (game_id) REFERENCES games(game_id),
                UNIQUE(game_id, region_tag)
            )
        """)
        
        # Players table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS players (
                player_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                game_id TEXT NOT NULL,
                region_tag TEXT NOT NULL,
                ministry TEXT NOT NULL,
                is_ai BOOLEAN DEFAULT 0,
                is_logged_in_round1 BOOLEAN DEFAULT 0,
                is_logged_in_round2 BOOLEAN DEFAULT 0,
                is_logged_in_round3 BOOLEAN DEFAULT 0,
                lang TEXT DEFAULT 'en',
                langx INTEGER DEFAULT 0,
                mode TEXT DEFAULT 'normal',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (game_id) REFERENCES games(game_id)
            )
        """)
        # Migrate: add lang/langx/mode to existing players tables
        _pcols = {r[1] for r in conn.execute("PRAGMA table_info(players)").fetchall()}
        for _col, _dflt in [("lang", "'en'"), ("langx", "0"), ("mode", "'normal'")]:
            if _col not in _pcols:
                conn.execute(f"ALTER TABLE players ADD COLUMN {_col} TEXT DEFAULT {_dflt}")

        # Create index on username for fast lookups
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_players_username
            ON players(username)
        """)
        
        # Policies table - loaded from JSON with full structure
        conn.execute("""
            CREATE TABLE IF NOT EXISTS policies (
                pol_id INTEGER PRIMARY KEY,
                pol_tag TEXT NOT NULL UNIQUE,
                pol_name TEXT NOT NULL,
                pol_min REAL NOT NULL,
                pol_max REAL NOT NULL,
                pol_ministry TEXT NOT NULL,
                pol_ministry_tag TEXT NOT NULL
            )
        """)
        
        # Policy explanations table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS policy_explanations (
                pol_tag TEXT PRIMARY KEY,
                explanation TEXT NOT NULL,
                FOREIGN KEY (pol_tag) REFERENCES policies(pol_tag)
            )
        """)
        
        # Policy decisions table - changed to region_tag
        conn.execute("""
            CREATE TABLE IF NOT EXISTS policy_decisions (
                decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id TEXT NOT NULL,
                round INTEGER NOT NULL,
                region_tag TEXT NOT NULL,
                ministry TEXT NOT NULL,
                pol_id INTEGER NOT NULL,
                value REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (game_id) REFERENCES games(game_id),
                FOREIGN KEY (pol_id) REFERENCES policies(pol_id),
                UNIQUE(game_id, round, region_tag, ministry, pol_id)
            )
        """)
        
        # Plot variables table - loaded from JSON with full structure
        conn.execute("""
            CREATE TABLE IF NOT EXISTS plot_variables (
                pv_id INTEGER PRIMARY KEY,
                pv_sdg_nbr INTEGER,
                pv_indicator TEXT NOT NULL,
                pv_vensim_name TEXT NOT NULL,
                pv_green REAL,
                pv_red REAL,
                pv_lowerbetter INTEGER,
                pv_ymin REAL,
                pv_ymax REAL,
                pv_subtitle TEXT,
                pv_ministry TEXT NOT NULL,
                pv_pct INTEGER,
                pv_sdg TEXT
            )
        """)
        
        # Plot results table - changed to region_tag
        conn.execute("""
            CREATE TABLE IF NOT EXISTS plot_results (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id TEXT NOT NULL,
                round INTEGER NOT NULL,
                region_tag TEXT NOT NULL,
                pv_id INTEGER NOT NULL,
                value REAL NOT NULL,
                FOREIGN KEY (game_id) REFERENCES games(game_id),
                FOREIGN KEY (pv_id) REFERENCES plot_variables(pv_id),
                UNIQUE(game_id, round, region_tag, pv_id)
            )
        """)
        
        # Region submissions table - one row per (game, round, region) when Future submits
        conn.execute("""
            CREATE TABLE IF NOT EXISTS region_submissions (
                game_id TEXT NOT NULL,
                round_num INTEGER NOT NULL,
                region_tag TEXT NOT NULL,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (game_id, round_num, region_tag),
                FOREIGN KEY (game_id) REFERENCES games(game_id)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS human_regions (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id    TEXT NOT NULL,
                region_tag TEXT NOT NULL,
                sub_1      INTEGER DEFAULT 0,
                sub_2      INTEGER DEFAULT 0,
                sub_3      INTEGER DEFAULT 0
            )
        """)

        # Sessions table - token-based identity, one row per active browser session
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                token      TEXT PRIMARY KEY,
                username   TEXT,
                game_id    TEXT,
                role       TEXT,
                ministry   TEXT,
                region_tag TEXT,
                lang       TEXT    DEFAULT 'en',
                dark       INTEGER DEFAULT 0,
                last_page  TEXT    DEFAULT '/'
            )
        """)

        conn.commit()


def get_session(token: str) -> dict | None:
    if not token:
        return None
    with get_db() as conn:
        row = conn.execute(
            'SELECT * FROM sessions WHERE token = ?', (token,)
        ).fetchone()
        return dict(row) if row else None


def create_session(token: str, username: str, game_id: str, role: str,
                   ministry: str, region_tag: str, lang: str, dark: int):
    with get_db() as conn:
        conn.execute('''
            INSERT OR REPLACE INTO sessions
            (token, username, game_id, role, ministry, region_tag, lang, dark)
            VALUES (?,?,?,?,?,?,?,?)
        ''', (token, username, game_id, role, ministry, region_tag, lang, dark))
        conn.commit()


def update_session(token: str, **kwargs):
    if not kwargs:
        return
    cols = ', '.join(f'{k} = ?' for k in kwargs)
    with get_db() as conn:
        conn.execute(
            f'UPDATE sessions SET {cols} WHERE token = ?',
            (*kwargs.values(), token)
        )
        conn.commit()


def delete_session(token: str):
    with get_db() as conn:
        conn.execute('DELETE FROM sessions WHERE token = ?', (token,))
        conn.commit()

def get_list_that_should_be_logged_in(game_id):
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT game_id, ministry, region_tag
            FROM players 
            WHERE game_id = ?
            AND is_ai = ?
            ORDER BY region_tag DESC
            """,
            (game_id, False)
        )
        rows = cursor.fetchall()
        if rows:
            return rows
        return None
    pass


def get_all_logged_in(game_id, runde):
    field = f"is_logged_in_round{runde}"
    with get_db() as conn:
        cursor = conn.execute(
            f"""
            SELECT game_id, ministry, region_tag
            FROM players 
            WHERE game_id = ? AND {field} = 1
            AND is_ai = ?
            ORDER BY region_tag DESC
            """,
            (game_id, False)
        )
        rows = cursor.fetchall()
        if rows:
            return rows
        return None
    pass

def get_accept_decisions(game_id: str, runde: int, region_tag: str = None):
    """Check if submissions are allowed for a round.
    If region_tag given, check that specific region; otherwise check any human region."""
    field = f"sub_{runde}"
    with get_db() as conn:
        if region_tag:
            cursor = conn.execute(
                f"SELECT {field} FROM human_regions WHERE game_id = ? AND region_tag = ?",
                (game_id, region_tag)
            )
        else:
            cursor = conn.execute(
                f"SELECT {field} FROM human_regions WHERE game_id = ? LIMIT 1",
                (game_id,)
            )
        row = cursor.fetchone()
        if row:
            return row[0]
        return 0


def set_accept_decisions(game_id: str, runde: int, value: int):
    """Set submissions allowed/denied for ALL human regions for this round."""
    field = f"sub_{runde}"
    print('set_accept_decisions ' + game_id + ' ' + str(runde) + ' ' + str(value))
    with get_db() as conn:
        conn.execute(
            f"UPDATE human_regions SET {field} = ? WHERE game_id = ?",
            (value, game_id)
        )
        conn.commit()


def load_policies_data():
    """Load 32 policies and explanations from JSON data"""
    policies_json = [{"pol_id":1,"pol_tag":"ExPS","pol_name":"Expand policy space","pol_min":0.0,"pol_max":100.0,"pol_ministry":"Poverty","pol_ministry_tag":"pov"},{"pol_id":2,"pol_tag":"LPB","pol_name":"Lending from public bodies (LPB)","pol_min":0.0,"pol_max":30.0,"pol_ministry":"Poverty","pol_ministry_tag":"pov"},{"pol_id":3,"pol_tag":"LPBsplit","pol_name":"LPB: Split the use of funds from public lenders","pol_min":0.0,"pol_max":100.0,"pol_ministry":"Poverty","pol_ministry_tag":"pov"},{"pol_id":4,"pol_tag":"LPBgrant","pol_name":"LPB: funds given as loans or grants","pol_min":0.0,"pol_max":100.0,"pol_ministry":"Poverty","pol_ministry_tag":"pov"},{"pol_id":5,"pol_tag":"FMPLDD","pol_name":"Fraction of credit with private lenders NOT drawn down per y","pol_min":0.0,"pol_max":90.0,"pol_ministry":"Poverty","pol_ministry_tag":"pov"},{"pol_id":6,"pol_tag":"TOW","pol_name":"Taxing Owners Wealth","pol_min":0.0,"pol_max":80.0,"pol_ministry":"Poverty","pol_ministry_tag":"pov"},{"pol_id":7,"pol_tag":"FPGDC","pol_name":"Cancel debt from public lenders","pol_min":0.0,"pol_max":100.0,"pol_ministry":"Poverty","pol_ministry_tag":"pov"},{"pol_id":8,"pol_tag":"Lfrac","pol_name":"Leakage fraction reduction","pol_min":0.0,"pol_max":100.0,"pol_ministry":"Poverty","pol_ministry_tag":"pov"},{"pol_id":9,"pol_tag":"SSGDR","pol_name":"Stretch repayment","pol_min":1.0,"pol_max":5.0,"pol_ministry":"Poverty","pol_ministry_tag":"pov"},{"pol_id":10,"pol_tag":"XtaxFrac","pol_name":"Extra taxes paid by the super rich","pol_min":50.0,"pol_max":90.0,"pol_ministry":"Inequality","pol_ministry_tag":"ineq"},{"pol_id":11,"pol_tag":"StrUP","pol_name":"Strengthen Unions","pol_min":0.0,"pol_max":3.0,"pol_ministry":"Inequality","pol_ministry_tag":"ineq"},{"pol_id":12,"pol_tag":"Wreaction","pol_name":"Worker reaction","pol_min":0.0,"pol_max":3.0,"pol_ministry":"Inequality","pol_ministry_tag":"ineq"},{"pol_id":13,"pol_tag":"XtaxCom","pol_name":"Introduce a Universal basic dividend","pol_min":0.0,"pol_max":5.0,"pol_ministry":"Inequality","pol_ministry_tag":"ineq"},{"pol_id":14,"pol_tag":"ICTR","pol_name":"Increase consumption tax rate","pol_min":0.0,"pol_max":10.0,"pol_ministry":"Inequality","pol_ministry_tag":"ineq"},{"pol_id":15,"pol_tag":"IOITR","pol_name":"Increase owner income tax rate","pol_min":0.0,"pol_max":10.0,"pol_ministry":"Inequality","pol_ministry_tag":"ineq"},{"pol_id":16,"pol_tag":"IWITR","pol_name":"Increase worker income tax rate","pol_min":0.0,"pol_max":10.0,"pol_ministry":"Inequality","pol_ministry_tag":"ineq"},{"pol_id":17,"pol_tag":"Ctax","pol_name":"Introduce a Carbon tax","pol_min":0.0,"pol_max":100.0,"pol_ministry":"Inequality","pol_ministry_tag":"ineq"},{"pol_id":18,"pol_tag":"SGRPI","pol_name":"Shift govt spending to investment","pol_min":0.0,"pol_max":50.0,"pol_ministry":"Inequality","pol_ministry_tag":"ineq"},{"pol_id":19,"pol_tag":"FEHC","pol_name":"Education to all","pol_min":0.0,"pol_max":10.0,"pol_ministry":"Empowerment","pol_ministry_tag":"emp"},{"pol_id":20,"pol_tag":"XtaxRateEmp","pol_name":"Female leadership","pol_min":0.0,"pol_max":5.0,"pol_ministry":"Empowerment","pol_ministry_tag":"emp"},{"pol_id":21,"pol_tag":"SGMP","pol_name":"Pensions to all","pol_min":0.0,"pol_max":10.0,"pol_ministry":"Empowerment","pol_ministry_tag":"emp"},{"pol_id":22,"pol_tag":"FWRP","pol_name":"Food waste reduction","pol_min":0.0,"pol_max":90.0,"pol_ministry":"Food","pol_ministry_tag":"food"},{"pol_id":23,"pol_tag":"FLWR","pol_name":"Regenerative agriculture","pol_min":0.0,"pol_max":95.0,"pol_ministry":"Food","pol_ministry_tag":"food"},{"pol_id":24,"pol_tag":"RMDR","pol_name":"Change diets","pol_min":0.0,"pol_max":95.0,"pol_ministry":"Food","pol_ministry_tag":"food"},{"pol_id":25,"pol_tag":"RIPLGF","pol_name":"Reduce food imports","pol_min":0.0,"pol_max":50.0,"pol_ministry":"Food","pol_ministry_tag":"food"},{"pol_id":26,"pol_tag":"FC","pol_name":"Max forest cutting","pol_min":0.0,"pol_max":90.0,"pol_ministry":"Food","pol_ministry_tag":"food"},{"pol_id":27,"pol_tag":"REFOREST","pol_name":"Reforestation","pol_min":0.0,"pol_max":3.0,"pol_ministry":"Food","pol_ministry_tag":"food"},{"pol_id":28,"pol_tag":"FTPEE","pol_name":"Energy system efficiency","pol_min":1.0,"pol_max":2.5,"pol_ministry":"Energy","pol_ministry_tag":"ener"},{"pol_id":29,"pol_tag":"NEP","pol_name":"Electrify everything","pol_min":0.0,"pol_max":95.0,"pol_ministry":"Energy","pol_ministry_tag":"ener"},{"pol_id":30,"pol_tag":"ISPV","pol_name":"Invest in Renewables","pol_min":50.0,"pol_max":95.0,"pol_ministry":"Energy","pol_ministry_tag":"ener"},{"pol_id":31,"pol_tag":"CCS","pol_name":"CCS: Carbon capture and storage at source","pol_min":0.0,"pol_max":80.0,"pol_ministry":"Energy","pol_ministry_tag":"ener"},{"pol_id":32,"pol_tag":"DAC","pol_name":"Direct air capture","pol_min":0.0,"pol_max":1.5,"pol_ministry":"Energy","pol_ministry_tag":"ener"}]
    
    explanations_json = [{"pol_tag":"CCS","explanation":"Percent of fossil use to be equipped with carbon capture and storage (CCS) at source.  This means that you still emit CO2 but it does not get to the atmosphere, where it causes warming,  because you capture it and store it underground."},{"pol_tag":"TOW","explanation":"0 means no wealth tax,  80 means 80% of accrued owners wealth is taxed away each year,  50: half of it"},{"pol_tag":"FPGDC","explanation":"Cancels a percentage of Govt debt outstanding to public lenders. 0 means nothing is cancelled,  100 all is cancelled,  50 half is cancelled --- in the policy start year"},{"pol_tag":"RMDR","explanation":"Change in diet, esp. a reduction in red meat consumption. 0 means red meat is consumed as before, 50 means 50% is replaced with lab meat, 100 means 100% is replaced with lab meat  i.e. no more red meat is 'produced' by intensive livestock farming  aka factory farming."},{"pol_tag":"REFOREST","explanation":"Policy to reforest land, i.e. plant new trees. 0 means no reforestation, 1 means you increase the forest area by 1‰ / yr (that is 1 promille), 3 = you increase the forest area by 3‰ / yr"},{"pol_tag":"FTPEE","explanation":"Annual percentage increase in energy efficiency; 1% per yr is the historical value over the last 40 years. Beware of the power of compound interest!"},{"pol_tag":"LPBsplit","explanation":"0 means all LBP funding goes to consumption (eg child support,  subsidies for food or energy,  etc.)  100 means all goes to public investment like infrastructure,  security,  etc. NOTE This only has an effect if LPB is NOT set to zero"},{"pol_tag":"ExPS","explanation":"Cancels a percentage of Govt debt outstanding to private lenders --- in the policy start year"},{"pol_tag":"FMPLDD","explanation":"Given your credit worthiness  you have an amount you you can borrow from private lenders. Here you choose the fraction of credit you actually draw down each year."},{"pol_tag":"StrUP","explanation":"In any economy, the national income is shared between owners and workers. This policy changes the share going to workers. 1 multiplies the share with 1%,  2 with 2%,  etc "},{"pol_tag":"Wreaction","explanation":"In any economy, there is a power struggle between workers and owners about the share of national income each gets. This policy strenghtens the workers negotiation position. 1 by 1%,  2 by 2%,  etc. "},{"pol_tag":"SGMP","explanation":"To fight poverty in old age  you can introduce pensions for all. The size of the pension is expressed as the percent of the GDP you want to invest. 0 means you invest nothing and leave things as they are. 5 means you invest 5 % of GDP; 10 = 10 % of GDP  money is transferred to workers and paid for by owners"},{"pol_tag":"FWRP","explanation":"Here you decide how much the percentage of 'normal' waste, which is 30%, is to be reduced. I.e. 100 means  no more waste! 50 means waste is reduced by 50 %,  0 means waste continues as always"},{"pol_tag":"ICTR","explanation":"This policy is an increase in the consumption tax (aka sales tax, value added tax (VAT),  etc. 0 means no increase, 10 means an increase by 10 percentage points, 5 by 5 percentage points; the money raised goes to general govt revenue."},{"pol_tag":"XtaxCom","explanation":"A universal basic dividend is created when a state taxes common goods  like fishing rights, mining rights, the right to use airwaves  etc. This policy sets this tax as a percent of GDP  i.e.  0 = 0 % of GDP  i.e. nothing; 5 = 5 % of GDP; 3 = 3 % of GDP  money is transferred to general govt tax revenue."},{"pol_tag":"Lfrac","explanation":"Leakage describes the use of money for illicit purposes: Corruption,  bribery,  etc. The normal leakage is 20%  - so a value of 0 reduction means that those 20% do in fact disappear - a 50 % reduction means 10% disappear and 100% reduction means nothing disappears and everyone in your region is totally honest!"},{"pol_tag":"IOITR","explanation":"This is an increase in the income tax paid by owners. 0 means no increase,  10 means an increase by 10 percentage points, 5 by 5 percentage points; the money raised goes to general govt revenue."},{"pol_tag":"IWITR","explanation":"This is an increase in the income tax paid by workers. 0 means no increase, 10 means an increase by 10 percentage points, 5 by 5 percentage points; the money raised goes to general govt revenue."},{"pol_tag":"SGRPI","explanation":"Governments choose how to use their spending: primarily for consumption (eg child support, subsidies for food or energy, etc.) or for public investment (education, health care, infrastructure  etc.) This policy shifts spending from consumption to investment. 0 means no shift, 10= 10% of consumption shifted to investment, 25 = 25 % of consumption shifted to investment, etc"},{"pol_tag":"FEHC","explanation":"The higher the level of education  esp. of women,  in a society,  the lower the birth rate. Thus  education for all lowers the birth rate. By how much? You make an educated guess: 0 means no effect, 10 means a 10% reduction, 5 means a 5% reduction, etc."},{"pol_tag":"XtaxRateEmp","explanation":"To support women to reach equality costs some money, esp. to close the pay gender gap. How much do you want to spend  as a pct of GDP? 0 means you spend nothing and leave things as they are; 5 means you spend= 5 % of GDP; 3 = 3 % of GDP. Money is transferred to general govt tax revenue"},{"pol_tag":"FLWR","explanation":"Here you decide the percentage of your cropland that is worked regeneratively (low or no tillage,  low or no fertilizers and pesticides  etc.)  50 means 50 % cropland worked is regeneratively, 100 = 100 % of cropland is worked regeneratively, etc. 0 leaves things as they are."},{"pol_tag":"RIPLGF","explanation":"Reduction in food imports. 0 means no reduction,  10=10% reduction, 50=50% reduction This policy reduces food available from elsewhere but strenghtens local producers"},{"pol_tag":"FC","explanation":"Policy to limit forest cutting. 0 means no limitation on cutting,  10=10% reduction in the maximum amount that can be cut,  50=50% reduction in max cut, etc. all the way to 90 % reduction which is practically a ban on cutting"},{"pol_tag":"NEP","explanation":"Percent of fossil fuel (oil, gas, and coal) *not* used for electricity generation (mobility,  heating,  industrial use  etc.) that you want to electrify."},{"pol_tag":"Ctax","explanation":"This is the carbon emission tax. 0 means no carbon tax,  25 = 25 $/ton of CO2 emitted  etc."},{"pol_tag":"DAC","explanation":"Capturing CO2 that is already in the atmosphere and storing it underground   - in GtCO2/yr (Giga tons -  giga is 10^9); In 2020  regional emissions were roughly: USA 5,  Africa  south of Sahara 1,  China 12,  the rest all between 2 and 3 GtCO2/yr. You can capture more than you emit."},{"pol_tag":"XtaxFrac","explanation":"The percentage of *extra* taxes paid by owners (owners pay 50% of extra taxes even under TLTL)  I.e. 90 means owners pay 90 % of extra taxes,  70 means owners pay 70 % of extra taxes, etc. Extra taxes are those for empowerment and to give women equal pay."},{"pol_tag":"LPBgrant","explanation":"0 means all LPB funding is given as loans that must be repaid,  100 means all is given as grants that carry no interest and must not be repaid. NOTE This only has an effect if LPB is NOT set to zero"},{"pol_tag":"LPB","explanation":"The percentage of your GDP made available as financing from public bodies (WorldBank,  IMF,  off-balance funding) LPB= Lending from Public Bodies"},{"pol_tag":"SSGDR","explanation":"You can stretch repayment into the future  so that each year you pay less,  but you do have to pay for a longer time. 1 means no stretching - 2 doubles repayment time  - 3 trebles repayment time - and so on"},{"pol_tag":"ISPV","explanation":"Percent of electricity generation from renewable sources (40% is what we managed to achieve in the past)"}]
    
    with get_db() as conn:
        # Check if already loaded
        cursor = conn.execute("SELECT COUNT(*) as count FROM policies")
        if cursor.fetchone()['count'] > 0:
            return  # Already loaded
        
        # Insert policies
        for policy in policies_json:
            conn.execute("""
                INSERT INTO policies (pol_id, pol_tag, pol_name, pol_min, pol_max, pol_ministry, pol_ministry_tag)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (policy['pol_id'], policy['pol_tag'], policy['pol_name'], policy['pol_min'], 
                  policy['pol_max'], policy['pol_ministry'], policy['pol_ministry_tag']))
        
        # Insert explanations
        for exp in explanations_json:
            conn.execute("""
                INSERT INTO policy_explanations (pol_tag, explanation)
                VALUES (?, ?)
            """, (exp['pol_tag'], exp['explanation']))
        
        conn.commit()


def load_plot_variables_data():
    """Load 48 plot variables from JSON data"""
    plot_vars_json = [{"pv_id":1,"pv_sdg_nbr":1,"pv_indicator":"Poverty rate","pv_vensim_name":"Fraction of population below existential minimum","pv_green":5.0,"pv_red":13.0,"pv_lowerbetter":1,"pv_ymin":0.0,"pv_ymax":65.0,"pv_subtitle":"Fraction of population living below $6.85 per day (%)","pv_ministry":"Poverty","pv_pct":100,"pv_sdg":"No poverty"},{"pv_id":2,"pv_sdg_nbr":2,"pv_indicator":"Undernourished fraction","pv_vensim_name":"Fraction of population undernourished","pv_green":3.0,"pv_red":7.0,"pv_lowerbetter":1,"pv_ymin":0.0,"pv_ymax":30.0,"pv_subtitle":"Fraction of population undernourished (%)","pv_ministry":"Poverty","pv_pct":100,"pv_sdg":"No hunger"},{"pv_id":3,"pv_sdg_nbr":2,"pv_indicator":"Regenerative agriculture","pv_vensim_name":"Regenerative cropland fraction","pv_green":70.0,"pv_red":30.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":100.0,"pv_subtitle":"Proportion of agricultural area worked regeneratively (%)","pv_ministry":"Food","pv_pct":100,"pv_sdg":"No hunger"},{"pv_id":4,"pv_sdg_nbr":3,"pv_indicator":"Average wellbeing index","pv_vensim_name":"Average wellbeing index","pv_green":1.8,"pv_red":1.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":3.0,"pv_subtitle":"Average wellbeing index","pv_ministry":"Future","pv_pct":1,"pv_sdg":"Good health and wellbeing"},{"pv_id":5,"pv_sdg_nbr":3,"pv_indicator":"Life expectancy","pv_vensim_name":"Life expectancy at birth","pv_green":80.0,"pv_red":60.0,"pv_lowerbetter":0,"pv_ymin":30.0,"pv_ymax":110.0,"pv_subtitle":"Life expectancy (years)","pv_ministry":"Inequality","pv_pct":1,"pv_sdg":"Good health and wellbeing"},{"pv_id":6,"pv_sdg_nbr":4,"pv_indicator":"Years in school","pv_vensim_name":"Years of schooling","pv_green":15.0,"pv_red":13.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":18.0,"pv_subtitle":"Years in school","pv_ministry":"Empowerment","pv_pct":1,"pv_sdg":"Quality education"},{"pv_id":7,"pv_sdg_nbr":5,"pv_indicator":"Female labor income share","pv_vensim_name":"GenderEquality","pv_green":48.0,"pv_red":40.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":60.0,"pv_subtitle":"Female pre-tax labor income share (%)","pv_ministry":"Empowerment","pv_pct":100,"pv_sdg":"Gender equality"},{"pv_id":8,"pv_sdg_nbr":6,"pv_indicator":"Safe water access","pv_vensim_name":"Safe water","pv_green":95.0,"pv_red":80.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":100.0,"pv_subtitle":"Fraction of population with access to safe water (%)","pv_ministry":"Poverty","pv_pct":100,"pv_sdg":"Access to clean water"},{"pv_id":9,"pv_sdg_nbr":6,"pv_indicator":"Safe sanitation access","pv_vensim_name":"Safe sanitation","pv_green":90.0,"pv_red":65.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":100.0,"pv_subtitle":"Fraction of population with access to safe sanitation (%)","pv_ministry":"Poverty","pv_pct":100,"pv_sdg":"Access to clean sanitation"},{"pv_id":10,"pv_sdg_nbr":7,"pv_indicator":"Electricity access","pv_vensim_name":"Access to electricity","pv_green":98.0,"pv_red":90.0,"pv_lowerbetter":0,"pv_ymin":10.0,"pv_ymax":100.0,"pv_subtitle":"Fraction of population with access to electricity (%)","pv_ministry":"Empowerment","pv_pct":100,"pv_sdg":"Affordable and clean energy"},{"pv_id":11,"pv_sdg_nbr":7,"pv_indicator":"Renewable energy share","pv_vensim_name":"Renewable energy share in the total final energy consumption","pv_green":80.0,"pv_red":50.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":100.0,"pv_subtitle":"Wind and PV energy share in total energy consumption (%)","pv_ministry":"Energy","pv_pct":100,"pv_sdg":"Affordable and clean energy"},{"pv_id":12,"pv_sdg_nbr":7,"pv_indicator":"Energy intensity","pv_vensim_name":"Total energy use per GDP","pv_green":0.1,"pv_red":0.5,"pv_lowerbetter":1,"pv_ymin":0.0,"pv_ymax":2.0,"pv_subtitle":"Energy intensity in terms of primary energy and GDP (kWh/$)","pv_ministry":"Energy","pv_pct":1,"pv_sdg":"Affordable and clean energy"},{"pv_id":13,"pv_sdg_nbr":8,"pv_indicator":"Worker disposable income","pv_vensim_name":"Disposable income pp post tax pre loan impact","pv_green":25.0,"pv_red":15.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":50.0,"pv_subtitle":"Worker disposable income (1000 $/person-year)","pv_ministry":"Inequality","pv_pct":1,"pv_sdg":"Decent work and economic growth"},{"pv_id":16,"pv_sdg_nbr":8,"pv_indicator":"GDP growth rate","pv_vensim_name":"Smoothed RoC in GDPpp","pv_green":4.0,"pv_red":2.0,"pv_lowerbetter":0,"pv_ymin":-5.0,"pv_ymax":10.0,"pv_subtitle":"Growth rate of GDP per capita (%/yr)","pv_ministry":"Poverty","pv_pct":100,"pv_sdg":"Decent work and economic growth"},{"pv_id":17,"pv_sdg_nbr":11,"pv_indicator":"Emissions per person","pv_vensim_name":"Energy footprint pp","pv_green":0.5,"pv_red":2.0,"pv_lowerbetter":1,"pv_ymin":0.0,"pv_ymax":15.0,"pv_subtitle":"Emissions per person (tCO2/p/y)","pv_ministry":"Energy","pv_pct":1,"pv_sdg":"Sustainable cities and communities"},{"pv_id":19,"pv_sdg_nbr":13,"pv_indicator":"Temperature rise","pv_vensim_name":"Temp surface anomaly compared to 1850 degC","pv_green":1.0,"pv_red":1.5,"pv_lowerbetter":1,"pv_ymin":0.0,"pv_ymax":3.0,"pv_subtitle":"Temperature rise (deg C above 1850)","pv_ministry":"Future","pv_pct":1,"pv_sdg":"Climate action"},{"pv_id":20,"pv_sdg_nbr":13,"pv_indicator":"Total GHG emissions","pv_vensim_name":"Total CO2 emissions","pv_green":1.0,"pv_red":5.0,"pv_lowerbetter":1,"pv_ymin":0.0,"pv_ymax":15.0,"pv_subtitle":"Total greenhouse gas emissions per year (GtCO2/yr)","pv_ministry":"Energy","pv_pct":1,"pv_sdg":"Climate action"},{"pv_id":21,"pv_sdg_nbr":14,"pv_indicator":"Ocean pH","pv_vensim_name":"pH in surface","pv_green":8.15,"pv_red":8.1,"pv_lowerbetter":0,"pv_ymin":8.0,"pv_ymax":8.2,"pv_subtitle":"Ocean surface pH","pv_ministry":"Future","pv_pct":1,"pv_sdg":"Life below water"},{"pv_id":23,"pv_sdg_nbr":16,"pv_indicator":"Public services","pv_vensim_name":"Public services pp","pv_green":15.0,"pv_red":8.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":25.0,"pv_subtitle":"Public services per person (1000 $/person-yr)","pv_ministry":"Inequality","pv_pct":1,"pv_sdg":"Peace justice and strong institutions"},{"pv_id":24,"pv_sdg_nbr":17,"pv_indicator":"Trust in institutions","pv_vensim_name":"Social trust","pv_green":1.5,"pv_red":1.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":3.0,"pv_subtitle":"Trust in institutions (1980=1)","pv_ministry":"Empowerment","pv_pct":1,"pv_sdg":"Partnership for the Goals"},{"pv_id":25,"pv_sdg_nbr":17,"pv_indicator":"Govt revenue share","pv_vensim_name":"Total government revenue as a proportion of GDP","pv_green":45.0,"pv_red":30.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":60.0,"pv_subtitle":"Total government revenue as a proportion of GDP (%)","pv_ministry":"Inequality","pv_pct":100,"pv_sdg":"Partnership for the Goals"},{"pv_id":26,"pv_sdg_nbr":0,"pv_indicator":"Population","pv_vensim_name":"Population","pv_green":1000.0,"pv_red":1500.0,"pv_lowerbetter":1,"pv_ymin":0.0,"pv_ymax":2000.0,"pv_subtitle":"Population (million people)","pv_ministry":"Future","pv_pct":1,"pv_sdg":"Total population"},{"pv_id":27,"pv_sdg_nbr":10,"pv_indicator":"Labour share of GDP","pv_vensim_name":"Labour share of GDP","pv_green":60.0,"pv_red":50.0,"pv_lowerbetter":0,"pv_ymin":40.0,"pv_ymax":70.0,"pv_subtitle":"Labour share of GDP (%)","pv_ministry":"Inequality","pv_pct":100,"pv_sdg":"Reduced inequalities"},{"pv_id":29,"pv_sdg_nbr":18,"pv_indicator":"Number of SDGs met","pv_vensim_name":"All SDG Scores","pv_green":16.0,"pv_red":14.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":17.0,"pv_subtitle":"Number of SDGs met - 17 can be met","pv_ministry":"Future","pv_pct":1,"pv_sdg":"SDG scores"},{"pv_id":30,"pv_sdg_nbr":9,"pv_indicator":"Investment share","pv_vensim_name":"Local private and govt investment share","pv_green":40.0,"pv_red":30.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":60.0,"pv_subtitle":"Private and govt investment share (% of GDP)","pv_ministry":"Poverty","pv_pct":100,"pv_sdg":"Industry innovation and infrastructure"},{"pv_id":31,"pv_sdg_nbr":11,"pv_indicator":"City area change","pv_vensim_name":"RoC Populated land","pv_green":0.0,"pv_red":1.0,"pv_lowerbetter":1,"pv_ymin":-3.0,"pv_ymax":5.0,"pv_subtitle":"Annual rate of change in city area (%)","pv_ministry":"Food","pv_pct":100,"pv_sdg":"Sustainable cities and communities"},{"pv_id":32,"pv_sdg_nbr":12,"pv_indicator":"Nitrogen use","pv_vensim_name":"Nitrogen use per ha","pv_green":10.0,"pv_red":20.0,"pv_lowerbetter":1,"pv_ymin":0.0,"pv_ymax":300.0,"pv_subtitle":"Nitrogen use (kg/ha-year)","pv_ministry":"Food","pv_pct":100,"pv_sdg":"Responsible consumption and production"},{"pv_id":33,"pv_sdg_nbr":15,"pv_indicator":"Forest area change","pv_vensim_name":"RoC in Forest land","pv_green":1.5,"pv_red":0.0,"pv_lowerbetter":0,"pv_ymin":-3.0,"pv_ymax":4.0,"pv_subtitle":"Annual change in forest area (%)","pv_ministry":"Food","pv_pct":100,"pv_sdg":"Life on land"},{"pv_id":34,"pv_sdg_nbr":9,"pv_indicator":"Donor investment share","pv_vensim_name":"LPB investment share","pv_green":30.0,"pv_red":25.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":50.0,"pv_subtitle":"Donor and off balance-sheet investment share (% of GDP)","pv_ministry":"Inequality","pv_pct":100,"pv_sdg":"Industry innovation and infrastructure"},{"pv_id":35,"pv_sdg_nbr":0,"pv_indicator":"Planetary boundaries breached","pv_vensim_name":"Planetary risk","pv_green":0.5,"pv_red":2.0,"pv_lowerbetter":1,"pv_ymin":0.0,"pv_ymax":5.0,"pv_subtitle":"Planetary boundaries breached","pv_ministry":"Future","pv_pct":1,"pv_sdg":"Planetary boundaries"},{"pv_id":38,"pv_sdg_nbr":19,"pv_indicator":"Social trust","pv_vensim_name":"Social trust","pv_green":1.0,"pv_red":0.7,"pv_lowerbetter":0,"pv_ymin":0.2,"pv_ymax":2.0,"pv_subtitle":"Social trust (index)","pv_ministry":"Future","pv_pct":1,"pv_sdg":"Social trust"},{"pv_id":39,"pv_sdg_nbr":20,"pv_indicator":"Social tension","pv_vensim_name":"Smoothed Social tension index with trust effect","pv_green":1.0,"pv_red":1.2,"pv_lowerbetter":1,"pv_ymin":0.2,"pv_ymax":2.0,"pv_subtitle":"Smoothed Social tension index with trust effect (index)","pv_ministry":"Future","pv_pct":1,"pv_sdg":"Social tension"},{"pv_id":40,"pv_sdg_nbr":99,"pv_indicator":"Global social trust","pv_vensim_name":"Global_social_trust","pv_green":None,"pv_red":None,"pv_lowerbetter":None,"pv_ymin":None,"pv_ymax":None,"pv_subtitle":"(index)","pv_ministry":"GM","pv_pct":None,"pv_sdg":""},{"pv_id":41,"pv_sdg_nbr":99,"pv_indicator":"Global energy intensity","pv_vensim_name":"Energy_intensity_in_terms_of_GDP","pv_green":None,"pv_red":None,"pv_lowerbetter":None,"pv_ymin":None,"pv_ymax":None,"pv_subtitle":"Energy intensity in terms of primary energy and GDP (kWh/$)","pv_ministry":"GM","pv_pct":None,"pv_sdg":""},{"pv_id":42,"pv_sdg_nbr":99,"pv_indicator":"Global energy footprint","pv_vensim_name":"Global_average_Energy_footprint_pp","pv_green":None,"pv_red":None,"pv_lowerbetter":None,"pv_ymin":None,"pv_ymax":None,"pv_subtitle":"Global average energy footprint per person (toe/person)","pv_ministry":"GM","pv_pct":None,"pv_sdg":""},{"pv_id":43,"pv_sdg_nbr":99,"pv_indicator":"Perceived warming","pv_vensim_name":"Perceived_global_warming","pv_green":None,"pv_red":None,"pv_lowerbetter":None,"pv_ymin":None,"pv_ymax":None,"pv_subtitle":"Perceived global warming (degC over 1850)","pv_ministry":"GM","pv_pct":None,"pv_sdg":""},{"pv_id":44,"pv_sdg_nbr":99,"pv_indicator":"Global wellbeing","pv_vensim_name":"Global_avg_wellbeing","pv_green":None,"pv_red":None,"pv_lowerbetter":None,"pv_ymin":None,"pv_ymax":None,"pv_subtitle":"(index)","pv_ministry":"GM","pv_pct":None,"pv_sdg":""},{"pv_id":45,"pv_sdg_nbr":99,"pv_indicator":"Global inequality","pv_vensim_name":"Global_inequality","pv_green":None,"pv_red":None,"pv_lowerbetter":None,"pv_ymin":None,"pv_ymax":None,"pv_subtitle":"(index)","pv_ministry":"GM","pv_pct":None,"pv_sdg":""},{"pv_id":46,"pv_sdg_nbr":99,"pv_indicator":"Global tension","pv_vensim_name":"Global_social_tension","pv_green":None,"pv_red":None,"pv_lowerbetter":None,"pv_ymin":None,"pv_ymax":None,"pv_subtitle":"(index)","pv_ministry":"GM","pv_pct":None,"pv_sdg":""},{"pv_id":47,"pv_sdg_nbr":99,"pv_indicator":"Population below 15k","pv_vensim_name":"Pop_below_15_kpy","pv_green":None,"pv_red":None,"pv_lowerbetter":None,"pv_ymin":None,"pv_ymax":None,"pv_subtitle":"Population below 15000 $ per year (Million people)","pv_ministry":"GM","pv_pct":None,"pv_sdg":""},{"pv_id":48,"pv_sdg_nbr":99,"pv_indicator":"Global population","pv_vensim_name":"Global_Population","pv_green":None,"pv_red":None,"pv_lowerbetter":None,"pv_ymin":None,"pv_ymax":None,"pv_subtitle":"Global Population (Million people)","pv_ministry":"GM","pv_pct":None,"pv_sdg":""}]
    
    with get_db() as conn:
        # Check if already loaded
        cursor = conn.execute("SELECT COUNT(*) as count FROM plot_variables")
        if cursor.fetchone()['count'] > 0:
            return  # Already loaded
        
        # Insert plot variables
        for pv in plot_vars_json:
            conn.execute("""
                INSERT INTO plot_variables 
                (pv_id, pv_sdg_nbr, pv_indicator, pv_vensim_name, pv_green, pv_red, 
                 pv_lowerbetter, pv_ymin, pv_ymax, pv_subtitle, pv_ministry, pv_pct, pv_sdg)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (pv['pv_id'], pv['pv_sdg_nbr'], pv['pv_indicator'], pv['pv_vensim_name'],
                  pv['pv_green'], pv['pv_red'], pv['pv_lowerbetter'], pv['pv_ymin'],
                  pv['pv_ymax'], pv['pv_subtitle'], pv['pv_ministry'], pv['pv_pct'], pv['pv_sdg']))
        
        conn.commit()


def check_username_available(username: str) -> bool:
    """Check if username is available globally"""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT username FROM players WHERE username = ?",
            (username,)
        )
        return cursor.fetchone() is None


def get_game_by_gm_username(username: str) -> Optional[Dict]:
    """Get game information by GM username"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT game_id, gm_username, num_rounds, current_round, state, 
                   accept_decisions, created_at, updated_at
            FROM games 
            WHERE gm_username = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (username,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def set_ai_regions(game_id: str, region_tags: List[str]):
    """Set which regions are controlled by AI"""
    with get_db() as conn:
        # Clear existing AI regions for this game
        conn.execute("DELETE FROM ai_regions WHERE game_id = ?", (game_id,))
        
        # Insert new AI regions
        for tag in region_tags:
            conn.execute(
                "INSERT INTO ai_regions (game_id, region_tag) VALUES (?, ?)",
                (game_id, tag)
            )
        
        conn.commit()


def get_ai_regions(game_id: str) -> List[str]:
    """Get list of AI-controlled region tags for a game"""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT region_tag FROM ai_regions WHERE game_id = ?",
            (game_id,)
        )
        return [row['region_tag'] for row in cursor.fetchall()]


def get_available_regions_ministries(game_id: str) -> Dict[str, List[str]]:
    """
    Get available (unclaimed) ministries for each region (excluding AI regions)
    Returns dict: {region_tag: [ministry1, ministry2, ...]}
    """
    with get_db() as conn:
        # Get AI regions
        ai_regions = get_ai_regions(game_id)
        
        # Get all claimed positions by human players
        cursor = conn.execute(
            """
            SELECT region_tag, ministry 
            FROM players 
            WHERE game_id = ? AND is_ai = 0
            """,
            (game_id,)
        )
        claimed = {(row['region_tag'], row['ministry']) for row in cursor.fetchall()}
        
        # Build available positions (excluding AI regions)
        available = {}
        for region_tag in luf_original.rt_en.keys():
            if region_tag in ai_regions:
                continue  # Skip AI regions
            
            available_ministries = [
                ministry for ministry in MINISTRIES 
                if (region_tag, ministry) not in claimed
            ]
            if available_ministries:  # Only include regions with available spots
                available[region_tag] = available_ministries
        
        return available


def get_logged(game_id: str, round_num: int) -> Dict[str, List[str]]:
    """
    Get ministries NOT yet logged in for this round, per human region.
    Includes both unclaimed slots and players with is_logged_in_round{N} = 0.
    Returns dict: {region_tag: [ministry1, ministry2, ...]}
    """
    field = f"is_logged_in_round{round_num}"
    with get_db() as conn:
        # Get only the human regions for this game
        cursor = conn.execute(
            "SELECT region_tag FROM human_regions WHERE game_id = ?",
            (game_id,)
        )
        human_regions = [row['region_tag'] for row in cursor.fetchall()]

        # Get players who ARE logged in for this round
        cursor = conn.execute(
            f"""
            SELECT region_tag, ministry
            FROM players
            WHERE game_id = ? AND is_ai = 0 AND {field} = 1
            ORDER BY region_tag, ministry
            """,
            (game_id,)
        )
        logged_in = {(row['region_tag'], row['ministry']) for row in cursor.fetchall()}

        # Build not-yet-logged-in positions for human regions only
        not_logged = {}
        for region_tag in human_regions:
            missing = [
                ministry for ministry in MINISTRIES
                if (region_tag, ministry) not in logged_in
            ]
            if missing:
                not_logged[region_tag] = missing

        return not_logged

def get_logged_for_reg(game_id: str, round_num: int, reg: str) -> list:
    """
    Get available (unclaimed) ministries for each region (excluding AI regions)
    Returns dict: {region_tag: [ministry1, ministry2, ...]}
    """
    field = f"is_logged_in_round{round_num}"
    with get_db() as conn:
        # Get AI regions
        #ai_regions = get_ai_regions(game_id)
        
        # Get all claimed positions by human players
        cursor = conn.execute(           
            f"""
            SELECT region_tag, ministry, {field} as submitted
            FROM players 
            WHERE game_id = ? AND is_ai = 0 AND region_tag = ? AND {field} = 1
            ORDER BY region_tag, ministry
            """,
            (game_id, reg, )
        )
        c2 = []
        c3 = cursor.fetchall()
        for row in c3:
            c2.append(row[1])
        
        
        waiting = []
        for r in MINISTRIES:
            if r == 'Future':
                continue  # Skip Future
            if r not in c2:
                waiting.append(r)
        
        return waiting


def create_game(gm_username: str) -> str:
    """Create a new game (always 3 rounds) and return game_id"""
    game_id = create_unique_game_id()
    lang = app.storage.user.get('lang')
    langx = app.storage.user.get('langx')
    mode = app.storage.user.get('mode')
    print(f'create game {lang} {str(langx)} {mode}')
    
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO games (game_id, gm_username, num_rounds, current_round, state, lang, langx, mode, state_x)
            VALUES (?, ?, 3, 0, 'setup', ?, ?, ?, 1)
            """,
            (game_id, gm_username, lang, langx, mode)
        )
        conn.commit()
    
    return game_id


def add_player(game_id: str, username: str, region_tag: str, ministry: str, runde: int, is_ai: bool = False) -> bool:
    """Add a player to the game"""
    with get_db() as conn:
        try:
            conn.execute(
                """
                INSERT INTO players (username, game_id, region_tag, ministry, is_logged_in_round1, is_ai)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (username, game_id, region_tag, ministry, runde, is_ai)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False


def get_player_info(username: str) -> Optional[Dict]:
    """Get player information by username"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT p.player_id, p.username, p.game_id, p.region_tag, p.ministry, 
                   p.is_ai, p.is_logged_in_round1, p.is_logged_in_round2, 
                   p.is_logged_in_round3, g.num_rounds, g.current_round, g.state
            FROM players p
            JOIN games g ON p.game_id = g.game_id
            WHERE p.username = ?
            """,
            (username,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def does_player_exist(username: str) -> bool:
    """Get player information by username"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT username
            FROM players
            WHERE username = ?
            """,
            (username,)
        )
        row = cursor.fetchone()
        if row:
            return True
        return False


def get_game_by_gm_username(gm_username: str) -> Optional[Dict]:
    """Get game information by GM username (returns most recent game)"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT game_id, gm_username, num_rounds, current_round, state, 
                   accept_decisions, created_at, updated_at
            FROM games
            WHERE gm_username = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (gm_username,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def get_policies_for_ministry(ministry: str) -> List[Dict]:
    """Get all policies for a specific ministry"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT p.*, pe.explanation
            FROM policies p
            LEFT JOIN policy_explanations pe ON p.pol_tag = pe.pol_tag
            WHERE p.pol_ministry = ?
            ORDER BY p.pol_id
            """,
            (ministry,)
        )
        return [dict(row) for row in cursor.fetchall()]


def get_plot_variables_for_ministry(ministry: str) -> List[Dict]:
    """Get all plot variables for a specific ministry"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM plot_variables
            WHERE pv_ministry = ?
            ORDER BY pv_id
            """,
            (ministry,)
        )
        return [dict(row) for row in cursor.fetchall()]


def save_policy_decision(conn, game_id: str, round_num: int, region_tag: str, 
                         ministry: str, pol_id: int, value: float, pol_tag: str, is_ai: int):
    """Save a policy decision to the database"""
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO policy_decisions (game_id, round, region_tag, ministry, pol_id, value, pol_tag, is_ai)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (game_id, round_num, region_tag, ministry, pol_id, value, pol_tag, is_ai)
        )
    except Exception as e:
        print(f"❌ ERROR saving policy decision: {e}")
        print(f"   Data: game_id={game_id}, round={round_num}, region={region_tag}, ministry={ministry}, pol_id={pol_id}, value={value}, pol_tag={pol_tag}")
        raise

def save_policy_decision_from_slider(game_id: str, round_num: int, region_tag: str, 
                         ministry: str, pol_id: int, value: float, pol_tag: str):
    """Save a policy decision to the database"""
    ts = datetime.datetime.now().replace(microsecond=0)
    with get_db() as conn:
        try:
            conn.execute(
                """
                UPDATE policy_decisions SET value = ?, timestamp = ?
                WHERE game_id = ? AND round = ? AND region_tag = ? AND ministry = ? AND pol_id = ? AND pol_tag = ?
                """,
                (value, ts, game_id, round_num, region_tag, ministry, pol_id, pol_tag)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"❌ ERROR saving policy decision: {e}")
            print(f"   Data: game_id={game_id}, round={round_num}, region={region_tag}, ministry={ministry}, pol_id={pol_id}, value={value}, pol_tag={pol_tag}")
            raise

def get_policy_decisions(game_id: str, round_num: int, region_tag: str, 
                         ministry: str) -> List[Tuple[int, float]]:
    """Get policy decisions for a specific player in a round"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT pol_id, value
            FROM policy_decisions
            WHERE game_id = ? AND round = ? AND region_tag = ? AND ministry = ?
            ORDER BY pol_id
            """,
            (game_id, round_num, region_tag, ministry)
        )
#        abc =  [(row['pol_id'], row['value']) for row in cursor.fetchall()]
        return [(row['pol_id'], row['value']) for row in cursor.fetchall()]

def get_one_policy_decision(game_id: str, round_num: int, region_tag: str, 
                         ministry: str, pol_tag: str) -> float:
    """Get policy decisions for a specific player in a round"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT value
            FROM policy_decisions
            WHERE game_id = ? AND round = ? AND region_tag = ? AND ministry = ? AND pol_tag = ?
            """,
            (game_id, round_num, region_tag, ministry, pol_tag)
        )
        row = cursor.fetchone()
        abc = row['value']
        return abc

def generate_ai_policy_valueOLD(pol_min: float, pol_max: float) -> float:
    """
    Generate random policy value using specified algorithm
    Value will be between pol_min + range/2 and pol_max
    thus biased towards GL
    """
    range_val = (pol_max - pol_min) / 2
    value = pol_min + range_val + random.uniform(0, 1) * (range_val / 2)
    return round(value, 5)

def generate_ai_policy_value(pol_min: float, pol_max: float) -> float:
    """
    Generate random policy value using specified algorithm
    values will be between pol_min and pol_max with bottom and top cut off
    """
    value = pol_min + random.uniform(0.1, 0.9) * (pol_max - pol_min)
    return round(value, 5)

def generate_human_regions(game_id: str, ai: list):
    with get_db() as conn:
        for r in REGION_ABBR:
            if r not in ai:
                cursor = conn.execute(
                    """
                    INSERT INTO human_regions (game_id, region_tag, sub_1, sub_2, sub_3)
                    VALUES (?, ?, ?, ?, ?)
                """, (game_id, r, 0, 0, 0))
        conn.commit()


def get_state_x(game_id: str, reg: str, actor: str):
    with get_db() as conn:
        if actor == 'gm':
            cursor = conn.execute(
                    """
                    SELECT state_x FROM games WHERE game_id = ?
                    VALUES (?)
                """, (game_id, ))
            row = cursor.fetchone()
            return int(row[0])
        
        cursor = conn.execute(
                """
                SELECT state_x FROM players WHERE game_id = ? AND region_tag = ? and ministry = ?
                VALUES (?, ?, ?)
            """, (game_id, reg, actor, ))
        row = cursor.fetchone()
        return int(row[0])

#def set_gm():
#    with get_db() as conn:
#        x = get_state_x(game_id, reg, actor)
#        x = x + 1
#        if actor == 'gm':
#            cursor = conn.execute(
#            f"""
#                UPDATE games
#                SET state_x = {x}
#                WHERE game_id = ?
#            """,
#            (game_id, ))
#            conn.commit()
#            return
#        cursor = conn.execute(
#        f"""
#            UPDATE players
#            SET state_x = {x}
#            WHERE game_id = ? AND region_tag = ? AND ministry = ?
#        """,
#        (game_id, reg, actor))
#        conn.commit()
#    pass

def set_state_x_plus_one(game_id: str, reg: str, actor: str):
    with get_db() as conn:
        x = get_state_x(game_id, reg, actor)
        x = x + 1
        if actor == 'gm':
            cursor = conn.execute(
            f"""
                UPDATE games
                SET state_x = {x}
                WHERE game_id = ?
            """,
            (game_id, ))
            conn.commit()
            return
        cursor = conn.execute(
        f"""
            UPDATE players
            SET state_x = {x}
            WHERE game_id = ? AND region_tag = ? AND ministry = ?
        """,
        (game_id, reg, actor))
        conn.commit()
    

def set_state_x_abs(game_id: str, reg: str, actor: str, x: int):
    with get_db() as conn:
        if actor == 'gm':
            cursor = conn.execute(
            f"""
                UPDATE games
                SET state_x = {x}
                WHERE game_id = ?
            """,
            (game_id, ))
            conn.commit()
            return
        cursor = conn.execute(
        f"""
            UPDATE players
            SET state_x = {x}
            WHERE game_id = ? AND region_tag = ? AND ministry = ?
        """,
        (game_id, reg, actor))
        conn.commit()
    


def generate_ai_policy_decisions(game_id: str):
    """
    Generate all AI policy decisions for a given round
    """
    with get_db() as conn:
        # Get all AI regions
        cursor = conn.execute(
            """
            SELECT region_tag
            FROM ai_regions
            WHERE game_id = ?
            """,
            (game_id,)
        )
        ai_regions = cursor.fetchall()
        ai_reg_list = [row[0] for row in ai_regions]
        
        # Get all policy tags
        ai_count = 0
        non_ai_count = 0
        cursor = conn.execute(
            """
            SELECT pol_tag, pol_min, pol_max, pol_id
            FROM policies
            """,
        )
        pols = cursor.fetchall()
        pols_list = [row[0] for row in pols]
        pols_mins = [row[1] for row in pols]
        pols_maxs = [row[2] for row in pols]
        pols_ids = [row[3] for row in pols]
        
        my_dict = dict(zip(pols_list, pols_ids))
#        print(my_dict)             
 
        for ministry in MINISTRIES:
            if ministry == 'Future':
                # Future Minister takes no decisions, just makes sure his / her colleauges don't go over the budget!
                continue
            cursor = conn.execute(
                """
                SELECT pol_tag, pol_min, pol_max
                FROM policies
                WHERE pol_ministry = ?
                """,
                (ministry, )
            )
            pols = cursor.fetchall()
            pols_list = [row[0] for row in pols]
            pols_mins = [row[1] for row in pols]
            pols_maxs = [row[2] for row in pols]
            
            for runde in range(1, 4):
                for re in REGION_ABBR:
                    i = 0
                    for p in pols_list:
                        pid = my_dict[p]
                        if re in ai_reg_list:
                            value = generate_ai_policy_value(pols_mins[i], pols_maxs[i])
                            ai_count += 1
                            is_ai = 1
#                            print(f"in ai -- R {str(runde)} reg={re} p={p} pid={str(pid)} value={str(value)} ai_cnt={str(ai_count)}")
                        else:
                            value = pols_mins[i]
                            non_ai_count += 1
                            is_ai = 0
#                            print(f"--- in NOT ai -- R {str(runde)} reg={re} p={p} pid={str(pid)} value={str(value)} NON_ai_cnt={str(non_ai_count)}")
                        save_policy_decision(conn, game_id, runde, re, ministry, int(pid), value, p, is_ai)
                        i += 1
                
        print(f"\n✅ Total ai decisions to save: {ai_count}")
        print(f"✅ Total NON ai decisions to save: {non_ai_count}")
        print(f"🔄 Committing transaction...")
        conn.commit()
        print(f"✅ Commit successful!")
        # Verify the data was saved
        cursor = conn.execute(
            "SELECT COUNT(*) as count FROM policy_decisions WHERE game_id = ? ",
            (game_id, )
        )
        saved_count = cursor.fetchone()['count']
        print(f"✅ Verified: {saved_count} decisions in database")
        print(f"=== POLICY GENERATION COMPLETE ===\n")
        print(f"\n --- Generating Human Regions for submission check ---\n")
        generate_human_regions(game_id, ai_reg_list)
        # Verify the data was saved
        cursor = conn.execute(
            "SELECT COUNT(*) as count FROM human_regions WHERE game_id = ? ",
            (game_id, )
        )
        saved_count = cursor.fetchone()['count']
        print(f"✅ Verified: {saved_count} regions in db")
        
def mark_player_submission(game_id: str, username: str, round_num: int,
                           region_tag: str = "", ministry: str = ""):
    """Mark that a player has opened their dashboard for a round (logged-in flag)."""
    field = f"is_logged_in_round{round_num}"
    with get_db() as conn:
        conn.execute(
            f"""
            INSERT INTO players (game_id, username, region_tag, ministry, {field})
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT(username) DO UPDATE SET {field} = 1
            """,
            (game_id, username, region_tag, ministry)
        )
        conn.commit()


def get_submission_status(game_id: str, round_num: int) -> Dict:
    """
    Get submission status for all human players in a round
    Returns: {
        'total_human': int,
        'submitted': int,
        'waiting': [(region_tag, ministry, username), ...],
        'all_submitted': bool
    }
    """
    with get_db() as conn:
        field = f"is_logged_in_round{round_num}"
        
        cursor = conn.execute(
            f"""
            SELECT region_tag, ministry, username, {field} as submitted
            FROM players
            WHERE game_id = ? AND is_ai = 0
            ORDER BY region_tag, ministry
            """,
            (game_id,)
        )
        players = cursor.fetchall()
        
        total = len(players)
        submitted = sum(1 for p in players if p['submitted'])
        waiting = [(p['region_tag'], p['ministry'], p['username']) 
                   for p in players if not p['submitted']]
        
        return {
            'total_human': total,
            'submitted': submitted,
            'waiting': waiting,
            'all_submitted': (submitted == total and total > 0)
        }


def advance_round(game_id: str):
    """
    Advance game to next round
    - Increment current_round
    - Reset accept_decisions to 0
    """
    with get_db() as conn:
        # Get current round
        cursor = conn.execute(
            "SELECT current_round, num_rounds FROM games WHERE game_id = ?",
            (game_id,)
        )
        game = cursor.fetchone()
        
        if not game:
            return False
        
        new_round = game['current_round'] + 1
        
        if new_round > game['num_rounds']:
            # Game is complete — still increment current_round so runde calc works
            conn.execute(
                """
                UPDATE games
                SET state = 'complete', current_round = ?, updated_at = CURRENT_TIMESTAMP
                WHERE game_id = ?
                """,
                (new_round, game_id)
            )
        else:
            # Advance to next round
            conn.execute(
                """
                UPDATE games
                SET current_round = ?, accept_decisions = 0, 
                    state = 'playing', updated_at = CURRENT_TIMESTAMP
                WHERE game_id = ?
                """,
                (new_round, game_id)
            )
        
        conn.commit()
        
        return True


def set_accept_decisionsFAKE(game_id: str, accept: bool):
    """Toggle accept_decisions flag"""
    with get_db() as conn:
        conn.execute(
            """
            UPDATE games
            SET accept_decisions = ?, updated_at = CURRENT_TIMESTAMP
            WHERE game_id = ?
            """,
            (1 if accept else 0, game_id)
        )
        conn.commit()


def get_game_info(game_id: str) -> Optional[Dict]:
    """Get complete game information"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM games WHERE game_id = ?
            """,
            (game_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def get_game_info_player(username: str) -> Optional[Dict]:
    """Get complete game information"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT game_id, region_tag, ministry, is_logged_in_round1, is_logged_in_round2, is_logged_in_round3, lang, langx, mode, state_x FROM players WHERE username = ?
            """,
            (username,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

def set_game_info_player(username, game_id, role ,lang, langx):
    ### see if username exists
    p_exists = does_player_exist(username)
    print(f'\nset_game_info_player: p_exists={p_exists} user={username} role={role}')
    app.storage.user['username'] = username
    with get_db() as conn:
        if p_exists:
            conn.execute("""
                UPDATE players
                SET is_logged_in_round1 = ?, lang = ?, langx = ?, state_x = ?
                WHERE username = ? AND game_id = ?
            """,
                (1, lang, langx, username, game_id, 99)
            )
        else:
            ts = datetime.datetime.now().replace(microsecond=0)
            conn.execute("""
                INSERT INTO players (game_id, username, ministry, lang, langx, state_x, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (game_id, username, role, lang, langx, 1, ts)
            )

def get_budget(game_id, current_round, region_tag, ta):
    """Get complete budget information"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM bud WHERE game_id = ? AND round = ? AND reg = ? AND ta = ? 
            """,
            (game_id, current_round, region_tag, ta)
        )
        pols = cursor.fetchall()
        tas = [row[0] for row in pols]
        amts = [row[1] for row in pols]
        
        my_dict = dict(zip(tas, amts))
        return amts


def disable_policy_sliders(game_id, round_num, region_tag):
    from nicegui import ui
    ui.notify(f'disable_policy_sliders GameID {game_id} Round {round_num} Reg {region_tag}', close_button='OK')
    
def mark_region_submitted(game_id: str, round_num: int, region_tag: str):
    """Record that Future has submitted the region's proposals for this round."""
    with get_db() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO region_submissions (game_id, round_num, region_tag)
            VALUES (?, ?, ?)
            """,
            (game_id, round_num, region_tag)
        )
        conn.commit()


def is_region_submitted(game_id: str, round_num: int, region_tag: str) -> bool:
    """Return True if Future has submitted this region's proposals for the given round."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT 1 FROM region_submissions WHERE game_id = ? AND round_num = ? AND region_tag = ?",
            (game_id, round_num, region_tag)
        ).fetchone()
    return row is not None


def get_unsubmitted_regions(game_id: str, round_num: int) -> list:
    """Return list of human region_tags that have NOT yet submitted for this round."""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT region_tag FROM human_regions
            WHERE game_id = ?
              AND region_tag NOT IN (
                  SELECT region_tag FROM region_submissions
                  WHERE game_id = ? AND round_num = ?
              )
            """,
            (game_id, game_id, round_num)
        )
        return [row['region_tag'] for row in cursor.fetchall()]


def add_notification_to_gm(game_id, round_num, region_tag):
    from nicegui import ui
    ui.notify(f'add_notification_to_gm GameID {game_id} Round {round_num} Reg {region_tag}', close_button='Bra')
    
    
def get_pols_by_ta(m):
    """Get investment proposals"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT pol_tag FROM policies WHERE pol_ministry = ?
            """,
            (m, )
        )
        pols = cursor.fetchall()
        tags = [row[0] for row in pols]
    return tags


def get_all_pols():
    """Get investment proposals"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT pol_tag FROM policies
            ORDER BY pol_tag
            """,
        )
        pols = cursor.fetchall()
        tags = [row[0] for row in pols]
    return tags

                
def get_inv_props(game_id, current_round, region_tag, m, p):
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT value FROM policy_decisions WHERE game_id = ? AND round = ? AND region_tag = ? AND ministry = ? AND pol_tag = ?
            """,
            (game_id, current_round, region_tag, m, p)
        )
        v = cursor.fetchone()
        x1 = v[0]
 
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT pol_min, pol_max FROM policies WHERE pol_tag = ?
            """,
            (p, )
        )
        v = cursor.fetchone()
        mi = v[0]
        mx = v[1]
        x = x1 - mi
    
    pct = x / (mx - mi) 
    return pct

def get_budget_claude(self, game_id, current_round, region_tag):
    """Get complete budget information"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT thematic_area, amount FROM bud 
            WHERE game_id = ? AND round = ? AND reg = ?
            """,
            (game_id, current_round, region_tag)
        )
        rows = cursor.fetchall()
        return {row[0]: row[1] for row in rows}

def get_ministry_budget_summary_claude(game_id, current_round, region_tag):
    """Get budget summary for all ministries in one query"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT 
                pd.ministry,
                p.pol_ministry_label,
                SUM((pd.value - p.pol_min) / (p.pol_max - p.pol_min) * b.amount) as total_amount,
                COUNT(*) as num_policies
            FROM policy_decisions pd
            JOIN policies p ON pd.pol_tag = p.pol_tag
            JOIN bud b ON p.pol_ministry = b.thematic_area
            WHERE pd.game_id = ? 
                AND pd.round = ? 
                AND pd.region_tag = ?
                AND b.game_id = ?
                AND b.round = ?
                AND b.reg = ?
            GROUP BY pd.ministry, p.pol_ministry_label
            ORDER BY pd.ministry
            """,
            (game_id, current_round, region_tag, game_id, current_round, region_tag)
        )
        return cursor.fetchall()
    
    
def get_ministry_tag(ministry: str) -> str:
    """Convert ministry name to tag"""
    mapping = {
        'Poverty': 'pov',
        'Inequality': 'ineq',
        'Empowerment': 'emp',
        'Food': 'food',
        'Energy': 'ener',
        'Future': 'fut'
    }
    return mapping.get(ministry, ministry.lower()[:4])


def get_budget_by_ministry_and_policy(game_id, current_round, region_tag):
    """Get budget organized by ministry with policy details"""
    
    # Determine budget parameters based on round
    if current_round == 1:
        budget_game_id = 'START'
        budget_round = 0
    else:
        budget_game_id = game_id
        budget_round = current_round - 1
    
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT
                pd.ministry,
                p.pol_ministry,
                pd.pol_tag,
                p.pol_name,
                pd.value as policy_value,
                (pd.value - p.pol_min) / (p.pol_max - p.pol_min) * b.value as amount_allocated
            FROM policy_decisions pd
            JOIN policies p ON pd.pol_tag = p.pol_tag
            JOIN bud b ON p.pol_ministry_tag = b.ta
            WHERE pd.game_id = ? 
                AND pd.round = ? 
                AND pd.region_tag = ?
                AND b.game_id = ?
                AND b.round = ?
                AND b.reg = ?
            ORDER BY pd.ministry, p.pol_name
            """,
            (game_id, current_round, region_tag, budget_game_id, budget_round, region_tag)
        )
        
        # Organize by ministry
        ministry_data = {}
        for row in cursor.fetchall():
            ministry = row['pol_ministry']
            if ministry not in ministry_data:
                ministry_data[ministry] = {
                    'ministry_name': ministry,
                    'policies': [],
                    'total': 0.0
                }
            
            policy_info = {
                'name': row['pol_name'],
                'pol_tag': row['pol_tag'],
                'value': row['policy_value'],
                'amount': row['amount_allocated']
            }
            ministry_data[ministry]['policies'].append(policy_info)
            ministry_data[ministry]['total'] += row['amount_allocated']
        
        return ministry_data

def get_session(token: str) -> dict | None:
    with get_db() as conn:
        row = conn.execute(
            'SELECT * FROM sessions WHERE token = ?', (token,)
        ).fetchone()
        return dict(row) if row else None

def create_session(token, username, game_id, role, ministry,
                   region_tag, lang, dark):
    with get_db() as conn:
        conn.execute('''
            INSERT OR REPLACE INTO sessions
            (token, username, game_id, role, ministry, region_tag, lang, dark)
            VALUES (?,?,?,?,?,?,?,?)
        ''', (token, username, game_id, role, ministry, region_tag, lang, dark))
        conn.commit()

def update_session(token: str, **kwargs):
    if not kwargs:
        return
    cols = ', '.join(f'{k} = ?' for k in kwargs)
    with get_db() as conn:
        conn.execute(
            f'UPDATE sessions SET {cols} WHERE token = ?',
            (*kwargs.values(), token)
        )
        conn.commit()

def delete_session(token: str):
    with get_db() as conn:
        conn.execute('DELETE FROM sessions WHERE token = ?', (token,))
        conn.commit()

if __name__ == "__main__":
    # Initialize database
    init_database()
    load_policies_data()
    load_plot_variables_data()
    print("Database initialized with 32 policies and 48 plot variables!")
    
    # Test game_id generation
    print("\nSample game IDs:")
    for _ in range(5):
        print(f"  {generate_game_id()}")
        