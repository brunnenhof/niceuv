import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import pickle
import sqlite3
from contextlib import contextmanager
import database as db

@contextmanager
def get_db2():
    """Context manager for database connections"""
    conn = sqlite3.connect(db.DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def budget_to_db(cid, round, ro, mpc):
    regs = ['us', 'af', 'cn', 'me', 'sa', 'la', 'pa', 'ec', 'eu', 'se']
    x_all = mpc.index("Budget_for_all_TA_per_region_calculated_as_pct_of_GDP.0")
#    print(str(x_all) + ' ' + mpc[x_all])
    x_pov = mpc.index("Cost_per_regional_poverty_policy.0")
    x_ineq = mpc.index("Cost_per_regional_inequality_policy.0")
    x_ener = mpc.index("Cost_per_regional_energy_policy.0")
    x_foo = mpc.index("Cost_per_regional_food_policy.0")
    x_emp = mpc.index("Cost_per_regional_empowerment_policy.0")

    for i in range(0, 10):
        con = sqlite3.connect("sdg3_game.db")
        ### see if row exists
        q = "SELECT * FROM bud WHERE game_id='" + cid + "' AND round='" + str(round) + "' AND reg='" + regs[i] + "';"
        exist = pd.read_sql_query(q, con)
        regi = regs[i]
        total_ta = ro[x_all + 1 + i]
        c_pov = ro[x_pov + 1 + i]
        c_ineq = ro[x_ineq + 1 + i]
        c_ener = ro[x_ener + 1 + i]
        c_food = ro[x_foo + 1 + i]
        c_emp = ro[x_emp + 1 + i]
#        print(regs[i] + ' budget ' + f"{total_ta:.1f}")
#        print(regs[i] + ' c_emp ' + f"{c_emp:.1f}")
#        print(regs[i] + ' c_pov ' + f"{c_pov:.1f}")
#        print(regs[i] + ' c_ineq ' + f"{c_ineq:.1f}")
#        print(regs[i] + ' c_ener ' + f"{c_ener:.1f}")
#        print(regs[i] + ' c_food ' + f"{c_food:.1f}")

        pass
        if len(exist) == 0:
            con.execute("""
                INSERT INTO bud (game_id, round, ta, value, reg, regx)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                        (cid, round, 'bud', total_ta, regi, i))
            con.commit()
            con.execute("""
                INSERT INTO bud (game_id, round, ta, value, reg, regx)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                        (cid, round, 'pov', c_pov, regi, i))
            con.commit()
            con.execute("""
                INSERT INTO bud (game_id, round, ta, value, reg, regx)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                        (cid, round, 'ineq', c_ineq, regi, i))
            con.commit()
            con.execute("""
                INSERT INTO bud (game_id, round, ta, value, reg, regx)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                        (cid, round, 'emp', c_emp, regi, i))
            con.commit()
            con.execute("""
                INSERT INTO bud (game_id, round, ta, value, reg, regx)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                        (cid, round, 'food', c_food, regi, i))
            con.commit()
            con.execute("""
                INSERT INTO bud (game_id, round, ta, value, reg, regx)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                        (cid, round, 'ener', c_ener, regi, i))
            con.commit()
        else:
            update_statement = 'UPDATE bud SET value=? WHERE game_id = ? AND reg = ? AND round = ? AND ta = ?'
            con.execute("""
                UPDATE bud SET value=? WHERE game_id = ? AND reg = ? AND round = ? AND ta = ? """,
                        (total_ta, cid, regs[i], round, 'bud'))
            con.commit()

            con.execute("""
                UPDATE bud SET value=? WHERE game_id = ? AND reg = ? AND round = ? AND ta = ? """,
                        (c_pov, cid, regs[i], round, 'pov'))
            con.commit()

            con.execute("""
                UPDATE bud SET value=? WHERE game_id = ? AND reg = ? AND round = ? AND ta = ? """,
                        (c_ineq, cid, regs[i], round, 'ineq'))
            con.commit()

            con.execute("""
                UPDATE bud SET value=? WHERE game_id = ? AND reg = ? AND round = ? AND ta = ? """,
                        (c_ener, cid, regs[i], round, 'ener'))
            con.commit()

            con.execute("""
                UPDATE bud SET value=? WHERE game_id = ? AND reg = ? AND round = ? AND ta = ? """,
                        (c_food, cid, regs[i], round, 'food'))
            con.commit()

            con.execute("""
                UPDATE bud SET value=? WHERE game_id = ? AND reg = ? AND round = ? AND ta = ? """,
                        (c_emp, cid, regs[i], round, 'emp'))
            con.commit()
        con.close()

start_time = time.time()
#
#
path = "files/"
game_id = "XXC-902"
with open(path + "plot_var_list.pkl", "rb") as fp:  # Unpickling
    plot_var_list = pickle.load(fp)
with open(path + "plot_var_list_10.pkl", "rb") as fp:  # Unpickling
    plot_var_list_10 = pickle.load(fp)
#with open(path + "plot_var_list.pkl", "rb") as fp:  # Unpickling
#    plot_var_list = pickle.load(fp)
#with open(path + "plot_var_list_10.pkl", "rb") as fp:  # Unpickling
#    plot_var_list_10 = pickle.load(fp)
    
mdf_cur = np.load(game_id + '_plot25_40.npy')
ro = mdf_cur[480,:]
budget_to_db(game_id, 1, ro, plot_var_list)

duration = time.time() - start_time
print("--- %s seconds ---" % (time.time() - start_time))
