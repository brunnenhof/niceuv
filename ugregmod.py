# -*- coding: utf-8 -*-
# Created on Fri 16 Jan 2026 16:01:30
#    created by    e4apm_jan_16_prod.php    from    mov251229_ge4a_10reg.txt
# @author: U Goluke

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import json
import time
import pickle
from contextlib import contextmanager
from sys import exit
import sqlite3
import database as db

#path = "C:\\Users\\ekj26\\Desktop\\game_w2526\\"
path = "files/"

###################
###################

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
#        if i == 0:
#            print(ro[x_all - 1 + i])
#            print(ro[x_all + 0 + i])
#            print(ro[x_all + 1 + i])
        c_pov = ro[x_pov + 1 + i]
        c_ineq = ro[x_ineq + 1 + i]
        c_ener = ro[x_ener + 1 + i]
        c_food = ro[x_foo + 1 + i]
        c_emp = ro[x_emp + 1 + i]
#        if i == 0:
#        print(regs[i] + ' runde ' + str(round) + ' budget ' + f"{total_ta:.1f}")
#        print(regs[i] + ' runde ' + str(round) + ' c_emp ' + f"{c_emp:.1f}")
#        print(regs[i] + ' runde ' + str(round) + ' c_pov ' + f"{c_pov:.1f}")
#        print(regs[i] + ' runde ' + str(round) + ' c_ineq ' + f"{c_ineq:.1f}")
#        print(regs[i] + ' runde ' + str(round) + ' c_ener ' + f"{c_ener:.1f}")
#        print(regs[i] + ' runde ' + str(round) + ' c_food ' + f"{c_food:.1f}")

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


def ugregmod(game_id, runde):
#    ro80 = np.load(path+'ro80.npy')
    ch = np.load(path+'ch.npy')
#    chtab = np.load(path+'chtab.npy')
#    var_sampeld = np.load(path+'var_sampeld.npy')
    with open(path+'fcol_in_mdf.json', 'r') as ff:
        fcol_in_mdf = json.load(ff)
    with open(path+'ftab_in_d_table.json', 'r') as ff:
        ftab_in_d_table = json.load(ff)
    with open(path+'d_table.pkl', 'rb') as fp:
        d_table = pickle.load(fp)


    def STEP(zeit, amt, start):
        if zeit < start:
            return 0.0
        if zeit >= start:
            return amt

    def GRAPH(x, xarr, yarr):
        last = len(xarr) - 1
        if x < xarr[0]:
            return yarr[0]
        if x > xarr[last]:
            return yarr[last]
        if np.all(np.diff(xarr) == 0):
            print('x not monotonically increasing ==0')
        if np.all(np.diff(xarr) < 0):
            print('x not monotonically increasing <0')
        return np.interp(x, xarr, yarr)


    def IF_THEN_ELSE(c, t, f):
        if isinstance(c, np.ndarray):
            arr = np.zeros(10)
            for i in range(0,10):
                if c[i]:
                    if isinstance(t, np.ndarray):
                        arr[i] = t[i]
                    else:
                        arr[i] = t
                else:
                    if isinstance(f, np.ndarray):
                        arr[i] = f[i]
                    else:
                        arr[i] = f
    #        print(type(arr))
    #        print(arr)
            return arr
        if c:
            return t
        else:
            return f

    def SAMPLE_IF_TRUE(a, t, f, i):
        global var_sampeld
        if zeit < a:
            return f
        elif zeit == a:
            var_sampeld[i] = t
            return var_sampeld[i]
        else:
            return var_sampeld[i]

    def ZIDZ(a, b):
        if b < 1e-06 and b > -1e-06:
            return 0.0
        else:
            return a/b

    def PULSE_TRAIN(zeit, first,duration,every,height):
        s = list(range(first, 2100, every))
        e = list(range(first + duration, 2100, every))
        if len(e) != 3:
            raise ValueError('in PULSE_TRAIN as coded there must be exactly 3 repetitions before 2100')
        if zeit < first:
            return 0
        if (zeit >= s[0] and zeit < e[0]) or (zeit >= s[1] and zeit < e[1]) or (zeit >= s[2] and zeit < e[2]):
            return height
        else:
            return 0

    def SQRT(a):
        return np.sqrt(a)

    def fill_mdf_plot_row_start(runde, mdf_plot, ch, plot_var_list, plot_var_list_10, filled_from_row, rowi):
        ###
        #    fills for the selected row (timestep) the mdf_plot matrix with the corresponding values from the model (the mdf matrix)
        ###
        i = 1
        new_list = plot_var_list_10
        for c in new_list:
            c_zero = c.find('.0')
            if not(c_zero == -1):
                c = c.replace('.0','')
                x = np.where(ch == (c+'-us'))[0][0]
                mdf_plot[rowi, i:i+10] = filled_from_row[x:x+10]
                i += 10
            else:
                x = np.where(ch == c)[0][0]
                mdf_plot[rowi, i] = filled_from_row[x]
                i += 1
        return mdf_plot


# Read excel file with all the info about policies by round
# to set up 3 dataframes which are identical at the beginning and read in MAX and MIN values
# CAREFUL: the location, the ilocs, are hard wired!

### read in policies from DB
    def get_pol_min_max():
        cnx = sqlite3.connect('sdg3_game.db')
        query = """
            SELECT pol_tag, pol_min, pol_max FROM policies
            ORDER BY pol_tag
            """
        df = pd.read_sql_query(query, cnx)
        cnx.commit()
        cnx.close()
        return df


    def get_policies(game_id, runde):
        cnx = sqlite3.connect('sdg3_game.db')
        query = """
            SELECT region_tag, pol_tag, value FROM policy_decisions
            WHERE game_id = ? AND round = ?
            ORDER BY pol_tag, region_tag
            """
        df = pd.read_sql_query(query, cnx, params=(game_id, runde))
        cnx.commit()
        cnx.close()
        return df

    def get_pol_values_as_list(p, dict_df1, game_id):
        pol_list = []
        for reg in db.REGION_ABBR:
#            idx = dict_df1.loc[(dict_df1['region_tag'] == reg) & (dict_df1['pol_tag'] == p) & (dict_df1['game_id'] == game_id)]
            idx = dict_df1.loc[(dict_df1['region_tag'] == reg) & (dict_df1['pol_tag'] == p)]
#            print(idx)
#            print(type(idx))
#            print(idx.shape)
            v = idx.iloc[0,2]
#            print(v)
            pol_list.append(v)
        return pol_list
        
    pols = db.get_all_pols()
    #print(pols)
    dict_df1 = get_policies(game_id, 1)
    #print(dict_df1)
    for p in pols:
        pol_list = get_pol_values_as_list(p, dict_df1, game_id)
        if p == 'CCS':
            CCS_R1_via_Excel = pol_list
        elif p == 'Ctax':
            Ctax_R1_via_Excel = pol_list
        elif p == 'DAC':
            DAC_R1_via_Excel = pol_list
        elif p == 'ExPS':
            ExPS_R1_via_Excel = pol_list
        elif p == 'FC':
            REFOREST_R1_via_Excel = pol_list
        elif p == 'FEHC':
            FEHC_R1_via_Excel = pol_list
        elif p == 'FLWR':
            FLWR_R1_via_Excel = pol_list
        elif p == 'FMPLDD':
            FMPLDD_R1_via_Excel = pol_list
        elif p == 'FPGDC':
            FPGDC_R1_via_Excel = pol_list
        elif p == 'FTPEE':
            FTPEE_R1_via_Excel = pol_list
        elif p == 'FWRP':
            FWRP_R1_via_Excel = pol_list
        elif p == 'ICTR':
            ICTR_R1_via_Excel = pol_list
        elif p == 'IOITR':
            IOITR_R1_via_Excel = pol_list
        elif p == 'ISPV':
            ISPV_R1_via_Excel = pol_list
        elif p == 'IWITR':
            IWITR_R1_via_Excel = pol_list
        elif p == 'LPB':
            LPB_R1_via_Excel = pol_list
        elif p == 'LPBgrant':
            LPBgrant_R1_via_Excel = pol_list
        elif p == 'LPBsplit':
            LPBsplit_R1_via_Excel = pol_list
        elif p == 'Lfrac':
            Lfrac_R1_via_Excel = pol_list
        elif p == 'NEP':
            NEP_R1_via_Excel = pol_list
        elif p == 'RIPLGF':
            RIPLGF_R1_via_Excel = pol_list
        elif p == 'RMDR':
            RMDR_R1_via_Excel = pol_list
        elif p == 'SGMP':
            SGMP_R1_via_Excel = pol_list
        elif p == 'SGRPI':
            SGRPI_R1_via_Excel = pol_list
        elif p == 'SSGDR':
            SSGDR_R1_via_Excel = pol_list
        elif p == 'StrUP':
            StrUP_R1_via_Excel = pol_list
        elif p == 'TOW':
            TOW_R1_via_Excel = pol_list
        elif p == 'Wreaction':
            Wreaction_R1_via_Excel = pol_list
        elif p == 'XtaxCom':
            XtaxCom_R1_via_Excel = pol_list
        elif p == 'XtaxFrac':
            XtaxFrac_R1_via_Excel = pol_list
        elif p == 'XtaxRateEmp':
            XtaxEmp_R1_via_Excel = pol_list


    dict_df2 = get_policies(game_id, 2)
    for p in pols:
        pol_list = get_pol_values_as_list(p, dict_df2, game_id)
        if p == 'CCS':
            CCS_R2_via_Excel = pol_list
        elif p == 'Ctax':
            Ctax_R2_via_Excel = pol_list
        elif p == 'DAC':
            DAC_R2_via_Excel = pol_list
        elif p == 'ExPS':
            ExPS_R2_via_Excel = pol_list
        elif p == 'FC':
            REFOREST_R2_via_Excel = pol_list
        elif p == 'FEHC':
            FEHC_R2_via_Excel = pol_list
        elif p == 'FLWR':
            FLWR_R2_via_Excel = pol_list
        elif p == 'FPGDC':
            FPGDC_R2_via_Excel = pol_list
        elif p == 'FMPLDD':
            FMPLDD_R2_via_Excel = pol_list
        elif p == 'FTPEE':
            FTPEE_R2_via_Excel = pol_list
        elif p == 'FWRP':
            FWRP_R2_via_Excel = pol_list
        elif p == 'ICTR':
            ICTR_R2_via_Excel = pol_list
        elif p == 'IOITR':
            IOITR_R2_via_Excel = pol_list
        elif p == 'ISPV':
            ISPV_R2_via_Excel = pol_list
        elif p == 'IWITR':
            IWITR_R2_via_Excel = pol_list
        elif p == 'LPB':
            LPB_R2_via_Excel = pol_list
        elif p == 'LPBgrant':
            LPBgrant_R2_via_Excel = pol_list
        elif p == 'LPBsplit':
            LPBsplit_R2_via_Excel = pol_list
        elif p == 'Lfrac':
            Lfrac_R2_via_Excel = pol_list
        elif p == 'NEP':
            NEP_R2_via_Excel = pol_list
        elif p == 'RIPLGF':
            RIPLGF_R2_via_Excel = pol_list
        elif p == 'RMDR':
            RMDR_R2_via_Excel = pol_list
        elif p == 'SGMP':
            SGMP_R2_via_Excel = pol_list
        elif p == 'SGRPI':
            SGRPI_R2_via_Excel = pol_list
        elif p == 'SSGDR':
            SSGDR_R2_via_Excel = pol_list
        elif p == 'StrUP':
            StrUP_R2_via_Excel = pol_list
        elif p == 'TOW':
            TOW_R2_via_Excel = pol_list
        elif p == 'Wreaction':
            Wreaction_R2_via_Excel = pol_list
        elif p == 'XtaxCom':
            XtaxCom_R2_via_Excel = pol_list
        elif p == 'XtaxFrac':
            XtaxFrac_R2_via_Excel = pol_list
        elif p == 'XtaxRateEmp':
            XtaxEmp_R2_via_Excel = pol_list


    dict_df3 = get_policies(game_id, 3)
    for p in pols:
        pol_list = get_pol_values_as_list(p, dict_df3, game_id)
        if p == 'CCS':
            CCS_R3_via_Excel = pol_list
        elif p == 'Ctax':
            Ctax_R3_via_Excel = pol_list
        elif p == 'DAC':
            DAC_R3_via_Excel = pol_list
        elif p == 'ExPS':
            ExPS_R3_via_Excel = pol_list
        elif p == 'FC':
            REFOREST_R3_via_Excel = pol_list
        elif p == 'FEHC':
            FEHC_R3_via_Excel = pol_list
        elif p == 'FLWR':
            FLWR_R3_via_Excel = pol_list
        elif p == 'FMPLDD':
            FMPLDD_R3_via_Excel = pol_list
        elif p == 'FPGDC':
            FPGDC_R3_via_Excel = pol_list
        elif p == 'FTPEE':
            FTPEE_R3_via_Excel = pol_list
        elif p == 'FWRP':
            FWRP_R3_via_Excel = pol_list
        elif p == 'ICTR':
            ICTR_R3_via_Excel = pol_list
        elif p == 'IOITR':
            IOITR_R3_via_Excel = pol_list
        elif p == 'ISPV':
            ISPV_R3_via_Excel = pol_list
        elif p == 'IWITR':
            IWITR_R3_via_Excel = pol_list
        elif p == 'LPB':
            LPB_R3_via_Excel = pol_list
        elif p == 'LPBgrant':
            LPBgrant_R3_via_Excel = pol_list
        elif p == 'LPBsplit':
            LPBsplit_R3_via_Excel = pol_list
        elif p == 'Lfrac':
            Lfrac_R3_via_Excel = pol_list
        elif p == 'NEP':
            NEP_R3_via_Excel = pol_list
        elif p == 'RIPLGF':
            RIPLGF_R3_via_Excel = pol_list
        elif p == 'RMDR':
            RMDR_R3_via_Excel = pol_list
        elif p == 'SGMP':
            SGMP_R3_via_Excel = pol_list
        elif p == 'SGRPI':
            SGRPI_R3_via_Excel = pol_list
        elif p == 'SSGDR':
            SSGDR_R3_via_Excel = pol_list
        elif p == 'StrUP':
            StrUP_R3_via_Excel = pol_list
        elif p == 'TOW':
            TOW_R3_via_Excel = pol_list
        elif p == 'Wreaction':
            Wreaction_R3_via_Excel = pol_list
        elif p == 'XtaxCom':
            XtaxCom_R3_via_Excel = pol_list
        elif p == 'XtaxFrac':
            XtaxFrac_R3_via_Excel = pol_list
        elif p == 'XtaxRateEmp':
            XtaxEmp_R3_via_Excel = pol_list

    min_max = get_pol_min_max()
    #print(min_max)
    for p in pols:
        row = min_max.loc[(min_max['pol_tag'] == p)]
#        print(row)
        mini = row.iloc[0,1]
        maxi = row.iloc[0,2]
        if p == 'CCS':
            CCS_policy_Max = maxi
            CCS_policy_Min = mini
        elif p == 'Ctax':
            Ctax_policy_Max = maxi
            Ctax_policy_Min = mini
        elif p == 'DAC':
            DAC_policy_Max = maxi
            DAC_policy_Min = mini
        elif p == 'ExPS':
            ExPS_policy_Max = maxi
            ExPS_policy_Min = mini
        elif p == 'FC':
            REFOREST_policy_Max = maxi
            REFOREST_policy_Min = mini
        elif p == 'FEHC':
            FEHC_policy_Max = maxi
            FEHC_policy_Min = mini
        elif p == 'FLWR':
            FLWR_policy_Max = maxi
            FLWR_policy_Min = mini
        elif p == 'FMPLDD':
            FMPLDD_policy_Max = maxi
            FMPLDD_policy_Min = mini
        elif p == 'FPGDC':
            FPGDC_policy_Max = maxi
            FPGDC_policy_Min = mini
        elif p == 'FTPEE':
            FTPEE_policy_Max = maxi
            FTPEE_policy_Min = mini
        elif p == 'FWRP':
            FWRP_policy_Max = maxi
            FWRP_policy_Min = mini
        elif p == 'ICTR':
            ICTR_policy_Max = maxi
            ICTR_policy_Min = mini
        elif p == 'IOITR':
            IOITR_policy_Max = maxi
            IOITR_policy_Min = mini
        elif p == 'ISPV':
            ISPV_policy_Max = maxi
            ISPV_policy_Min = mini
        elif p == 'IWITR':
            IWITR_policy_Max = maxi
            IWITR_policy_Min = mini
        elif p == 'LPB':
            LPB_policy_Max = maxi
            LPB_policy_Min = mini
        elif p == 'LPBgrant':
            LPBgrant_policy_Max = maxi
            LPBgrant_policy_Min = mini
        elif p == 'LPBsplit':
            LPBsplit_policy_Max = maxi
            LPBsplit_policy_Min = mini
        elif p == 'Lfrac':
            Lfrac_policy_Max = maxi
            Lfrac_policy_Min = mini
        elif p == 'NEP':
            NEP_policy_Max = maxi
            NEP_policy_Min = mini
        elif p == 'RIPLGF':
            RIPLGF_policy_Max = maxi
            RIPLGF_policy_Min = mini
        elif p == 'RMDR':
            RMDR_policy_Max = maxi
            RMDR_policy_Min = mini
        elif p == 'SGMP':
            SGMP_policy_Max = maxi
            SGMP_policy_Min = mini
        elif p == 'SGRPI':
            SGRPI_policy_Max = maxi
            SGRPI_policy_Min = mini
        elif p == 'SSGDR':
            SSGDR_policy_Max = maxi
            SSGDR_policy_Min = mini
        elif p == 'StrUP':
            StrUP_policy_Max = maxi
            StrUP_policy_Min = mini
        elif p == 'TOW':
            TOW_policy_Max = maxi
            TOW_policy_Min = mini
        elif p == 'Wreaction':
            Wreaction_policy_Max = maxi
            Wreaction_policy_Min = mini
        elif p == 'XtaxCom':
            XtaxCom_policy_Max = maxi
            XtaxCom_policy_Min = mini
        elif p == 'XtaxFrac':
            XtaxFrac_policy_Max = maxi
            XtaxFrac_policy_Min = mini
        elif p == 'XtaxRateEmp':
            XtaxEmp_policy_Max = maxi
            XtaxEmp_policy_Min = mini

#    ExPS_R3_via_Excel = r3_df.iloc[0, 3:13].tolist()
#    ExPS_R2_via_Excel = r2_df.iloc[0, 3:13].tolist()
#    ExPS_R1_via_Excel = r1_df.iloc[0, 3:13].tolist()
#    ExPS_policy_Max = r1_df.iloc[0, 14]
#    ExPS_policy_Min = r1_df.iloc[0, 13]

#    dict_df2 = get_policies(game_id, 2)
#    dict_df3 = get_policies(game_id, 3)
#    dict_df = pd.read_excel('e4a-game-policies.xlsx',sheet_name=['r1'])
#    r1_df = dict_df.get('r1')
    # the EXCEL file has dirty rows in it
#    r1_df_clean = r1_df.drop(labels=[0,5,11,12,13,14,24,25,29,30,37,43,44,45,46,47,48], axis = 0)
#    r1_df_clean = r1_df_clean.reset_index()
#    r1_df_clean = r1_df_clean.drop(labels=['index'], axis = 1)
#    r1_df = r1_df_clean

#    dict_df = pd.read_excel('e4a-game-policies.xlsx',sheet_name=['r2'])
#    r2_df = dict_df.get('r2')
#    # the EXCEL file has dirty rows in it
#    r2_df_clean = r2_df.drop(labels=[0,5,11,12,13,14,24,25,29,30,37,43,44,45,46,47,48], axis = 0)
#    r2_df_clean = r2_df_clean.reset_index()
#    r2_df_clean = r2_df_clean.drop(labels=['index'], axis = 1)
#    r2_df = r2_df_clean

#    dict_df = pd.read_excel('e4a-game-policies.xlsx',sheet_name=['r3'])
#    r3_df = dict_df.get('r3')
#    # the EXCEL file has dirty rows in it
#    r3_df_clean = r3_df.drop(labels=[0,5,11,12,13,14,24,25,29,30,37,43,44,45,46,47,48], axis = 0)
#    r3_df_clean = r3_df_clean.reset_index()
#    r3_df_clean = r3_df_clean.drop(labels=['index'], axis = 1)
#    r3_df = r3_df_clean

#    ExPS_R3_via_Excel = r3_df.iloc[0, 3:13].tolist()
#    ExPS_R2_via_Excel = r2_df.iloc[0, 3:13].tolist()
#    ExPS_R1_via_Excel = r1_df.iloc[0, 3:13].tolist()
#    ExPS_policy_Max = r1_df.iloc[0, 14]
#    ExPS_policy_Min = r1_df.iloc[0, 13]
    
#    LPB_R3_via_Excel = r3_df.iloc[1, 3:13].tolist()
#    LPB_R2_via_Excel = r2_df.iloc[1, 3:13].tolist()
#    LPB_R1_via_Excel = r1_df.iloc[1, 3:13].tolist()
#    LPB_policy_Max = r1_df.iloc[1, 14]
#    LPB_policy_Min = r1_df.iloc[1, 13]
    
#    LPBsplit_R3_via_Excel = r3_df.iloc[2, 3:13].tolist()
#    LPBsplit_R2_via_Excel = r2_df.iloc[2, 3:13].tolist()
#    LPBsplit_R1_via_Excel = r1_df.iloc[2, 3:13].tolist()
#    LPBsplit_policy_Max = r1_df.iloc[2, 14]
#    LPBsplit_policy_Min = r1_df.iloc[2, 13]
    
#    LPBgrant_R3_via_Excel = r3_df.iloc[3, 3:13].tolist()
#    LPBgrant_R2_via_Excel = r2_df.iloc[3, 3:13].tolist()
#    LPBgrant_R1_via_Excel = r1_df.iloc[3, 3:13].tolist()
#    LPBgrant_policy_Max = r1_df.iloc[3, 14]
#    LPBgrant_policy_Min = r1_df.iloc[3, 13]
    
#    FMPLDD_R3_via_Excel = r3_df.iloc[4, 3:13].tolist()
#    FMPLDD_R2_via_Excel = r2_df.iloc[4, 3:13].tolist()
#    FMPLDD_R1_via_Excel = r1_df.iloc[4, 3:13].tolist()
#    FMPLDD_policy_Max = r1_df.iloc[4, 14]
#    FMPLDD_policy_Min = r1_df.iloc[4, 13]
    
#    TOW_R3_via_Excel = r3_df.iloc[5, 3:13].tolist()
#    TOW_R2_via_Excel = r2_df.iloc[5, 3:13].tolist()
#    TOW_R1_via_Excel = r1_df.iloc[5, 3:13].tolist()
#    TOW_policy_Max = r1_df.iloc[5, 14]
#    TOW_policy_Min = r1_df.iloc[5, 13]
    
#    FPGDC_R3_via_Excel = r3_df.iloc[6, 3:13].tolist()
#    FPGDC_R2_via_Excel = r2_df.iloc[6, 3:13].tolist()
#    FPGDC_R1_via_Excel = r1_df.iloc[6, 3:13].tolist()
#    FPGDC_policy_Max = r1_df.iloc[6, 14]
#    FPGDC_policy_Min = r1_df.iloc[6, 13]
    
#    Lfrac_R3_via_Excel = r3_df.iloc[7, 3:13].tolist()
#    Lfrac_R2_via_Excel = r2_df.iloc[7, 3:13].tolist()
#    Lfrac_R1_via_Excel = r1_df.iloc[7, 3:13].tolist()
#    Lfrac_policy_Max = r1_df.iloc[7, 14]
#    Lfrac_policy_Min = r1_df.iloc[7, 13]
    
#    SSGDR_R3_via_Excel = r3_df.iloc[8, 3:13].tolist()
#    SSGDR_R2_via_Excel = r2_df.iloc[8, 3:13].tolist()
#    SSGDR_R1_via_Excel = r1_df.iloc[8, 3:13].tolist()
#    SSGDR_policy_Max = r1_df.iloc[8, 14]
#    SSGDR_policy_Min = r1_df.iloc[8, 13]
    
#    XtaxFrac_R3_via_Excel = r3_df.iloc[9, 3:13].tolist()
#    XtaxFrac_R2_via_Excel = r2_df.iloc[9, 3:13].tolist()
#    XtaxFrac_R1_via_Excel = r1_df.iloc[9, 3:13].tolist()
#    Xtaxfrac_policy_Max = r1_df.iloc[9, 14]
#    Xtaxfrac_policy_Min = r1_df.iloc[9, 13]
#    XtaxFrac_policy_Min = Xtaxfrac_policy_Min
#    XtaxFrac_policy_Max = Xtaxfrac_policy_Max
    
#    StrUP_R3_via_Excel = r3_df.iloc[10, 3:13].tolist()
#    StrUP_R2_via_Excel = r2_df.iloc[10, 3:13].tolist()
#    StrUP_R1_via_Excel = r1_df.iloc[10, 3:13].tolist()
#    StrUP_policy_Max = r1_df.iloc[10, 14]
#    StrUP_policy_Min = r1_df.iloc[10, 13]
    
#    Wreaction_R3_via_Excel = r3_df.iloc[11, 3:13].tolist()
#    Wreaction_R2_via_Excel = r2_df.iloc[11, 3:13].tolist()
#    Wreaction_R1_via_Excel = r1_df.iloc[11, 3:13].tolist()
#    WReaction_policy_Max = r1_df.iloc[11, 14]
#    WReaction_policy_Min = r1_df.iloc[11, 13]
#    Wreaction_policy_Min = WReaction_policy_Min
#    Wreaction_policy_Max = WReaction_policy_Max
#    
#    XtaxCom_R3_via_Excel = r3_df.iloc[12, 3:13].tolist()
#    XtaxCom_R2_via_Excel = r2_df.iloc[12, 3:13].tolist()
#    XtaxCom_R1_via_Excel = r1_df.iloc[12, 3:13].tolist()
#    XtaxCom_policy_Max = r1_df.iloc[12, 14]
#    XtaxCom_policy_Min = r1_df.iloc[12, 13]
    
#    ICTR_R3_via_Excel = r3_df.iloc[13, 3:13].tolist()
#    ICTR_R2_via_Excel = r2_df.iloc[13, 3:13].tolist()
#    ICTR_R1_via_Excel = r1_df.iloc[13, 3:13].tolist()
#    ICTR_policy_Max = r1_df.iloc[13, 14]
#    ICTR_policy_Min = r1_df.iloc[13, 13]
    
#    IOITR_R3_via_Excel = r3_df.iloc[14, 3:13].tolist()
#    IOITR_R2_via_Excel = r2_df.iloc[14, 3:13].tolist()
#    IOITR_R1_via_Excel = r1_df.iloc[14, 3:13].tolist()
#    IOITR_policy_Max = r1_df.iloc[14, 14]
#    IOITR_policy_Min = r1_df.iloc[14, 13]
    
#    IWITR_R3_via_Excel = r3_df.iloc[15, 3:13].tolist()
#    IWITR_R2_via_Excel = r2_df.iloc[15, 3:13].tolist()
#    IWITR_R1_via_Excel = r1_df.iloc[15, 3:13].tolist()
#    IWITR_policy_Max = r1_df.iloc[15, 14]
#    IWITR_policy_Min = r1_df.iloc[15, 13]
#    
#    Ctax_R3_via_Excel = r3_df.iloc[16, 3:13].tolist()
#    Ctax_R2_via_Excel = r2_df.iloc[16, 3:13].tolist()
#    Ctax_R1_via_Excel = r1_df.iloc[16, 3:13].tolist()
#    Ctax_policy_Max = r1_df.iloc[16, 14]
#    Ctax_policy_Min = r1_df.iloc[16, 13]
    
#    SGRPI_R3_via_Excel = r3_df.iloc[17, 3:13].tolist()
#    SGRPI_R2_via_Excel = r2_df.iloc[17, 3:13].tolist()
#    SGRPI_R1_via_Excel = r1_df.iloc[17, 3:13].tolist()
#    SGRPI_policy_Max = r1_df.iloc[17, 14]
#    SGRPI_policy_Min = r1_df.iloc[17, 13]
    
#    FEHC_R3_via_Excel = r3_df.iloc[18, 3:13].tolist()
#    FEHC_R2_via_Excel = r2_df.iloc[18, 3:13].tolist()
#    FEHC_R1_via_Excel = r1_df.iloc[18, 3:13].tolist()
#    FEHC_policy_Max = r1_df.iloc[18, 14]
#    FEHC_policy_Min = r1_df.iloc[18, 13]
    
#    XtaxEmp_R3_via_Excel = r3_df.iloc[19, 3:13].tolist()
#    XtaxEmp_R2_via_Excel = r2_df.iloc[19, 3:13].tolist()
#    XtaxEmp_R1_via_Excel = r1_df.iloc[19, 3:13].tolist()
#    XtaxRateEmp_policy_Max = r1_df.iloc[19, 14]
#    XtaxRateEmp_policy_Min = r1_df.iloc[19, 13]
#    XtaxEmp_policy_Min = XtaxRateEmp_policy_Min
#    XtaxEmp_policy_Max = XtaxRateEmp_policy_Max
    
#    SGMP_R3_via_Excel = r3_df.iloc[20, 3:13].tolist()
#    SGMP_R2_via_Excel = r2_df.iloc[20, 3:13].tolist()
#    SGMP_R1_via_Excel = r1_df.iloc[20, 3:13].tolist()
#    SGMP_policy_Max = r1_df.iloc[20, 14]
#    SGMP_policy_Min = r1_df.iloc[20, 13]
    
#    FWRP_R3_via_Excel = r3_df.iloc[21, 3:13].tolist()
#    FWRP_R2_via_Excel = r2_df.iloc[21, 3:13].tolist()
#    FWRP_R1_via_Excel = r1_df.iloc[21, 3:13].tolist()
#    FWRP_policy_Max = r1_df.iloc[21, 14]
#    FWRP_policy_Min = r1_df.iloc[21, 13]
    
#    FLWR_R3_via_Excel = r3_df.iloc[22, 3:13].tolist()
#    FLWR_R2_via_Excel = r2_df.iloc[22, 3:13].tolist()
#    FLWR_R1_via_Excel = r1_df.iloc[22, 3:13].tolist()
#    FLWR_policy_Max = r1_df.iloc[22, 14]
#    FLWR_policy_Min = r1_df.iloc[22, 13]
    
#    RMDR_R3_via_Excel = r3_df.iloc[23, 3:13].tolist()
#    RMDR_R2_via_Excel = r2_df.iloc[23, 3:13].tolist()
#    RMDR_R1_via_Excel = r1_df.iloc[23, 3:13].tolist()
#    RMDR_policy_Max = r1_df.iloc[23, 14]
#    RMDR_policy_Min = r1_df.iloc[23, 13]
    
#    RIPLGF_R3_via_Excel = r3_df.iloc[24, 3:13].tolist()
#    RIPLGF_R2_via_Excel = r2_df.iloc[24, 3:13].tolist()
#    RIPLGF_R1_via_Excel = r1_df.iloc[24, 3:13].tolist()
#    RIPLGF_policy_Max = r1_df.iloc[24, 14]
#    RIPLGF_policy_Min = r1_df.iloc[24, 13]
    
#    REFOREST_R3_via_Excel = r3_df.iloc[26, 3:13].tolist()
#    REFOREST_R2_via_Excel = r2_df.iloc[26, 3:13].tolist()
#    REFOREST_R1_via_Excel = r1_df.iloc[26, 3:13].tolist()
#    REFOREST_policy_Max = r1_df.iloc[26, 14]
#    REFOREST_policy_Min = r1_df.iloc[26, 13]
    
#    FTPEE_R3_via_Excel = r3_df.iloc[27, 3:13].tolist()
#    FTPEE_R2_via_Excel = r2_df.iloc[27, 3:13].tolist()
#    FTPEE_R1_via_Excel = r1_df.iloc[27, 3:13].tolist()
#    FTPEE_policy_Max = r1_df.iloc[27, 14]
#    FTPEE_policy_Min = r1_df.iloc[27, 13]
    
#    NEP_R3_via_Excel = r3_df.iloc[28, 3:13].tolist()
#    NEP_R2_via_Excel = r2_df.iloc[28, 3:13].tolist()
#    NEP_R1_via_Excel = r1_df.iloc[28, 3:13].tolist()
#    NEP_policy_Max = r1_df.iloc[28, 14]
#    NEP_policy_Min = r1_df.iloc[28, 13]
    
#    ISPV_R3_via_Excel = r3_df.iloc[29, 3:13].tolist()
#    ISPV_R2_via_Excel = r2_df.iloc[29, 3:13].tolist()
#    ISPV_R1_via_Excel = r1_df.iloc[29, 3:13].tolist()
#    ISPV_policy_Max = r1_df.iloc[29, 14]
#    ISPV_policy_Min = r1_df.iloc[29, 13]
    
#    CCS_R3_via_Excel = r3_df.iloc[30, 3:13].tolist()
#    CCS_R2_via_Excel = r2_df.iloc[30, 3:13].tolist()
#    CCS_R1_via_Excel = r1_df.iloc[30, 3:13].tolist()
#    CCS_policy_Max = r1_df.iloc[30, 14]
#    CCS_policy_Min = r1_df.iloc[30, 13]
    
#    DAC_R3_via_Excel = r3_df.iloc[31, 3:13].tolist()
#    DAC_R2_via_Excel = r2_df.iloc[31, 3:13].tolist()
#    DAC_R1_via_Excel = r1_df.iloc[31, 3:13].tolist()
#    DAC_policy_Max = r1_df.iloc[31, 14]
#    DAC_policy_Min = r1_df.iloc[31, 13]

    with open(path + "plot_var_list.pkl", "rb") as fp:  # Unpickling
        plot_var_list = pickle.load(fp)
    with open(path + "plot_var_list_10.pkl", "rb") as fp:  # Unpickling
        plot_var_list_10 = pickle.load(fp)


    Antarctic_ice_volume_in_1980 = 3e+07
    Arctic_ice_area_in_1980_km2 = 1.18874e+07
    C_in_atmosphere_in_1980 = 752.397
    C_in_the_form_of_CH4_in_atm_1980 = 2.79426
    CC_in_cold_ocean_0_to_100m_in_1980 = 2325.64
    UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre = 1e+06 / 12.01 * 1000
    Area_of_ocean_at_surface_361900_Gm2 = 361900
    Thickness_of_surface_water_box_100m = 100
    Fraction_of_ocean_classified_warm_surface = 0.8
    Fraction_of_ocean_classified_as_cold_surface = 1 - Fraction_of_ocean_classified_warm_surface
    UNIT_conversion_to_Gm3 = 1
    Volume_cold_ocean_0_to_100m = Area_of_ocean_at_surface_361900_Gm2 * Thickness_of_surface_water_box_100m * Fraction_of_ocean_classified_as_cold_surface * UNIT_conversion_to_Gm3
    Carbon_in_cold_ocean_0_to_100m_1850 = ( CC_in_cold_ocean_0_to_100m_in_1980 / UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre ) * Volume_cold_ocean_0_to_100m
    CC_in_cold_ocean_downwelling_100m_bottom_in_1980 = 2253.86
    Thickness_of_intermediate_water_box_800m = 800
    Thickness_of_deep_water_box_1km_to_bottom = 2800
    Volume_cold_ocean_downwelling_100m_to_bottom = Area_of_ocean_at_surface_361900_Gm2 * ( Thickness_of_intermediate_water_box_800m + Thickness_of_deep_water_box_1km_to_bottom ) * Fraction_of_ocean_classified_as_cold_surface * UNIT_conversion_to_Gm3
    Carbon_in_cold_ocean_trunk_100m_to_bottom_1850 = ( CC_in_cold_ocean_downwelling_100m_bottom_in_1980 / UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre ) * Volume_cold_ocean_downwelling_100m_to_bottom
    CC_ocean_deep_1km_to_bottom_in_1980 = 2232.12
    Volume_ocean_deep_1km_to_bottom = Area_of_ocean_at_surface_361900_Gm2 * Thickness_of_deep_water_box_1km_to_bottom * Fraction_of_ocean_classified_warm_surface * UNIT_conversion_to_Gm3
    Carbon_in_ocean_deep_1k_to_bottom_ocean_1850 = ( CC_ocean_deep_1km_to_bottom_in_1980 / UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre ) * Volume_ocean_deep_1km_to_bottom
    CC_in_ocean_upwelling_100m_to_1km_in_1980 = 2237.8
    Volume_ocean_upwelling_100m_to_1km = Area_of_ocean_at_surface_361900_Gm2 * Thickness_of_intermediate_water_box_800m * Fraction_of_ocean_classified_warm_surface * UNIT_conversion_to_Gm3
    Carbon_in_ocean_upwelling_100m_to_1km_1850 = ( CC_in_ocean_upwelling_100m_to_1km_in_1980 / UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre ) * Volume_ocean_upwelling_100m_to_1km
    C_in_sediment_initially = 3e+09
    CC_in_warm_ocean_0_to_100m_in_1980 = 2242.96
    Volume_warm_ocean_0_to_100m = Area_of_ocean_at_surface_361900_Gm2 * Thickness_of_surface_water_box_100m * Fraction_of_ocean_classified_warm_surface * UNIT_conversion_to_Gm3
    Carbon_in_warm_ocean_0_to_100m_1850 = ( CC_in_warm_ocean_0_to_100m_in_1980 / UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre ) * Volume_warm_ocean_0_to_100m
    Lifetime_of_capacity_in_1980 = 15
    Capacity_construction_time = 1.5
    Normal_bank_operating_margin = 0.015
    Normal_basic_bank_margin = 0.02
    Normal_corporate_credit_risk_margin = 0.02
    Cumulative_N_use_since_2020_in_1980 = 0
    Fossil_fuel_reserves_in_ground_at_initial_time_GtC = 5827.98
    Kappa = 0.3
    Lambdav = 1 - Kappa
    Goal_for_relative_inventory = 1
    Hours_worked_index_in_1980 = 1
    UNIT_conv_to_k2017pppUSD_pr_py = 1
    Glacial_ice_volume_in_1980 = 165694
    GRASS_area_burned_in_1980 = 1.741
    GRASS_area_harvested_in_1980 = 2.15683
    GRASS_Biomass_locked_in_construction_material_in_1980 = 1.99186
    GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM_in_1980 = 1086.88
    GRASS_area_deforested_in_1980 = 1.22174
    GRASS_Living_biomass_in_1980 = 381.43
    Greenland_ice_volume_in_1980 = 2.85e+06
    Heat_in_atmosphere_in_1980 = 1030.43
    Heat_in_ocean_deep_in_1980 = 1.95347e+06
    Heat_in_surface_in_1980 = 25034.6
    Incoming_solar_in_1850_ZJ_py = 5470.69
    Evaporation_as_fraction_of_incoming_solar_in_1850 = 0.289
    Sensitivity_of_evaporation_to_temp = 0.36
    Temp_surface_1850 = 286.815
    Heat_in_surface_in_1850_ZJ = 25000
    Conversion_heat_surface_to_temp = Temp_surface_1850 / Heat_in_surface_in_1850_ZJ
    Reference_temp_C = 10
    Water_content_of_evaporation_g_p_kg_per_ZJ_py = 0.001253
    Goal_for_inventory_coverage = 0.4
    N2O_in_atmosphere_MtN2O_in_1980 = 1082.4
    NF_area_burned_in_1980 = 2.09605
    NF_area_clear_cut_in_1980 = 3.99473
    NF_area_deforested_in_1980 = 0.129448
    NF_area_harvested_in_1980 = 0.897719
    NF_Biomass_locked_in_construction_material_in_1980 = 16.8741
    NF_Dead_biomass_litter_and_soil_organic_matter_SOM_in_1980 = 304.415
    NF_Living_biomass_in_1980 = 150.39
    Owner_power_in_1980 = 1
    People_considering_entering_the_pool_in_1980 = 2
    People_considering_leaving_the_pool_in_1980 = 2
    Size_of_public_capacity_in_1980 = 0.2
    Social_trust_in_1980 = 0.6
    One_year = 1
    TFP_in_1980 = 1
    TROP_area_burned_in_1980 = 1.64305
    TROP_area_clear_cut_in_1980 = 0.467813
    TROP_area_deforested_in_1980 = 5.97649
    TROP_area_harvested_in_1980 = 0.24296
    TROP_Biomass_locked_in_construction_material_in_1980 = 44.963
    TROP_Dead_biomass_litter_and_soil_organic_matter_SOM_in_1980 = 158.789
    TROP_Living_biomass_in_1980 = 379.797
    TUNDRA_area_burned_in_1980 = 1.8566
    TUNDRA_area_harvested_in_1980 = 2.5
    TUNDRA_Biomass_locked_in_construction_material_in_1980 = 1.92761
    TUNDRA_Dead_biomass_litter_and_soil_organic_matter_SOM_in_1980 = 1207.56
    TUNDRA_area_deforested_in_1980 = 0
    TUNDRA_Living_biomass_in_1980 = 391.84
    wind_and_PV_el_cap_in_1980 = 0.1
    Delivery_delay_index_in_1980 = 1
    Implemented_spending_on_GL_in_1980 = 0
    Worker_power_scaling_factor = 60
    Worker_power_scaling_factor_reference = 0.53
    Round3_start = 2060
    Round2_start = 2040
    Policy_start_year = 2025
    SoE_of_social_trust_on_reform = 0.1
    Scaling_factor_for_amplitude_in_RoC_in_living_conditions_index = 20
    Scaling_factor_of_eff_of_wealth_on_social_tension = 1
    Strength_of_the_impact_of_social_tension_on_reform_willingness = 0.3
    SoE_of_unemployment_ratio_on_WSO = 0.01
    Societal_unemployment_rate_norm = 0.06
    UNIT_conv_to_make_exp_dmnl = 1
    Max_age = 100
    Years_between_60_and_max_age = 40
    UNIT_conv_to_kUSDpp = 1
    GL_investment_fraction = 0.4
    Income_tax_rate_ie_fraction_for_workers_before_policies = 0.3
    Worker_resistance_initially = 1 - Owner_power_in_1980
    Access_to_electricity_L = 0.999
    Access_to_electricity_k = 0.5
    UNIT_conv_to_make_base_dmnless = 1
    Access_to_electricity_x0 = 3
    Access_to_electricity_min = - 0.01
    cereal_dmd_CN_a = 30.3753
    cereal_dmd_CN_b = 121.165
    UNIT_conv_to_kg_crop_ppy = 1
    Strength_of_inequality_effect_on_energy_TA = 2
    SDG4_a = 1.3463
    Income_tax_rate_ie_fraction_owners_before_policies = 0.22
    TOW_UNIT_conv_to_pa = 1
    Fossil_use_pp_NOT_for_El_gen_CN_a = 0
    Fossil_use_pp_NOT_for_El_gen_CN_b = 0.7
    UNIT_conv_to_toe_py = 1
    UNIT_conv_toe_to_Mtoe = 1
    wind_and_PV_capacity_factor = 0.1
    Hours_per_year = 8760
    UNIT_conv_GWh_and_TWh = 1 / 1000
    Actual_GH_share = 0
    kWh_per_kgH = 55
    UNIT_conv_to_TWh_per_Mth = 1
    TWh_per_MtH = kWh_per_kgH * UNIT_conv_to_TWh_per_Mth
    toe_per_tH = 0.338524
    Fraction_of_Fossil_fuel_for_NON_El_use_that_cannot_be_electrified = 0.05
    UNIT_conv_to_Gtoe = 1 / 1000
    CO2_emi_from_IPC_2_CN_L = 2
    CO2_emi_from_IPC_2_CN_k = 0.25
    CO2_emi_from_IPC_2_CN_x0 = 10
    Ctax_UNIT_conv_to_GtCO2_pr_yr = 1
    UNIT_conv_to_G2017pppUSD = 1
    Ref_Future_TLTL_leakage = 0.2
    Fraction_of_govt_income_transferred_to_workers_a = 0.45
    Fraction_of_govt_income_transferred_to_workers_b = - 0.0424405
    Fraction_of_govt_income_transferred_to_workers_c = 1.62454
    Normal_Govt_payback_period_to_PL = 20
    Long_term_risk_margin = 0.015
    Fraction_set_aside_to_service_loans = 0.9
    Fraction_of_avail_cash_used_to_meet_private_lender_obligations = 0.9
    UNIT_conv_to_pa = 1
    Normal_time_to_payback_public_debt = 30
    Govt_consumption_fraction = 0.3
    UNIT_conv_to_make_base_and_ln_dmnl = 1
    SDG4_b = 9.734
    Strength_of_FEHC_mult_on_years_of_schooling = 0.1
    SDG4_threshold_red = 13
    SDG4_threshold_green = 15
    SDG5_threshold_red = 0.4
    SDG5_threshold_green = 0.48
    Strength_of_Effect_of_empowerment_on_speed_of_food_TA = 0.1
    UNIT_conv_from_kg_to_Mt = 1e+09
    UNIT_conv_btw_p_and_Mp = 1e+06
    red_meat_dmd_PA_a = 11.878
    red_meat_dmd_PA_b = 0.0945
    red_meat_dmd_SA_a = 1.49475
    red_meat_dmd_SA_b = - 0.6628
    red_meat_dmd_SA_c = 2.5
    UNIT_conv_to_kg_red_meat_ppy = 1
    UNIT_conv_kgrmeat_and_Mtrmea = 1e+09
    UNIT_conv_red_meat = 1
    white_meat_dmd_CN_a = 19.1013
    white_meat_dmd_CN_b = 2.61946
    UNIT_conv_to_kg_white_meat_ppy = 1
    UNIT_conv_kgwmeat_and_Mtwmeat = 1e+09
    UNIT_conv_white_meat = 1
    UNIT_conv_meat_to_feed = 1
    Reference_crop_import_in_1980 = 0
    Soil_quality_in_1980 = 1
    Soil_quality_of_regenerative_cropland = 1.2
    SoE_of_CO2_on_yield = 0.2
    C_in_atmosphere_in_1850_GtC = 600
    CO2_concentration_ppm_in_1850 = 284.725
    Conversion_constant_GtC_to_ppm = C_in_atmosphere_in_1850_GtC / CO2_concentration_ppm_in_1850
    CO2_concentration_2020 = 426
    Warm_surface_water_volume = Volume_warm_ocean_0_to_100m
    Intermediate_upwelling_water_volume_100m_to_1km = Volume_ocean_upwelling_100m_to_1km
    Surface_ocean_warm_volume = Warm_surface_water_volume + Intermediate_upwelling_water_volume_100m_to_1km
    Temp_surface_anfang_less_zero_k = Temp_surface_1850 - 273.15
    Pressure_adjustment_surface_pct = 0.2
    UNIT_conversion_Gm3_to_km3 = 1
    Ocean_surface_area_km2 = 0.3619 * 1e+09
    UNIT_Conversion_from_km3_to_km2 = 1
    Cold_surface_water_volume = Volume_cold_ocean_0_to_100m
    Cold_water_volume_downwelling = Volume_cold_ocean_downwelling_100m_to_bottom
    Deep_water_volume_1km_to_4km = Volume_ocean_deep_1km_to_bottom
    Deep_ocean_cold_volume = Cold_surface_water_volume + Cold_water_volume_downwelling + Deep_water_volume_1km_to_4km
    Temp_ocean_deep_in_1850_C = 4
    Temp_ocean_deep_in_1850_in_K = Temp_ocean_deep_in_1850_C + 273.15
    Heat_in_ocean_deep_in_1850_ZJ = 1.9532e+06
    Conversion_constant_heat_ocean_deep_to_temp = Temp_ocean_deep_in_1850_in_K / Heat_in_ocean_deep_in_1850_ZJ
    Pressure_adjustment_deep_pct = 1
    UNIT_conversion_from_km_to_m = 1000
    Avg_flatness_of_worlds_coastline = 0.65
    sea_level_rise_2020 = 0.2725
    temp_in_2020 = 1.09922
    expSoE_of_ed_on_agri_yield = 0.1
    SoE_of_relative_wealth_on_env_damage = 0.01
    Time_for_abandoned_agri_land_to_become_forest = 300
    Grazing_land_EC_a = 529.5
    UNIT_conv_meat_to_dmnl = 1
    Grazing_land_EC_b = - 0.031
    Grazing_land_LA_L = 418.8
    Grazing_land_LA_k = 0.17169
    Grazing_land_LA_x = 0.3264
    Grazing_land_LA_L2 = - 170
    Grazing_land_LA_k2 = - 0.0313754
    Grazing_land_LA_x2 = 49.3867
    Grazing_land_ME_L = 320
    Grazing_land_ME_k = 0.309
    Grazing_land_ME_x = - 1.27
    Grazing_land_ME_min = 0
    Grazing_land_PA_L = 271
    Grazing_land_PA_k = - 0.42
    Grazing_land_PA_x = 16.11
    Grazing_land_PA_min = 250
    Grazing_land_SA_a = 23.72
    Grazing_land_SA_b = - 0.109
    Grazing_land_SE_a = 0.48
    Grazing_land_SE_b = 14.721
    UNIT_conv_to_Mha = 1
    Fraction_of_grazing_land_gap_closed_from_acgl = 1
    Fraction_of_abandoned_agri_land_developed_for_urban_land = 0.03
    pb_Ocean_acidification_green_threshold = 8.15
    UNIT_conversion_C_to_pH = 1
    UNIT_conversion_km3_to_Gm3 = 1
    Volume_of_total_ocean_Gm3 = Volume_cold_ocean_0_to_100m + Volume_cold_ocean_downwelling_100m_to_bottom + Volume_ocean_deep_1km_to_bottom + Volume_ocean_upwelling_100m_to_1km + Volume_warm_ocean_0_to_100m
    Frac_vol_warm_ocean_0_to_100m_of_total = Volume_warm_ocean_0_to_100m / Volume_of_total_ocean_Gm3
    UNIT_conversion_ymoles_p_litre_to_dless = 1
    Frac_vol_cold_ocean_0_to_100m_of_total = Volume_cold_ocean_0_to_100m / Volume_of_total_ocean_Gm3
    UNIT_conv_to_GtCO2_pr_yr = 1
    Nuclear_gen_cap_EU_s = 25
    Nuclear_gen_cap_EU_g = 100
    Nuclear_gen_cap_EU_h = 31
    Nuclear_gen_cap_EU_k = 16
    UNIT_conv_to_GW = 1
    Nuclear_capacity_factor = 0.91
    UNIT_conv_to_kWh_ppp = 1
    Inequality_considered_normal_in_1980 = 1.1
    GRASS_Ref_historical_deforestation_pct_py = 0.1
    GRASS_historical_deforestation_pct_py = ( GRASS_Ref_historical_deforestation_pct_py / 100 )
    Fraction_GRASS_being_deforested_1_py = GRASS_historical_deforestation_pct_py
    GRASS_fraction_of_DeadB_and_SOM_being_destroyed_by_deforesting = 1
    GRASS_Living_biomass_in_1850 = 310
    Use_of_GRASS_biomass_for_energy_in_1850_pct = 1
    Use_of_GRASS_for_energy_in_2000_GtBiomass = GRASS_Living_biomass_in_1850 * Use_of_GRASS_biomass_for_energy_in_1850_pct / 100
    UNIT_conv_to_Bp = 1000
    Population_2000_bn = 6.187
    UNIT_conversion_1_py = 1
    GRASS_living_biomass_densitiy_in_1850_tBiomass_pr_km2 = 14500
    Sensitivity_of_biomass_new_growth_to_CO2_concentration = 1.5
    Slope_of_temp_eff_on_potential_biomass_per_km2 = - 0.5
    UNIT_conversion_GtBiomass_py_to_Mkm2_py = 1000
    GRASS_fraction_of_DeadB_and_SOM_being_destroyed_by_energy_harvesting = 0.1
    GRASS_runoff_time = 2000
    Slope_temp_eff_on_fire_incidence = 0.1
    GRASS_Normal_fire_incidence_fraction_py = 1
    GRASS_fraction_of_DeadB_and_SOM_destroyed_by_natural_fires = 0
    GRASS_Time_to_decompose_undisturbed_dead_biomass_yr = 1000
    NF_Ref_historical_deforestation_pct_py = 0.02
    NF_historical_deforestation_pct_py = ( NF_Ref_historical_deforestation_pct_py / 100 )
    NF_fraction_of_DeadB_and_SOM_being_destroyed_by_deforesting = 1
    NF_DeadB_and_SOM_densitiy_in_1850 = 27500
    NF_Living_biomass_in_1850 = 115
    Use_of_NF_biomass_for_energy_in_1850_pct = 1.09
    Use_of_NF_for_energy_in_2000_GtBiomass = NF_Living_biomass_in_1850 * Use_of_NF_biomass_for_energy_in_1850_pct / 100
    NF_living_biomass_densitiy_in_1850_tBiomass_pr_km2 = 7500
    NF_fraction_of_DeadB_and_SOM_being_destroyed_by_energy_harvesting = 0.1
    NF_runoff_time = 2000
    NF_fraction_of_DeadB_and_SOM_being_destroyed_by_clear_cutting = 0.5
    NF_Normal_fire_incidence_fraction_py = 0.7
    NF_fraction_of_DeadB_and_SOM_destroyed_by_natural_fires = 0
    NF_Time_to_decompose_undisturbed_dead_biomass_yr = 250
    TROP_Ref_historical_deforestation = 1
    Time_at_which_human_deforestation_is_stopped = 3000
    TROP_fraction_of_DeadB_and_SOM_being_destroyed_by_deforesting = 1
    TROP_DeadB_and_SOM_densitiy_in_1850_tBiomass_pr_km2 = 8500
    TROP_Living_biomass_in_1850 = 370
    Use_of_TROP_biomass_for_energy_in_1850_pct = 0.07
    Use_of_TROP_for_energy_in_2000_GtBiomass = TROP_Living_biomass_in_1850 * Use_of_TROP_biomass_for_energy_in_1850_pct / 100
    UNIT_conversion_to_yr = 1
    TROP_living_biomass_densitiy_in_1850_tBiomass_pr_km2 = 16500
    TROP_clear_cut_fraction = 0.5
    TROP_fraction_of_DeadB_and_SOM_being_destroyed_by_energy_harvesting = 0.1
    TROP_runoff_time = 2000
    TROP_fraction_of_DeadB_and_SOM_being_destroyed_by_clear_cutting = 0.5
    TROP_Normal_fire_incidence = 0.3
    TROP_fraction_of_DeadB_and_SOM_destroyed_by_natural_fires = 0
    TROP_Time_to_decompose_undisturbed_dead_biomass_yr = 24
    SoE_of_env_damage_indicator = - 0.4
    El_use_pp_US_s = 9.3
    El_use_pp_US_g = 5
    El_use_pp_US_h = 55
    El_use_pp_US_k = 18
    UNIT_conv_to_MWh_ppy = 1
    UNIT_conv_to_TWh = 1
    Life_of_fossil_el_gen_cap = 40
    wind_and_PV_construction_time = 1.5
    Lifetime_of_wind_and_PV_el_cap = 40
    Nitrogen_use_AF_L = 22.5
    Nitrogen_use_AF_k = 0.62
    UNIT_conv_to_make_N_use_dmnl = 1
    Nitrogen_use_AF_x0 = 4.4
    Nitrogen_use_CN_b = 164
    Nitrogen_use_CN_a = 200
    Nitrogen_use_SA_a = 65.3
    Nitrogen_use_SA_b = 25
    Fraction_of_N_use_saved_through_regenerative_practice = 0.9
    UNIT_conv_kgN_to_Nt = 1 / 1000
    Slope_of_Indicated_effect_of_worker_share_of_output_on_capital_labour_ratio = 2
    UNIT_conv_to_Mp = 1000
    Addl_time_to_shift_govt_expenditure = 3
    Value_of_anthropogenic_aerosol_emissions_during_2015 = 0.225
    Cohort_duration_is_5_yrs = 5
    Urban_aerosol_concentration_in_2020 = 43.5
    pb_Urban_aerosol_concentration_green_threshold = 20
    Albedo_Antarctic = 0.7
    Albedo_BARREN_normal = 0.17
    Albedo_DESERT_normal = 0.24
    Albedo_glacier = 0.4
    Albedo_GRASS_burnt = 0.08
    Albedo_GRASS_deforested = 0.3
    Albedo_GRASS_normal_cover = 0.16
    Albedo_Greenland = 0.7
    Area_of_earth_m2 = 5.1e+14
    UNIT_conversion_m2_to_Mkm2 = 1e+12
    Area_of_earth_Mkm2 = Area_of_earth_m2 / UNIT_conversion_m2_to_Mkm2
    Fraction_of_earth_surface_as_ocean = 0.7
    Urban_area_fraction_2000 = 0.004
    Avg_thickness_Antarctic_km = 2.14
    Avg_thickness_glacier_km = 0.23
    UNIT_conversion_km3_div_km_to_km2 = 1
    Avg_thickness_Greenland_km = 1.35
    UNIT_conversion_km2_to_Mkm2 = 1 / 1e+06
    Area_of_land_Mkm2 = Area_of_earth_Mkm2 * ( 1 - Fraction_of_earth_surface_as_ocean )
    Conversion_Million_km2_to_km2 = 1e-06
    Albedo_NF_normal_cover = 0.08
    Albedo_NF_burnt = 0.13
    Albedo_NF_deforested = 0.18
    Albedo_TROP_normal_cover = 0.14
    Albedo_TROP_burnt = 0.1
    Albedo_TROP_deforested = 0.168
    Albedo_TUNDRA_normal_cover = 0.23
    Albedo_TUNDRA_burnt = 0.23
    Albedo_TUNDRA_deforested = 0.23
    Albedo_URBAN_normal = 0.15
    Albedo_URBAN = Albedo_URBAN_normal
    Arctic_ice_albedo_1850 = 0.7
    Ocean_area_km2 = 5.1e+08 * 0.7
    Open_ocean_albedo = 0.065
    UNIT_conv_kgac_to_kg = 1
    UNIT_conv_CO2_to_C = 3.667
    UNIT_conversion_for_CO2_from_CO2e_to_C = 12 / 44
    UNIT_conv_Mtrmeat = 1
    CH4_emi_from_energy_EU_a = 14
    CH4_emi_from_energy_EU_b = - 0.036
    CH4_emi_from_energy_US_a = 18
    CH4_emi_from_energy_US_b = - 0.008
    CH4_emi_from_energy_EC_a = 11.39
    UNIT_conv_to_make_fossil_fuels_dmnl = 1000
    CH4_emi_from_energy_EC_b = 18.271
    CH4_emi_from_waste_AF_a = 1.2596
    CH4_emi_from_waste_AF_b = 0.9904
    CH4_emi_from_waste_CN_a = 7.09
    CH4_emi_from_waste_CN_b = - 0.071
    UNIT_conversion_from_MtCH4_to_GtC = 1 / ( 1000 / 12 * 16 )
    Global_Warming_Potential_CH4 = 25
    UNIT_conversion_for_CH4_from_CO2e_to_C = 1 / ( 16 / 12 * Global_Warming_Potential_CH4 )
    N2O_emi_from_agri_AF_a = 0.5301
    UNIT_conv_to_MtN = 1 / 1000
    UNIT_conv_to_dmnl_for_MtNmeat = 1
    UNIT_conv_to_MtN_from_meat = 1
    UNIT_conv_to_make_LN_dmnl = 1
    N2O_emi_from_agri_AF_b = - 0.579
    N2O_emi_X_agri_US_a = 0.9042
    N2O_emi_X_agri_US_b = - 0.012
    N2O_emi_X_agri_EU_a = 1.8178
    N2O_emi_X_agri_EU_b = - 0.047
    N2O_emi_X_agri_CN_a = 0.4272
    N2O_emi_X_agri_CN_b = - 0.2683
    N2O_emi_X_agri_SA_a = 0.1257
    N2O_emi_X_agri_SA_b = 0.0234
    Global_Warming_Potential_N20 = 298
    UNIT_conversion_Gt_to_Mt = 1000
    Kyoto_Fluor_Global_Warming_Potential = 7000
    UNIT_conversion_Gt_to_kt = 1e+06
    Montreal_Global_Warming_Potential = 10000
    N2O_natural_emissions = 9
    All_region_max_cost_estimate_empowerment_PES = 1000
    All_region_max_cost_estimate_energy_PES = 1000
    All_region_max_cost_estimate_food_PES = 1000
    All_region_max_cost_estimate_inequality_PES = 4000
    All_region_max_cost_estimate_poverty_PES = 1000
    Normal_k = 0.3
    JR_sINEeolLOK_lt_0 = - 0.45
    Strength_of_inequality_proxy = 6
    UNIT_conv_to_dmnl = 1
    SDG1_threshold_red = 0.13
    SDG1_threshold_green = 0.05
    SDG2_a = 0.42
    SDG2_b = - 0.747
    SDG2_threshold_red = 0.07
    SDG2_threshold_green = 0.03
    Weight_disposable_income = 1
    Disposable_income_threshold_for_wellbeing = 8
    Weight_el_use = 1
    El_use_wellbeing_a = 4
    El_use_wellbeing_b = 1
    Basic_el_use = 2
    Weight_food = 1
    stdev = 0.4
    UNIT_conv_kgwmeat_to_kg = 1
    Healthy_white_meat_consumption = 30
    mean_value = 1
    Weight_on_white_meat = 0.5
    UNIT_conv_kgrmeat_to_kg = 1
    Healthy_red_meat_consumption = 30
    Weight_on_red_meat = 0.25
    Healthy_all_crop_consumption = 800
    Weight_on_crops = 1
    Sum_of_food_weights = Weight_on_crops + Weight_on_red_meat + Weight_on_white_meat
    Weight_inequality = 0.1
    Weight_population_in_job_market = 1
    Slope_of_wellbeing_from_fraction_of_people_outside_of_labor_pool = 3
    Weight_public_spending = 1
    UNIT_conv_to_k217pppUSD_ppy = 1
    Satisfactory_public_spending = 0.22
    Sum_weights_living_conditions = Weight_disposable_income + Weight_el_use + Weight_food + Weight_inequality + Weight_population_in_job_market + Weight_public_spending
    Weight_on_living_conditions = 0.65
    Weight_on_env_conditions = 1 - Weight_on_living_conditions
    Weight_on_physical_conditions = 0.75
    SoE_of_Wellbeing_from_social_tension = - 2
    Social_tension_index_in_1980 = 1
    SDG3_threshold_red = 1.2
    SDG3_threshold_green = 1.4
    Safe_water_cn_L = 0.999
    Safe_water_cn_k = 1
    Safe_water_cn_x0 = 0
    Safe_water_cn_min = - 0.02
    Safe_water_rest_L = 0.999
    Safe_water_rest_k = 0.2
    Safe_water_rest_x0 = 10
    Safe_water_rest_min = - 0.02
    SDG6a_threshold_red = 0.8
    SDG6a_threshold_green = 0.95
    Safe_sanitation_L = 0.999
    Safe_sanitation_k = 0.15
    Safe_sanitation_x0 = 12
    Safe_sanitation_min = - 0.02
    SDG6b_threshold_red = 0.65
    SDG6b_threshold_green = 0.9
    SDG_7_threshold_red = 0.9
    SDG_7_threshold_green = 0.98
    Normal_consumer_credit_risk_margin = 0
    Worker_drawdown_period = 5
    Fraction_by_law_or_custom_left_for_surviving = 0.5
    Workers_payback_period = 3
    SDG_8_threshold_red = 15
    SDG_8_threshold_green = 25
    UNIT_conv_to_tCO2_pr_USD = 1000
    SDG_9_threshold_green = 0
    SDG_9_threshold_red = 0.1
    SDG_10_threshold_green = 0.6
    SDG_10_threshold_red = 0.4
    UNIT_conv_to_t_ppy = 1000
    SDG_11_threshold_green = 0
    SDG_11_threshold_red = 2
    UNIT_conv_to_kgN = 1000
    SDG12_global_green_threshold = 62
    SDG12_global_red_threshold = 82
    SDG_13_threshold_green = 1
    SDG_13_threshold_red = 1.5
    SDG_14_threshold_green = 8.15
    SDG_14_threshold_red = 8.1
    SDG_15_threshold_green = 25
    SDG_15_threshold_red = 15
    SDG_16_threshold_green = 15
    SDG_16_threshold_red = 5
    SDG_17_threshold_green = 1
    SDG_17_threshold_red = 0.75
    Annual_reduction_in_UAC_TLTL = 0.2
    UNIT_conv_to_1_per_yr = 1
    Time_at_which_govt_public_debt_is_cancelled = 2025
    Public_Govt_debt_cancelling_spread = 2
    Nbr_of_policies = 30
    Annual_reduction_in_UAC_GL = 2
    Slope_of_Worker_share_of_output_with_unemployment_effect_on_available_capital = - 2.9
    Slope_of_Eff_of_dmd_imbalance_on_flow_of_available_capital = 1
    Dmd_imbalance_in_1980 = 1
    Worker_consumption_fraction = 0.85
    Foreign_capital_inflow = 0
    Time_to_melt_or_freeze_antarctic_ice_at_the_reference_delta_temp = 18000
    Effective_time_to_melt_or_freeze_antarctic_ice_at_the_reference_delta_temp = Time_to_melt_or_freeze_antarctic_ice_at_the_reference_delta_temp
    Slope_temp_vs_antarctic_ice_melting = 1.2
    SCALE_converter_zero_C_to_K = 273.15
    UNIT_conversion_Celsius_to_Kelvin_C_p_K = 1
    Ref_temp_difference_for_antarctic_ice_melting_3_degC = 3
    Heat_in_atmosphere_in_1850_ZJ = 1025.67
    Land_area_km2 = 5.1e+08 * 0.3
    Atmos_heat_used_for_melting_Initially_1_py = 0
    Ocean_heat_used_for_melting_Initially_1_py = 0
    UNIT_Conversion_from_km3_p_kmy_to_Mkm2_py = 1e-06
    GtIce_vs_km3 = 0.9167
    Densitiy_of_water_relative_to_ice = 0.916
    Human_aerosol_forcing_1_is_ON_0_is_OFF = 1
    Conversion_of_anthro_aerosol_emissions_to_forcing = - 1.325
    Time_for_abandoned_urban_land_to_become_fallow = 100
    Time_to_develop_urban_land_from_abandoned_land = 2
    UNIT_conversion_m2_to_km2 = 1e+06
    Arctic_ice_area_max_km2 = ( Area_of_earth_m2 / UNIT_conversion_m2_to_km2 - Land_area_km2 )
    Time_to_melt_Arctic_ice_at_the_reference_delta_temp = 500
    Effective_time_to_melt_Arctic_ice_at_the_reference_delta_temp = Time_to_melt_Arctic_ice_at_the_reference_delta_temp
    Slope_temp_vs_Arctic_ice_melting = 0.65
    Ref_temp_difference_for_Arctic_ice_melting = 0.4
    Arctic_surface_temp_delay_yr = 15
    Area_covered_by_high_clouds_in_1980 = 0.214448
    Sensitivity_of_high_cloud_coverage_to_temp_normal = 50
    Logistics_curve_param_c = 20
    Logistics_curve_param_k = 0.1
    Logistics_curve_param_shift = 2000
    Area_covered_by_low_clouds_in_1980 = 0.431994
    Sensitivity_of_low_cloud_coverage_to_temp = 58
    Area_equivalent_of_1km_linear_retreat_km2 = 17500
    Melting_of_permafrost_at_all_depths_at_4_deg_C_temp_diff_km_py = 0.71
    UNIT_conversion_to_km2_py = 1
    Area_equivalent_of_linear_retreat_km2_py = Melting_of_permafrost_at_all_depths_at_4_deg_C_temp_diff_km_py * Area_equivalent_of_1km_linear_retreat_km2 * UNIT_conversion_to_km2_py
    Time_to_melt_or_freeze_glacial_ice_at_the_reference_delta_temp = 500
    Effective_time_to_melt_glacial_ice_at_the_reference_delta_temp = Time_to_melt_or_freeze_glacial_ice_at_the_reference_delta_temp
    Slope_temp_vs_glacial_ice_melting = 1
    Ref_temp_difference_for_glacial_ice_melting_1_degC = 3
    Heat_needed_to_melt_1_km3_of_ice_ZJ = 0.0003327
    UNIT_conversion_1_p_km3 = 1
    UNIT_conversion_GtIce_to_ZJ_melting = 1
    Fraction_of_heat_needed_to_melt_antarctic_ice_coming_from_air = 0.6
    Time_to_melt_greenland_ice_at_the_reference_delta_temp = 4000
    Effective_time_to_melt_greenland_ice_at_the_reference_delta_temp = Time_to_melt_greenland_ice_at_the_reference_delta_temp
    Slope_temp_vs_greenland_ice_melting = 0.1
    Ref_temp_difference_for_greenland_ice_melting_C = 1
    Average_thickness_arctic_ice_km = 0.0025
    UNIT_conversion_km2_times_km_to_km3 = 1
    Fraction_of_heat_needed_to_melt_arctic_ice_coming_from_air = 0.5
    Avg_amount_of_C_in_the_form_of_CH4_per_km2 = 4.8e-05
    Slope_btw_temp_and_permafrost_melting_or_freezing_base = 1
    Slope_btw_temp_and_permafrost_melting_or_freezing_sensitivity = 1
    Ref_temp_difference_4_degC = 4
    Avg_depth_of_permafrost_km = 0.1
    Heat_gained_or_needed_to_freeze_or_unfreeze_1_km3_permafrost_ZJ_p_km3 = 0.0001717
    Fraction_of_C_released_from_permafrost_released_as_CH4_dmnl = 0.125
    UNIT_conv_to_y = 1
    Conversion_ymoles_per_kg_to_pCO2_yatm = 0.127044
    Conversion_of_volcanic_aerosol_forcing_to_volcanic_aerosol_emissions = - 1
    Future_volcanic_eruptions_1_is_ON_0_is_OFF = 0
    NEvt_2a_Volcanic_eruptions_in_the_future_VAEs_first_future_pulse = 2025
    VAES_pulse_duration = 4
    VAES_puls_repetition = 30
    VAES_pulse_height = 1
    Conversion_of_volcanic_aerosol_emissions_to_CO2_emissions_GtC_pr_VAE = 2.8
    Emissivity_surface = 1
    Stephan_Boltzmann_constant = 5.67037e-08
    Seconds_per_yr = 60 * 60 * 24 * 365
    UNIT_conversion_W_to_ZJ_p_sec = 1
    Zetta = 1e+21
    UNIT_conversion_W_p_m2_earth_to_ZJ_py = ( Seconds_per_yr * Area_of_earth_m2 ) * UNIT_conversion_W_to_ZJ_p_sec / Zetta
    Emissivity_atm = 1
    Temp_atm_1850 = 274.31
    Conversion_heat_atm_to_temp = Temp_atm_1850 / Heat_in_atmosphere_in_1850_ZJ
    Biocapacity_reference = 1.2e+07
    UNIT_conv_to_Mha_footprint = 1000
    pb_Biodiversity_loss_green_threshold = 0.4
    Net_marine_primary_production_in_1850 = 0.4
    Carbon_in_top_ocean_layer_1850 = Carbon_in_cold_ocean_0_to_100m_1850 + Carbon_in_warm_ocean_0_to_100m_1850
    Concentration_of_C_in_ocean_top_layer_in_1850 = Carbon_in_top_ocean_layer_1850 / ( Volume_cold_ocean_0_to_100m + Volume_warm_ocean_0_to_100m )
    Slope_of_efffect_of_acidification_on_NMPP = 5
    Frac_vol_cold_ocean_downwelling_of_total = Volume_cold_ocean_downwelling_100m_to_bottom / Volume_of_total_ocean_Gm3
    ph_in_cold_water_in_1980 = 8.30948
    Slope_Effect_Temp_on_NMPP = 2
    birth_rate_a_CN = 0.0262464
    birth_rate_b_CN = 0.00216569
    birth_rate_c_CN = - 0.190456
    birth_rate_d_CN = - 0.95
    UNIT_conv_to_make_the_bell_shaped_birth_rate_formula_have_units_of_1_pr_y = 1
    conversion_factor_CH4_Gt_to_ppb = 468
    LW_radiation_fraction_blocked_by_other_GHG_in_1850 = 0.0398
    Slope_btw_Kyoto_Fluor_ppt_and_blocking_multiplier = 0.3
    Conversion_from_Kyoto_Fluor_amount_to_concentration_ppt_p_kt = 0.04
    Kyoto_Fluor_concentration_in_1970_ppt = 9.32074
    Slope_btw_Montreal_gases_ppt_and_blocking_multiplier = 0.3
    Conversion_from_Montreal_gases_amount_to_concentration_ppt_p_kt = 0.04
    Montreal_gases_concentration_in_1970_ppt = 262.353
    Slope_btw_N2O_ppb_and_blocking_multiplier = 0.1
    UNIT_Conversion_from_N2O_amount_to_concentration_ppb_p_MtN2O = 0.305
    Model_N2O_concentration_in_1850_ppb = 274.5
    LW_LO_cloud_radiation_reference_in_1980 = 20
    LW_HI_cloud_radiation_reference_in_1980 = 7.9
    pct_of_GDP_budgeted_for_GL = 0.02
    expSoE_of_ed_on_cost_of_TAs = 3
    Nbr_of_relevant_energy_policies = 5
    Nbr_of_relevant_food_policies = 5
    Nbr_of_relevant_inequality_policies = 9
    Nbr_of_relevant_empowerment_policies = 3
    Nbr_of_relevant_poverty_policies = 9
    Time_to_reach_C_equilibrium_between_atmosphere_and_ocean = 90
    UNIT_conversion_GtC_to_MtC = 1000
    Carbon_per_biomass = 0.5
    TUNDRA_runoff_time = 2000
    Time_for_agri_land_to_become_abandoned = 2
    Fraction_of_cropland_developed_for_urban_land = 0.01
    GL_private_investment_fraction = 0.1
    expSoE_of_ed_on_cost_of_new_capacity = 0.075
    Frac_vol_deep_ocean_of_total = Volume_ocean_deep_1km_to_bottom / Volume_of_total_ocean_Gm3
    Frac_vol_ocean_upwelling_of_total = Volume_ocean_upwelling_100m_to_1km / Volume_of_total_ocean_Gm3
    Time_in_cold = 6.51772
    Time_in_trunk = 234.638
    Time_in_deep = 739.89
    Time_in_intermediate_yr = 211.397
    Time_in_warm = 26.227
    Natural_CH4_emissions = 0.19
    CH4_halflife_in_atmosphere = 7.3
    SoE_of_Inventory_on_RoC_of_ddx = - 0.2
    Sufficient_relative_inventory = 1
    Max_FOPOLM = 0.2
    Half_life_of_tech_progress_in_non_energy_footprint = 120
    GenEq_cn_a = 0.4314
    GenEq_cn_b = - 0.095
    GenEq_ec_a = 0.0152
    GenEq_ec_b = 0.3476
    GenEq_me_a = 0.0003
    GenEq_me_b = 0.1032
    GenEq_sa_la_af_a = 0.06
    GenEq_sa_la_af_b = 0.15
    GenEq_se_eu_pa_us_a = 0.0021
    GenEq_se_eu_pa_us_b = 0.241
    Time_to_change_GE = 10
    Strength_of_owner_reaction_to_worker_resistance = 0.05
    Slope_of_RoC_of_people_considering_entering_the_labor_pool = - 1
    Slope_of_RoC_of_people_considering_leaving_the_labor_pool = 1
    SoE_of_industrialization_on_RoC_in_TFP = 0
    Size_of_agri_sector_a = 1
    Size_of_agri_sector_b = 37
    Size_of_agri_sector_c = 5
    Size_of_tertiary_sector_lim = 80
    Size_of_tertiary_sector_a = 40
    Size_of_tertiary_sector_c = 20
    SoE_of_inflation_rate_on_indicated_signal_rate = 1.4
    SoE_of_unemployment_rate_on_indicated_signal_rate = - 1.3
    Signal_rate_adjustment_time = 0.1
    Reference_public_spending_fraction = 0.3
    Strength_of_Effect_of_gender_inequality_on_social_trust = 0.1
    Strength_of_Effect_of_schooling_on_social_trust = 0.1
    Time_to_change_social_trust = 10
    Strength_of_worker_reaction_to_owner_power_normal = 0.075
    Strength_of_inequality_effect_on_food_TA = 2
    Strength_of_Effect_of_TAs_on_inequality = 0.1
    GRASS_Avg_life_of_building_yr = 10
    GRASS_Fraction_of_construction_waste_burned_0_to_1 = 0.5
    NF_Avg_life_of_building_yr = 20
    NF_Fraction_of_construction_waste_burned_0_to_1 = 0.5
    TROP_Avg_life_of_building_yr = 20
    TROP_Fraction_of_construction_waste_burned_0_to_1 = 0.5
    TUNDRA_Avg_life_of_building_yr = 10
    TUNDRA_Fraction_of_construction_waste_burned_0_to_1 = 0.5
    TUNDRA_Time_to_decompose_undisturbed_dead_biomass_yr = 1000
    TUNDRA_Ref_historical_deforestation_pct_py = 0
    TUNDRA_historical_deforestation_pct_py = ( TUNDRA_Ref_historical_deforestation_pct_py / 100 )
    Fraction_TUNDRA_being_deforested_1_py = TUNDRA_historical_deforestation_pct_py
    TUNDRA_Normal_fire_incidence_fraction_py = 1
    TUNDRA_Living_biomass_in_1850 = 300
    Use_of_TUNDRA_biomass_for_energy_in_1850_pct = 1
    Use_of_TUNDRA_for_energy_in_2000_GtBiomass = TUNDRA_Living_biomass_in_1850 * Use_of_TUNDRA_biomass_for_energy_in_1850_pct / 100
    TUNDRA_living_biomass_densitiy_at_initial_time_tBiomass_pr_km2 = 14500
    TUNDRA_fraction_of_DeadB_and_SOM_being_destroyed_by_deforesting = 1
    TUNDRA_DeadB_and_SOM_densitiy_at_initial_time_tBiomass_pr_km2 = 65000
    TUNDRA_fraction_of_DeadB_and_SOM_being_destroyed_by_energy_harvesting = 0.1
    TUNDRA_fraction_of_DeadB_and_SOM_destroyed_by_natural_fires = 0
    GRASS_Speed_of_regrowth_yr = 2
    NF_Speed_of_regrowth_yr = 3
    TROP_Speed_of_regrowth_yr = 3
    TUNDRA_Speed_of_regrowth_yr = 3
    Strength_of_Effect_of_SDG_scores_on_wellbeing = 0.3
    Consumption_tax_rate_ie_fraction = 0.03
    Convection_as_f_of_incoming_solar_in_1850 = 0.071
    Sensitivity_of_convection_to_temp = 2.5
    Indicated_crop_yield_SE_L = 11
    Indicated_crop_yield_SE_k = 0.03171
    UNIT_conv_N_to_yield = 1
    Indicated_crop_yield_SE_x = - 14.5
    Indicated_crop_yield_SE_L2 = 5
    Indicated_crop_yield_SE_k2 = - 0.232
    Indicated_crop_yield_SE_x2 = 62.13
    Indicated_crop_yield_SE_min = 2.1
    UNIT_conv_to_per_thousand = 1000
    Ctax_Time_to_implement_goal = 5
    DAC_Time_to_implement_goal = 15
    expSoE_of_ed_on_dying = 0.15
    Strength_of_malnutrition_effect = 6
    Strength_of_poverty_effect = 2
    Strength_of_inequality_effect_on_mortality = 0.5
    Debt_cancelling_stepheight = 1
    Govt_debt_cancelling_spread = 2
    Lifetime_of_public_capacity = 25
    Time_to_write_of_public_loan_defaults = 30
    Time_to_implement_conventional_practices = 1
    Demand_adjustment_time = 1
    Time_to_deposit_C_in_sediment = 20000
    Slope_of_Eff_of_dmd_imbalnce_on_life_of_capacity = 0
    expSoE_of_ed_on_TFP = 0.25
    Sensitivity_of_trop_to_humidity = 5
    Humidity_of_atmosphere_in_1850_g_p_kg = 1.98018
    Strength_of_effect_of_income_ratio_after_tax = 0.1
    Reference_Time_to_regrow_TROP_after_deforesting = 1000
    Time_to_implement_actually_entering_the_pool = 1
    Reference_max_fraction_of_forest_possible_to_cut = 0.8
    FEHC_Time_to_implement_policy = 3
    Finance_sector_response_time_to_central_bank = 1
    FLWR_Time_to_implement_ISPV_goal = 5
    pb_Forest_degradation_green_threshold = 25
    UNIT_conv_to_Mkm2 = 1000
    Frac_atm_absorption = 75 / 340
    Frac_of_surface_emission_through_atm_window = 0.051
    Frac_SW_clear_sky_reflection_aka_scattering = 0.0837
    Frac_SW_HI_cloud_efffect_aka_cloud_albedo = 0.006
    Frac_SW_LO_cloud_efffect_aka_cloud_albedo = 0.158
    Fraction_blocked_by_ALL_GHG_in_1980 = 0.213577
    Fraction_blocked_CH4_in_1980 = 0.00445458
    Fraction_blocked_CO2_in_1980 = 0.0911213
    Fraction_blocked_othGHG_in_1980 = 0.0393
    UNIT_conv_pct_to_fraction = 100
    Freshwater_withdrawal_per_person_TLTL = 415
    UNIT_conv_to_cubic_km_pr_yr = 1 / 1000
    pb_Freshwater_withdrawal_green_threshold = 3000
    FTPEE_Time_to_implement_goal = 3
    FVE_shape_time = 3
    FWRP_Time_to_implement_goal = 15
    Time_required_to_fill_jobs = 7
    Global_warming_potential_CO2 = 1
    UNIT_conversion_to_tCO2e_pr_USD = 1000
    UNIT_conv_to_TUSD = 1 / 1000
    pb_Global_Warming_green_threshold = 1
    Time_to_write_off_govt_defaults_to_private_lenders = 30
    GRASS_Avg_life_biomass_yr = 100
    Use_of_GRASS_biomass_for_construction_in_1850_pct = 0.05
    Use_of_GRASS_for_construction_in_2000_GtBiomass = GRASS_Living_biomass_in_1850 * Use_of_GRASS_biomass_for_construction_in_1850_pct / 100
    Time_to_regrow_GRASS_yr = 10
    Time_to_regrow_GRASS_after_deforesting_yr = 80
    Heat_flow_from_the_earths_core = 0.1 * 16.09
    Hydro_future_net_dep_rate = 0.01
    Solar_sine_forcing_offset_yr = - 7
    Solar_sine_forcing_period_yr = 11
    Solar_sine_forcing_amplitude = 0.085
    Solar_sine_forcing_lift = 0.06
    Time_to_implement_regen_practices = 5
    Max_OSF = 0.95
    Min_OSF = 0.1
    pb_Air_Pollution_a = 0.0425
    pb_Air_Pollution_Unit_conv_to_make_LN_dmnl_from_terra_USD = 1
    pb_Air_Pollution_b = 37.7
    UNIT_conv_to_UAC = 1
    INITIAL_TIME = 1980
    Inventory_coverage_perception_time = 0.3
    K_to_C_conversion = 273.15
    Time_to_degrade_Kyoto_Fluor_yr = 50
    Land_surface_temp_adjustment_time_yr = 25
    Time_to_implement_lay_off = 3
    Lead_PB_green_threshold = 5
    Lead_release_a = 3.2
    Lead_release_b = 4.0412
    Unit_conv_to_make_LN_dmnl_from_terra_USD = 1000
    Start_year_P_Pb_phaseout = 2020
    P_Pb_Phaseout_time_TLTL = 150
    Lead_UNIT_conv_to_Mt_pr_yr = 1
    Time_to_implement_actually_leaving_the_pool = 1.5
    Long_term_interest_rate_expectation_formation_time = 4
    LPB_Time_to_implement_policy = 3
    LPBgrant_Time_to_implement_policy = 3
    LPBsplit_Time_to_implement_policy = 3
    UNIT_conversion_to_pct = 100
    Time_for_volcanic_aerosols_to_remain_in_the_stratosphere = 1
    Time_to_degrade_Montreal_gases_yr = 30
    N_number_of_years_ago = 5
    Nitrogen_PB_green_threshold = 100
    Time_to_degrade_N2O_in_atmopshere_yr = 95
    NEP_Time_to_implement_goal = 3
    Time_to_adjust_owner_investment_behaviour_in_productive_assets = 10
    Net_heat_flow_ocean_between_surface_and_deep_per_K_of_difference_ZJ_py_K = 10
    Temp_gradient_in_surface_degK = 9.7
    NF_Avg_life_biomass_yr = 60
    Use_of_NF_biomass_for_construction_in_1850_pct = 0.58
    Use_of_NF_for_construction_in_2000_GtBiomass = NF_Living_biomass_in_1850 * Use_of_NF_biomass_for_construction_in_1850_pct / 100
    Time_to_regrow_NF_yr = 30
    Time_to_regrow_NF_after_deforesting_yr = 80
    Normal_Time_to_implement_UN_policies = 5
    Nuclear_future_net_dep_rate = 0.02
    P_release_a = 5.3439
    P_release_b = 7.6136
    UNIT_conv_to_Mt_pr_yr = 1
    Phosphorous_PB_green_threshold = 10
    Temp_ocean_surface_in_1850_C = Temp_surface_1850 - Temp_gradient_in_surface_degK
    Output_growth_in_1980 = 0.035
    UNIT_conversion_to_M = 1000
    pb_Ozone_depletion_green_threshold = 0.25
    per_annum_yr = 1
    Time_for_urban_land_to_become_abandoned = 20
    Ref_shifting_biome_yr = 50
    REFOREST_policy_Time_to_implement_goal = 15
    Retooling_time = 3
    RIPLGF_Addl_time_to_shift_govt_expenditure = 3
    RMDR_Time_to_implement_policy = 10
    Social_tension_perception_delay = 5
    Sales_averaging_time = 1
    TIME_STEP = 0.03125
    Scaling_factor_of_eff_of_poverty_on_social_tension = 0.08
    UNIT_conversion_mm_to_m = 1 / 1000
    SGMP_Time_to_implement_policy = 3
    Zero_C_on_K_scale_K = 273.15
    Slope_of_effect_of_temp_shifting_DESERT_to_GRASS = 0.4
    Slope_of_effect_of_temp_shifting_GRASS_to_DESERT = 5
    Slope_of_effect_of_temp_shifting_GRASS_to_NF = 0.1
    Slope_of_effect_of_temp_shifting_GRASS_to_TROP = 0.2
    Slope_of_effect_of_temp_shifting_NF_to_GRASS = 0.01
    Slope_of_effect_of_temp_shifting_NF_to_TROP = 0.2
    Slope_of_effect_of_temp_on_shifting_NF_to_Tundra = 0.1
    Slope_of_effect_of_temp_shifting_TROP_to_GRASS = 0.05
    Slope_of_effect_of_temp_on_shifting_TROP_to_NF = 1
    Slope_of_effect_of_temp_shifting_tundra_to_NF = 0.2
    StrUP_Time_to_implement_policy = 3
    the_N_for_PC_N_yrs_ago = 5
    Time_for_defaulting_to_impact_cost_of_capital = 3
    Time_for_env_damage_to_affect_wellbeing = 3
    Time_for_GDPpp_to_affect_death_rates = 1
    Time_for_GDPpp_to_affect_owner_saving_fraction = 10
    Time_for_inequality_to_impact_wellbeing = 5
    Time_for_max_debt_debt_burden_to_affect_max_debt = 5
    Time_for_N_use_to_affect_regeneative_choice = 5
    Time_for_N_use_to_affect_soil_quality = 10
    Time_for_poverty_to_affect_social_tension_and_trust = 5
    Time_for_public_spending_to_affect_wellbeing = 5
    Time_for_shifts_in_relative_wealth_to_affect_env_damage_response = 10
    Time_lag_for_env_damage_to_affect_mortality = 5
    Time_required_for_inventory_fluctuations_to_impact_inflation_rate = 2
    Time_to_adjust_budget = 1
    Time_to_adjust_Existential_minimum_income = 5
    Time_to_adjust_forest_area_to_CO2_emissions = 2
    Time_to_adjust_owners_budget = 1
    Time_to_adjust_reform_willingness = 5
    Time_to_adjust_worker_consumption_pattern = 1
    Time_to_affect_life_expectancy = 10
    Time_to_ease_in_wealth_accumulation = 10
    Time_to_establish_Long_term_unemployment_rate = 5
    Time_to_form_an_opinion_about_demand_imbalance = 1
    Time_to_implement_CCS_goal = 10
    Time_to_implement_cutbacks = 5
    Time_to_implement_deforestation = 5
    Time_to_implement_ISPV_goal = 3
    Time_to_implement_spending_adjustments = 3
    Time_to_let_shells_form_and_sink_to_sediment_yr = 25
    Time_to_propagate_temperature_change_through_the_volume_of_permafrost_yr = 5
    Time_to_ramp_in_future_TLTL_leakage = 5
    Time_to_regrow_TROP_yr = 30
    Time_to_regrow_TUNDRA_after_deforesting_yr = 80
    Time_to_regrow_TUNDRA_yr = 10
    Time_to_smooth_cost_of_capital_for_workers = 10
    Time_to_smooth_effect_of_env_dam_on_TAs = 5
    Time_to_smooth_forest_land_comparison = 15
    Time_to_smooth_malnutrition_effect = 3
    Time_to_smooth_max_govt_debt = 2
    Time_to_smooth_Multplier_from_empowerment_on_indicated_social_trust = 5
    Time_to_smooth_Multplier_from_empowerment_on_speed_of_food_TA = 5
    Time_to_smooth_non_energy_footprint_changes = 5
    Time_to_smooth_out_temperature_diff_relevant_for_melting_or_freezing_from_1850_yr = 3
    Time_to_smooth_poverty_effect = 3
    Time_to_smooth_regional_food_balance = 3
    Time_to_smooth_RoC_in_GDPpp = 4
    Time_to_smooth_SDG_scores_for_wellbeing = 5
    Time_to_smooth_social_tension_index = 3
    Time_to_smooth_the_anchor_SDG_scores_for_wellbeing = 5
    Time_to_smooth_UAC = 10
    Time_to_smooth_unemp_rate = 5
    Time_to_verify_emi = 2
    Time_to_write_off_worker_defaults = 5
    TROP_Avg_life_biomass_yr = 60
    Use_of_TROP_biomass_for_construction_in_1850_pct = 0.48
    Use_of_TROP_for_construction_in_2000_GtBiomass = TROP_Living_biomass_in_1850 * Use_of_TROP_biomass_for_construction_in_1850_pct / 100
    TUNDRA_Avg_life_biomass_yr = 100
    Use_of_TUNDRA_biomass_for_construction_in_1850_pct = 0.05
    Use_of_TUNDRA_for_construction_in_2000_GtBiomass = TUNDRA_Living_biomass_in_1850 * Use_of_TUNDRA_biomass_for_construction_in_1850_pct / 100
    Unemployment_perception_time = 1
    WReaction_Time_to_implement_policy = 3
    XtaxCom_Time_to_implement_policy = 3
    Xtaxfrac_Time_to_implement_policy = 3
    XtaxRateEmp_Time_to_implement_policy = 3
    Years_for_CBC_comparison = 5
    Barren_land_in_1980 = np.array([59.725 , 598.224 , 302.224 , 532.885 , 61.2205 , 231.005 , 562.628 , 75.1457 , 225.261 , 15.9273]) * 1.0
    GDP_in_1980 = np.array([7070 , 1160 , 1970 , 1510 , 1210 , 2650 , 3750 , 4290 , 8780 , 940]) * 1.0
    Capital_output_ratio_in_1980 = np.array([3 , 8 , 1.6 , 8 , 8 , 6 , 4 , 5 , 3 , 8]) * 1.0
    Central_bank_signal_rate_in_1980 = np.array([0.13 , 0.1 , 0.1 , 0.13 , 0.13 , 0.13 , 0.13 , 0.13 , 0.13 , 0.13]) * 1.0
    Cohort_0_to_4_in_1980 = ([ 16.907701, 66.801562, 103.943347, 31.569206, 135.398637, 51.48271, 17.468252, 30.095115, 36.461211, 52.640757 ])
    Cohort_10_to_14_in_1980 = ([ 18.937472, 43.940929, 133.948072, 22.767273, 103.455397, 43.046737, 19.352604, 26.373505, 40.038377, 44.788868 ])
    Cohort_15_to_19_in_1980 = ([ 21.517461, 37.081781, 110.482973, 19.527712, 92.45383, 38.903513, 18.357064, 28.52345, 40.461573, 39.511144 ])
    Cohort_20_to_24_in_1980 = np.array([21.8119 , 30.9356 , 90.8949 , 16.2883 , 80.2574 , 33.0054 , 17.9121 , 29.3363 , 38.3132 , 33.8076]) * 1.0
    Cohort_25_to_29_in_1980 = np.array([20.1388 , 25.7601 , 93.9462 , 13.5363 , 68.8477 , 27.871 , 16.9721 , 27.0832 , 35.9392 , 27.1812]) * 1.0
    Cohort_30_to_34_in_1980 = np.array([17.9741 , 21.4953 , 66.5902 , 10.1467 , 54.7314 , 22.3587 , 18.112 , 21.9265 , 34.3898 , 20.3428]) * 1.0
    Cohort_35_to_39_in_1980 = np.array([14.1212 , 18.1089 , 51.7003 , 8.11063 , 47.8514 , 18.4678 , 15.4939 , 15.9304 , 29.6731 , 17.5491]) * 1.0
    Cohort_40to_44_in_1980 = np.array([12.0704 , 15.1989 , 49.1493 , 7.57296 , 43.0932 , 16.0675 , 13.9846 , 23.9835 , 29.6751 , 16.2267]) * 1.0
    Cohort_45_to_49_in_1980 = np.array([11.2448 , 12.9651 , 45.6996 , 6.93185 , 37.0717 , 13.7945 , 12.771 , 18.9808 , 28.5509 , 14.2525]) * 1.0
    Cohort_5_to_9_in_1980 = ([ 17.16009, 53.164399, 128.476879, 26.126713, 116.397822, 46.652054, 20.355446, 28.12971, 37.948148, 48.979344 ])
    Cohort_50_to_54_in_1980 = np.array([11.8282 , 10.7494 , 38.8158 , 5.90496 , 31.0911 , 12.1465 , 11.2918 , 21.2099 , 27.634 , 11.6688]) * 1.0
    Cohort_55_to_59_in_1980 = np.array([11.7494 , 8.77535 , 32.7015 , 4.77509 , 25.2041 , 9.80378 , 9.31261 , 14.8069 , 26.0149 , 9.27789]) * 1.0
    Cohort_60to_64_in_1980 = np.array([10.3383 , 6.85514 , 28.8279 , 3.5816 , 19.5622 , 7.63257 , 7.39933 , 9.67908 , 17.9898 , 7.30147]) * 1.0
    Cohort_65_to_69_in_1980 = np.array([9.05561 , 4.99637 , 21.6784 , 2.67587 , 14.1206 , 6.14692 , 6.37421 , 11.5565 , 20.9206 , 5.76418]) * 1.0
    Cohort_70_to_74_in_1980 = np.array([7.12572 , 3.26783 , 13.93 , 1.9277 , 9.35538 , 4.35627 , 4.72676 , 8.85296 , 17.7072 , 3.98601]) * 1.0
    Cohort_75_to_79_in_1980 = np.array([5.33309 , 1.78414 , 7.96522 , 1.14022 , 5.04137 , 2.7543 , 3.06813 , 5.64866 , 12.3354 , 2.32888]) * 1.0
    Cohort_80_to_84_in_1980 = np.array([2.9033 , 0.730893 , 3.1889 , 0.527981 , 2.38067 , 1.44232 , 1.65191 , 2.70643 , 6.80679 , 1.07722]) * 1.0
    Cohort_85_to_89_in_1980 = np.array([1.65033 , 0.193374 , 0.968024 , 0.168828 , 0.729614 , 0.527403 , 0.665821 , 1.10846 , 2.78283 , 0.360152]) * 1.0
    Cohort_90_to_94_in_1980 = np.array([0.564662 , 0.02922 , 0.173605 , 0.0348 , 0.187232 , 0.145646 , 0.185384 , 0.364529 , 0.791019 , 0.085622]) * 1.0
    Cohort_95p_in_1980 = np.array([0.134325 , 0.002834 , 0.020406 , 0.004407 , 0.033359 , 0.029358 , 0.031645 , 0.075015 , 0.13436 , 0.015641]) * 1.0
    Normal_signal_rate = np.array([0.02 , 0.04 , 0.02 , 0.02 , 0.02 , 0.02 , 0.02 , 0.02 , 0.02 , 0.02]) * 1.0
    Cropland_in_1980 = np.array([190.624 , 131.158 , 100.219 , 51.67 , 214.32 , 138.743 , 68.646 , 248.075 , 145.678 , 77.2311]) * 1.0
    Employed_in_1980 = np.array([103 , 139 , 494 , 41 , 322 , 114 , 92 , 163 , 194 , 128]) * 1.0
    Forest_land_in_1980 = np.array([257.393 , 297.096 , 213.879 , 50 , 35.6341 , 769.077 , 620.972 , 1066.66 , 118.106 , 234.835]) * 1.0
    Fossil_el_gen_cap_in_1980 = np.array([200 , 30 , 50 , 30 , 10 , 25 , 70 , 160 , 160 , 20]) * 1.0
    Frac_outside_of_labour_pool_in_1980 = np.array([0.52 , 0.77 , 0.47 , 0.69 , 0.61 , 0.62 , 0.55 , 0.58 , 0.58 , 0.53]) * 1.0
    SoE_of_inventory_on_indicated_hours_worked_index = np.array([-1 , -1 , -0.6 , -1 , -1 , -1 , -1 , -1 , -1 , -1]) * 1.0
    Perceived_relative_inventory_in_1980 = np.array([1 , 1 , 1 , 1 , 0.89 , 0.8 , 0.89 , 1 , 0.8 , 1]) * 1.0
    GE_in_1980 = np.array([0.3 , 0.2 , 0.4 , 0.1 , 0.17 , 0.3 , 0.28 , 0.38 , 0.28 , 0.25]) * 1.0
    Govt_debt_in_1980 = np.array([3535 , 1160 , 394 , 1510 , 1210 , 2650 , 3750 , 4290 , 8780 , 940]) * 1.0
    Grazing_land_in_1980 = np.array([237.539 , 609.232 , 328.3 , 227.076 , 20.209 , 512.548 , 513.767 , 452.092 , 81.1108 , 15.133]) * 1.0
    OSF_in_1980 = np.array([0.8 , 0.2 , 0.45 , 0.4 , 0.3 , 0.4 , 0.85 , 0.4 , 0.8 , 0.3]) * 1.0
    Fraction_multiple_of_regional_GDP_as_owners_wealth_in_1980 = np.array([2 , 2 , 2 , 2 , 2 , 2 , 2 , 2 , 2 , 2]) * 1.0
    Populated_land_in_1980 = np.array([43.4524 , 3.612 , 48.6394 , 3.82125 , 6.94276 , 9.03042 , 13.6515 , 2.953 , 14.5271 , 6.66976]) * 1.0
    Rate_of_tech_advance_RoTA_in_TFP_in_1980 = np.array([0.019 , 0.0225 , 0.05 , 0.0375 , 0.06 , 0.035 , 0.0275 , 0.03 , 0.0225 , 0.06]) * 1.0
    Multiple_of_spec_assets_to_GDP_in_1980 = np.array([5 , 0.5 , 0.5 , 10 , 0.3 , 0.7 , 2 , 0.1 , 2 , 1.5]) * 1.0
    Unemployment_in_1980 = np.array([8 , 10 , 35 , 5 , 10 , 5 , 5 , 5 , 15 , 10]) * 1.0
    Indicated_reform_willingness_at_2025 = np.array([1.11495 , 1.04327 , 1.2296 , 1.07187 , 1.07767 , 1.08293 , 1.14946 , 1.07685 , 1.08014 , 1.09736]) * 1.0
    Life_expec_a = np.array([47 , 36 , 64 , 40 , 57 , 40 , 53 , 47 , 35 , 58]) * 1.0
    Life_expec_b = np.array([10 , 15 , 7 , 10 , 8 , 10 , 8 , 10 , 13 , 8]) * 1.0
    Life_expectancy_at_birth_in_1980 = np.array([73.8 , 48.5 , 66.8 , 58.2 , 54 , 64.5 , 73.3 , 66.8 , 72 , 60.4]) * 1.0
    Pension_age_in_1980 = np.array([65 , 65 , 65 , 65 , 65 , 65 , 65 , 65 , 65 , 65]) * 1.0
    SoE_of_LE_on_Pension_age = np.array([0.6 , 0.6 , 0.6 , 0.6 , 0.6 , 0.6 , 0.6 , 0.6 , 0.6 , 0.6]) * 1.0
    Worker_debt_ratio_in_1980 = np.array([1 , 0.2 , 0.2 , 0.4 , 0.4 , 0.4 , 0.4 , 0.4 , 0.4 , 0.4]) * 1.0
    cereal_dmd_func_pp_L = np.array([220 , 250 , 199 , 230 , 290 , 200 , 250 , 250 , 250 , 275]) * 1.0
    cereal_dmd_func_pp_k = np.array([0.06 , 0.3 , 0.1 , 0.081 , 0.19 , 0.078 , 0.01 , 0.01 , 0.0189 , 0.3]) * 1.0
    cereal_dmd_func_pp_x0 = np.array([10 , 3 , 1 , -6.46 , 1 , 1.1368 , 1 , -50 , -2.2 , 2]) * 1.0
    Food_wasted_in_1980 = np.array([0.3 , 0.3 , 0.3 , 0.3 , 0.3 , 0.3 , 0.3 , 0.3 , 0.3 , 0.3]) * 1.0
    Consumption_taxes_in_1980 = np.array([84.9169 , 21.154 , 30.8086 , 24.4263 , 20.8022 , 42.7945 , 42.9795 , 69.2588 , 105.452 , 16.1664]) * 1.0
    toe_to_CO2_a = np.array([2.7 , 2.8 , 2.6 , 2.16 , 2.4 , 2.37 , 2 , 3 , 2.1 , 2.1]) * 1.0
    Fossil_use_pp_NOT_for_El_gen_WO_CN_L = np.array([5.7 , 4 , 4 , 3.5 , 4 , 3.5 , 3.5 , 4 , 9.7 , 4]) * 1.0
    Fossil_use_pp_NOT_for_El_gen_WO_CN_k = np.array([-0.06 , 0.25 , 0.01 , 0.055 , 0.197 , 0.027 , 0.0395 , 0.05 , -0.0205 , 0.1]) * 1.0
    Fossil_use_pp_NOT_for_El_gen_WO_CN_x0 = np.array([80 , 15 , 1 , 22.03 , 16.81 , 60 , 6.134 , 20 , -25 , 26.5]) * 1.0
    Hydro_gen_cap_L = np.array([85 , 100 , 500 , 13 , 80 , 200 , 150 , 84 , 200 , 65]) * 1.0
    Hydro_gen_cap_k = np.array([0.045 , 0.4 , 0.3 , 0.15 , 0.25 , 0.3 , 0.04 , 0.08 , 0.045 , 0.3]) * 1.0
    Hydro_gen_cap_x0 = np.array([12 , 7.2 , 11 , 8 , 4 , 6 , -2 , 6 , 12 , 7.5]) * 1.0
    Hydrocapacity_factor = np.array([0.45 , 0.45 , 0.41 , 0.45 , 0.45 , 0.45 , 0.45 , 0.45 , 0.45 , 0.45]) * 1.0
    Fossil_actual_uptime_factor = np.array([0.82 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 0.81 , 1]) * 1.0
    Conversion_Mtoe_to_TWh = np.array([4 , 4 , 4 , 4 , 4 , 4.5 , 5 , 4.5 , 4 , 4]) * 1.0
    toe_to_CO2_b = np.array([1 , 0 , -0.0036 , 0.1599 , 0.1 , 0.15 , 0.8 , 0.0347 , 1 , 0.1]) * 1.0
    CO2_emi_from_IPC2_use_a = np.array([-0.132 , 0.0494 , 0.7005 , 0.2 , 0.0882 , 0.1347 , 0.0352 , -0.056 , -0.038 , 0.1055]) * 1.0
    CO2_emi_from_IPC2_use_b = np.array([0.7855 , -0.0029 , -0.5722 , -0.35 , 0.0396 , -0.1619 , 0.0264 , 0.4819 , 0.4481 , -0.0839]) * 1.0
    Reference_max_govt_debt_burden = np.array([2 , 2 , 1.25 , 2 , 2 , 2 , 2 , 2 , 2 , 2]) * 1.0
    oth_crop_dmd_pp_a = np.array([61.5666 , 155.265 , 218.985 , 103.477 , 89.3181 , 713.147 , 44.8079 , -63.6056 , -118.483 , 113.732]) * 1.0
    oth_crop_dmd_pp_b = np.array([351.895 , 288.935 , 157.457 , 149.41 , 322.62 , -129.904 , 285.873 , 820.263 , 1183.46 , 280.016]) * 1.0
    Feed_dmd_a = np.array([79.37 , 266.31 , 465.61 , 91.78 , 619.57 , 105.51 , 23.507 , 113.92 , 115.57 , 169.85]) * 1.0
    red_meat_dmd_func_pp_L = np.array([33.6 , 20 , 20 , 15 , 20 , 35 , 20 , 20 , 21 , 20]) * 1.0
    red_meat_dmd_func_pp_k = np.array([-0.053 , 0.13 , 0.13 , 0.0469 , 0.01 , 0.065 , 0.01 , 0.03 , -0.044 , 0.05]) * 1.0
    red_meat_dmd_func_pp_x0 = np.array([63.233 , 7.5 , 16 , -2.97 , 1 , -3.03 , 1 , -35 , 49 , 37]) * 1.0
    red_meat_dmd_func_pp_min = np.array([20 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 5 , 0]) * 1.0
    Desired_net_export_of_red_meat = np.array([0.1 , -0.06 , -0.06 , -0.35 , -0.06 , 0.1 , 0.1 , 0.1 , 0.1 , -0.06]) * 1.0
    white_meat_dmd_func_pp_L = np.array([120 , 50 , 50 , 50 , 20 , 65 , 70 , 65 , 58 , 50]) * 1.0
    white_meat_dmd_func_pp_k = np.array([0.0313 , 0.3 , 0.1 , 0.122 , 0.2 , 0.2 , 0.04 , 0.075 , 0.18 , 0.1]) * 1.0
    white_meat_dmd_func_pp_x0 = np.array([31.39 , 11 , 1 , 21.97 , 14 , 10 , 31 , 17 , 11.7 , 11]) * 1.0
    Feed_dmd_b = np.array([-151.9 , -267.87 , -1104.3 , -1.2125 , -702.71 , -165.85 , 31.095 , -168.57 , -180.11 , -208.09]) * 1.0
    All_crop_dmd_food_in_1980 = np.array([170.267 , 217.006 , 452.252 , 99.7209 , 454.033 , 556.297 , 119.587 , 267.5 , 470.721 , 193.064]) * 1.0
    Desired_net_export_of_crops = np.array([0.23 , 0 , 0 , -0.2 , 0 , 0.3 , 0 , 0.3 , 0.05 , 0.4]) * 1.0
    crop_yield_in_1980 = np.array([2.5 , 1.5 , 4.8 , 1.6 , 2 , 1.6 , 2.33 , 1.6 , 4.5 , 3.2]) * 1.0
    Fraction_of_supply_imbalance_to_be_closed_by_land = np.array([0.1 , 1 , 1 , 1 , 1 , 0.1 , 0 , 0.1 , 0.1 , 1]) * 1.0
    Fraction_of_cropland_gap_closed_from_acgl = np.array([1 , 1 , 1 , 1 , 1 , 1 , 0 , 1 , 1 , 1]) * 1.0
    Grazing_land_Rest_L = np.array([300 , 720 , 393 , 300 , 300 , 300 , 300 , 300 , 100 , 300]) * 1.0
    Grazing_land_Rest_k = np.array([0.00344 , 0.1 , 0.107 , 0 , 0 , 0 , 0 , 0 , 0.0131 , 0]) * 1.0
    Grazing_land_Rest_x = np.array([-418 , -14 , -0.127 , 1 , 1 , 1 , 1 , 1 , -96 , 1]) * 1.0
    Urban_land_per_population = np.array([0.25 , 0.049 , 0.036 , 0.06 , 0.03 , 0.06 , 0.07 , 0.019 , 0.06 , 0.034]) * 1.0
    Nuclear_gen_cap_WO_EU_L = np.array([117.5 , 2.1 , 75 , 2 , 10 , 5 , 100 , 43 , 99 , 0]) * 1.0
    Nuclear_gen_cap_WO_EU_k = np.array([0.1 , 0.5 , 0.3 , 0.5 , 0.5 , 0.3 , 0.06 , 0.2 , 0.1 , 0.2]) * 1.0
    Nuclear_gen_cap_WO_EU_x0 = np.array([32.5 , 2 , 14 , 20 , 5 , 10 , 30 , 12 , 1 , 3.5]) * 1.0
    El_use_pp_WO_US_L = np.array([8 , 10 , 10 , 8 , 8 , 8 , 12 , 12 , 8 , 10]) * 1.0
    El_use_pp_WO_US_k = np.array([0.055 , 0.3 , 0.3 , 0.0939 , 0.2541 , 0.0939 , 0.069 , 0.075 , 0.055 , 0.1]) * 1.0
    El_use_pp_WO_US_x0 = np.array([6.2 , 13 , 13 , 22.6 , 13.49 , 22.6 , 20.34 , 26 , 6.2 , 28]) * 1.0
    Fossil_capacity_factor = np.array([0.45 , 0.4 , 0.4 , 0.4 , 0.4 , 0.3 , 0.4 , 0.5 , 0.45 , 0.4]) * 1.0
    Time_to_close_gap_in_fossil_el_cap = np.array([15 , 5 , 6 , 10 , 5 , 5 , 5 , 5 , 10 , 6]) * 1.0
    wind_and_PV_el_share_k = np.array([0.128133 , 0.5 , 0.4 , 0.135 , 0.66707 , 0.2 , 0.15 , 0.367 , 0.158 , 0.1]) * 1.0
    wind_and_PV_el_share_x0 = np.array([76 , 10 , 17.5 , 45 , 7.48978 , 24 , 60 , 32 , 46 , 35]) * 1.0
    Fraction_of_supply_imbalance_to_be_closed_by_yield_adjustment = np.array([0.3 , 0.3 , 0.3 , 0.3 , 0.3 , 0.3 , 0.3 , 0.3 , 0.3 , 0.3]) * 1.0
    Nitrogen_use_rest_L = np.array([108 , 22.5 , 50 , 75 , 50 , 85 , 100 , 50 , 130 , 65]) * 1.0
    Nitrogen_use_rest_k = np.array([0.04 , 0.6 , 0.1 , 0.134 , 0.1 , 0.12 , 0.066148 , 0.09 , 0.016 , 0.9]) * 1.0
    Nitrogen_use_rest_x0 = np.array([36.64 , 4.4 , 1 , 10.46 , 1 , 12.3717 , 30.348 , 21 , -34 , 2.5]) * 1.0
    Capital_labour_ratio_in_1980 = np.array([20000 , 11000 , 5000 , 25000 , 5000 , 15000 , 25000 , 25000 , 25000 , 5000]) * 1.0
    RoC_Capital_labour_ratio_in_1980 = np.array([0.025 , 0.025 , 0.05 , 0.025 , 0.02 , 0.02 , 0.02 , 0.01 , 0.025 , 0.02]) * 1.0
    SoE_of_GDPpp_on_RoC_of_CLR = np.array([0.05 , 0.3 , 0.3 , 0.05 , 0.05 , 0.05 , 0.05 , 0.05 , 0.05 , 0.05]) * 1.0
    Worker_share_of_output_with_unemployment_effect_in_1980 = np.array([0.556634 , 0.556105 , 0.556004 , 0.56073 , 0.552323 , 0.553507 , 0.554477 , 0.552287 , 0.556602 , 0.556677]) * 1.0
    CH4_emi_from_agriculture_a = np.array([3 , 10.342 , 3.12151 , 0.8249 , 10 , 9.1509 , -1.7 , 8.6162 , 5.3 , 4.08118]) * 1.0
    CH4_emi_from_agriculture_b = np.array([1.672 , 0.605134 , 14.4031 , 1.75 , 5 , -1.6894 , 9.06 , -8.3246 , -1.75 , 8.71646]) * 1.0
    CH4_emi_from_energy_a = np.array([1 , 25 , 9.7 , 22.561 , 3.2 , 6.9187 , 3.7161 , 16 , 1 , 6]) * 1.0
    CH4_emi_from_energy_b = np.array([1 , 0.6 , 0.756 , 0.5886 , -0.2 , 0.7615 , 0.0535 , -0.7615 , 1 , 0.4]) * 1.0
    CH4_emi_from_waste_a = np.array([-4.858 , 1 , 1 , 3.672 , 3 , 7.082 , -0.235 , 1.53 , -3.947 , 7]) * 1.0
    CH4_emi_from_waste_b = np.array([25.387 , 1 , 1 , -4.58 , 1 , -11.039 , 3.4589 , 0.5983 , 22.115 , -6]) * 1.0
    N_excreted_a = np.array([7.687 , 2.3781 , 0.6 , 2.308 , 5.3304 , 6.2719 , 9.943 , 3.439 , 124.64 , 1.5105]) * 1.0
    N_excreted_b = np.array([-1.031 , -0.018 , -0.016 , -0.651 , -0.506 , -0.658 , -1.146 , -0.742 , -1.624 , -0.599]) * 1.0
    N2O_emi_from_agri_a = np.array([0.0265 , 0.036 , 0.029 , 0.037 , 0.0159 , 0.037 , 0.0159 , 0.0263 , 0.03 , 0.0228]) * 1.0
    N2O_emi_from_agri_b = np.array([0.6528 , 0.38 , -0.09 , -0.024 , -0.0934 , -0.024 , 0.042 , 0.2452 , -0.024 , 0.083]) * 1.0
    N2O_emi_X_agri_a = np.array([0 , 0.0252 , 0.0671 , 0.007 , 0.05 , 0.0048 , -0.0009 , 0.0012 , 0 , 0.009]) * 1.0
    N2O_emi_X_agri_b = np.array([0.1 , 0.0484 , 0.0035 , 0.043 , 0 , 0.0858 , 0.2027 , 0.1361 , 0.1 , 0.0309]) * 1.0
    Annual_pct_deforested = np.array([0.1 , 1 , 0.3 , 1 , 0.5 , 1 , 0.1 , 0.3 , 0 , 1]) * 1.0
    Slope_of_Corporate_borrowing_cost_eff_on_available_capital = np.array([-0.1 , 0 , 0 , 0 , 0 , -0.4 , 0 , -0.3 , -0.1 , 0]) * 1.0
    SWITCH_CBC_effect_on_available_capital = np.array([1 , 2 , 2 , 2 , 2 , 1 , 2 , 1 , 1 , 2]) * 1.0
    Owner_income_in_1980 = np.array([2444.98 , 401.637 , 682.245 , 517.372 , 422.518 , 922.901 , 1303.15 , 1498.14 , 3036.57 , 325.045]) * 1.0
    Average_wellbeing_index_in_1980 = np.array([0.963519 , 0.900166 , 0.722803 , 0.776837 , 0.693668 , 0.81494 , 0.868185 , 0.865638 , 0.904384 , 0.880155]) * 1.0
    birth_rate_a = np.array([0.0982 , 0.205 , 0.09 , 0.232 , 0.086 , 1.87 , 0.1317 , 0.0418 , 0.1214 , 0.1174]) * 1.0
    birth_rate_b = np.array([-0.472 , -0.83 , -0.01 , -0.5599 , -1.025 , -1.92394 , -0.459 , -0.042 , -0.414 , -0.515]) * 1.0
    birth_rate_c = np.array([0.015 , 0.0025 , 0.01 , 0 , 0.025 , 0.025 , 0 , 0 , 0 , 0]) * 1.0
    Births_effect_from_cohorts_outside_15_to_45 = np.array([1 , 1.06 , 0.97 , 1.03 , 0.83 , 0.775 , 0.93 , 0.95 , 1 , 0.84]) * 1.0
    So_Eff_of_labour_imbalance_on_FOLP = np.array([0.0002 , 0.012 , 0.005 , 0.0003 , 0.0005 , 0.0018 , 0.001 , 0 , 0.0003 , 0.0005]) * 1.0
    Scaling_strength_of_RoC_from_unemployed_to_pool = np.array([1 , 0.95 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1]) * 1.0
    SoE_of_PC_on_RoC_in_change_in_rate_of_tech_advance = np.array([1 , 6 , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 1]) * 1.0
    SoE_of_tertiary_sector_on_RoC_in_TFP = np.array([-0.06 , -0.05 , -0.05 , -0.05 , -0.05 , -0.05 , -0.06 , -0.05 , -0.05 , -0.06]) * 1.0
    Perceived_inflation_in_1980 = np.array([0.15 , 0.08 , 0.08 , 0.1 , 0.18 , 0.15 , 0.1 , 0.15 , 0.15 , 0.08]) * 1.0
    Inflation_target = np.array([0.02 , 0.05 , 0.035 , 0.035 , 0.05 , 0.05 , 0.02 , 0.03 , 0.02 , 0.025]) * 1.0
    SWITCH_unemp_target_or_long_term = np.array([1 , 1 , 1 , 2 , 1 , 2 , 1 , 1 , 1 , 2]) * 1.0
    Unemployment_target_for_interest = np.array([0.05 , 0.07 , 0.07 , 0.03 , 0.07 , 0.03 , 0.03 , 0.03 , 0.05 , 0.04]) * 1.0
    Indicated_WACC_fraction = np.array([0.3 , 0.3 , 0.3 , 0.3 , 0.3 , 0.3 , 0.3 , 0.3 , 0.3 , 0.3]) * 1.0
    Indicated_crop_yield_rest_L = np.array([6.24 , 4.6 , 15 , 4.5 , 10 , 12 , 5 , 6 , 12 , 11]) * 1.0
    Indicated_crop_yield_rest_k = np.array([0.0508 , 0.3 , 0.012 , 0.15 , 0.0198 , 0.1 , 0.027 , 0.06 , 0.085 , 0.03171]) * 1.0
    Indicated_crop_yield_rest_x0 = np.array([59.34 , 6.2 , 150 , 32 , 88 , 30 , 30 , 30 , 97 , 1]) * 1.0
    dr0_a = np.array([0.2044 , 0.0968 , 0.0239721 , 0.0970563 , 0.0463457 , 0.760547 , 0.172593 , 0.0548485 , 0.342607 , 0.0581034]) * 1.0
    dr0_b = np.array([-1.221 , -1.119 , -0.759395 , -0.924117 , -0.986135 , -1.98658 , -1.26419 , -0.715971 , -1.33556 , -1.04907]) * 1.0
    dr35_a = np.array([0.0053 , 0.016668 , 0.00267271 , 0.0137294 , 0.00510275 , 0.0141353 , 0.0164776 , 0.00768488 , 0.00967385 , 0.00712475]) * 1.0
    dr35_b = np.array([-0.292 , -0.621721 , -0.332791 , -0.749027 , -0.41194 , -0.692944 , -0.759418 , -0.265449 , -0.588911 , -0.480438]) * 1.0
    dr40_a = np.array([0.0128 , 0.0180344 , 0.00371472 , 0.0156144 , 0.00678361 , 0.0202697 , 0.0163656 , 0.0131108 , 0.0111224 , 0.00827057]) * 1.0
    dr40_b = np.array([-0.437 , -0.559318 , -0.319419 , -0.688518 , -0.407372 , -0.735979 , -0.640284 , -0.351418 , -0.504529 , -0.400984]) * 1.0
    dr45_a = np.array([0.0264 , 0.0196008 , 0.00538171 , 0.0205822 , 0.00936926 , 0.0266287 , 0.0207681 , 0.0214813 , 0.0152363 , 0.0102799]) * 1.0
    dr45_b = np.array([-0.518 , -0.498066 , -0.326391 , -0.626545 , -0.372203 , -0.713779 , -0.58857 , -0.400453 , -0.463706 , -0.330488]) * 1.0
    dr50_a = np.array([0.0442 , 0.022758 , 0.00955783 , 0.0277957 , 0.0139832 , 0.0330396 , 0.0295831 , 0.0403044 , 0.0235237 , 0.0138102]) * 1.0
    dr50_b = np.array([-0.54 , -0.413595 , -0.360736 , -0.547992 , -0.343307 , -0.650265 , -0.570757 , -0.515076 , -0.46261 , -0.283289]) * 1.0
    dr55_a = np.array([0.0873 , 0.0282151 , 0.0148174 , 0.034803 , 0.0208927 , 0.0467877 , 0.0442172 , 0.0414436 , 0.0383174 , 0.0195808]) * 1.0
    dr55_b = np.array([-0.611 , -0.363389 , -0.331583 , -0.487561 , -0.330148 , -0.636649 , -0.556872 , -0.382674 , -0.481035 , -0.257094]) * 1.0
    dr60_a = np.array([0.2076 , 0.0394868 , 0.0247627 , 0.0448349 , 0.0345093 , 0.0729714 , 0.074377 , 0.0499546 , 0.0654207 , 0.0325169]) * 1.0
    dr60_b = np.array([-0.73 , -0.320545 , -0.280082 , -0.393731 , -0.37166 , -0.651625 , -0.575179 , -0.322127 , -0.512493 , -0.301312]) * 1.0
    dr65_a = np.array([0.3796 , 0.0569518 , 0.0376463 , 0.0679361 , 0.0504093 , 0.106026 , 0.12198 , 0.0611206 , 0.111736 , 0.0550353]) * 1.0
    dr65_b = np.array([-0.787 , -0.277367 , -0.218713 , -0.374043 , -0.332814 , -0.638809 , -0.591236 , -0.269116 , -0.542689 , -0.340119]) * 1.0
    dr70_a = np.array([0.572 , 0.087954 , 0.0667662 , 0.103967 , 0.0739432 , 0.158873 , 0.192363 , 0.0884276 , 0.191794 , 0.0888564]) * 1.0
    dr70_b = np.array([-0.785 , -0.254721 , -0.205684 , -0.33058 , -0.283363 , -0.635569 , -0.588862 , -0.248511 , -0.563631 , -0.351908]) * 1.0
    dr75_a = np.array([0.5533 , 0.13508 , 0.107517 , 0.149683 , 0.108474 , 0.227804 , 0.272054 , 0.135544 , 0.30471 , 0.132639]) * 1.0
    dr75_b = np.array([-0.664 , -0.230475 , -0.188994 , -0.270794 , -0.272187 , -0.603628 , -0.537849 , -0.240646 , -0.550445 , -0.325219]) * 1.0
    dr80_a = np.array([0.7722 , 0.21254 , 0.182508 , 0.212282 , 0.160006 , 0.423807 , 0.37234 , 0.245588 , 0.432721 , 0.20363]) * 1.0
    dr80_b = np.array([-0.621 , -0.223126 , -0.237083 , -0.214784 , -0.234113 , -0.670318 , -0.478028 , -0.299529 , -0.497531 , -0.325019]) * 1.0
    dr85_a = np.array([0.5184 , 0.324963 , 0.270235 , 0.305642 , 0.233244 , 0.581153 , 0.491005 , 0.281373 , 0.602357 , 0.271059]) * 1.0
    dr85_b = np.array([-0.389 , -0.221219 , -0.218259 , -0.184128 , -0.208412 , -0.620289 , -0.410508 , -0.178954 , -0.443274 , -0.284262]) * 1.0
    dr90_a = np.array([0.524 , 0.456045 , 0.383196 , 0.42516 , 0.324786 , 0.687932 , 0.593281 , 0.380448 , 0.678884 , 0.346641]) * 1.0
    dr90_b = np.array([-0.267 , -0.200075 , -0.220698 , -0.166495 , -0.173688 , -0.535241 , -0.325032 , -0.144953 , -0.334793 , -0.261247]) * 1.0
    dr95p_a = np.array([0.5031 , 0.579391 , 0.492643 , 0.595128 , 0.347011 , 0.656443 , 0.707515 , 0.563918 , 0.735896 , 0.444143]) * 1.0
    dr95p_b = np.array([-0.132 , -0.194424 , -0.179435 , -0.167295 , -0.186558 , -0.3355 , -0.234102 , -0.157949 , -0.220606 , -0.236568]) * 1.0
    Reference_fraction_of_supply_imbalance_to_be_closed_by_imports = np.array([0 , 0.3 , 0.3 , 0.75 , 0.3 , 0.75 , 0.3 , 0.75 , 0 , 0.3]) * 1.0
    mort_80_to_84_adjust_factor = np.array([0.8 , 1.3 , 1 , 1.2 , 1.8 , 1.4 , 0.6 , 0.7 , 0.8 , 1.8]) * 1.0
    mort_85_to_89_adjust_factor = np.array([1.1 , 1.7 , 1.8 , 1.5 , 1.3 , 1.4 , 1 , 1.4 , 1.1 , 1.3]) * 1.0
    mort_90_to_94_adjust_factor = np.array([1.2 , 2.2 , 1.6 , 2.1 , 1.7 , 1.4 , 1.2 , 1.4 , 1.2 , 1.7]) * 1.0
    mort_95plus_adjust_factor = np.array([2.2 , 3.6 , 2 , 3.1 , 2.6 , 2.3 , 1.9 , 3.3 , 2.2 , 2.6]) * 1.0
    Effect_of_poverty_on_social_tension_in_1980 = np.array([0.895992 , 0.212402 , 0.192882 , 0.361938 , 0.189584 , 0.379113 , 0.753294 , 0.56287 , 0.807669 , 0.198562]) * 1.0
    Worker_to_owner_income_after_tax_ratio_in_1980 = np.array([1.27683 , 1.19194 , 1.18794 , 1.2262 , 1.17016 , 1.19347 , 1.22728 , 1.19954 , 1.24581 , 1.19309]) * 1.0
    Factor_to_account_for_net_migration_not_officially_recorded = np.array([0.1 , 14 , -9 , 0 , -0.1 , -0.1 , 0.7 , 0 , 0 , -2]) * 1.0
    Slope_of_OSF_from_GDPpp_alone = np.array([-0.06 , -0.06 , -0.06 , -0.02 , -0.02 , -0.06 , -0.06 , -0.06 , -0.02 , -0.06]) * 1.0
    Size_of_industrial_sector_in_1980 = np.array([0.276639 , 0.335694 , 0.301545 , 0.383726 , 0.287493 , 0.383928 , 0.334497 , 0.370616 , 0.320088 , 0.322107]) * 1.0
    Strength_of_effect_of_industrial_sector_size_on_OSF = np.array([1 , 1.85 , 1.5 , 1 , 1 , 1 , 1 , 1 , 1 , 1]) * 1.0
    Inflation_perception_time = np.array([1 , 2 , 2 , 1 , 1 , 1 , 1 , 1 , 1 , 1]) * 1.0
    SoE_of_inventory_on_inflation_rate = np.array([0.5 , 3 , 3 , 0.5 , 0.5 , 0.5 , 0.5 , 0.5 , 0.5 , 2]) * 1.0
    Minimum_relative_inventory_without_inflation = np.array([0.94 , 0.97 , 0.99 , 0.88 , 0.9 , 0.75 , 0.95 , 0.85 , 0.92 , 0.981]) * 1.0
    LULUC_emissions_a = np.array([0.1 , 2 , -0.3 , 0 , -4 , -0.8 , 0.5 , 0.15 , 0.3 , -0.7]) * 1.0
    LULUC_emissions_b = np.array([-0.65 , 1.5 , -0.75 , 0 , -0.4 , 1.2 , -1.8 , -1.5 , -0.4 , -0.5]) * 1.0
    Migration_fraction_10_to_14_cohort = np.array([0.4 , 0.2 , 0 , 0.2 , 0 , 0 , 0.2 , 0 , 0 , 0.2]) * 1.0
    Migration_fraction_20_to_24_cohort = np.array([0 , 0.2 , 0 , 0.2 , 0 , 0 , 0 , 0 , 0 , 0.2]) * 1.0
    Migration_fraction_25_to_29_cohort = np.array([0.3 , 0.2 , 0 , 0.2 , 0 , 0 , 0 , 0 , 0 , 0.2]) * 1.0
    Migration_fraction_30_to_34_cohort = np.array([0 , 0.2 , 0 , 0.2 , 0 , 0 , 0 , 0 , 0 , 0.2]) * 1.0
    nmf_a = np.array([0.4133 , -0.3 , -0.16 , 0.0889 , 2.78 , 0.4073 , 0.4322 , 0.4812 , 1.7649 , -0.3]) * 1.0
    nmf_b = np.array([-0.6174 , 0.1 , 0.0969 , -0.1085 , -1.716 , -1.6676 , -1.1157 , -1.3905 , -4.8616 , 0.1]) * 1.0
    nmf_c = np.array([0 , 0 , 0 , 0 , -1.58 , 0 , 0 , 0 , 0 , 0]) * 1.0
    Population_in_1979 = np.array([230 , 356 , 1017 , 179 , 861 , 355 , 215 , 326 , 484 , 356]) * 1.0
    Time_to_adjust_cultural_birth_rate_norm = np.array([1 , 10 , 1 , 5 , 5 , 3 , 1 , 2 , 1 , 2]) * 1.0
    Time_to_adjust_work_hours = np.array([0.5 , 0.25 , 0.25 , 0.5 , 0.5 , 0.5 , 0.5 , 0.5 , 0.5 , 0.25]) * 1.0

    oo = np.load(path+'Capacity_in_1980.npy')
    Capacity_in_1980 = oo[:,0] # make correct shape for later
    oo = np.load(path+'Capacity_under_construction_in_1980.npy')
    Capacity_under_construction_in_1980 = oo[:,0] # make correct shape for later
    oo = np.load(path+'Corporate_borrowing_cost_in_1980.npy')
    Corporate_borrowing_cost_in_1980 = oo[:,0] # make correct shape for later
    oo = np.load(path+'Optimal_output_in_1980.npy')
    Optimal_output_in_1980 = oo[:,0] # make correct shape for later
    oo = np.load(path+'GDPpp_in_1980.npy')
    GDPpp_in_1980 = oo[:,0] # make correct shape for later
    oo = np.load(path+'Inventory_in_1980.npy')
    Inventory_in_1980 = oo[:,0] # make correct shape for later
    # initial        CG
    LW_TOA_radiation_from_atm_to_space_in_1850 = 3826.2
    oo = np.load(path+'Owner_wealth_accumulated_in_1980.npy')
    Owner_wealth_accumulated_in_1980 = oo[:,0] # make correct shape for later
    oo = np.load(path+'Public_Capacity_in_1980.npy')
    Public_Capacity_in_1980 = oo[:,0] # make correct shape for later
#    oo = np.load(path+'Speculative_asset_pool_relative_to_init_in_1980.npy')
#    Speculative_asset_pool_relative_to_init_in_1980 = oo[:,0] # make correct shape for later
    oo = np.load(path+'Demand_in_1980.npy')
    Demand_in_1980 = oo[:,0] # make correct shape for later
    oo = np.load(path+'Worker_income_after_tax_in_1980.npy')
    Worker_income_after_tax_in_1980 = oo[:,0] # make correct shape for later
    oo = np.load(path+'Workers_debt_in_1980.npy')
    Workers_debt_in_1980 = oo[:,0] # make correct shape for later
    Global_forest_land_in_1980 = float(np.load(path+'Global_forest_land_in_1980.npy'))
    oo = np.load(path+'Output_last_year_in_1980.npy')
    Output_last_year_in_1980 = oo[:,0] # make correct shape for later

### runde = 99: run from 80 to 90
### runde = 0: run from 90 to 2025
### runde = 1: run from 2025 to 2040
### runde = 2: run from 2040 to 2060
### runde = 2: run from 2060 to 2100

    dt = 1 / 32
    if runde == 99: ### runde = 99: run from 80 to 90
        row_start = np.load(path+'ro80.npy')
        start_mod = 1980
        zeit = start_mod
        end_mod = 1990
        time_slots = int((end_mod - start_mod) * (1 / dt) + 1)
        cols = len(ch)
        # set up the data matrix with ALL columns and rows according to current timeslots
        mdf = np.full((time_slots, cols), np.nan)
        tid = np.linspace(start_mod, end_mod, time_slots)
        mdf[:, 0] = tid
        mdf[0, :] = row_start
        start_tick_in_mdf_play = 1
        start_tick = 1
        end_tick = int((end_mod - start_mod) / dt + 1)
        ## set up mdf_plot
        plot_cols = len(plot_var_list) + 1
        mdf_plot = np.full((time_slots, plot_cols), np.nan)
        mdf_plot[:, 0] = tid
        mdf_plot = fill_mdf_plot_row_start(runde, mdf_plot, ch, plot_var_list, plot_var_list_10, row_start, 0)
    elif runde == 0:
        row_start = np.load(path+'ro90.npy')
        start_mod = 1990
        zeit = start_mod
        end_mod = 2025
        time_slots = int((end_mod - start_mod) * (1 / dt) + 1)
        cols = len(ch)
        # set up the data matrix with ALL columns and rows according to current timeslots
        mdf = np.full((time_slots, cols), np.nan)
        tid = np.linspace(start_mod, end_mod, time_slots)
        mdf[:, 0] = tid
        mdf[0, :] = row_start
        start_tick_in_mdf_play = 1
        start_tick = 1
        end_tick = int((end_mod - start_mod) / dt + 1)
        ## set up mdf_plot
        plot_cols = len(plot_var_list) + 1
        mdf_plot = np.full((time_slots, plot_cols), np.nan)
        mdf_plot[:, 0] = tid
        mdf_plot = fill_mdf_plot_row_start(runde, mdf_plot, ch, plot_var_list, plot_var_list_10, row_start, 0)
    elif runde == 1:
        row_start = np.load(path+'ro25.npy')
        start_mod = 2025
        zeit = start_mod
        end_mod = 2040
        time_slots = int((end_mod - start_mod) * (1 / dt) + 1)
        cols = len(ch)
        # set up the data matrix with ALL columns and rows according to current timeslots
        mdf = np.full((time_slots, cols), np.nan)
        tid = np.linspace(start_mod, end_mod, time_slots)
        mdf[:, 0] = tid
        mdf[0, :] = row_start
        start_tick_in_mdf_play = 1
        start_tick = 1
        end_tick = int((end_mod - start_mod) / dt + 1)
        ## set up mdf_plot
        plot_cols = len(plot_var_list) + 1
        mdf_plot = np.full((time_slots, plot_cols), np.nan)
        mdf_plot[:, 0] = tid
        mdf_plot = fill_mdf_plot_row_start(runde, mdf_plot, ch, plot_var_list, plot_var_list_10, row_start, 0)
    elif runde == 2:
        row_start = np.load(path+game_id+'_ro40.npy')
        start_mod = 2040
        zeit = start_mod
        end_mod = 2060
        time_slots = int((end_mod - start_mod) * (1 / dt) + 1)
        cols = len(ch)
        # set up the data matrix with ALL columns and rows according to current timeslots
        mdf = np.full((time_slots, cols), np.nan)
        tid = np.linspace(start_mod, end_mod, time_slots)
        mdf[:, 0] = tid
        mdf[0, :] = row_start
        start_tick_in_mdf_play = 1
        start_tick = 1
        end_tick = int((end_mod - start_mod) / dt + 1)
        ## set up mdf_plot
        plot_cols = len(plot_var_list) + 1
        mdf_plot = np.full((time_slots, plot_cols), np.nan)
        mdf_plot[:, 0] = tid
        mdf_plot = fill_mdf_plot_row_start(runde, mdf_plot, ch, plot_var_list, plot_var_list_10, row_start, 0)
    elif runde == 3:
        row_start = np.load(path + game_id + '_ro60.npy')
        start_mod = 2060
        zeit = start_mod
        end_mod = 2100
        time_slots = int((end_mod - start_mod) * (1 / dt) + 1)
        cols = len(ch)
        # set up the data matrix with ALL columns and rows according to current timeslots
        mdf = np.full((time_slots, cols), np.nan)
        tid = np.linspace(start_mod, end_mod, time_slots)
        mdf[:, 0] = tid
        mdf[0, :] = row_start
        start_tick_in_mdf_play = 1
        start_tick = 1
        end_tick = int((end_mod - start_mod) / dt + 1)
        ## set up mdf_plot
        plot_cols = len(plot_var_list) + 1
        mdf_plot = np.full((time_slots, plot_cols), np.nan)
        mdf_plot[:, 0] = tid
        mdf_plot = fill_mdf_plot_row_start(runde, mdf_plot, ch, plot_var_list, plot_var_list_10, row_start, 0)
        pass
    elif runde == 3:
        pass
    else:
        print('We have a problem in def run_game with von and bis')

    over_end = time.time()
#    print("over_end: " + str(over_end-over_start))
    ###################
    #
    # loop to run the model
    #
    yr = int(zeit)
    for rowi in range(start_tick, end_tick):
        loop_start = time.time()
        loop_tot = 0
        nat_tot = 0
        store_tot = 0
        zeit = zeit + dt
        slot = mdf[rowi,0]
        if not zeit == slot:
            print(zeit)
#        print(str(rowi)+' '+ str(mdf[rowi,0])+' '+ str(mdf[rowi,1]))
        jjyr = rowi - 1
        if jjyr % 32 == 0:
#            print(yr)
            print('.',end='')
            yr += 1

     
    # Abandoned_crop_and_grazing_land[region] = INTEG ( c_to_acgl[region] + gl_to_acgl[region] + apl_to_acgl[region] - acgl_to_c[region] - acgl_to_fa[region] - acgl_to_gl[region] - acgl_to_pl[region] , 0 )
        idx1 = fcol_in_mdf['Abandoned_crop_and_grazing_land']
        idx2 = fcol_in_mdf['c_to_acgl']
        idx3 = fcol_in_mdf['gl_to_acgl']
        idx4 = fcol_in_mdf['apl_to_acgl']
        idx5 = fcol_in_mdf['acgl_to_c']
        idx6 = fcol_in_mdf['acgl_to_fa']
        idx7 = fcol_in_mdf['acgl_to_gl']
        idx8 = fcol_in_mdf['acgl_to_pl']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] + mdf[rowi-1, idx3:idx3 + 10] + mdf[rowi-1, idx4:idx4 + 10] - mdf[rowi-1, idx5:idx5 + 10] - mdf[rowi-1, idx6:idx6 + 10] - mdf[rowi-1, idx7:idx7 + 10] - mdf[rowi-1, idx8:idx8 + 10] ) * dt
     
    # Abandoned_populated_land[region] = INTEG ( pl_to_apl[region] - apl_to_pl[region] - apl_to_acgl[region] , 0 )
        idx1 = fcol_in_mdf['Abandoned_populated_land']
        idx2 = fcol_in_mdf['pl_to_apl']
        idx3 = fcol_in_mdf['apl_to_pl']
        idx4 = fcol_in_mdf['apl_to_acgl']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] - mdf[rowi-1, idx4:idx4 + 10] ) * dt
     
    # Antarctic_ice_volume_km3 = INTEG ( - Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py , Antarctic_ice_volume_in_1980 )
        idx1 = fcol_in_mdf['Antarctic_ice_volume_km3']
        idx2 = fcol_in_mdf['Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( - mdf[rowi-1, idx2] ) * dt
     
    # Arctic_ice_on_sea_area_km2 = INTEG ( - Arctic_ice_melting_is_pos_or_freezing_is_neg_km2_py , Arctic_ice_area_in_1980_km2 )
        idx1 = fcol_in_mdf['Arctic_ice_on_sea_area_km2']
        idx2 = fcol_in_mdf['Arctic_ice_melting_is_pos_or_freezing_is_neg_km2_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( - mdf[rowi-1, idx2] ) * dt
     
    # Barren_land_which_is_ice_and_snow[region] = INTEG ( future_deforestation[region] + historical_deforestation[region] - Reforestation_policy[region] , Barren_land_in_1980[region] )
        idx1 = fcol_in_mdf['Barren_land_which_is_ice_and_snow']
        idx2 = fcol_in_mdf['future_deforestation']
        idx3 = fcol_in_mdf['historical_deforestation']
        idx4 = fcol_in_mdf['Reforestation_policy']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] + mdf[rowi-1, idx3:idx3 + 10] - mdf[rowi-1, idx4:idx4 + 10] ) * dt
     
    # C_in_atmosphere_GtC = INTEG ( Avg_volcanic_activity_GtC_py + C_release_from_permafrost_melting_as_CO2_GtC_py + CH4_in_the_atmosphere_converted_to_CO2 + CO2_flux_GRASS_to_atm_GtC_py + CO2_flux_NF_to_atm_GtC_py + CO2_flux_TROP_to_atm_GtC_py + CO2_flux_TUNDRA_to_atm + Man_made_fossil_C_emissions_GtC_py - C_diffusion_into_ocean_from_atm_net - Carbon_captured_and_stored_GtC_py - CO2_flux_from_atm_to_GRASS_for_new_growth_GtC_py - CO2_flux_from_atm_to_NF_for_new_growth_GtC_py - CO2_flux_from_atm_to_TROP_for_new_growth_GtC_py - CO2_flux_from_atm_to_TUNDRA_for_new_growth , C_in_atmosphere_in_1980 )
        idx1 = fcol_in_mdf['C_in_atmosphere_GtC']
        idx2 = fcol_in_mdf['Avg_volcanic_activity_GtC_py']
        idx3 = fcol_in_mdf['C_release_from_permafrost_melting_as_CO2_GtC_py']
        idx4 = fcol_in_mdf['CH4_in_the_atmosphere_converted_to_CO2']
        idx5 = fcol_in_mdf['CO2_flux_GRASS_to_atm_GtC_py']
        idx6 = fcol_in_mdf['CO2_flux_NF_to_atm_GtC_py']
        idx7 = fcol_in_mdf['CO2_flux_TROP_to_atm_GtC_py']
        idx8 = fcol_in_mdf['CO2_flux_TUNDRA_to_atm']
        idx9 = fcol_in_mdf['Man_made_fossil_C_emissions_GtC_py']
        idx10 = fcol_in_mdf['C_diffusion_into_ocean_from_atm_net']
        idx11 = fcol_in_mdf['Carbon_captured_and_stored_GtC_py']
        idx12 = fcol_in_mdf['CO2_flux_from_atm_to_GRASS_for_new_growth_GtC_py']
        idx13 = fcol_in_mdf['CO2_flux_from_atm_to_NF_for_new_growth_GtC_py']
        idx14 = fcol_in_mdf['CO2_flux_from_atm_to_TROP_for_new_growth_GtC_py']
        idx15 = fcol_in_mdf['CO2_flux_from_atm_to_TUNDRA_for_new_growth']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] + mdf[rowi-1, idx3] + mdf[rowi-1, idx4] + mdf[rowi-1, idx5] + mdf[rowi-1, idx6] + mdf[rowi-1, idx7] + mdf[rowi-1, idx8] + mdf[rowi-1, idx9] - mdf[rowi-1, idx10] - mdf[rowi-1, idx11] - mdf[rowi-1, idx12] - mdf[rowi-1, idx13] - mdf[rowi-1, idx14] - mdf[rowi-1, idx15] ) * dt
     
    # C_in_atmosphere_in_form_of_CH4 = INTEG ( CH4_release_or_capture_from_permafrost_area_loss_or_gain_GtC_py + Human_activity_CH4_emissions + Natural_CH4_emissions - CH4_conversion_to_CO2_and_H2O , C_in_the_form_of_CH4_in_atm_1980 )
        idx1 = fcol_in_mdf['C_in_atmosphere_in_form_of_CH4']
        idx2 = fcol_in_mdf['CH4_release_or_capture_from_permafrost_area_loss_or_gain_GtC_py']
        idx3 = fcol_in_mdf['Human_activity_CH4_emissions']
        idx4 = fcol_in_mdf['CH4_conversion_to_CO2_and_H2O']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] + mdf[rowi-1, idx3] + Natural_CH4_emissions - mdf[rowi-1, idx4] ) * dt
     
    # C_in_cold_surface_water_GtC = INTEG ( C_diffusion_into_ocean_from_atm_net + Carbon_flow_from_warm_to_cold_surface_GtC_per_yr - Carbon_flow_from_cold_surface_downwelling_Gtc_per_yr , Carbon_in_cold_ocean_0_to_100m_1850 )
        idx1 = fcol_in_mdf['C_in_cold_surface_water_GtC']
        idx2 = fcol_in_mdf['C_diffusion_into_ocean_from_atm_net']
        idx3 = fcol_in_mdf['Carbon_flow_from_warm_to_cold_surface_GtC_per_yr']
        idx4 = fcol_in_mdf['Carbon_flow_from_cold_surface_downwelling_Gtc_per_yr']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] + mdf[rowi-1, idx3] - mdf[rowi-1, idx4] ) * dt
     
    # C_in_cold_water_trunk_downwelling_GtC = INTEG ( Carbon_flow_from_cold_surface_downwelling_Gtc_per_yr - Carbon_flow_from_cold_to_deep_GtC_per_yr , Carbon_in_cold_ocean_trunk_100m_to_bottom_1850 )
        idx1 = fcol_in_mdf['C_in_cold_water_trunk_downwelling_GtC']
        idx2 = fcol_in_mdf['Carbon_flow_from_cold_surface_downwelling_Gtc_per_yr']
        idx3 = fcol_in_mdf['Carbon_flow_from_cold_to_deep_GtC_per_yr']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] ) * dt
     
    # C_in_deep_water_volume_1km_to_bottom_GtC = INTEG ( Carbon_flow_from_cold_to_deep_GtC_per_yr - Depositing_of_C_to_sediment - Carbon_flow_from_deep , Carbon_in_ocean_deep_1k_to_bottom_ocean_1850 )
        idx1 = fcol_in_mdf['C_in_deep_water_volume_1km_to_bottom_GtC']
        idx2 = fcol_in_mdf['Carbon_flow_from_cold_to_deep_GtC_per_yr']
        idx3 = fcol_in_mdf['Depositing_of_C_to_sediment']
        idx4 = fcol_in_mdf['Carbon_flow_from_deep']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] - mdf[rowi-1, idx4] ) * dt
     
    # C_in_intermediate_upwelling_water_100m_to_1km_GtC = INTEG ( Carbon_flow_from_deep - Carbon_flow_from_intermediate_to_surface_box_GtC_per_yr , Carbon_in_ocean_upwelling_100m_to_1km_1850 )
        idx1 = fcol_in_mdf['C_in_intermediate_upwelling_water_100m_to_1km_GtC']
        idx2 = fcol_in_mdf['Carbon_flow_from_deep']
        idx3 = fcol_in_mdf['Carbon_flow_from_intermediate_to_surface_box_GtC_per_yr']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] ) * dt
     
    # C_in_permafrost_in_form_of_CH4 = INTEG ( - CH4_release_or_capture_from_permafrost_area_loss_or_gain_GtC_py , 1199.78 )
        idx1 = fcol_in_mdf['C_in_permafrost_in_form_of_CH4']
        idx2 = fcol_in_mdf['CH4_release_or_capture_from_permafrost_area_loss_or_gain_GtC_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( - mdf[rowi-1, idx2] ) * dt
     
    # C_in_warm_surface_water_GtC = INTEG ( Carbon_flow_from_intermediate_to_surface_box_GtC_per_yr + C_runoff_from_biomass_soil - Biological_removal_of_C_from_WSW_GtC_per_yr - Carbon_flow_from_warm_to_cold_surface_GtC_per_yr , Carbon_in_warm_ocean_0_to_100m_1850 )
        idx1 = fcol_in_mdf['C_in_warm_surface_water_GtC']
        idx2 = fcol_in_mdf['Carbon_flow_from_intermediate_to_surface_box_GtC_per_yr']
        idx3 = fcol_in_mdf['C_runoff_from_biomass_soil']
        idx4 = fcol_in_mdf['Biological_removal_of_C_from_WSW_GtC_per_yr']
        idx5 = fcol_in_mdf['Carbon_flow_from_warm_to_cold_surface_GtC_per_yr']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] + mdf[rowi-1, idx3] - mdf[rowi-1, idx4] - mdf[rowi-1, idx5] ) * dt
     
    # Capacity[region] = INTEG ( Adding_capacity[region] - Discarding_capacity[region] , Capacity_in_1980[region] )
        idx1 = fcol_in_mdf['Capacity']
        idx2 = fcol_in_mdf['Adding_capacity']
        idx3 = fcol_in_mdf['Discarding_capacity']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] ) * dt
     
    # Capacity_under_construction[region] = INTEG ( Initiating_capacity_construction[region] - Adding_capacity[region] , Capacity_under_construction_in_1980[region] )
        idx1 = fcol_in_mdf['Capacity_under_construction']
        idx2 = fcol_in_mdf['Initiating_capacity_construction']
        idx3 = fcol_in_mdf['Adding_capacity']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] ) * dt
     
    # Central_bank_signal_rate[region] = INTEG ( Change_in_signal_rate[region] , Central_bank_signal_rate_in_1980[region] )
        idx1 = fcol_in_mdf['Central_bank_signal_rate']
        idx2 = fcol_in_mdf['Change_in_signal_rate']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] ) * dt
     
    # Cohort_0_to_4[region] = INTEG ( Births[region] - Aging_4_to_5[region] - dying_0_to_4[region] , Cohort_0_to_4_in_1980[region] )
        idx1 = fcol_in_mdf['Cohort_0_to_4']
        idx2 = fcol_in_mdf['Births']
        idx3 = fcol_in_mdf['Aging_4_to_5']
        idx4 = fcol_in_mdf['dying_0_to_4']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] - mdf[rowi-1, idx4:idx4 + 10] ) * dt
     
    # Cohort_10_to_14[region] = INTEG ( Aging_9_to_10[region] - Aging_14_to_15[region] + net_migration_10_to_14[region] , Cohort_10_to_14_in_1980[region] )
        idx1 = fcol_in_mdf['Cohort_10_to_14']
        idx2 = fcol_in_mdf['Aging_9_to_10']
        idx3 = fcol_in_mdf['Aging_14_to_15']
        idx4 = fcol_in_mdf['net_migration_10_to_14']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] + mdf[rowi-1, idx4:idx4 + 10] ) * dt
     
    # Cohort_15_to_19[region] = INTEG ( Aging_14_to_15[region] - Aging_19_to_20[region] , Cohort_15_to_19_in_1980[region] )
        idx1 = fcol_in_mdf['Cohort_15_to_19']
        idx2 = fcol_in_mdf['Aging_14_to_15']
        idx3 = fcol_in_mdf['Aging_19_to_20']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] ) * dt
     
    # Cohort_20_to_24[region] = INTEG ( Aging_19_to_20[region] - Aging_24_to_25[region] + net_migration_20_to_24[region] , Cohort_20_to_24_in_1980[region] )
        idx1 = fcol_in_mdf['Cohort_20_to_24']
        idx2 = fcol_in_mdf['Aging_19_to_20']
        idx3 = fcol_in_mdf['Aging_24_to_25']
        idx4 = fcol_in_mdf['net_migration_20_to_24']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] + mdf[rowi-1, idx4:idx4 + 10] ) * dt
     
    # Cohort_25_to_29[region] = INTEG ( Aging_24_to_25[region] - Aging_29_to_30[region] + net_migration_25_to_29[region] , Cohort_25_to_29_in_1980[region] )
        idx1 = fcol_in_mdf['Cohort_25_to_29']
        idx2 = fcol_in_mdf['Aging_24_to_25']
        idx3 = fcol_in_mdf['Aging_29_to_30']
        idx4 = fcol_in_mdf['net_migration_25_to_29']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] + mdf[rowi-1, idx4:idx4 + 10] ) * dt
     
    # Cohort_30_to_34[region] = INTEG ( Aging_29_to_30[region] - Aging_34_to_35[region] + net_migration_30_to_34[region] , Cohort_30_to_34_in_1980[region] )
        idx1 = fcol_in_mdf['Cohort_30_to_34']
        idx2 = fcol_in_mdf['Aging_29_to_30']
        idx3 = fcol_in_mdf['Aging_34_to_35']
        idx4 = fcol_in_mdf['net_migration_30_to_34']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] + mdf[rowi-1, idx4:idx4 + 10] ) * dt
     
    # Cohort_35_to_39[region] = INTEG ( Aging_34_to_35[region] - Aging_39_to_40[region] - dying_35_to_39[region] , Cohort_35_to_39_in_1980[region] )
        idx1 = fcol_in_mdf['Cohort_35_to_39']
        idx2 = fcol_in_mdf['Aging_34_to_35']
        idx3 = fcol_in_mdf['Aging_39_to_40']
        idx4 = fcol_in_mdf['dying_35_to_39']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] - mdf[rowi-1, idx4:idx4 + 10] ) * dt
     
    # Cohort_40_to_44[region] = INTEG ( Aging_39_to_40[region] - Aging_44_to_45[region] - dying_40_to_45[region] , Cohort_40to_44_in_1980[region] )
        idx1 = fcol_in_mdf['Cohort_40_to_44']
        idx2 = fcol_in_mdf['Aging_39_to_40']
        idx3 = fcol_in_mdf['Aging_44_to_45']
        idx4 = fcol_in_mdf['dying_40_to_45']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] - mdf[rowi-1, idx4:idx4 + 10] ) * dt
     
    # Cohort_45_to_49[region] = INTEG ( Aging_44_to_45[region] - Aging_49_to_50[region] - dying_45_to_49[region] , Cohort_45_to_49_in_1980[region] )
        idx1 = fcol_in_mdf['Cohort_45_to_49']
        idx2 = fcol_in_mdf['Aging_44_to_45']
        idx3 = fcol_in_mdf['Aging_49_to_50']
        idx4 = fcol_in_mdf['dying_45_to_49']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] - mdf[rowi-1, idx4:idx4 + 10] ) * dt
     
    # Cohort_5_to_9[region] = INTEG ( Aging_4_to_5[region] - Aging_9_to_10[region] , Cohort_5_to_9_in_1980[region] )
        idx1 = fcol_in_mdf['Cohort_5_to_9']
        idx2 = fcol_in_mdf['Aging_4_to_5']
        idx3 = fcol_in_mdf['Aging_9_to_10']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] ) * dt
     
    # Cohort_50_to_54[region] = INTEG ( Aging_49_to_50[region] - Aging_54_to_55[region] - dying_50_to_54[region] , Cohort_50_to_54_in_1980[region] )
        idx1 = fcol_in_mdf['Cohort_50_to_54']
        idx2 = fcol_in_mdf['Aging_49_to_50']
        idx3 = fcol_in_mdf['Aging_54_to_55']
        idx4 = fcol_in_mdf['dying_50_to_54']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] - mdf[rowi-1, idx4:idx4 + 10] ) * dt
     
    # Cohort_55_to_59[region] = INTEG ( Aging_54_to_55[region] - Aging_59_to_60[region] - dying_55_to_59[region] , Cohort_55_to_59_in_1980[region] )
        idx1 = fcol_in_mdf['Cohort_55_to_59']
        idx2 = fcol_in_mdf['Aging_54_to_55']
        idx3 = fcol_in_mdf['Aging_59_to_60']
        idx4 = fcol_in_mdf['dying_55_to_59']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] - mdf[rowi-1, idx4:idx4 + 10] ) * dt
     
    # Cohort_60_to_64[region] = INTEG ( Aging_59_to_60[region] - Aging_64_to_65[region] - dying_60_to_64[region] , Cohort_60to_64_in_1980[region] )
        idx1 = fcol_in_mdf['Cohort_60_to_64']
        idx2 = fcol_in_mdf['Aging_59_to_60']
        idx3 = fcol_in_mdf['Aging_64_to_65']
        idx4 = fcol_in_mdf['dying_60_to_64']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] - mdf[rowi-1, idx4:idx4 + 10] ) * dt
     
    # Cohort_65_to_69[region] = INTEG ( Aging_64_to_65[region] - Aging_69_to_70[region] - dying_65_to_69[region] , Cohort_65_to_69_in_1980[region] )
        idx1 = fcol_in_mdf['Cohort_65_to_69']
        idx2 = fcol_in_mdf['Aging_64_to_65']
        idx3 = fcol_in_mdf['Aging_69_to_70']
        idx4 = fcol_in_mdf['dying_65_to_69']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] - mdf[rowi-1, idx4:idx4 + 10] ) * dt
     
    # Cohort_70_to_74[region] = INTEG ( Aging_69_to_70[region] - Aging_74_to_75[region] - dying_70_to_74[region] , Cohort_70_to_74_in_1980[region] )
        idx1 = fcol_in_mdf['Cohort_70_to_74']
        idx2 = fcol_in_mdf['Aging_69_to_70']
        idx3 = fcol_in_mdf['Aging_74_to_75']
        idx4 = fcol_in_mdf['dying_70_to_74']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] - mdf[rowi-1, idx4:idx4 + 10] ) * dt
     
    # Cohort_75_to_79[region] = INTEG ( Aging_74_to_75[region] - Aging_79_to_80[region] - dying_75_to_79[region] , Cohort_75_to_79_in_1980[region] )
        idx1 = fcol_in_mdf['Cohort_75_to_79']
        idx2 = fcol_in_mdf['Aging_74_to_75']
        idx3 = fcol_in_mdf['Aging_79_to_80']
        idx4 = fcol_in_mdf['dying_75_to_79']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] - mdf[rowi-1, idx4:idx4 + 10] ) * dt
     
    # Cohort_80_to_84[region] = INTEG ( Aging_79_to_80[region] - Aging_84_to_85[region] - dying_80_to_84[region] , Cohort_80_to_84_in_1980[region] )
        idx1 = fcol_in_mdf['Cohort_80_to_84']
        idx2 = fcol_in_mdf['Aging_79_to_80']
        idx3 = fcol_in_mdf['Aging_84_to_85']
        idx4 = fcol_in_mdf['dying_80_to_84']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] - mdf[rowi-1, idx4:idx4 + 10] ) * dt
     
    # Cohort_85_to_89[region] = INTEG ( Aging_84_to_85[region] - Aging_89_to_90[region] - dying_85_to_89[region] , Cohort_85_to_89_in_1980[region] )
        idx1 = fcol_in_mdf['Cohort_85_to_89']
        idx2 = fcol_in_mdf['Aging_84_to_85']
        idx3 = fcol_in_mdf['Aging_89_to_90']
        idx4 = fcol_in_mdf['dying_85_to_89']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] - mdf[rowi-1, idx4:idx4 + 10] ) * dt
     
    # Cohort_90_to_94[region] = INTEG ( Aging_89_to_90[region] - Aging_95_to_95plus[region] - dying_90_to_94[region] , Cohort_90_to_94_in_1980[region] )
        idx1 = fcol_in_mdf['Cohort_90_to_94']
        idx2 = fcol_in_mdf['Aging_89_to_90']
        idx3 = fcol_in_mdf['Aging_95_to_95plus']
        idx4 = fcol_in_mdf['dying_90_to_94']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] - mdf[rowi-1, idx4:idx4 + 10] ) * dt
     
    # Cohort_95p[region] = INTEG ( Aging_95_to_95plus[region] - dying_95p[region] , Cohort_95p_in_1980[region] )
        idx1 = fcol_in_mdf['Cohort_95p']
        idx2 = fcol_in_mdf['Aging_95_to_95plus']
        idx3 = fcol_in_mdf['dying_95p']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] ) * dt
     
    # Cropland[region] = INTEG ( acgl_to_c[region] + fa_to_c[region] - c_to_acgl[region] - c_to_pl[region] , Cropland_in_1980[region] )
        idx1 = fcol_in_mdf['Cropland']
        idx2 = fcol_in_mdf['acgl_to_c']
        idx3 = fcol_in_mdf['fa_to_c']
        idx4 = fcol_in_mdf['c_to_acgl']
        idx5 = fcol_in_mdf['c_to_pl']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] + mdf[rowi-1, idx3:idx3 + 10] - mdf[rowi-1, idx4:idx4 + 10] - mdf[rowi-1, idx5:idx5 + 10] ) * dt
     
    # Cumulative_N_use_since_2020[region] = INTEG ( Addition_to_N_use_over_the_years[region] , Cumulative_N_use_since_2020_in_1980[region] )
        idx1 = fcol_in_mdf['Cumulative_N_use_since_2020']
        idx2 = fcol_in_mdf['Addition_to_N_use_over_the_years']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] ) * dt
     
    # Cumulative_ocean_volume_increase_due_to_ice_melting_km3 = INTEG ( Antarctic_ice_melting_as_water_km3_py + Glacial_ice_melting_as_water_km3_py + Greenland_ice_melting_as_water_km3_py , 46498.3 )
        idx1 = fcol_in_mdf['Cumulative_ocean_volume_increase_due_to_ice_melting_km3']
        idx2 = fcol_in_mdf['Antarctic_ice_melting_as_water_km3_py']
        idx3 = fcol_in_mdf['Glacial_ice_melting_as_water_km3_py']
        idx4 = fcol_in_mdf['Greenland_ice_melting_as_water_km3_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] + mdf[rowi-1, idx3] + mdf[rowi-1, idx4] ) * dt
     
    # Delivery_delay_index[region] = INTEG ( Change_in_delivery_delay_index[region] , 1 )
        idx1 = fcol_in_mdf['Delivery_delay_index']
        idx2 = fcol_in_mdf['Change_in_delivery_delay_index']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] ) * dt
     
    # DESERT_Mkm2 = INTEG ( Shifting_GRASS_to_DESERT_Mkm2_py - Shifting_DESERT_to_GRASS_Mkm2_py , 25.4039 )
        idx1 = fcol_in_mdf['DESERT_Mkm2']
        idx2 = fcol_in_mdf['Shifting_GRASS_to_DESERT_Mkm2_py']
        idx3 = fcol_in_mdf['Shifting_DESERT_to_GRASS_Mkm2_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] ) * dt
     
    # Embedded_TFP[region] = INTEG ( Effect_of_capacity_renewal[region] , 1 )
        idx1 = fcol_in_mdf['Embedded_TFP']
        idx2 = fcol_in_mdf['Effect_of_capacity_renewal']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] ) * dt
     
    # Employed[region] = INTEG ( Getting_a_job[region] - Loosing_a_job[region] , Employed_in_1980[region] )
        idx1 = fcol_in_mdf['Employed']
        idx2 = fcol_in_mdf['Getting_a_job']
        idx3 = fcol_in_mdf['Loosing_a_job']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] ) * dt
     
    # Extra_energy_productivity_index_2024_is_1[region] = INTEG ( Increase_in_exepi[region] , 1 )
        idx1 = fcol_in_mdf['Extra_energy_productivity_index_2024_is_1']
        idx2 = fcol_in_mdf['Increase_in_exepi']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] ) * dt
     
    # Forest_land[region] = INTEG ( acgl_to_fa[region] - historical_deforestation[region] + Reforestation_policy[region] - fa_to_c[region] - fa_to_gl[region] - future_deforestation[region] , Forest_land_in_1980[region] )
        idx1 = fcol_in_mdf['Forest_land']
        idx2 = fcol_in_mdf['acgl_to_fa']
        idx3 = fcol_in_mdf['historical_deforestation']
        idx4 = fcol_in_mdf['Reforestation_policy']
        idx5 = fcol_in_mdf['fa_to_c']
        idx6 = fcol_in_mdf['fa_to_gl']
        idx7 = fcol_in_mdf['future_deforestation']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] + mdf[rowi-1, idx4:idx4 + 10] - mdf[rowi-1, idx5:idx5 + 10] - mdf[rowi-1, idx6:idx6 + 10] - mdf[rowi-1, idx7:idx7 + 10] ) * dt
     
    # Fossil_el_gen_cap[region] = INTEG ( Addition_of_FEGC[region] - Discarding_of_FEGC[region] , Fossil_el_gen_cap_in_1980[region] )
        idx1 = fcol_in_mdf['Fossil_el_gen_cap']
        idx2 = fcol_in_mdf['Addition_of_FEGC']
        idx3 = fcol_in_mdf['Discarding_of_FEGC']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] ) * dt
     
    # Fossil_fuel_reserves_in_ground_GtC = INTEG ( - Man_made_fossil_C_emissions_GtC_py , Fossil_fuel_reserves_in_ground_at_initial_time_GtC )
        idx1 = fcol_in_mdf['Fossil_fuel_reserves_in_ground_GtC']
        idx2 = fcol_in_mdf['Man_made_fossil_C_emissions_GtC_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( - mdf[rowi-1, idx2] ) * dt
     
    # Fraction_of_people_outside_of_labour_market_FOPOLM[region] = INTEG ( Change_in_Fraction_of_people_outside_of_labour_market[region] , Frac_outside_of_labour_pool_in_1980[region] )
        idx1 = fcol_in_mdf['Fraction_of_people_outside_of_labour_market_FOPOLM']
        idx2 = fcol_in_mdf['Change_in_Fraction_of_people_outside_of_labour_market']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] ) * dt
    
    # Optimal_real_output[region] = Optimal_output_in_1980[region] * ( Capacity[region] / Capacity_in_1980[region] ) ^ Kappa * ( Employed[region] / Employed_in_1980[region] ) ^ Lambdav * ( Embedded_TFP[region] )
        idxlhs = fcol_in_mdf['Optimal_real_output']
        idx1 = fcol_in_mdf['Capacity']
        idx2 = fcol_in_mdf['Employed']
        idx3 = fcol_in_mdf['Embedded_TFP']
        mdf[rowi, idxlhs:idxlhs + 10] =  Optimal_output_in_1980[0:10]  *  ( mdf[rowi , idx1:idx1 + 10] /  Capacity_in_1980[0:10]  )  **  Kappa  *  ( mdf[rowi , idx2:idx2 + 10] /  Employed_in_1980[0:10]  )  **  Lambdav  *  ( mdf[rowi , idx3:idx3 + 10] ) 
    
    # Perceived_relative_inventory[region] = SMOOTHI ( Inventory_coverage_to_goal_ratio[region] , Inventory_coverage_perception_time , Perceived_relative_inventory_in_1980[region] )
        idx1 = fcol_in_mdf['Perceived_relative_inventory']
        idx2 = fcol_in_mdf['Inventory_coverage_to_goal_ratio']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi - 1, idx1:idx1 + 10]) / Inventory_coverage_perception_time * dt
    
    # Indicated_hours_worked_index[region] = 1 + SoE_of_inventory_on_indicated_hours_worked_index[region] * ( Perceived_relative_inventory[region] / Goal_for_relative_inventory - 1 )
        idxlhs = fcol_in_mdf['Indicated_hours_worked_index']
        idx1 = fcol_in_mdf['Perceived_relative_inventory']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  +  SoE_of_inventory_on_indicated_hours_worked_index[0:10]  *  ( mdf[rowi , idx1:idx1 + 10] /  Goal_for_relative_inventory  -  1  ) 
    
    # Hours_worked_index[region] = SMOOTH ( Indicated_hours_worked_index[region] , Time_to_adjust_work_hours[region] )
        idx1 = fcol_in_mdf['Hours_worked_index']
        idx2 = fcol_in_mdf['Indicated_hours_worked_index']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1+10] + ( mdf[rowi-1 , idx2:idx2 + 10] - mdf[rowi -1 , idx1:idx1 + 10]) / Time_to_adjust_work_hours[0:10] * dt
    
    # Output[region] = Optimal_real_output[region] * Hours_worked_index[region] / Hours_worked_index_in_1980[region]
        idxlhs = fcol_in_mdf['Output']
        idx1 = fcol_in_mdf['Optimal_real_output']
        idx2 = fcol_in_mdf['Hours_worked_index']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] /  Hours_worked_index_in_1980 
    
    # GDP_model[region] = Output[region]
        idxlhs = fcol_in_mdf['GDP_model']
        idx1 = fcol_in_mdf['Output']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10]
    
    # Cohort_0_to_20[region] = Cohort_0_to_4[region] + Cohort_10_to_14[region] + Cohort_15_to_19[region] + Cohort_5_to_9[region]
        idxlhs = fcol_in_mdf['Cohort_0_to_20']
        idx1 = fcol_in_mdf['Cohort_0_to_4']
        idx2 = fcol_in_mdf['Cohort_10_to_14']
        idx3 = fcol_in_mdf['Cohort_15_to_19']
        idx4 = fcol_in_mdf['Cohort_5_to_9']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] + mdf[rowi , idx4:idx4 + 10]
    
    # Cohort_20_to_40[region] = Cohort_20_to_24[region] + Cohort_25_to_29[region] + Cohort_30_to_34[region] + Cohort_35_to_39[region]
        idxlhs = fcol_in_mdf['Cohort_20_to_40']
        idx1 = fcol_in_mdf['Cohort_20_to_24']
        idx2 = fcol_in_mdf['Cohort_25_to_29']
        idx3 = fcol_in_mdf['Cohort_30_to_34']
        idx4 = fcol_in_mdf['Cohort_35_to_39']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] + mdf[rowi , idx4:idx4 + 10]
    
    # Cohort_40_to_60[region] = Cohort_40_to_44[region] + Cohort_45_to_49[region] + Cohort_50_to_54[region] + Cohort_55_to_59[region]
        idxlhs = fcol_in_mdf['Cohort_40_to_60']
        idx1 = fcol_in_mdf['Cohort_40_to_44']
        idx2 = fcol_in_mdf['Cohort_45_to_49']
        idx3 = fcol_in_mdf['Cohort_50_to_54']
        idx4 = fcol_in_mdf['Cohort_55_to_59']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] + mdf[rowi , idx4:idx4 + 10]
    
    # Cohort_60plus[region] = Cohort_60_to_64[region] + Cohort_65_to_69[region] + Cohort_70_to_74[region] + Cohort_75_to_79[region] + Cohort_80_to_84[region] + Cohort_85_to_89[region] + Cohort_90_to_94[region] + Cohort_95p[region]
        idxlhs = fcol_in_mdf['Cohort_60plus']
        idx1 = fcol_in_mdf['Cohort_60_to_64']
        idx2 = fcol_in_mdf['Cohort_65_to_69']
        idx3 = fcol_in_mdf['Cohort_70_to_74']
        idx4 = fcol_in_mdf['Cohort_75_to_79']
        idx5 = fcol_in_mdf['Cohort_80_to_84']
        idx6 = fcol_in_mdf['Cohort_85_to_89']
        idx7 = fcol_in_mdf['Cohort_90_to_94']
        idx8 = fcol_in_mdf['Cohort_95p']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] + mdf[rowi , idx4:idx4 + 10] + mdf[rowi , idx5:idx5 + 10] + mdf[rowi , idx6:idx6 + 10] + mdf[rowi , idx7:idx7 + 10] + mdf[rowi , idx8:idx8 + 10]
    
    # Population[region] = Cohort_0_to_20[region] + Cohort_20_to_40[region] + Cohort_40_to_60[region] + Cohort_60plus[region]
        idxlhs = fcol_in_mdf['Population']
        idx1 = fcol_in_mdf['Cohort_0_to_20']
        idx2 = fcol_in_mdf['Cohort_20_to_40']
        idx3 = fcol_in_mdf['Cohort_40_to_60']
        idx4 = fcol_in_mdf['Cohort_60plus']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] + mdf[rowi , idx4:idx4 + 10]
    
    # GDPpp_model[region] = GDP_model[region] / Population[region] * UNIT_conv_to_k2017pppUSD_pr_py[region]
        idxlhs = fcol_in_mdf['GDPpp_model']
        idx1 = fcol_in_mdf['GDP_model']
        idx2 = fcol_in_mdf['Population']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10] *  UNIT_conv_to_k2017pppUSD_pr_py 
    
    # GDPpp_USED[region] = GDPpp_model[region]
        idxlhs = fcol_in_mdf['GDPpp_USED']
        idx1 = fcol_in_mdf['GDPpp_model']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10]
     
    # GenderEquality[region] = INTEG ( Change_in_GE[region] , GE_in_1980[region] )
        idx1 = fcol_in_mdf['GenderEquality']
        idx2 = fcol_in_mdf['Change_in_GE']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] ) * dt
     
    # Glacial_ice_volume_km3 = INTEG ( - Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py , Glacial_ice_volume_in_1980 )
        idx1 = fcol_in_mdf['Glacial_ice_volume_km3']
        idx2 = fcol_in_mdf['Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( - mdf[rowi-1, idx2] ) * dt
     
    # Govt_debt_from_public_lenders[region] = INTEG ( Increase_in_GDPL[region] - Decrease_in_GDPL[region] - Govt_debt_from_public_lenders_cancelled[region] , 0 )
        idx1 = fcol_in_mdf['Govt_debt_from_public_lenders']
        idx2 = fcol_in_mdf['Increase_in_GDPL']
        idx3 = fcol_in_mdf['Decrease_in_GDPL']
        idx4 = fcol_in_mdf['Govt_debt_from_public_lenders_cancelled']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] - mdf[rowi-1, idx4:idx4 + 10] ) * dt
     
    # Govt_debt_owed_to_private_lenders[region] = INTEG ( Govt_new_debt_from_private_lenders[region] - Govt_debt_paid_back_to_private_lenders[region] - Govt_debt_cancelling[region] , Govt_debt_in_1980[region] )
        idx1 = fcol_in_mdf['Govt_debt_owed_to_private_lenders']
        idx2 = fcol_in_mdf['Govt_new_debt_from_private_lenders']
        idx3 = fcol_in_mdf['Govt_debt_paid_back_to_private_lenders']
        idx4 = fcol_in_mdf['Govt_debt_cancelling']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] - mdf[rowi-1, idx4:idx4 + 10] ) * dt
     
    # Govt_in_default_to_private_lenders[region] = INTEG ( Govt_defaulting[region] - Govt_defaults_written_off[region] , 0 )
        idx1 = fcol_in_mdf['Govt_in_default_to_private_lenders']
        idx2 = fcol_in_mdf['Govt_defaulting']
        idx3 = fcol_in_mdf['Govt_defaults_written_off']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] ) * dt
     
    # GRASS_area_burnt_Mkm2 = INTEG ( GRASS_burning_Mkm2_py - GRASS_regrowing_after_being_burnt_Mkm2_py , GRASS_area_burned_in_1980 )
        idx1 = fcol_in_mdf['GRASS_area_burnt_Mkm2']
        idx2 = fcol_in_mdf['GRASS_burning_Mkm2_py']
        idx3 = fcol_in_mdf['GRASS_regrowing_after_being_burnt_Mkm2_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] ) * dt
     
    # GRASS_area_harvested_Mkm2 = INTEG ( GRASS_being_harvested_Mkm2_py - GRASS_regrowing_after_harvesting_Mkm2_py , GRASS_area_harvested_in_1980 )
        idx1 = fcol_in_mdf['GRASS_area_harvested_Mkm2']
        idx2 = fcol_in_mdf['GRASS_being_harvested_Mkm2_py']
        idx3 = fcol_in_mdf['GRASS_regrowing_after_harvesting_Mkm2_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] ) * dt
     
    # GRASS_Biomass_locked_in_construction_material_GtBiomass = INTEG ( GRASS_for_construction_use - GRASS_Biomass_in_construction_material_being_burnt - GRASS_Biomass_in_construction_material_left_to_rot , GRASS_Biomass_locked_in_construction_material_in_1980 )
        idx1 = fcol_in_mdf['GRASS_Biomass_locked_in_construction_material_GtBiomass']
        idx2 = fcol_in_mdf['GRASS_for_construction_use']
        idx3 = fcol_in_mdf['GRASS_Biomass_in_construction_material_being_burnt']
        idx4 = fcol_in_mdf['GRASS_Biomass_in_construction_material_left_to_rot']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] - mdf[rowi-1, idx4] ) * dt
     
    # GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass = INTEG ( GRASS_Biomass_in_construction_material_left_to_rot + GRASS_Living_biomass_rotting - GRASS_Dead_biomass_decomposing - GRASS_DeadB_SOM_being_lost_due_to_deforestation - GRASS_DeadB_SOM_being_lost_due_to_energy_harvesting - GRASS_runoff - GRASS_soil_degradation_from_forest_fires , GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM_in_1980 )
        idx1 = fcol_in_mdf['GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass']
        idx2 = fcol_in_mdf['GRASS_Biomass_in_construction_material_left_to_rot']
        idx3 = fcol_in_mdf['GRASS_Living_biomass_rotting']
        idx4 = fcol_in_mdf['GRASS_Dead_biomass_decomposing']
        idx5 = fcol_in_mdf['GRASS_DeadB_SOM_being_lost_due_to_deforestation']
        idx6 = fcol_in_mdf['GRASS_DeadB_SOM_being_lost_due_to_energy_harvesting']
        idx7 = fcol_in_mdf['GRASS_runoff']
        idx8 = fcol_in_mdf['GRASS_soil_degradation_from_forest_fires']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] + mdf[rowi-1, idx3] - mdf[rowi-1, idx4] - mdf[rowi-1, idx5] - mdf[rowi-1, idx6] - mdf[rowi-1, idx7] - mdf[rowi-1, idx8] ) * dt
     
    # GRASS_deforested_Mkm2 = INTEG ( GRASS_being_deforested_Mkm2_py - GRASS_regrowing_after_being_deforested_Mkm2_py , GRASS_area_deforested_in_1980 )
        idx1 = fcol_in_mdf['GRASS_deforested_Mkm2']
        idx2 = fcol_in_mdf['GRASS_being_deforested_Mkm2_py']
        idx3 = fcol_in_mdf['GRASS_regrowing_after_being_deforested_Mkm2_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] ) * dt
     
    # GRASS_Living_biomass_GtBiomass = INTEG ( GRASS_biomass_new_growing - GRASS_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting - GRASS_for_construction_use - GRASS_Living_biomass_rotting , GRASS_Living_biomass_in_1980 )
        idx1 = fcol_in_mdf['GRASS_Living_biomass_GtBiomass']
        idx2 = fcol_in_mdf['GRASS_biomass_new_growing']
        idx3 = fcol_in_mdf['GRASS_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting']
        idx4 = fcol_in_mdf['GRASS_for_construction_use']
        idx5 = fcol_in_mdf['GRASS_Living_biomass_rotting']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] - mdf[rowi-1, idx4] - mdf[rowi-1, idx5] ) * dt
     
    # GRASS_potential_area_Mkm2 = INTEG ( Shifting_NF_to_GRASS_Mkm2_py + Shifting_TROP_to_GRASS_Mkm2_py + Shifting_DESERT_to_GRASS_Mkm2_py - Shifting_GRASS_to_DESERT_Mkm2_py - Shifting_GRASS_to_NF_Mkm2_py - Shifting_GRASS_to_TROP_Mkm2_py , 22.5095 )
        idx1 = fcol_in_mdf['GRASS_potential_area_Mkm2']
        idx2 = fcol_in_mdf['Shifting_NF_to_GRASS_Mkm2_py']
        idx3 = fcol_in_mdf['Shifting_TROP_to_GRASS_Mkm2_py']
        idx4 = fcol_in_mdf['Shifting_DESERT_to_GRASS_Mkm2_py']
        idx5 = fcol_in_mdf['Shifting_GRASS_to_DESERT_Mkm2_py']
        idx6 = fcol_in_mdf['Shifting_GRASS_to_NF_Mkm2_py']
        idx7 = fcol_in_mdf['Shifting_GRASS_to_TROP_Mkm2_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] + mdf[rowi-1, idx3] + mdf[rowi-1, idx4] - mdf[rowi-1, idx5] - mdf[rowi-1, idx6] - mdf[rowi-1, idx7] ) * dt
     
    # Grazing_land[region] = INTEG ( fa_to_gl[region] + acgl_to_gl[region] - gl_to_acgl[region] , Grazing_land_in_1980[region] )
        idx1 = fcol_in_mdf['Grazing_land']
        idx2 = fcol_in_mdf['fa_to_gl']
        idx3 = fcol_in_mdf['acgl_to_gl']
        idx4 = fcol_in_mdf['gl_to_acgl']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] + mdf[rowi-1, idx3:idx3 + 10] - mdf[rowi-1, idx4:idx4 + 10] ) * dt
     
    # Greenland_ice_volume_on_Greenland_km3 = INTEG ( - Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py , Greenland_ice_volume_in_1980 )
        idx1 = fcol_in_mdf['Greenland_ice_volume_on_Greenland_km3']
        idx2 = fcol_in_mdf['Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( - mdf[rowi-1, idx2] ) * dt
     
    # Heat_in_atmosphere_ZJ = INTEG ( Convection_aka_sensible_heat_flow + Evaporation_aka_latent_heat_flow + LW_surface_emissions_NOT_escaping_through_atm_window + SW_Atmospheric_absorption - Heat_withdrawn_from_atm_by_melting_pos_or_added_neg_by_freezing_ice_ZJ_py - LW_clear_sky_emissions_to_surface - LW_TOA_radiation_from_atm_to_space , Heat_in_atmosphere_in_1980 )
        idx1 = fcol_in_mdf['Heat_in_atmosphere_ZJ']
        idx2 = fcol_in_mdf['Convection_aka_sensible_heat_flow']
        idx3 = fcol_in_mdf['Evaporation_aka_latent_heat_flow']
        idx4 = fcol_in_mdf['LW_surface_emissions_NOT_escaping_through_atm_window']
        idx5 = fcol_in_mdf['SW_Atmospheric_absorption']
        idx6 = fcol_in_mdf['Heat_withdrawn_from_atm_by_melting_pos_or_added_neg_by_freezing_ice_ZJ_py']
        idx7 = fcol_in_mdf['LW_clear_sky_emissions_to_surface']
        idx8 = fcol_in_mdf['LW_TOA_radiation_from_atm_to_space']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] + mdf[rowi-1, idx3] + mdf[rowi-1, idx4] + mdf[rowi-1, idx5] - mdf[rowi-1, idx6] - mdf[rowi-1, idx7] - mdf[rowi-1, idx8] ) * dt
     
    # Heat_in_deep_ZJ = INTEG ( Heat_flow_from_the_earths_core + Net_heat_flow_ocean_from_surface_to_deep_ZJ_py , Heat_in_ocean_deep_in_1980 )
        idx1 = fcol_in_mdf['Heat_in_deep_ZJ']
        idx2 = fcol_in_mdf['Net_heat_flow_ocean_from_surface_to_deep_ZJ_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( Heat_flow_from_the_earths_core + mdf[rowi-1, idx2] ) * dt
     
    # Heat_in_surface = INTEG ( LW_clear_sky_emissions_to_surface + LW_re_radiated_by_clouds + SW_surface_absorption - Convection_aka_sensible_heat_flow - Evaporation_aka_latent_heat_flow - Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_antarctic_ice_ZJ_py - Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_arctic_ice_ZJ_py - LW_surface_emission - Net_heat_flow_ocean_from_surface_to_deep_ZJ_py , Heat_in_surface_in_1980 )
        idx1 = fcol_in_mdf['Heat_in_surface']
        idx2 = fcol_in_mdf['LW_clear_sky_emissions_to_surface']
        idx3 = fcol_in_mdf['LW_re_radiated_by_clouds']
        idx4 = fcol_in_mdf['SW_surface_absorption']
        idx5 = fcol_in_mdf['Convection_aka_sensible_heat_flow']
        idx6 = fcol_in_mdf['Evaporation_aka_latent_heat_flow']
        idx7 = fcol_in_mdf['Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_antarctic_ice_ZJ_py']
        idx8 = fcol_in_mdf['Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_arctic_ice_ZJ_py']
        idx9 = fcol_in_mdf['LW_surface_emission']
        idx10 = fcol_in_mdf['Net_heat_flow_ocean_from_surface_to_deep_ZJ_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] + mdf[rowi-1, idx3] + mdf[rowi-1, idx4] - mdf[rowi-1, idx5] - mdf[rowi-1, idx6] - mdf[rowi-1, idx7] - mdf[rowi-1, idx8] - mdf[rowi-1, idx9] - mdf[rowi-1, idx10] ) * dt
    
    # Temp_surface_average_K = Heat_in_surface * Conversion_heat_surface_to_temp
        idxlhs = fcol_in_mdf['Temp_surface_average_K']
        idx1 = fcol_in_mdf['Heat_in_surface']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Conversion_heat_surface_to_temp 
    
    # Temp_surface = Temp_surface_average_K - 273.15
        idxlhs = fcol_in_mdf['Temp_surface']
        idx1 = fcol_in_mdf['Temp_surface_average_K']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] -  273.15 
    
    # Temp_surface_anomaly_compared_to_anfang_degC = Temp_surface - ( Temp_surface_1850 - 273.15 )
        idxlhs = fcol_in_mdf['Temp_surface_anomaly_compared_to_anfang_degC']
        idx1 = fcol_in_mdf['Temp_surface']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] -  (  Temp_surface_1850  -  273.15  ) 
    
    # Evaporation_as_f_of_temp = ( Incoming_solar_in_1850_ZJ_py * Evaporation_as_fraction_of_incoming_solar_in_1850 ) * ( 1 + Sensitivity_of_evaporation_to_temp * ( Temp_surface_anomaly_compared_to_anfang_degC / Reference_temp_C ) )
        idxlhs = fcol_in_mdf['Evaporation_as_f_of_temp']
        idx1 = fcol_in_mdf['Temp_surface_anomaly_compared_to_anfang_degC']
        mdf[rowi, idxlhs] =  (  Incoming_solar_in_1850_ZJ_py  *  Evaporation_as_fraction_of_incoming_solar_in_1850  )  *  (  1  +  Sensitivity_of_evaporation_to_temp  *  ( mdf[rowi, idx1] /  Reference_temp_C  )  ) 
    
    # Humidity_of_atmosphere = Evaporation_as_f_of_temp * Water_content_of_evaporation_g_p_kg_per_ZJ_py
        idxlhs = fcol_in_mdf['Humidity_of_atmosphere']
        idx1 = fcol_in_mdf['Evaporation_as_f_of_temp']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Water_content_of_evaporation_g_p_kg_per_ZJ_py 
     
    # Hydro_net_depreciation_multiplier_on_gen_cap = INTEG ( - Hydro_net_depreciation , 1 )
        idx1 = fcol_in_mdf['Hydro_net_depreciation_multiplier_on_gen_cap']
        idx2 = fcol_in_mdf['Hydro_net_depreciation']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( - mdf[rowi-1, idx2] ) * dt
     
    # Indicated_Existential_minimum_income = INTEG ( Increase_in_existential_minimum_income , 2.5 )
        idx1 = fcol_in_mdf['Indicated_Existential_minimum_income']
        idx2 = fcol_in_mdf['Increase_in_existential_minimum_income']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] ) * dt
     
    # Inventory[region] = INTEG ( Output[region] - Sales[region] , Inventory_in_1980[region] )
        idx1 = fcol_in_mdf['Inventory']
        idx2 = fcol_in_mdf['Output']
        idx3 = fcol_in_mdf['Sales']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] ) * dt
     
    # Kyoto_Fluor_gases_in_atm = INTEG ( Kyoto_Fluor_emissions - Kyoto_Fluor_degradation , 361.575 )
        idx1 = fcol_in_mdf['Kyoto_Fluor_gases_in_atm']
        idx2 = fcol_in_mdf['Kyoto_Fluor_emissions']
        idx3 = fcol_in_mdf['Kyoto_Fluor_degradation']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] ) * dt
     
    # Montreal_gases_in_atm = INTEG ( Montreal_gases_emissions - Montreal_gases_degradation , 16239.5 )
        idx1 = fcol_in_mdf['Montreal_gases_in_atm']
        idx2 = fcol_in_mdf['Montreal_gases_emissions']
        idx3 = fcol_in_mdf['Montreal_gases_degradation']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] ) * dt
     
    # N2O_in_atmosphere_MtN2O = INTEG ( All_N2O_emissions - N2O_degradation_MtN2O_py , N2O_in_atmosphere_MtN2O_in_1980 )
        idx1 = fcol_in_mdf['N2O_in_atmosphere_MtN2O']
        idx2 = fcol_in_mdf['All_N2O_emissions']
        idx3 = fcol_in_mdf['N2O_degradation_MtN2O_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] ) * dt
     
    # NF_area_burnt_Mkm2 = INTEG ( NF_burning_Mkm2_py - NF_regrowing_after_being_burnt_Mkm2_py , NF_area_burned_in_1980 )
        idx1 = fcol_in_mdf['NF_area_burnt_Mkm2']
        idx2 = fcol_in_mdf['NF_burning_Mkm2_py']
        idx3 = fcol_in_mdf['NF_regrowing_after_being_burnt_Mkm2_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] ) * dt
     
    # NF_area_clear_cut_Mkm2 = INTEG ( NF_being_harvested_by_clear_cutting_Mkm2_py - NF_regrowing_after_being_clear_cut_Mkm2_py , NF_area_clear_cut_in_1980 )
        idx1 = fcol_in_mdf['NF_area_clear_cut_Mkm2']
        idx2 = fcol_in_mdf['NF_being_harvested_by_clear_cutting_Mkm2_py']
        idx3 = fcol_in_mdf['NF_regrowing_after_being_clear_cut_Mkm2_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] ) * dt
     
    # NF_area_deforested_Mkm2 = INTEG ( NF_being_deforested_Mkm2_py - NF_regrowing_after_being_deforested_Mkm2_py , NF_area_deforested_in_1980 )
        idx1 = fcol_in_mdf['NF_area_deforested_Mkm2']
        idx2 = fcol_in_mdf['NF_being_deforested_Mkm2_py']
        idx3 = fcol_in_mdf['NF_regrowing_after_being_deforested_Mkm2_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] ) * dt
     
    # NF_area_harvested_Mkm2 = INTEG ( NF_being_harvested_normally_Mkm2_py - NF_regrowing_after_harvesting_Mkm2_py , NF_area_harvested_in_1980 )
        idx1 = fcol_in_mdf['NF_area_harvested_Mkm2']
        idx2 = fcol_in_mdf['NF_being_harvested_normally_Mkm2_py']
        idx3 = fcol_in_mdf['NF_regrowing_after_harvesting_Mkm2_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] ) * dt
     
    # NF_Biomass_locked_in_construction_material_GtBiomass = INTEG ( NF_for_construction_use - NF_Biomass_in_construction_material_being_burnt - NF_TUNDRA_Biomass_in_construction_material_left_to_rot , NF_Biomass_locked_in_construction_material_in_1980 )
        idx1 = fcol_in_mdf['NF_Biomass_locked_in_construction_material_GtBiomass']
        idx2 = fcol_in_mdf['NF_for_construction_use']
        idx3 = fcol_in_mdf['NF_Biomass_in_construction_material_being_burnt']
        idx4 = fcol_in_mdf['NF_TUNDRA_Biomass_in_construction_material_left_to_rot']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] - mdf[rowi-1, idx4] ) * dt
     
    # NF_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass = INTEG ( NF_TUNDRA_Biomass_in_construction_material_left_to_rot + NF_Living_biomass_rotting - NF_Dead_biomass_decomposing - NF_DeadB_SOM_being_lost_due_to_deforestation - NF_DeadB_SOM_being_lost_due_to_energy_harvesting - NF_runoff - NF_soil_degradation_from_clear_cutting - NF_soil_degradation_from_forest_fires , NF_Dead_biomass_litter_and_soil_organic_matter_SOM_in_1980 )
        idx1 = fcol_in_mdf['NF_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass']
        idx2 = fcol_in_mdf['NF_TUNDRA_Biomass_in_construction_material_left_to_rot']
        idx3 = fcol_in_mdf['NF_Living_biomass_rotting']
        idx4 = fcol_in_mdf['NF_Dead_biomass_decomposing']
        idx5 = fcol_in_mdf['NF_DeadB_SOM_being_lost_due_to_deforestation']
        idx6 = fcol_in_mdf['NF_DeadB_SOM_being_lost_due_to_energy_harvesting']
        idx7 = fcol_in_mdf['NF_runoff']
        idx8 = fcol_in_mdf['NF_soil_degradation_from_clear_cutting']
        idx9 = fcol_in_mdf['NF_soil_degradation_from_forest_fires']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] + mdf[rowi-1, idx3] - mdf[rowi-1, idx4] - mdf[rowi-1, idx5] - mdf[rowi-1, idx6] - mdf[rowi-1, idx7] - mdf[rowi-1, idx8] - mdf[rowi-1, idx9] ) * dt
     
    # NF_Living_biomass_GtBiomass = INTEG ( NF_biomass_new_growing - NF_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting - NF_for_construction_use - NF_Living_biomass_rotting , NF_Living_biomass_in_1980 )
        idx1 = fcol_in_mdf['NF_Living_biomass_GtBiomass']
        idx2 = fcol_in_mdf['NF_biomass_new_growing']
        idx3 = fcol_in_mdf['NF_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting']
        idx4 = fcol_in_mdf['NF_for_construction_use']
        idx5 = fcol_in_mdf['NF_Living_biomass_rotting']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] - mdf[rowi-1, idx4] - mdf[rowi-1, idx5] ) * dt
     
    # NF_potential_area_Mkm2 = INTEG ( Shifting_GRASS_to_NF_Mkm2_py + Shifting_TROP_to_NF_Mkm2_py + Shifting_Tundra_to_NF_Mkm2_py - Shifting_NF_to_GRASS_Mkm2_py - Shifting_NF_to_TROP_Mkm2_py - Shifting_NF_to_Tundra_Mkm2_py , 17.0089 )
        idx1 = fcol_in_mdf['NF_potential_area_Mkm2']
        idx2 = fcol_in_mdf['Shifting_GRASS_to_NF_Mkm2_py']
        idx3 = fcol_in_mdf['Shifting_TROP_to_NF_Mkm2_py']
        idx4 = fcol_in_mdf['Shifting_Tundra_to_NF_Mkm2_py']
        idx5 = fcol_in_mdf['Shifting_NF_to_GRASS_Mkm2_py']
        idx6 = fcol_in_mdf['Shifting_NF_to_TROP_Mkm2_py']
        idx7 = fcol_in_mdf['Shifting_NF_to_Tundra_Mkm2_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] + mdf[rowi-1, idx3] + mdf[rowi-1, idx4] - mdf[rowi-1, idx5] - mdf[rowi-1, idx6] - mdf[rowi-1, idx7] ) * dt
     
    # Non_energy_footprint_pp_future = INTEG ( - Change_in_future_footprint_pp , 0.99 )
        idx1 = fcol_in_mdf['Non_energy_footprint_pp_future']
        idx2 = fcol_in_mdf['Change_in_future_footprint_pp']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( - mdf[rowi-1, idx2] ) * dt
     
    # Nuclear_net_depreciation_multiplier_on_gen_cap = INTEG ( - Nuclear_net_depreciation , 1 )
        idx1 = fcol_in_mdf['Nuclear_net_depreciation_multiplier_on_gen_cap']
        idx2 = fcol_in_mdf['Nuclear_net_depreciation']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( - mdf[rowi-1, idx2] ) * dt
     
    # Owner_power_or_weakness[region] = INTEG ( - Change_in_Owner_power[region] , Owner_power_in_1980 )
        idx1 = fcol_in_mdf['Owner_power_or_weakness']
        idx2 = fcol_in_mdf['Change_in_Owner_power']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( - mdf[rowi-1, idx2:idx2 + 10] ) * dt
     
    # Owner_saving_fraction[region] = INTEG ( Net_change_in_OSF[region] , OSF_in_1980[region] )
        idx1 = fcol_in_mdf['Owner_saving_fraction']
        idx2 = fcol_in_mdf['Net_change_in_OSF']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] ) * dt
     
    # Owner_wealth_accumulated[region] = INTEG ( Owner_wealth_accumulating[region] - Wealth_taxing[region] , Owner_wealth_accumulated_in_1980[region] )
        idx1 = fcol_in_mdf['Owner_wealth_accumulated']
        idx2 = fcol_in_mdf['Owner_wealth_accumulating']
        idx3 = fcol_in_mdf['Wealth_taxing']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] ) * dt
     
    # People_considering_entering_the_pool[region] = INTEG ( Change_in_people_considering_entering_the_pool[region] , People_considering_entering_the_pool_in_1980 )
        idx1 = fcol_in_mdf['People_considering_entering_the_pool']
        idx2 = fcol_in_mdf['Change_in_people_considering_entering_the_pool']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] ) * dt
     
    # People_considering_leaving_the_pool[region] = INTEG ( Change_in_people_considering_leaving_the_pool[region] , People_considering_leaving_the_pool_in_1980 )
        idx1 = fcol_in_mdf['People_considering_leaving_the_pool']
        idx2 = fcol_in_mdf['Change_in_people_considering_leaving_the_pool']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] ) * dt
     
    # Populated_land[region] = INTEG ( acgl_to_pl[region] + apl_to_pl[region] + c_to_pl[region] - pl_to_apl[region] , Populated_land_in_1980[region] )
        idx1 = fcol_in_mdf['Populated_land']
        idx2 = fcol_in_mdf['acgl_to_pl']
        idx3 = fcol_in_mdf['apl_to_pl']
        idx4 = fcol_in_mdf['c_to_pl']
        idx5 = fcol_in_mdf['pl_to_apl']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] + mdf[rowi-1, idx3:idx3 + 10] + mdf[rowi-1, idx4:idx4 + 10] - mdf[rowi-1, idx5:idx5 + 10] ) * dt
     
    # Public_capacity[region] = INTEG ( Increase_in_public_capacity[region] - Decrease_in_public_capacity[region] , Public_Capacity_in_1980[region] )
        idx1 = fcol_in_mdf['Public_capacity']
        idx2 = fcol_in_mdf['Increase_in_public_capacity']
        idx3 = fcol_in_mdf['Decrease_in_public_capacity']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] ) * dt
     
    # Public_loan_defaults[region] = INTEG ( Increase_in_public_loan_defaults[region] - Decrease_in_public_loan_defaults[region] , 0 )
        idx1 = fcol_in_mdf['Public_loan_defaults']
        idx2 = fcol_in_mdf['Increase_in_public_loan_defaults']
        idx3 = fcol_in_mdf['Decrease_in_public_loan_defaults']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] ) * dt
     
    # Rate_of_tech_advance_RoTA_in_TFP[region] = INTEG ( Change_in_RoTA[region] , Rate_of_tech_advance_RoTA_in_TFP_in_1980[region] )
        idx1 = fcol_in_mdf['Rate_of_tech_advance_RoTA_in_TFP']
        idx2 = fcol_in_mdf['Change_in_RoTA']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] ) * dt
     
    # Regenerative_cropland_fraction[region] = INTEG ( Increase_in_regen_cropland[region] - Decrease_in_regen_cropland[region] , 0 )
        idx1 = fcol_in_mdf['Regenerative_cropland_fraction']
        idx2 = fcol_in_mdf['Increase_in_regen_cropland']
        idx3 = fcol_in_mdf['Decrease_in_regen_cropland']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] ) * dt
     
    # Social_trust[region] = INTEG ( Change_in_social_trust[region] , Social_trust_in_1980 )
        idx1 = fcol_in_mdf['Social_trust']
        idx2 = fcol_in_mdf['Change_in_social_trust']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] ) * dt
    
    # GDP_USED[region] = GDP_model[region]
        idxlhs = fcol_in_mdf['GDP_USED']
        idx1 = fcol_in_mdf['GDP_model']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10]
     
    # Speculative_asset_pool_relative_to_init[region] = INTEG ( increase_in_speculative_asset_pool[region] - decrease_in_speculative_asset_pool[region] , Speculative_asset_pool_relative_to_init_in_1980[region] )
        idx1 = fcol_in_mdf['Speculative_asset_pool_relative_to_init']
        idx2 = fcol_in_mdf['increase_in_speculative_asset_pool']
        idx3 = fcol_in_mdf['decrease_in_speculative_asset_pool']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] ) * dt
     
    # Total_factor_productivity_TFP_before_env_damage[region] = INTEG ( Change_in_TFP[region] , TFP_in_1980 )
        idx1 = fcol_in_mdf['Total_factor_productivity_TFP_before_env_damage']
        idx2 = fcol_in_mdf['Change_in_TFP']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] ) * dt
     
    # TROP_area_burnt = INTEG ( TROP_burning - TROP_regrowing_after_being_burnt_Mkm2_py , TROP_area_burned_in_1980 )
        idx1 = fcol_in_mdf['TROP_area_burnt']
        idx2 = fcol_in_mdf['TROP_burning']
        idx3 = fcol_in_mdf['TROP_regrowing_after_being_burnt_Mkm2_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] ) * dt
     
    # TROP_area_clear_cut = INTEG ( TROP_being_harvested_by_clear_cutting - TROP_regrowing_after_being_clear_cut , TROP_area_clear_cut_in_1980 )
        idx1 = fcol_in_mdf['TROP_area_clear_cut']
        idx2 = fcol_in_mdf['TROP_being_harvested_by_clear_cutting']
        idx3 = fcol_in_mdf['TROP_regrowing_after_being_clear_cut']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] ) * dt
     
    # TROP_area_deforested = INTEG ( TROP_being_deforested_Mkm2_py - TROP_regrowing_after_being_deforested , TROP_area_deforested_in_1980 )
        idx1 = fcol_in_mdf['TROP_area_deforested']
        idx2 = fcol_in_mdf['TROP_being_deforested_Mkm2_py']
        idx3 = fcol_in_mdf['TROP_regrowing_after_being_deforested']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] ) * dt
     
    # TROP_area_harvested_Mkm2 = INTEG ( TROP_being_harvested_normally - TROP_regrowing_after_harvesting_Mkm2_py , TROP_area_harvested_in_1980 )
        idx1 = fcol_in_mdf['TROP_area_harvested_Mkm2']
        idx2 = fcol_in_mdf['TROP_being_harvested_normally']
        idx3 = fcol_in_mdf['TROP_regrowing_after_harvesting_Mkm2_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] ) * dt
     
    # TROP_Biomass_locked_in_construction_material_GtBiomass = INTEG ( TROP_for_construction_use - TROP_Biomass_in_construction_material_being_burnt - TROP_Biomass_in_construction_material_left_to_rot , TROP_Biomass_locked_in_construction_material_in_1980 )
        idx1 = fcol_in_mdf['TROP_Biomass_locked_in_construction_material_GtBiomass']
        idx2 = fcol_in_mdf['TROP_for_construction_use']
        idx3 = fcol_in_mdf['TROP_Biomass_in_construction_material_being_burnt']
        idx4 = fcol_in_mdf['TROP_Biomass_in_construction_material_left_to_rot']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] - mdf[rowi-1, idx4] ) * dt
     
    # TROP_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass = INTEG ( TROP_Biomass_in_construction_material_left_to_rot + TROP_Living_biomass_rotting - TROP_Dead_biomass_decomposing - TROP_DeadB_SOM_being_lost_due_to_deforestation - TROP_DeadB_SOM_being_lost_due_to_energy_harvesting - TROP_runoff - TROP_soil_degradation_from_clear_cutting - TROP_soil_degradation_from_forest_fires , TROP_Dead_biomass_litter_and_soil_organic_matter_SOM_in_1980 )
        idx1 = fcol_in_mdf['TROP_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass']
        idx2 = fcol_in_mdf['TROP_Biomass_in_construction_material_left_to_rot']
        idx3 = fcol_in_mdf['TROP_Living_biomass_rotting']
        idx4 = fcol_in_mdf['TROP_Dead_biomass_decomposing']
        idx5 = fcol_in_mdf['TROP_DeadB_SOM_being_lost_due_to_deforestation']
        idx6 = fcol_in_mdf['TROP_DeadB_SOM_being_lost_due_to_energy_harvesting']
        idx7 = fcol_in_mdf['TROP_runoff']
        idx8 = fcol_in_mdf['TROP_soil_degradation_from_clear_cutting']
        idx9 = fcol_in_mdf['TROP_soil_degradation_from_forest_fires']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] + mdf[rowi-1, idx3] - mdf[rowi-1, idx4] - mdf[rowi-1, idx5] - mdf[rowi-1, idx6] - mdf[rowi-1, idx7] - mdf[rowi-1, idx8] - mdf[rowi-1, idx9] ) * dt
     
    # TROP_Living_biomass_GtBiomass = INTEG ( TROP_biomass_new_growing - TROP_for_construction_use - TROP_Living_biomass_rotting - TROP_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting , TROP_Living_biomass_in_1980 )
        idx1 = fcol_in_mdf['TROP_Living_biomass_GtBiomass']
        idx2 = fcol_in_mdf['TROP_biomass_new_growing']
        idx3 = fcol_in_mdf['TROP_for_construction_use']
        idx4 = fcol_in_mdf['TROP_Living_biomass_rotting']
        idx5 = fcol_in_mdf['TROP_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] - mdf[rowi-1, idx4] - mdf[rowi-1, idx5] ) * dt
     
    # TROP_potential_area_Mkm2 = INTEG ( Shifting_GRASS_to_TROP_Mkm2_py + Shifting_NF_to_TROP_Mkm2_py - Shifting_TROP_to_GRASS_Mkm2_py - Shifting_TROP_to_NF_Mkm2_py , 25.0208 )
        idx1 = fcol_in_mdf['TROP_potential_area_Mkm2']
        idx2 = fcol_in_mdf['Shifting_GRASS_to_TROP_Mkm2_py']
        idx3 = fcol_in_mdf['Shifting_NF_to_TROP_Mkm2_py']
        idx4 = fcol_in_mdf['Shifting_TROP_to_GRASS_Mkm2_py']
        idx5 = fcol_in_mdf['Shifting_TROP_to_NF_Mkm2_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] + mdf[rowi-1, idx3] - mdf[rowi-1, idx4] - mdf[rowi-1, idx5] ) * dt
     
    # TUNDRA_area_burnt_Mkm2 = INTEG ( TUNDRA_burning_Mkm2_py - TUNDRA_regrowing_after_being_burnt_Mkm2_py , TUNDRA_area_burned_in_1980 )
        idx1 = fcol_in_mdf['TUNDRA_area_burnt_Mkm2']
        idx2 = fcol_in_mdf['TUNDRA_burning_Mkm2_py']
        idx3 = fcol_in_mdf['TUNDRA_regrowing_after_being_burnt_Mkm2_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] ) * dt
     
    # TUNDRA_area_harvested_Mkm2 = INTEG ( TUNDRA_being_harvested_Mkm2_py - TUNDRA_regrowing_after_harvesting_Mkm2_py , TUNDRA_area_harvested_in_1980 )
        idx1 = fcol_in_mdf['TUNDRA_area_harvested_Mkm2']
        idx2 = fcol_in_mdf['TUNDRA_being_harvested_Mkm2_py']
        idx3 = fcol_in_mdf['TUNDRA_regrowing_after_harvesting_Mkm2_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] ) * dt
     
    # TUNDRA_Biomass_locked_in_construction_material_GtBiomass = INTEG ( TUNDRA_for_construction_use - TUNDRA_Biomass_in_construction_material_being_burnt - TUNDRA_Biomass_in_construction_material_left_to_rot , TUNDRA_Biomass_locked_in_construction_material_in_1980 )
        idx1 = fcol_in_mdf['TUNDRA_Biomass_locked_in_construction_material_GtBiomass']
        idx2 = fcol_in_mdf['TUNDRA_for_construction_use']
        idx3 = fcol_in_mdf['TUNDRA_Biomass_in_construction_material_being_burnt']
        idx4 = fcol_in_mdf['TUNDRA_Biomass_in_construction_material_left_to_rot']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] - mdf[rowi-1, idx4] ) * dt
     
    # TUNDRA_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass = INTEG ( TUNDRA_Biomass_in_construction_material_left_to_rot + TUNDRA_Living_biomass_rotting - TUNDRA_Dead_biomass_decomposing - TUNDRA_DeadB_SOM_being_lost_due_to_deforestation - TUNDRA_DeadB_SOM_being_lost_due_to_energy_harvesting - TUNDRA_runoff - TUNDRA_soil_degradation_from_forest_fires , TUNDRA_Dead_biomass_litter_and_soil_organic_matter_SOM_in_1980 )
        idx1 = fcol_in_mdf['TUNDRA_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass']
        idx2 = fcol_in_mdf['TUNDRA_Biomass_in_construction_material_left_to_rot']
        idx3 = fcol_in_mdf['TUNDRA_Living_biomass_rotting']
        idx4 = fcol_in_mdf['TUNDRA_Dead_biomass_decomposing']
        idx5 = fcol_in_mdf['TUNDRA_DeadB_SOM_being_lost_due_to_deforestation']
        idx6 = fcol_in_mdf['TUNDRA_DeadB_SOM_being_lost_due_to_energy_harvesting']
        idx7 = fcol_in_mdf['TUNDRA_runoff']
        idx8 = fcol_in_mdf['TUNDRA_soil_degradation_from_forest_fires']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] + mdf[rowi-1, idx3] - mdf[rowi-1, idx4] - mdf[rowi-1, idx5] - mdf[rowi-1, idx6] - mdf[rowi-1, idx7] - mdf[rowi-1, idx8] ) * dt
     
    # TUNDRA_deforested_Mkm2 = INTEG ( TUNDRA_being_deforested_Mkm2_py - TUNDRA_regrowing_after_being_deforested_Mkm2_py , TUNDRA_area_deforested_in_1980 )
        idx1 = fcol_in_mdf['TUNDRA_deforested_Mkm2']
        idx2 = fcol_in_mdf['TUNDRA_being_deforested_Mkm2_py']
        idx3 = fcol_in_mdf['TUNDRA_regrowing_after_being_deforested_Mkm2_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] ) * dt
     
    # TUNDRA_Living_biomass = INTEG ( TUNDRA_biomass_new_growing - TUNDRA_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting - TUNDRA_for_construction_use - TUNDRA_Living_biomass_rotting , TUNDRA_Living_biomass_in_1980 )
        idx1 = fcol_in_mdf['TUNDRA_Living_biomass']
        idx2 = fcol_in_mdf['TUNDRA_biomass_new_growing']
        idx3 = fcol_in_mdf['TUNDRA_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting']
        idx4 = fcol_in_mdf['TUNDRA_for_construction_use']
        idx5 = fcol_in_mdf['TUNDRA_Living_biomass_rotting']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] - mdf[rowi-1, idx4] - mdf[rowi-1, idx5] ) * dt
     
    # Tundra_potential_area_Mkm2 = INTEG ( Shifting_ice_on_land_to_tundra_Mkm2_py + Shifting_NF_to_Tundra_Mkm2_py - Shifting_tundra_to_ice_on_land_Mkm2_py - Shifting_Tundra_to_NF_Mkm2_py , 22.5089 )
        idx1 = fcol_in_mdf['Tundra_potential_area_Mkm2']
        idx2 = fcol_in_mdf['Shifting_ice_on_land_to_tundra_Mkm2_py']
        idx3 = fcol_in_mdf['Shifting_NF_to_Tundra_Mkm2_py']
        idx4 = fcol_in_mdf['Shifting_tundra_to_ice_on_land_Mkm2_py']
        idx5 = fcol_in_mdf['Shifting_Tundra_to_NF_Mkm2_py']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] + mdf[rowi-1, idx3] - mdf[rowi-1, idx4] - mdf[rowi-1, idx5] ) * dt
     
    # UAC_reduction_effort = INTEG ( - Change_in_UACre , 1 )
        idx1 = fcol_in_mdf['UAC_reduction_effort']
        idx2 = fcol_in_mdf['Change_in_UACre']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( - mdf[rowi-1, idx2] ) * dt
     
    # Unemployed[region] = INTEG ( Entering_the_labor_pool[region] + Loosing_a_job[region] - Getting_a_job[region] - Leaving_the_labor_pool[region] , Unemployment_in_1980[region] )
        idx1 = fcol_in_mdf['Unemployed']
        idx2 = fcol_in_mdf['Entering_the_labor_pool']
        idx3 = fcol_in_mdf['Loosing_a_job']
        idx4 = fcol_in_mdf['Getting_a_job']
        idx5 = fcol_in_mdf['Leaving_the_labor_pool']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] + mdf[rowi-1, idx3:idx3 + 10] - mdf[rowi-1, idx4:idx4 + 10] - mdf[rowi-1, idx5:idx5 + 10] ) * dt
     
    # Volcanic_aerosols_in_stratosphere = INTEG ( Volcanic_aerosols_emissions - Volcanic_aerosols_removed_from_stratosphere , 0.118607 )
        idx1 = fcol_in_mdf['Volcanic_aerosols_in_stratosphere']
        idx2 = fcol_in_mdf['Volcanic_aerosols_emissions']
        idx3 = fcol_in_mdf['Volcanic_aerosols_removed_from_stratosphere']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idx3] ) * dt
     
    # wind_and_PV_el_capacity[region] = INTEG ( Addition_of_wind_and_PV_el_capacity[region] - Discarding_wind_and_PV_el_capacity[region] , wind_and_PV_el_cap_in_1980 )
        idx1 = fcol_in_mdf['wind_and_PV_el_capacity']
        idx2 = fcol_in_mdf['Addition_of_wind_and_PV_el_capacity']
        idx3 = fcol_in_mdf['Discarding_wind_and_PV_el_capacity']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] ) * dt
     
    # Worker_debt_defaults_outstanding[region] = INTEG ( Worker_debt_defaulting[region] - Worker_defaults_written_off[region] , 0 )
        idx1 = fcol_in_mdf['Worker_debt_defaults_outstanding']
        idx2 = fcol_in_mdf['Worker_debt_defaulting']
        idx3 = fcol_in_mdf['Worker_defaults_written_off']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] ) * dt
    
    # Effective_purchasing_power[region] = SMOOTHI ( Consumption_and_investment[region] , Demand_adjustment_time , Demand_in_1980[region] )
        idx1 = fcol_in_mdf['Effective_purchasing_power']
        idx2 = fcol_in_mdf['Consumption_and_investment']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi - 1, idx1:idx1 + 10]) / Demand_adjustment_time * dt
    
    # Sales[region] = ( Effective_purchasing_power[region] / ( Delivery_delay_index[region] / Delivery_delay_index_in_1980[region] ) )
        idxlhs = fcol_in_mdf['Sales']
        idx1 = fcol_in_mdf['Effective_purchasing_power']
        idx2 = fcol_in_mdf['Delivery_delay_index']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] /  ( mdf[rowi , idx2:idx2 + 10] /  Delivery_delay_index_in_1980  )  ) 
    
    # National_income_before_GL[region] = Sales[region]
        idxlhs = fcol_in_mdf['National_income_before_GL']
        idx1 = fcol_in_mdf['Sales']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10]
    
    # Implemented_spending_on_GL[region] = SMOOTH3I ( Planned_investments_for_all_TAs[region] , Time_to_implement_spending_adjustments , Implemented_spending_on_GL_in_1980[region] )
        idxlhs = fcol_in_mdf['Implemented_spending_on_GL']
        idxin = fcol_in_mdf['Planned_investments_for_all_TAs']
        idx2 = fcol_in_mdf['Implemented_spending_on_GL_2']
        idx1 = fcol_in_mdf['Implemented_spending_on_GL_1']
        idxout = fcol_in_mdf['Implemented_spending_on_GL']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( Time_to_implement_spending_adjustments / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( Time_to_implement_spending_adjustments / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( Time_to_implement_spending_adjustments / 3) * dt
    
    # pct_of_GDP_spent_on_GL[region] = Implemented_spending_on_GL[region] / GDP_USED[region]
        idxlhs = fcol_in_mdf['pct_of_GDP_spent_on_GL']
        idx1 = fcol_in_mdf['Implemented_spending_on_GL']
        idx2 = fcol_in_mdf['GDP_USED']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # National_income[region] = National_income_before_GL[region] * ( 1 - pct_of_GDP_spent_on_GL[region] )
        idxlhs = fcol_in_mdf['National_income']
        idx1 = fcol_in_mdf['National_income_before_GL']
        idx2 = fcol_in_mdf['pct_of_GDP_spent_on_GL']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  1  - mdf[rowi , idx2:idx2 + 10] ) 
    
    # Worker_share_of_output[region] = ( ( Owner_power_or_weakness[region] + 1 ) / Worker_power_scaling_factor ) + Worker_power_scaling_factor_reference
        idxlhs = fcol_in_mdf['Worker_share_of_output']
        idx1 = fcol_in_mdf['Owner_power_or_weakness']
        mdf[rowi, idxlhs:idxlhs + 10] =  (  ( mdf[rowi , idx1:idx1 + 10] +  1  )  /  Worker_power_scaling_factor  )  +  Worker_power_scaling_factor_reference 
    
    # StrUP_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , StrUP_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , StrUP_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , StrUP_R1_via_Excel , StrUP_policy_Min ) ) )
        idxlhs = fcol_in_mdf['StrUP_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  StrUP_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  StrUP_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  StrUP_R1_via_Excel[0:10]  ,  StrUP_policy_Min  )  )  ) 
    
    # Eff_of_social_trust_on_reform_willingness_and_social_tension[region] = 1 + SoE_of_social_trust_on_reform * ( Social_trust[region] / Social_trust_in_1980 - 1 )
        idxlhs = fcol_in_mdf['Eff_of_social_trust_on_reform_willingness_and_social_tension']
        idx1 = fcol_in_mdf['Social_trust']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  +  SoE_of_social_trust_on_reform  *  ( mdf[rowi , idx1:idx1 + 10] /  Social_trust_in_1980  -  1  ) 
    
    # Perceived_RoC_in_Living_conditions_index_with_env_damage[region] = SMOOTHI ( RoC_in_Living_conditions_index_with_env_damage[region] , Social_tension_perception_delay , 0 )
        idx1 = fcol_in_mdf['Perceived_RoC_in_Living_conditions_index_with_env_damage']
        idx2 = fcol_in_mdf['RoC_in_Living_conditions_index_with_env_damage']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi - 1, idx1:idx1 + 10]) / Social_tension_perception_delay * dt
    
    # Scaled_and_smoothed_Effect_of_poverty_on_social_tension_and_trust[region] = SMOOTHI ( Scaled_Effect_of_poverty_on_social_tension_and_trust[region] , Time_for_poverty_to_affect_social_tension_and_trust , 1 )
        idx1 = fcol_in_mdf['Scaled_and_smoothed_Effect_of_poverty_on_social_tension_and_trust']
        idx2 = fcol_in_mdf['Scaled_Effect_of_poverty_on_social_tension_and_trust']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi - 1, idx1:idx1 + 10]) / Time_for_poverty_to_affect_social_tension_and_trust * dt
    
    # Speculative_asset_pool_relative_to_init_as_share_of_GDP[region] = Speculative_asset_pool_relative_to_init[region] / GDP_USED[region]
        idxlhs = fcol_in_mdf['Speculative_asset_pool_relative_to_init_as_share_of_GDP']
        idx1 = fcol_in_mdf['Speculative_asset_pool_relative_to_init']
        idx2 = fcol_in_mdf['GDP_USED']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # Effect_on_Wealth_on_Social_Tension[region] = WITH LOOKUP ( Speculative_asset_pool_relative_to_init_as_share_of_GDP[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 0.5 ) , ( 0.5 , 0.9 ) , ( 1 , 1 ) , ( 2 , 2 ) , ( 5 , 5 ) , ( 10 , 15 ) ) )
        tabidx = ftab_in_d_table['Effect_on_Wealth_on_Social_Tension'] # fetch the correct table
        idx2 = fcol_in_mdf['Effect_on_Wealth_on_Social_Tension'] # get the location of the lhs in mdf
        idx3 = fcol_in_mdf['Speculative_asset_pool_relative_to_init_as_share_of_GDP']
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:,0], look[:, 1])
    
    # Scaled_Effect_of_wealth_on_social_tension_and_trust[region] = Effect_on_Wealth_on_Social_Tension[region] * Scaling_factor_of_eff_of_wealth_on_social_tension
        idxlhs = fcol_in_mdf['Scaled_Effect_of_wealth_on_social_tension_and_trust']
        idx1 = fcol_in_mdf['Effect_on_Wealth_on_Social_Tension']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi, idx1:idx1 + 10] *  Scaling_factor_of_eff_of_wealth_on_social_tension 
    
    # Indicated_Social_tension_index[region] = 1 + ( 1 / ( 1 + Perceived_RoC_in_Living_conditions_index_with_env_damage[region] ) - 1 ) * Scaling_factor_for_amplitude_in_RoC_in_living_conditions_index * Scaled_and_smoothed_Effect_of_poverty_on_social_tension_and_trust[region] * Scaled_Effect_of_wealth_on_social_tension_and_trust[region]
        idxlhs = fcol_in_mdf['Indicated_Social_tension_index']
        idx1 = fcol_in_mdf['Perceived_RoC_in_Living_conditions_index_with_env_damage']
        idx2 = fcol_in_mdf['Scaled_and_smoothed_Effect_of_poverty_on_social_tension_and_trust']
        idx3 = fcol_in_mdf['Scaled_Effect_of_wealth_on_social_tension_and_trust']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  +  (  1  /  (  1  + mdf[rowi , idx1:idx1 + 10] )  -  1  )  *  Scaling_factor_for_amplitude_in_RoC_in_living_conditions_index  * mdf[rowi , idx2:idx2 + 10] * mdf[rowi , idx3:idx3 + 10]
    
    # Actual_Social_tension_index[region] = WITH LOOKUP ( Indicated_Social_tension_index[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 0.1 ) , ( 0.25 , 0.13 ) , ( 0.5 , 0.23 ) , ( 0.75 , 0.5 ) , ( 1 , 1 ) , ( 1.25 , 1.5 ) , ( 1.5 , 1.85 ) , ( 1.75 , 1.95 ) , ( 2 , 2 ) ) )
        tabidx = ftab_in_d_table['Actual_Social_tension_index'] # fetch the correct table
        idx2 = fcol_in_mdf['Actual_Social_tension_index'] # get the location of the lhs in mdf
        idx3 = fcol_in_mdf['Indicated_Social_tension_index']
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:,0], look[:, 1])
    
    # Smoothed_Social_tension_index_ie_rate_of_progress[region] = SMOOTH ( Actual_Social_tension_index[region] , Time_to_smooth_social_tension_index )
        idx1 = fcol_in_mdf['Smoothed_Social_tension_index_ie_rate_of_progress']
        idx2 = fcol_in_mdf['Actual_Social_tension_index']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1+10] + ( mdf[rowi-1 , idx2:idx2 + 10] - mdf[rowi -1 , idx1:idx1 + 10]) / Time_to_smooth_social_tension_index * dt
    
    # Smoothed_Social_tension_index_with_trust_effect[region] = Smoothed_Social_tension_index_ie_rate_of_progress[region] / Eff_of_social_trust_on_reform_willingness_and_social_tension[region]
        idxlhs = fcol_in_mdf['Smoothed_Social_tension_index_with_trust_effect']
        idx1 = fcol_in_mdf['Smoothed_Social_tension_index_ie_rate_of_progress']
        idx2 = fcol_in_mdf['Eff_of_social_trust_on_reform_willingness_and_social_tension']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # Indicated_effect_of_social_tension_on_reform_willingness[region] = ( Smoothed_Social_tension_index_with_trust_effect[region] - 1 ) * Strength_of_the_impact_of_social_tension_on_reform_willingness
        idxlhs = fcol_in_mdf['Indicated_effect_of_social_tension_on_reform_willingness']
        idx1 = fcol_in_mdf['Smoothed_Social_tension_index_with_trust_effect']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] -  1  )  *  Strength_of_the_impact_of_social_tension_on_reform_willingness 
    
    # Effect_of_social_tension_on_reform_willingness[region] = Indicated_effect_of_social_tension_on_reform_willingness[region] + 1
        idxlhs = fcol_in_mdf['Effect_of_social_tension_on_reform_willingness']
        idx1 = fcol_in_mdf['Indicated_effect_of_social_tension_on_reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] +  1 
    
    # Indicated_reform_willingness[region] = Eff_of_social_trust_on_reform_willingness_and_social_tension[region] / Effect_of_social_tension_on_reform_willingness[region]
        idxlhs = fcol_in_mdf['Indicated_reform_willingness']
        idx1 = fcol_in_mdf['Eff_of_social_trust_on_reform_willingness_and_social_tension']
        idx2 = fcol_in_mdf['Effect_of_social_tension_on_reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # Reform_willingness_scaled_to_today[region] = IF_THEN_ELSE ( zeit < Policy_start_year , 1 , Indicated_reform_willingness / Indicated_reform_willingness_at_2025 )
        idxlhs = fcol_in_mdf['Reform_willingness_scaled_to_today']
        idx1 = fcol_in_mdf['Indicated_reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  <  Policy_start_year  ,  1  , mdf[rowi , idx1:idx1 + 10] /  Indicated_reform_willingness_at_2025[0:10]  ) 
    
    # Smoothed_Reform_willingness[region] = SMOOTH3 ( Reform_willingness_scaled_to_today[region] , Time_to_adjust_reform_willingness )
        idxin = fcol_in_mdf['Reform_willingness_scaled_to_today' ]
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness_2']
        idx1 = fcol_in_mdf['Smoothed_Reform_willingness_1']
        idxout = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( Time_to_adjust_reform_willingness / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( Time_to_adjust_reform_willingness / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( Time_to_adjust_reform_willingness / 3) * dt
    
    # StrUP_policy_with_RW[region] = StrUP_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['StrUP_policy_with_RW']
        idx1 = fcol_in_mdf['StrUP_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
     
    # StrUP_pol_div_100[region] = MIN ( StrUP_policy_Max , MAX ( StrUP_policy_Min , StrUP_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['StrUP_pol_div_100']
        idx1 = fcol_in_mdf['StrUP_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], StrUP_policy_Min, StrUP_policy_Max) / 100
    
    # StrUP_policy[region] = SMOOTH3 ( StrUP_pol_div_100[region] , StrUP_Time_to_implement_policy )
        idxin = fcol_in_mdf['StrUP_pol_div_100' ]
        idx2 = fcol_in_mdf['StrUP_policy_2']
        idx1 = fcol_in_mdf['StrUP_policy_1']
        idxout = fcol_in_mdf['StrUP_policy']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( StrUP_Time_to_implement_policy / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( StrUP_Time_to_implement_policy / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( StrUP_Time_to_implement_policy / 3) * dt
    
    # StrU_mult_used[region] = 1 + StrUP_policy[region]
        idxlhs = fcol_in_mdf['StrU_mult_used']
        idx1 = fcol_in_mdf['StrUP_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  + mdf[rowi , idx1:idx1 + 10]
    
    # Worker_share_of_output_with_policy[region] = Worker_share_of_output[region] * StrU_mult_used[region]
        idxlhs = fcol_in_mdf['Worker_share_of_output_with_policy']
        idx1 = fcol_in_mdf['Worker_share_of_output']
        idx2 = fcol_in_mdf['StrU_mult_used']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # Unemployment_rate[region] = Unemployed[region] / Employed[region]
        idxlhs = fcol_in_mdf['Unemployment_rate']
        idx1 = fcol_in_mdf['Unemployed']
        idx2 = fcol_in_mdf['Employed']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # Unemployment_ratio[region] = Unemployment_rate[region] / Societal_unemployment_rate_norm
        idxlhs = fcol_in_mdf['Unemployment_ratio']
        idx1 = fcol_in_mdf['Unemployment_rate']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Societal_unemployment_rate_norm 
    
    # Effect_of_unemployment_ratio_on_Worker_share_of_output[region] = 1 + SoE_of_unemployment_ratio_on_WSO * ( Unemployment_ratio[region] - 1 )
        idxlhs = fcol_in_mdf['Effect_of_unemployment_ratio_on_Worker_share_of_output']
        idx1 = fcol_in_mdf['Unemployment_ratio']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  +  SoE_of_unemployment_ratio_on_WSO  *  ( mdf[rowi , idx1:idx1 + 10] -  1  ) 
    
    # Worker_share_of_output_with_unemployment_effect[region] = Worker_share_of_output_with_policy[region] * Effect_of_unemployment_ratio_on_Worker_share_of_output[region]
        idxlhs = fcol_in_mdf['Worker_share_of_output_with_unemployment_effect']
        idx1 = fcol_in_mdf['Worker_share_of_output_with_policy']
        idx2 = fcol_in_mdf['Effect_of_unemployment_ratio_on_Worker_share_of_output']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # Life_expectancy_at_birth_as_f_of_GDPpp[region] = Life_expec_a[region] + Life_expec_b[region] * LN ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl )
        idxlhs = fcol_in_mdf['Life_expectancy_at_birth_as_f_of_GDPpp']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  Life_expec_a[0:10]  +  Life_expec_b[0:10]  *  np.log  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  ) 
    
    # Life_expectancy_at_birth[region] = SMOOTH ( Life_expectancy_at_birth_as_f_of_GDPpp[region] , Time_to_affect_life_expectancy )
        idx1 = fcol_in_mdf['Life_expectancy_at_birth']
        idx2 = fcol_in_mdf['Life_expectancy_at_birth_as_f_of_GDPpp']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1+10] + ( mdf[rowi-1 , idx2:idx2 + 10] - mdf[rowi -1 , idx1:idx1 + 10]) / Time_to_affect_life_expectancy * dt
    
    # Pension_age[region] = IF_THEN_ELSE ( Life_expectancy_at_birth < Life_expectancy_at_birth_in_1980 , Pension_age_in_1980 , Pension_age_in_1980 + SoE_of_LE_on_Pension_age * ( Life_expectancy_at_birth - Life_expectancy_at_birth_in_1980 ) )
        idxlhs = fcol_in_mdf['Pension_age']
        idx1 = fcol_in_mdf['Life_expectancy_at_birth']
        idx2 = fcol_in_mdf['Life_expectancy_at_birth']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  ( mdf[rowi , idx1:idx1 + 10] <  Life_expectancy_at_birth_in_1980[0:10]  ,  Pension_age_in_1980[0:10]  ,  Pension_age_in_1980[0:10]  +  SoE_of_LE_on_Pension_age[0:10]  *  ( mdf[rowi , idx2:idx2 + 10] -  Life_expectancy_at_birth_in_1980[0:10]  )  ) 
    
    # Theoretical_fraction_of_people_60plus_drawing_a_pension[region] = MAX ( 0 , ( Max_age - Pension_age[region] ) / Years_between_60_and_max_age )
        idxlhs = fcol_in_mdf['Theoretical_fraction_of_people_60plus_drawing_a_pension']
        idx1 = fcol_in_mdf['Pension_age']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.maximum  (  0  ,  (  Max_age  - mdf[rowi , idx1:idx1 + 10] )  /  Years_between_60_and_max_age  ) 
    
    # Actual_fraction_of_people_60plus_drawing_a_pension[region] = IF_THEN_ELSE ( Pension_age < 60 , 1 , Theoretical_fraction_of_people_60plus_drawing_a_pension )
        idxlhs = fcol_in_mdf['Actual_fraction_of_people_60plus_drawing_a_pension']
        idx1 = fcol_in_mdf['Pension_age']
        idx2 = fcol_in_mdf['Theoretical_fraction_of_people_60plus_drawing_a_pension']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  ( mdf[rowi , idx1:idx1 + 10] <  60  ,  1  , mdf[rowi , idx2:idx2 + 10] ) 
    
    # People_drawing_a_pension[region] = Cohort_60plus[region] * Actual_fraction_of_people_60plus_drawing_a_pension[region]
        idxlhs = fcol_in_mdf['People_drawing_a_pension']
        idx1 = fcol_in_mdf['Cohort_60plus']
        idx2 = fcol_in_mdf['Actual_fraction_of_people_60plus_drawing_a_pension']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # SGMP_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , SGMP_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , SGMP_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , SGMP_R1_via_Excel , SGMP_policy_Min ) ) )
        idxlhs = fcol_in_mdf['SGMP_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  SGMP_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  SGMP_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  SGMP_R1_via_Excel[0:10]  ,  SGMP_policy_Min  )  )  ) 
    
    # SGMP_policy_with_RW[region] = SGMP_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['SGMP_policy_with_RW']
        idx1 = fcol_in_mdf['SGMP_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
     
    # SGMP_pol_div_100[region] = MIN ( SGMP_policy_Max , MAX ( SGMP_policy_Min , SGMP_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['SGMP_pol_div_100']
        idx1 = fcol_in_mdf['SGMP_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], SGMP_policy_Min, SGMP_policy_Max) / 100
    
    # SGMP_policy[region] = SMOOTH3 ( SGMP_pol_div_100[region] , SGMP_Time_to_implement_policy )
        idxin = fcol_in_mdf['SGMP_pol_div_100' ]
        idx2 = fcol_in_mdf['SGMP_policy_2']
        idx1 = fcol_in_mdf['SGMP_policy_1']
        idxout = fcol_in_mdf['SGMP_policy']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( SGMP_Time_to_implement_policy / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( SGMP_Time_to_implement_policy / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( SGMP_Time_to_implement_policy / 3) * dt
    
    # State_guaranteed_minimum_pension[region] = People_drawing_a_pension[region] * GDPpp_USED[region] * UNIT_conv_to_kUSDpp * SGMP_policy[region]
        idxlhs = fcol_in_mdf['State_guaranteed_minimum_pension']
        idx1 = fcol_in_mdf['People_drawing_a_pension']
        idx2 = fcol_in_mdf['GDPpp_USED']
        idx3 = fcol_in_mdf['SGMP_policy']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] *  UNIT_conv_to_kUSDpp  * mdf[rowi , idx3:idx3 + 10]
    
    # National_income_used_for_GL[region] = National_income_before_GL[region] * pct_of_GDP_spent_on_GL[region]
        idxlhs = fcol_in_mdf['National_income_used_for_GL']
        idx1 = fcol_in_mdf['National_income_before_GL']
        idx2 = fcol_in_mdf['pct_of_GDP_spent_on_GL']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # GL_spending_going_to_workers_wages[region] = National_income_used_for_GL[region] * ( 1 - GL_investment_fraction )
        idxlhs = fcol_in_mdf['GL_spending_going_to_workers_wages']
        idx1 = fcol_in_mdf['National_income_used_for_GL']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  1  -  GL_investment_fraction  ) 
    
    # Worker_income[region] = National_income[region] * Worker_share_of_output_with_unemployment_effect[region] + State_guaranteed_minimum_pension[region] + GL_spending_going_to_workers_wages[region]
        idxlhs = fcol_in_mdf['Worker_income']
        idx1 = fcol_in_mdf['National_income']
        idx2 = fcol_in_mdf['Worker_share_of_output_with_unemployment_effect']
        idx3 = fcol_in_mdf['State_guaranteed_minimum_pension']
        idx4 = fcol_in_mdf['GL_spending_going_to_workers_wages']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] + mdf[rowi , idx4:idx4 + 10]
    
    # IWITR_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , IWITR_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , IWITR_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , IWITR_R1_via_Excel , IWITR_policy_Min ) ) )
        idxlhs = fcol_in_mdf['IWITR_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  IWITR_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  IWITR_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  IWITR_R1_via_Excel[0:10]  ,  IWITR_policy_Min  )  )  ) 
    
    # IWITR_policy_with_RW[region] = IWITR_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['IWITR_policy_with_RW']
        idx1 = fcol_in_mdf['IWITR_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
     
    # IWITR_pol_div_100[region] = MIN ( IWITR_policy_Max , MAX ( IWITR_policy_Min , IWITR_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['IWITR_pol_div_100']
        idx1 = fcol_in_mdf['IWITR_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], IWITR_policy_Min, IWITR_policy_Max) / 100
    
    # IWITR_policy[region] = SMOOTH3 ( IWITR_pol_div_100[region] , Time_to_implement_UN_policies[region] )
        idxin = fcol_in_mdf['IWITR_pol_div_100' ]
        idx2 = fcol_in_mdf['IWITR_policy_2']
        idx1 = fcol_in_mdf['IWITR_policy_1']
        idxout = fcol_in_mdf['IWITR_policy']
        idx5 = fcol_in_mdf['Time_to_implement_UN_policies']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
    
    # Income_tax_rate_workers_after_GITx[region] = Income_tax_rate_ie_fraction_for_workers_before_policies + IWITR_policy[region]
        idxlhs = fcol_in_mdf['Income_tax_rate_workers_after_GITx']
        idx1 = fcol_in_mdf['IWITR_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  Income_tax_rate_ie_fraction_for_workers_before_policies  + mdf[rowi , idx1:idx1 + 10]
    
    # Income_tax_rate_workers[region] = Income_tax_rate_workers_after_GITx[region]
        idxlhs = fcol_in_mdf['Income_tax_rate_workers']
        idx1 = fcol_in_mdf['Income_tax_rate_workers_after_GITx']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10]
     
    # Worker_resistance_or_resignation[region] = INTEG ( Change_in_worker_resistance[region] , Worker_resistance_initially )
        idx1 = fcol_in_mdf['Worker_resistance_or_resignation']
        idx2 = fcol_in_mdf['Change_in_worker_resistance']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] ) * dt
     
    # Workers_debt[region] = INTEG ( Workers_taking_on_new_debt[region] - Workers_debt_payback[region] , Workers_debt_in_1980[region] )
        idx1 = fcol_in_mdf['Workers_debt']
        idx2 = fcol_in_mdf['Workers_taking_on_new_debt']
        idx3 = fcol_in_mdf['Workers_debt_payback']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idx3:idx3 + 10] ) * dt
    
    # Access_to_electricity[region] = Access_to_electricity_L / ( 1 + np.exp ( - Access_to_electricity_k * ( ( GDPpp_USED[region] / UNIT_conv_to_make_base_dmnless ) - Access_to_electricity_x0 ) ) ) + Access_to_electricity_min
        idxlhs = fcol_in_mdf['Access_to_electricity']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  Access_to_electricity_L  /  (  1  +  np.exp  (  -  Access_to_electricity_k  *  (  ( mdf[rowi , idx1:idx1 + 10] /  UNIT_conv_to_make_base_dmnless  )  -  Access_to_electricity_x0  )  )  )  +  Access_to_electricity_min 
    
    # cereal_dmd_CN = cereal_dmd_CN_a * LN ( GDPpp_USED[cn] * UNIT_conv_to_make_exp_dmnl ) + cereal_dmd_CN_b
        idxlhs = fcol_in_mdf['cereal_dmd_CN']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs] =  cereal_dmd_CN_a  *  np.log  ( mdf[rowi, idx1 + 2] *  UNIT_conv_to_make_exp_dmnl  )  +  cereal_dmd_CN_b 
    
    # cereal_dmd_func_pp[region] = cereal_dmd_func_pp_L[region] / ( 1 + np.exp ( - cereal_dmd_func_pp_k[region] * ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl - cereal_dmd_func_pp_x0[region] ) ) )
        idxlhs = fcol_in_mdf['cereal_dmd_func_pp']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  cereal_dmd_func_pp_L[0:10]  /  (  1  +  np.exp  (  -  cereal_dmd_func_pp_k[0:10]  *  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  -  cereal_dmd_func_pp_x0[0:10]  )  )  ) 
    
    # cereal_dmd_pp = IF_THEN_ELSE ( j==2 , cereal_dmd_CN , cereal_dmd_func_pp )
        idxlhs = fcol_in_mdf['cereal_dmd_pp']
        idx1 = fcol_in_mdf['cereal_dmd_CN']
        idx2 = fcol_in_mdf['cereal_dmd_func_pp']
        for j in range(0,10):
            mdf[rowi, idxlhs + j] =  IF_THEN_ELSE  (  j==2  , mdf[rowi , idx1] , mdf[rowi , idx2 + j] ) 
    
    # cereal_dmd_food_pp[region] = cereal_dmd_pp[region] * UNIT_conv_to_kg_crop_ppy
        idxlhs = fcol_in_mdf['cereal_dmd_food_pp']
        idx1 = fcol_in_mdf['cereal_dmd_pp']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_kg_crop_ppy 
    
    # cereal_dmd_food_pp_consumed[region] = cereal_dmd_food_pp[region] * ( 1 - Food_wasted_in_1980[region] )
        idxlhs = fcol_in_mdf['cereal_dmd_food_pp_consumed']
        idx1 = fcol_in_mdf['cereal_dmd_food_pp']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  1  -  Food_wasted_in_1980[0:10]  ) 
    
    # FWRP_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , FWRP_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , FWRP_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , FWRP_R1_via_Excel , FWRP_policy_Min ) ) )
        idxlhs = fcol_in_mdf['FWRP_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  FWRP_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  FWRP_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  FWRP_R1_via_Excel[0:10]  ,  FWRP_policy_Min  )  )  ) 
    
    # Actual_inequality_index_higher_is_more_unequal[region] = SMOOTH3I ( Indicated_inequality_index_with_tax[region] , Time_for_inequality_to_impact_wellbeing , 1 )
        idxin = fcol_in_mdf['Indicated_inequality_index_with_tax']
        idx2 = fcol_in_mdf['Actual_inequality_index_higher_is_more_unequal_2']
        idx1 = fcol_in_mdf['Actual_inequality_index_higher_is_more_unequal_1']
        idxout = fcol_in_mdf['Actual_inequality_index_higher_is_more_unequal']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( Time_for_inequality_to_impact_wellbeing / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( Time_for_inequality_to_impact_wellbeing / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( Time_for_inequality_to_impact_wellbeing / 3) * dt
    
    # Inequality_effect_on_energy_TA[region] = 1 + ( Actual_inequality_index_higher_is_more_unequal[region] - 1 ) * Strength_of_inequality_effect_on_energy_TA
        idxlhs = fcol_in_mdf['Inequality_effect_on_energy_TA']
        idx1 = fcol_in_mdf['Actual_inequality_index_higher_is_more_unequal']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  +  ( mdf[rowi , idx1:idx1 + 10] -  1  )  *  Strength_of_inequality_effect_on_energy_TA 
    
    # Owner_income[region] = National_income[region] * ( 1 - Worker_share_of_output_with_unemployment_effect[region] )
        idxlhs = fcol_in_mdf['Owner_income']
        idx1 = fcol_in_mdf['National_income']
        idx2 = fcol_in_mdf['Worker_share_of_output_with_unemployment_effect']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  1  - mdf[rowi , idx2:idx2 + 10] ) 
    
    # IOITR_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , IOITR_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , IOITR_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , IOITR_R1_via_Excel , IOITR_policy_Min ) ) )
        idxlhs = fcol_in_mdf['IOITR_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  IOITR_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  IOITR_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  IOITR_R1_via_Excel[0:10]  ,  IOITR_policy_Min  )  )  ) 
    
    # IOITR_policy_with_RW[region] = IOITR_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['IOITR_policy_with_RW']
        idx1 = fcol_in_mdf['IOITR_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
     
    # IOITR_pol_div_100[region] = MIN ( IOITR_policy_Max , MAX ( IOITR_policy_Min , IOITR_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['IOITR_pol_div_100']
        idx1 = fcol_in_mdf['IOITR_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], IOITR_policy_Min, IOITR_policy_Max) / 100
    
    # IOITR_policy[region] = SMOOTH3 ( IOITR_pol_div_100[region] , Time_to_implement_UN_policies[region] )
        idxin = fcol_in_mdf['IOITR_pol_div_100' ]
        idx2 = fcol_in_mdf['IOITR_policy_2']
        idx1 = fcol_in_mdf['IOITR_policy_1']
        idxout = fcol_in_mdf['IOITR_policy']
        idx5 = fcol_in_mdf['Time_to_implement_UN_policies']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
    
    # Additional_tax_rate_needed_to_pay_for_SGMP[region] = State_guaranteed_minimum_pension[region] / Owner_income[region]
        idxlhs = fcol_in_mdf['Additional_tax_rate_needed_to_pay_for_SGMP']
        idx1 = fcol_in_mdf['State_guaranteed_minimum_pension']
        idx2 = fcol_in_mdf['Owner_income']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # Additional_tax_rate_needed_to_pay_for_SGMP_after_policy_start[region] = IF_THEN_ELSE ( zeit > Policy_start_year , Additional_tax_rate_needed_to_pay_for_SGMP , 0 )
        idxlhs = fcol_in_mdf['Additional_tax_rate_needed_to_pay_for_SGMP_after_policy_start']
        idx1 = fcol_in_mdf['Additional_tax_rate_needed_to_pay_for_SGMP']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >  Policy_start_year  , mdf[rowi , idx1:idx1 + 10] ,  0  ) 
    
    # Income_tax_rate_owners_after_GITx[region] = Income_tax_rate_ie_fraction_owners_before_policies + IOITR_policy[region] + Additional_tax_rate_needed_to_pay_for_SGMP_after_policy_start[region]
        idxlhs = fcol_in_mdf['Income_tax_rate_owners_after_GITx']
        idx1 = fcol_in_mdf['IOITR_policy']
        idx2 = fcol_in_mdf['Additional_tax_rate_needed_to_pay_for_SGMP_after_policy_start']
        mdf[rowi, idxlhs:idxlhs + 10] =  Income_tax_rate_ie_fraction_owners_before_policies  + mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10]
    
    # Income_tax_rate[region] = Income_tax_rate_owners_after_GITx[region]
        idxlhs = fcol_in_mdf['Income_tax_rate']
        idx1 = fcol_in_mdf['Income_tax_rate_owners_after_GITx']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10]
    
    # XtaxEmp_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , XtaxEmp_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , XtaxEmp_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , XtaxEmp_R1_via_Excel , XtaxRateEmp_policy_Min ) ) )
        idxlhs = fcol_in_mdf['XtaxEmp_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  XtaxEmp_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  XtaxEmp_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  XtaxEmp_R1_via_Excel[0:10]  ,  XtaxEmp_policy_Min  )  )  ) 
    
    # XtaxEmp_policy_with_RW[region] = XtaxEmp_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['XtaxEmp_policy_with_RW']
        idx1 = fcol_in_mdf['XtaxEmp_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
     
    # XtaxEmp_pol_div_100[region] = MIN ( XtaxRateEmp_policy_Max , MAX ( XtaxRateEmp_policy_Min , XtaxEmp_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['XtaxEmp_pol_div_100']
        idx1 = fcol_in_mdf['XtaxEmp_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], XtaxEmp_policy_Min, XtaxEmp_policy_Max) / 100
    
    # XtaxRateEmp_policy[region] = SMOOTH3 ( XtaxEmp_pol_div_100[region] , XtaxRateEmp_Time_to_implement_policy )
        idxin = fcol_in_mdf['XtaxEmp_pol_div_100' ]
        idx2 = fcol_in_mdf['XtaxRateEmp_policy_2']
        idx1 = fcol_in_mdf['XtaxRateEmp_policy_1']
        idxout = fcol_in_mdf['XtaxRateEmp_policy']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( XtaxRateEmp_Time_to_implement_policy / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( XtaxRateEmp_Time_to_implement_policy / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( XtaxRateEmp_Time_to_implement_policy / 3) * dt
    
    # Female_leadership_spending[region] = National_income[region] * XtaxRateEmp_policy[region]
        idxlhs = fcol_in_mdf['Female_leadership_spending']
        idx1 = fcol_in_mdf['National_income']
        idx2 = fcol_in_mdf['XtaxRateEmp_policy']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # Extra_policy_taxes[region] = Female_leadership_spending[region]
        idxlhs = fcol_in_mdf['Extra_policy_taxes']
        idx1 = fcol_in_mdf['Female_leadership_spending']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10]
    
    # XtaxFrac_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , XtaxFrac_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , XtaxFrac_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , XtaxFrac_R1_via_Excel , Xtaxfrac_policy_Min ) ) )
        idxlhs = fcol_in_mdf['XtaxFrac_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  XtaxFrac_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  XtaxFrac_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  XtaxFrac_R1_via_Excel[0:10]  ,  XtaxFrac_policy_Min  )  )  ) 
    
    # XtaxFrac_policy_with_RW[region] = Xtaxfrac_policy_Min + ( XtaxFrac_rounds_via_Excel[region] - Xtaxfrac_policy_Min ) * Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['XtaxFrac_policy_with_RW']
        idx1 = fcol_in_mdf['XtaxFrac_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] =  XtaxFrac_policy_Min  +  ( mdf[rowi , idx1:idx1 + 10] -  XtaxFrac_policy_Min  )  * mdf[rowi , idx2:idx2 + 10]
     
    # XtaxFrac_pol_div_100[region] = MIN ( Xtaxfrac_policy_Max , MAX ( Xtaxfrac_policy_Min , XtaxFrac_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['XtaxFrac_pol_div_100']
        idx1 = fcol_in_mdf['XtaxFrac_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], XtaxFrac_policy_Min, XtaxFrac_policy_Max) / 100
    
    # Xtaxfrac_policy[region] = SMOOTH3 ( XtaxFrac_pol_div_100[region] , Xtaxfrac_Time_to_implement_policy )
        idxin = fcol_in_mdf['XtaxFrac_pol_div_100' ]
        idx2 = fcol_in_mdf['Xtaxfrac_policy_2']
        idx1 = fcol_in_mdf['Xtaxfrac_policy_1']
        idxout = fcol_in_mdf['Xtaxfrac_policy']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( Xtaxfrac_Time_to_implement_policy / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( Xtaxfrac_Time_to_implement_policy / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( Xtaxfrac_Time_to_implement_policy / 3) * dt
    
    # Fraction_of_extra_taxes_paid_by_owners[region] = Xtaxfrac_policy[region]
        idxlhs = fcol_in_mdf['Fraction_of_extra_taxes_paid_by_owners']
        idx1 = fcol_in_mdf['Xtaxfrac_policy']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10]
    
    # Extra_policy_taxes_paid_by_owners[region] = Extra_policy_taxes[region] * Fraction_of_extra_taxes_paid_by_owners[region]
        idxlhs = fcol_in_mdf['Extra_policy_taxes_paid_by_owners']
        idx1 = fcol_in_mdf['Extra_policy_taxes']
        idx2 = fcol_in_mdf['Fraction_of_extra_taxes_paid_by_owners']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # Income_and_policy_taxes_paid_by_owners[region] = Owner_income[region] * Income_tax_rate[region] + Extra_policy_taxes_paid_by_owners[region]
        idxlhs = fcol_in_mdf['Income_and_policy_taxes_paid_by_owners']
        idx1 = fcol_in_mdf['Owner_income']
        idx2 = fcol_in_mdf['Income_tax_rate']
        idx3 = fcol_in_mdf['Extra_policy_taxes_paid_by_owners']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10]
    
    # Extra_policy_taxes_paid_by_workers[region] = Extra_policy_taxes[region] * ( 1 - Fraction_of_extra_taxes_paid_by_owners[region] )
        idxlhs = fcol_in_mdf['Extra_policy_taxes_paid_by_workers']
        idx1 = fcol_in_mdf['Extra_policy_taxes']
        idx2 = fcol_in_mdf['Fraction_of_extra_taxes_paid_by_owners']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  1  - mdf[rowi , idx2:idx2 + 10] ) 
    
    # Worker_income_and_policy_taxes[region] = Worker_income[region] * Income_tax_rate_workers[region] + Extra_policy_taxes_paid_by_workers[region]
        idxlhs = fcol_in_mdf['Worker_income_and_policy_taxes']
        idx1 = fcol_in_mdf['Worker_income']
        idx2 = fcol_in_mdf['Income_tax_rate_workers']
        idx3 = fcol_in_mdf['Extra_policy_taxes_paid_by_workers']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10]
    
    # Consumption_taxes_last_year[region] = SMOOTHI ( Consumption_taxes[region] , One_year , Consumption_taxes_in_1980[region] )
        idx1 = fcol_in_mdf['Consumption_taxes_last_year']
        idx2 = fcol_in_mdf['Consumption_taxes']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi - 1, idx1:idx1 + 10]) / One_year * dt
    
    # XtaxCom_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , XtaxCom_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , XtaxCom_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , XtaxCom_R1_via_Excel , XtaxCom_policy_Min ) ) )
        idxlhs = fcol_in_mdf['XtaxCom_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  XtaxCom_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  XtaxCom_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  XtaxCom_R1_via_Excel[0:10]  ,  XtaxCom_policy_Min  )  )  ) 
    
    # XtaxCom_policy_with_RW[region] = XtaxCom_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['XtaxCom_policy_with_RW']
        idx1 = fcol_in_mdf['XtaxCom_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
     
    # XtaxCom_pol_div_100[region] = MIN ( XtaxCom_policy_Max , MAX ( XtaxCom_policy_Min , XtaxCom_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['XtaxCom_pol_div_100']
        idx1 = fcol_in_mdf['XtaxCom_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], XtaxCom_policy_Min, XtaxCom_policy_Max) / 100
    
    # XtaxCom_policy[region] = SMOOTH3 ( XtaxCom_pol_div_100[region] , XtaxCom_Time_to_implement_policy )
        idxin = fcol_in_mdf['XtaxCom_pol_div_100' ]
        idx2 = fcol_in_mdf['XtaxCom_policy_2']
        idx1 = fcol_in_mdf['XtaxCom_policy_1']
        idxout = fcol_in_mdf['XtaxCom_policy']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( XtaxCom_Time_to_implement_policy / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( XtaxCom_Time_to_implement_policy / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( XtaxCom_Time_to_implement_policy / 3) * dt
    
    # Universal_basic_dividend[region] = National_income[region] * XtaxCom_policy[region]
        idxlhs = fcol_in_mdf['Universal_basic_dividend']
        idx1 = fcol_in_mdf['National_income']
        idx2 = fcol_in_mdf['XtaxCom_policy']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # TOW_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , TOW_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , TOW_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , TOW_R1_via_Excel , TOW_policy_Min ) ) )
        idxlhs = fcol_in_mdf['TOW_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  TOW_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  TOW_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  TOW_R1_via_Excel[0:10]  ,  TOW_policy_Min  )  )  ) 
    
    # TOW_policy_with_RW[region] = TOW_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['TOW_policy_with_RW']
        idx1 = fcol_in_mdf['TOW_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
     
    # TOW_pol_div_100[region] = MIN ( TOW_policy_Max , MAX ( TOW_policy_Min , TOW_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['TOW_pol_div_100']
        idx1 = fcol_in_mdf['TOW_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], TOW_policy_Min, TOW_policy_Max) / 100
    
    # TOW_policy_converted_to_pa[region] = TOW_pol_div_100[region] * TOW_UNIT_conv_to_pa
        idxlhs = fcol_in_mdf['TOW_policy_converted_to_pa']
        idx1 = fcol_in_mdf['TOW_pol_div_100']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  TOW_UNIT_conv_to_pa 
    
    # TOW_policy[region] = SMOOTH3 ( TOW_policy_converted_to_pa[region] , Time_to_implement_UN_policies[region] )
        idxin = fcol_in_mdf['TOW_policy_converted_to_pa' ]
        idx2 = fcol_in_mdf['TOW_policy_2']
        idx1 = fcol_in_mdf['TOW_policy_1']
        idxout = fcol_in_mdf['TOW_policy']
        idx5 = fcol_in_mdf['Time_to_implement_UN_policies']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
    
    # Wealth_taxing[region] = Owner_wealth_accumulated[region] * TOW_policy[region]
        idxlhs = fcol_in_mdf['Wealth_taxing']
        idx1 = fcol_in_mdf['Owner_wealth_accumulated']
        idx2 = fcol_in_mdf['TOW_policy']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # Fossil_use_pp_NOT_for_El_gen_CN = Fossil_use_pp_NOT_for_El_gen_CN_a + Fossil_use_pp_NOT_for_El_gen_CN_b * ( LN ( GDPpp_USED[cn] * UNIT_conv_to_make_exp_dmnl ) )
        idxlhs = fcol_in_mdf['Fossil_use_pp_NOT_for_El_gen_CN']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs] =  Fossil_use_pp_NOT_for_El_gen_CN_a  +  Fossil_use_pp_NOT_for_El_gen_CN_b  *  (  np.log  ( mdf[rowi, idx1 + 2] *  UNIT_conv_to_make_exp_dmnl  )  ) 
    
    # Fossil_use_pp_NOT_for_El_gen_WO_CN[region] = Fossil_use_pp_NOT_for_El_gen_WO_CN_L[region] / ( 1 + np.exp ( - Fossil_use_pp_NOT_for_El_gen_WO_CN_k[region] * ( ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl ) - Fossil_use_pp_NOT_for_El_gen_WO_CN_x0[region] ) ) )
        idxlhs = fcol_in_mdf['Fossil_use_pp_NOT_for_El_gen_WO_CN']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  Fossil_use_pp_NOT_for_El_gen_WO_CN_L[0:10]  /  (  1  +  np.exp  (  -  Fossil_use_pp_NOT_for_El_gen_WO_CN_k[0:10]  *  (  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  )  -  Fossil_use_pp_NOT_for_El_gen_WO_CN_x0[0:10]  )  )  ) 
    
    # Fossil_use_pp_NOT_for_El_gen = IF_THEN_ELSE ( j==2 , Fossil_use_pp_NOT_for_El_gen_CN , Fossil_use_pp_NOT_for_El_gen_WO_CN )
        idxlhs = fcol_in_mdf['Fossil_use_pp_NOT_for_El_gen']
        idx1 = fcol_in_mdf['Fossil_use_pp_NOT_for_El_gen_CN']
        idx2 = fcol_in_mdf['Fossil_use_pp_NOT_for_El_gen_WO_CN']
        for j in range(0,10):
            mdf[rowi, idxlhs + j] =  IF_THEN_ELSE  (  j==2  , mdf[rowi , idx1] , mdf[rowi , idx2 + j] ) 
    
    # Fossil_use_pp_NOT_for_El_gen_toe_py[region] = Fossil_use_pp_NOT_for_El_gen[region] * UNIT_conv_to_toe_py
        idxlhs = fcol_in_mdf['Fossil_use_pp_NOT_for_El_gen_toe_py']
        idx1 = fcol_in_mdf['Fossil_use_pp_NOT_for_El_gen']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_toe_py 
    
    # El_from_wind_and_PV[region] = wind_and_PV_el_capacity[region] * wind_and_PV_capacity_factor[region] * Hours_per_year * UNIT_conv_GWh_and_TWh
        idxlhs = fcol_in_mdf['El_from_wind_and_PV']
        idx1 = fcol_in_mdf['wind_and_PV_el_capacity']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  wind_and_PV_capacity_factor  *  Hours_per_year  *  UNIT_conv_GWh_and_TWh 
    
    # Hydro_gen_cap[region] = ( Hydro_gen_cap_L[region] / ( 1 + np.exp ( - Hydro_gen_cap_k[region] * ( ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl ) - Hydro_gen_cap_x0[region] ) ) ) ) * Hydro_net_depreciation_multiplier_on_gen_cap
        idxlhs = fcol_in_mdf['Hydro_gen_cap']
        idx1 = fcol_in_mdf['GDPpp_USED']
        idx2 = fcol_in_mdf['Hydro_net_depreciation_multiplier_on_gen_cap']
        mdf[rowi, idxlhs:idxlhs + 10] =  (  Hydro_gen_cap_L[0:10]  /  (  1  +  np.exp  (  -  Hydro_gen_cap_k[0:10]  *  (  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  )  -  Hydro_gen_cap_x0[0:10]  )  )  )  )  * mdf[rowi , idx2]
    
    # El_from_Hydro[region] = Hydro_gen_cap[region] * Hydrocapacity_factor[region] * Hours_per_year * UNIT_conv_GWh_and_TWh
        idxlhs = fcol_in_mdf['El_from_Hydro']
        idx1 = fcol_in_mdf['Hydro_gen_cap']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  Hydrocapacity_factor[0:10]  *  Hours_per_year  *  UNIT_conv_GWh_and_TWh 
    
    # wind_PV_and_hydro_el_generation[region] = El_from_wind_and_PV[region] + El_from_Hydro[region]
        idxlhs = fcol_in_mdf['wind_PV_and_hydro_el_generation']
        idx1 = fcol_in_mdf['El_from_wind_and_PV']
        idx2 = fcol_in_mdf['El_from_Hydro']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10]
    
    # Green_hydrogen[region] = wind_PV_and_hydro_el_generation[region] * Actual_GH_share / TWh_per_MtH
        idxlhs = fcol_in_mdf['Green_hydrogen']
        idx1 = fcol_in_mdf['wind_PV_and_hydro_el_generation']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  Actual_GH_share  /  TWh_per_MtH 
    
    # Green_hydrogen_in_Mtoe_py[region] = Green_hydrogen[region] * toe_per_tH
        idxlhs = fcol_in_mdf['Green_hydrogen_in_Mtoe_py']
        idx1 = fcol_in_mdf['Green_hydrogen']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  toe_per_tH 
    
    # Low_carbon_heat_production[region] = Green_hydrogen_in_Mtoe_py[region]
        idxlhs = fcol_in_mdf['Low_carbon_heat_production']
        idx1 = fcol_in_mdf['Green_hydrogen_in_Mtoe_py']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10]
    
    # Fossil_fuel_NOT_for_El_gen[region] = ( ( Fossil_use_pp_NOT_for_El_gen_toe_py[region] * Population[region] ) / Extra_energy_productivity_index_2024_is_1[region] ) * UNIT_conv_toe_to_Mtoe - Low_carbon_heat_production[region]
        idxlhs = fcol_in_mdf['Fossil_fuel_NOT_for_El_gen']
        idx1 = fcol_in_mdf['Fossil_use_pp_NOT_for_El_gen_toe_py']
        idx2 = fcol_in_mdf['Population']
        idx3 = fcol_in_mdf['Extra_energy_productivity_index_2024_is_1']
        idx4 = fcol_in_mdf['Low_carbon_heat_production']
        mdf[rowi, idxlhs:idxlhs + 10] =  (  ( mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] )  / mdf[rowi , idx3:idx3 + 10] )  *  UNIT_conv_toe_to_Mtoe  - mdf[rowi , idx4:idx4 + 10]
    
    # Fossil_fuel_for_NON_El_use_that_CANNOT_be_electrified[region] = Fossil_fuel_NOT_for_El_gen[region] * Fraction_of_Fossil_fuel_for_NON_El_use_that_cannot_be_electrified
        idxlhs = fcol_in_mdf['Fossil_fuel_for_NON_El_use_that_CANNOT_be_electrified']
        idx1 = fcol_in_mdf['Fossil_fuel_NOT_for_El_gen']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  Fraction_of_Fossil_fuel_for_NON_El_use_that_cannot_be_electrified 
    
    # Fossil_fuel_for_NON_El_use_that_COULD_be_electrified[region] = Fossil_fuel_NOT_for_El_gen[region] - Fossil_fuel_for_NON_El_use_that_CANNOT_be_electrified[region]
        idxlhs = fcol_in_mdf['Fossil_fuel_for_NON_El_use_that_COULD_be_electrified']
        idx1 = fcol_in_mdf['Fossil_fuel_NOT_for_El_gen']
        idx2 = fcol_in_mdf['Fossil_fuel_for_NON_El_use_that_CANNOT_be_electrified']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10]
    
    # NEP_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , NEP_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , NEP_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , NEP_R1_via_Excel , NEP_policy_Min ) ) )
        idxlhs = fcol_in_mdf['NEP_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  NEP_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  NEP_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  NEP_R1_via_Excel[0:10]  ,  NEP_policy_Min  )  )  ) 
    
    # NEP_policy_with_RW[region] = NEP_rounds_via_Excel[region] * Smoothed_Reform_willingness[region] / Inequality_effect_on_energy_TA[region]
        idxlhs = fcol_in_mdf['NEP_policy_with_RW']
        idx1 = fcol_in_mdf['NEP_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        idx3 = fcol_in_mdf['Inequality_effect_on_energy_TA']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] / mdf[rowi , idx3:idx3 + 10]
     
    # NEP_pol_div_100[region] = MIN ( NEP_policy_Max , MAX ( NEP_policy_Min , NEP_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['NEP_pol_div_100']
        idx1 = fcol_in_mdf['NEP_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], NEP_policy_Min, NEP_policy_Max) / 100
    
    # NEP_policy[region] = SMOOTH3 ( NEP_pol_div_100[region] , NEP_Time_to_implement_goal )
        idxin = fcol_in_mdf['NEP_pol_div_100' ]
        idx2 = fcol_in_mdf['NEP_policy_2']
        idx1 = fcol_in_mdf['NEP_policy_1']
        idxout = fcol_in_mdf['NEP_policy']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( NEP_Time_to_implement_goal / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( NEP_Time_to_implement_goal / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( NEP_Time_to_implement_goal / 3) * dt
    
    # Fossil_fuel_for_NON_El_use_that_IS_being_electrified[region] = Fossil_fuel_for_NON_El_use_that_COULD_be_electrified[region] * NEP_policy[region]
        idxlhs = fcol_in_mdf['Fossil_fuel_for_NON_El_use_that_IS_being_electrified']
        idx1 = fcol_in_mdf['Fossil_fuel_for_NON_El_use_that_COULD_be_electrified']
        idx2 = fcol_in_mdf['NEP_policy']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # Fossil_fuel_for_NON_El_use_that_IS_NOT_being_electrified[region] = Fossil_fuel_for_NON_El_use_that_COULD_be_electrified[region] - Fossil_fuel_for_NON_El_use_that_IS_being_electrified[region]
        idxlhs = fcol_in_mdf['Fossil_fuel_for_NON_El_use_that_IS_NOT_being_electrified']
        idx1 = fcol_in_mdf['Fossil_fuel_for_NON_El_use_that_COULD_be_electrified']
        idx2 = fcol_in_mdf['Fossil_fuel_for_NON_El_use_that_IS_being_electrified']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10]
    
    # El_gen_from_fossil_fuels[region] = Fossil_el_gen_cap[region] * Hours_per_year * Fossil_actual_uptime_factor[region] * UNIT_conv_GWh_and_TWh
        idxlhs = fcol_in_mdf['El_gen_from_fossil_fuels']
        idx1 = fcol_in_mdf['Fossil_el_gen_cap']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  Hours_per_year  *  Fossil_actual_uptime_factor[0:10]  *  UNIT_conv_GWh_and_TWh 
    
    # Fossil_fuels_for_el_gen[region] = El_gen_from_fossil_fuels[region] / Conversion_Mtoe_to_TWh[region]
        idxlhs = fcol_in_mdf['Fossil_fuels_for_el_gen']
        idx1 = fcol_in_mdf['El_gen_from_fossil_fuels']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Conversion_Mtoe_to_TWh[0:10] 
    
    # Total_use_of_fossil_fuels[region] = Fossil_fuel_for_NON_El_use_that_CANNOT_be_electrified[region] + Fossil_fuel_for_NON_El_use_that_IS_NOT_being_electrified[region] + Fossil_fuels_for_el_gen[region]
        idxlhs = fcol_in_mdf['Total_use_of_fossil_fuels']
        idx1 = fcol_in_mdf['Fossil_fuel_for_NON_El_use_that_CANNOT_be_electrified']
        idx2 = fcol_in_mdf['Fossil_fuel_for_NON_El_use_that_IS_NOT_being_electrified']
        idx3 = fcol_in_mdf['Fossil_fuels_for_el_gen']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10]
    
    # CCS_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , CCS_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , CCS_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , CCS_R1_via_Excel , CCS_policy_Min ) ) )
        idxlhs = fcol_in_mdf['CCS_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  CCS_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  CCS_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  CCS_R1_via_Excel[0:10]  ,  CCS_policy_Min  )  )  ) 
    
    # CCS_policy_with_RW[region] = CCS_rounds_via_Excel[region] * Smoothed_Reform_willingness[region] / Inequality_effect_on_energy_TA[region]
        idxlhs = fcol_in_mdf['CCS_policy_with_RW']
        idx1 = fcol_in_mdf['CCS_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        idx3 = fcol_in_mdf['Inequality_effect_on_energy_TA']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] / mdf[rowi , idx3:idx3 + 10]
     
    # CCS_pol_div_100[region] = MIN ( CCS_policy_Max , MAX ( CCS_policy_Min , CCS_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['CCS_pol_div_100']
        idx1 = fcol_in_mdf['CCS_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], CCS_policy_Min, CCS_policy_Max) / 100
    
    # CCS_policy[region] = SMOOTH3 ( CCS_pol_div_100[region] , Time_to_implement_CCS_goal )
        idxin = fcol_in_mdf['CCS_pol_div_100' ]
        idx2 = fcol_in_mdf['CCS_policy_2']
        idx1 = fcol_in_mdf['CCS_policy_1']
        idxout = fcol_in_mdf['CCS_policy']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( Time_to_implement_CCS_goal / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( Time_to_implement_CCS_goal / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( Time_to_implement_CCS_goal / 3) * dt
    
    # Fraction_of_fossil_fuels_compensated_by_CCS[region] = CCS_policy[region]
        idxlhs = fcol_in_mdf['Fraction_of_fossil_fuels_compensated_by_CCS']
        idx1 = fcol_in_mdf['CCS_policy']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10]
    
    # Total_use_of_fossil_fuels_NOT_compensated[region] = Total_use_of_fossil_fuels[region] * ( 1 - Fraction_of_fossil_fuels_compensated_by_CCS[region] )
        idxlhs = fcol_in_mdf['Total_use_of_fossil_fuels_NOT_compensated']
        idx1 = fcol_in_mdf['Total_use_of_fossil_fuels']
        idx2 = fcol_in_mdf['Fraction_of_fossil_fuels_compensated_by_CCS']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  1  - mdf[rowi , idx2:idx2 + 10] ) 
    
    # CO2_from_fossil_fuels_to_atm[region] = MAX ( 0 , toe_to_CO2_a[region] * ( Total_use_of_fossil_fuels_NOT_compensated[region] * UNIT_conv_to_Gtoe ) + toe_to_CO2_b[region] )
        idxlhs = fcol_in_mdf['CO2_from_fossil_fuels_to_atm']
        idx1 = fcol_in_mdf['Total_use_of_fossil_fuels_NOT_compensated']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.maximum  (  0  ,  toe_to_CO2_a[0:10]  *  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_Gtoe  )  +  toe_to_CO2_b[0:10]  ) 
    
    # CO2_emi_from_IPC_2_CN = CO2_emi_from_IPC_2_CN_L / ( 1 + np.exp ( - CO2_emi_from_IPC_2_CN_k * ( ( GDPpp_USED[cn] * UNIT_conv_to_make_exp_dmnl ) - CO2_emi_from_IPC_2_CN_x0 ) ) )
        idxlhs = fcol_in_mdf['CO2_emi_from_IPC_2_CN']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs] =  CO2_emi_from_IPC_2_CN_L  /  (  1  +  np.exp  (  -  CO2_emi_from_IPC_2_CN_k  *  (  ( mdf[rowi, idx1 + 2] *  UNIT_conv_to_make_exp_dmnl  )  -  CO2_emi_from_IPC_2_CN_x0  )  )  ) 
    
    # CO2_emi_from_IPC2_use_wo_CN[region] = CO2_emi_from_IPC2_use_a[region] * LN ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl ) + CO2_emi_from_IPC2_use_b[region]
        idxlhs = fcol_in_mdf['CO2_emi_from_IPC2_use_wo_CN']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  CO2_emi_from_IPC2_use_a[0:10]  *  np.log  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  )  +  CO2_emi_from_IPC2_use_b[0:10] 
    
    # CO2_emi_from_IPC2_use = IF_THEN_ELSE ( j==2 , CO2_emi_from_IPC_2_CN , CO2_emi_from_IPC2_use_wo_CN )
        idxlhs = fcol_in_mdf['CO2_emi_from_IPC2_use']
        idx1 = fcol_in_mdf['CO2_emi_from_IPC_2_CN']
        idx2 = fcol_in_mdf['CO2_emi_from_IPC2_use_wo_CN']
        for j in range(0,10):
            mdf[rowi, idxlhs + j] =  IF_THEN_ELSE  (  j==2  , mdf[rowi , idx1] , mdf[rowi , idx2 + j] ) 
    
    # Total_CO2_emissions[region] = CO2_from_fossil_fuels_to_atm[region] + CO2_emi_from_IPC2_use[region]
        idxlhs = fcol_in_mdf['Total_CO2_emissions']
        idx1 = fcol_in_mdf['CO2_from_fossil_fuels_to_atm']
        idx2 = fcol_in_mdf['CO2_emi_from_IPC2_use']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10]
    
    # Ctax_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , Ctax_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , Ctax_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , Ctax_R1_via_Excel , Ctax_policy_Min ) ) )
        idxlhs = fcol_in_mdf['Ctax_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  Ctax_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  Ctax_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  Ctax_R1_via_Excel[0:10]  ,  Ctax_policy_Min  )  )  ) 
    
    # Ctax_policy_with_RW[region] = Ctax_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['Ctax_policy_with_RW']
        idx1 = fcol_in_mdf['Ctax_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
     
    # Ctax_pol_div_100[region] = MIN ( Ctax_policy_Max , MAX ( Ctax_policy_Min , Ctax_policy_with_RW[region] ) ) / 1
        idxlhs = fcol_in_mdf['Ctax_pol_div_100']
        idx1 = fcol_in_mdf['Ctax_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], Ctax_policy_Min, Ctax_policy_Max) / 1
    
    # Ctax_policy_with_inequality_effect[region] = MIN ( Ctax_policy_Max , Ctax_pol_div_100[region] / Inequality_effect_on_energy_TA[region] )
        idxlhs = fcol_in_mdf['Ctax_policy_with_inequality_effect']
        idx1 = fcol_in_mdf['Ctax_pol_div_100']
        idx2 = fcol_in_mdf['Inequality_effect_on_energy_TA']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.minimum  (  Ctax_policy_Max  , mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10] ) 
    
    # Ctax_policy[region] = SMOOTH3 ( Ctax_policy_with_inequality_effect[region] , Ctax_Time_to_implement_goal )
        idxin = fcol_in_mdf['Ctax_policy_with_inequality_effect' ]
        idx2 = fcol_in_mdf['Ctax_policy_2']
        idx1 = fcol_in_mdf['Ctax_policy_1']
        idxout = fcol_in_mdf['Ctax_policy']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( Ctax_Time_to_implement_goal / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( Ctax_Time_to_implement_goal / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( Ctax_Time_to_implement_goal / 3) * dt
    
    # Ctax_carbon_tax_policy[region] = Ctax_policy[region] * Ctax_UNIT_conv_to_GtCO2_pr_yr
        idxlhs = fcol_in_mdf['Ctax_carbon_tax_policy']
        idx1 = fcol_in_mdf['Ctax_policy']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  Ctax_UNIT_conv_to_GtCO2_pr_yr 
    
    # Carbon_taxes[region] = Total_CO2_emissions[region] * Ctax_carbon_tax_policy[region] * UNIT_conv_to_G2017pppUSD
        idxlhs = fcol_in_mdf['Carbon_taxes']
        idx1 = fcol_in_mdf['Total_CO2_emissions']
        idx2 = fcol_in_mdf['Ctax_carbon_tax_policy']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] *  UNIT_conv_to_G2017pppUSD 
    
    # Gross_Govt_income[region] = Income_and_policy_taxes_paid_by_owners[region] + Worker_income_and_policy_taxes[region] + Consumption_taxes_last_year[region] + Universal_basic_dividend[region] + Wealth_taxing[region] + Carbon_taxes[region]
        idxlhs = fcol_in_mdf['Gross_Govt_income']
        idx1 = fcol_in_mdf['Income_and_policy_taxes_paid_by_owners']
        idx2 = fcol_in_mdf['Worker_income_and_policy_taxes']
        idx3 = fcol_in_mdf['Consumption_taxes_last_year']
        idx4 = fcol_in_mdf['Universal_basic_dividend']
        idx5 = fcol_in_mdf['Wealth_taxing']
        idx6 = fcol_in_mdf['Carbon_taxes']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] + mdf[rowi , idx4:idx4 + 10] + mdf[rowi , idx5:idx5 + 10] + mdf[rowi , idx6:idx6 + 10]
    
    # Indicated_Future_TLTL_leakage[region] = IF_THEN_ELSE ( zeit > Policy_start_year , Ref_Future_TLTL_leakage , 0 )
        idxlhs = fcol_in_mdf['Indicated_Future_TLTL_leakage']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >  Policy_start_year  ,  Ref_Future_TLTL_leakage  ,  0  ) 
    
    # Future_TLTL_leakage[region] = SMOOTH3 ( Indicated_Future_TLTL_leakage[region] , Time_to_ramp_in_future_TLTL_leakage )
        idxin = fcol_in_mdf['Indicated_Future_TLTL_leakage' ]
        idx2 = fcol_in_mdf['Future_TLTL_leakage_2']
        idx1 = fcol_in_mdf['Future_TLTL_leakage_1']
        idxout = fcol_in_mdf['Future_TLTL_leakage']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( Time_to_ramp_in_future_TLTL_leakage / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( Time_to_ramp_in_future_TLTL_leakage / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( Time_to_ramp_in_future_TLTL_leakage / 3) * dt
    
    # Lfrac_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , Lfrac_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , Lfrac_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , Lfrac_R1_via_Excel , Lfrac_policy_Min ) ) )
        idxlhs = fcol_in_mdf['Lfrac_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  Lfrac_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  Lfrac_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  Lfrac_R1_via_Excel[0:10]  ,  Lfrac_policy_Min  )  )  ) 
    
    # Lfrac_policy_with_RW[region] = Lfrac_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['Lfrac_policy_with_RW']
        idx1 = fcol_in_mdf['Lfrac_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
     
    # Lfrac_pol_div_100[region] = MIN ( Lfrac_policy_Max , MAX ( Lfrac_policy_Min , Lfrac_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['Lfrac_pol_div_100']
        idx1 = fcol_in_mdf['Lfrac_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], Lfrac_policy_Min, Lfrac_policy_Max) / 100
    
    # Lfrac_policy[region] = SMOOTH3 ( Lfrac_pol_div_100[region] , Time_to_implement_UN_policies[region] )
        idxin = fcol_in_mdf['Lfrac_pol_div_100' ]
        idx2 = fcol_in_mdf['Lfrac_policy_2']
        idx1 = fcol_in_mdf['Lfrac_policy_1']
        idxout = fcol_in_mdf['Lfrac_policy']
        idx5 = fcol_in_mdf['Time_to_implement_UN_policies']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
    
    # Future_leakage_indicated[region] = Future_TLTL_leakage[region] * ( 1 - Lfrac_policy[region] )
        idxlhs = fcol_in_mdf['Future_leakage_indicated']
        idx1 = fcol_in_mdf['Future_TLTL_leakage']
        idx2 = fcol_in_mdf['Lfrac_policy']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  1  - mdf[rowi , idx2:idx2 + 10] ) 
    
    # Future_leakage[region] = SMOOTH3 ( Future_leakage_indicated[region] , Time_to_implement_UN_policies[region] )
        idxin = fcol_in_mdf['Future_leakage_indicated' ]
        idx2 = fcol_in_mdf['Future_leakage_2']
        idx1 = fcol_in_mdf['Future_leakage_1']
        idxout = fcol_in_mdf['Future_leakage']
        idx5 = fcol_in_mdf['Time_to_implement_UN_policies']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
    
    # Max_transfer_share[region] = MIN ( 1 , Fraction_of_govt_income_transferred_to_workers_a )
        idxlhs = fcol_in_mdf['Max_transfer_share']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.minimum  (  1  ,  Fraction_of_govt_income_transferred_to_workers_a  ) 
    
    # Fraction_of_govt_income_transferred_to_workers[region] = Max_transfer_share[region] / ( 1 + np.exp ( Fraction_of_govt_income_transferred_to_workers_b * GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl + Fraction_of_govt_income_transferred_to_workers_c ) )
        idxlhs = fcol_in_mdf['Fraction_of_govt_income_transferred_to_workers']
        idx1 = fcol_in_mdf['Max_transfer_share']
        idx2 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  (  1  +  np.exp  (  Fraction_of_govt_income_transferred_to_workers_b  * mdf[rowi , idx2:idx2 + 10] *  UNIT_conv_to_make_exp_dmnl  +  Fraction_of_govt_income_transferred_to_workers_c  )  ) 
    
    # Transfer_from_govt_to_workers[region] = Gross_Govt_income[region] * ( 1 - Future_leakage[region] ) * Fraction_of_govt_income_transferred_to_workers[region]
        idxlhs = fcol_in_mdf['Transfer_from_govt_to_workers']
        idx1 = fcol_in_mdf['Gross_Govt_income']
        idx2 = fcol_in_mdf['Future_leakage']
        idx3 = fcol_in_mdf['Fraction_of_govt_income_transferred_to_workers']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  1  - mdf[rowi , idx2:idx2 + 10] )  * mdf[rowi , idx3:idx3 + 10]
    
    # Govt_income_after_transfers[region] = Gross_Govt_income[region] - Transfer_from_govt_to_workers[region]
        idxlhs = fcol_in_mdf['Govt_income_after_transfers']
        idx1 = fcol_in_mdf['Gross_Govt_income']
        idx2 = fcol_in_mdf['Transfer_from_govt_to_workers']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10]
    
    # SSGDR_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , SSGDR_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , SSGDR_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , SSGDR_R1_via_Excel , SSGDR_policy_Min ) ) )
        idxlhs = fcol_in_mdf['SSGDR_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  SSGDR_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  SSGDR_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  SSGDR_R1_via_Excel[0:10]  ,  SSGDR_policy_Min  )  )  ) 
    
    # SSGDR_policy_with_RW[region] = SSGDR_policy_Min + ( SSGDR_rounds_via_Excel[region] - SSGDR_policy_Min ) * Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['SSGDR_policy_with_RW']
        idx1 = fcol_in_mdf['SSGDR_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] =  SSGDR_policy_Min  +  ( mdf[rowi , idx1:idx1 + 10] -  SSGDR_policy_Min  )  * mdf[rowi , idx2:idx2 + 10]
     
    # SSGDR_pol_div_100[region] = MIN ( SSGDR_policy_Max , MAX ( SSGDR_policy_Min , SSGDR_policy_with_RW[region] ) ) / 1
        idxlhs = fcol_in_mdf['SSGDR_pol_div_100']
        idx1 = fcol_in_mdf['SSGDR_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], SSGDR_policy_Min, SSGDR_policy_Max) / 1
    
    # SSGDR_policy[region] = SMOOTH3 ( SSGDR_pol_div_100[region] , Time_to_implement_UN_policies[region] )
        idxin = fcol_in_mdf['SSGDR_pol_div_100' ]
        idx2 = fcol_in_mdf['SSGDR_policy_2']
        idx1 = fcol_in_mdf['SSGDR_policy_1']
        idxout = fcol_in_mdf['SSGDR_policy']
        idx5 = fcol_in_mdf['Time_to_implement_UN_policies']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
    
    # Govt_payback_period_to_PL[region] = Normal_Govt_payback_period_to_PL * SSGDR_policy[region]
        idxlhs = fcol_in_mdf['Govt_payback_period_to_PL']
        idx1 = fcol_in_mdf['SSGDR_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  Normal_Govt_payback_period_to_PL  * mdf[rowi , idx1:idx1 + 10]
    
    # Govt_debt_repayment_obligation[region] = Govt_debt_owed_to_private_lenders[region] / Govt_payback_period_to_PL[region]
        idxlhs = fcol_in_mdf['Govt_debt_repayment_obligation']
        idx1 = fcol_in_mdf['Govt_debt_owed_to_private_lenders']
        idx2 = fcol_in_mdf['Govt_payback_period_to_PL']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # Short_term_interest_rate[region] = Central_bank_signal_rate[region] + Normal_basic_bank_margin
        idxlhs = fcol_in_mdf['Short_term_interest_rate']
        idx1 = fcol_in_mdf['Central_bank_signal_rate']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] +  Normal_basic_bank_margin 
    
    # Indicated_long_term_interest_rate[region] = Short_term_interest_rate[region] + Long_term_risk_margin
        idxlhs = fcol_in_mdf['Indicated_long_term_interest_rate']
        idx1 = fcol_in_mdf['Short_term_interest_rate']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] +  Long_term_risk_margin 
    
    # Long_term_interest_rate_used_by_private_lenders[region] = SMOOTH ( Indicated_long_term_interest_rate[region] , Long_term_interest_rate_expectation_formation_time )
        idx1 = fcol_in_mdf['Long_term_interest_rate_used_by_private_lenders']
        idx2 = fcol_in_mdf['Indicated_long_term_interest_rate']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1+10] + ( mdf[rowi-1 , idx2:idx2 + 10] - mdf[rowi -1 , idx1:idx1 + 10]) / Long_term_interest_rate_expectation_formation_time * dt
    
    # Govt_defaulting_N_yrs_ago[region] = SMOOTHI ( Govt_defaulting[region] , Time_for_defaulting_to_impact_cost_of_capital , 0 )
        idx1 = fcol_in_mdf['Govt_defaulting_N_yrs_ago']
        idx2 = fcol_in_mdf['Govt_defaulting']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi - 1, idx1:idx1 + 10]) / Time_for_defaulting_to_impact_cost_of_capital * dt
    
    # Govt_default_ratio[region] = Govt_defaulting_N_yrs_ago[region] / Govt_income_after_transfers[region]
        idxlhs = fcol_in_mdf['Govt_default_ratio']
        idx1 = fcol_in_mdf['Govt_defaulting_N_yrs_ago']
        idx2 = fcol_in_mdf['Govt_income_after_transfers']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # Effect_of_defaulting_on_debt_obligations_on_cost_of_capital_for_govt_borrowing[region] = WITH LOOKUP ( Govt_default_ratio[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 1 ) , ( 0.25 , 1.04 ) , ( 0.5 , 1.1 ) , ( 0.75 , 1.3 ) , ( 1 , 1.6 ) , ( 1.5 , 2.5 ) , ( 2 , 4 ) ) )
        tabidx = ftab_in_d_table['Effect_of_defaulting_on_debt_obligations_on_cost_of_capital_for_govt_borrowing'] # fetch the correct table
        idx2 = fcol_in_mdf['Effect_of_defaulting_on_debt_obligations_on_cost_of_capital_for_govt_borrowing'] # get the location of the lhs in mdf
        idx3 = fcol_in_mdf['Govt_default_ratio']
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:,0], look[:, 1])
    
    # Govt_interest_payment_obligation_to_PL[region] = Govt_debt_owed_to_private_lenders[region] * Long_term_interest_rate_used_by_private_lenders[region] * Effect_of_defaulting_on_debt_obligations_on_cost_of_capital_for_govt_borrowing[region]
        idxlhs = fcol_in_mdf['Govt_interest_payment_obligation_to_PL']
        idx1 = fcol_in_mdf['Govt_debt_owed_to_private_lenders']
        idx2 = fcol_in_mdf['Long_term_interest_rate_used_by_private_lenders']
        idx3 = fcol_in_mdf['Effect_of_defaulting_on_debt_obligations_on_cost_of_capital_for_govt_borrowing']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] * mdf[rowi, idx3:idx3 + 10]
    
    # Govt_loan_obligations_to_PL[region] = Govt_debt_repayment_obligation[region] + Govt_interest_payment_obligation_to_PL[region]
        idxlhs = fcol_in_mdf['Govt_loan_obligations_to_PL']
        idx1 = fcol_in_mdf['Govt_debt_repayment_obligation']
        idx2 = fcol_in_mdf['Govt_interest_payment_obligation_to_PL']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10]
    
    # Govt_cash_available_to_meet_all_loan_obligations[region] = Govt_income_after_transfers[region] * Fraction_set_aside_to_service_loans[region]
        idxlhs = fcol_in_mdf['Govt_cash_available_to_meet_all_loan_obligations']
        idx1 = fcol_in_mdf['Govt_income_after_transfers']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  Fraction_set_aside_to_service_loans 
    
    # Govt_cash_to_meet_private_loan_obligations[region] = Govt_cash_available_to_meet_all_loan_obligations[region] * Fraction_of_avail_cash_used_to_meet_private_lender_obligations[region]
        idxlhs = fcol_in_mdf['Govt_cash_to_meet_private_loan_obligations']
        idx1 = fcol_in_mdf['Govt_cash_available_to_meet_all_loan_obligations']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  Fraction_of_avail_cash_used_to_meet_private_lender_obligations 
    
    # Govt_loan_obligations_to_PL_MET[region] = MIN ( Govt_loan_obligations_to_PL[region] , Govt_cash_to_meet_private_loan_obligations[region] )
        idxlhs = fcol_in_mdf['Govt_loan_obligations_to_PL_MET']
        idx1 = fcol_in_mdf['Govt_loan_obligations_to_PL']
        idx2 = fcol_in_mdf['Govt_cash_to_meet_private_loan_obligations']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.minimum  ( mdf[rowi , idx1:idx1 + 10] , mdf[rowi , idx2:idx2 + 10] ) 
    
    # Max_govt_debt_burden_multiplier_historical_and_future[us] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 2050 , 2 ) ] , ( 1980 , 0 ) , ( 1990 , 1 ) , ( 2000 , 0 ) , ( 2018 , 1.2 ) , ( 2020 , 1 ) , ( 2050 , 0.6 ) ) ) Max_govt_debt_burden_multiplier_historical_and_future[af] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 0.75 ) , ( 2000 , 0.5 ) , ( 2018 , 0.35 ) , ( 2020 , 0.3 ) , ( 2050 , 0.5 ) ) ) Max_govt_debt_burden_multiplier_historical_and_future[cn] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0.25 ) , ( 2000 , 0.5 ) , ( 2018 , 0.9 ) , ( 2020 , 0.9 ) , ( 2050 , 0.5 ) ) ) Max_govt_debt_burden_multiplier_historical_and_future[me] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0.25 ) , ( 2000 , 0.5 ) , ( 2018 , 0.6 ) , ( 2020 , 0.75 ) , ( 2050 , 0.6 ) ) ) Max_govt_debt_burden_multiplier_historical_and_future[sa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0.5 ) , ( 2000 , 1 ) , ( 2018 , 0.5 ) , ( 2020 , 0.5 ) , ( 2050 , 0.5 ) ) ) Max_govt_debt_burden_multiplier_historical_and_future[la] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0.25 ) , ( 2000 , 0.5 ) , ( 2018 , 0.6 ) , ( 2020 , 0.75 ) , ( 2050 , 0.6 ) ) ) Max_govt_debt_burden_multiplier_historical_and_future[pa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0.5 ) , ( 2000 , 1 ) , ( 2018 , 1.5 ) , ( 2020 , 1 ) , ( 2050 , 0.5 ) ) ) Max_govt_debt_burden_multiplier_historical_and_future[ec] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0.05 ) , ( 2000 , 0.1 ) , ( 2018 , 0.2 ) , ( 2020 , 0.5 ) , ( 2050 , 0.4 ) ) ) Max_govt_debt_burden_multiplier_historical_and_future[eu] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0.25 ) , ( 2000 , 0.5 ) , ( 2018 , 0.6 ) , ( 2020 , 0.75 ) , ( 2050 , 0.6 ) ) ) Max_govt_debt_burden_multiplier_historical_and_future[se] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 0.75 ) , ( 2000 , 0.5 ) , ( 2018 , 0.35 ) , ( 2020 , 0.3 ) , ( 2050 , 0.5 ) ) )
        tabidx = ftab_in_d_table['Max_govt_debt_burden_multiplier_historical_and_future'] # fetch the correct table
        idx2 = fcol_in_mdf['Max_govt_debt_burden_multiplier_historical_and_future'] # get the location of the lhs in mdf
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(zeit, look[:,0], look[:, j + 1])
    
    # Max_govt_debt[region] = GDP_USED[region] * Max_govt_debt_burden_multiplier_historical_and_future[region] * Reference_max_govt_debt_burden[region]
        idxlhs = fcol_in_mdf['Max_govt_debt']
        idx1 = fcol_in_mdf['GDP_USED']
        idx2 = fcol_in_mdf['Max_govt_debt_burden_multiplier_historical_and_future']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi, idx2:idx2 + 10] *  Reference_max_govt_debt_burden[0:10] 
    
    # Max_govt_debt_smoothed[region] = SMOOTH ( Max_govt_debt[region] , Time_to_smooth_max_govt_debt )
        idx1 = fcol_in_mdf['Max_govt_debt_smoothed']
        idx2 = fcol_in_mdf['Max_govt_debt']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1+10] + ( mdf[rowi-1 , idx2:idx2 + 10] - mdf[rowi -1 , idx1:idx1 + 10]) / Time_to_smooth_max_govt_debt * dt
    
    # Smoothed_Govt_debt_owed_to_private_lenders[region] = SMOOTH ( Govt_debt_owed_to_private_lenders[region] , Time_to_smooth_max_govt_debt )
        idx1 = fcol_in_mdf['Smoothed_Govt_debt_owed_to_private_lenders']
        idx2 = fcol_in_mdf['Govt_debt_owed_to_private_lenders']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1+10] + ( mdf[rowi-1 , idx2:idx2 + 10] - mdf[rowi -1 , idx1:idx1 + 10]) / Time_to_smooth_max_govt_debt * dt
    
    # FMPLDD_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , FMPLDD_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , FMPLDD_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , FMPLDD_R1_via_Excel , FMPLDD_policy_Min ) ) )
        idxlhs = fcol_in_mdf['FMPLDD_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  FMPLDD_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  FMPLDD_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  FMPLDD_R1_via_Excel[0:10]  ,  FMPLDD_policy_Min  )  )  ) 
    
    # FMPLDD_policy_with_RW[region] = FMPLDD_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['FMPLDD_policy_with_RW']
        idx1 = fcol_in_mdf['FMPLDD_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
     
    # FMPLDD_pol_div_100[region] = MIN ( FMPLDD_policy_Max , MAX ( FMPLDD_policy_Min , FMPLDD_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['FMPLDD_pol_div_100']
        idx1 = fcol_in_mdf['FMPLDD_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], FMPLDD_policy_Min, FMPLDD_policy_Max) / 100
    
    # FMPLDD_policy_converted_to_pa[region] = FMPLDD_pol_div_100[region] * UNIT_conv_to_pa
        idxlhs = fcol_in_mdf['FMPLDD_policy_converted_to_pa']
        idx1 = fcol_in_mdf['FMPLDD_pol_div_100']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_pa 
    
    # FMPLDD_policy[region] = SMOOTH3 ( FMPLDD_policy_converted_to_pa[region] , Time_to_implement_UN_policies[region] )
        idxin = fcol_in_mdf['FMPLDD_policy_converted_to_pa' ]
        idx2 = fcol_in_mdf['FMPLDD_policy_2']
        idx1 = fcol_in_mdf['FMPLDD_policy_1']
        idxout = fcol_in_mdf['FMPLDD_policy']
        idx5 = fcol_in_mdf['Time_to_implement_UN_policies']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
    
    # Govt_new_debt_from_private_lenders[region] = MAX ( 0 , ( Max_govt_debt_smoothed[region] - Smoothed_Govt_debt_owed_to_private_lenders[region] ) ) * ( 1 - FMPLDD_policy[region] )
        idxlhs = fcol_in_mdf['Govt_new_debt_from_private_lenders']
        idx1 = fcol_in_mdf['Max_govt_debt_smoothed']
        idx2 = fcol_in_mdf['Smoothed_Govt_debt_owed_to_private_lenders']
        idx3 = fcol_in_mdf['FMPLDD_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.maximum  (  0  ,  ( mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10] )  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Govt_cashflow_to_owners[region] = Govt_loan_obligations_to_PL_MET[region] - Govt_new_debt_from_private_lenders[region]
        idxlhs = fcol_in_mdf['Govt_cashflow_to_owners']
        idx1 = fcol_in_mdf['Govt_loan_obligations_to_PL_MET']
        idx2 = fcol_in_mdf['Govt_new_debt_from_private_lenders']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10]
     
    # GLobal_GDP = SUM ( GDP_model[region!] )
        idxlhs = fcol_in_mdf['GLobal_GDP']
        idx1 = fcol_in_mdf['GDP_model']
        globsum = 0
        for j in range(0,10):
            globsum = globsum + mdf[rowi, idx1 + j]
        mdf[rowi, idxlhs] = globsum 
    
    # Global_GDP_USED = GLobal_GDP
        idxlhs = fcol_in_mdf['Global_GDP_USED']
        idx1 = fcol_in_mdf['GLobal_GDP']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
     
    # Avg_global_long_term_interest_rate = Long_term_interest_rate_used_by_private_lenders[us] * GDP_USED[us] / Global_GDP_USED + Long_term_interest_rate_used_by_private_lenders[cn] * GDP_USED[cn] / Global_GDP_USED + Long_term_interest_rate_used_by_private_lenders[af] * GDP_USED[af] / Global_GDP_USED + Long_term_interest_rate_used_by_private_lenders[me] * GDP_USED[me] / Global_GDP_USED + Long_term_interest_rate_used_by_private_lenders[pa] * GDP_USED[pa] / Global_GDP_USED + Long_term_interest_rate_used_by_private_lenders[ec] * GDP_USED[ec] / Global_GDP_USED + Long_term_interest_rate_used_by_private_lenders[eu] * GDP_USED[eu] / Global_GDP_USED + Long_term_interest_rate_used_by_private_lenders[la] * GDP_USED[la] / Global_GDP_USED + Long_term_interest_rate_used_by_private_lenders[sa] * GDP_USED[sa] / Global_GDP_USED + Long_term_interest_rate_used_by_private_lenders[se] * GDP_USED[se] / Global_GDP_USED
        idxlhs = fcol_in_mdf['Avg_global_long_term_interest_rate']
        idx1 = fcol_in_mdf['Long_term_interest_rate_used_by_private_lenders']
        idx2 = fcol_in_mdf['GDP_USED']
        idx3 = fcol_in_mdf['Global_GDP_USED']
        mdf[rowi, idxlhs] = ( mdf[rowi, idx1 + 0 ] *  mdf[rowi, idx2 + 0 ] /  mdf[rowi, idx3] + mdf[rowi, idx1 + 1 ] *  mdf[rowi, idx2 + 1 ] /  mdf[rowi, idx3] + mdf[rowi, idx1 + 2 ] *  mdf[rowi, idx2 + 2 ] /  mdf[rowi, idx3] + mdf[rowi, idx1 + 3 ] *  mdf[rowi, idx2 + 3 ] /  mdf[rowi, idx3] + mdf[rowi, idx1 + 4 ] *  mdf[rowi, idx2 + 4 ] /  mdf[rowi, idx3] + mdf[rowi, idx1 + 5 ] *  mdf[rowi, idx2 + 5 ] /  mdf[rowi, idx3] + mdf[rowi, idx1 + 6 ] *  mdf[rowi, idx2 + 6 ] /  mdf[rowi, idx3] + mdf[rowi, idx1 + 7 ] *  mdf[rowi, idx2 + 7 ] /  mdf[rowi, idx3] + mdf[rowi, idx1 + 8 ] *  mdf[rowi, idx2 + 8 ] /  mdf[rowi, idx3] + mdf[rowi, idx1 + 9 ] *  mdf[rowi, idx2 + 9 ] /  mdf[rowi, idx3]  )
    
    # Indicated_long_term_interest_rate_after_global_considerations[region] = MIN ( Long_term_interest_rate_used_by_private_lenders[region] , Avg_global_long_term_interest_rate )
        idxlhs = fcol_in_mdf['Indicated_long_term_interest_rate_after_global_considerations']
        idx1 = fcol_in_mdf['Long_term_interest_rate_used_by_private_lenders']
        idx2 = fcol_in_mdf['Avg_global_long_term_interest_rate']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.minimum  ( mdf[rowi , idx1:idx1 + 10] , mdf[rowi , idx2] ) 
    
    # Long_term_interest_rate_used_by_public_lenders[region] = SMOOTH ( Indicated_long_term_interest_rate_after_global_considerations[region] , Long_term_interest_rate_expectation_formation_time )
        idx1 = fcol_in_mdf['Long_term_interest_rate_used_by_public_lenders']
        idx2 = fcol_in_mdf['Indicated_long_term_interest_rate_after_global_considerations']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1+10] + ( mdf[rowi-1 , idx2:idx2 + 10] - mdf[rowi -1 , idx1:idx1 + 10]) / Long_term_interest_rate_expectation_formation_time * dt
    
    # Public_loan_defaults_as_fraction_of_GDP[region] = Public_loan_defaults[region] / GDP_USED[region]
        idxlhs = fcol_in_mdf['Public_loan_defaults_as_fraction_of_GDP']
        idx1 = fcol_in_mdf['Public_loan_defaults']
        idx2 = fcol_in_mdf['GDP_USED']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # Effect_of_public_loan_defaults_on_interest_rate[region] = WITH LOOKUP ( Public_loan_defaults_as_fraction_of_GDP[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 0 ) , ( 0.25 , 0 ) , ( 0.5 , 0.005 ) , ( 0.75 , 0.01 ) , ( 1 , 0.02 ) , ( 1.5 , 0.05 ) , ( 2 , 0.1 ) ) )
        tabidx = ftab_in_d_table['Effect_of_public_loan_defaults_on_interest_rate'] # fetch the correct table
        idx2 = fcol_in_mdf['Effect_of_public_loan_defaults_on_interest_rate'] # get the location of the lhs in mdf
        idx3 = fcol_in_mdf['Public_loan_defaults_as_fraction_of_GDP']
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:,0], look[:, 1])
    
    # Long_term_interest_rate_applied[region] = Long_term_interest_rate_used_by_public_lenders[region] + Effect_of_public_loan_defaults_on_interest_rate[region]
        idxlhs = fcol_in_mdf['Long_term_interest_rate_applied']
        idx1 = fcol_in_mdf['Long_term_interest_rate_used_by_public_lenders']
        idx2 = fcol_in_mdf['Effect_of_public_loan_defaults_on_interest_rate']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi, idx2:idx2 + 10]
    
    # Obligation_for_interest_payments_on_debt_from_public_lenders[region] = Govt_debt_from_public_lenders[region] * Long_term_interest_rate_applied[region]
        idxlhs = fcol_in_mdf['Obligation_for_interest_payments_on_debt_from_public_lenders']
        idx1 = fcol_in_mdf['Govt_debt_from_public_lenders']
        idx2 = fcol_in_mdf['Long_term_interest_rate_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # Time_to_payback_public_debt[region] = Normal_time_to_payback_public_debt * SSGDR_policy[region]
        idxlhs = fcol_in_mdf['Time_to_payback_public_debt']
        idx1 = fcol_in_mdf['SSGDR_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  Normal_time_to_payback_public_debt  * mdf[rowi , idx1:idx1 + 10]
    
    # Obligation_for_payback_of_debt_from_public_lenders[region] = Govt_debt_from_public_lenders[region] / Time_to_payback_public_debt[region]
        idxlhs = fcol_in_mdf['Obligation_for_payback_of_debt_from_public_lenders']
        idx1 = fcol_in_mdf['Govt_debt_from_public_lenders']
        idx2 = fcol_in_mdf['Time_to_payback_public_debt']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # All_loan_service_obligations_to_public_lenders[region] = Obligation_for_interest_payments_on_debt_from_public_lenders[region] + Obligation_for_payback_of_debt_from_public_lenders[region]
        idxlhs = fcol_in_mdf['All_loan_service_obligations_to_public_lenders']
        idx1 = fcol_in_mdf['Obligation_for_interest_payments_on_debt_from_public_lenders']
        idx2 = fcol_in_mdf['Obligation_for_payback_of_debt_from_public_lenders']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10]
    
    # Govt_cash_to_meet_public_loan_obligations[region] = Govt_cash_available_to_meet_all_loan_obligations[region] * ( 1 - Fraction_of_avail_cash_used_to_meet_private_lender_obligations[region] )
        idxlhs = fcol_in_mdf['Govt_cash_to_meet_public_loan_obligations']
        idx1 = fcol_in_mdf['Govt_cash_available_to_meet_all_loan_obligations']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  1  -  Fraction_of_avail_cash_used_to_meet_private_lender_obligations  ) 
    
    # All_loan_service_obligations_to_public_lenders_met[region] = MIN ( All_loan_service_obligations_to_public_lenders[region] , Govt_cash_to_meet_public_loan_obligations[region] )
        idxlhs = fcol_in_mdf['All_loan_service_obligations_to_public_lenders_met']
        idx1 = fcol_in_mdf['All_loan_service_obligations_to_public_lenders']
        idx2 = fcol_in_mdf['Govt_cash_to_meet_public_loan_obligations']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.minimum  ( mdf[rowi , idx1:idx1 + 10] , mdf[rowi , idx2:idx2 + 10] ) 
    
    # All_loan_service_obligations_to_public_lenders_not_met[region] = MAX ( 0 , All_loan_service_obligations_to_public_lenders[region] - All_loan_service_obligations_to_public_lenders_met[region] )
        idxlhs = fcol_in_mdf['All_loan_service_obligations_to_public_lenders_not_met']
        idx1 = fcol_in_mdf['All_loan_service_obligations_to_public_lenders']
        idx2 = fcol_in_mdf['All_loan_service_obligations_to_public_lenders_met']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.maximum  (  0  , mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10] ) 
     
    # Fraction_of_public_loans_not_serviced[region] = ZIDZ ( All_loan_service_obligations_to_public_lenders_not_met[region] , All_loan_service_obligations_to_public_lenders[region] )
        idxlhs = fcol_in_mdf['Fraction_of_public_loans_not_serviced']
        idx1 = fcol_in_mdf['All_loan_service_obligations_to_public_lenders_not_met']
        idx2 = fcol_in_mdf['All_loan_service_obligations_to_public_lenders']
        for i in range(0,10):
            mdf[rowi, idxlhs + i] = ZIDZ ( mdf[rowi, idx1 + i], mdf[rowi, idx2 + i])
    
    # Obligation_for_interest_payments_on_debt_from_public_lenders_actually_met[region] = Obligation_for_interest_payments_on_debt_from_public_lenders[region] * ( 1 - Fraction_of_public_loans_not_serviced[region] )
        idxlhs = fcol_in_mdf['Obligation_for_interest_payments_on_debt_from_public_lenders_actually_met']
        idx1 = fcol_in_mdf['Obligation_for_interest_payments_on_debt_from_public_lenders']
        idx2 = fcol_in_mdf['Fraction_of_public_loans_not_serviced']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  1  - mdf[rowi , idx2:idx2 + 10] ) 
    
    # Actual_govt_cash_inflow[region] = Govt_income_after_transfers[region] - Govt_cashflow_to_owners[region] - Obligation_for_interest_payments_on_debt_from_public_lenders_actually_met[region]
        idxlhs = fcol_in_mdf['Actual_govt_cash_inflow']
        idx1 = fcol_in_mdf['Govt_income_after_transfers']
        idx2 = fcol_in_mdf['Govt_cashflow_to_owners']
        idx3 = fcol_in_mdf['Obligation_for_interest_payments_on_debt_from_public_lenders_actually_met']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10] - mdf[rowi , idx3:idx3 + 10]
    
    # Actual_govt_cash_inflow_seasonally_adjusted[region] = SMOOTH ( Actual_govt_cash_inflow[region] , Time_to_adjust_budget )
        idx1 = fcol_in_mdf['Actual_govt_cash_inflow_seasonally_adjusted']
        idx2 = fcol_in_mdf['Actual_govt_cash_inflow']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1+10] + ( mdf[rowi-1 , idx2:idx2 + 10] - mdf[rowi -1 , idx1:idx1 + 10]) / Time_to_adjust_budget * dt
    
    # SGRPI_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , SGRPI_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , SGRPI_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , SGRPI_R1_via_Excel , SGRPI_policy_Min ) ) )
        idxlhs = fcol_in_mdf['SGRPI_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  SGRPI_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  SGRPI_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  SGRPI_R1_via_Excel[0:10]  ,  SGRPI_policy_Min  )  )  ) 
    
    # SGRPI_policy_with_RW[region] = SGRPI_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['SGRPI_policy_with_RW']
        idx1 = fcol_in_mdf['SGRPI_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
     
    # SGRPI_pol_div_100[region] = MIN ( SGRPI_policy_Max , MAX ( SGRPI_policy_Min , SGRPI_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['SGRPI_pol_div_100']
        idx1 = fcol_in_mdf['SGRPI_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], SGRPI_policy_Min, SGRPI_policy_Max) / 100
    
    # SGRPI_policy[region] = SMOOTH3 ( SGRPI_pol_div_100[region] , Time_to_implement_SGRPI_policy[region] )
        idxin = fcol_in_mdf['SGRPI_pol_div_100' ]
        idx2 = fcol_in_mdf['SGRPI_policy_2']
        idx1 = fcol_in_mdf['SGRPI_policy_1']
        idxout = fcol_in_mdf['SGRPI_policy']
        idx5 = fcol_in_mdf['Time_to_implement_SGRPI_policy']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
    
    # Govt_consumption_fraction_after_SGRPI[region] = MAX ( 0.05 , Govt_consumption_fraction * ( 1 - SGRPI_policy[region] ) )
        idxlhs = fcol_in_mdf['Govt_consumption_fraction_after_SGRPI']
        idx1 = fcol_in_mdf['SGRPI_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.maximum  (  0.05  ,  Govt_consumption_fraction  *  (  1  - mdf[rowi , idx1:idx1 + 10] )  ) 
    
    # Govt_consumption_ie_purchases[region] = Actual_govt_cash_inflow_seasonally_adjusted[region] * Govt_consumption_fraction_after_SGRPI[region]
        idxlhs = fcol_in_mdf['Govt_consumption_ie_purchases']
        idx1 = fcol_in_mdf['Actual_govt_cash_inflow_seasonally_adjusted']
        idx2 = fcol_in_mdf['Govt_consumption_fraction_after_SGRPI']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # LPB_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , LPB_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , LPB_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , LPB_R1_via_Excel , LPB_policy_Min ) ) )
        idxlhs = fcol_in_mdf['LPB_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  LPB_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  LPB_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  LPB_R1_via_Excel[0:10]  ,  LPB_policy_Min  )  )  ) 
    
    # LPB_policy_with_RW[region] = LPB_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['LPB_policy_with_RW']
        idx1 = fcol_in_mdf['LPB_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
     
    # LPB_pol_div_100[region] = MIN ( LPB_policy_Max , MAX ( LPB_policy_Min , LPB_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['LPB_pol_div_100']
        idx1 = fcol_in_mdf['LPB_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], LPB_policy_Min, LPB_policy_Max) / 100
    
    # LPB_policy[region] = SMOOTH3 ( LPB_pol_div_100[region] , LPB_Time_to_implement_policy )
        idxin = fcol_in_mdf['LPB_pol_div_100' ]
        idx2 = fcol_in_mdf['LPB_policy_2']
        idx1 = fcol_in_mdf['LPB_policy_1']
        idxout = fcol_in_mdf['LPB_policy']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( LPB_Time_to_implement_policy / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( LPB_Time_to_implement_policy / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( LPB_Time_to_implement_policy / 3) * dt
    
    # Public_money_from_LPB_policy[region] = GDP_USED[region] * LPB_policy[region]
        idxlhs = fcol_in_mdf['Public_money_from_LPB_policy']
        idx1 = fcol_in_mdf['GDP_USED']
        idx2 = fcol_in_mdf['LPB_policy']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # LPBsplit_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , LPBsplit_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , LPBsplit_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , LPBsplit_R1_via_Excel , LPBsplit_policy_Min ) ) )
        idxlhs = fcol_in_mdf['LPBsplit_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  LPBsplit_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  LPBsplit_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  LPBsplit_R1_via_Excel[0:10]  ,  LPBsplit_policy_Min  )  )  ) 
    
    # LPBsplit_policy_with_RW[region] = LPBsplit_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['LPBsplit_policy_with_RW']
        idx1 = fcol_in_mdf['LPBsplit_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
     
    # LPBsplit_pol_div_100[region] = MIN ( LPBsplit_policy_Max , MAX ( LPBsplit_policy_Min , LPBsplit_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['LPBsplit_pol_div_100']
        idx1 = fcol_in_mdf['LPBsplit_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], LPBsplit_policy_Min, LPBsplit_policy_Max) / 100
    
    # LPBsplit_policy[region] = SMOOTH3 ( LPBsplit_pol_div_100[region] , LPBsplit_Time_to_implement_policy )
        idxin = fcol_in_mdf['LPBsplit_pol_div_100' ]
        idx2 = fcol_in_mdf['LPBsplit_policy_2']
        idx1 = fcol_in_mdf['LPBsplit_policy_1']
        idxout = fcol_in_mdf['LPBsplit_policy']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( LPBsplit_Time_to_implement_policy / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( LPBsplit_Time_to_implement_policy / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( LPBsplit_Time_to_implement_policy / 3) * dt
    
    # Effect_of_public_loan_defaults_on_availability_of_new_loans[region] = WITH LOOKUP ( Public_loan_defaults_as_fraction_of_GDP[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 1 ) , ( 0.25 , 1 ) , ( 0.5 , 1 ) , ( 0.75 , 0.98 ) , ( 1 , 0.95 ) , ( 1.5 , 0.7 ) , ( 2 , 0.3 ) , ( 3 , 0 ) ) )
        tabidx = ftab_in_d_table['Effect_of_public_loan_defaults_on_availability_of_new_loans'] # fetch the correct table
        idx2 = fcol_in_mdf['Effect_of_public_loan_defaults_on_availability_of_new_loans'] # get the location of the lhs in mdf
        idx3 = fcol_in_mdf['Public_loan_defaults_as_fraction_of_GDP']
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:,0], look[:, 1])
    
    # Public_money_from_LPB_policy_to_investment[region] = Public_money_from_LPB_policy[region] * LPBsplit_policy[region] * Effect_of_public_loan_defaults_on_availability_of_new_loans[region]
        idxlhs = fcol_in_mdf['Public_money_from_LPB_policy_to_investment']
        idx1 = fcol_in_mdf['Public_money_from_LPB_policy']
        idx2 = fcol_in_mdf['LPBsplit_policy']
        idx3 = fcol_in_mdf['Effect_of_public_loan_defaults_on_availability_of_new_loans']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] * mdf[rowi, idx3:idx3 + 10]
    
    # Public_money_from_LPB_policy_to_public_spending[region] = Public_money_from_LPB_policy[region] - Public_money_from_LPB_policy_to_investment[region]
        idxlhs = fcol_in_mdf['Public_money_from_LPB_policy_to_public_spending']
        idx1 = fcol_in_mdf['Public_money_from_LPB_policy']
        idx2 = fcol_in_mdf['Public_money_from_LPB_policy_to_investment']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10]
    
    # Public_services[region] = Transfer_from_govt_to_workers[region] + Govt_consumption_ie_purchases[region] * ( 1 - Future_leakage[region] ) + Public_money_from_LPB_policy_to_public_spending[region] * ( 1 - Future_leakage[region] )
        idxlhs = fcol_in_mdf['Public_services']
        idx1 = fcol_in_mdf['Transfer_from_govt_to_workers']
        idx2 = fcol_in_mdf['Govt_consumption_ie_purchases']
        idx3 = fcol_in_mdf['Future_leakage']
        idx4 = fcol_in_mdf['Public_money_from_LPB_policy_to_public_spending']
        idx5 = fcol_in_mdf['Future_leakage']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] *  (  1  - mdf[rowi , idx3:idx3 + 10] )  + mdf[rowi , idx4:idx4 + 10] *  (  1  - mdf[rowi , idx5:idx5 + 10] ) 
    
    # Public_services_pp[region] = Public_services[region] / Population[region]
        idxlhs = fcol_in_mdf['Public_services_pp']
        idx1 = fcol_in_mdf['Public_services']
        idx2 = fcol_in_mdf['Population']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # FEHC_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , FEHC_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , FEHC_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , FEHC_R1_via_Excel , FEHC_policy_Min ) ) )
        idxlhs = fcol_in_mdf['FEHC_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  FEHC_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  FEHC_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  FEHC_R1_via_Excel[0:10]  ,  FEHC_policy_Min  )  )  ) 
    
    # FEHC_policy_with_RW[region] = FEHC_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['FEHC_policy_with_RW']
        idx1 = fcol_in_mdf['FEHC_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
     
    # FEHC_pol_div_100[region] = MIN ( FEHC_policy_Max , MAX ( FEHC_policy_Min , FEHC_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['FEHC_pol_div_100']
        idx1 = fcol_in_mdf['FEHC_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], FEHC_policy_Min, FEHC_policy_Max) / 100
    
    # FEHC_policy[region] = SMOOTH3 ( FEHC_pol_div_100[region] , FEHC_Time_to_implement_policy )
        idxin = fcol_in_mdf['FEHC_pol_div_100' ]
        idx2 = fcol_in_mdf['FEHC_policy_2']
        idx1 = fcol_in_mdf['FEHC_policy_1']
        idxout = fcol_in_mdf['FEHC_policy']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( FEHC_Time_to_implement_policy / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( FEHC_Time_to_implement_policy / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( FEHC_Time_to_implement_policy / 3) * dt
    
    # FEHC_mult_used[region] = 1 - FEHC_policy[region]
        idxlhs = fcol_in_mdf['FEHC_mult_used']
        idx1 = fcol_in_mdf['FEHC_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  - mdf[rowi , idx1:idx1 + 10]
    
    # Effect_of_FEHC_mult_on_years_of_schooling[region] = 1 + ( FEHC_mult_used[region] - 1 ) * Strength_of_FEHC_mult_on_years_of_schooling
        idxlhs = fcol_in_mdf['Effect_of_FEHC_mult_on_years_of_schooling']
        idx1 = fcol_in_mdf['FEHC_mult_used']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  +  ( mdf[rowi , idx1:idx1 + 10] -  1  )  *  Strength_of_FEHC_mult_on_years_of_schooling 
    
    # Years_of_schooling[region] = ( SDG4_a * LN ( Public_services_pp[region] / UNIT_conv_to_make_base_and_ln_dmnl ) + SDG4_b ) / Effect_of_FEHC_mult_on_years_of_schooling[region]
        idxlhs = fcol_in_mdf['Years_of_schooling']
        idx1 = fcol_in_mdf['Public_services_pp']
        idx2 = fcol_in_mdf['Effect_of_FEHC_mult_on_years_of_schooling']
        mdf[rowi, idxlhs:idxlhs + 10] =  (  SDG4_a  *  np.log  ( mdf[rowi , idx1:idx1 + 10] /  UNIT_conv_to_make_base_and_ln_dmnl  )  +  SDG4_b  )  / mdf[rowi , idx2:idx2 + 10]
    
    # SDG4_Score[region] = IF_THEN_ELSE ( Years_of_schooling < SDG4_threshold_red , 0 , IF_THEN_ELSE ( Years_of_schooling < SDG4_threshold_green , 0.5 , 1 ) )
        idxlhs = fcol_in_mdf['SDG4_Score']
        idx1 = fcol_in_mdf['Years_of_schooling']
        idx2 = fcol_in_mdf['Years_of_schooling']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  ( mdf[rowi , idx1:idx1 + 10] <  SDG4_threshold_red  ,  0  ,  IF_THEN_ELSE  ( mdf[rowi , idx2:idx2 + 10] <  SDG4_threshold_green  ,  0.5  ,  1  )  ) 
    
    # SDG_5_Score[region] = IF_THEN_ELSE ( GenderEquality < SDG5_threshold_red , 0 , IF_THEN_ELSE ( GenderEquality < SDG5_threshold_green , 0.5 , 1 ) )
        idxlhs = fcol_in_mdf['SDG_5_Score']
        idx1 = fcol_in_mdf['GenderEquality']
        idx2 = fcol_in_mdf['GenderEquality']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  ( mdf[rowi , idx1:idx1 + 10] <  SDG5_threshold_red  ,  0  ,  IF_THEN_ELSE  ( mdf[rowi , idx2:idx2 + 10] <  SDG5_threshold_green  ,  0.5  ,  1  )  ) 
    
    # Empowerment_score[region] = ( SDG4_Score[region] + SDG_5_Score[region] ) / 2
        idxlhs = fcol_in_mdf['Empowerment_score']
        idx1 = fcol_in_mdf['SDG4_Score']
        idx2 = fcol_in_mdf['SDG_5_Score']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] )  /  2 
    
    # Multplier_from_empowerment_on_speed_of_food_TA[region] = 1 + ( Empowerment_score[region] - 0.5 ) * Strength_of_Effect_of_empowerment_on_speed_of_food_TA
        idxlhs = fcol_in_mdf['Multplier_from_empowerment_on_speed_of_food_TA']
        idx1 = fcol_in_mdf['Empowerment_score']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  +  ( mdf[rowi , idx1:idx1 + 10] -  0.5  )  *  Strength_of_Effect_of_empowerment_on_speed_of_food_TA 
    
    # Smoothed_Multplier_from_empowerment_on_speed_of_food_TA[region] = SMOOTH3 ( Multplier_from_empowerment_on_speed_of_food_TA[region] , Time_to_smooth_Multplier_from_empowerment_on_speed_of_food_TA )
        idxin = fcol_in_mdf['Multplier_from_empowerment_on_speed_of_food_TA' ]
        idx2 = fcol_in_mdf['Smoothed_Multplier_from_empowerment_on_speed_of_food_TA_2']
        idx1 = fcol_in_mdf['Smoothed_Multplier_from_empowerment_on_speed_of_food_TA_1']
        idxout = fcol_in_mdf['Smoothed_Multplier_from_empowerment_on_speed_of_food_TA']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( Time_to_smooth_Multplier_from_empowerment_on_speed_of_food_TA / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( Time_to_smooth_Multplier_from_empowerment_on_speed_of_food_TA / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( Time_to_smooth_Multplier_from_empowerment_on_speed_of_food_TA / 3) * dt
    
    # FWRP_policy_with_RW[region] = FWRP_rounds_via_Excel[region] * Smoothed_Reform_willingness[region] / Inequality_effect_on_energy_TA[region] * Smoothed_Multplier_from_empowerment_on_speed_of_food_TA[region]
        idxlhs = fcol_in_mdf['FWRP_policy_with_RW']
        idx1 = fcol_in_mdf['FWRP_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        idx3 = fcol_in_mdf['Inequality_effect_on_energy_TA']
        idx4 = fcol_in_mdf['Smoothed_Multplier_from_empowerment_on_speed_of_food_TA']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] / mdf[rowi , idx3:idx3 + 10] * mdf[rowi , idx4:idx4 + 10]
     
    # FWRP_pol_div_100[region] = MIN ( FWRP_policy_Max , MAX ( FWRP_policy_Min , FWRP_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['FWRP_pol_div_100']
        idx1 = fcol_in_mdf['FWRP_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], FWRP_policy_Min, FWRP_policy_Max) / 100
    
    # FWRP_policy[region] = SMOOTH3 ( FWRP_pol_div_100[region] , FWRP_Time_to_implement_goal )
        idxin = fcol_in_mdf['FWRP_pol_div_100' ]
        idx2 = fcol_in_mdf['FWRP_policy_2']
        idx1 = fcol_in_mdf['FWRP_policy_1']
        idxout = fcol_in_mdf['FWRP_policy']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( FWRP_Time_to_implement_goal / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( FWRP_Time_to_implement_goal / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( FWRP_Time_to_implement_goal / 3) * dt
    
    # Fraction_of_food_wasted[region] = Food_wasted_in_1980[region] * ( 1 - FWRP_policy[region] )
        idxlhs = fcol_in_mdf['Fraction_of_food_wasted']
        idx1 = fcol_in_mdf['FWRP_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  Food_wasted_in_1980[0:10]  *  (  1  - mdf[rowi , idx1:idx1 + 10] ) 
    
    # cereal_dmd_food_pp_wasted[region] = cereal_dmd_food_pp[region] * Fraction_of_food_wasted[region]
        idxlhs = fcol_in_mdf['cereal_dmd_food_pp_wasted']
        idx1 = fcol_in_mdf['cereal_dmd_food_pp']
        idx2 = fcol_in_mdf['Fraction_of_food_wasted']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # oth_crop_dmd_pp[region] = oth_crop_dmd_pp_a[region] * LN ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl ) + oth_crop_dmd_pp_b[region]
        idxlhs = fcol_in_mdf['oth_crop_dmd_pp']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  oth_crop_dmd_pp_a[0:10]  *  np.log  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  )  +  oth_crop_dmd_pp_b[0:10] 
    
    # oth_crop_dmd_food_pp[region] = oth_crop_dmd_pp[region] * UNIT_conv_to_kg_crop_ppy
        idxlhs = fcol_in_mdf['oth_crop_dmd_food_pp']
        idx1 = fcol_in_mdf['oth_crop_dmd_pp']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_kg_crop_ppy 
    
    # oth_crop_dmd_food_pp_consumed[region] = oth_crop_dmd_food_pp[region] * ( 1 - Food_wasted_in_1980[region] )
        idxlhs = fcol_in_mdf['oth_crop_dmd_food_pp_consumed']
        idx1 = fcol_in_mdf['oth_crop_dmd_food_pp']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  1  -  Food_wasted_in_1980[0:10]  ) 
    
    # oth_crop_dmd_food_pp_wasted[region] = oth_crop_dmd_food_pp[region] * Fraction_of_food_wasted[region]
        idxlhs = fcol_in_mdf['oth_crop_dmd_food_pp_wasted']
        idx1 = fcol_in_mdf['oth_crop_dmd_food_pp']
        idx2 = fcol_in_mdf['Fraction_of_food_wasted']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # All_crop_dmd_food[region] = ( cereal_dmd_food_pp_consumed[region] + cereal_dmd_food_pp_wasted[region] + oth_crop_dmd_food_pp_consumed[region] + oth_crop_dmd_food_pp_wasted[region] ) * Population[region] / UNIT_conv_from_kg_to_Mt * UNIT_conv_btw_p_and_Mp
        idxlhs = fcol_in_mdf['All_crop_dmd_food']
        idx1 = fcol_in_mdf['cereal_dmd_food_pp_consumed']
        idx2 = fcol_in_mdf['cereal_dmd_food_pp_wasted']
        idx3 = fcol_in_mdf['oth_crop_dmd_food_pp_consumed']
        idx4 = fcol_in_mdf['oth_crop_dmd_food_pp_wasted']
        idx5 = fcol_in_mdf['Population']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] + mdf[rowi , idx4:idx4 + 10] )  * mdf[rowi , idx5:idx5 + 10] /  UNIT_conv_from_kg_to_Mt  *  UNIT_conv_btw_p_and_Mp 
    
    # red_meat_dmd_PA = red_meat_dmd_PA_a * ( GDPpp_USED[pa] * UNIT_conv_to_make_exp_dmnl ) ^ red_meat_dmd_PA_b
        idxlhs = fcol_in_mdf['red_meat_dmd_PA']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs] =  red_meat_dmd_PA_a  *  ( mdf[rowi, idx1 + 6] *  UNIT_conv_to_make_exp_dmnl  )  **  red_meat_dmd_PA_b 
    
    # red_meat_dmd_SA = red_meat_dmd_SA_a * ( GDPpp_USED[sa] * UNIT_conv_to_make_exp_dmnl ) ^ red_meat_dmd_SA_b + red_meat_dmd_SA_c
        idxlhs = fcol_in_mdf['red_meat_dmd_SA']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs] =  red_meat_dmd_SA_a  *  ( mdf[rowi, idx1 + 4] *  UNIT_conv_to_make_exp_dmnl  )  **  red_meat_dmd_SA_b  +  red_meat_dmd_SA_c 
    
    # red_meat_dmd_func_pp[region] = red_meat_dmd_func_pp_L[region] / ( 1 + np.exp ( - red_meat_dmd_func_pp_k[region] * ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl - red_meat_dmd_func_pp_x0[region] ) ) ) + red_meat_dmd_func_pp_min[region]
        idxlhs = fcol_in_mdf['red_meat_dmd_func_pp']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  red_meat_dmd_func_pp_L[0:10]  /  (  1  +  np.exp  (  -  red_meat_dmd_func_pp_k[0:10]  *  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  -  red_meat_dmd_func_pp_x0[0:10]  )  )  )  +  red_meat_dmd_func_pp_min[0:10] 
    
    # red_meat_dmd_pp = IF_THEN_ELSE ( j==6 , red_meat_dmd_PA , IF_THEN_ELSE ( j==4 , red_meat_dmd_SA , red_meat_dmd_func_pp ) )
        idxlhs = fcol_in_mdf['red_meat_dmd_pp']
        idx1 = fcol_in_mdf['red_meat_dmd_PA']
        idx2 = fcol_in_mdf['red_meat_dmd_SA']
        idx3 = fcol_in_mdf['red_meat_dmd_func_pp']
        for j in range(0,10):
            mdf[rowi, idxlhs + j] =  IF_THEN_ELSE  (  j==6  , mdf[rowi , idx1] ,  IF_THEN_ELSE  (  j==4  , mdf[rowi , idx2] , mdf[rowi , idx3 + j] )  ) 
    
    # RMDR_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , RMDR_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , RMDR_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , RMDR_R1_via_Excel , RMDR_policy_Min ) ) )
        idxlhs = fcol_in_mdf['RMDR_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  RMDR_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  RMDR_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  RMDR_R1_via_Excel[0:10]  ,  RMDR_policy_Min  )  )  ) 
    
    # RMDR_policy_with_RW[region] = RMDR_rounds_via_Excel[region] * Smoothed_Reform_willingness[region] / Inequality_effect_on_energy_TA[region] * Smoothed_Multplier_from_empowerment_on_speed_of_food_TA[region]
        idxlhs = fcol_in_mdf['RMDR_policy_with_RW']
        idx1 = fcol_in_mdf['RMDR_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        idx3 = fcol_in_mdf['Inequality_effect_on_energy_TA']
        idx4 = fcol_in_mdf['Smoothed_Multplier_from_empowerment_on_speed_of_food_TA']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] / mdf[rowi , idx3:idx3 + 10] * mdf[rowi , idx4:idx4 + 10]
     
    # RMDR_pol_div_100[region] = MIN ( RMDR_policy_Max , MAX ( RMDR_policy_Min , RMDR_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['RMDR_pol_div_100']
        idx1 = fcol_in_mdf['RMDR_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], RMDR_policy_Min, RMDR_policy_Max) / 100
    
    # RMDR_policy[region] = SMOOTH3 ( RMDR_pol_div_100[region] , RMDR_Time_to_implement_policy )
        idxin = fcol_in_mdf['RMDR_pol_div_100' ]
        idx2 = fcol_in_mdf['RMDR_policy_2']
        idx1 = fcol_in_mdf['RMDR_policy_1']
        idxout = fcol_in_mdf['RMDR_policy']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( RMDR_Time_to_implement_policy / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( RMDR_Time_to_implement_policy / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( RMDR_Time_to_implement_policy / 3) * dt
    
    # RMDR_multiplier_used[region] = 1 - RMDR_policy[region]
        idxlhs = fcol_in_mdf['RMDR_multiplier_used']
        idx1 = fcol_in_mdf['RMDR_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  - mdf[rowi , idx1:idx1 + 10]
    
    # red_meat_demand_pp[region] = red_meat_dmd_pp[region] * UNIT_conv_to_kg_red_meat_ppy * RMDR_multiplier_used[region]
        idxlhs = fcol_in_mdf['red_meat_demand_pp']
        idx1 = fcol_in_mdf['red_meat_dmd_pp']
        idx2 = fcol_in_mdf['RMDR_multiplier_used']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_kg_red_meat_ppy  * mdf[rowi , idx2:idx2 + 10]
    
    # red_meat_demand_pp_consumed[region] = red_meat_demand_pp[region] * ( 1 - Food_wasted_in_1980[region] )
        idxlhs = fcol_in_mdf['red_meat_demand_pp_consumed']
        idx1 = fcol_in_mdf['red_meat_demand_pp']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  1  -  Food_wasted_in_1980[0:10]  ) 
    
    # red_meat_demand_pp_wasted[region] = red_meat_demand_pp[region] * Fraction_of_food_wasted[region]
        idxlhs = fcol_in_mdf['red_meat_demand_pp_wasted']
        idx1 = fcol_in_mdf['red_meat_demand_pp']
        idx2 = fcol_in_mdf['Fraction_of_food_wasted']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # red_meat_demand[region] = ( red_meat_demand_pp_consumed[region] + red_meat_demand_pp_wasted[region] ) * Population[region] / UNIT_conv_kgrmeat_and_Mtrmea * UNIT_conv_btw_p_and_Mp
        idxlhs = fcol_in_mdf['red_meat_demand']
        idx1 = fcol_in_mdf['red_meat_demand_pp_consumed']
        idx2 = fcol_in_mdf['red_meat_demand_pp_wasted']
        idx3 = fcol_in_mdf['Population']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] )  * mdf[rowi , idx3:idx3 + 10] /  UNIT_conv_kgrmeat_and_Mtrmea  *  UNIT_conv_btw_p_and_Mp 
    
    # RIPLGF_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , RIPLGF_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , RIPLGF_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , RIPLGF_R1_via_Excel , RIPLGF_policy_Min ) ) )
        idxlhs = fcol_in_mdf['RIPLGF_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  RIPLGF_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  RIPLGF_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  RIPLGF_R1_via_Excel[0:10]  ,  RIPLGF_policy_Min  )  )  ) 
    
    # RIPLGF_policy_with_RW[region] = RIPLGF_rounds_via_Excel[region] * Smoothed_Reform_willingness[region] / Inequality_effect_on_energy_TA[region] * Smoothed_Multplier_from_empowerment_on_speed_of_food_TA[region]
        idxlhs = fcol_in_mdf['RIPLGF_policy_with_RW']
        idx1 = fcol_in_mdf['RIPLGF_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        idx3 = fcol_in_mdf['Inequality_effect_on_energy_TA']
        idx4 = fcol_in_mdf['Smoothed_Multplier_from_empowerment_on_speed_of_food_TA']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] / mdf[rowi , idx3:idx3 + 10] * mdf[rowi , idx4:idx4 + 10]
     
    # RIPLGF_pol_div_100[region] = MIN ( RIPLGF_policy_Max , MAX ( RIPLGF_policy_Min , RIPLGF_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['RIPLGF_pol_div_100']
        idx1 = fcol_in_mdf['RIPLGF_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], RIPLGF_policy_Min, RIPLGF_policy_Max) / 100
    
    # RIPLGF_policy[region] = SMOOTH3 ( RIPLGF_pol_div_100[region] , RIPLGF_smoothing_time[region] )
        idxin = fcol_in_mdf['RIPLGF_pol_div_100' ]
        idx2 = fcol_in_mdf['RIPLGF_policy_2']
        idx1 = fcol_in_mdf['RIPLGF_policy_1']
        idxout = fcol_in_mdf['RIPLGF_policy']
        idx5 = fcol_in_mdf['RIPLGF_smoothing_time']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
    
    # Desired_net_export_of_red_meat_after_import_restriction_policy[region] = Desired_net_export_of_red_meat[region] * ( 1 - RIPLGF_policy[region] )
        idxlhs = fcol_in_mdf['Desired_net_export_of_red_meat_after_import_restriction_policy']
        idx1 = fcol_in_mdf['RIPLGF_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  Desired_net_export_of_red_meat[0:10]  *  (  1  - mdf[rowi , idx1:idx1 + 10] ) 
    
    # Red_meat_production[region] = ( red_meat_demand[region] / ( 1 - Desired_net_export_of_red_meat_after_import_restriction_policy[region] ) )
        idxlhs = fcol_in_mdf['Red_meat_production']
        idx1 = fcol_in_mdf['red_meat_demand']
        idx2 = fcol_in_mdf['Desired_net_export_of_red_meat_after_import_restriction_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] /  (  1  - mdf[rowi , idx2:idx2 + 10] )  ) 
    
    # white_meat_dmd_CN = white_meat_dmd_CN_a * LN ( GDPpp_USED[cn] * UNIT_conv_to_make_exp_dmnl ) + white_meat_dmd_CN_b
        idxlhs = fcol_in_mdf['white_meat_dmd_CN']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs] =  white_meat_dmd_CN_a  *  np.log  ( mdf[rowi, idx1 + 2] *  UNIT_conv_to_make_exp_dmnl  )  +  white_meat_dmd_CN_b 
    
    # white_meat_dmd_func_pp[region] = white_meat_dmd_func_pp_L[region] / ( 1 + np.exp ( - white_meat_dmd_func_pp_k[region] * ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl - white_meat_dmd_func_pp_x0[region] ) ) )
        idxlhs = fcol_in_mdf['white_meat_dmd_func_pp']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  white_meat_dmd_func_pp_L[0:10]  /  (  1  +  np.exp  (  -  white_meat_dmd_func_pp_k[0:10]  *  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  -  white_meat_dmd_func_pp_x0[0:10]  )  )  ) 
    
    # white_meat_dmd_pp = IF_THEN_ELSE ( j==2 , white_meat_dmd_CN , white_meat_dmd_func_pp )
        idxlhs = fcol_in_mdf['white_meat_dmd_pp']
        idx1 = fcol_in_mdf['white_meat_dmd_CN']
        idx2 = fcol_in_mdf['white_meat_dmd_func_pp']
        for j in range(0,10):
            mdf[rowi, idxlhs + j] =  IF_THEN_ELSE  (  j==2  , mdf[rowi , idx1] , mdf[rowi , idx2 + j] ) 
    
    # white_meat_demand_pp[region] = white_meat_dmd_pp[region] * UNIT_conv_to_kg_white_meat_ppy
        idxlhs = fcol_in_mdf['white_meat_demand_pp']
        idx1 = fcol_in_mdf['white_meat_dmd_pp']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_kg_white_meat_ppy 
    
    # white_meat_demand_pp_consumed[region] = white_meat_demand_pp[region] * ( 1 - Food_wasted_in_1980[region] )
        idxlhs = fcol_in_mdf['white_meat_demand_pp_consumed']
        idx1 = fcol_in_mdf['white_meat_demand_pp']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  1  -  Food_wasted_in_1980[0:10]  ) 
    
    # white_meat_demand_pp_wasted[region] = white_meat_demand_pp[region] * Fraction_of_food_wasted[region]
        idxlhs = fcol_in_mdf['white_meat_demand_pp_wasted']
        idx1 = fcol_in_mdf['white_meat_demand_pp']
        idx2 = fcol_in_mdf['Fraction_of_food_wasted']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # white_meat_demand[region] = ( white_meat_demand_pp_consumed[region] + white_meat_demand_pp_wasted[region] ) * Population[region] / UNIT_conv_kgwmeat_and_Mtwmeat * UNIT_conv_btw_p_and_Mp
        idxlhs = fcol_in_mdf['white_meat_demand']
        idx1 = fcol_in_mdf['white_meat_demand_pp_consumed']
        idx2 = fcol_in_mdf['white_meat_demand_pp_wasted']
        idx3 = fcol_in_mdf['Population']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] )  * mdf[rowi , idx3:idx3 + 10] /  UNIT_conv_kgwmeat_and_Mtwmeat  *  UNIT_conv_btw_p_and_Mp 
    
    # Desired_net_export_of_white_meat[us] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0 ) , ( 2000 , 0 ) , ( 2010 , 0.1 ) , ( 2020 , 0.2 ) , ( 2050 , 0.2 ) , ( 2100 , 0.1 ) ) ) Desired_net_export_of_white_meat[af] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , - 0.04 ) , ( 1990 , - 0.04 ) , ( 2000 , - 0.04 ) , ( 2010 , - 0.04 ) , ( 2020 , - 0.04 ) , ( 2050 , - 0.04 ) , ( 2100 , - 0.04 ) ) ) Desired_net_export_of_white_meat[cn] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , - 0.04 ) , ( 1990 , - 0.04 ) , ( 2000 , - 0.04 ) , ( 2010 , - 0.04 ) , ( 2020 , - 0.04 ) , ( 2050 , - 0.04 ) , ( 2100 , - 0.04 ) ) ) Desired_net_export_of_white_meat[me] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , - 0.2 ) , ( 1990 , - 0.2 ) , ( 2000 , - 0.2 ) , ( 2010 , - 0.2 ) , ( 2020 , - 0.2 ) , ( 2050 , - 0.2 ) , ( 2100 , - 0.2 ) ) ) Desired_net_export_of_white_meat[sa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , - 0.04 ) , ( 1990 , - 0.04 ) , ( 2000 , - 0.04 ) , ( 2010 , - 0.04 ) , ( 2020 , - 0.04 ) , ( 2050 , - 0.04 ) , ( 2100 , - 0.04 ) ) ) Desired_net_export_of_white_meat[la] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0 ) , ( 2000 , 0 ) , ( 2010 , 0 ) , ( 2020 , 0 ) , ( 2050 , 0 ) , ( 2100 , 0 ) ) ) Desired_net_export_of_white_meat[pa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0 ) , ( 2000 , 0 ) , ( 2010 , 0 ) , ( 2020 , 0 ) , ( 2050 , 0 ) , ( 2100 , 0 ) ) ) Desired_net_export_of_white_meat[ec] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0 ) , ( 2000 , 0 ) , ( 2010 , 0 ) , ( 2020 , 0 ) , ( 2050 , 0 ) , ( 2100 , 0 ) ) ) Desired_net_export_of_white_meat[eu] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0 ) , ( 2000 , 0 ) , ( 2010 , 0.1 ) , ( 2020 , 0.2 ) , ( 2050 , 0.2 ) , ( 2100 , 0.1 ) ) ) Desired_net_export_of_white_meat[se] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , - 0.04 ) , ( 1990 , - 0.04 ) , ( 2000 , - 0.04 ) , ( 2010 , - 0.04 ) , ( 2020 , - 0.04 ) , ( 2050 , - 0.04 ) , ( 2100 , - 0.04 ) ) )
        tabidx = ftab_in_d_table['Desired_net_export_of_white_meat'] # fetch the correct table
        idx2 = fcol_in_mdf['Desired_net_export_of_white_meat'] # get the location of the lhs in mdf
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(zeit, look[:,0], look[:, j + 1])
    
    # Desired_net_export_of_white_meat_after_import_restriction_policy[region] = Desired_net_export_of_white_meat[region] * ( 1 - RIPLGF_policy[region] )
        idxlhs = fcol_in_mdf['Desired_net_export_of_white_meat_after_import_restriction_policy']
        idx1 = fcol_in_mdf['Desired_net_export_of_white_meat']
        idx2 = fcol_in_mdf['RIPLGF_policy']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi, idx1:idx1 + 10] *  (  1  - mdf[rowi , idx2:idx2 + 10] ) 
    
    # White_meat_production[region] = white_meat_demand[region] / ( 1 - Desired_net_export_of_white_meat_after_import_restriction_policy[region] )
        idxlhs = fcol_in_mdf['White_meat_production']
        idx1 = fcol_in_mdf['white_meat_demand']
        idx2 = fcol_in_mdf['Desired_net_export_of_white_meat_after_import_restriction_policy']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  (  1  - mdf[rowi , idx2:idx2 + 10] ) 
    
    # Meat_production[region] = Red_meat_production[region] * UNIT_conv_red_meat + White_meat_production[region] * UNIT_conv_white_meat
        idxlhs = fcol_in_mdf['Meat_production']
        idx1 = fcol_in_mdf['Red_meat_production']
        idx2 = fcol_in_mdf['White_meat_production']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_red_meat  + mdf[rowi , idx2:idx2 + 10] *  UNIT_conv_white_meat 
    
    # Feed_dmd[region] = Feed_dmd_a[region] * LN ( Meat_production[region] * UNIT_conv_meat_to_feed ) + Feed_dmd_b[region]
        idxlhs = fcol_in_mdf['Feed_dmd']
        idx1 = fcol_in_mdf['Meat_production']
        mdf[rowi, idxlhs:idxlhs + 10] =  Feed_dmd_a[0:10]  *  np.log  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_meat_to_feed  )  +  Feed_dmd_b[0:10] 
    
    # All_crop_regional_dmd_last_year[region] = SMOOTHI ( All_crop_regional_dmd[region] , One_year , All_crop_dmd_food_in_1980[region] )
        idx1 = fcol_in_mdf['All_crop_regional_dmd_last_year']
        idx2 = fcol_in_mdf['All_crop_regional_dmd']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi - 1, idx1:idx1 + 10]) / One_year * dt
    
    # Desired_crop_import[region] = SMOOTHI ( Desired_crop_import_indicated[region] , One_year , Reference_crop_import_in_1980[region] )
        idx1 = fcol_in_mdf['Desired_crop_import']
        idx2 = fcol_in_mdf['Desired_crop_import_indicated']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi - 1, idx1:idx1 + 10]) / One_year * dt
    
    # Eff_of_wealth_on_crop_import[region] = WITH LOOKUP ( GDPpp_USED[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 0 ) , ( 10 , 0.2 ) , ( 20 , 0.3 ) , ( 30 , 0.4 ) , ( 50 , 0.6 ) , ( 60 , 0.7 ) , ( 100 , 1 ) ) )
        tabidx = ftab_in_d_table['Eff_of_wealth_on_crop_import'] # fetch the correct table
        idx2 = fcol_in_mdf['Eff_of_wealth_on_crop_import'] # get the location of the lhs in mdf
        idx3 = fcol_in_mdf['GDPpp_USED']
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:,0], look[:, 1])
    
    # Actual_crop_import[region] = Desired_crop_import[region] * Eff_of_wealth_on_crop_import[region]
        idxlhs = fcol_in_mdf['Actual_crop_import']
        idx1 = fcol_in_mdf['Desired_crop_import']
        idx2 = fcol_in_mdf['Eff_of_wealth_on_crop_import']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi, idx2:idx2 + 10]
    
    # Net_export_of_crops[region] = All_crop_regional_dmd_last_year[region] * Desired_net_export_of_crops[region] - Actual_crop_import[region]
        idxlhs = fcol_in_mdf['Net_export_of_crops']
        idx1 = fcol_in_mdf['All_crop_regional_dmd_last_year']
        idx2 = fcol_in_mdf['Actual_crop_import']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  Desired_net_export_of_crops[0:10]  - mdf[rowi , idx2:idx2 + 10]
    
    # All_crop_regional_dmd[region] = All_crop_dmd_food[region] + Feed_dmd[region] + Net_export_of_crops[region]
        idxlhs = fcol_in_mdf['All_crop_regional_dmd']
        idx1 = fcol_in_mdf['All_crop_dmd_food']
        idx2 = fcol_in_mdf['Feed_dmd']
        idx3 = fcol_in_mdf['Net_export_of_crops']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10]
    
    # Smoothed_Crop_yield_from_N_use[region] = SMOOTHI ( Crop_yield_from_N_use[region] , One_year , crop_yield_in_1980[region] )
        idx1 = fcol_in_mdf['Smoothed_Crop_yield_from_N_use']
        idx2 = fcol_in_mdf['Crop_yield_from_N_use']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi - 1, idx1:idx1 + 10]) / One_year * dt
    
    # Smoothed_Cumulative_N_use_for_soil_quality[region] = SMOOTH ( Cumulative_N_use_since_2020[region] , Time_for_N_use_to_affect_soil_quality )
        idx1 = fcol_in_mdf['Smoothed_Cumulative_N_use_for_soil_quality']
        idx2 = fcol_in_mdf['Cumulative_N_use_since_2020']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1+10] + ( mdf[rowi-1 , idx2:idx2 + 10] - mdf[rowi -1 , idx1:idx1 + 10]) / Time_for_N_use_to_affect_soil_quality * dt
    
    # Eff_of_cumulative_N_use_on_soil_quality[region] = WITH LOOKUP ( Smoothed_Cumulative_N_use_for_soil_quality[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 1 ) , ( 10 , 1.05 ) , ( 20 , 1.5 ) ) )
        tabidx = ftab_in_d_table['Eff_of_cumulative_N_use_on_soil_quality'] # fetch the correct table
        idx2 = fcol_in_mdf['Eff_of_cumulative_N_use_on_soil_quality'] # get the location of the lhs in mdf
        idx3 = fcol_in_mdf['Smoothed_Cumulative_N_use_for_soil_quality']
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:,0], look[:, 1])
    
    # Soil_quality[region] = ( Soil_quality_in_1980[region] / Eff_of_cumulative_N_use_on_soil_quality[region] ) * ( ( 1 - Regenerative_cropland_fraction[region] ) + Soil_quality_of_regenerative_cropland[region] * Regenerative_cropland_fraction[region] )
        idxlhs = fcol_in_mdf['Soil_quality']
        idx1 = fcol_in_mdf['Eff_of_cumulative_N_use_on_soil_quality']
        idx2 = fcol_in_mdf['Regenerative_cropland_fraction']
        idx3 = fcol_in_mdf['Regenerative_cropland_fraction']
        mdf[rowi, idxlhs:idxlhs + 10] =  (  Soil_quality_in_1980  / mdf[rowi, idx1:idx1 + 10] )  *  (  (  1  - mdf[rowi , idx2:idx2 + 10] )  +  Soil_quality_of_regenerative_cropland  * mdf[rowi , idx3:idx3 + 10] ) 
    
    # MODEL_CO2_concentration_in_atmosphere2_ppm = C_in_atmosphere_GtC / Conversion_constant_GtC_to_ppm
        idxlhs = fcol_in_mdf['MODEL_CO2_concentration_in_atmosphere2_ppm']
        idx1 = fcol_in_mdf['C_in_atmosphere_GtC']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Conversion_constant_GtC_to_ppm 
    
    # CO2_concentration_used_after_any_experiments_ppm = MODEL_CO2_concentration_in_atmosphere2_ppm
        idxlhs = fcol_in_mdf['CO2_concentration_used_after_any_experiments_ppm']
        idx1 = fcol_in_mdf['MODEL_CO2_concentration_in_atmosphere2_ppm']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # CO2_concentration_ratio_wrt_2020 = IF_THEN_ELSE ( zeit < 2020 , 1 , CO2_concentration_used_after_any_experiments_ppm / CO2_concentration_2020 )
        idxlhs = fcol_in_mdf['CO2_concentration_ratio_wrt_2020']
        idx1 = fcol_in_mdf['CO2_concentration_used_after_any_experiments_ppm']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  (  zeit  <  2020  ,  1  , mdf[rowi, idx1] /  CO2_concentration_2020  ) 
    
    # Eff_of_CO2_on_yield = 1 + SoE_of_CO2_on_yield * ( CO2_concentration_ratio_wrt_2020 - 1 )
        idxlhs = fcol_in_mdf['Eff_of_CO2_on_yield']
        idx1 = fcol_in_mdf['CO2_concentration_ratio_wrt_2020']
        mdf[rowi, idxlhs] =  1  +  SoE_of_CO2_on_yield  *  ( mdf[rowi, idx1] -  1  ) 
    
    # Thermal_expansion_surface_pct = WITH LOOKUP ( Temp_surface , ( [ ( 0 , 0 ) - ( 20 , 0.2 ) ] , ( 0 , 0.015 ) , ( 1 , 0.008 ) , ( 2 , 0.0033 ) , ( 3 , 0.001 ) , ( 4 , 0 ) , ( 5 , 0.0012 ) , ( 6 , 0.0033 ) , ( 7 , 0.008 ) , ( 8 , 0.013 ) , ( 9 , 0.021 ) , ( 10 , 0.0287 ) , ( 20 , 0.1963 ) ) )
        tabidx = ftab_in_d_table['Thermal_expansion_surface_pct'] # fetch the correct table
        idxlhs = fcol_in_mdf['Thermal_expansion_surface_pct'] # get the location of the lhs in mdf
        idx1 = fcol_in_mdf['Temp_surface']
        look = d_table[tabidx]
        valgt = GRAPH(mdf[rowi,  idx1], look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # Thermal_expansion_surface_anfang_pct = WITH LOOKUP ( Temp_surface_anfang_less_zero_k , ( [ ( 0 , 0 ) - ( 20 , 0.2 ) ] , ( 0 , 0.015 ) , ( 1 , 0.008 ) , ( 2 , 0.0033 ) , ( 3 , 0.001 ) , ( 4 , 0 ) , ( 5 , 0.0012 ) , ( 6 , 0.0033 ) , ( 7 , 0.008 ) , ( 8 , 0.013 ) , ( 9 , 0.021 ) , ( 10 , 0.0287 ) , ( 20 , 0.1963 ) ) )
        tabidx = ftab_in_d_table['Thermal_expansion_surface_anfang_pct'] # fetch the correct table
        idxlhs = fcol_in_mdf['Thermal_expansion_surface_anfang_pct'] # get the location of the lhs in mdf
        look = d_table[tabidx]
        valgt = GRAPH( Temp_surface_anfang_less_zero_k , look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # Volume_expansion_from_thermal_expansion_surface_Gm3_is_km3 = Surface_ocean_warm_volume * ( Thermal_expansion_surface_pct - Thermal_expansion_surface_anfang_pct ) / 100 * ( 1 - Pressure_adjustment_surface_pct / 100 ) * UNIT_conversion_Gm3_to_km3
        idxlhs = fcol_in_mdf['Volume_expansion_from_thermal_expansion_surface_Gm3_is_km3']
        idx1 = fcol_in_mdf['Thermal_expansion_surface_pct']
        idx2 = fcol_in_mdf['Thermal_expansion_surface_anfang_pct']
        mdf[rowi, idxlhs] =  Surface_ocean_warm_volume  *  ( mdf[rowi, idx1] - mdf[rowi, idx2] )  /  100  *  (  1  -  Pressure_adjustment_surface_pct  /  100  )  *  UNIT_conversion_Gm3_to_km3 
    
    # Sea_level_change_from_thermal_expansion_surface_m = Volume_expansion_from_thermal_expansion_surface_Gm3_is_km3 / Ocean_surface_area_km2 * UNIT_Conversion_from_km3_to_km2
        idxlhs = fcol_in_mdf['Sea_level_change_from_thermal_expansion_surface_m']
        idx1 = fcol_in_mdf['Volume_expansion_from_thermal_expansion_surface_Gm3_is_km3']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Ocean_surface_area_km2  *  UNIT_Conversion_from_km3_to_km2 
    
    # Temp_ocean_deep_in_K = Heat_in_deep_ZJ * Conversion_constant_heat_ocean_deep_to_temp
        idxlhs = fcol_in_mdf['Temp_ocean_deep_in_K']
        idx1 = fcol_in_mdf['Heat_in_deep_ZJ']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Conversion_constant_heat_ocean_deep_to_temp 
    
    # Temp_ocean_deep_in_C = Temp_ocean_deep_in_K - 273.15
        idxlhs = fcol_in_mdf['Temp_ocean_deep_in_C']
        idx1 = fcol_in_mdf['Temp_ocean_deep_in_K']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] -  273.15 
    
    # Thermal_expansion_deep_pct = WITH LOOKUP ( Temp_ocean_deep_in_C , ( [ ( 0 , 0 ) - ( 20 , 0.2 ) ] , ( 0 , 0.015 ) , ( 1 , 0.008 ) , ( 2 , 0.0033 ) , ( 3 , 0.001 ) , ( 4 , 0 ) , ( 5 , 0.0012 ) , ( 6 , 0.0033 ) , ( 7 , 0.008 ) , ( 8 , 0.013 ) , ( 9 , 0.021 ) , ( 10 , 0.0287 ) , ( 20 , 0.1963 ) ) )
        tabidx = ftab_in_d_table['Thermal_expansion_deep_pct'] # fetch the correct table
        idxlhs = fcol_in_mdf['Thermal_expansion_deep_pct'] # get the location of the lhs in mdf
        idx1 = fcol_in_mdf['Temp_ocean_deep_in_C']
        look = d_table[tabidx]
        valgt = GRAPH(mdf[rowi,  idx1], look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # Thermal_expansion_deep_anfang_pct = WITH LOOKUP ( Temp_ocean_deep_in_1850_C , ( [ ( 0 , 0 ) - ( 20 , 0.2 ) ] , ( 0 , 0.015 ) , ( 1 , 0.008 ) , ( 2 , 0.0033 ) , ( 3 , 0.001 ) , ( 4 , 0 ) , ( 5 , 0.0012 ) , ( 6 , 0.0033 ) , ( 7 , 0.008 ) , ( 8 , 0.013 ) , ( 9 , 0.021 ) , ( 10 , 0.0287 ) , ( 20 , 0.1963 ) ) )
        tabidx = ftab_in_d_table['Thermal_expansion_deep_anfang_pct'] # fetch the correct table
        idxlhs = fcol_in_mdf['Thermal_expansion_deep_anfang_pct'] # get the location of the lhs in mdf
        look = d_table[tabidx]
        valgt = GRAPH( Temp_ocean_deep_in_1850_C , look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # Volume_expansion_from_thermal_expansion_deep_Gm3_is_km3 = Deep_ocean_cold_volume * ( Thermal_expansion_deep_pct - Thermal_expansion_deep_anfang_pct ) / 100 * ( 1 - Pressure_adjustment_deep_pct / 100 ) * UNIT_conversion_Gm3_to_km3
        idxlhs = fcol_in_mdf['Volume_expansion_from_thermal_expansion_deep_Gm3_is_km3']
        idx1 = fcol_in_mdf['Thermal_expansion_deep_pct']
        idx2 = fcol_in_mdf['Thermal_expansion_deep_anfang_pct']
        mdf[rowi, idxlhs] =  Deep_ocean_cold_volume  *  ( mdf[rowi, idx1] - mdf[rowi, idx2] )  /  100  *  (  1  -  Pressure_adjustment_deep_pct  /  100  )  *  UNIT_conversion_Gm3_to_km3 
    
    # Sea_level_change_from_thermal_expansion_deep_m = Volume_expansion_from_thermal_expansion_deep_Gm3_is_km3 / Ocean_surface_area_km2 * UNIT_Conversion_from_km3_to_km2
        idxlhs = fcol_in_mdf['Sea_level_change_from_thermal_expansion_deep_m']
        idx1 = fcol_in_mdf['Volume_expansion_from_thermal_expansion_deep_Gm3_is_km3']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Ocean_surface_area_km2  *  UNIT_Conversion_from_km3_to_km2 
    
    # Total_sea_level_change_from_thermal_expansion_m = ( Sea_level_change_from_thermal_expansion_surface_m + Sea_level_change_from_thermal_expansion_deep_m ) * UNIT_conversion_from_km_to_m
        idxlhs = fcol_in_mdf['Total_sea_level_change_from_thermal_expansion_m']
        idx1 = fcol_in_mdf['Sea_level_change_from_thermal_expansion_surface_m']
        idx2 = fcol_in_mdf['Sea_level_change_from_thermal_expansion_deep_m']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] + mdf[rowi, idx2] )  *  UNIT_conversion_from_km_to_m 
    
    # Sea_level_rise_from_melting_ice_m = Cumulative_ocean_volume_increase_due_to_ice_melting_km3 / Ocean_surface_area_km2 * UNIT_Conversion_from_km3_to_km2 * UNIT_conversion_from_km_to_m * Avg_flatness_of_worlds_coastline
        idxlhs = fcol_in_mdf['Sea_level_rise_from_melting_ice_m']
        idx1 = fcol_in_mdf['Cumulative_ocean_volume_increase_due_to_ice_melting_km3']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Ocean_surface_area_km2  *  UNIT_Conversion_from_km3_to_km2  *  UNIT_conversion_from_km_to_m  *  Avg_flatness_of_worlds_coastline 
    
    # Sea_level_change_from_melting_ice_and_thermal_expansion_m = Total_sea_level_change_from_thermal_expansion_m + Sea_level_rise_from_melting_ice_m
        idxlhs = fcol_in_mdf['Sea_level_change_from_melting_ice_and_thermal_expansion_m']
        idx1 = fcol_in_mdf['Total_sea_level_change_from_thermal_expansion_m']
        idx2 = fcol_in_mdf['Sea_level_rise_from_melting_ice_m']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2]
    
    # sea_level_rise_ratio_wrt_2020 = IF_THEN_ELSE ( zeit < 2020 , 1 , Sea_level_change_from_melting_ice_and_thermal_expansion_m / sea_level_rise_2020 )
        idxlhs = fcol_in_mdf['sea_level_rise_ratio_wrt_2020']
        idx1 = fcol_in_mdf['Sea_level_change_from_melting_ice_and_thermal_expansion_m']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  (  zeit  <  2020  ,  1  , mdf[rowi, idx1] /  sea_level_rise_2020  ) 
    
    # temp_ratio_wrt_2020 = IF_THEN_ELSE ( zeit < 2020 , 1 , Temp_surface_anomaly_compared_to_anfang_degC / temp_in_2020 )
        idxlhs = fcol_in_mdf['temp_ratio_wrt_2020']
        idx1 = fcol_in_mdf['Temp_surface_anomaly_compared_to_anfang_degC']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  (  zeit  <  2020  ,  1  , mdf[rowi, idx1] /  temp_in_2020  ) 
    
    # Combined_env_damage_indicator = ( sea_level_rise_ratio_wrt_2020 + temp_ratio_wrt_2020 ) / 2 - 1
        idxlhs = fcol_in_mdf['Combined_env_damage_indicator']
        idx1 = fcol_in_mdf['sea_level_rise_ratio_wrt_2020']
        idx2 = fcol_in_mdf['temp_ratio_wrt_2020']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] + mdf[rowi, idx2] )  /  2  -  1 
     
    # GDPpp_of_the_richest_region = VMAX ( GDPpp_USED[region!] )
        idxlhs = fcol_in_mdf['GDPpp_of_the_richest_region']
        idx1 = fcol_in_mdf['GDPpp_USED']
        vmax = mdf[rowi, idx1 + 0]
        for j in range(1,10):
            if mdf[rowi, idx1 + j] > vmax:
                vmax = mdf[rowi, idx1 + j]
        mdf[rowi, idxlhs] = vmax 
    
    # Ratio_of_regional_GDPpp_to_richest_region_GDPpp[region] = GDPpp_USED[region] / GDPpp_of_the_richest_region
        idxlhs = fcol_in_mdf['Ratio_of_regional_GDPpp_to_richest_region_GDPpp']
        idx1 = fcol_in_mdf['GDPpp_USED']
        idx2 = fcol_in_mdf['GDPpp_of_the_richest_region']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2]
    
    # Indicated_eff_of_relative_wealth_on_env_damage[region] = IF_THEN_ELSE ( zeit > 2020 , 1 + SoE_of_relative_wealth_on_env_damage * ( Ratio_of_regional_GDPpp_to_richest_region_GDPpp - 1 ) , 1 )
        idxlhs = fcol_in_mdf['Indicated_eff_of_relative_wealth_on_env_damage']
        idx1 = fcol_in_mdf['Ratio_of_regional_GDPpp_to_richest_region_GDPpp']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >  2020  ,  1  +  SoE_of_relative_wealth_on_env_damage  *  ( mdf[rowi , idx1:idx1 + 10] -  1  )  ,  1  ) 
    
    # Actual_eff_of_relative_wealth_on_env_damage[region] = SMOOTH3 ( Indicated_eff_of_relative_wealth_on_env_damage[region] , Time_for_shifts_in_relative_wealth_to_affect_env_damage_response )
        idxin = fcol_in_mdf['Indicated_eff_of_relative_wealth_on_env_damage' ]
        idx2 = fcol_in_mdf['Actual_eff_of_relative_wealth_on_env_damage_2']
        idx1 = fcol_in_mdf['Actual_eff_of_relative_wealth_on_env_damage_1']
        idxout = fcol_in_mdf['Actual_eff_of_relative_wealth_on_env_damage']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( Time_for_shifts_in_relative_wealth_to_affect_env_damage_response / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( Time_for_shifts_in_relative_wealth_to_affect_env_damage_response / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( Time_for_shifts_in_relative_wealth_to_affect_env_damage_response / 3) * dt
    
    # Eff_of_env_damage_on_agri_yield[region] = np.exp ( Combined_env_damage_indicator * expSoE_of_ed_on_agri_yield ) / Actual_eff_of_relative_wealth_on_env_damage[region]
        idxlhs = fcol_in_mdf['Eff_of_env_damage_on_agri_yield']
        idx1 = fcol_in_mdf['Combined_env_damage_indicator']
        idx2 = fcol_in_mdf['Actual_eff_of_relative_wealth_on_env_damage']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.exp  ( mdf[rowi , idx1] *  expSoE_of_ed_on_agri_yield  )  / mdf[rowi , idx2:idx2 + 10]
    
    # Crop_yield_with_soil_quality_CO2_and_env_dam_effects[region] = Smoothed_Crop_yield_from_N_use[region] * Soil_quality[region] * Eff_of_CO2_on_yield / Eff_of_env_damage_on_agri_yield[region]
        idxlhs = fcol_in_mdf['Crop_yield_with_soil_quality_CO2_and_env_dam_effects']
        idx1 = fcol_in_mdf['Smoothed_Crop_yield_from_N_use']
        idx2 = fcol_in_mdf['Soil_quality']
        idx3 = fcol_in_mdf['Eff_of_CO2_on_yield']
        idx4 = fcol_in_mdf['Eff_of_env_damage_on_agri_yield']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] * mdf[rowi , idx3] / mdf[rowi , idx4:idx4 + 10]
    
    # Crop_grown_regionally[region] = Cropland[region] * Crop_yield_with_soil_quality_CO2_and_env_dam_effects[region]
        idxlhs = fcol_in_mdf['Crop_grown_regionally']
        idx1 = fcol_in_mdf['Cropland']
        idx2 = fcol_in_mdf['Crop_yield_with_soil_quality_CO2_and_env_dam_effects']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # Ratio_of_demand_to_regional_supply_of_crops[region] = All_crop_regional_dmd[region] / Crop_grown_regionally[region]
        idxlhs = fcol_in_mdf['Ratio_of_demand_to_regional_supply_of_crops']
        idx1 = fcol_in_mdf['All_crop_regional_dmd']
        idx2 = fcol_in_mdf['Crop_grown_regionally']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # Desired_cropland[region] = Cropland[region] * ( 1 + Ratio_of_demand_to_regional_supply_of_crops[region] * Fraction_of_supply_imbalance_to_be_closed_by_land[region] )
        idxlhs = fcol_in_mdf['Desired_cropland']
        idx1 = fcol_in_mdf['Cropland']
        idx2 = fcol_in_mdf['Ratio_of_demand_to_regional_supply_of_crops']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  1  + mdf[rowi , idx2:idx2 + 10] *  Fraction_of_supply_imbalance_to_be_closed_by_land[0:10]  ) 
    
    # Cropland_gap[region] = Desired_cropland[region] - Cropland[region]
        idxlhs = fcol_in_mdf['Cropland_gap']
        idx1 = fcol_in_mdf['Desired_cropland']
        idx2 = fcol_in_mdf['Cropland']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10]
    
    # acgl_to_c[region] = MIN ( Abandoned_crop_and_grazing_land[region] , MAX ( 0 , Cropland_gap[region] ) ) * Fraction_of_cropland_gap_closed_from_acgl[region]
        idxlhs = fcol_in_mdf['acgl_to_c']
        idx1 = fcol_in_mdf['Abandoned_crop_and_grazing_land']
        idx2 = fcol_in_mdf['Cropland_gap']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.minimum  ( mdf[rowi , idx1:idx1 + 10] ,  np.maximum  (  0  , mdf[rowi , idx2:idx2 + 10] )  )  *  Fraction_of_cropland_gap_closed_from_acgl[0:10] 
    
    # acgl_to_fa[region] = Abandoned_crop_and_grazing_land[region] / Time_for_abandoned_agri_land_to_become_forest
        idxlhs = fcol_in_mdf['acgl_to_fa']
        idx1 = fcol_in_mdf['Abandoned_crop_and_grazing_land']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Time_for_abandoned_agri_land_to_become_forest 
    
    # Grazing_land_EC = Grazing_land_EC_a * ( Meat_production[ec] * UNIT_conv_meat_to_dmnl ) ^ Grazing_land_EC_b
        idxlhs = fcol_in_mdf['Grazing_land_EC']
        idx1 = fcol_in_mdf['Meat_production']
        mdf[rowi, idxlhs] =  Grazing_land_EC_a  *  ( mdf[rowi, idx1 + 7] *  UNIT_conv_meat_to_dmnl  )  **  Grazing_land_EC_b 
    
    # Grazing_land_LA = ( Grazing_land_LA_L / ( 1 + np.exp ( - Grazing_land_LA_k * ( Meat_production[la] * UNIT_conv_meat_to_dmnl - Grazing_land_LA_x ) ) ) ) - ( Grazing_land_LA_L2 / ( 1 + np.exp ( - Grazing_land_LA_k2 * ( Meat_production[la] * UNIT_conv_meat_to_dmnl - Grazing_land_LA_x2 ) ) ) )
        idxlhs = fcol_in_mdf['Grazing_land_LA']
        idx1 = fcol_in_mdf['Meat_production']
        idx2 = fcol_in_mdf['Meat_production']
        mdf[rowi, idxlhs] =  (  Grazing_land_LA_L  /  (  1  +  np.exp  (  -  Grazing_land_LA_k  *  ( mdf[rowi, idx1 + 5] *  UNIT_conv_meat_to_dmnl  -  Grazing_land_LA_x  )  )  )  )  -  (  Grazing_land_LA_L2  /  (  1  +  np.exp  (  -  Grazing_land_LA_k2  *  ( mdf[rowi, idx2 + 5] *  UNIT_conv_meat_to_dmnl  -  Grazing_land_LA_x2  )  )  )  ) 
    
    # Grazing_land_ME = Grazing_land_ME_L / ( 1 + np.exp ( - Grazing_land_ME_k * ( Meat_production[me] * UNIT_conv_meat_to_dmnl - Grazing_land_ME_x ) ) ) + Grazing_land_ME_min
        idxlhs = fcol_in_mdf['Grazing_land_ME']
        idx1 = fcol_in_mdf['Meat_production']
        mdf[rowi, idxlhs] =  Grazing_land_ME_L  /  (  1  +  np.exp  (  -  Grazing_land_ME_k  *  ( mdf[rowi, idx1 + 3] *  UNIT_conv_meat_to_dmnl  -  Grazing_land_ME_x  )  )  )  +  Grazing_land_ME_min 
    
    # Grazing_land_PA = Grazing_land_PA_L / ( 1 + np.exp ( - Grazing_land_PA_k * ( Meat_production[pa] * UNIT_conv_meat_to_dmnl - Grazing_land_PA_x ) ) ) + Grazing_land_PA_min
        idxlhs = fcol_in_mdf['Grazing_land_PA']
        idx1 = fcol_in_mdf['Meat_production']
        mdf[rowi, idxlhs] =  Grazing_land_PA_L  /  (  1  +  np.exp  (  -  Grazing_land_PA_k  *  ( mdf[rowi, idx1 + 6] *  UNIT_conv_meat_to_dmnl  -  Grazing_land_PA_x  )  )  )  +  Grazing_land_PA_min 
    
    # Grazing_land_SA = Grazing_land_SA_a * ( Meat_production[sa] * UNIT_conv_meat_to_dmnl ) ^ Grazing_land_SA_b
        idxlhs = fcol_in_mdf['Grazing_land_SA']
        idx1 = fcol_in_mdf['Meat_production']
        mdf[rowi, idxlhs] =  Grazing_land_SA_a  *  ( mdf[rowi, idx1 + 4] *  UNIT_conv_meat_to_dmnl  )  **  Grazing_land_SA_b 
    
    # Grazing_land_SE = Grazing_land_SE_a * LN ( Meat_production[se] * UNIT_conv_meat_to_dmnl ) + Grazing_land_SE_b
        idxlhs = fcol_in_mdf['Grazing_land_SE']
        idx1 = fcol_in_mdf['Meat_production']
        mdf[rowi, idxlhs] =  Grazing_land_SE_a  *  np.log  ( mdf[rowi, idx1 + 9] *  UNIT_conv_meat_to_dmnl  )  +  Grazing_land_SE_b 
    
    # Grazing_land_Rest[region] = Grazing_land_Rest_L[region] / ( 1 + np.exp ( - Grazing_land_Rest_k[region] * ( Meat_production[region] * UNIT_conv_meat_to_dmnl - Grazing_land_Rest_x[region] ) ) )
        idxlhs = fcol_in_mdf['Grazing_land_Rest']
        idx1 = fcol_in_mdf['Meat_production']
        mdf[rowi, idxlhs:idxlhs + 10] =  Grazing_land_Rest_L[0:10]  /  (  1  +  np.exp  (  -  Grazing_land_Rest_k[0:10]  *  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_meat_to_dmnl  -  Grazing_land_Rest_x[0:10]  )  )  ) 
    
    # Desired_grazing_land = IF_THEN_ELSE ( j==7 , Grazing_land_EC , IF_THEN_ELSE ( j==5 , Grazing_land_LA , IF_THEN_ELSE ( j==3 , Grazing_land_ME , IF_THEN_ELSE ( j==6 , Grazing_land_PA , IF_THEN_ELSE ( j==4 , Grazing_land_SA , IF_THEN_ELSE ( j==9 , Grazing_land_SE , Grazing_land_Rest ) ) ) ) ) )
        idxlhs = fcol_in_mdf['Desired_grazing_land']
        idx1 = fcol_in_mdf['Grazing_land_EC']
        idx2 = fcol_in_mdf['Grazing_land_LA']
        idx3 = fcol_in_mdf['Grazing_land_ME']
        idx4 = fcol_in_mdf['Grazing_land_PA']
        idx5 = fcol_in_mdf['Grazing_land_SA']
        idx6 = fcol_in_mdf['Grazing_land_SE']
        idx7 = fcol_in_mdf['Grazing_land_Rest']
        for j in range(0,10):
            mdf[rowi, idxlhs + j] =  IF_THEN_ELSE  (  j==7  , mdf[rowi , idx1] ,  IF_THEN_ELSE  (  j==5  , mdf[rowi , idx2] ,  IF_THEN_ELSE  (  j==3  , mdf[rowi , idx3] ,  IF_THEN_ELSE  (  j==6  , mdf[rowi , idx4] ,  IF_THEN_ELSE  (  j==4  , mdf[rowi , idx5] ,  IF_THEN_ELSE  (  j==9  , mdf[rowi , idx6] , mdf[rowi , idx7 + j] )  )  )  )  )  ) 
    
    # Graing_land_desired_for_all_meat[region] = Desired_grazing_land[region] * UNIT_conv_to_Mha
        idxlhs = fcol_in_mdf['Graing_land_desired_for_all_meat']
        idx1 = fcol_in_mdf['Desired_grazing_land']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_Mha 
    
    # Grazing_land_need[region] = Graing_land_desired_for_all_meat[region]
        idxlhs = fcol_in_mdf['Grazing_land_need']
        idx1 = fcol_in_mdf['Graing_land_desired_for_all_meat']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10]
    
    # Grazing_land_gap[region] = Grazing_land_need[region] - Grazing_land[region]
        idxlhs = fcol_in_mdf['Grazing_land_gap']
        idx1 = fcol_in_mdf['Grazing_land_need']
        idx2 = fcol_in_mdf['Grazing_land']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10]
    
    # acgl_to_gl[region] = MIN ( Abandoned_crop_and_grazing_land[region] , MAX ( 0 , Grazing_land_gap[region] ) ) * Fraction_of_grazing_land_gap_closed_from_acgl
        idxlhs = fcol_in_mdf['acgl_to_gl']
        idx1 = fcol_in_mdf['Abandoned_crop_and_grazing_land']
        idx2 = fcol_in_mdf['Grazing_land_gap']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.minimum  ( mdf[rowi , idx1:idx1 + 10] ,  np.maximum  (  0  , mdf[rowi , idx2:idx2 + 10] )  )  *  Fraction_of_grazing_land_gap_closed_from_acgl 
    
    # Populated_land_need[region] = Population[region] * Urban_land_per_population[region]
        idxlhs = fcol_in_mdf['Populated_land_need']
        idx1 = fcol_in_mdf['Population']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  Urban_land_per_population[0:10] 
    
    # Populated_land_gap[region] = Populated_land_need[region] - Populated_land[region]
        idxlhs = fcol_in_mdf['Populated_land_gap']
        idx1 = fcol_in_mdf['Populated_land_need']
        idx2 = fcol_in_mdf['Populated_land']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10]
    
    # acgl_to_pl[region] = MIN ( Abandoned_crop_and_grazing_land[region] , MAX ( 0 , Populated_land_gap[region] ) ) * Fraction_of_abandoned_agri_land_developed_for_urban_land
        idxlhs = fcol_in_mdf['acgl_to_pl']
        idx1 = fcol_in_mdf['Abandoned_crop_and_grazing_land']
        idx2 = fcol_in_mdf['Populated_land_gap']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.minimum  ( mdf[rowi , idx1:idx1 + 10] ,  np.maximum  (  0  , mdf[rowi , idx2:idx2 + 10] )  )  *  Fraction_of_abandoned_agri_land_developed_for_urban_land 
    
    # Carbon_concentration_in_warm_surface = C_in_warm_surface_water_GtC / ( Warm_surface_water_volume + Cumulative_ocean_volume_increase_due_to_ice_melting_km3 * UNIT_conversion_km3_to_Gm3 * Frac_vol_warm_ocean_0_to_100m_of_total )
        idxlhs = fcol_in_mdf['Carbon_concentration_in_warm_surface']
        idx1 = fcol_in_mdf['C_in_warm_surface_water_GtC']
        idx2 = fcol_in_mdf['Cumulative_ocean_volume_increase_due_to_ice_melting_km3']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  (  Warm_surface_water_volume  + mdf[rowi, idx2] *  UNIT_conversion_km3_to_Gm3  *  Frac_vol_warm_ocean_0_to_100m_of_total  ) 
    
    # CC_in_warm_surface_ymoles_per_litre = Carbon_concentration_in_warm_surface * UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre
        idxlhs = fcol_in_mdf['CC_in_warm_surface_ymoles_per_litre']
        idx1 = fcol_in_mdf['Carbon_concentration_in_warm_surface']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre 
    
    # CC_in_warm_surface_ymoles_per_litre_dmnl = CC_in_warm_surface_ymoles_per_litre * UNIT_conversion_ymoles_p_litre_to_dless
        idxlhs = fcol_in_mdf['CC_in_warm_surface_ymoles_per_litre_dmnl']
        idx1 = fcol_in_mdf['CC_in_warm_surface_ymoles_per_litre']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  UNIT_conversion_ymoles_p_litre_to_dless 
    
    # pH_in_warm_surface_water = UNIT_conversion_C_to_pH * ( 1 - 0.0017 * Temp_surface - 0.0003 ) * ( 163.2 * CC_in_warm_surface_ymoles_per_litre_dmnl ** ( - 0.385 ) )
        idxlhs = fcol_in_mdf['pH_in_warm_surface_water']
        idx1 = fcol_in_mdf['Temp_surface']
        idx2 = fcol_in_mdf['CC_in_warm_surface_ymoles_per_litre_dmnl']
        mdf[rowi, idxlhs] =  UNIT_conversion_C_to_pH  *  (  1  -  0.0017  * mdf[rowi, idx1] -  0.0003  )  *  (  163.2  * mdf[rowi, idx2] **  (  -  0.385  )  ) 
    
    # Temp_of_cold_surface_water = Temp_surface / 3
        idxlhs = fcol_in_mdf['Temp_of_cold_surface_water']
        idx1 = fcol_in_mdf['Temp_surface']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  3 
    
    # Carbon_concentration_in_cold_surface_ocean = C_in_cold_surface_water_GtC / ( Cold_surface_water_volume + Cumulative_ocean_volume_increase_due_to_ice_melting_km3 * UNIT_conversion_km3_to_Gm3 * Frac_vol_cold_ocean_0_to_100m_of_total )
        idxlhs = fcol_in_mdf['Carbon_concentration_in_cold_surface_ocean']
        idx1 = fcol_in_mdf['C_in_cold_surface_water_GtC']
        idx2 = fcol_in_mdf['Cumulative_ocean_volume_increase_due_to_ice_melting_km3']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  (  Cold_surface_water_volume  + mdf[rowi, idx2] *  UNIT_conversion_km3_to_Gm3  *  Frac_vol_cold_ocean_0_to_100m_of_total  ) 
    
    # CC_in_cold_surface_ymoles_per_litre = Carbon_concentration_in_cold_surface_ocean * UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre
        idxlhs = fcol_in_mdf['CC_in_cold_surface_ymoles_per_litre']
        idx1 = fcol_in_mdf['Carbon_concentration_in_cold_surface_ocean']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre 
    
    # CC_in_cold_surface_ymoles_per_litre_dmnl = CC_in_cold_surface_ymoles_per_litre * UNIT_conversion_ymoles_p_litre_to_dless
        idxlhs = fcol_in_mdf['CC_in_cold_surface_ymoles_per_litre_dmnl']
        idx1 = fcol_in_mdf['CC_in_cold_surface_ymoles_per_litre']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  UNIT_conversion_ymoles_p_litre_to_dless 
    
    # pH_in_cold_suface_water = UNIT_conversion_C_to_pH * ( 1 - 0.0017 * Temp_of_cold_surface_water - 0.0003 ) * ( 163.2 * CC_in_cold_surface_ymoles_per_litre_dmnl ^ ( - 0.385 ) )
        idxlhs = fcol_in_mdf['pH_in_cold_suface_water']
        idx1 = fcol_in_mdf['Temp_of_cold_surface_water']
        idx2 = fcol_in_mdf['CC_in_cold_surface_ymoles_per_litre_dmnl']
        mdf[rowi, idxlhs] =  UNIT_conversion_C_to_pH  *  (  1  -  0.0017  * mdf[rowi, idx1] -  0.0003  )  *  (  163.2  * mdf[rowi, idx2] **  (  -  0.385  )  ) 
    
    # pH_in_surface = pH_in_warm_surface_water * Volume_warm_ocean_0_to_100m / ( Volume_warm_ocean_0_to_100m + Volume_cold_ocean_0_to_100m ) + pH_in_cold_suface_water * Volume_cold_ocean_0_to_100m / ( Volume_warm_ocean_0_to_100m + Volume_cold_ocean_0_to_100m )
        idxlhs = fcol_in_mdf['pH_in_surface']
        idx1 = fcol_in_mdf['pH_in_warm_surface_water']
        idx2 = fcol_in_mdf['pH_in_cold_suface_water']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Volume_warm_ocean_0_to_100m  /  (  Volume_warm_ocean_0_to_100m  +  Volume_cold_ocean_0_to_100m  )  + mdf[rowi, idx2] *  Volume_cold_ocean_0_to_100m  /  (  Volume_warm_ocean_0_to_100m  +  Volume_cold_ocean_0_to_100m  ) 
    
    # pb_Ocean_acidification = pH_in_surface
        idxlhs = fcol_in_mdf['pb_Ocean_acidification']
        idx1 = fcol_in_mdf['pH_in_surface']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # Acidification_risk_score = IF_THEN_ELSE ( pb_Ocean_acidification_green_threshold > pb_Ocean_acidification , 1 , 0 )
        idxlhs = fcol_in_mdf['Acidification_risk_score']
        idx1 = fcol_in_mdf['pb_Ocean_acidification']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  (  pb_Ocean_acidification_green_threshold  > mdf[rowi, idx1] ,  1  ,  0  ) 
    
    # DAC_CCS_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , DAC_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , DAC_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , DAC_R1_via_Excel , DAC_policy_Min ) ) )
        idxlhs = fcol_in_mdf['DAC_CCS_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  DAC_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  DAC_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  DAC_R1_via_Excel[0:10]  ,  DAC_policy_Min  )  )  ) 
    
    # DAC_policy_with_RW[region] = DAC_CCS_rounds_via_Excel[region] * Smoothed_Reform_willingness[region] / Inequality_effect_on_energy_TA[region]
        idxlhs = fcol_in_mdf['DAC_policy_with_RW']
        idx1 = fcol_in_mdf['DAC_CCS_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        idx3 = fcol_in_mdf['Inequality_effect_on_energy_TA']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] / mdf[rowi , idx3:idx3 + 10]
     
    # DAC_pol_div_100[region] = MIN ( DAC_policy_Max , MAX ( DAC_policy_Min , DAC_policy_with_RW[region] ) ) / 1
        idxlhs = fcol_in_mdf['DAC_pol_div_100']
        idx1 = fcol_in_mdf['DAC_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], DAC_policy_Min, DAC_policy_Max) / 1
    
    # DAC_policy[region] = SMOOTH3 ( DAC_pol_div_100[region] , DAC_Time_to_implement_goal )
        idxin = fcol_in_mdf['DAC_pol_div_100' ]
        idx2 = fcol_in_mdf['DAC_policy_2']
        idx1 = fcol_in_mdf['DAC_policy_1']
        idxout = fcol_in_mdf['DAC_policy']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( DAC_Time_to_implement_goal / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( DAC_Time_to_implement_goal / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( DAC_Time_to_implement_goal / 3) * dt
    
    # Actual_CO2_taken_directly_out_of_the_atmosphere_ie_direct_air_capture[region] = DAC_policy[region] * UNIT_conv_to_GtCO2_pr_yr
        idxlhs = fcol_in_mdf['Actual_CO2_taken_directly_out_of_the_atmosphere_ie_direct_air_capture']
        idx1 = fcol_in_mdf['DAC_policy']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_GtCO2_pr_yr 
    
    # Nuclear_gen_cap_EU = ( Nuclear_gen_cap_EU_s + Nuclear_gen_cap_EU_g * np.exp ( - ( ( ( ( GDPpp_USED[eu] * UNIT_conv_to_make_exp_dmnl ) - Nuclear_gen_cap_EU_h ) ^ 2 ) / ( 2 * Nuclear_gen_cap_EU_k ^ 2 ) ) ) ) * UNIT_conv_to_GW
        idxlhs = fcol_in_mdf['Nuclear_gen_cap_EU']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs] =  (  Nuclear_gen_cap_EU_s  +  Nuclear_gen_cap_EU_g  *  np.exp  (  -  (  (  (  ( mdf[rowi, idx1 + 8] *  UNIT_conv_to_make_exp_dmnl  )  -  Nuclear_gen_cap_EU_h  )  **  2  )  /  (  2  *  Nuclear_gen_cap_EU_k  **  2  )  )  )  )  *  UNIT_conv_to_GW 
    
    # Nuclear_gen_cap_WO_EU[region] = Nuclear_gen_cap_WO_EU_L[region] / ( 1 + np.exp ( - Nuclear_gen_cap_WO_EU_k[region] * ( ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl ) - Nuclear_gen_cap_WO_EU_x0[region] ) ) )
        idxlhs = fcol_in_mdf['Nuclear_gen_cap_WO_EU']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  Nuclear_gen_cap_WO_EU_L[0:10]  /  (  1  +  np.exp  (  -  Nuclear_gen_cap_WO_EU_k[0:10]  *  (  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  )  -  Nuclear_gen_cap_WO_EU_x0[0:10]  )  )  ) 
    
    # Nuclear_gen_cap = IF_THEN_ELSE ( j==8 , Nuclear_gen_cap_EU , Nuclear_gen_cap_WO_EU )
        idxlhs = fcol_in_mdf['Nuclear_gen_cap']
        idx1 = fcol_in_mdf['Nuclear_gen_cap_EU']
        idx2 = fcol_in_mdf['Nuclear_gen_cap_WO_EU']
        for j in range(0,10):
            mdf[rowi, idxlhs + j] =  IF_THEN_ELSE  (  j==8  , mdf[rowi , idx1] , mdf[rowi , idx2 + j] ) 
    
    # Nuclear_gen_cap_after_depreciation[region] = Nuclear_gen_cap[region] * Nuclear_net_depreciation_multiplier_on_gen_cap
        idxlhs = fcol_in_mdf['Nuclear_gen_cap_after_depreciation']
        idx1 = fcol_in_mdf['Nuclear_gen_cap']
        idx2 = fcol_in_mdf['Nuclear_net_depreciation_multiplier_on_gen_cap']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2]
    
    # El_from_nuclear[region] = Nuclear_gen_cap_after_depreciation[region] * Nuclear_capacity_factor * Hours_per_year * UNIT_conv_GWh_and_TWh
        idxlhs = fcol_in_mdf['El_from_nuclear']
        idx1 = fcol_in_mdf['Nuclear_gen_cap_after_depreciation']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  Nuclear_capacity_factor  *  Hours_per_year  *  UNIT_conv_GWh_and_TWh 
    
    # wind_PV_nuclear_hydro_el_generation[region] = El_from_wind_and_PV[region] + El_from_nuclear[region] + El_from_Hydro[region]
        idxlhs = fcol_in_mdf['wind_PV_nuclear_hydro_el_generation']
        idx1 = fcol_in_mdf['El_from_wind_and_PV']
        idx2 = fcol_in_mdf['El_from_nuclear']
        idx3 = fcol_in_mdf['El_from_Hydro']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10]
    
    # El_from_all_sources[region] = El_gen_from_fossil_fuels[region] + wind_PV_nuclear_hydro_el_generation[region]
        idxlhs = fcol_in_mdf['El_from_all_sources']
        idx1 = fcol_in_mdf['El_gen_from_fossil_fuels']
        idx2 = fcol_in_mdf['wind_PV_nuclear_hydro_el_generation']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10]
    
    # Actual_el_use_pp[region] = El_from_all_sources[region] / Population[region] * UNIT_conv_to_kWh_ppp
        idxlhs = fcol_in_mdf['Actual_el_use_pp']
        idx1 = fcol_in_mdf['El_from_all_sources']
        idx2 = fcol_in_mdf['Population']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10] *  UNIT_conv_to_kWh_ppp 
    
    # Actual_inequality_index_higher_is_more_unequal_N_years_ago[region] = SMOOTH3I ( Actual_inequality_index_higher_is_more_unequal[region] , N_number_of_years_ago , Inequality_considered_normal_in_1980[region] )
        idxlhs = fcol_in_mdf['Actual_inequality_index_higher_is_more_unequal_N_years_ago']
        idxin = fcol_in_mdf['Actual_inequality_index_higher_is_more_unequal']
        idx2 = fcol_in_mdf['Actual_inequality_index_higher_is_more_unequal_N_years_ago_2']
        idx1 = fcol_in_mdf['Actual_inequality_index_higher_is_more_unequal_N_years_ago_1']
        idxout = fcol_in_mdf['Actual_inequality_index_higher_is_more_unequal_N_years_ago']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( N_number_of_years_ago / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( N_number_of_years_ago / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( N_number_of_years_ago / 3) * dt
    
    # GRASS_with_normal_cover_Mkm2 = GRASS_potential_area_Mkm2 - GRASS_area_burnt_Mkm2 - GRASS_deforested_Mkm2 - GRASS_area_harvested_Mkm2
        idxlhs = fcol_in_mdf['GRASS_with_normal_cover_Mkm2']
        idx1 = fcol_in_mdf['GRASS_potential_area_Mkm2']
        idx2 = fcol_in_mdf['GRASS_area_burnt_Mkm2']
        idx3 = fcol_in_mdf['GRASS_deforested_Mkm2']
        idx4 = fcol_in_mdf['GRASS_area_harvested_Mkm2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] - mdf[rowi, idx2] - mdf[rowi, idx3] - mdf[rowi, idx4]
    
    # GRASS_being_deforested_Mkm2_py = GRASS_with_normal_cover_Mkm2 * Fraction_GRASS_being_deforested_1_py
        idxlhs = fcol_in_mdf['GRASS_being_deforested_Mkm2_py']
        idx1 = fcol_in_mdf['GRASS_with_normal_cover_Mkm2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Fraction_GRASS_being_deforested_1_py 
    
    # GRASS_DeadB_and_SOM_tB_per_km2 = GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass / GRASS_with_normal_cover_Mkm2 * 1000
        idxlhs = fcol_in_mdf['GRASS_DeadB_and_SOM_tB_per_km2']
        idx1 = fcol_in_mdf['GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass']
        idx2 = fcol_in_mdf['GRASS_with_normal_cover_Mkm2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] / mdf[rowi, idx2] *  1000 
    
    # GRASS_DeadB_SOM_being_lost_due_to_deforestation = GRASS_being_deforested_Mkm2_py * GRASS_fraction_of_DeadB_and_SOM_being_destroyed_by_deforesting * GRASS_DeadB_and_SOM_tB_per_km2 / 1000
        idxlhs = fcol_in_mdf['GRASS_DeadB_SOM_being_lost_due_to_deforestation']
        idx1 = fcol_in_mdf['GRASS_being_deforested_Mkm2_py']
        idx2 = fcol_in_mdf['GRASS_DeadB_and_SOM_tB_per_km2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  GRASS_fraction_of_DeadB_and_SOM_being_destroyed_by_deforesting  * mdf[rowi, idx2] /  1000 
     
    # Global_population = SUM ( Population[region!] )
        idxlhs = fcol_in_mdf['Global_population']
        idx1 = fcol_in_mdf['Population']
        globsum = 0
        for j in range(0,10):
            globsum = globsum + mdf[rowi, idx1 + j]
        mdf[rowi, idxlhs] = globsum 
    
    # Global_population_in_Bp = Global_population / UNIT_conv_to_Bp
        idxlhs = fcol_in_mdf['Global_population_in_Bp']
        idx1 = fcol_in_mdf['Global_population']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  UNIT_conv_to_Bp 
    
    # Urbanzation_Effect_on_biomass_use = WITH LOOKUP ( zeit , ( [ ( 1850 , 0 ) - ( 2300 , 5 ) ] , ( 1850 , 5 ) , ( 1880 , 4.71 ) , ( 1900 , 4.4 ) , ( 1925 , 3.73 ) , ( 1945 , 3.11 ) , ( 1965 , 2.37 ) , ( 1975 , 1.93 ) , ( 1988 , 1.4 ) , ( 2000 , 1 ) , ( 2012 , 0.79 ) , ( 2028 , 0.59 ) , ( 2060 , 0.37 ) , ( 2100 , 0.25 ) , ( 2300 , 0 ) ) )
        tabidx = ftab_in_d_table['Urbanzation_Effect_on_biomass_use'] # fetch the correct table
        idxlhs = fcol_in_mdf['Urbanzation_Effect_on_biomass_use'] # get the location of the lhs in mdf
        look = d_table[tabidx]
        valgt = GRAPH( zeit, look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # Effect_of_population_and_urbanization_on_biomass_use = Global_population_in_Bp / Population_2000_bn * Urbanzation_Effect_on_biomass_use
        idxlhs = fcol_in_mdf['Effect_of_population_and_urbanization_on_biomass_use']
        idx1 = fcol_in_mdf['Global_population_in_Bp']
        idx2 = fcol_in_mdf['Urbanzation_Effect_on_biomass_use']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Population_2000_bn  * mdf[rowi, idx2]
    
    # Use_of_GRASS_biomass_for_energy = Use_of_GRASS_for_energy_in_2000_GtBiomass * Effect_of_population_and_urbanization_on_biomass_use * UNIT_conversion_1_py
        idxlhs = fcol_in_mdf['Use_of_GRASS_biomass_for_energy']
        idx1 = fcol_in_mdf['Effect_of_population_and_urbanization_on_biomass_use']
        mdf[rowi, idxlhs] =  Use_of_GRASS_for_energy_in_2000_GtBiomass  * mdf[rowi, idx1] *  UNIT_conversion_1_py 
    
    # Effect_of_CO2_on_new_biomass_growth = 1 + Sensitivity_of_biomass_new_growth_to_CO2_concentration * LN ( CO2_concentration_used_after_any_experiments_ppm / CO2_concentration_ppm_in_1850 )
        idxlhs = fcol_in_mdf['Effect_of_CO2_on_new_biomass_growth']
        idx1 = fcol_in_mdf['CO2_concentration_used_after_any_experiments_ppm']
        mdf[rowi, idxlhs] =  1  +  Sensitivity_of_biomass_new_growth_to_CO2_concentration  *  np.log  ( mdf[rowi, idx1] /  CO2_concentration_ppm_in_1850  ) 
    
    # Effect_of_temperature_on_new_biomass_growth_dmnl = ( 1 + Slope_of_temp_eff_on_potential_biomass_per_km2 * ( Temp_surface / ( Temp_surface_1850 - 273.15 ) - 1 ) )
        idxlhs = fcol_in_mdf['Effect_of_temperature_on_new_biomass_growth_dmnl']
        idx1 = fcol_in_mdf['Temp_surface']
        mdf[rowi, idxlhs] =  (  1  +  Slope_of_temp_eff_on_potential_biomass_per_km2  *  ( mdf[rowi, idx1] /  (  Temp_surface_1850  -  273.15  )  -  1  )  ) 
    
    # GRASS_living_biomass_densitiy_tBiomass_pr_km2 = GRASS_living_biomass_densitiy_in_1850_tBiomass_pr_km2 * Effect_of_CO2_on_new_biomass_growth * Effect_of_temperature_on_new_biomass_growth_dmnl
        idxlhs = fcol_in_mdf['GRASS_living_biomass_densitiy_tBiomass_pr_km2']
        idx1 = fcol_in_mdf['Effect_of_CO2_on_new_biomass_growth']
        idx2 = fcol_in_mdf['Effect_of_temperature_on_new_biomass_growth_dmnl']
        mdf[rowi, idxlhs] =  GRASS_living_biomass_densitiy_in_1850_tBiomass_pr_km2  * mdf[rowi, idx1] * mdf[rowi, idx2]
    
    # GRASS_being_harvested_Mkm2_py = Use_of_GRASS_biomass_for_energy / GRASS_living_biomass_densitiy_tBiomass_pr_km2 * UNIT_conversion_GtBiomass_py_to_Mkm2_py
        idxlhs = fcol_in_mdf['GRASS_being_harvested_Mkm2_py']
        idx1 = fcol_in_mdf['Use_of_GRASS_biomass_for_energy']
        idx2 = fcol_in_mdf['GRASS_living_biomass_densitiy_tBiomass_pr_km2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] / mdf[rowi, idx2] *  UNIT_conversion_GtBiomass_py_to_Mkm2_py 
    
    # GRASS_DeadB_SOM_being_lost_due_to_energy_harvesting = GRASS_being_harvested_Mkm2_py * GRASS_fraction_of_DeadB_and_SOM_being_destroyed_by_energy_harvesting * GRASS_DeadB_and_SOM_tB_per_km2 / 1000
        idxlhs = fcol_in_mdf['GRASS_DeadB_SOM_being_lost_due_to_energy_harvesting']
        idx1 = fcol_in_mdf['GRASS_being_harvested_Mkm2_py']
        idx2 = fcol_in_mdf['GRASS_DeadB_and_SOM_tB_per_km2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  GRASS_fraction_of_DeadB_and_SOM_being_destroyed_by_energy_harvesting  * mdf[rowi, idx2] /  1000 
    
    # GRASS_runoff = GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass / GRASS_runoff_time
        idxlhs = fcol_in_mdf['GRASS_runoff']
        idx1 = fcol_in_mdf['GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  GRASS_runoff_time 
    
    # Effect_of_temperature_on_fire_incidence = 1 + Slope_temp_eff_on_fire_incidence * ( Temp_surface / ( Temp_surface_1850 - 273.15 ) - 1 )
        idxlhs = fcol_in_mdf['Effect_of_temperature_on_fire_incidence']
        idx1 = fcol_in_mdf['Temp_surface']
        mdf[rowi, idxlhs] =  1  +  Slope_temp_eff_on_fire_incidence  *  ( mdf[rowi, idx1] /  (  Temp_surface_1850  -  273.15  )  -  1  ) 
    
    # GRASS_burning_Mkm2_py = GRASS_with_normal_cover_Mkm2 * Effect_of_temperature_on_fire_incidence * GRASS_Normal_fire_incidence_fraction_py / 100
        idxlhs = fcol_in_mdf['GRASS_burning_Mkm2_py']
        idx1 = fcol_in_mdf['GRASS_with_normal_cover_Mkm2']
        idx2 = fcol_in_mdf['Effect_of_temperature_on_fire_incidence']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2] *  GRASS_Normal_fire_incidence_fraction_py  /  100 
    
    # GRASS_soil_degradation_from_forest_fires = GRASS_burning_Mkm2_py * GRASS_DeadB_and_SOM_tB_per_km2 / 1000 * GRASS_fraction_of_DeadB_and_SOM_destroyed_by_natural_fires
        idxlhs = fcol_in_mdf['GRASS_soil_degradation_from_forest_fires']
        idx1 = fcol_in_mdf['GRASS_burning_Mkm2_py']
        idx2 = fcol_in_mdf['GRASS_DeadB_and_SOM_tB_per_km2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2] /  1000  *  GRASS_fraction_of_DeadB_and_SOM_destroyed_by_natural_fires 
    
    # GRASS_Dead_biomass_decomposing = GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass / GRASS_Time_to_decompose_undisturbed_dead_biomass_yr
        idxlhs = fcol_in_mdf['GRASS_Dead_biomass_decomposing']
        idx1 = fcol_in_mdf['GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  GRASS_Time_to_decompose_undisturbed_dead_biomass_yr 
    
    # Sum_outflows_GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM = GRASS_DeadB_SOM_being_lost_due_to_deforestation + GRASS_DeadB_SOM_being_lost_due_to_energy_harvesting + GRASS_runoff + GRASS_soil_degradation_from_forest_fires + GRASS_Dead_biomass_decomposing
        idxlhs = fcol_in_mdf['Sum_outflows_GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM']
        idx1 = fcol_in_mdf['GRASS_DeadB_SOM_being_lost_due_to_deforestation']
        idx2 = fcol_in_mdf['GRASS_DeadB_SOM_being_lost_due_to_energy_harvesting']
        idx3 = fcol_in_mdf['GRASS_runoff']
        idx4 = fcol_in_mdf['GRASS_soil_degradation_from_forest_fires']
        idx5 = fcol_in_mdf['GRASS_Dead_biomass_decomposing']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] + mdf[rowi, idx4] + mdf[rowi, idx5]
    
    # NF_with_normal_cover_Mkm2 = NF_potential_area_Mkm2 - NF_area_burnt_Mkm2 - NF_area_deforested_Mkm2 - NF_area_clear_cut_Mkm2 - NF_area_harvested_Mkm2
        idxlhs = fcol_in_mdf['NF_with_normal_cover_Mkm2']
        idx1 = fcol_in_mdf['NF_potential_area_Mkm2']
        idx2 = fcol_in_mdf['NF_area_burnt_Mkm2']
        idx3 = fcol_in_mdf['NF_area_deforested_Mkm2']
        idx4 = fcol_in_mdf['NF_area_clear_cut_Mkm2']
        idx5 = fcol_in_mdf['NF_area_harvested_Mkm2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] - mdf[rowi, idx2] - mdf[rowi, idx3] - mdf[rowi, idx4] - mdf[rowi, idx5]
    
    # NF_being_deforested_Mkm2_py = NF_with_normal_cover_Mkm2 * NF_historical_deforestation_pct_py
        idxlhs = fcol_in_mdf['NF_being_deforested_Mkm2_py']
        idx1 = fcol_in_mdf['NF_with_normal_cover_Mkm2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  NF_historical_deforestation_pct_py 
    
    # NF_DeadB_and_SOM_tB_per_km2 = NF_DeadB_and_SOM_densitiy_in_1850 * Effect_of_CO2_on_new_biomass_growth * Effect_of_temperature_on_new_biomass_growth_dmnl
        idxlhs = fcol_in_mdf['NF_DeadB_and_SOM_tB_per_km2']
        idx1 = fcol_in_mdf['Effect_of_CO2_on_new_biomass_growth']
        idx2 = fcol_in_mdf['Effect_of_temperature_on_new_biomass_growth_dmnl']
        mdf[rowi, idxlhs] =  NF_DeadB_and_SOM_densitiy_in_1850  * mdf[rowi, idx1] * mdf[rowi, idx2]
    
    # NF_DeadB_SOM_being_lost_due_to_deforestation = NF_being_deforested_Mkm2_py * NF_fraction_of_DeadB_and_SOM_being_destroyed_by_deforesting * NF_DeadB_and_SOM_tB_per_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
        idxlhs = fcol_in_mdf['NF_DeadB_SOM_being_lost_due_to_deforestation']
        idx1 = fcol_in_mdf['NF_being_deforested_Mkm2_py']
        idx2 = fcol_in_mdf['NF_DeadB_and_SOM_tB_per_km2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  NF_fraction_of_DeadB_and_SOM_being_destroyed_by_deforesting  * mdf[rowi, idx2] /  UNIT_conversion_GtBiomass_py_to_Mkm2_py 
    
    # Use_of_NF_biomass_for_energy = Use_of_NF_for_energy_in_2000_GtBiomass * Effect_of_population_and_urbanization_on_biomass_use * UNIT_conversion_1_py
        idxlhs = fcol_in_mdf['Use_of_NF_biomass_for_energy']
        idx1 = fcol_in_mdf['Effect_of_population_and_urbanization_on_biomass_use']
        mdf[rowi, idxlhs] =  Use_of_NF_for_energy_in_2000_GtBiomass  * mdf[rowi, idx1] *  UNIT_conversion_1_py 
     
    # Global_forest_land = SUM ( Forest_land[region!] )
        idxlhs = fcol_in_mdf['Global_forest_land']
        idx1 = fcol_in_mdf['Forest_land']
        globsum = 0
        for j in range(0,10):
            globsum = globsum + mdf[rowi, idx1 + j]
        mdf[rowi, idxlhs] = globsum 
    
    # Forest_land_rel_to_init = Global_forest_land / Global_forest_land_in_1980
        idxlhs = fcol_in_mdf['Forest_land_rel_to_init']
        idx1 = fcol_in_mdf['Global_forest_land']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Global_forest_land_in_1980 
    
    # Smoothed_Forest_land_rel_to_init = SMOOTH3 ( Forest_land_rel_to_init , Time_to_smooth_forest_land_comparison )
        idx1 = fcol_in_mdf['Forest_land_rel_to_init']
        idxin = fcol_in_mdf['Forest_land_rel_to_init' ]
        idx2 = fcol_in_mdf['Smoothed_Forest_land_rel_to_init_2']
        idx1 = fcol_in_mdf['Smoothed_Forest_land_rel_to_init_1']
        idxout = fcol_in_mdf['Smoothed_Forest_land_rel_to_init']
        mdf[rowi, idxout] = mdf[rowi-1, idxout] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idxout]) / ( Time_to_smooth_forest_land_comparison / 3) * dt
        mdf[rowi, idx2] = mdf[rowi-1, idx2] + ( mdf[rowi-1, idx1] - mdf[rowi-1, idx2]) / ( Time_to_smooth_forest_land_comparison / 3) * dt
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idxin] - mdf[rowi-1, idx1]) / ( Time_to_smooth_forest_land_comparison / 3) * dt
    
    # NF_living_biomass_densitiy_tBiomass_pr_km2 = NF_living_biomass_densitiy_in_1850_tBiomass_pr_km2 * Effect_of_CO2_on_new_biomass_growth * Effect_of_temperature_on_new_biomass_growth_dmnl * Smoothed_Forest_land_rel_to_init
        idxlhs = fcol_in_mdf['NF_living_biomass_densitiy_tBiomass_pr_km2']
        idx1 = fcol_in_mdf['Effect_of_CO2_on_new_biomass_growth']
        idx2 = fcol_in_mdf['Effect_of_temperature_on_new_biomass_growth_dmnl']
        idx3 = fcol_in_mdf['Smoothed_Forest_land_rel_to_init']
        mdf[rowi, idxlhs] =  NF_living_biomass_densitiy_in_1850_tBiomass_pr_km2  * mdf[rowi, idx1] * mdf[rowi, idx2] * mdf[rowi, idx3]
    
    # NF_usage_as_pct_of_potential_area = ( NF_area_burnt_Mkm2 + NF_area_clear_cut_Mkm2 + NF_area_deforested_Mkm2 + NF_area_harvested_Mkm2 ) / NF_with_normal_cover_Mkm2
        idxlhs = fcol_in_mdf['NF_usage_as_pct_of_potential_area']
        idx1 = fcol_in_mdf['NF_area_burnt_Mkm2']
        idx2 = fcol_in_mdf['NF_area_clear_cut_Mkm2']
        idx3 = fcol_in_mdf['NF_area_deforested_Mkm2']
        idx4 = fcol_in_mdf['NF_area_harvested_Mkm2']
        idx5 = fcol_in_mdf['NF_with_normal_cover_Mkm2']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] + mdf[rowi, idx4] )  / mdf[rowi, idx5]
    
    # NF_usage_cutoff = WITH LOOKUP ( NF_usage_as_pct_of_potential_area , ( [ ( 0.5 , 0 ) - ( 0.8 , 1 ) ] , ( 0.5 , 1 ) , ( 0.621101 , 0.921053 ) , ( 0.700917 , 0.732456 ) , ( 0.738532 , 0.442982 ) , ( 0.761468 , 0.223684 ) , ( 0.777064 , 0.0789474 ) , ( 0.8 , 0 ) ) )
        tabidx = ftab_in_d_table['NF_usage_cutoff'] # fetch the correct table
        idxlhs = fcol_in_mdf['NF_usage_cutoff'] # get the location of the lhs in mdf
        idx1 = fcol_in_mdf['NF_usage_as_pct_of_potential_area']
        look = d_table[tabidx]
        valgt = GRAPH(mdf[rowi,  idx1], look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # NF_being_harvested_Mkm2_py = Use_of_NF_biomass_for_energy / NF_living_biomass_densitiy_tBiomass_pr_km2 * UNIT_conversion_GtBiomass_py_to_Mkm2_py * NF_usage_cutoff
        idxlhs = fcol_in_mdf['NF_being_harvested_Mkm2_py']
        idx1 = fcol_in_mdf['Use_of_NF_biomass_for_energy']
        idx2 = fcol_in_mdf['NF_living_biomass_densitiy_tBiomass_pr_km2']
        idx3 = fcol_in_mdf['NF_usage_cutoff']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] / mdf[rowi, idx2] *  UNIT_conversion_GtBiomass_py_to_Mkm2_py  * mdf[rowi, idx3]
    
    # NF_clear_cut_fraction = WITH LOOKUP ( zeit , ( [ ( 1850 , - 0.0005 ) - ( 2100 , 0.9 ) ] , ( 1850 , 0 ) , ( 1900 , 0.5 ) , ( 1950 , 0.8 ) , ( 2000 , 0.8 ) , ( 2050 , 0.6 ) , ( 2100 , 0.8 ) ) )
        tabidx = ftab_in_d_table['NF_clear_cut_fraction'] # fetch the correct table
        idxlhs = fcol_in_mdf['NF_clear_cut_fraction'] # get the location of the lhs in mdf
        look = d_table[tabidx]
        valgt = GRAPH( zeit, look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # NF_being_harvested_normally_Mkm2_py = NF_being_harvested_Mkm2_py * ( 1 - NF_clear_cut_fraction )
        idxlhs = fcol_in_mdf['NF_being_harvested_normally_Mkm2_py']
        idx1 = fcol_in_mdf['NF_being_harvested_Mkm2_py']
        idx2 = fcol_in_mdf['NF_clear_cut_fraction']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  (  1  - mdf[rowi, idx2] ) 
    
    # NF_DeadB_SOM_being_lost_due_to_energy_harvesting = NF_being_harvested_normally_Mkm2_py * NF_fraction_of_DeadB_and_SOM_being_destroyed_by_energy_harvesting * NF_DeadB_and_SOM_tB_per_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
        idxlhs = fcol_in_mdf['NF_DeadB_SOM_being_lost_due_to_energy_harvesting']
        idx1 = fcol_in_mdf['NF_being_harvested_normally_Mkm2_py']
        idx2 = fcol_in_mdf['NF_DeadB_and_SOM_tB_per_km2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  NF_fraction_of_DeadB_and_SOM_being_destroyed_by_energy_harvesting  * mdf[rowi, idx2] /  UNIT_conversion_GtBiomass_py_to_Mkm2_py 
    
    # NF_runoff = NF_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass / NF_runoff_time
        idxlhs = fcol_in_mdf['NF_runoff']
        idx1 = fcol_in_mdf['NF_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  NF_runoff_time 
    
    # NF_being_harvested_by_clear_cutting_Mkm2_py = NF_being_harvested_Mkm2_py * NF_clear_cut_fraction
        idxlhs = fcol_in_mdf['NF_being_harvested_by_clear_cutting_Mkm2_py']
        idx1 = fcol_in_mdf['NF_being_harvested_Mkm2_py']
        idx2 = fcol_in_mdf['NF_clear_cut_fraction']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2]
    
    # NF_soil_degradation_from_clear_cutting = NF_being_harvested_by_clear_cutting_Mkm2_py * NF_fraction_of_DeadB_and_SOM_being_destroyed_by_clear_cutting * NF_DeadB_and_SOM_tB_per_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
        idxlhs = fcol_in_mdf['NF_soil_degradation_from_clear_cutting']
        idx1 = fcol_in_mdf['NF_being_harvested_by_clear_cutting_Mkm2_py']
        idx2 = fcol_in_mdf['NF_DeadB_and_SOM_tB_per_km2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  NF_fraction_of_DeadB_and_SOM_being_destroyed_by_clear_cutting  * mdf[rowi, idx2] /  UNIT_conversion_GtBiomass_py_to_Mkm2_py 
    
    # NF_burning_Mkm2_py = NF_with_normal_cover_Mkm2 * Effect_of_temperature_on_fire_incidence * NF_Normal_fire_incidence_fraction_py / 100
        idxlhs = fcol_in_mdf['NF_burning_Mkm2_py']
        idx1 = fcol_in_mdf['NF_with_normal_cover_Mkm2']
        idx2 = fcol_in_mdf['Effect_of_temperature_on_fire_incidence']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2] *  NF_Normal_fire_incidence_fraction_py  /  100 
    
    # NF_soil_degradation_from_forest_fires = NF_burning_Mkm2_py * NF_DeadB_and_SOM_tB_per_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py * NF_fraction_of_DeadB_and_SOM_destroyed_by_natural_fires
        idxlhs = fcol_in_mdf['NF_soil_degradation_from_forest_fires']
        idx1 = fcol_in_mdf['NF_burning_Mkm2_py']
        idx2 = fcol_in_mdf['NF_DeadB_and_SOM_tB_per_km2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2] /  UNIT_conversion_GtBiomass_py_to_Mkm2_py  *  NF_fraction_of_DeadB_and_SOM_destroyed_by_natural_fires 
    
    # NF_Dead_biomass_decomposing = NF_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass / NF_Time_to_decompose_undisturbed_dead_biomass_yr
        idxlhs = fcol_in_mdf['NF_Dead_biomass_decomposing']
        idx1 = fcol_in_mdf['NF_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  NF_Time_to_decompose_undisturbed_dead_biomass_yr 
    
    # NF_Sum_outflows_NF_Dead_biomass_litter_and_soil_organic_matter_SOM = NF_DeadB_SOM_being_lost_due_to_deforestation + NF_DeadB_SOM_being_lost_due_to_energy_harvesting + NF_runoff + NF_soil_degradation_from_clear_cutting + NF_soil_degradation_from_forest_fires + NF_Dead_biomass_decomposing
        idxlhs = fcol_in_mdf['NF_Sum_outflows_NF_Dead_biomass_litter_and_soil_organic_matter_SOM']
        idx1 = fcol_in_mdf['NF_DeadB_SOM_being_lost_due_to_deforestation']
        idx2 = fcol_in_mdf['NF_DeadB_SOM_being_lost_due_to_energy_harvesting']
        idx3 = fcol_in_mdf['NF_runoff']
        idx4 = fcol_in_mdf['NF_soil_degradation_from_clear_cutting']
        idx5 = fcol_in_mdf['NF_soil_degradation_from_forest_fires']
        idx6 = fcol_in_mdf['NF_Dead_biomass_decomposing']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] + mdf[rowi, idx4] + mdf[rowi, idx5] + mdf[rowi, idx6]
    
    # TROP_with_normal_cover = TROP_potential_area_Mkm2 - TROP_area_burnt - TROP_area_deforested - TROP_area_clear_cut - TROP_area_harvested_Mkm2
        idxlhs = fcol_in_mdf['TROP_with_normal_cover']
        idx1 = fcol_in_mdf['TROP_potential_area_Mkm2']
        idx2 = fcol_in_mdf['TROP_area_burnt']
        idx3 = fcol_in_mdf['TROP_area_deforested']
        idx4 = fcol_in_mdf['TROP_area_clear_cut']
        idx5 = fcol_in_mdf['TROP_area_harvested_Mkm2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] - mdf[rowi, idx2] - mdf[rowi, idx3] - mdf[rowi, idx4] - mdf[rowi, idx5]
    
    # TROP_deforestion_multiplier = WITH LOOKUP ( zeit , ( [ ( 1850 , 0 ) - ( 2100 , 2 ) ] , ( 1850 , 0 ) , ( 1970 , 0.4 ) , ( 2000 , 0.5 ) , ( 2020 , 0.5 ) , ( 2100 , 0 ) ) )
        tabidx = ftab_in_d_table['TROP_deforestion_multiplier'] # fetch the correct table
        idxlhs = fcol_in_mdf['TROP_deforestion_multiplier'] # get the location of the lhs in mdf
        look = d_table[tabidx]
        valgt = GRAPH( zeit, look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # TROP_historical_deforestation = ( TROP_Ref_historical_deforestation / 100 ) * TROP_deforestion_multiplier
        idxlhs = fcol_in_mdf['TROP_historical_deforestation']
        idx1 = fcol_in_mdf['TROP_deforestion_multiplier']
        mdf[rowi, idxlhs] =  (  TROP_Ref_historical_deforestation  /  100  )  * mdf[rowi, idx1]
    
    # TROP_deforested_as_pct_of_potential_area = TROP_area_deforested / TROP_potential_area_Mkm2
        idxlhs = fcol_in_mdf['TROP_deforested_as_pct_of_potential_area']
        idx1 = fcol_in_mdf['TROP_area_deforested']
        idx2 = fcol_in_mdf['TROP_potential_area_Mkm2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] / mdf[rowi, idx2]
    
    # TROP_deforestation_cutoff = WITH LOOKUP ( TROP_deforested_as_pct_of_potential_area , ( [ ( 0.5 , 0 ) - ( 0.8 , 1 ) ] , ( 0.5 , 1 ) , ( 0.621101 , 0.921053 ) , ( 0.700917 , 0.732456 ) , ( 0.738532 , 0.442982 ) , ( 0.761468 , 0.223684 ) , ( 0.777064 , 0.0789474 ) , ( 0.8 , 0 ) ) )
        tabidx = ftab_in_d_table['TROP_deforestation_cutoff'] # fetch the correct table
        idxlhs = fcol_in_mdf['TROP_deforestation_cutoff'] # get the location of the lhs in mdf
        idx1 = fcol_in_mdf['TROP_deforested_as_pct_of_potential_area']
        look = d_table[tabidx]
        valgt = GRAPH(mdf[rowi,  idx1], look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # Stop_of_human_deforestation = IF_THEN_ELSE ( zeit > Time_at_which_human_deforestation_is_stopped , 0 , 1 )
        idxlhs = fcol_in_mdf['Stop_of_human_deforestation']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  (  zeit  >  Time_at_which_human_deforestation_is_stopped  ,  0  ,  1  ) 
    
    # TROP_being_deforested_Mkm2_py = TROP_with_normal_cover * TROP_historical_deforestation * TROP_deforestation_cutoff * Stop_of_human_deforestation
        idxlhs = fcol_in_mdf['TROP_being_deforested_Mkm2_py']
        idx1 = fcol_in_mdf['TROP_with_normal_cover']
        idx2 = fcol_in_mdf['TROP_historical_deforestation']
        idx3 = fcol_in_mdf['TROP_deforestation_cutoff']
        idx4 = fcol_in_mdf['Stop_of_human_deforestation']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2] * mdf[rowi, idx3] * mdf[rowi, idx4]
    
    # TROP_DeadB_and_SOM_tB_per_km2 = TROP_DeadB_and_SOM_densitiy_in_1850_tBiomass_pr_km2 * Effect_of_CO2_on_new_biomass_growth * Effect_of_temperature_on_new_biomass_growth_dmnl
        idxlhs = fcol_in_mdf['TROP_DeadB_and_SOM_tB_per_km2']
        idx1 = fcol_in_mdf['Effect_of_CO2_on_new_biomass_growth']
        idx2 = fcol_in_mdf['Effect_of_temperature_on_new_biomass_growth_dmnl']
        mdf[rowi, idxlhs] =  TROP_DeadB_and_SOM_densitiy_in_1850_tBiomass_pr_km2  * mdf[rowi, idx1] * mdf[rowi, idx2]
    
    # TROP_DeadB_SOM_being_lost_due_to_deforestation = TROP_being_deforested_Mkm2_py * TROP_fraction_of_DeadB_and_SOM_being_destroyed_by_deforesting * TROP_DeadB_and_SOM_tB_per_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
        idxlhs = fcol_in_mdf['TROP_DeadB_SOM_being_lost_due_to_deforestation']
        idx1 = fcol_in_mdf['TROP_being_deforested_Mkm2_py']
        idx2 = fcol_in_mdf['TROP_DeadB_and_SOM_tB_per_km2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  TROP_fraction_of_DeadB_and_SOM_being_destroyed_by_deforesting  * mdf[rowi, idx2] /  UNIT_conversion_GtBiomass_py_to_Mkm2_py 
    
    # TROP_Use_of_NF_biomass_for_energy = Use_of_TROP_for_energy_in_2000_GtBiomass * Effect_of_population_and_urbanization_on_biomass_use * UNIT_conversion_to_yr
        idxlhs = fcol_in_mdf['TROP_Use_of_NF_biomass_for_energy']
        idx1 = fcol_in_mdf['Effect_of_population_and_urbanization_on_biomass_use']
        mdf[rowi, idxlhs] =  Use_of_TROP_for_energy_in_2000_GtBiomass  * mdf[rowi, idx1] *  UNIT_conversion_to_yr 
    
    # TROP_living_biomass_densitiy_tBiomass_pr_km2 = TROP_living_biomass_densitiy_in_1850_tBiomass_pr_km2 * Effect_of_CO2_on_new_biomass_growth * Effect_of_temperature_on_new_biomass_growth_dmnl * Smoothed_Forest_land_rel_to_init
        idxlhs = fcol_in_mdf['TROP_living_biomass_densitiy_tBiomass_pr_km2']
        idx1 = fcol_in_mdf['Effect_of_CO2_on_new_biomass_growth']
        idx2 = fcol_in_mdf['Effect_of_temperature_on_new_biomass_growth_dmnl']
        idx3 = fcol_in_mdf['Smoothed_Forest_land_rel_to_init']
        mdf[rowi, idxlhs] =  TROP_living_biomass_densitiy_in_1850_tBiomass_pr_km2  * mdf[rowi, idx1] * mdf[rowi, idx2] * mdf[rowi, idx3]
    
    # TROP_being_harvested = TROP_Use_of_NF_biomass_for_energy / TROP_living_biomass_densitiy_tBiomass_pr_km2 * UNIT_conversion_GtBiomass_py_to_Mkm2_py
        idxlhs = fcol_in_mdf['TROP_being_harvested']
        idx1 = fcol_in_mdf['TROP_Use_of_NF_biomass_for_energy']
        idx2 = fcol_in_mdf['TROP_living_biomass_densitiy_tBiomass_pr_km2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] / mdf[rowi, idx2] *  UNIT_conversion_GtBiomass_py_to_Mkm2_py 
    
    # TROP_being_harvested_normally = TROP_being_harvested * ( 1 - TROP_clear_cut_fraction )
        idxlhs = fcol_in_mdf['TROP_being_harvested_normally']
        idx1 = fcol_in_mdf['TROP_being_harvested']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  (  1  -  TROP_clear_cut_fraction  ) 
    
    # TROP_DeadB_SOM_being_lost_due_to_energy_harvesting = TROP_being_harvested_normally * TROP_fraction_of_DeadB_and_SOM_being_destroyed_by_energy_harvesting * TROP_DeadB_and_SOM_tB_per_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
        idxlhs = fcol_in_mdf['TROP_DeadB_SOM_being_lost_due_to_energy_harvesting']
        idx1 = fcol_in_mdf['TROP_being_harvested_normally']
        idx2 = fcol_in_mdf['TROP_DeadB_and_SOM_tB_per_km2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  TROP_fraction_of_DeadB_and_SOM_being_destroyed_by_energy_harvesting  * mdf[rowi, idx2] /  UNIT_conversion_GtBiomass_py_to_Mkm2_py 
    
    # TROP_runoff = TROP_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass / TROP_runoff_time
        idxlhs = fcol_in_mdf['TROP_runoff']
        idx1 = fcol_in_mdf['TROP_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  TROP_runoff_time 
    
    # TROP_being_harvested_by_clear_cutting = TROP_being_harvested * TROP_clear_cut_fraction
        idxlhs = fcol_in_mdf['TROP_being_harvested_by_clear_cutting']
        idx1 = fcol_in_mdf['TROP_being_harvested']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  TROP_clear_cut_fraction 
    
    # TROP_soil_degradation_from_clear_cutting = TROP_being_harvested_by_clear_cutting * TROP_fraction_of_DeadB_and_SOM_being_destroyed_by_clear_cutting * TROP_DeadB_and_SOM_tB_per_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
        idxlhs = fcol_in_mdf['TROP_soil_degradation_from_clear_cutting']
        idx1 = fcol_in_mdf['TROP_being_harvested_by_clear_cutting']
        idx2 = fcol_in_mdf['TROP_DeadB_and_SOM_tB_per_km2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  TROP_fraction_of_DeadB_and_SOM_being_destroyed_by_clear_cutting  * mdf[rowi, idx2] /  UNIT_conversion_GtBiomass_py_to_Mkm2_py 
    
    # TROP_burning = TROP_with_normal_cover * Effect_of_temperature_on_fire_incidence * TROP_Normal_fire_incidence / 100
        idxlhs = fcol_in_mdf['TROP_burning']
        idx1 = fcol_in_mdf['TROP_with_normal_cover']
        idx2 = fcol_in_mdf['Effect_of_temperature_on_fire_incidence']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2] *  TROP_Normal_fire_incidence  /  100 
    
    # TROP_soil_degradation_from_forest_fires = TROP_burning * TROP_DeadB_and_SOM_tB_per_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py * TROP_fraction_of_DeadB_and_SOM_destroyed_by_natural_fires
        idxlhs = fcol_in_mdf['TROP_soil_degradation_from_forest_fires']
        idx1 = fcol_in_mdf['TROP_burning']
        idx2 = fcol_in_mdf['TROP_DeadB_and_SOM_tB_per_km2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2] /  UNIT_conversion_GtBiomass_py_to_Mkm2_py  *  TROP_fraction_of_DeadB_and_SOM_destroyed_by_natural_fires 
    
    # TROP_Dead_biomass_decomposing = TROP_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass / TROP_Time_to_decompose_undisturbed_dead_biomass_yr
        idxlhs = fcol_in_mdf['TROP_Dead_biomass_decomposing']
        idx1 = fcol_in_mdf['TROP_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  TROP_Time_to_decompose_undisturbed_dead_biomass_yr 
    
    # TROP_Sum_outflows_TROP_Dead_biomass_litter_and_soil_organic_matter_SOM = TROP_DeadB_SOM_being_lost_due_to_deforestation + TROP_DeadB_SOM_being_lost_due_to_energy_harvesting + TROP_runoff + TROP_soil_degradation_from_clear_cutting + TROP_soil_degradation_from_forest_fires + TROP_Dead_biomass_decomposing
        idxlhs = fcol_in_mdf['TROP_Sum_outflows_TROP_Dead_biomass_litter_and_soil_organic_matter_SOM']
        idx1 = fcol_in_mdf['TROP_DeadB_SOM_being_lost_due_to_deforestation']
        idx2 = fcol_in_mdf['TROP_DeadB_SOM_being_lost_due_to_energy_harvesting']
        idx3 = fcol_in_mdf['TROP_runoff']
        idx4 = fcol_in_mdf['TROP_soil_degradation_from_clear_cutting']
        idx5 = fcol_in_mdf['TROP_soil_degradation_from_forest_fires']
        idx6 = fcol_in_mdf['TROP_Dead_biomass_decomposing']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] + mdf[rowi, idx4] + mdf[rowi, idx5] + mdf[rowi, idx6]
    
    # Indicated_wellbeing_from_env_damage = MAX ( 0 , 1 + SoE_of_env_damage_indicator * Combined_env_damage_indicator )
        idxlhs = fcol_in_mdf['Indicated_wellbeing_from_env_damage']
        idx1 = fcol_in_mdf['Combined_env_damage_indicator']
        mdf[rowi, idxlhs] =  np.maximum  (  0  ,  1  +  SoE_of_env_damage_indicator  * mdf[rowi, idx1] ) 
    
    # Actual_wellbeing_from_env_damage = SMOOTH3 ( Indicated_wellbeing_from_env_damage , Time_for_env_damage_to_affect_wellbeing )
        idx1 = fcol_in_mdf['Indicated_wellbeing_from_env_damage']
        idxin = fcol_in_mdf['Indicated_wellbeing_from_env_damage' ]
        idx2 = fcol_in_mdf['Actual_wellbeing_from_env_damage_2']
        idx1 = fcol_in_mdf['Actual_wellbeing_from_env_damage_1']
        idxout = fcol_in_mdf['Actual_wellbeing_from_env_damage']
        mdf[rowi, idxout] = mdf[rowi-1, idxout] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idxout]) / ( Time_for_env_damage_to_affect_wellbeing / 3) * dt
        mdf[rowi, idx2] = mdf[rowi-1, idx2] + ( mdf[rowi-1, idx1] - mdf[rowi-1, idx2]) / ( Time_for_env_damage_to_affect_wellbeing / 3) * dt
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idxin] - mdf[rowi-1, idx1]) / ( Time_for_env_damage_to_affect_wellbeing / 3) * dt
    
    # Adding_capacity[region] = Capacity_under_construction[region] / Capacity_construction_time
        idxlhs = fcol_in_mdf['Adding_capacity']
        idx1 = fcol_in_mdf['Capacity_under_construction']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Capacity_construction_time 
    
    # El_use_pp_US = El_use_pp_US_s + El_use_pp_US_g * np.exp ( - ( ( ( GDPpp_USED[us] * UNIT_conv_to_make_exp_dmnl ) - El_use_pp_US_h ) ^ 2 ) / ( 1.8 * El_use_pp_US_k ^ 2 ) )
        idxlhs = fcol_in_mdf['El_use_pp_US']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs] =  El_use_pp_US_s  +  El_use_pp_US_g  *  np.exp  (  -  (  (  ( mdf[rowi, idx1 + 0] *  UNIT_conv_to_make_exp_dmnl  )  -  El_use_pp_US_h  )  **  2  )  /  (  1.8  *  El_use_pp_US_k  **  2  )  ) 
    
    # El_use_pp_WO_US[region] = El_use_pp_WO_US_L[region] / ( 1 + np.exp ( - El_use_pp_WO_US_k[region] * ( ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl ) - El_use_pp_WO_US_x0[region] ) ) )
        idxlhs = fcol_in_mdf['El_use_pp_WO_US']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  El_use_pp_WO_US_L[0:10]  /  (  1  +  np.exp  (  -  El_use_pp_WO_US_k[0:10]  *  (  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  )  -  El_use_pp_WO_US_x0[0:10]  )  )  ) 
    
    # El_use_pp = IF_THEN_ELSE ( j==0 , El_use_pp_US , El_use_pp_WO_US )
        idxlhs = fcol_in_mdf['El_use_pp']
        idx1 = fcol_in_mdf['El_use_pp_US']
        idx2 = fcol_in_mdf['El_use_pp_WO_US']
        for j in range(0,10):
            mdf[rowi, idxlhs + j] =  IF_THEN_ELSE  (  j==0  , mdf[rowi , idx1] , mdf[rowi , idx2 + j] ) 
    
    # El_use_pp_in_MWh_ppy[region] = El_use_pp[region] * UNIT_conv_to_MWh_ppy
        idxlhs = fcol_in_mdf['El_use_pp_in_MWh_ppy']
        idx1 = fcol_in_mdf['El_use_pp']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_MWh_ppy 
    
    # Demand_for_El_before_NEP[region] = ( ( ( Population[region] * El_use_pp_in_MWh_ppy[region] ) / Extra_energy_productivity_index_2024_is_1[region] ) ) * UNIT_conv_to_TWh
        idxlhs = fcol_in_mdf['Demand_for_El_before_NEP']
        idx1 = fcol_in_mdf['Population']
        idx2 = fcol_in_mdf['El_use_pp_in_MWh_ppy']
        idx3 = fcol_in_mdf['Extra_energy_productivity_index_2024_is_1']
        mdf[rowi, idxlhs:idxlhs + 10] =  (  (  ( mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] )  / mdf[rowi , idx3:idx3 + 10] )  )  *  UNIT_conv_to_TWh 
    
    # Increase_in_el_dmd_from_NEP[region] = Fossil_fuel_for_NON_El_use_that_IS_being_electrified[region] * Conversion_Mtoe_to_TWh[region]
        idxlhs = fcol_in_mdf['Increase_in_el_dmd_from_NEP']
        idx1 = fcol_in_mdf['Fossil_fuel_for_NON_El_use_that_IS_being_electrified']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  Conversion_Mtoe_to_TWh[0:10] 
    
    # Demand_for_El_afer_NEP[region] = Demand_for_El_before_NEP[region] + Increase_in_el_dmd_from_NEP[region]
        idxlhs = fcol_in_mdf['Demand_for_El_afer_NEP']
        idx1 = fcol_in_mdf['Demand_for_El_before_NEP']
        idx2 = fcol_in_mdf['Increase_in_el_dmd_from_NEP']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10]
    
    # Demand_for_el_from_fossil_fuel[region] = MAX ( 0 , Demand_for_El_afer_NEP[region] - wind_PV_nuclear_hydro_el_generation[region] )
        idxlhs = fcol_in_mdf['Demand_for_el_from_fossil_fuel']
        idx1 = fcol_in_mdf['Demand_for_El_afer_NEP']
        idx2 = fcol_in_mdf['wind_PV_nuclear_hydro_el_generation']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.maximum  (  0  , mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10] ) 
    
    # Desired_fossil_gen_capacity[region] = Demand_for_el_from_fossil_fuel[region] / Fossil_capacity_factor[region] / Hours_per_year / UNIT_conv_GWh_and_TWh
        idxlhs = fcol_in_mdf['Desired_fossil_gen_capacity']
        idx1 = fcol_in_mdf['Demand_for_el_from_fossil_fuel']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Fossil_capacity_factor[0:10]  /  Hours_per_year  /  UNIT_conv_GWh_and_TWh 
    
    # Discarding_of_FEGC[region] = Fossil_el_gen_cap[region] / Life_of_fossil_el_gen_cap
        idxlhs = fcol_in_mdf['Discarding_of_FEGC']
        idx1 = fcol_in_mdf['Fossil_el_gen_cap']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Life_of_fossil_el_gen_cap 
    
    # Desired_fossil_el_capacity_change[region] = ( Desired_fossil_gen_capacity[region] - Fossil_el_gen_cap[region] ) / Time_to_close_gap_in_fossil_el_cap[region] + Discarding_of_FEGC[region]
        idxlhs = fcol_in_mdf['Desired_fossil_el_capacity_change']
        idx1 = fcol_in_mdf['Desired_fossil_gen_capacity']
        idx2 = fcol_in_mdf['Fossil_el_gen_cap']
        idx3 = fcol_in_mdf['Discarding_of_FEGC']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10] )  /  Time_to_close_gap_in_fossil_el_cap[0:10]  + mdf[rowi , idx3:idx3 + 10]
    
    # Addition_of_FEGC[region] = Desired_fossil_el_capacity_change[region]
        idxlhs = fcol_in_mdf['Addition_of_FEGC']
        idx1 = fcol_in_mdf['Desired_fossil_el_capacity_change']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10]
    
    # ISPV_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , ISPV_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , ISPV_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , ISPV_R1_via_Excel , ISPV_policy_Min ) ) )
        idxlhs = fcol_in_mdf['ISPV_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  ISPV_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  ISPV_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  ISPV_R1_via_Excel[0:10]  ,  ISPV_policy_Min  )  )  ) 
    
    # ISPV_policy_with_RW[region] = ISPV_policy_Min + ( ISPV_rounds_via_Excel[region] - ISPV_policy_Min ) * Smoothed_Reform_willingness[region] / Inequality_effect_on_energy_TA[region]
        idxlhs = fcol_in_mdf['ISPV_policy_with_RW']
        idx1 = fcol_in_mdf['ISPV_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        idx3 = fcol_in_mdf['Inequality_effect_on_energy_TA']
        mdf[rowi, idxlhs:idxlhs + 10] =  ISPV_policy_Min  +  ( mdf[rowi , idx1:idx1 + 10] -  ISPV_policy_Min  )  * mdf[rowi , idx2:idx2 + 10] / mdf[rowi , idx3:idx3 + 10]
     
    # ISPV_pol_div_100[region] = MIN ( ISPV_policy_Max , MAX ( ISPV_policy_Min , ISPV_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['ISPV_pol_div_100']
        idx1 = fcol_in_mdf['ISPV_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], ISPV_policy_Min, ISPV_policy_Max) / 100
    
    # wind_and_PV_el_share_max[region] = SMOOTH3 ( ISPV_pol_div_100[region] , Time_to_implement_ISPV_goal )
        idxin = fcol_in_mdf['ISPV_pol_div_100' ]
        idx2 = fcol_in_mdf['wind_and_PV_el_share_max_2']
        idx1 = fcol_in_mdf['wind_and_PV_el_share_max_1']
        idxout = fcol_in_mdf['wind_and_PV_el_share_max']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( Time_to_implement_ISPV_goal / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( Time_to_implement_ISPV_goal / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( Time_to_implement_ISPV_goal / 3) * dt
    
    # wind_and_PV_el_share[region] = wind_and_PV_el_share_max[region] / ( 1 + np.exp ( - wind_and_PV_el_share_k[region] * ( ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl ) - wind_and_PV_el_share_x0[region] ) ) )
        idxlhs = fcol_in_mdf['wind_and_PV_el_share']
        idx1 = fcol_in_mdf['wind_and_PV_el_share_max']
        idx2 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  (  1  +  np.exp  (  -  wind_and_PV_el_share_k[0:10]  *  (  ( mdf[rowi , idx2:idx2 + 10] *  UNIT_conv_to_make_exp_dmnl  )  -  wind_and_PV_el_share_x0[0:10]  )  )  ) 
    
    # Goal_for_suppy_of_wind_and_PV_el[region] = Demand_for_El_afer_NEP[region] * wind_and_PV_el_share[region]
        idxlhs = fcol_in_mdf['Goal_for_suppy_of_wind_and_PV_el']
        idx1 = fcol_in_mdf['Demand_for_El_afer_NEP']
        idx2 = fcol_in_mdf['wind_and_PV_el_share']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # Desired_wind_and_PV_el_cap[region] = Goal_for_suppy_of_wind_and_PV_el[region] / Hours_per_year / wind_and_PV_capacity_factor[region] / UNIT_conv_GWh_and_TWh
        idxlhs = fcol_in_mdf['Desired_wind_and_PV_el_cap']
        idx1 = fcol_in_mdf['Goal_for_suppy_of_wind_and_PV_el']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Hours_per_year  /  wind_and_PV_capacity_factor  /  UNIT_conv_GWh_and_TWh 
    
    # Goal_for_wind_and_PV_el_capacity_change[region] = Desired_wind_and_PV_el_cap[region] - wind_and_PV_el_capacity[region]
        idxlhs = fcol_in_mdf['Goal_for_wind_and_PV_el_capacity_change']
        idx1 = fcol_in_mdf['Desired_wind_and_PV_el_cap']
        idx2 = fcol_in_mdf['wind_and_PV_el_capacity']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10]
    
    # Discarding_wind_and_PV_el_capacity[region] = wind_and_PV_el_capacity[region] / Lifetime_of_wind_and_PV_el_cap
        idxlhs = fcol_in_mdf['Discarding_wind_and_PV_el_capacity']
        idx1 = fcol_in_mdf['wind_and_PV_el_capacity']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Lifetime_of_wind_and_PV_el_cap 
    
    # Addition_of_wind_and_PV_el_capacity[region] = MAX ( 0 , ( Goal_for_wind_and_PV_el_capacity_change[region] / wind_and_PV_construction_time ) + Discarding_wind_and_PV_el_capacity[region] )
        idxlhs = fcol_in_mdf['Addition_of_wind_and_PV_el_capacity']
        idx1 = fcol_in_mdf['Goal_for_wind_and_PV_el_capacity_change']
        idx2 = fcol_in_mdf['Discarding_wind_and_PV_el_capacity']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.maximum  (  0  ,  ( mdf[rowi , idx1:idx1 + 10] /  wind_and_PV_construction_time  )  + mdf[rowi , idx2:idx2 + 10] ) 
    
    # Crop_yield_last_year[region] = SMOOTHI ( Crop_yield_with_soil_quality_CO2_and_env_dam_effects[region] , One_year , crop_yield_in_1980[region] )
        idx1 = fcol_in_mdf['Crop_yield_last_year']
        idx2 = fcol_in_mdf['Crop_yield_with_soil_quality_CO2_and_env_dam_effects']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi - 1, idx1:idx1 + 10]) / One_year * dt
    
    # Desired_crop_yield[region] = Crop_yield_last_year[region] * ( 1 + Ratio_of_demand_to_regional_supply_of_crops[region] * Fraction_of_supply_imbalance_to_be_closed_by_yield_adjustment[region] )
        idxlhs = fcol_in_mdf['Desired_crop_yield']
        idx1 = fcol_in_mdf['Crop_yield_last_year']
        idx2 = fcol_in_mdf['Ratio_of_demand_to_regional_supply_of_crops']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  1  + mdf[rowi , idx2:idx2 + 10] *  Fraction_of_supply_imbalance_to_be_closed_by_yield_adjustment[0:10]  ) 
    
    # Nitrogen_use_AF = Nitrogen_use_AF_L / ( 1 + np.exp ( - Nitrogen_use_AF_k * ( Desired_crop_yield[af] / UNIT_conv_to_make_N_use_dmnl - Nitrogen_use_AF_x0 ) ) )
        idxlhs = fcol_in_mdf['Nitrogen_use_AF']
        idx1 = fcol_in_mdf['Desired_crop_yield']
        mdf[rowi, idxlhs] =  Nitrogen_use_AF_L  /  (  1  +  np.exp  (  -  Nitrogen_use_AF_k  *  ( mdf[rowi, idx1 + 1] /  UNIT_conv_to_make_N_use_dmnl  -  Nitrogen_use_AF_x0  )  )  ) 
    
    # Nitrogen_use_CN = Nitrogen_use_CN_b * LN ( Desired_crop_yield[cn] / UNIT_conv_to_make_N_use_dmnl ) - Nitrogen_use_CN_a
        idxlhs = fcol_in_mdf['Nitrogen_use_CN']
        idx1 = fcol_in_mdf['Desired_crop_yield']
        mdf[rowi, idxlhs] =  Nitrogen_use_CN_b  *  np.log  ( mdf[rowi, idx1 + 2] /  UNIT_conv_to_make_N_use_dmnl  )  -  Nitrogen_use_CN_a 
    
    # Nitrogen_use_SA = ( Nitrogen_use_SA_a * LN ( GDPpp_USED[sa] * UNIT_conv_to_make_exp_dmnl ) + Nitrogen_use_SA_b )
        idxlhs = fcol_in_mdf['Nitrogen_use_SA']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs] =  (  Nitrogen_use_SA_a  *  np.log  ( mdf[rowi, idx1 + 4] *  UNIT_conv_to_make_exp_dmnl  )  +  Nitrogen_use_SA_b  ) 
    
    # Nitrogen_use_rest[region] = Nitrogen_use_rest_L[region] / ( 1 + np.exp ( - Nitrogen_use_rest_k[region] * ( GDPpp_USED[region] - Nitrogen_use_rest_x0[region] ) ) )
        idxlhs = fcol_in_mdf['Nitrogen_use_rest']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  Nitrogen_use_rest_L[0:10]  /  (  1  +  np.exp  (  -  Nitrogen_use_rest_k[0:10]  *  ( mdf[rowi , idx1:idx1 + 10] -  Nitrogen_use_rest_x0[0:10]  )  )  ) 
    
    # Nitrogen_use = IF_THEN_ELSE ( j==1 , Nitrogen_use_AF , IF_THEN_ELSE ( j==2 , Nitrogen_use_CN , IF_THEN_ELSE ( j==4 , Nitrogen_use_SA , Nitrogen_use_rest ) ) )
        idxlhs = fcol_in_mdf['Nitrogen_use']
        idx1 = fcol_in_mdf['Nitrogen_use_AF']
        idx2 = fcol_in_mdf['Nitrogen_use_CN']
        idx3 = fcol_in_mdf['Nitrogen_use_SA']
        idx4 = fcol_in_mdf['Nitrogen_use_rest']
        for j in range(0,10):
            mdf[rowi, idxlhs + j] =  IF_THEN_ELSE  (  j==1  , mdf[rowi , idx1] ,  IF_THEN_ELSE  (  j==2  , mdf[rowi , idx2] ,  IF_THEN_ELSE  (  j==4  , mdf[rowi , idx3] , mdf[rowi , idx4 + j] )  )  ) 
    
    # Nitrogen_use_after_soil_regeneration[region] = Nitrogen_use[region] * ( 1 - Regenerative_cropland_fraction[region] * Fraction_of_N_use_saved_through_regenerative_practice[region] )
        idxlhs = fcol_in_mdf['Nitrogen_use_after_soil_regeneration']
        idx1 = fcol_in_mdf['Nitrogen_use']
        idx2 = fcol_in_mdf['Regenerative_cropland_fraction']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  1  - mdf[rowi , idx2:idx2 + 10] *  Fraction_of_N_use_saved_through_regenerative_practice  ) 
    
    # Addition_to_N_use_over_the_years[region] = IF_THEN_ELSE ( zeit > 2022 , Nitrogen_use_after_soil_regeneration * UNIT_conv_kgN_to_Nt , 0 )
        idxlhs = fcol_in_mdf['Addition_to_N_use_over_the_years']
        idx1 = fcol_in_mdf['Nitrogen_use_after_soil_regeneration']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >  2022  , mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_kgN_to_Nt  ,  0  ) 
    
    # Effect_of_GDPpp_on_RoC_of_CLR[region] = 1 + SoE_of_GDPpp_on_RoC_of_CLR[region] * ( GDPpp_USED[region] / GDPpp_in_1980[region] - 1 )
        idxlhs = fcol_in_mdf['Effect_of_GDPpp_on_RoC_of_CLR']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  +  SoE_of_GDPpp_on_RoC_of_CLR[0:10]  *  ( mdf[rowi , idx1:idx1 + 10] /  GDPpp_in_1980[0:10]  -  1  ) 
    
    # RoC_in_Capital_labour_ratio[region] = RoC_Capital_labour_ratio_in_1980[region] / Effect_of_GDPpp_on_RoC_of_CLR[region]
        idxlhs = fcol_in_mdf['RoC_in_Capital_labour_ratio']
        idx1 = fcol_in_mdf['Effect_of_GDPpp_on_RoC_of_CLR']
        mdf[rowi, idxlhs:idxlhs + 10] =  RoC_Capital_labour_ratio_in_1980[0:10]  / mdf[rowi , idx1:idx1 + 10]
    
    # Indicated_effect_of_worker_share_of_output_on_capital_labour_ratio[region] = 1 + Slope_of_Indicated_effect_of_worker_share_of_output_on_capital_labour_ratio * ( Worker_share_of_output_with_unemployment_effect[region] / Worker_share_of_output_with_unemployment_effect_in_1980[region] - 1 )
        idxlhs = fcol_in_mdf['Indicated_effect_of_worker_share_of_output_on_capital_labour_ratio']
        idx1 = fcol_in_mdf['Worker_share_of_output_with_unemployment_effect']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  +  Slope_of_Indicated_effect_of_worker_share_of_output_on_capital_labour_ratio  *  ( mdf[rowi , idx1:idx1 + 10] /  Worker_share_of_output_with_unemployment_effect_in_1980[0:10]  -  1  ) 
    
    # effect_of_worker_share_of_output_on_capital_labour_ratio[region] = SMOOTH ( Indicated_effect_of_worker_share_of_output_on_capital_labour_ratio[region] , Retooling_time )
        idx1 = fcol_in_mdf['effect_of_worker_share_of_output_on_capital_labour_ratio']
        idx2 = fcol_in_mdf['Indicated_effect_of_worker_share_of_output_on_capital_labour_ratio']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1+10] + ( mdf[rowi-1 , idx2:idx2 + 10] - mdf[rowi -1 , idx1:idx1 + 10]) / Retooling_time * dt
    
    # Capital_labour_ratio[region] = Capital_labour_ratio_in_1980[region] * np.exp ( RoC_in_Capital_labour_ratio[region] * ( zeit - 1980 ) ) * effect_of_worker_share_of_output_on_capital_labour_ratio[region]
        idxlhs = fcol_in_mdf['Capital_labour_ratio']
        idx1 = fcol_in_mdf['RoC_in_Capital_labour_ratio']
        idx2 = fcol_in_mdf['effect_of_worker_share_of_output_on_capital_labour_ratio']
        mdf[rowi, idxlhs:idxlhs + 10] =  Capital_labour_ratio_in_1980[0:10]  *  np.exp  ( mdf[rowi , idx1:idx1 + 10] *  (  zeit  -  1980  )  )  * mdf[rowi , idx2:idx2 + 10]
    
    # Theoretical_full_time_jobs_at_current_CLR[region] = ( Capacity[region] / Capital_labour_ratio[region] ) * UNIT_conv_to_Mp
        idxlhs = fcol_in_mdf['Theoretical_full_time_jobs_at_current_CLR']
        idx1 = fcol_in_mdf['Capacity']
        idx2 = fcol_in_mdf['Capital_labour_ratio']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10] )  *  UNIT_conv_to_Mp 
    
    # Max_people_in_labour_pool[region] = Population[region] * ( 1 - Fraction_of_people_outside_of_labour_market_FOPOLM[region] )
        idxlhs = fcol_in_mdf['Max_people_in_labour_pool']
        idx1 = fcol_in_mdf['Population']
        idx2 = fcol_in_mdf['Fraction_of_people_outside_of_labour_market_FOPOLM']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  1  - mdf[rowi , idx2:idx2 + 10] ) 
    
    # Full_time_jobs_with_participation_constraint[region] = MIN ( Theoretical_full_time_jobs_at_current_CLR[region] , Max_people_in_labour_pool[region] )
        idxlhs = fcol_in_mdf['Full_time_jobs_with_participation_constraint']
        idx1 = fcol_in_mdf['Theoretical_full_time_jobs_at_current_CLR']
        idx2 = fcol_in_mdf['Max_people_in_labour_pool']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.minimum  ( mdf[rowi , idx1:idx1 + 10] , mdf[rowi , idx2:idx2 + 10] ) 
    
    # Additional_people_required[region] = MAX ( 0 , Full_time_jobs_with_participation_constraint[region] - Employed[region] )
        idxlhs = fcol_in_mdf['Additional_people_required']
        idx1 = fcol_in_mdf['Full_time_jobs_with_participation_constraint']
        idx2 = fcol_in_mdf['Employed']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.maximum  (  0  , mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10] ) 
    
    # Future_shape_of_anthropogenic_aerosol_emissions = WITH LOOKUP ( zeit , ( [ ( 2015 , 0 ) - ( 2100 , 1 ) ] , ( 2015 , 1 ) , ( 2030 , 0.7 ) , ( 2050 , 0.5 ) , ( 2075 , 0.3 ) , ( 2100 , 0.1 ) ) )
        tabidx = ftab_in_d_table['Future_shape_of_anthropogenic_aerosol_emissions'] # fetch the correct table
        idxlhs = fcol_in_mdf['Future_shape_of_anthropogenic_aerosol_emissions'] # get the location of the lhs in mdf
        look = d_table[tabidx]
        valgt = GRAPH( zeit, look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # Historical_aerosol_emissions_anthro = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.24244 ) , ( 1981 , 0.252631 ) , ( 1982 , 0.255142 ) , ( 1983 , 0.258769 ) , ( 1984 , 0.262684 ) , ( 1985 , 0.264687 ) , ( 1986 , 0.267037 ) , ( 1987 , 0.270969 ) , ( 1988 , 0.274536 ) , ( 1989 , 0.276449 ) , ( 1990 , 0.277538 ) , ( 1991 , 0.276088 ) , ( 1992 , 0.275472 ) , ( 1993 , 0.274971 ) , ( 1994 , 0.272579 ) , ( 1995 , 0.267623 ) , ( 1996 , 0.261881 ) , ( 1997 , 0.264898 ) , ( 1998 , 0.274336 ) , ( 1999 , 0.281674 ) , ( 2000 , 0.2881 ) , ( 2001 , 0.291714 ) , ( 2002 , 0.291645 ) , ( 2003 , 0.292187 ) , ( 2004 , 0.293088 ) , ( 2005 , 0.292335 ) , ( 2006 , 0.288602 ) , ( 2007 , 0.283524 ) , ( 2008 , 0.278418 ) , ( 2009 , 0.273299 ) , ( 2010 , 0.267428 ) , ( 2011 , 0.260052 ) , ( 2012 , 0.251923 ) , ( 2013 , 0.243794 ) , ( 2014 , 0.235665 ) , ( 2015 , 0.227536 ) ) )
        tabidx = ftab_in_d_table['Historical_aerosol_emissions_anthro'] # fetch the correct table
        idxlhs = fcol_in_mdf['Historical_aerosol_emissions_anthro'] # get the location of the lhs in mdf
        look = d_table[tabidx]
        valgt = GRAPH( zeit, look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # Aerosol_anthropogenic_emissions = IF_THEN_ELSE ( zeit >= 2015 , Future_shape_of_anthropogenic_aerosol_emissions * Value_of_anthropogenic_aerosol_emissions_during_2015 , Historical_aerosol_emissions_anthro )
        idxlhs = fcol_in_mdf['Aerosol_anthropogenic_emissions']
        idx1 = fcol_in_mdf['Future_shape_of_anthropogenic_aerosol_emissions']
        idx2 = fcol_in_mdf['Historical_aerosol_emissions_anthro']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  (  zeit  >=  2015  , mdf[rowi, idx1] *  Value_of_anthropogenic_aerosol_emissions_during_2015  , mdf[rowi, idx2] ) 
    
    # Aging_14_to_15[region] = Cohort_10_to_14[region] / Cohort_duration_is_5_yrs
        idxlhs = fcol_in_mdf['Aging_14_to_15']
        idx1 = fcol_in_mdf['Cohort_10_to_14']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Cohort_duration_is_5_yrs 
    
    # Aging_19_to_20[region] = Cohort_15_to_19[region] / Cohort_duration_is_5_yrs
        idxlhs = fcol_in_mdf['Aging_19_to_20']
        idx1 = fcol_in_mdf['Cohort_15_to_19']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Cohort_duration_is_5_yrs 
    
    # Aging_24_to_25[region] = Cohort_20_to_24[region] / Cohort_duration_is_5_yrs
        idxlhs = fcol_in_mdf['Aging_24_to_25']
        idx1 = fcol_in_mdf['Cohort_20_to_24']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Cohort_duration_is_5_yrs 
    
    # Aging_29_to_30[region] = Cohort_25_to_29[region] / Cohort_duration_is_5_yrs
        idxlhs = fcol_in_mdf['Aging_29_to_30']
        idx1 = fcol_in_mdf['Cohort_25_to_29']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Cohort_duration_is_5_yrs 
    
    # Aging_34_to_35[region] = Cohort_30_to_34[region] / Cohort_duration_is_5_yrs
        idxlhs = fcol_in_mdf['Aging_34_to_35']
        idx1 = fcol_in_mdf['Cohort_30_to_34']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Cohort_duration_is_5_yrs 
    
    # Aging_39_to_40[region] = Cohort_35_to_39[region] / Cohort_duration_is_5_yrs
        idxlhs = fcol_in_mdf['Aging_39_to_40']
        idx1 = fcol_in_mdf['Cohort_35_to_39']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Cohort_duration_is_5_yrs 
    
    # Aging_4_to_5[region] = Cohort_0_to_4[region] / Cohort_duration_is_5_yrs
        idxlhs = fcol_in_mdf['Aging_4_to_5']
        idx1 = fcol_in_mdf['Cohort_0_to_4']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Cohort_duration_is_5_yrs 
    
    # Aging_44_to_45[region] = Cohort_40_to_44[region] / Cohort_duration_is_5_yrs
        idxlhs = fcol_in_mdf['Aging_44_to_45']
        idx1 = fcol_in_mdf['Cohort_40_to_44']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Cohort_duration_is_5_yrs 
    
    # Aging_49_to_50[region] = Cohort_45_to_49[region] / Cohort_duration_is_5_yrs
        idxlhs = fcol_in_mdf['Aging_49_to_50']
        idx1 = fcol_in_mdf['Cohort_45_to_49']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Cohort_duration_is_5_yrs 
    
    # Aging_54_to_55[region] = Cohort_50_to_54[region] / Cohort_duration_is_5_yrs
        idxlhs = fcol_in_mdf['Aging_54_to_55']
        idx1 = fcol_in_mdf['Cohort_50_to_54']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Cohort_duration_is_5_yrs 
    
    # Aging_59_to_60[region] = Cohort_55_to_59[region] / Cohort_duration_is_5_yrs
        idxlhs = fcol_in_mdf['Aging_59_to_60']
        idx1 = fcol_in_mdf['Cohort_55_to_59']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Cohort_duration_is_5_yrs 
    
    # Aging_64_to_65[region] = Cohort_60_to_64[region] / Cohort_duration_is_5_yrs
        idxlhs = fcol_in_mdf['Aging_64_to_65']
        idx1 = fcol_in_mdf['Cohort_60_to_64']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Cohort_duration_is_5_yrs 
    
    # Aging_69_to_70[region] = Cohort_65_to_69[region] / Cohort_duration_is_5_yrs
        idxlhs = fcol_in_mdf['Aging_69_to_70']
        idx1 = fcol_in_mdf['Cohort_65_to_69']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Cohort_duration_is_5_yrs 
    
    # Aging_74_to_75[region] = Cohort_70_to_74[region] / Cohort_duration_is_5_yrs
        idxlhs = fcol_in_mdf['Aging_74_to_75']
        idx1 = fcol_in_mdf['Cohort_70_to_74']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Cohort_duration_is_5_yrs 
    
    # Aging_79_to_80[region] = Cohort_75_to_79[region] / Cohort_duration_is_5_yrs
        idxlhs = fcol_in_mdf['Aging_79_to_80']
        idx1 = fcol_in_mdf['Cohort_75_to_79']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Cohort_duration_is_5_yrs 
    
    # Aging_84_to_85[region] = Cohort_80_to_84[region] / Cohort_duration_is_5_yrs
        idxlhs = fcol_in_mdf['Aging_84_to_85']
        idx1 = fcol_in_mdf['Cohort_80_to_84']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Cohort_duration_is_5_yrs 
    
    # Aging_89_to_90[region] = Cohort_85_to_89[region] / Cohort_duration_is_5_yrs
        idxlhs = fcol_in_mdf['Aging_89_to_90']
        idx1 = fcol_in_mdf['Cohort_85_to_89']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Cohort_duration_is_5_yrs 
    
    # Aging_9_to_10[region] = Cohort_5_to_9[region] / Cohort_duration_is_5_yrs
        idxlhs = fcol_in_mdf['Aging_9_to_10']
        idx1 = fcol_in_mdf['Cohort_5_to_9']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Cohort_duration_is_5_yrs 
    
    # Aging_95_to_95plus[region] = Cohort_90_to_94[region] / Cohort_duration_is_5_yrs
        idxlhs = fcol_in_mdf['Aging_95_to_95plus']
        idx1 = fcol_in_mdf['Cohort_90_to_94']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Cohort_duration_is_5_yrs 
    
    # Smoothed_Urban_aerosol_concentration_future = SMOOTH3I ( Urban_aerosol_concentration_future , Time_to_smooth_UAC , Urban_aerosol_concentration_in_2020 )
        idxlhs = fcol_in_mdf['Smoothed_Urban_aerosol_concentration_future']
        idxin = fcol_in_mdf['Urban_aerosol_concentration_future']
        idx2 = fcol_in_mdf['Smoothed_Urban_aerosol_concentration_future_2']
        idx1 = fcol_in_mdf['Smoothed_Urban_aerosol_concentration_future_1']
        idxout = fcol_in_mdf['Smoothed_Urban_aerosol_concentration_future']
        mdf[rowi, idxout] = mdf[rowi-1, idxout] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idxout]) / ( Time_to_smooth_UAC / 3) * dt
        mdf[rowi, idx2] = mdf[rowi-1, idx2] + ( mdf[rowi-1, idx1] - mdf[rowi-1, idx2]) / ( Time_to_smooth_UAC / 3) * dt
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idxin] - mdf[rowi-1, idx1]) / ( Time_to_smooth_UAC / 3) * dt
    
    # Air_Pollution_risk_score = IF_THEN_ELSE ( Smoothed_Urban_aerosol_concentration_future > pb_Urban_aerosol_concentration_green_threshold , 1 , 0 )
        idxlhs = fcol_in_mdf['Air_Pollution_risk_score']
        idx1 = fcol_in_mdf['Smoothed_Urban_aerosol_concentration_future']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  ( mdf[rowi, idx1] >  pb_Urban_aerosol_concentration_green_threshold  ,  1  ,  0  ) 
    
    # Urban_area_fraction = MAX ( 0 , MIN ( 1 , Global_population_in_Bp / Population_2000_bn * Urban_area_fraction_2000 ) )
        idxlhs = fcol_in_mdf['Urban_area_fraction']
        idx1 = fcol_in_mdf['Global_population_in_Bp']
        mdf[rowi, idxlhs] =  np.maximum  (  0  ,  np.minimum  (  1  , mdf[rowi, idx1] /  Population_2000_bn  *  Urban_area_fraction_2000  )  ) 
    
    # Urban_Mkm2 = Area_of_earth_Mkm2 * ( 1 - Fraction_of_earth_surface_as_ocean ) * Urban_area_fraction
        idxlhs = fcol_in_mdf['Urban_Mkm2']
        idx1 = fcol_in_mdf['Urban_area_fraction']
        mdf[rowi, idxlhs] =  Area_of_earth_Mkm2  *  (  1  -  Fraction_of_earth_surface_as_ocean  )  * mdf[rowi, idx1]
    
    # Antarctic_ice_area_km2 = Antarctic_ice_volume_km3 / Avg_thickness_Antarctic_km * UNIT_Conversion_from_km3_to_km2
        idxlhs = fcol_in_mdf['Antarctic_ice_area_km2']
        idx1 = fcol_in_mdf['Antarctic_ice_volume_km3']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Avg_thickness_Antarctic_km  *  UNIT_Conversion_from_km3_to_km2 
    
    # Glacial_ice_area_km2 = Glacial_ice_volume_km3 / Avg_thickness_glacier_km * UNIT_conversion_km3_div_km_to_km2
        idxlhs = fcol_in_mdf['Glacial_ice_area_km2']
        idx1 = fcol_in_mdf['Glacial_ice_volume_km3']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Avg_thickness_glacier_km  *  UNIT_conversion_km3_div_km_to_km2 
    
    # Greenland_ice_area_km2 = ( Greenland_ice_volume_on_Greenland_km3 / Avg_thickness_Greenland_km ) * UNIT_Conversion_from_km3_to_km2
        idxlhs = fcol_in_mdf['Greenland_ice_area_km2']
        idx1 = fcol_in_mdf['Greenland_ice_volume_on_Greenland_km3']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] /  Avg_thickness_Greenland_km  )  *  UNIT_Conversion_from_km3_to_km2 
    
    # Land_covered_with_ice_km2 = Antarctic_ice_area_km2 + Glacial_ice_area_km2 + Greenland_ice_area_km2
        idxlhs = fcol_in_mdf['Land_covered_with_ice_km2']
        idx1 = fcol_in_mdf['Antarctic_ice_area_km2']
        idx2 = fcol_in_mdf['Glacial_ice_area_km2']
        idx3 = fcol_in_mdf['Greenland_ice_area_km2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3]
    
    # Sum_biomes_Mkm2 = Land_covered_with_ice_km2 * UNIT_conversion_km2_to_Mkm2 + Tundra_potential_area_Mkm2 + NF_potential_area_Mkm2 + DESERT_Mkm2 + GRASS_potential_area_Mkm2 + TROP_potential_area_Mkm2
        idxlhs = fcol_in_mdf['Sum_biomes_Mkm2']
        idx1 = fcol_in_mdf['Land_covered_with_ice_km2']
        idx2 = fcol_in_mdf['Tundra_potential_area_Mkm2']
        idx3 = fcol_in_mdf['NF_potential_area_Mkm2']
        idx4 = fcol_in_mdf['DESERT_Mkm2']
        idx5 = fcol_in_mdf['GRASS_potential_area_Mkm2']
        idx6 = fcol_in_mdf['TROP_potential_area_Mkm2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  UNIT_conversion_km2_to_Mkm2  + mdf[rowi, idx2] + mdf[rowi, idx3] + mdf[rowi, idx4] + mdf[rowi, idx5] + mdf[rowi, idx6]
    
    # Barren_land_Mkm2 = Area_of_earth_Mkm2 * ( 1 - Fraction_of_earth_surface_as_ocean ) - Urban_Mkm2 - Sum_biomes_Mkm2
        idxlhs = fcol_in_mdf['Barren_land_Mkm2']
        idx1 = fcol_in_mdf['Urban_Mkm2']
        idx2 = fcol_in_mdf['Sum_biomes_Mkm2']
        mdf[rowi, idxlhs] =  Area_of_earth_Mkm2  *  (  1  -  Fraction_of_earth_surface_as_ocean  )  - mdf[rowi, idx1] - mdf[rowi, idx2]
    
    # BARREN_land_normal_albedo_Mkm2 = Barren_land_Mkm2
        idxlhs = fcol_in_mdf['BARREN_land_normal_albedo_Mkm2']
        idx1 = fcol_in_mdf['Barren_land_Mkm2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # Contrib_of_BARREN_land_to_albedo_land = BARREN_land_normal_albedo_Mkm2 / Area_of_land_Mkm2 * Albedo_BARREN_normal
        idxlhs = fcol_in_mdf['Contrib_of_BARREN_land_to_albedo_land']
        idx1 = fcol_in_mdf['BARREN_land_normal_albedo_Mkm2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Area_of_land_Mkm2  *  Albedo_BARREN_normal 
    
    # Contrib_of_GRASS_to_albedo_land = ( GRASS_potential_area_Mkm2 - GRASS_area_burnt_Mkm2 - GRASS_deforested_Mkm2 ) / Area_of_land_Mkm2 * Albedo_GRASS_normal_cover + GRASS_area_burnt_Mkm2 / Area_of_land_Mkm2 * Albedo_GRASS_burnt + GRASS_deforested_Mkm2 / Area_of_land_Mkm2 * Albedo_GRASS_deforested
        idxlhs = fcol_in_mdf['Contrib_of_GRASS_to_albedo_land']
        idx1 = fcol_in_mdf['GRASS_potential_area_Mkm2']
        idx2 = fcol_in_mdf['GRASS_area_burnt_Mkm2']
        idx3 = fcol_in_mdf['GRASS_deforested_Mkm2']
        idx4 = fcol_in_mdf['GRASS_area_burnt_Mkm2']
        idx5 = fcol_in_mdf['GRASS_deforested_Mkm2']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] - mdf[rowi, idx2] - mdf[rowi, idx3] )  /  Area_of_land_Mkm2  *  Albedo_GRASS_normal_cover  + mdf[rowi, idx4] /  Area_of_land_Mkm2  *  Albedo_GRASS_burnt  + mdf[rowi, idx5] /  Area_of_land_Mkm2  *  Albedo_GRASS_deforested 
    
    # Contrib_of_ICE_ON_LAND_to_albedo_land = Antarctic_ice_area_km2 * Conversion_Million_km2_to_km2 / Area_of_land_Mkm2 * Albedo_Antarctic + Glacial_ice_area_km2 * Conversion_Million_km2_to_km2 / Area_of_land_Mkm2 * Albedo_glacier + Greenland_ice_area_km2 * Conversion_Million_km2_to_km2 / Area_of_land_Mkm2 * Albedo_Greenland
        idxlhs = fcol_in_mdf['Contrib_of_ICE_ON_LAND_to_albedo_land']
        idx1 = fcol_in_mdf['Antarctic_ice_area_km2']
        idx2 = fcol_in_mdf['Glacial_ice_area_km2']
        idx3 = fcol_in_mdf['Greenland_ice_area_km2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Conversion_Million_km2_to_km2  /  Area_of_land_Mkm2  *  Albedo_Antarctic  + mdf[rowi, idx2] *  Conversion_Million_km2_to_km2  /  Area_of_land_Mkm2  *  Albedo_glacier  + mdf[rowi, idx3] *  Conversion_Million_km2_to_km2  /  Area_of_land_Mkm2  *  Albedo_Greenland 
    
    # Contrib_of_NF_to_albedo_land = ( NF_potential_area_Mkm2 - NF_area_burnt_Mkm2 - NF_area_deforested_Mkm2 - NF_area_clear_cut_Mkm2 ) / Area_of_land_Mkm2 * Albedo_NF_normal_cover + NF_area_burnt_Mkm2 / Area_of_land_Mkm2 * Albedo_NF_burnt + NF_area_deforested_Mkm2 / Area_of_land_Mkm2 * Albedo_NF_deforested + NF_area_clear_cut_Mkm2 / Area_of_land_Mkm2 * Albedo_NF_deforested
        idxlhs = fcol_in_mdf['Contrib_of_NF_to_albedo_land']
        idx1 = fcol_in_mdf['NF_potential_area_Mkm2']
        idx2 = fcol_in_mdf['NF_area_burnt_Mkm2']
        idx3 = fcol_in_mdf['NF_area_deforested_Mkm2']
        idx4 = fcol_in_mdf['NF_area_clear_cut_Mkm2']
        idx5 = fcol_in_mdf['NF_area_burnt_Mkm2']
        idx6 = fcol_in_mdf['NF_area_deforested_Mkm2']
        idx7 = fcol_in_mdf['NF_area_clear_cut_Mkm2']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] - mdf[rowi, idx2] - mdf[rowi, idx3] - mdf[rowi, idx4] )  /  Area_of_land_Mkm2  *  Albedo_NF_normal_cover  + mdf[rowi, idx5] /  Area_of_land_Mkm2  *  Albedo_NF_burnt  + mdf[rowi, idx6] /  Area_of_land_Mkm2  *  Albedo_NF_deforested  + mdf[rowi, idx7] /  Area_of_land_Mkm2  *  Albedo_NF_deforested 
    
    # Contrib_of_TROP_to_albedo_land = ( TROP_potential_area_Mkm2 - TROP_area_burnt - TROP_area_deforested ) / Area_of_land_Mkm2 * Albedo_TROP_normal_cover + TROP_area_burnt / Area_of_land_Mkm2 * Albedo_TROP_burnt + TROP_area_deforested / Area_of_land_Mkm2 * Albedo_TROP_deforested + TROP_area_clear_cut / Area_of_land_Mkm2 * Albedo_TROP_deforested
        idxlhs = fcol_in_mdf['Contrib_of_TROP_to_albedo_land']
        idx1 = fcol_in_mdf['TROP_potential_area_Mkm2']
        idx2 = fcol_in_mdf['TROP_area_burnt']
        idx3 = fcol_in_mdf['TROP_area_deforested']
        idx4 = fcol_in_mdf['TROP_area_burnt']
        idx5 = fcol_in_mdf['TROP_area_deforested']
        idx6 = fcol_in_mdf['TROP_area_clear_cut']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] - mdf[rowi, idx2] - mdf[rowi, idx3] )  /  Area_of_land_Mkm2  *  Albedo_TROP_normal_cover  + mdf[rowi, idx4] /  Area_of_land_Mkm2  *  Albedo_TROP_burnt  + mdf[rowi, idx5] /  Area_of_land_Mkm2  *  Albedo_TROP_deforested  + mdf[rowi, idx6] /  Area_of_land_Mkm2  *  Albedo_TROP_deforested 
    
    # Contrib_of_TUNDRA_to_albedo_land = ( Tundra_potential_area_Mkm2 - TUNDRA_area_burnt_Mkm2 - TUNDRA_deforested_Mkm2 ) / Area_of_land_Mkm2 * Albedo_TUNDRA_normal_cover + TUNDRA_area_burnt_Mkm2 / Area_of_land_Mkm2 * Albedo_TUNDRA_burnt + TUNDRA_deforested_Mkm2 / Area_of_land_Mkm2 * Albedo_TUNDRA_deforested
        idxlhs = fcol_in_mdf['Contrib_of_TUNDRA_to_albedo_land']
        idx1 = fcol_in_mdf['Tundra_potential_area_Mkm2']
        idx2 = fcol_in_mdf['TUNDRA_area_burnt_Mkm2']
        idx3 = fcol_in_mdf['TUNDRA_deforested_Mkm2']
        idx4 = fcol_in_mdf['TUNDRA_area_burnt_Mkm2']
        idx5 = fcol_in_mdf['TUNDRA_deforested_Mkm2']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] - mdf[rowi, idx2] - mdf[rowi, idx3] )  /  Area_of_land_Mkm2  *  Albedo_TUNDRA_normal_cover  + mdf[rowi, idx4] /  Area_of_land_Mkm2  *  Albedo_TUNDRA_burnt  + mdf[rowi, idx5] /  Area_of_land_Mkm2  *  Albedo_TUNDRA_deforested 
    
    # Albedo_land_biomes = Contrib_of_BARREN_land_to_albedo_land + Albedo_DESERT_normal * DESERT_Mkm2 / Area_of_land_Mkm2 + Contrib_of_GRASS_to_albedo_land + Contrib_of_ICE_ON_LAND_to_albedo_land + Contrib_of_NF_to_albedo_land + Contrib_of_TROP_to_albedo_land + Contrib_of_TUNDRA_to_albedo_land + Albedo_URBAN * Urban_Mkm2 / Area_of_land_Mkm2
        idxlhs = fcol_in_mdf['Albedo_land_biomes']
        idx1 = fcol_in_mdf['Contrib_of_BARREN_land_to_albedo_land']
        idx2 = fcol_in_mdf['DESERT_Mkm2']
        idx3 = fcol_in_mdf['Contrib_of_GRASS_to_albedo_land']
        idx4 = fcol_in_mdf['Contrib_of_ICE_ON_LAND_to_albedo_land']
        idx5 = fcol_in_mdf['Contrib_of_NF_to_albedo_land']
        idx6 = fcol_in_mdf['Contrib_of_TROP_to_albedo_land']
        idx7 = fcol_in_mdf['Contrib_of_TUNDRA_to_albedo_land']
        idx8 = fcol_in_mdf['Urban_Mkm2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] +  Albedo_DESERT_normal  * mdf[rowi, idx2] /  Area_of_land_Mkm2  + mdf[rowi, idx3] + mdf[rowi, idx4] + mdf[rowi, idx5] + mdf[rowi, idx6] + mdf[rowi, idx7] +  Albedo_URBAN  * mdf[rowi, idx8] /  Area_of_land_Mkm2 
    
    # Arctic_as_fraction_of_ocean = Arctic_ice_on_sea_area_km2 / Ocean_area_km2
        idxlhs = fcol_in_mdf['Arctic_as_fraction_of_ocean']
        idx1 = fcol_in_mdf['Arctic_ice_on_sea_area_km2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Ocean_area_km2 
    
    # Open_water_as_frac_of_ocean_area = 1 - ( Arctic_ice_on_sea_area_km2 / Ocean_area_km2 )
        idxlhs = fcol_in_mdf['Open_water_as_frac_of_ocean_area']
        idx1 = fcol_in_mdf['Arctic_ice_on_sea_area_km2']
        mdf[rowi, idxlhs] =  1  -  ( mdf[rowi, idx1] /  Ocean_area_km2  ) 
    
    # Albedo_ocean_with_arctic_ice_changes = Arctic_ice_albedo_1850 * Arctic_as_fraction_of_ocean + Open_ocean_albedo * Open_water_as_frac_of_ocean_area
        idxlhs = fcol_in_mdf['Albedo_ocean_with_arctic_ice_changes']
        idx1 = fcol_in_mdf['Arctic_as_fraction_of_ocean']
        idx2 = fcol_in_mdf['Open_water_as_frac_of_ocean_area']
        mdf[rowi, idxlhs] =  Arctic_ice_albedo_1850  * mdf[rowi, idx1] +  Open_ocean_albedo  * mdf[rowi, idx2]
    
    # all_crop_not_wasted_pp[region] = ( cereal_dmd_food_pp_consumed[region] + oth_crop_dmd_food_pp_consumed[region] ) * UNIT_conv_kgac_to_kg
        idxlhs = fcol_in_mdf['all_crop_not_wasted_pp']
        idx1 = fcol_in_mdf['cereal_dmd_food_pp_consumed']
        idx2 = fcol_in_mdf['oth_crop_dmd_food_pp_consumed']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] )  *  UNIT_conv_kgac_to_kg 
     
    # Global_Total_CO2_emissions = SUM ( Total_CO2_emissions[region!] )
        idxlhs = fcol_in_mdf['Global_Total_CO2_emissions']
        idx1 = fcol_in_mdf['Total_CO2_emissions']
        globsum = 0
        for j in range(0,10):
            globsum = globsum + mdf[rowi, idx1 + j]
        mdf[rowi, idxlhs] = globsum 
    
    # Global_Total_CO2_emissions_GtC_py = Global_Total_CO2_emissions / UNIT_conv_CO2_to_C
        idxlhs = fcol_in_mdf['Global_Total_CO2_emissions_GtC_py']
        idx1 = fcol_in_mdf['Global_Total_CO2_emissions']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  UNIT_conv_CO2_to_C 
    
    # Emissions_of_CO2_1850_to_2100_GtC_py = Global_Total_CO2_emissions_GtC_py
        idxlhs = fcol_in_mdf['Emissions_of_CO2_1850_to_2100_GtC_py']
        idx1 = fcol_in_mdf['Global_Total_CO2_emissions_GtC_py']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # Fossil_fuel_reserves_in_ground_current_to_inital_ratio = Fossil_fuel_reserves_in_ground_GtC / Fossil_fuel_reserves_in_ground_at_initial_time_GtC
        idxlhs = fcol_in_mdf['Fossil_fuel_reserves_in_ground_current_to_inital_ratio']
        idx1 = fcol_in_mdf['Fossil_fuel_reserves_in_ground_GtC']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Fossil_fuel_reserves_in_ground_at_initial_time_GtC 
    
    # RCPFossil_fuel_usage_cutoff = WITH LOOKUP ( Fossil_fuel_reserves_in_ground_current_to_inital_ratio , ( [ ( 0 , 0 ) - ( 1 , 1 ) ] , ( 0 , 0 ) , ( 0.25 , 0.657895 ) , ( 0.5 , 0.881579 ) , ( 0.75 , 0.960526 ) , ( 1 , 1 ) ) )
        tabidx = ftab_in_d_table['RCPFossil_fuel_usage_cutoff'] # fetch the correct table
        idxlhs = fcol_in_mdf['RCPFossil_fuel_usage_cutoff'] # get the location of the lhs in mdf
        idx1 = fcol_in_mdf['Fossil_fuel_reserves_in_ground_current_to_inital_ratio']
        look = d_table[tabidx]
        valgt = GRAPH(mdf[rowi,  idx1], look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # CO2_emissions_before_co2e_exp = Emissions_of_CO2_1850_to_2100_GtC_py * RCPFossil_fuel_usage_cutoff
        idxlhs = fcol_in_mdf['CO2_emissions_before_co2e_exp']
        idx1 = fcol_in_mdf['Emissions_of_CO2_1850_to_2100_GtC_py']
        idx2 = fcol_in_mdf['RCPFossil_fuel_usage_cutoff']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2]
    
    # Man_made_fossil_C_emissions_GtC_py = CO2_emissions_before_co2e_exp
        idxlhs = fcol_in_mdf['Man_made_fossil_C_emissions_GtC_py']
        idx1 = fcol_in_mdf['CO2_emissions_before_co2e_exp']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # Man_made_fossil_C_emissions_GtCO2e_py = Man_made_fossil_C_emissions_GtC_py / UNIT_conversion_for_CO2_from_CO2e_to_C
        idxlhs = fcol_in_mdf['Man_made_fossil_C_emissions_GtCO2e_py']
        idx1 = fcol_in_mdf['Man_made_fossil_C_emissions_GtC_py']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  UNIT_conversion_for_CO2_from_CO2e_to_C 
    
    # CH4_emi_from_agriculture[region] = MAX ( 0 , CH4_emi_from_agriculture_a[region] * LN ( Red_meat_production[region] / UNIT_conv_Mtrmeat ) + CH4_emi_from_agriculture_b[region] )
        idxlhs = fcol_in_mdf['CH4_emi_from_agriculture']
        idx1 = fcol_in_mdf['Red_meat_production']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.maximum  (  0  ,  CH4_emi_from_agriculture_a[0:10]  *  np.log  ( mdf[rowi , idx1:idx1 + 10] /  UNIT_conv_Mtrmeat  )  +  CH4_emi_from_agriculture_b[0:10]  ) 
     
    # Global_CH4_emi_from_agriculture = SUM ( CH4_emi_from_agriculture[region!] )
        idxlhs = fcol_in_mdf['Global_CH4_emi_from_agriculture']
        idx1 = fcol_in_mdf['CH4_emi_from_agriculture']
        globsum = 0
        for j in range(0,10):
            globsum = globsum + mdf[rowi, idx1 + j]
        mdf[rowi, idxlhs] = globsum 
    
    # CH4_emi_from_energy_EU = CH4_emi_from_energy_EU_a * np.exp ( GDPpp_USED[eu] * UNIT_conv_to_make_exp_dmnl * CH4_emi_from_energy_EU_b )
        idxlhs = fcol_in_mdf['CH4_emi_from_energy_EU']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs] =  CH4_emi_from_energy_EU_a  *  np.exp  ( mdf[rowi, idx1 + 8] *  UNIT_conv_to_make_exp_dmnl  *  CH4_emi_from_energy_EU_b  ) 
    
    # CH4_emi_from_energy_US = CH4_emi_from_energy_US_a * np.exp ( GDPpp_USED[us] * UNIT_conv_to_make_exp_dmnl * CH4_emi_from_energy_US_b )
        idxlhs = fcol_in_mdf['CH4_emi_from_energy_US']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs] =  CH4_emi_from_energy_US_a  *  np.exp  ( mdf[rowi, idx1 + 0] *  UNIT_conv_to_make_exp_dmnl  *  CH4_emi_from_energy_US_b  ) 
    
    # CH4_emi_from_energy_EC = MAX ( 0 , CH4_emi_from_energy_EC_a * LN ( Total_use_of_fossil_fuels[ec] / UNIT_conv_to_make_fossil_fuels_dmnl ) + CH4_emi_from_energy_EC_b )
        idxlhs = fcol_in_mdf['CH4_emi_from_energy_EC']
        idx1 = fcol_in_mdf['Total_use_of_fossil_fuels']
        mdf[rowi, idxlhs] =  np.maximum  (  0  ,  CH4_emi_from_energy_EC_a  *  np.log  ( mdf[rowi, idx1 + 7] /  UNIT_conv_to_make_fossil_fuels_dmnl  )  +  CH4_emi_from_energy_EC_b  ) 
    
    # CH4_emi_from_energy_WO_US_EC_EU[region] = CH4_emi_from_energy_a[region] * ( Total_use_of_fossil_fuels[region] / UNIT_conv_to_make_fossil_fuels_dmnl ) ^ CH4_emi_from_energy_b[region]
        idxlhs = fcol_in_mdf['CH4_emi_from_energy_WO_US_EC_EU']
        idx1 = fcol_in_mdf['Total_use_of_fossil_fuels']
        mdf[rowi, idxlhs:idxlhs + 10] =  CH4_emi_from_energy_a[0:10]  *  ( mdf[rowi , idx1:idx1 + 10] /  UNIT_conv_to_make_fossil_fuels_dmnl  )  **  CH4_emi_from_energy_b[0:10] 
    
    # CH4_emi_from_energy = IF_THEN_ELSE ( j==8 , CH4_emi_from_energy_EU , IF_THEN_ELSE ( j==0 , CH4_emi_from_energy_US , IF_THEN_ELSE ( j==7 , CH4_emi_from_energy_EC , CH4_emi_from_energy_WO_US_EC_EU ) ) )
        idxlhs = fcol_in_mdf['CH4_emi_from_energy']
        idx1 = fcol_in_mdf['CH4_emi_from_energy_EU']
        idx2 = fcol_in_mdf['CH4_emi_from_energy_US']
        idx3 = fcol_in_mdf['CH4_emi_from_energy_EC']
        idx4 = fcol_in_mdf['CH4_emi_from_energy_WO_US_EC_EU']
        for j in range(0,10):
            mdf[rowi, idxlhs + j] =  IF_THEN_ELSE  (  j==8  , mdf[rowi , idx1] ,  IF_THEN_ELSE  (  j==0  , mdf[rowi , idx2] ,  IF_THEN_ELSE  (  j==7  , mdf[rowi , idx3] , mdf[rowi , idx4 + j] )  )  ) 
     
    # Global_CH4_emi_from_energy = SUM ( CH4_emi_from_energy[region!] )
        idxlhs = fcol_in_mdf['Global_CH4_emi_from_energy']
        idx1 = fcol_in_mdf['CH4_emi_from_energy']
        globsum = 0
        for j in range(0,10):
            globsum = globsum + mdf[rowi, idx1 + j]
        mdf[rowi, idxlhs] = globsum 
    
    # CH4_emi_from_waste_AF = CH4_emi_from_waste_AF_a * ( GDPpp_USED[af] * UNIT_conv_to_make_exp_dmnl ) ^ CH4_emi_from_waste_AF_b
        idxlhs = fcol_in_mdf['CH4_emi_from_waste_AF']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs] =  CH4_emi_from_waste_AF_a  *  ( mdf[rowi, idx1 + 1] *  UNIT_conv_to_make_exp_dmnl  )  **  CH4_emi_from_waste_AF_b 
    
    # CH4_emi_from_waste_CN = CH4_emi_from_waste_CN_a * ( GDPpp_USED[cn] * UNIT_conv_to_make_exp_dmnl ) ^ CH4_emi_from_waste_CN_b
        idxlhs = fcol_in_mdf['CH4_emi_from_waste_CN']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs] =  CH4_emi_from_waste_CN_a  *  ( mdf[rowi, idx1 + 2] *  UNIT_conv_to_make_exp_dmnl  )  **  CH4_emi_from_waste_CN_b 
    
    # CH4_emi_from_waste_WO_CN_AF[region] = CH4_emi_from_waste_a[region] * LN ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl ) + CH4_emi_from_waste_b[region]
        idxlhs = fcol_in_mdf['CH4_emi_from_waste_WO_CN_AF']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  CH4_emi_from_waste_a[0:10]  *  np.log  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  )  +  CH4_emi_from_waste_b[0:10] 
    
    # CH4_emi_from_waste = IF_THEN_ELSE ( j==1 , CH4_emi_from_waste_AF , IF_THEN_ELSE ( j==2 , CH4_emi_from_waste_CN , CH4_emi_from_waste_WO_CN_AF ) )
        idxlhs = fcol_in_mdf['CH4_emi_from_waste']
        idx1 = fcol_in_mdf['CH4_emi_from_waste_AF']
        idx2 = fcol_in_mdf['CH4_emi_from_waste_CN']
        idx3 = fcol_in_mdf['CH4_emi_from_waste_WO_CN_AF']
        for j in range(0,10):
            mdf[rowi, idxlhs + j] =  IF_THEN_ELSE  (  j==1  , mdf[rowi , idx1] ,  IF_THEN_ELSE  (  j==2  , mdf[rowi , idx2] , mdf[rowi , idx3 + j] )  ) 
     
    # Global_CH4_emi_from_waste = SUM ( CH4_emi_from_waste[region!] )
        idxlhs = fcol_in_mdf['Global_CH4_emi_from_waste']
        idx1 = fcol_in_mdf['CH4_emi_from_waste']
        globsum = 0
        for j in range(0,10):
            globsum = globsum + mdf[rowi, idx1 + j]
        mdf[rowi, idxlhs] = globsum 
    
    # Global_CH4_emissions = Global_CH4_emi_from_agriculture + Global_CH4_emi_from_energy + Global_CH4_emi_from_waste
        idxlhs = fcol_in_mdf['Global_CH4_emissions']
        idx1 = fcol_in_mdf['Global_CH4_emi_from_agriculture']
        idx2 = fcol_in_mdf['Global_CH4_emi_from_energy']
        idx3 = fcol_in_mdf['Global_CH4_emi_from_waste']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3]
    
    # Global_CH4_emissions_GtC_py = Global_CH4_emissions * UNIT_conversion_from_MtCH4_to_GtC
        idxlhs = fcol_in_mdf['Global_CH4_emissions_GtC_py']
        idx1 = fcol_in_mdf['Global_CH4_emissions']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  UNIT_conversion_from_MtCH4_to_GtC 
    
    # Human_activity_CH4_emissions = Global_CH4_emissions_GtC_py
        idxlhs = fcol_in_mdf['Human_activity_CH4_emissions']
        idx1 = fcol_in_mdf['Global_CH4_emissions_GtC_py']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # Human_activity_CH4_emissions_GtCO2e_py = Human_activity_CH4_emissions / UNIT_conversion_for_CH4_from_CO2e_to_C
        idxlhs = fcol_in_mdf['Human_activity_CH4_emissions_GtCO2e_py']
        idx1 = fcol_in_mdf['Human_activity_CH4_emissions']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  UNIT_conversion_for_CH4_from_CO2e_to_C 
    
    # Nitrogen_syn_use[region] = Cropland[region] * Nitrogen_use_after_soil_regeneration[region] * UNIT_conv_to_MtN
        idxlhs = fcol_in_mdf['Nitrogen_syn_use']
        idx1 = fcol_in_mdf['Cropland']
        idx2 = fcol_in_mdf['Nitrogen_use_after_soil_regeneration']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] *  UNIT_conv_to_MtN 
    
    # Red_and_White_meat_production[region] = Meat_production[region]
        idxlhs = fcol_in_mdf['Red_and_White_meat_production']
        idx1 = fcol_in_mdf['Meat_production']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10]
    
    # N_excreted_AF = N_excreted_a[af] * np.exp ( Red_and_White_meat_production[af] / UNIT_conv_to_dmnl_for_MtNmeat * N_excreted_b[af] )
        idxlhs = fcol_in_mdf['N_excreted_AF']
        idx1 = fcol_in_mdf['Red_and_White_meat_production']
        mdf[rowi, idxlhs] =  N_excreted_a[1]  *  np.exp  ( mdf[rowi, idx1 + 1] /  UNIT_conv_to_dmnl_for_MtNmeat  *  N_excreted_b[1]  ) 
    
    # N_excreted_CN = N_excreted_a[cn] * np.exp ( Red_and_White_meat_production[cn] / UNIT_conv_to_dmnl_for_MtNmeat * N_excreted_b[cn] )
        idxlhs = fcol_in_mdf['N_excreted_CN']
        idx1 = fcol_in_mdf['Red_and_White_meat_production']
        mdf[rowi, idxlhs] =  N_excreted_a[2]  *  np.exp  ( mdf[rowi, idx1 + 2] /  UNIT_conv_to_dmnl_for_MtNmeat  *  N_excreted_b[2]  ) 
    
    # N_excreted_without_AF_CN[region] = N_excreted_a[region] * ( Red_and_White_meat_production[region] / UNIT_conv_to_dmnl_for_MtNmeat ) ^ N_excreted_b[region]
        idxlhs = fcol_in_mdf['N_excreted_without_AF_CN']
        idx1 = fcol_in_mdf['Red_and_White_meat_production']
        mdf[rowi, idxlhs:idxlhs + 10] =  N_excreted_a[0:10]  *  ( mdf[rowi , idx1:idx1 + 10] /  UNIT_conv_to_dmnl_for_MtNmeat  )  **  N_excreted_b[0:10] 
    
    # N_excreted_per_unit_of_meat_production_func = IF_THEN_ELSE ( j==1 , N_excreted_AF , IF_THEN_ELSE ( j==2 , N_excreted_CN , N_excreted_without_AF_CN ) )
        idxlhs = fcol_in_mdf['N_excreted_per_unit_of_meat_production_func']
        idx1 = fcol_in_mdf['N_excreted_AF']
        idx2 = fcol_in_mdf['N_excreted_CN']
        idx3 = fcol_in_mdf['N_excreted_without_AF_CN']
        for j in range(0,10):
            mdf[rowi, idxlhs + j] =  IF_THEN_ELSE  (  j==1  , mdf[rowi , idx1] ,  IF_THEN_ELSE  (  j==2  , mdf[rowi , idx2] , mdf[rowi , idx3 + j] )  ) 
    
    # N_excreted_per_unit_of_meat_production[region] = N_excreted_per_unit_of_meat_production_func[region] * UNIT_conv_to_MtN_from_meat
        idxlhs = fcol_in_mdf['N_excreted_per_unit_of_meat_production']
        idx1 = fcol_in_mdf['N_excreted_per_unit_of_meat_production_func']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_MtN_from_meat 
    
    # N_excreted_on_pasture[region] = Red_and_White_meat_production[region] * N_excreted_per_unit_of_meat_production[region]
        idxlhs = fcol_in_mdf['N_excreted_on_pasture']
        idx1 = fcol_in_mdf['Red_and_White_meat_production']
        idx2 = fcol_in_mdf['N_excreted_per_unit_of_meat_production']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # All_N_use_syn_and_excreted[region] = Nitrogen_syn_use[region] + N_excreted_on_pasture[region]
        idxlhs = fcol_in_mdf['All_N_use_syn_and_excreted']
        idx1 = fcol_in_mdf['Nitrogen_syn_use']
        idx2 = fcol_in_mdf['N_excreted_on_pasture']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10]
    
    # N2O_emi_from_agri_AF = N2O_emi_from_agri_AF_a * LN ( All_N_use_syn_and_excreted[af] / UNIT_conv_to_make_LN_dmnl ) + N2O_emi_from_agri_AF_b
        idxlhs = fcol_in_mdf['N2O_emi_from_agri_AF']
        idx1 = fcol_in_mdf['All_N_use_syn_and_excreted']
        mdf[rowi, idxlhs] =  N2O_emi_from_agri_AF_a  *  np.log  ( mdf[rowi, idx1 + 1] /  UNIT_conv_to_make_LN_dmnl  )  +  N2O_emi_from_agri_AF_b 
    
    # N2O_emi_from_agri_X_AF[region] = N2O_emi_from_agri_a[region] * All_N_use_syn_and_excreted[region] + N2O_emi_from_agri_b[region]
        idxlhs = fcol_in_mdf['N2O_emi_from_agri_X_AF']
        idx1 = fcol_in_mdf['All_N_use_syn_and_excreted']
        mdf[rowi, idxlhs:idxlhs + 10] =  N2O_emi_from_agri_a[0:10]  * mdf[rowi , idx1:idx1 + 10] +  N2O_emi_from_agri_b[0:10] 
    
    # N2O_emi_from_agri = IF_THEN_ELSE ( j==1 , N2O_emi_from_agri_AF , N2O_emi_from_agri_X_AF )
        idxlhs = fcol_in_mdf['N2O_emi_from_agri']
        idx1 = fcol_in_mdf['N2O_emi_from_agri_AF']
        idx2 = fcol_in_mdf['N2O_emi_from_agri_X_AF']
        for j in range(0,10):
            mdf[rowi, idxlhs + j] =  IF_THEN_ELSE  (  j==1  , mdf[rowi , idx1] , mdf[rowi , idx2 + j] ) 
     
    # Global_N2O_emi_from_agri = SUM ( N2O_emi_from_agri[region!] )
        idxlhs = fcol_in_mdf['Global_N2O_emi_from_agri']
        idx1 = fcol_in_mdf['N2O_emi_from_agri']
        globsum = 0
        for j in range(0,10):
            globsum = globsum + mdf[rowi, idx1 + j]
        mdf[rowi, idxlhs] = globsum 
    
    # N2O_emi_X_agri_US = N2O_emi_X_agri_US_a * np.exp ( GDPpp_USED[us] * UNIT_conv_to_make_exp_dmnl * N2O_emi_X_agri_US_b )
        idxlhs = fcol_in_mdf['N2O_emi_X_agri_US']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs] =  N2O_emi_X_agri_US_a  *  np.exp  ( mdf[rowi, idx1 + 0] *  UNIT_conv_to_make_exp_dmnl  *  N2O_emi_X_agri_US_b  ) 
    
    # N2O_emi_X_agri_EU = N2O_emi_X_agri_EU_a * np.exp ( GDPpp_USED[eu] * UNIT_conv_to_make_exp_dmnl * N2O_emi_X_agri_EU_b )
        idxlhs = fcol_in_mdf['N2O_emi_X_agri_EU']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs] =  N2O_emi_X_agri_EU_a  *  np.exp  ( mdf[rowi, idx1 + 8] *  UNIT_conv_to_make_exp_dmnl  *  N2O_emi_X_agri_EU_b  ) 
    
    # N2O_emi_X_agri_CN = N2O_emi_X_agri_CN_a * LN ( GDPpp_USED[cn] * UNIT_conv_to_make_exp_dmnl ) + N2O_emi_X_agri_CN_b
        idxlhs = fcol_in_mdf['N2O_emi_X_agri_CN']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs] =  N2O_emi_X_agri_CN_a  *  np.log  ( mdf[rowi, idx1 + 2] *  UNIT_conv_to_make_exp_dmnl  )  +  N2O_emi_X_agri_CN_b 
    
    # N2O_emi_X_agri_SA = N2O_emi_X_agri_SA_a * LN ( GDPpp_USED[sa] * UNIT_conv_to_make_exp_dmnl ) + N2O_emi_X_agri_SA_b
        idxlhs = fcol_in_mdf['N2O_emi_X_agri_SA']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs] =  N2O_emi_X_agri_SA_a  *  np.log  ( mdf[rowi, idx1 + 4] *  UNIT_conv_to_make_exp_dmnl  )  +  N2O_emi_X_agri_SA_b 
    
    # N2O_emi_X_agri_WO_US_EU_CN_SA[region] = N2O_emi_X_agri_a[region] * GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl + N2O_emi_X_agri_b[region]
        idxlhs = fcol_in_mdf['N2O_emi_X_agri_WO_US_EU_CN_SA']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  N2O_emi_X_agri_a[0:10]  * mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  +  N2O_emi_X_agri_b[0:10] 
    
    # N2O_emi_X_agri = IF_THEN_ELSE ( j==0 , N2O_emi_X_agri_US , IF_THEN_ELSE ( j==8 , N2O_emi_X_agri_EU , IF_THEN_ELSE ( j==2 , N2O_emi_X_agri_CN , IF_THEN_ELSE ( j==4 , N2O_emi_X_agri_SA , N2O_emi_X_agri_WO_US_EU_CN_SA ) ) ) )
        idxlhs = fcol_in_mdf['N2O_emi_X_agri']
        idx1 = fcol_in_mdf['N2O_emi_X_agri_US']
        idx2 = fcol_in_mdf['N2O_emi_X_agri_EU']
        idx3 = fcol_in_mdf['N2O_emi_X_agri_CN']
        idx4 = fcol_in_mdf['N2O_emi_X_agri_SA']
        idx5 = fcol_in_mdf['N2O_emi_X_agri_WO_US_EU_CN_SA']
        for j in range(0,10):
            mdf[rowi, idxlhs + j] =  IF_THEN_ELSE  (  j==0  , mdf[rowi , idx1] ,  IF_THEN_ELSE  (  j==8  , mdf[rowi , idx2] ,  IF_THEN_ELSE  (  j==2  , mdf[rowi , idx3] ,  IF_THEN_ELSE  (  j==4  , mdf[rowi , idx4] , mdf[rowi , idx5 + j] )  )  )  ) 
     
    # Global_N2O_emi_X_agri = SUM ( N2O_emi_X_agri[region!] )
        idxlhs = fcol_in_mdf['Global_N2O_emi_X_agri']
        idx1 = fcol_in_mdf['N2O_emi_X_agri']
        globsum = 0
        for j in range(0,10):
            globsum = globsum + mdf[rowi, idx1 + j]
        mdf[rowi, idxlhs] = globsum 
    
    # Global_N2O_emissions = Global_N2O_emi_from_agri + Global_N2O_emi_X_agri
        idxlhs = fcol_in_mdf['Global_N2O_emissions']
        idx1 = fcol_in_mdf['Global_N2O_emi_from_agri']
        idx2 = fcol_in_mdf['Global_N2O_emi_X_agri']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2]
    
    # N2O_emissions_JR_RCP3_or_SSP245 = Global_N2O_emissions
        idxlhs = fcol_in_mdf['N2O_emissions_JR_RCP3_or_SSP245']
        idx1 = fcol_in_mdf['Global_N2O_emissions']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # N2O_man_made_emissions_experiment = N2O_emissions_JR_RCP3_or_SSP245
        idxlhs = fcol_in_mdf['N2O_man_made_emissions_experiment']
        idx1 = fcol_in_mdf['N2O_emissions_JR_RCP3_or_SSP245']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # N2O_man_made_emissions_GtCO2e_py = N2O_man_made_emissions_experiment * Global_Warming_Potential_N20 / UNIT_conversion_Gt_to_Mt
        idxlhs = fcol_in_mdf['N2O_man_made_emissions_GtCO2e_py']
        idx1 = fcol_in_mdf['N2O_man_made_emissions_experiment']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Global_Warming_Potential_N20  /  UNIT_conversion_Gt_to_Mt 
    
    # Emissions_of_Kyoto_Fluor_with_JR_shape_kt_py = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 102.464 ) , ( 1981 , 102.866 ) , ( 1982 , 97.6419 ) , ( 1983 , 104.071 ) , ( 1984 , 114.518 ) , ( 1985 , 113.715 ) , ( 1986 , 115.724 ) , ( 1987 , 121.349 ) , ( 1988 , 133.404 ) , ( 1989 , 140.637 ) , ( 1990 , 137.824 ) , ( 1991 , 135.413 ) , ( 1992 , 132.198 ) , ( 1993 , 129.787 ) , ( 1994 , 135.413 ) , ( 1995 , 147.467 ) , ( 1996 , 159.12 ) , ( 1997 , 173.586 ) , ( 1998 , 178.006 ) , ( 1999 , 187.649 ) , ( 2000 , 184.033 ) , ( 2001 , 177.604 ) , ( 2002 , 188.855 ) , ( 2003 , 193.275 ) , ( 2004 , 217.786 ) , ( 2005 , 236.671 ) , ( 2006 , 254.753 ) , ( 2007 , 262.789 ) , ( 2008 , 274.844 ) , ( 2009 , 272.031 ) , ( 2010 , 289.309 ) , ( 2011 , 302.569 ) , ( 2012 , 319.044 ) , ( 2013 , 349.984 ) , ( 2014 , 381.728 ) , ( 2015 , 371.682 ) , ( 2016 , 384.139 ) , ( 2017 , 399.809 ) , ( 2018 , 413.873 ) , ( 2019 , 421.91 ) , ( 2020 , 425.573 ) , ( 2021 , 430.467 ) , ( 2022 , 435.361 ) , ( 2023 , 440.255 ) , ( 2024 , 445.149 ) , ( 2025 , 450.043 ) , ( 2026 , 452.659 ) , ( 2027 , 455.275 ) , ( 2028 , 457.891 ) , ( 2029 , 460.507 ) , ( 2030 , 463.123 ) , ( 2031 , 461.834 ) , ( 2032 , 460.546 ) , ( 2033 , 459.257 ) , ( 2034 , 457.968 ) , ( 2035 , 456.68 ) , ( 2036 , 453.04 ) , ( 2037 , 449.401 ) , ( 2038 , 445.761 ) , ( 2039 , 442.122 ) , ( 2040 , 438.482 ) , ( 2041 , 431.628 ) , ( 2042 , 424.774 ) , ( 2043 , 417.92 ) , ( 2044 , 411.065 ) , ( 2045 , 404.211 ) , ( 2046 , 394.801 ) , ( 2047 , 385.39 ) , ( 2048 , 375.979 ) , ( 2049 , 366.568 ) , ( 2050 , 357.158 ) , ( 2051 , 350.015 ) , ( 2052 , 342.871 ) , ( 2053 , 335.728 ) , ( 2054 , 328.585 ) , ( 2055 , 321.442 ) , ( 2056 , 314.299 ) , ( 2057 , 307.156 ) , ( 2058 , 300.012 ) , ( 2059 , 292.869 ) , ( 2060 , 285.726 ) , ( 2061 , 278.583 ) , ( 2062 , 271.44 ) , ( 2063 , 264.297 ) , ( 2064 , 257.154 ) , ( 2065 , 250.01 ) , ( 2066 , 242.867 ) , ( 2067 , 235.724 ) , ( 2068 , 228.581 ) , ( 2069 , 221.438 ) , ( 2070 , 214.295 ) , ( 2071 , 207.151 ) , ( 2072 , 200.008 ) , ( 2073 , 192.865 ) , ( 2074 , 185.722 ) , ( 2075 , 178.579 ) , ( 2076 , 171.436 ) , ( 2077 , 164.293 ) , ( 2078 , 157.149 ) , ( 2079 , 150.006 ) , ( 2080 , 142.863 ) , ( 2081 , 135.72 ) , ( 2082 , 128.577 ) , ( 2083 , 121.434 ) , ( 2084 , 114.29 ) , ( 2085 , 107.147 ) , ( 2086 , 100.004 ) , ( 2087 , 92.861 ) , ( 2088 , 85.7178 ) , ( 2089 , 78.5747 ) , ( 2090 , 71.4315 ) , ( 2091 , 64.2884 ) , ( 2092 , 57.1452 ) , ( 2093 , 50.0021 ) , ( 2094 , 42.8589 ) , ( 2095 , 35.7158 ) , ( 2096 , 28.5726 ) , ( 2097 , 21.4295 ) , ( 2098 , 14.2863 ) , ( 2099 , 7.14315 ) , ( 2100 , 0 ) ) )
        tabidx = ftab_in_d_table['Emissions_of_Kyoto_Fluor_with_JR_shape_kt_py'] # fetch the correct table
        idxlhs = fcol_in_mdf['Emissions_of_Kyoto_Fluor_with_JR_shape_kt_py'] # get the location of the lhs in mdf
        look = d_table[tabidx]
        valgt = GRAPH( zeit, look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # Kyoto_Fluor_emissions_JR_RCP3_or_SSP245 = Emissions_of_Kyoto_Fluor_with_JR_shape_kt_py
        idxlhs = fcol_in_mdf['Kyoto_Fluor_emissions_JR_RCP3_or_SSP245']
        idx1 = fcol_in_mdf['Emissions_of_Kyoto_Fluor_with_JR_shape_kt_py']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # Kyoto_Fluor_emissions = Kyoto_Fluor_emissions_JR_RCP3_or_SSP245
        idxlhs = fcol_in_mdf['Kyoto_Fluor_emissions']
        idx1 = fcol_in_mdf['Kyoto_Fluor_emissions_JR_RCP3_or_SSP245']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # Kyoto_Fluor_emissions_GtCO2e_py = Kyoto_Fluor_emissions * Kyoto_Fluor_Global_Warming_Potential / UNIT_conversion_Gt_to_kt
        idxlhs = fcol_in_mdf['Kyoto_Fluor_emissions_GtCO2e_py']
        idx1 = fcol_in_mdf['Kyoto_Fluor_emissions']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Kyoto_Fluor_Global_Warming_Potential  /  UNIT_conversion_Gt_to_kt 
    
    # Emissions_of_Montreal_gases_with_JR_shape_kt_py = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1638.4 ) , ( 1981 , 1532.3 ) , ( 1982 , 1539.42 ) , ( 1983 , 1677.43 ) , ( 1984 , 1792.07 ) , ( 1985 , 1685.65 ) , ( 1986 , 1939.86 ) , ( 1987 , 2064.68 ) , ( 1988 , 2060.15 ) , ( 1989 , 1813.51 ) , ( 1990 , 1989.86 ) , ( 1991 , 1607.8 ) , ( 1992 , 1517.42 ) , ( 1993 , 1168.94 ) , ( 1994 , 1014.23 ) , ( 1995 , 962.917 ) , ( 1996 , 795.891 ) , ( 1997 , 711.038 ) , ( 1998 , 728.513 ) , ( 1999 , 680.544 ) , ( 2000 , 677.163 ) , ( 2001 , 625.922 ) , ( 2002 , 609.698 ) , ( 2003 , 626.466 ) , ( 2004 , 605.364 ) , ( 2005 , 545.23 ) , ( 2006 , 557.65 ) , ( 2007 , 564.595 ) , ( 2008 , 566.209 ) , ( 2009 , 568.007 ) , ( 2010 , 564.927 ) , ( 2011 , 550.292 ) , ( 2012 , 535.908 ) , ( 2013 , 521.714 ) , ( 2014 , 507.677 ) , ( 2015 , 486.503 ) , ( 2016 , 479.534 ) , ( 2017 , 472.965 ) , ( 2018 , 466.766 ) , ( 2019 , 460.903 ) , ( 2020 , 455.355 ) , ( 2021 , 434.648 ) , ( 2022 , 414.207 ) , ( 2023 , 394.013 ) , ( 2024 , 374.045 ) , ( 2025 , 354.289 ) , ( 2026 , 334.726 ) , ( 2027 , 315.343 ) , ( 2028 , 296.127 ) , ( 2029 , 277.066 ) , ( 2030 , 258.146 ) , ( 2031 , 242.019 ) , ( 2032 , 226 ) , ( 2033 , 210.081 ) , ( 2034 , 194.256 ) , ( 2035 , 178.515 ) , ( 2036 , 162.855 ) , ( 2037 , 147.269 ) , ( 2038 , 131.752 ) , ( 2039 , 116.301 ) , ( 2040 , 100.909 ) , ( 2041 , 94.99 ) , ( 2042 , 89.141 ) , ( 2043 , 83.353 ) , ( 2044 , 77.627 ) , ( 2045 , 71.956 ) , ( 2046 , 66.335 ) , ( 2047 , 60.763 ) , ( 2048 , 55.238 ) , ( 2049 , 49.753 ) , ( 2050 , 44.307 ) , ( 2051 , 42.06 ) , ( 2052 , 39.846 ) , ( 2053 , 37.664 ) , ( 2054 , 35.513 ) , ( 2055 , 33.39 ) , ( 2056 , 31.295 ) , ( 2057 , 29.222 ) , ( 2058 , 27.176 ) , ( 2059 , 25.149 ) , ( 2060 , 23.144 ) , ( 2061 , 22.109 ) , ( 2062 , 21.096 ) , ( 2063 , 20.097 ) , ( 2064 , 19.116 ) , ( 2065 , 18.151 ) , ( 2066 , 17.199 ) , ( 2067 , 16.261 ) , ( 2068 , 15.338 ) , ( 2069 , 14.425 ) , ( 2070 , 13.524 ) , ( 2071 , 12.972 ) , ( 2072 , 12.429 ) , ( 2073 , 11.896 ) , ( 2074 , 11.372 ) , ( 2075 , 10.859 ) , ( 2076 , 10.353 ) , ( 2077 , 9.855 ) , ( 2078 , 9.365 ) , ( 2079 , 8.883 ) , ( 2080 , 8.407 ) , ( 2081 , 8.079 ) , ( 2082 , 7.762 ) , ( 2083 , 7.448 ) , ( 2084 , 7.139 ) , ( 2085 , 6.838 ) , ( 2086 , 6.542 ) , ( 2087 , 6.25 ) , ( 2088 , 5.962 ) , ( 2089 , 5.68 ) , ( 2090 , 5.403 ) , ( 2091 , 5.201 ) , ( 2092 , 5.002 ) , ( 2093 , 4.808 ) , ( 2094 , 4.616 ) , ( 2095 , 4.429 ) , ( 2096 , 4.245 ) , ( 2097 , 4.063 ) , ( 2098 , 3.888 ) , ( 2099 , 3.713 ) , ( 2100 , 3.541 ) ) )
        tabidx = ftab_in_d_table['Emissions_of_Montreal_gases_with_JR_shape_kt_py'] # fetch the correct table
        idxlhs = fcol_in_mdf['Emissions_of_Montreal_gases_with_JR_shape_kt_py'] # get the location of the lhs in mdf
        look = d_table[tabidx]
        valgt = GRAPH( zeit, look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # Montreal_gases_emissions_JR_RCP3_or_SSP245 = Emissions_of_Montreal_gases_with_JR_shape_kt_py
        idxlhs = fcol_in_mdf['Montreal_gases_emissions_JR_RCP3_or_SSP245']
        idx1 = fcol_in_mdf['Emissions_of_Montreal_gases_with_JR_shape_kt_py']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # Montreal_gases_emissions = Montreal_gases_emissions_JR_RCP3_or_SSP245
        idxlhs = fcol_in_mdf['Montreal_gases_emissions']
        idx1 = fcol_in_mdf['Montreal_gases_emissions_JR_RCP3_or_SSP245']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # Montreal_emissions_GtCO2e_py = Montreal_gases_emissions * Montreal_Global_Warming_Potential / UNIT_conversion_Gt_to_kt
        idxlhs = fcol_in_mdf['Montreal_emissions_GtCO2e_py']
        idx1 = fcol_in_mdf['Montreal_gases_emissions']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Montreal_Global_Warming_Potential  /  UNIT_conversion_Gt_to_kt 
    
    # All_N2O_emissions = N2O_man_made_emissions_experiment + N2O_natural_emissions
        idxlhs = fcol_in_mdf['All_N2O_emissions']
        idx1 = fcol_in_mdf['N2O_man_made_emissions_experiment']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] +  N2O_natural_emissions 
    
    # Regional_GDP_weight[region] = GDP_USED[region] / Global_GDP_USED
        idxlhs = fcol_in_mdf['Regional_GDP_weight']
        idx1 = fcol_in_mdf['GDP_USED']
        idx2 = fcol_in_mdf['Global_GDP_USED']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2]
    
    # Each_region_max_cost_estimate_empowerment_PES[region] = All_region_max_cost_estimate_empowerment_PES * Regional_GDP_weight[region]
        idxlhs = fcol_in_mdf['Each_region_max_cost_estimate_empowerment_PES']
        idx1 = fcol_in_mdf['Regional_GDP_weight']
        mdf[rowi, idxlhs:idxlhs + 10] =  All_region_max_cost_estimate_empowerment_PES  * mdf[rowi , idx1:idx1 + 10]
    
    # Each_region_max_cost_estimate_energy_PES[region] = All_region_max_cost_estimate_energy_PES * Regional_GDP_weight[region]
        idxlhs = fcol_in_mdf['Each_region_max_cost_estimate_energy_PES']
        idx1 = fcol_in_mdf['Regional_GDP_weight']
        mdf[rowi, idxlhs:idxlhs + 10] =  All_region_max_cost_estimate_energy_PES  * mdf[rowi , idx1:idx1 + 10]
    
    # Each_region_max_cost_estimate_food_PES[region] = All_region_max_cost_estimate_food_PES * Regional_GDP_weight[region]
        idxlhs = fcol_in_mdf['Each_region_max_cost_estimate_food_PES']
        idx1 = fcol_in_mdf['Regional_GDP_weight']
        mdf[rowi, idxlhs:idxlhs + 10] =  All_region_max_cost_estimate_food_PES  * mdf[rowi , idx1:idx1 + 10]
    
    # Each_region_max_cost_estimate_inequality_PES[region] = All_region_max_cost_estimate_inequality_PES * Regional_GDP_weight[region]
        idxlhs = fcol_in_mdf['Each_region_max_cost_estimate_inequality_PES']
        idx1 = fcol_in_mdf['Regional_GDP_weight']
        mdf[rowi, idxlhs:idxlhs + 10] =  All_region_max_cost_estimate_inequality_PES  * mdf[rowi , idx1:idx1 + 10]
    
    # Each_region_max_cost_estimate_poverty_PES[region] = All_region_max_cost_estimate_poverty_PES * Regional_GDP_weight[region]
        idxlhs = fcol_in_mdf['Each_region_max_cost_estimate_poverty_PES']
        idx1 = fcol_in_mdf['Regional_GDP_weight']
        mdf[rowi, idxlhs:idxlhs + 10] =  All_region_max_cost_estimate_poverty_PES  * mdf[rowi , idx1:idx1 + 10]
    
    # Each_region_max_cost_estimate_all_TAs_PES[region] = Each_region_max_cost_estimate_empowerment_PES[region] + Each_region_max_cost_estimate_energy_PES[region] + Each_region_max_cost_estimate_food_PES[region] + Each_region_max_cost_estimate_inequality_PES[region] + Each_region_max_cost_estimate_poverty_PES[region]
        idxlhs = fcol_in_mdf['Each_region_max_cost_estimate_all_TAs_PES']
        idx1 = fcol_in_mdf['Each_region_max_cost_estimate_empowerment_PES']
        idx2 = fcol_in_mdf['Each_region_max_cost_estimate_energy_PES']
        idx3 = fcol_in_mdf['Each_region_max_cost_estimate_food_PES']
        idx4 = fcol_in_mdf['Each_region_max_cost_estimate_inequality_PES']
        idx5 = fcol_in_mdf['Each_region_max_cost_estimate_poverty_PES']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] + mdf[rowi , idx4:idx4 + 10] + mdf[rowi , idx5:idx5 + 10]
     
    # All_regions_from_Each_region_max_cost_estimate_all_TAs_PES = SUM ( Each_region_max_cost_estimate_all_TAs_PES[region!] )
        idxlhs = fcol_in_mdf['All_regions_from_Each_region_max_cost_estimate_all_TAs_PES']
        idx1 = fcol_in_mdf['Each_region_max_cost_estimate_all_TAs_PES']
        globsum = 0
        for j in range(0,10):
            globsum = globsum + mdf[rowi, idx1 + j]
        mdf[rowi, idxlhs] = globsum 
    
    # Indicated_inequality_index_higher_is_more_unequal[region] = 1 + Strength_of_inequality_proxy * ( Worker_share_of_output_with_unemployment_effect_in_1980[region] / Worker_share_of_output_with_unemployment_effect[region] - 1 )
        idxlhs = fcol_in_mdf['Indicated_inequality_index_higher_is_more_unequal']
        idx1 = fcol_in_mdf['Worker_share_of_output_with_unemployment_effect']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  +  Strength_of_inequality_proxy  *  (  Worker_share_of_output_with_unemployment_effect_in_1980[0:10]  / mdf[rowi , idx1:idx1 + 10] -  1  ) 
    
    # JR_inequality_effect_on_logistic_k[region] = 1 + JR_sINEeolLOK_lt_0 * ( Indicated_inequality_index_higher_is_more_unequal[region] / 0.5 - 1 )
        idxlhs = fcol_in_mdf['JR_inequality_effect_on_logistic_k']
        idx1 = fcol_in_mdf['Indicated_inequality_index_higher_is_more_unequal']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  +  JR_sINEeolLOK_lt_0  *  ( mdf[rowi , idx1:idx1 + 10] /  0.5  -  1  ) 
    
    # Logistic_k[region] = Normal_k * JR_inequality_effect_on_logistic_k[region]
        idxlhs = fcol_in_mdf['Logistic_k']
        idx1 = fcol_in_mdf['JR_inequality_effect_on_logistic_k']
        mdf[rowi, idxlhs:idxlhs + 10] =  Normal_k  * mdf[rowi , idx1:idx1 + 10]
    
    # Existential_minimum_income = SMOOTH ( Indicated_Existential_minimum_income , Time_to_adjust_Existential_minimum_income )
        idx1 = fcol_in_mdf['Existential_minimum_income']
        idx2 = fcol_in_mdf['Indicated_Existential_minimum_income']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1 , idx2] - mdf[rowi -1 , idx1 ]) / Time_to_adjust_Existential_minimum_income * dt
    
    # Fraction_of_population_below_existential_minimum[region] = 1 - ( 0.975 / ( 1 + np.exp ( - Logistic_k[region] * ( ( GDPpp_USED[region] - Existential_minimum_income ) / UNIT_conv_to_dmnl ) ) ) )
        idxlhs = fcol_in_mdf['Fraction_of_population_below_existential_minimum']
        idx1 = fcol_in_mdf['Logistic_k']
        idx2 = fcol_in_mdf['GDPpp_USED']
        idx3 = fcol_in_mdf['Existential_minimum_income']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  -  (  0.975  /  (  1  +  np.exp  (  - mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] - mdf[rowi , idx3] )  /  UNIT_conv_to_dmnl  )  )  )  ) 
    
    # SDG1_Score[region] = IF_THEN_ELSE ( Fraction_of_population_below_existential_minimum > SDG1_threshold_red , 0 , IF_THEN_ELSE ( Fraction_of_population_below_existential_minimum > SDG1_threshold_green , 0.5 , 1 ) )
        idxlhs = fcol_in_mdf['SDG1_Score']
        idx1 = fcol_in_mdf['Fraction_of_population_below_existential_minimum']
        idx2 = fcol_in_mdf['Fraction_of_population_below_existential_minimum']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  ( mdf[rowi , idx1:idx1 + 10] >  SDG1_threshold_red  ,  0  ,  IF_THEN_ELSE  ( mdf[rowi , idx2:idx2 + 10] >  SDG1_threshold_green  ,  0.5  ,  1  )  ) 
    
    # Fraction_of_population_undernourished[region] = MIN ( 1 , SDG2_a * ( GDPpp_USED[region] / UNIT_conv_to_make_base_dmnless ) ^ ( SDG2_b ) )
        idxlhs = fcol_in_mdf['Fraction_of_population_undernourished']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.minimum  (  1  ,  SDG2_a  *  ( mdf[rowi , idx1:idx1 + 10] /  UNIT_conv_to_make_base_dmnless  )  **  (  SDG2_b  )  ) 
    
    # SDG_2_Score[region] = IF_THEN_ELSE ( Fraction_of_population_undernourished > SDG2_threshold_red , 0 , IF_THEN_ELSE ( Fraction_of_population_undernourished > SDG2_threshold_green , 0.5 , 1 ) )
        idxlhs = fcol_in_mdf['SDG_2_Score']
        idx1 = fcol_in_mdf['Fraction_of_population_undernourished']
        idx2 = fcol_in_mdf['Fraction_of_population_undernourished']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  ( mdf[rowi , idx1:idx1 + 10] >  SDG2_threshold_red  ,  0  ,  IF_THEN_ELSE  ( mdf[rowi , idx2:idx2 + 10] >  SDG2_threshold_green  ,  0.5  ,  1  )  ) 
    
    # Worker_cash_inflow_seasonally_adjusted[region] = SMOOTHI ( Worker_cash_inflow[region] , Time_to_adjust_worker_consumption_pattern , Worker_income_after_tax_in_1980[region] )
        idx1 = fcol_in_mdf['Worker_cash_inflow_seasonally_adjusted']
        idx2 = fcol_in_mdf['Worker_cash_inflow']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi - 1, idx1:idx1 + 10]) / Time_to_adjust_worker_consumption_pattern * dt
    
    # Worker_cash_inflow_seasonally_adjusted_pp[region] = Worker_cash_inflow_seasonally_adjusted[region] / Population[region]
        idxlhs = fcol_in_mdf['Worker_cash_inflow_seasonally_adjusted_pp']
        idx1 = fcol_in_mdf['Worker_cash_inflow_seasonally_adjusted']
        idx2 = fcol_in_mdf['Population']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # Wellbeing_from_disposable_income[region] = Worker_cash_inflow_seasonally_adjusted_pp[region] / Disposable_income_threshold_for_wellbeing
        idxlhs = fcol_in_mdf['Wellbeing_from_disposable_income']
        idx1 = fcol_in_mdf['Worker_cash_inflow_seasonally_adjusted_pp']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Disposable_income_threshold_for_wellbeing 
    
    # Ratio_actual_to_basic_el_use[region] = Actual_el_use_pp[region] / Basic_el_use
        idxlhs = fcol_in_mdf['Ratio_actual_to_basic_el_use']
        idx1 = fcol_in_mdf['Actual_el_use_pp']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Basic_el_use 
    
    # Wellbeing_from_el_use_raw[region] = El_use_wellbeing_a + El_use_wellbeing_b * LN ( Ratio_actual_to_basic_el_use[region] )
        idxlhs = fcol_in_mdf['Wellbeing_from_el_use_raw']
        idx1 = fcol_in_mdf['Ratio_actual_to_basic_el_use']
        mdf[rowi, idxlhs:idxlhs + 10] =  El_use_wellbeing_a  +  El_use_wellbeing_b  *  np.log  ( mdf[rowi , idx1:idx1 + 10] ) 
    
    # Wellbeing_from_el_use_scaled[region] = Wellbeing_from_el_use_raw[region] / ( El_use_wellbeing_a + El_use_wellbeing_b * LN ( 1 ) )
        idxlhs = fcol_in_mdf['Wellbeing_from_el_use_scaled']
        idx1 = fcol_in_mdf['Wellbeing_from_el_use_raw']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  (  El_use_wellbeing_a  +  El_use_wellbeing_b  *  np.log  (  1  )  ) 
    
    # white_meat_not_wasted_pp[region] = white_meat_demand_pp_consumed[region] * UNIT_conv_kgwmeat_to_kg
        idxlhs = fcol_in_mdf['white_meat_not_wasted_pp']
        idx1 = fcol_in_mdf['white_meat_demand_pp_consumed']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_kgwmeat_to_kg 
    
    # Ratio_of_actual_to_healthy_white_meat[region] = white_meat_not_wasted_pp[region] / Healthy_white_meat_consumption
        idxlhs = fcol_in_mdf['Ratio_of_actual_to_healthy_white_meat']
        idx1 = fcol_in_mdf['white_meat_not_wasted_pp']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Healthy_white_meat_consumption 
    
    # Wellbeing_from_white_meat[region] = ( 1 / ( stdev * SQRT ( 2 * 3.14142 ) ) ) * np.exp ( - ( ( Ratio_of_actual_to_healthy_white_meat[region] - mean_value ) ^ 2 ) / ( 2 * stdev ^ 2 ) )
        idxlhs = fcol_in_mdf['Wellbeing_from_white_meat']
        idx1 = fcol_in_mdf['Ratio_of_actual_to_healthy_white_meat']
        mdf[rowi, idxlhs:idxlhs + 10] =  (  1  /  (  stdev  *  SQRT  (  2  *  3.14142  )  )  )  *  np.exp  (  -  (  ( mdf[rowi , idx1:idx1 + 10] -  mean_value  )  **  2  )  /  (  2  *  stdev  **  2  )  ) 
    
    # red_meat_not_wasted_pp[region] = red_meat_demand_pp_consumed[region] * UNIT_conv_kgrmeat_to_kg
        idxlhs = fcol_in_mdf['red_meat_not_wasted_pp']
        idx1 = fcol_in_mdf['red_meat_demand_pp_consumed']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_kgrmeat_to_kg 
    
    # Ratio_of_actual_to_healthy_red_meat[region] = red_meat_not_wasted_pp[region] / Healthy_red_meat_consumption
        idxlhs = fcol_in_mdf['Ratio_of_actual_to_healthy_red_meat']
        idx1 = fcol_in_mdf['red_meat_not_wasted_pp']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Healthy_red_meat_consumption 
    
    # Wellbeing_from_red_meat[region] = ( 1 / ( stdev * SQRT ( 2 * 3.14142 ) ) ) * np.exp ( - ( ( Ratio_of_actual_to_healthy_red_meat[region] - mean_value ) ^ 2 ) / ( 2 * stdev ^ 2 ) )
        idxlhs = fcol_in_mdf['Wellbeing_from_red_meat']
        idx1 = fcol_in_mdf['Ratio_of_actual_to_healthy_red_meat']
        mdf[rowi, idxlhs:idxlhs + 10] =  (  1  /  (  stdev  *  SQRT  (  2  *  3.14142  )  )  )  *  np.exp  (  -  (  ( mdf[rowi , idx1:idx1 + 10] -  mean_value  )  **  2  )  /  (  2  *  stdev  **  2  )  ) 
    
    # Ratio_of_actual_to_healthy_all_crop[region] = all_crop_not_wasted_pp[region] / Healthy_all_crop_consumption
        idxlhs = fcol_in_mdf['Ratio_of_actual_to_healthy_all_crop']
        idx1 = fcol_in_mdf['all_crop_not_wasted_pp']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Healthy_all_crop_consumption 
    
    # Wellbeing_from_crops[region] = ( 1 / ( stdev * SQRT ( 2 * 3.14142 ) ) ) * np.exp ( - ( ( Ratio_of_actual_to_healthy_all_crop[region] - mean_value ) ^ 2 ) / ( 2 * stdev ^ 2 ) )
        idxlhs = fcol_in_mdf['Wellbeing_from_crops']
        idx1 = fcol_in_mdf['Ratio_of_actual_to_healthy_all_crop']
        mdf[rowi, idxlhs:idxlhs + 10] =  (  1  /  (  stdev  *  SQRT  (  2  *  3.14142  )  )  )  *  np.exp  (  -  (  ( mdf[rowi , idx1:idx1 + 10] -  mean_value  )  **  2  )  /  (  2  *  stdev  **  2  )  ) 
    
    # Wellbeing_from_food[region] = ( Wellbeing_from_white_meat[region] * Weight_on_white_meat + Wellbeing_from_red_meat[region] * Weight_on_red_meat + Wellbeing_from_crops[region] * Weight_on_crops ) / Sum_of_food_weights
        idxlhs = fcol_in_mdf['Wellbeing_from_food']
        idx1 = fcol_in_mdf['Wellbeing_from_white_meat']
        idx2 = fcol_in_mdf['Wellbeing_from_red_meat']
        idx3 = fcol_in_mdf['Wellbeing_from_crops']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] *  Weight_on_white_meat  + mdf[rowi , idx2:idx2 + 10] *  Weight_on_red_meat  + mdf[rowi , idx3:idx3 + 10] *  Weight_on_crops  )  /  Sum_of_food_weights 
    
    # Wellbeing_from_inequality[region] = 1 / Actual_inequality_index_higher_is_more_unequal[region]
        idxlhs = fcol_in_mdf['Wellbeing_from_inequality']
        idx1 = fcol_in_mdf['Actual_inequality_index_higher_is_more_unequal']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  / mdf[rowi , idx1:idx1 + 10]
    
    # Wellbeing_from_population_with_regular_job[region] = 1 + Slope_of_wellbeing_from_fraction_of_people_outside_of_labor_pool * ( Frac_outside_of_labour_pool_in_1980[region] / Fraction_of_people_outside_of_labour_market_FOPOLM[region] - 1 )
        idxlhs = fcol_in_mdf['Wellbeing_from_population_with_regular_job']
        idx1 = fcol_in_mdf['Fraction_of_people_outside_of_labour_market_FOPOLM']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  +  Slope_of_wellbeing_from_fraction_of_people_outside_of_labor_pool  *  (  Frac_outside_of_labour_pool_in_1980[0:10]  / mdf[rowi , idx1:idx1 + 10] -  1  ) 
    
    # Public_spending_as_share_of_GDP[region] = Public_services_pp[region] / GDPpp_USED[region] / UNIT_conv_to_k217pppUSD_ppy
        idxlhs = fcol_in_mdf['Public_spending_as_share_of_GDP']
        idx1 = fcol_in_mdf['Public_services_pp']
        idx2 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10] /  UNIT_conv_to_k217pppUSD_ppy 
    
    # Smoothed_Public_spending_as_share_of_GDP[region] = SMOOTH ( Public_spending_as_share_of_GDP[region] , Time_for_public_spending_to_affect_wellbeing )
        idx1 = fcol_in_mdf['Smoothed_Public_spending_as_share_of_GDP']
        idx2 = fcol_in_mdf['Public_spending_as_share_of_GDP']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1+10] + ( mdf[rowi-1 , idx2:idx2 + 10] - mdf[rowi -1 , idx1:idx1 + 10]) / Time_for_public_spending_to_affect_wellbeing * dt
    
    # Public_spending_ratio[region] = Smoothed_Public_spending_as_share_of_GDP[region] / Satisfactory_public_spending
        idxlhs = fcol_in_mdf['Public_spending_ratio']
        idx1 = fcol_in_mdf['Smoothed_Public_spending_as_share_of_GDP']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Satisfactory_public_spending 
    
    # Wellbeing_from_public_spending[region] = WITH LOOKUP ( Public_spending_ratio[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 0 ) , ( 0.25 , 0.02907 ) , ( 0.5 , 0.08995 ) , ( 0.75 , 0.2175 ) , ( 1 , 0.4699 ) , ( 1.25 , 0.9055 ) , ( 1.5 , 1.5 ) , ( 1.75 , 2.095 ) , ( 2 , 2.53 ) , ( 2.25 , 2.782 ) , ( 2.5 , 2.91 ) , ( 2.75 , 2.971 ) , ( 3 , 3 ) ) )
        tabidx = ftab_in_d_table['Wellbeing_from_public_spending'] # fetch the correct table
        idx2 = fcol_in_mdf['Wellbeing_from_public_spending'] # get the location of the lhs in mdf
        idx3 = fcol_in_mdf['Public_spending_ratio']
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:,0], look[:, 1])
    
    # Living_conditions_index[region] = ( Weight_disposable_income * Wellbeing_from_disposable_income[region] + Weight_el_use * Wellbeing_from_el_use_scaled[region] + Weight_food * Wellbeing_from_food[region] + Weight_inequality * Wellbeing_from_inequality[region] + Weight_population_in_job_market * Wellbeing_from_population_with_regular_job[region] + Weight_public_spending * Wellbeing_from_public_spending[region] ) / Sum_weights_living_conditions
        idxlhs = fcol_in_mdf['Living_conditions_index']
        idx1 = fcol_in_mdf['Wellbeing_from_disposable_income']
        idx2 = fcol_in_mdf['Wellbeing_from_el_use_scaled']
        idx3 = fcol_in_mdf['Wellbeing_from_food']
        idx4 = fcol_in_mdf['Wellbeing_from_inequality']
        idx5 = fcol_in_mdf['Wellbeing_from_population_with_regular_job']
        idx6 = fcol_in_mdf['Wellbeing_from_public_spending']
        mdf[rowi, idxlhs:idxlhs + 10] =  (  Weight_disposable_income  * mdf[rowi , idx1:idx1 + 10] +  Weight_el_use  * mdf[rowi , idx2:idx2 + 10] +  Weight_food  * mdf[rowi , idx3:idx3 + 10] +  Weight_inequality  * mdf[rowi , idx4:idx4 + 10] +  Weight_population_in_job_market  * mdf[rowi , idx5:idx5 + 10] +  Weight_public_spending  * mdf[rowi, idx6:idx6 + 10] )  /  Sum_weights_living_conditions 
    
    # Living_conditions_index_with_env_damage[region] = Living_conditions_index[region] * Weight_on_living_conditions + Actual_wellbeing_from_env_damage * Weight_on_env_conditions
        idxlhs = fcol_in_mdf['Living_conditions_index_with_env_damage']
        idx1 = fcol_in_mdf['Living_conditions_index']
        idx2 = fcol_in_mdf['Actual_wellbeing_from_env_damage']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  Weight_on_living_conditions  + mdf[rowi , idx2] *  Weight_on_env_conditions 
    
    # Wellbeing_from_social_tension[region] = 1 + SoE_of_Wellbeing_from_social_tension * ( Smoothed_Social_tension_index_with_trust_effect[region] / Social_tension_index_in_1980 - 1 )
        idxlhs = fcol_in_mdf['Wellbeing_from_social_tension']
        idx1 = fcol_in_mdf['Smoothed_Social_tension_index_with_trust_effect']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  +  SoE_of_Wellbeing_from_social_tension  *  ( mdf[rowi , idx1:idx1 + 10] /  Social_tension_index_in_1980  -  1  ) 
    
    # Smoothed_comparison_Effect_of_SDG_score_on_wellbeing[region] = SMOOTH3I ( Comparison_Effect_of_SDG_score_on_wellbeing[region] , Time_to_smooth_SDG_scores_for_wellbeing , 1 )
        idxin = fcol_in_mdf['Comparison_Effect_of_SDG_score_on_wellbeing']
        idx2 = fcol_in_mdf['Smoothed_comparison_Effect_of_SDG_score_on_wellbeing_2']
        idx1 = fcol_in_mdf['Smoothed_comparison_Effect_of_SDG_score_on_wellbeing_1']
        idxout = fcol_in_mdf['Smoothed_comparison_Effect_of_SDG_score_on_wellbeing']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( Time_to_smooth_SDG_scores_for_wellbeing / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( Time_to_smooth_SDG_scores_for_wellbeing / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( Time_to_smooth_SDG_scores_for_wellbeing / 3) * dt
    
    # Average_wellbeing_index[region] = ( Living_conditions_index_with_env_damage[region] * Weight_on_physical_conditions + Wellbeing_from_social_tension[region] * ( 1 - Weight_on_physical_conditions ) ) * Smoothed_comparison_Effect_of_SDG_score_on_wellbeing[region]
        idxlhs = fcol_in_mdf['Average_wellbeing_index']
        idx1 = fcol_in_mdf['Living_conditions_index_with_env_damage']
        idx2 = fcol_in_mdf['Wellbeing_from_social_tension']
        idx3 = fcol_in_mdf['Smoothed_comparison_Effect_of_SDG_score_on_wellbeing']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] *  Weight_on_physical_conditions  + mdf[rowi , idx2:idx2 + 10] *  (  1  -  Weight_on_physical_conditions  )  )  * mdf[rowi , idx3:idx3 + 10]
    
    # SDG_3_Score[region] = IF_THEN_ELSE ( Average_wellbeing_index < SDG3_threshold_red , 0 , IF_THEN_ELSE ( Average_wellbeing_index < SDG3_threshold_green , 0.5 , 1 ) )
        idxlhs = fcol_in_mdf['SDG_3_Score']
        idx1 = fcol_in_mdf['Average_wellbeing_index']
        idx2 = fcol_in_mdf['Average_wellbeing_index']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  ( mdf[rowi , idx1:idx1 + 10] <  SDG3_threshold_red  ,  0  ,  IF_THEN_ELSE  ( mdf[rowi , idx2:idx2 + 10] <  SDG3_threshold_green  ,  0.5  ,  1  )  ) 
    
    # Safe_water_cn = Safe_water_cn_L / ( 1 + np.exp ( - Safe_water_cn_k * ( ( GDPpp_USED[cn] / UNIT_conv_to_make_base_dmnless ) - Safe_water_cn_x0 ) ) ) + Safe_water_cn_min
        idxlhs = fcol_in_mdf['Safe_water_cn']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs] =  Safe_water_cn_L  /  (  1  +  np.exp  (  -  Safe_water_cn_k  *  (  ( mdf[rowi, idx1 + 2] /  UNIT_conv_to_make_base_dmnless  )  -  Safe_water_cn_x0  )  )  )  +  Safe_water_cn_min 
    
    # Safe_water_rest[region] = Safe_water_rest_L / ( 1 + np.exp ( - Safe_water_rest_k * ( ( GDPpp_USED[region] / UNIT_conv_to_make_base_dmnless ) - Safe_water_rest_x0 ) ) ) + Safe_water_rest_min
        idxlhs = fcol_in_mdf['Safe_water_rest']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  Safe_water_rest_L  /  (  1  +  np.exp  (  -  Safe_water_rest_k  *  (  ( mdf[rowi , idx1:idx1 + 10] /  UNIT_conv_to_make_base_dmnless  )  -  Safe_water_rest_x0  )  )  )  +  Safe_water_rest_min 
    
    # Safe_water = IF_THEN_ELSE ( j==2 , Safe_water_cn , Safe_water_rest )
        idxlhs = fcol_in_mdf['Safe_water']
        idx1 = fcol_in_mdf['Safe_water_cn']
        idx2 = fcol_in_mdf['Safe_water_rest']
        for j in range(0,10):
            mdf[rowi, idxlhs + j] =  IF_THEN_ELSE  (  j==2  , mdf[rowi , idx1] , mdf[rowi , idx2 + j] ) 
    
    # SDG6a_Score[region] = IF_THEN_ELSE ( Safe_water < SDG6a_threshold_red , 0 , IF_THEN_ELSE ( Safe_water < SDG6a_threshold_green , 0.5 , 1 ) )
        idxlhs = fcol_in_mdf['SDG6a_Score']
        idx1 = fcol_in_mdf['Safe_water']
        idx2 = fcol_in_mdf['Safe_water']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  ( mdf[rowi , idx1:idx1 + 10] <  SDG6a_threshold_red  ,  0  ,  IF_THEN_ELSE  ( mdf[rowi , idx2:idx2 + 10] <  SDG6a_threshold_green  ,  0.5  ,  1  )  ) 
    
    # Safe_sanitation[region] = Safe_sanitation_L / ( 1 + np.exp ( - Safe_sanitation_k * ( ( GDPpp_USED[region] / UNIT_conv_to_make_base_dmnless ) - Safe_sanitation_x0 ) ) ) + Safe_sanitation_min
        idxlhs = fcol_in_mdf['Safe_sanitation']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  Safe_sanitation_L  /  (  1  +  np.exp  (  -  Safe_sanitation_k  *  (  ( mdf[rowi , idx1:idx1 + 10] /  UNIT_conv_to_make_base_dmnless  )  -  Safe_sanitation_x0  )  )  )  +  Safe_sanitation_min 
    
    # SDG6b_Score[region] = IF_THEN_ELSE ( Safe_sanitation < SDG6b_threshold_red , 0 , IF_THEN_ELSE ( Safe_sanitation < SDG6b_threshold_green , 0.5 , 1 ) )
        idxlhs = fcol_in_mdf['SDG6b_Score']
        idx1 = fcol_in_mdf['Safe_sanitation']
        idx2 = fcol_in_mdf['Safe_sanitation']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  ( mdf[rowi , idx1:idx1 + 10] <  SDG6b_threshold_red  ,  0  ,  IF_THEN_ELSE  ( mdf[rowi , idx2:idx2 + 10] <  SDG6b_threshold_green  ,  0.5  ,  1  )  ) 
    
    # SDG_6_score[region] = ( SDG6a_Score[region] + SDG6b_Score[region] ) / 2
        idxlhs = fcol_in_mdf['SDG_6_score']
        idx1 = fcol_in_mdf['SDG6a_Score']
        idx2 = fcol_in_mdf['SDG6b_Score']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] )  /  2 
    
    # SDG_7_Score[region] = IF_THEN_ELSE ( Access_to_electricity < SDG_7_threshold_red , 0 , IF_THEN_ELSE ( Access_to_electricity < SDG_7_threshold_green , 0.5 , 1 ) )
        idxlhs = fcol_in_mdf['SDG_7_Score']
        idx1 = fcol_in_mdf['Access_to_electricity']
        idx2 = fcol_in_mdf['Access_to_electricity']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  ( mdf[rowi , idx1:idx1 + 10] <  SDG_7_threshold_red  ,  0  ,  IF_THEN_ELSE  ( mdf[rowi , idx2:idx2 + 10] <  SDG_7_threshold_green  ,  0.5  ,  1  )  ) 
    
    # Indicated_cost_of_capital_for_secured_debt[region] = Short_term_interest_rate[region] + Normal_bank_operating_margin
        idxlhs = fcol_in_mdf['Indicated_cost_of_capital_for_secured_debt']
        idx1 = fcol_in_mdf['Short_term_interest_rate']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] +  Normal_bank_operating_margin 
    
    # Cost_of_capital_for_secured_debt[region] = SMOOTHI ( Indicated_cost_of_capital_for_secured_debt[region] , Finance_sector_response_time_to_central_bank , Indicated_cost_of_capital_for_secured_debt[region] )
        idx1 = fcol_in_mdf['Cost_of_capital_for_secured_debt']
        idx2 = fcol_in_mdf['Indicated_cost_of_capital_for_secured_debt']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi - 1, idx1:idx1 + 10]) / Finance_sector_response_time_to_central_bank * dt
    
    # Cost_of_capital_for_worker_borrowing[region] = Cost_of_capital_for_secured_debt[region] + Normal_consumer_credit_risk_margin
        idxlhs = fcol_in_mdf['Cost_of_capital_for_worker_borrowing']
        idx1 = fcol_in_mdf['Cost_of_capital_for_secured_debt']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] +  Normal_consumer_credit_risk_margin 
    
    # Cost_of_capital_for_worker_borrowing_smoothed[region] = SMOOTH ( Cost_of_capital_for_worker_borrowing[region] , Time_to_smooth_cost_of_capital_for_workers )
        idx1 = fcol_in_mdf['Cost_of_capital_for_worker_borrowing_smoothed']
        idx2 = fcol_in_mdf['Cost_of_capital_for_worker_borrowing']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1+10] + ( mdf[rowi-1 , idx2:idx2 + 10] - mdf[rowi -1 , idx1:idx1 + 10]) / Time_to_smooth_cost_of_capital_for_workers * dt
    
    # Worker_debt_defaulting_N_yrs_ago[region] = SMOOTHI ( Worker_debt_defaulting[region] , Time_for_defaulting_to_impact_cost_of_capital , 0 )
        idx1 = fcol_in_mdf['Worker_debt_defaulting_N_yrs_ago']
        idx2 = fcol_in_mdf['Worker_debt_defaulting']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi - 1, idx1:idx1 + 10]) / Time_for_defaulting_to_impact_cost_of_capital * dt
    
    # Worker_income_after_tax[region] = Worker_income[region] - Worker_income_and_policy_taxes[region] + Transfer_from_govt_to_workers[region]
        idxlhs = fcol_in_mdf['Worker_income_after_tax']
        idx1 = fcol_in_mdf['Worker_income']
        idx2 = fcol_in_mdf['Worker_income_and_policy_taxes']
        idx3 = fcol_in_mdf['Transfer_from_govt_to_workers']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10]
    
    # Worker_default_ratio[region] = Worker_debt_defaulting_N_yrs_ago[region] / Worker_income_after_tax[region]
        idxlhs = fcol_in_mdf['Worker_default_ratio']
        idx1 = fcol_in_mdf['Worker_debt_defaulting_N_yrs_ago']
        idx2 = fcol_in_mdf['Worker_income_after_tax']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # Effect_of_defaulting_on_debt_obligations_on_cost_of_capital_for_worker_borrowing[region] = WITH LOOKUP ( Worker_default_ratio[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 1 ) , ( 0.25 , 1.04 ) , ( 0.5 , 1.1 ) , ( 0.75 , 1.3 ) , ( 1 , 1.6 ) , ( 1.5 , 2.5 ) , ( 2 , 4 ) ) )
        tabidx = ftab_in_d_table['Effect_of_defaulting_on_debt_obligations_on_cost_of_capital_for_worker_borrowing'] # fetch the correct table
        idx2 = fcol_in_mdf['Effect_of_defaulting_on_debt_obligations_on_cost_of_capital_for_worker_borrowing'] # get the location of the lhs in mdf
        idx3 = fcol_in_mdf['Worker_default_ratio']
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:,0], look[:, 1])
    
    # Worker_interest_payment_obligation[region] = Workers_debt[region] * Cost_of_capital_for_worker_borrowing_smoothed[region] * Effect_of_defaulting_on_debt_obligations_on_cost_of_capital_for_worker_borrowing[region]
        idxlhs = fcol_in_mdf['Worker_interest_payment_obligation']
        idx1 = fcol_in_mdf['Workers_debt']
        idx2 = fcol_in_mdf['Cost_of_capital_for_worker_borrowing_smoothed']
        idx3 = fcol_in_mdf['Effect_of_defaulting_on_debt_obligations_on_cost_of_capital_for_worker_borrowing']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] * mdf[rowi, idx3:idx3 + 10]
    
    # Max_workers_debt_burden[us] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 2 ) , ( 1990 , 3 ) , ( 2000 , 1 ) , ( 2010 , 3 ) , ( 2020 , 2.4 ) , ( 2050 , 2 ) ) ) Max_workers_debt_burden[af] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.5 ) , ( 1990 , 0.5 ) , ( 2000 , 0.65 ) , ( 2010 , 0.7 ) , ( 2020 , 0.7 ) , ( 2050 , 0.7 ) ) ) Max_workers_debt_burden[cn] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.5 ) , ( 1990 , 2.5 ) , ( 2000 , 3 ) , ( 2010 , 4 ) , ( 2020 , 5 ) , ( 2050 , 3 ) ) ) Max_workers_debt_burden[me] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 0.5 ) , ( 2000 , 1 ) , ( 2010 , 1.5 ) , ( 2020 , 2 ) , ( 2050 , 1.5 ) ) ) Max_workers_debt_burden[sa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.5 ) , ( 1990 , 1 ) , ( 2000 , 2 ) , ( 2010 , 2.5 ) , ( 2020 , 2 ) , ( 2050 , 1.5 ) ) ) Max_workers_debt_burden[la] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.1 ) , ( 1990 , 2 ) , ( 2000 , 1 ) , ( 2010 , 1.5 ) , ( 2020 , 2 ) , ( 2050 , 1.5 ) ) ) Max_workers_debt_burden[pa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 3 ) , ( 1990 , 5 ) , ( 2000 , 4 ) , ( 2010 , 4.5 ) , ( 2020 , 5 ) , ( 2050 , 4 ) ) ) Max_workers_debt_burden[ec] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.1 ) , ( 1990 , 1.5 ) , ( 2000 , 0.1 ) , ( 2010 , 1.5 ) , ( 2020 , 2 ) , ( 2050 , 1.5 ) ) ) Max_workers_debt_burden[eu] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 2 ) , ( 1990 , 3 ) , ( 2000 , 3 ) , ( 2010 , 4.5 ) , ( 2020 , 3 ) , ( 2050 , 2 ) ) ) Max_workers_debt_burden[se] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.5 ) , ( 1990 , 2.5 ) , ( 2000 , 2 ) , ( 2010 , 1.5 ) , ( 2020 , 2.5 ) , ( 2050 , 1.5 ) ) )
        tabidx = ftab_in_d_table['Max_workers_debt_burden'] # fetch the correct table
        idx2 = fcol_in_mdf['Max_workers_debt_burden'] # get the location of the lhs in mdf
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(zeit, look[:,0], look[:, j + 1])
    
    # Indicated_max_workers_debt[region] = Worker_income[region] * Max_workers_debt_burden[region]
        idxlhs = fcol_in_mdf['Indicated_max_workers_debt']
        idx1 = fcol_in_mdf['Worker_income']
        idx2 = fcol_in_mdf['Max_workers_debt_burden']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi, idx2:idx2 + 10]
    
    # Smoothed_max_workers_debt[region] = SMOOTH ( Indicated_max_workers_debt[region] , Time_for_max_debt_debt_burden_to_affect_max_debt )
        idx1 = fcol_in_mdf['Smoothed_max_workers_debt']
        idx2 = fcol_in_mdf['Indicated_max_workers_debt']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1+10] + ( mdf[rowi-1 , idx2:idx2 + 10] - mdf[rowi -1 , idx1:idx1 + 10]) / Time_for_max_debt_debt_burden_to_affect_max_debt * dt
    
    # Workers_taking_on_new_debt[region] = MAX ( 0 , ( Smoothed_max_workers_debt[region] - Workers_debt[region] ) / Worker_drawdown_period )
        idxlhs = fcol_in_mdf['Workers_taking_on_new_debt']
        idx1 = fcol_in_mdf['Smoothed_max_workers_debt']
        idx2 = fcol_in_mdf['Workers_debt']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.maximum  (  0  ,  ( mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10] )  /  Worker_drawdown_period  ) 
    
    # Worker_cash_available_to_meet_loan_obligations[region] = ( Worker_income_after_tax[region] + Workers_taking_on_new_debt[region] ) * Fraction_by_law_or_custom_left_for_surviving
        idxlhs = fcol_in_mdf['Worker_cash_available_to_meet_loan_obligations']
        idx1 = fcol_in_mdf['Worker_income_after_tax']
        idx2 = fcol_in_mdf['Workers_taking_on_new_debt']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] )  *  Fraction_by_law_or_custom_left_for_surviving 
    
    # Worker_debt_repayment_obligation[region] = Workers_debt[region] / Workers_payback_period
        idxlhs = fcol_in_mdf['Worker_debt_repayment_obligation']
        idx1 = fcol_in_mdf['Workers_debt']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Workers_payback_period 
    
    # Worker_loan_repayment_obligations[region] = Worker_interest_payment_obligation[region] + Worker_debt_repayment_obligation[region]
        idxlhs = fcol_in_mdf['Worker_loan_repayment_obligations']
        idx1 = fcol_in_mdf['Worker_interest_payment_obligation']
        idx2 = fcol_in_mdf['Worker_debt_repayment_obligation']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10]
    
    # Fraction_of_worker_loan_obligations_met[region] = MIN ( 1 , Worker_cash_available_to_meet_loan_obligations[region] / Worker_loan_repayment_obligations[region] )
        idxlhs = fcol_in_mdf['Fraction_of_worker_loan_obligations_met']
        idx1 = fcol_in_mdf['Worker_cash_available_to_meet_loan_obligations']
        idx2 = fcol_in_mdf['Worker_loan_repayment_obligations']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.minimum  (  1  , mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10] ) 
    
    # Worker_interest_payment_obligation_met[region] = Worker_interest_payment_obligation[region] * Fraction_of_worker_loan_obligations_met[region]
        idxlhs = fcol_in_mdf['Worker_interest_payment_obligation_met']
        idx1 = fcol_in_mdf['Worker_interest_payment_obligation']
        idx2 = fcol_in_mdf['Fraction_of_worker_loan_obligations_met']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # Workers_debt_payback[region] = Worker_debt_repayment_obligation[region] * Fraction_of_worker_loan_obligations_met[region]
        idxlhs = fcol_in_mdf['Workers_debt_payback']
        idx1 = fcol_in_mdf['Worker_debt_repayment_obligation']
        idx2 = fcol_in_mdf['Fraction_of_worker_loan_obligations_met']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # Worker_cashflow_to_owners[region] = Worker_interest_payment_obligation_met[region] + Workers_debt_payback[region] - Workers_taking_on_new_debt[region]
        idxlhs = fcol_in_mdf['Worker_cashflow_to_owners']
        idx1 = fcol_in_mdf['Worker_interest_payment_obligation_met']
        idx2 = fcol_in_mdf['Workers_debt_payback']
        idx3 = fcol_in_mdf['Workers_taking_on_new_debt']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] - mdf[rowi , idx3:idx3 + 10]
    
    # Disposable_income_pp_post_tax_pre_loan_impact[region] = ( Worker_cash_inflow_seasonally_adjusted[region] - Worker_cashflow_to_owners[region] ) / Population[region]
        idxlhs = fcol_in_mdf['Disposable_income_pp_post_tax_pre_loan_impact']
        idx1 = fcol_in_mdf['Worker_cash_inflow_seasonally_adjusted']
        idx2 = fcol_in_mdf['Worker_cashflow_to_owners']
        idx3 = fcol_in_mdf['Population']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10] )  / mdf[rowi , idx3:idx3 + 10]
    
    # SDG_8_Score[region] = IF_THEN_ELSE ( Disposable_income_pp_post_tax_pre_loan_impact < SDG_8_threshold_red , 0 , IF_THEN_ELSE ( Disposable_income_pp_post_tax_pre_loan_impact < SDG_8_threshold_green , 0.5 , 1 ) )
        idxlhs = fcol_in_mdf['SDG_8_Score']
        idx1 = fcol_in_mdf['Disposable_income_pp_post_tax_pre_loan_impact']
        idx2 = fcol_in_mdf['Disposable_income_pp_post_tax_pre_loan_impact']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  ( mdf[rowi , idx1:idx1 + 10] <  SDG_8_threshold_red  ,  0  ,  IF_THEN_ELSE  ( mdf[rowi , idx2:idx2 + 10] <  SDG_8_threshold_green  ,  0.5  ,  1  )  ) 
    
    # Carbon_intensity[region] = ( Total_CO2_emissions[region] - Actual_CO2_taken_directly_out_of_the_atmosphere_ie_direct_air_capture[region] ) / GDP_USED[region] * UNIT_conv_to_tCO2_pr_USD
        idxlhs = fcol_in_mdf['Carbon_intensity']
        idx1 = fcol_in_mdf['Total_CO2_emissions']
        idx2 = fcol_in_mdf['Actual_CO2_taken_directly_out_of_the_atmosphere_ie_direct_air_capture']
        idx3 = fcol_in_mdf['GDP_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10] )  / mdf[rowi , idx3:idx3 + 10] *  UNIT_conv_to_tCO2_pr_USD 
    
    # SDG_9_Score[region] = IF_THEN_ELSE ( Carbon_intensity < SDG_9_threshold_green , 1 , IF_THEN_ELSE ( Carbon_intensity < SDG_9_threshold_red , 0.5 , 0 ) )
        idxlhs = fcol_in_mdf['SDG_9_Score']
        idx1 = fcol_in_mdf['Carbon_intensity']
        idx2 = fcol_in_mdf['Carbon_intensity']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  ( mdf[rowi , idx1:idx1 + 10] <  SDG_9_threshold_green  ,  1  ,  IF_THEN_ELSE  ( mdf[rowi , idx2:idx2 + 10] <  SDG_9_threshold_red  ,  0.5  ,  0  )  ) 
    
    # Owner_income_after_tax_but_before_lending_transactions[region] = Owner_income[region] - Income_and_policy_taxes_paid_by_owners[region]
        idxlhs = fcol_in_mdf['Owner_income_after_tax_but_before_lending_transactions']
        idx1 = fcol_in_mdf['Owner_income']
        idx2 = fcol_in_mdf['Income_and_policy_taxes_paid_by_owners']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10]
    
    # Labour_share_of_GDP[region] = Worker_income_after_tax[region] / ( Worker_income_after_tax[region] + Owner_income_after_tax_but_before_lending_transactions[region] )
        idxlhs = fcol_in_mdf['Labour_share_of_GDP']
        idx1 = fcol_in_mdf['Worker_income_after_tax']
        idx2 = fcol_in_mdf['Worker_income_after_tax']
        idx3 = fcol_in_mdf['Owner_income_after_tax_but_before_lending_transactions']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  ( mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] ) 
    
    # SDG_10_Score[region] = IF_THEN_ELSE ( Labour_share_of_GDP > SDG_10_threshold_green , 1 , IF_THEN_ELSE ( Labour_share_of_GDP > SDG_10_threshold_red , 0.5 , 0 ) )
        idxlhs = fcol_in_mdf['SDG_10_Score']
        idx1 = fcol_in_mdf['Labour_share_of_GDP']
        idx2 = fcol_in_mdf['Labour_share_of_GDP']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  ( mdf[rowi , idx1:idx1 + 10] >  SDG_10_threshold_green  ,  1  ,  IF_THEN_ELSE  ( mdf[rowi , idx2:idx2 + 10] >  SDG_10_threshold_red  ,  0.5  ,  0  )  ) 
    
    # Energy_footprint_pp[region] = ( Total_CO2_emissions[region] ) / Population[region] * UNIT_conv_to_t_ppy
        idxlhs = fcol_in_mdf['Energy_footprint_pp']
        idx1 = fcol_in_mdf['Total_CO2_emissions']
        idx2 = fcol_in_mdf['Population']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] )  / mdf[rowi , idx2:idx2 + 10] *  UNIT_conv_to_t_ppy 
    
    # SDG_11_Score[region] = IF_THEN_ELSE ( Energy_footprint_pp < SDG_11_threshold_green , 1 , IF_THEN_ELSE ( Energy_footprint_pp < SDG_11_threshold_red , 0.5 , 0 ) )
        idxlhs = fcol_in_mdf['SDG_11_Score']
        idx1 = fcol_in_mdf['Energy_footprint_pp']
        idx2 = fcol_in_mdf['Energy_footprint_pp']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  ( mdf[rowi , idx1:idx1 + 10] <  SDG_11_threshold_green  ,  1  ,  IF_THEN_ELSE  ( mdf[rowi , idx2:idx2 + 10] <  SDG_11_threshold_red  ,  0.5  ,  0  )  ) 
    
    # Food_footprint[region] = Nitrogen_syn_use[region] / Population[region]
        idxlhs = fcol_in_mdf['Food_footprint']
        idx1 = fcol_in_mdf['Nitrogen_syn_use']
        idx2 = fcol_in_mdf['Population']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # Food_footprint_kgN_ppy[region] = Food_footprint[region] * UNIT_conv_to_kgN
        idxlhs = fcol_in_mdf['Food_footprint_kgN_ppy']
        idx1 = fcol_in_mdf['Food_footprint']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_kgN 
    
    # SDG_12_threshold_green_PES = SDG12_global_green_threshold / Global_population * UNIT_conv_to_kgN
        idxlhs = fcol_in_mdf['SDG_12_threshold_green_PES']
        idx1 = fcol_in_mdf['Global_population']
        mdf[rowi, idxlhs] =  SDG12_global_green_threshold  / mdf[rowi, idx1] *  UNIT_conv_to_kgN 
    
    # SDG_12_threshold_red_PES = SDG12_global_red_threshold / Global_population * UNIT_conv_to_kgN
        idxlhs = fcol_in_mdf['SDG_12_threshold_red_PES']
        idx1 = fcol_in_mdf['Global_population']
        mdf[rowi, idxlhs] =  SDG12_global_red_threshold  / mdf[rowi, idx1] *  UNIT_conv_to_kgN 
    
    # SDG_12_Score[region] = IF_THEN_ELSE ( Food_footprint_kgN_ppy < SDG_12_threshold_green_PES , 1 , IF_THEN_ELSE ( Food_footprint_kgN_ppy < SDG_12_threshold_red_PES , 0.5 , 0 ) )
        idxlhs = fcol_in_mdf['SDG_12_Score']
        idx1 = fcol_in_mdf['Food_footprint_kgN_ppy']
        idx2 = fcol_in_mdf['SDG_12_threshold_green_PES']
        idx3 = fcol_in_mdf['Food_footprint_kgN_ppy']
        idx4 = fcol_in_mdf['SDG_12_threshold_red_PES']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  ( mdf[rowi , idx1:idx1 + 10] < mdf[rowi , idx2] ,  1  ,  IF_THEN_ELSE  ( mdf[rowi , idx3:idx3 + 10] < mdf[rowi , idx4] ,  0.5  ,  0  )  ) 
    
    # SDG_13_Score[region] = IF_THEN_ELSE ( Temp_surface_anomaly_compared_to_anfang_degC < SDG_13_threshold_green , 1 , IF_THEN_ELSE ( Temp_surface_anomaly_compared_to_anfang_degC < SDG_13_threshold_red , 0.5 , 0 ) )
        idxlhs = fcol_in_mdf['SDG_13_Score']
        idx1 = fcol_in_mdf['Temp_surface_anomaly_compared_to_anfang_degC']
        idx2 = fcol_in_mdf['Temp_surface_anomaly_compared_to_anfang_degC']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  ( mdf[rowi , idx1] <  SDG_13_threshold_green  ,  1  ,  IF_THEN_ELSE  ( mdf[rowi , idx2] <  SDG_13_threshold_red  ,  0.5  ,  0  )  ) 
    
    # SDG_14_Score[region] = IF_THEN_ELSE ( pH_in_surface > SDG_14_threshold_green , 1 , IF_THEN_ELSE ( pH_in_surface > SDG_14_threshold_red , 0.5 , 0 ) )
        idxlhs = fcol_in_mdf['SDG_14_Score']
        idx1 = fcol_in_mdf['pH_in_surface']
        idx2 = fcol_in_mdf['pH_in_surface']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  ( mdf[rowi , idx1] >  SDG_14_threshold_green  ,  1  ,  IF_THEN_ELSE  ( mdf[rowi , idx2] >  SDG_14_threshold_red  ,  0.5  ,  0  )  ) 
    
    # SDG_15_Score[region] = IF_THEN_ELSE ( TROP_with_normal_cover > SDG_15_threshold_green , 1 , IF_THEN_ELSE ( TROP_with_normal_cover > SDG_15_threshold_red , 0.5 , 0 ) )
        idxlhs = fcol_in_mdf['SDG_15_Score']
        idx1 = fcol_in_mdf['TROP_with_normal_cover']
        idx2 = fcol_in_mdf['TROP_with_normal_cover']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  ( mdf[rowi , idx1] >  SDG_15_threshold_green  ,  1  ,  IF_THEN_ELSE  ( mdf[rowi , idx2] >  SDG_15_threshold_red  ,  0.5  ,  0  )  ) 
    
    # SDG_16_Score[region] = IF_THEN_ELSE ( Public_services_pp > SDG_16_threshold_green , 1 , IF_THEN_ELSE ( Public_services_pp > SDG_16_threshold_red , 0.5 , 0 ) )
        idxlhs = fcol_in_mdf['SDG_16_Score']
        idx1 = fcol_in_mdf['Public_services_pp']
        idx2 = fcol_in_mdf['Public_services_pp']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  ( mdf[rowi , idx1:idx1 + 10] >  SDG_16_threshold_green  ,  1  ,  IF_THEN_ELSE  ( mdf[rowi , idx2:idx2 + 10] >  SDG_16_threshold_red  ,  0.5  ,  0  )  ) 
    
    # Social_trust_init_is_1[region] = Social_trust[region] / Social_trust_in_1980
        idxlhs = fcol_in_mdf['Social_trust_init_is_1']
        idx1 = fcol_in_mdf['Social_trust']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Social_trust_in_1980 
    
    # SDG_17_Score[region] = IF_THEN_ELSE ( Social_trust_init_is_1 > SDG_17_threshold_green , 1 , IF_THEN_ELSE ( Social_trust_init_is_1 > SDG_17_threshold_red , 0.5 , 0 ) )
        idxlhs = fcol_in_mdf['SDG_17_Score']
        idx1 = fcol_in_mdf['Social_trust_init_is_1']
        idx2 = fcol_in_mdf['Social_trust_init_is_1']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  ( mdf[rowi , idx1:idx1 + 10] >  SDG_17_threshold_green  ,  1  ,  IF_THEN_ELSE  ( mdf[rowi , idx2:idx2 + 10] >  SDG_17_threshold_red  ,  0.5  ,  0  )  ) 
    
    # All_SDG_Scores[region] = SDG1_Score[region] + SDG_2_Score[region] + SDG_3_Score[region] + SDG4_Score[region] + SDG_5_Score[region] + SDG_6_score[region] + SDG_7_Score[region] + SDG_8_Score[region] + SDG_9_Score[region] + SDG_10_Score[region] + SDG_11_Score[region] + SDG_12_Score[region] + SDG_13_Score[region] + SDG_14_Score[region] + SDG_15_Score[region] + SDG_16_Score[region] + SDG_17_Score[region]
        idxlhs = fcol_in_mdf['All_SDG_Scores']
        idx1 = fcol_in_mdf['SDG1_Score']
        idx2 = fcol_in_mdf['SDG_2_Score']
        idx3 = fcol_in_mdf['SDG_3_Score']
        idx4 = fcol_in_mdf['SDG4_Score']
        idx5 = fcol_in_mdf['SDG_5_Score']
        idx6 = fcol_in_mdf['SDG_6_score']
        idx7 = fcol_in_mdf['SDG_7_Score']
        idx8 = fcol_in_mdf['SDG_8_Score']
        idx9 = fcol_in_mdf['SDG_9_Score']
        idx10 = fcol_in_mdf['SDG_10_Score']
        idx11 = fcol_in_mdf['SDG_11_Score']
        idx12 = fcol_in_mdf['SDG_12_Score']
        idx13 = fcol_in_mdf['SDG_13_Score']
        idx14 = fcol_in_mdf['SDG_14_Score']
        idx15 = fcol_in_mdf['SDG_15_Score']
        idx16 = fcol_in_mdf['SDG_16_Score']
        idx17 = fcol_in_mdf['SDG_17_Score']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] + mdf[rowi , idx4:idx4 + 10] + mdf[rowi , idx5:idx5 + 10] + mdf[rowi , idx6:idx6 + 10] + mdf[rowi , idx7:idx7 + 10] + mdf[rowi , idx8:idx8 + 10] + mdf[rowi , idx9:idx9 + 10] + mdf[rowi , idx10:idx10 + 10] + mdf[rowi , idx11:idx11 + 10] + mdf[rowi , idx12:idx12 + 10] + mdf[rowi , idx13:idx13 + 10] + mdf[rowi , idx14:idx14 + 10] + mdf[rowi , idx15:idx15 + 10] + mdf[rowi , idx16:idx16 + 10] + mdf[rowi , idx17:idx17 + 10]
    
    # CCS_contribution_to_GL[region] = ( CCS_policy[region] * 100 - CCS_policy_Min ) / ( CCS_policy_Max - CCS_policy_Min )
        idxlhs = fcol_in_mdf['CCS_contribution_to_GL']
        idx1 = fcol_in_mdf['CCS_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] *  100  -  CCS_policy_Min  )  /  (  CCS_policy_Max  -  CCS_policy_Min  ) 
    
    # Ctax_contribution_to_GL[region] = ( Ctax_policy[region] * 1 - Ctax_policy_Min ) / ( Ctax_policy_Max - Ctax_policy_Min )
        idxlhs = fcol_in_mdf['Ctax_contribution_to_GL']
        idx1 = fcol_in_mdf['Ctax_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] *  1  -  Ctax_policy_Min  )  /  (  Ctax_policy_Max  -  Ctax_policy_Min  ) 
    
    # DAC_contribution_to_GL[region] = ( DAC_policy[region] * 1 - DAC_policy_Min ) / ( DAC_policy_Max - DAC_policy_Min )
        idxlhs = fcol_in_mdf['DAC_contribution_to_GL']
        idx1 = fcol_in_mdf['DAC_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] *  1  -  DAC_policy_Min  )  /  (  DAC_policy_Max  -  DAC_policy_Min  ) 
    
    # FEHC_contribution_to_GL[region] = ( FEHC_policy[region] * 100 - FEHC_policy_Min ) / ( FEHC_policy_Max - FEHC_policy_Min )
        idxlhs = fcol_in_mdf['FEHC_contribution_to_GL']
        idx1 = fcol_in_mdf['FEHC_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] *  100  -  FEHC_policy_Min  )  /  (  FEHC_policy_Max  -  FEHC_policy_Min  ) 
    
    # FLWR_rounds_via_Excel_future = IF_THEN_ELSE ( zeit >= Round3_start , FLWR_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , FLWR_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , FLWR_R1_via_Excel , FLWR_policy_Min ) ) )
        idxlhs = fcol_in_mdf['FLWR_rounds_via_Excel_future']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  FLWR_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  FLWR_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  FLWR_R1_via_Excel[0:10]  ,  FLWR_policy_Min  )  )  ) 
    
    # FLWR_policy_with_RW[region] = FLWR_rounds_via_Excel_future[region] * Smoothed_Reform_willingness[region] / Inequality_effect_on_energy_TA[region] * Smoothed_Multplier_from_empowerment_on_speed_of_food_TA[region]
        idxlhs = fcol_in_mdf['FLWR_policy_with_RW']
        idx1 = fcol_in_mdf['FLWR_rounds_via_Excel_future']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        idx3 = fcol_in_mdf['Inequality_effect_on_energy_TA']
        idx4 = fcol_in_mdf['Smoothed_Multplier_from_empowerment_on_speed_of_food_TA']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] / mdf[rowi , idx3:idx3 + 10] * mdf[rowi , idx4:idx4 + 10]
     
    # FLWR_pol_div_100[region] = MIN ( FLWR_policy_Max , MAX ( FLWR_policy_Min , FLWR_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['FLWR_pol_div_100']
        idx1 = fcol_in_mdf['FLWR_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], FLWR_policy_Min, FLWR_policy_Max) / 100
    
    # FLWR_policy[region] = SMOOTH3 ( FLWR_pol_div_100[region] , FLWR_Time_to_implement_ISPV_goal )
        idxin = fcol_in_mdf['FLWR_pol_div_100' ]
        idx2 = fcol_in_mdf['FLWR_policy_2']
        idx1 = fcol_in_mdf['FLWR_policy_1']
        idxout = fcol_in_mdf['FLWR_policy']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( FLWR_Time_to_implement_ISPV_goal / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( FLWR_Time_to_implement_ISPV_goal / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( FLWR_Time_to_implement_ISPV_goal / 3) * dt
    
    # FLWR_contribution_to_GL[region] = ( FLWR_policy[region] * 100 - FLWR_policy_Min ) / ( FLWR_policy_Max - FLWR_policy_Min )
        idxlhs = fcol_in_mdf['FLWR_contribution_to_GL']
        idx1 = fcol_in_mdf['FLWR_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] *  100  -  FLWR_policy_Min  )  /  (  FLWR_policy_Max  -  FLWR_policy_Min  ) 
    
    # FTPEE_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , FTPEE_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , FTPEE_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , FTPEE_R1_via_Excel , FTPEE_policy_Min ) ) )
        idxlhs = fcol_in_mdf['FTPEE_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  FTPEE_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  FTPEE_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  FTPEE_R1_via_Excel[0:10]  ,  FTPEE_policy_Min  )  )  ) 
    
    # FTPEE_policy_with_RW[region] = FTPEE_policy_Min + ( FTPEE_rounds_via_Excel[region] - FTPEE_policy_Min ) * Smoothed_Reform_willingness[region] / Inequality_effect_on_energy_TA[region]
        idxlhs = fcol_in_mdf['FTPEE_policy_with_RW']
        idx1 = fcol_in_mdf['FTPEE_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        idx3 = fcol_in_mdf['Inequality_effect_on_energy_TA']
        mdf[rowi, idxlhs:idxlhs + 10] =  FTPEE_policy_Min  +  ( mdf[rowi , idx1:idx1 + 10] -  FTPEE_policy_Min  )  * mdf[rowi , idx2:idx2 + 10] / mdf[rowi , idx3:idx3 + 10]
     
    # FTPEE_pol_div_100[region] = MIN ( FTPEE_policy_Max , MAX ( FTPEE_policy_Min , FTPEE_policy_with_RW[region] ) ) / 1
        idxlhs = fcol_in_mdf['FTPEE_pol_div_100']
        idx1 = fcol_in_mdf['FTPEE_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], FTPEE_policy_Min, FTPEE_policy_Max) / 1
    
    # FTPEE_rate_of_change_policy[region] = SMOOTH3 ( FTPEE_pol_div_100[region] , FTPEE_Time_to_implement_goal )
        idxin = fcol_in_mdf['FTPEE_pol_div_100' ]
        idx2 = fcol_in_mdf['FTPEE_rate_of_change_policy_2']
        idx1 = fcol_in_mdf['FTPEE_rate_of_change_policy_1']
        idxout = fcol_in_mdf['FTPEE_rate_of_change_policy']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( FTPEE_Time_to_implement_goal / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( FTPEE_Time_to_implement_goal / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( FTPEE_Time_to_implement_goal / 3) * dt
    
    # FTPEE_contribution_to_GL[region] = ( FTPEE_rate_of_change_policy[region] * 1 - FTPEE_policy_Min ) / ( FTPEE_policy_Max - FTPEE_policy_Min )
        idxlhs = fcol_in_mdf['FTPEE_contribution_to_GL']
        idx1 = fcol_in_mdf['FTPEE_rate_of_change_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] *  1  -  FTPEE_policy_Min  )  /  (  FTPEE_policy_Max  -  FTPEE_policy_Min  ) 
    
    # FWRP_contribution_to_GL[region] = ( FWRP_policy[region] * 100 - FWRP_policy_Min ) / ( FWRP_policy_Max - FWRP_policy_Min )
        idxlhs = fcol_in_mdf['FWRP_contribution_to_GL']
        idx1 = fcol_in_mdf['FWRP_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] *  100  -  FWRP_policy_Min  )  /  (  FWRP_policy_Max  -  FWRP_policy_Min  ) 
    
    # FPGDC_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , FPGDC_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , FPGDC_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , FPGDC_R1_via_Excel , FPGDC_policy_Min ) ) )
        idxlhs = fcol_in_mdf['FPGDC_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  FPGDC_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  FPGDC_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  FPGDC_R1_via_Excel[0:10]  ,  FPGDC_policy_Min  )  )  ) 
    
    # FPGDC_policy_with_RW[region] = FPGDC_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['FPGDC_policy_with_RW']
        idx1 = fcol_in_mdf['FPGDC_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
     
    # FPGDC_pol_div_100[region] = MIN ( FPGDC_policy_Max , MAX ( FPGDC_policy_Min , FPGDC_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['FPGDC_pol_div_100']
        idx1 = fcol_in_mdf['FPGDC_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], FPGDC_policy_Min, FPGDC_policy_Max) / 100
    
    # FPGDC_logically_constrained[region] = MIN ( FPGDC_policy_Max , MAX ( FPGDC_policy_Min , FPGDC_pol_div_100[region] ) ) * UNIT_conv_to_1_per_yr
        idxlhs = fcol_in_mdf['FPGDC_logically_constrained']
        idx1 = fcol_in_mdf['FPGDC_pol_div_100']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.minimum  (  FPGDC_policy_Max  ,  np.maximum  (  FPGDC_policy_Min  , mdf[rowi , idx1:idx1 + 10] )  )  *  UNIT_conv_to_1_per_yr 
     
    # Public_Debt_cancelling_pulse[region] = ( STEP ( 1 , Time_at_which_govt_public_debt_is_cancelled[region] ) - STEP ( 1 , Time_at_which_govt_public_debt_is_cancelled[region] + Public_Govt_debt_cancelling_spread[region] ) ) * FPGDC_logically_constrained[region]
        idxlhs = fcol_in_mdf['Public_Debt_cancelling_pulse']
        idx1 = fcol_in_mdf['FPGDC_logically_constrained']
        for j in range(0,10):
            mdf[rowi, idxlhs + j] =   (  STEP  (  zeit  ,  1  ,  Time_at_which_govt_public_debt_is_cancelled  )  -  STEP  (  zeit  ,  1  ,  Time_at_which_govt_public_debt_is_cancelled  +  Public_Govt_debt_cancelling_spread  )  )  * mdf[rowi, idx1 + j]
    
    # FPGDC_contribution_to_GL[region] = FPGDC_logically_constrained[region] * Public_Debt_cancelling_pulse[region] / UNIT_conv_to_1_per_yr / UNIT_conv_to_1_per_yr
        idxlhs = fcol_in_mdf['FPGDC_contribution_to_GL']
        idx1 = fcol_in_mdf['FPGDC_logically_constrained']
        idx2 = fcol_in_mdf['Public_Debt_cancelling_pulse']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] /  UNIT_conv_to_1_per_yr  /  UNIT_conv_to_1_per_yr 
    
    # ICTR_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , ICTR_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , ICTR_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , ICTR_R1_via_Excel , ICTR_policy_Min ) ) )
        idxlhs = fcol_in_mdf['ICTR_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  ICTR_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  ICTR_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  ICTR_R1_via_Excel[0:10]  ,  ICTR_policy_Min  )  )  ) 
    
    # ICTR_policy_with_RW[region] = ICTR_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['ICTR_policy_with_RW']
        idx1 = fcol_in_mdf['ICTR_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
     
    # ICTR_pol_div_100[region] = MIN ( ICTR_policy_Max , MAX ( ICTR_policy_Min , ICTR_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['ICTR_pol_div_100']
        idx1 = fcol_in_mdf['ICTR_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], ICTR_policy_Min, ICTR_policy_Max) / 100
    
    # ICTR_policy[region] = SMOOTH3 ( ICTR_pol_div_100[region] , Time_to_implement_UN_policies[region] )
        idxin = fcol_in_mdf['ICTR_pol_div_100' ]
        idx2 = fcol_in_mdf['ICTR_policy_2']
        idx1 = fcol_in_mdf['ICTR_policy_1']
        idxout = fcol_in_mdf['ICTR_policy']
        idx5 = fcol_in_mdf['Time_to_implement_UN_policies']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( mdf[rowi-1, idx5:idx5 + 10] / 3) * dt
    
    # ICTR_contribution_to_GL[region] = 1 - ( ( ICTR_policy[region] * 100 - ICTR_policy_Max ) / ( ICTR_policy_Min - ICTR_policy_Max ) )
        idxlhs = fcol_in_mdf['ICTR_contribution_to_GL']
        idx1 = fcol_in_mdf['ICTR_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  -  (  ( mdf[rowi , idx1:idx1 + 10] *  100  -  ICTR_policy_Max  )  /  (  ICTR_policy_Min  -  ICTR_policy_Max  )  ) 
    
    # IOITR_contribution_to_GL[region] = 1 - ( ( IOITR_policy[region] * 100 - IOITR_policy_Max ) / ( IOITR_policy_Min - IOITR_policy_Max ) )
        idxlhs = fcol_in_mdf['IOITR_contribution_to_GL']
        idx1 = fcol_in_mdf['IOITR_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  -  (  ( mdf[rowi , idx1:idx1 + 10] *  100  -  IOITR_policy_Max  )  /  (  IOITR_policy_Min  -  IOITR_policy_Max  )  ) 
    
    # ISPV_contribution_to_GL[region] = ( wind_and_PV_el_share_max[region] * 100 - ISPV_policy_Min ) / ( ISPV_policy_Max - ISPV_policy_Min )
        idxlhs = fcol_in_mdf['ISPV_contribution_to_GL']
        idx1 = fcol_in_mdf['wind_and_PV_el_share_max']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] *  100  -  ISPV_policy_Min  )  /  (  ISPV_policy_Max  -  ISPV_policy_Min  ) 
    
    # IWITR_contribution_to_GL[region] = 1 - ( ( IWITR_policy[region] * 100 - IWITR_policy_Max ) / ( IWITR_policy_Min - IWITR_policy_Max ) )
        idxlhs = fcol_in_mdf['IWITR_contribution_to_GL']
        idx1 = fcol_in_mdf['IWITR_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  -  (  ( mdf[rowi , idx1:idx1 + 10] *  100  -  IWITR_policy_Max  )  /  (  IWITR_policy_Min  -  IWITR_policy_Max  )  ) 
    
    # Lfrac_contribution_to_GL[region] = Lfrac_policy[region]
        idxlhs = fcol_in_mdf['Lfrac_contribution_to_GL']
        idx1 = fcol_in_mdf['Lfrac_policy']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10]
    
    # LPB_contribution_to_GL[region] = ( LPB_policy[region] * 100 - LPB_policy_Min ) / ( LPB_policy_Max - LPB_policy_Min )
        idxlhs = fcol_in_mdf['LPB_contribution_to_GL']
        idx1 = fcol_in_mdf['LPB_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] *  100  -  LPB_policy_Min  )  /  (  LPB_policy_Max  -  LPB_policy_Min  ) 
    
    # LPBgrant_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , LPBgrant_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , LPBgrant_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , LPBgrant_R1_via_Excel , LPBgrant_policy_Min ) ) )
        idxlhs = fcol_in_mdf['LPBgrant_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  LPBgrant_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  LPBgrant_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  LPBgrant_R1_via_Excel[0:10]  ,  LPBgrant_policy_Min  )  )  ) 
    
    # LPBgrant_policy_with_RW[region] = LPBgrant_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['LPBgrant_policy_with_RW']
        idx1 = fcol_in_mdf['LPBgrant_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
     
    # LPBgrant_pol_div_100[region] = MIN ( LPBgrant_policy_Max , MAX ( LPBgrant_policy_Min , LPBgrant_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['LPBgrant_pol_div_100']
        idx1 = fcol_in_mdf['LPBgrant_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], LPBgrant_policy_Min, LPBgrant_policy_Max) / 100
    
    # LPBgrant_policy[region] = SMOOTH3 ( LPBgrant_pol_div_100[region] , LPBgrant_Time_to_implement_policy )
        idxin = fcol_in_mdf['LPBgrant_pol_div_100' ]
        idx2 = fcol_in_mdf['LPBgrant_policy_2']
        idx1 = fcol_in_mdf['LPBgrant_policy_1']
        idxout = fcol_in_mdf['LPBgrant_policy']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( LPBgrant_Time_to_implement_policy / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( LPBgrant_Time_to_implement_policy / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( LPBgrant_Time_to_implement_policy / 3) * dt
    
    # LPBgrant_contribution_to_GL[region] = ( LPBgrant_policy[region] * 100 - LPBgrant_policy_Min ) / ( LPBgrant_policy_Max - LPBgrant_policy_Min )
        idxlhs = fcol_in_mdf['LPBgrant_contribution_to_GL']
        idx1 = fcol_in_mdf['LPBgrant_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] *  100  -  LPBgrant_policy_Min  )  /  (  LPBgrant_policy_Max  -  LPBgrant_policy_Min  ) 
    
    # LPBsplit_contribution_to_GL[region] = ( LPBsplit_policy[region] * 100 - LPBsplit_policy_Min ) / ( LPBsplit_policy_Max - LPBsplit_policy_Min )
        idxlhs = fcol_in_mdf['LPBsplit_contribution_to_GL']
        idx1 = fcol_in_mdf['LPBsplit_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] *  100  -  LPBsplit_policy_Min  )  /  (  LPBsplit_policy_Max  -  LPBsplit_policy_Min  ) 
    
    # NEP_contribution_to_GL[region] = ( NEP_policy[region] * 100 - NEP_policy_Min ) / ( NEP_policy_Max - NEP_policy_Min )
        idxlhs = fcol_in_mdf['NEP_contribution_to_GL']
        idx1 = fcol_in_mdf['NEP_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] *  100  -  NEP_policy_Min  )  /  (  NEP_policy_Max  -  NEP_policy_Min  ) 
    
    # RMDR_contribution_to_GL[region] = ( RMDR_policy[region] * 100 - RMDR_policy_Min ) / ( RMDR_policy_Max - RMDR_policy_Min )
        idxlhs = fcol_in_mdf['RMDR_contribution_to_GL']
        idx1 = fcol_in_mdf['RMDR_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] *  100  -  RMDR_policy_Min  )  /  (  RMDR_policy_Max  -  RMDR_policy_Min  ) 
    
    # SGMP_contribution_to_GL[region] = ( SGMP_policy[region] * 100 - SGMP_policy_Min ) / ( SGMP_policy_Max - SGMP_policy_Min )
        idxlhs = fcol_in_mdf['SGMP_contribution_to_GL']
        idx1 = fcol_in_mdf['SGMP_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] *  100  -  SGMP_policy_Min  )  /  (  SGMP_policy_Max  -  SGMP_policy_Min  ) 
    
    # SGRPI_contribution_to_GL[region] = 1 - ( ( SGRPI_policy[region] * 100 - SGRPI_policy_Max ) / ( SGRPI_policy_Min - SGRPI_policy_Max ) )
        idxlhs = fcol_in_mdf['SGRPI_contribution_to_GL']
        idx1 = fcol_in_mdf['SGRPI_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  -  (  ( mdf[rowi , idx1:idx1 + 10] *  100  -  SGRPI_policy_Max  )  /  (  SGRPI_policy_Min  -  SGRPI_policy_Max  )  ) 
    
    # SSDGR_contribution_to_GL[region] = 1 - ( ( SSGDR_policy[region] * 1 - SSGDR_policy_Max ) / ( SSGDR_policy_Min - SSGDR_policy_Max ) )
        idxlhs = fcol_in_mdf['SSDGR_contribution_to_GL']
        idx1 = fcol_in_mdf['SSGDR_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  -  (  ( mdf[rowi , idx1:idx1 + 10] *  1  -  SSGDR_policy_Max  )  /  (  SSGDR_policy_Min  -  SSGDR_policy_Max  )  ) 
    
    # StrUP_contribution_to_GL[region] = ( StrUP_policy[region] * 100 - StrUP_policy_Min ) / ( StrUP_policy_Max - StrUP_policy_Min )
        idxlhs = fcol_in_mdf['StrUP_contribution_to_GL']
        idx1 = fcol_in_mdf['StrUP_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] *  100  -  StrUP_policy_Min  )  /  (  StrUP_policy_Max  -  StrUP_policy_Min  ) 
    
    # Wreaction_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , Wreaction_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , Wreaction_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , Wreaction_R1_via_Excel , WReaction_policy_Min ) ) )
        idxlhs = fcol_in_mdf['Wreaction_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  Wreaction_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  Wreaction_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  Wreaction_R1_via_Excel[0:10]  ,  Wreaction_policy_Min  )  )  ) 
    
    # Wreaction_policy_with_RW[region] = Wreaction_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['Wreaction_policy_with_RW']
        idx1 = fcol_in_mdf['Wreaction_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
     
    # Wreaction_pol_div_100[region] = MIN ( WReaction_policy_Max , MAX ( WReaction_policy_Min , Wreaction_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['Wreaction_pol_div_100']
        idx1 = fcol_in_mdf['Wreaction_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], Wreaction_policy_Min, Wreaction_policy_Max) / 100
    
    # WReaction_policy[region] = SMOOTH3 ( Wreaction_pol_div_100[region] , WReaction_Time_to_implement_policy )
        idxin = fcol_in_mdf['Wreaction_pol_div_100' ]
        idx2 = fcol_in_mdf['WReaction_policy_2']
        idx1 = fcol_in_mdf['WReaction_policy_1']
        idxout = fcol_in_mdf['WReaction_policy']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( WReaction_Time_to_implement_policy / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( WReaction_Time_to_implement_policy / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( WReaction_Time_to_implement_policy / 3) * dt
    
    # WReaction_contribution_to_GL[region] = ( WReaction_policy[region] * 100 - WReaction_policy_Min ) / ( WReaction_policy_Max - WReaction_policy_Min )
        idxlhs = fcol_in_mdf['WReaction_contribution_to_GL']
        idx1 = fcol_in_mdf['WReaction_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] *  100  -  Wreaction_policy_Min  )  /  (  Wreaction_policy_Max  -  Wreaction_policy_Min  ) 
    
    # XtaxCom_contribution_to_GL[region] = ( XtaxCom_policy[region] * 100 - XtaxCom_policy_Min ) / ( XtaxCom_policy_Max - XtaxCom_policy_Min )
        idxlhs = fcol_in_mdf['XtaxCom_contribution_to_GL']
        idx1 = fcol_in_mdf['XtaxCom_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] *  100  -  XtaxCom_policy_Min  )  /  (  XtaxCom_policy_Max  -  XtaxCom_policy_Min  ) 
    
    # Xtaxfrac_contribution_to_GL[region] = ( Xtaxfrac_policy[region] * 100 - Xtaxfrac_policy_Min ) / ( Xtaxfrac_policy_Max - Xtaxfrac_policy_Min )
        idxlhs = fcol_in_mdf['Xtaxfrac_contribution_to_GL']
        idx1 = fcol_in_mdf['Xtaxfrac_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] *  100  -  XtaxFrac_policy_Min  )  /  (  XtaxFrac_policy_Max  -  XtaxFrac_policy_Min  ) 
    
    # XtaxRateEmp_contribution_to_GL[region] = ( XtaxRateEmp_policy[region] * 100 - XtaxRateEmp_policy_Min ) / ( XtaxRateEmp_policy_Max - XtaxRateEmp_policy_Min )
        idxlhs = fcol_in_mdf['XtaxRateEmp_contribution_to_GL']
        idx1 = fcol_in_mdf['XtaxRateEmp_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] *  100  -  XtaxEmp_policy_Min  )  /  (  XtaxEmp_policy_Max  -  XtaxEmp_policy_Min  ) 
    
    # TOW_contribution_to_GL[region] = 1 - ( ( TOW_policy[region] * 100 / TOW_UNIT_conv_to_pa - TOW_policy_Max ) / ( TOW_policy_Min - TOW_policy_Max ) )
        idxlhs = fcol_in_mdf['TOW_contribution_to_GL']
        idx1 = fcol_in_mdf['TOW_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  -  (  ( mdf[rowi , idx1:idx1 + 10] *  100  /  TOW_UNIT_conv_to_pa  -  TOW_policy_Max  )  /  (  TOW_policy_Min  -  TOW_policy_Max  )  ) 
    
    # RIPLGF_contribution_to_GL[region] = 1 - ( ( RIPLGF_policy[region] * 100 - RIPLGF_policy_Max ) / ( RIPLGF_policy_Min - RIPLGF_policy_Max ) )
        idxlhs = fcol_in_mdf['RIPLGF_contribution_to_GL']
        idx1 = fcol_in_mdf['RIPLGF_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  -  (  ( mdf[rowi , idx1:idx1 + 10] *  100  -  RIPLGF_policy_Max  )  /  (  RIPLGF_policy_Min  -  RIPLGF_policy_Max  )  ) 
    
    # REFOREST_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , REFOREST_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , REFOREST_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , REFOREST_R1_via_Excel , REFOREST_policy_Min ) ) )
        idxlhs = fcol_in_mdf['REFOREST_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  REFOREST_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  REFOREST_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  REFOREST_R1_via_Excel[0:10]  ,  REFOREST_policy_Min  )  )  ) 
    
    # REFOREST_policy_with_RW[region] = REFOREST_rounds_via_Excel[region] * Smoothed_Reform_willingness[region] / Inequality_effect_on_energy_TA[region] * Smoothed_Multplier_from_empowerment_on_speed_of_food_TA[region]
        idxlhs = fcol_in_mdf['REFOREST_policy_with_RW']
        idx1 = fcol_in_mdf['REFOREST_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        idx3 = fcol_in_mdf['Inequality_effect_on_energy_TA']
        idx4 = fcol_in_mdf['Smoothed_Multplier_from_empowerment_on_speed_of_food_TA']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] / mdf[rowi , idx3:idx3 + 10] * mdf[rowi , idx4:idx4 + 10]
     
    # REFOREST_pol_div_100[region] = MIN ( REFOREST_policy_Max , MAX ( REFOREST_policy_Min , REFOREST_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['REFOREST_pol_div_100']
        idx1 = fcol_in_mdf['REFOREST_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], REFOREST_policy_Min, REFOREST_policy_Max) / 100
    
    # REFOREST_policy[region] = SMOOTH3 ( REFOREST_pol_div_100[region] , REFOREST_policy_Time_to_implement_goal )
        idxin = fcol_in_mdf['REFOREST_pol_div_100' ]
        idx2 = fcol_in_mdf['REFOREST_policy_2']
        idx1 = fcol_in_mdf['REFOREST_policy_1']
        idxout = fcol_in_mdf['REFOREST_policy']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( REFOREST_policy_Time_to_implement_goal / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( REFOREST_policy_Time_to_implement_goal / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( REFOREST_policy_Time_to_implement_goal / 3) * dt
    
    # REFOREST_policy_contribution_to_GL[region] = ( REFOREST_policy[region] * 100 - REFOREST_policy_Min ) / ( REFOREST_policy_Max - REFOREST_policy_Min )
        idxlhs = fcol_in_mdf['REFOREST_policy_contribution_to_GL']
        idx1 = fcol_in_mdf['REFOREST_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] *  100  -  REFOREST_policy_Min  )  /  (  REFOREST_policy_Max  -  REFOREST_policy_Min  ) 
    
    # Which_Scenario_is_run[region] = ( CCS_contribution_to_GL[region] + Ctax_contribution_to_GL[region] + DAC_contribution_to_GL[region] + FEHC_contribution_to_GL[region] + FLWR_contribution_to_GL[region] + FTPEE_contribution_to_GL[region] + FWRP_contribution_to_GL[region] + FPGDC_contribution_to_GL[region] + ICTR_contribution_to_GL[region] + IOITR_contribution_to_GL[region] + ISPV_contribution_to_GL[region] + IWITR_contribution_to_GL[region] + Lfrac_contribution_to_GL[region] + LPB_contribution_to_GL[region] + LPBgrant_contribution_to_GL[region] + LPBsplit_contribution_to_GL[region] + NEP_contribution_to_GL[region] + RMDR_contribution_to_GL[region] + SGMP_contribution_to_GL[region] + SGRPI_contribution_to_GL[region] + SSDGR_contribution_to_GL[region] + StrUP_contribution_to_GL[region] + WReaction_contribution_to_GL[region] + XtaxCom_contribution_to_GL[region] + Xtaxfrac_contribution_to_GL[region] + XtaxRateEmp_contribution_to_GL[region] + TOW_contribution_to_GL[region] + RIPLGF_contribution_to_GL[region] + REFOREST_policy_contribution_to_GL[region] ) / Nbr_of_policies
        idxlhs = fcol_in_mdf['Which_Scenario_is_run']
        idx1 = fcol_in_mdf['CCS_contribution_to_GL']
        idx2 = fcol_in_mdf['Ctax_contribution_to_GL']
        idx3 = fcol_in_mdf['DAC_contribution_to_GL']
        idx4 = fcol_in_mdf['FEHC_contribution_to_GL']
        idx5 = fcol_in_mdf['FLWR_contribution_to_GL']
        idx6 = fcol_in_mdf['FTPEE_contribution_to_GL']
        idx7 = fcol_in_mdf['FWRP_contribution_to_GL']
        idx8 = fcol_in_mdf['FPGDC_contribution_to_GL']
        idx9 = fcol_in_mdf['ICTR_contribution_to_GL']
        idx10 = fcol_in_mdf['IOITR_contribution_to_GL']
        idx11 = fcol_in_mdf['ISPV_contribution_to_GL']
        idx12 = fcol_in_mdf['IWITR_contribution_to_GL']
        idx13 = fcol_in_mdf['Lfrac_contribution_to_GL']
        idx14 = fcol_in_mdf['LPB_contribution_to_GL']
        idx15 = fcol_in_mdf['LPBgrant_contribution_to_GL']
        idx16 = fcol_in_mdf['LPBsplit_contribution_to_GL']
        idx17 = fcol_in_mdf['NEP_contribution_to_GL']
        idx18 = fcol_in_mdf['RMDR_contribution_to_GL']
        idx19 = fcol_in_mdf['SGMP_contribution_to_GL']
        idx20 = fcol_in_mdf['SGRPI_contribution_to_GL']
        idx21 = fcol_in_mdf['SSDGR_contribution_to_GL']
        idx22 = fcol_in_mdf['StrUP_contribution_to_GL']
        idx23 = fcol_in_mdf['WReaction_contribution_to_GL']
        idx24 = fcol_in_mdf['XtaxCom_contribution_to_GL']
        idx25 = fcol_in_mdf['Xtaxfrac_contribution_to_GL']
        idx26 = fcol_in_mdf['XtaxRateEmp_contribution_to_GL']
        idx27 = fcol_in_mdf['TOW_contribution_to_GL']
        idx28 = fcol_in_mdf['RIPLGF_contribution_to_GL']
        idx29 = fcol_in_mdf['REFOREST_policy_contribution_to_GL']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] + mdf[rowi , idx4:idx4 + 10] + mdf[rowi , idx5:idx5 + 10] + mdf[rowi , idx6:idx6 + 10] + mdf[rowi , idx7:idx7 + 10] + mdf[rowi , idx8:idx8 + 10] + mdf[rowi , idx9:idx9 + 10] + mdf[rowi , idx10:idx10 + 10] + mdf[rowi , idx11:idx11 + 10] + mdf[rowi , idx12:idx12 + 10] + mdf[rowi , idx13:idx13 + 10] + mdf[rowi , idx14:idx14 + 10] + mdf[rowi , idx15:idx15 + 10] + mdf[rowi , idx16:idx16 + 10] + mdf[rowi , idx17:idx17 + 10] + mdf[rowi , idx18:idx18 + 10] + mdf[rowi , idx19:idx19 + 10] + mdf[rowi , idx20:idx20 + 10] + mdf[rowi , idx21:idx21 + 10] + mdf[rowi , idx22:idx22 + 10] + mdf[rowi , idx23:idx23 + 10] + mdf[rowi , idx24:idx24 + 10] + mdf[rowi , idx25:idx25 + 10] + mdf[rowi , idx26:idx26 + 10] + mdf[rowi , idx27:idx27 + 10] + mdf[rowi , idx28:idx28 + 10] + mdf[rowi , idx29:idx29 + 10] )  /  Nbr_of_policies 
    
    # Regional_population_as_fraction_of_total[region] = Population[region] / Global_population
        idxlhs = fcol_in_mdf['Regional_population_as_fraction_of_total']
        idx1 = fcol_in_mdf['Population']
        idx2 = fcol_in_mdf['Global_population']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2]
     
    # Which_Scenario_is_run_globally = Which_Scenario_is_run[us] * Regional_population_as_fraction_of_total[us] + Which_Scenario_is_run[af] * Regional_population_as_fraction_of_total[af] + Which_Scenario_is_run[cn] * Regional_population_as_fraction_of_total[cn] + Which_Scenario_is_run[me] * Regional_population_as_fraction_of_total[me] + Which_Scenario_is_run[sa] * Regional_population_as_fraction_of_total[sa] + Which_Scenario_is_run[la] * Regional_population_as_fraction_of_total[la] + Which_Scenario_is_run[pa] * Regional_population_as_fraction_of_total[pa] + Which_Scenario_is_run[ec] * Regional_population_as_fraction_of_total[ec] + Which_Scenario_is_run[eu] * Regional_population_as_fraction_of_total[eu] + Which_Scenario_is_run[se] * Regional_population_as_fraction_of_total[se]
        idxlhs = fcol_in_mdf['Which_Scenario_is_run_globally']
        idx1 = fcol_in_mdf['Which_Scenario_is_run']
        idx2 = fcol_in_mdf['Regional_population_as_fraction_of_total']
        mdf[rowi, idxlhs] = ( mdf[rowi, idx1 + 0 ] *  mdf[rowi, idx2 + 0 ]+ mdf[rowi, idx1 + 1 ] *  mdf[rowi, idx2 + 1 ]+ mdf[rowi, idx1 + 2 ] *  mdf[rowi, idx2 + 2 ]+ mdf[rowi, idx1 + 3 ] *  mdf[rowi, idx2 + 3 ]+ mdf[rowi, idx1 + 4 ] *  mdf[rowi, idx2 + 4 ]+ mdf[rowi, idx1 + 5 ] *  mdf[rowi, idx2 + 5 ]+ mdf[rowi, idx1 + 6 ] *  mdf[rowi, idx2 + 6 ]+ mdf[rowi, idx1 + 7 ] *  mdf[rowi, idx2 + 7 ]+ mdf[rowi, idx1 + 8 ] *  mdf[rowi, idx2 + 8 ]+ mdf[rowi, idx1 + 9 ] *  mdf[rowi, idx2 + 9 ] )
    
    # Annual_reduction_in_UAC = Annual_reduction_in_UAC_TLTL * ( 1 - Which_Scenario_is_run_globally ) + Annual_reduction_in_UAC_GL * Which_Scenario_is_run_globally
        idxlhs = fcol_in_mdf['Annual_reduction_in_UAC']
        idx1 = fcol_in_mdf['Which_Scenario_is_run_globally']
        idx2 = fcol_in_mdf['Which_Scenario_is_run_globally']
        mdf[rowi, idxlhs] =  Annual_reduction_in_UAC_TLTL  *  (  1  - mdf[rowi, idx1] )  +  Annual_reduction_in_UAC_GL  * mdf[rowi, idx2]
    
    # WSO_effect_on_available_capital[region] = 1 + Slope_of_Worker_share_of_output_with_unemployment_effect_on_available_capital * ( Worker_share_of_output_with_unemployment_effect[region] / Worker_share_of_output_with_unemployment_effect_in_1980[region] - 1 )
        idxlhs = fcol_in_mdf['WSO_effect_on_available_capital']
        idx1 = fcol_in_mdf['Worker_share_of_output_with_unemployment_effect']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  +  Slope_of_Worker_share_of_output_with_unemployment_effect_on_available_capital  *  ( mdf[rowi , idx1:idx1 + 10] /  Worker_share_of_output_with_unemployment_effect_in_1980[0:10]  -  1  ) 
    
    # Corporate_borrowing_cost[region] = Cost_of_capital_for_secured_debt[region] + Normal_corporate_credit_risk_margin
        idxlhs = fcol_in_mdf['Corporate_borrowing_cost']
        idx1 = fcol_in_mdf['Cost_of_capital_for_secured_debt']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] +  Normal_corporate_credit_risk_margin 
    
    # Corporate_borrowing_cost_N_years_ago[region] = SMOOTHI ( Corporate_borrowing_cost[region] , Years_for_CBC_comparison , Corporate_borrowing_cost_in_1980[region] )
        idx1 = fcol_in_mdf['Corporate_borrowing_cost_N_years_ago']
        idx2 = fcol_in_mdf['Corporate_borrowing_cost']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi - 1, idx1:idx1 + 10]) / Years_for_CBC_comparison * dt
    
    # CBC_rate_denominator = IF_THEN_ELSE ( SWITCH_CBC_effect_on_available_capital == 1 , Corporate_borrowing_cost_in_1980 , Corporate_borrowing_cost_N_years_ago )
        idxlhs = fcol_in_mdf['CBC_rate_denominator']
        idx1 = fcol_in_mdf['Corporate_borrowing_cost_N_years_ago']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  SWITCH_CBC_effect_on_available_capital[0:10]  ==  1  ,  Corporate_borrowing_cost_in_1980[0:10]  , mdf[rowi , idx1:idx1 + 10] ) 
    
    # Corporate_borrowing_cost_eff_on_available_capital[region] = 1 + Slope_of_Corporate_borrowing_cost_eff_on_available_capital[region] * ( Corporate_borrowing_cost[region] / CBC_rate_denominator[region] - 1 )
        idxlhs = fcol_in_mdf['Corporate_borrowing_cost_eff_on_available_capital']
        idx1 = fcol_in_mdf['Corporate_borrowing_cost']
        idx2 = fcol_in_mdf['CBC_rate_denominator']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  +  Slope_of_Corporate_borrowing_cost_eff_on_available_capital[0:10]  *  ( mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10] -  1  ) 
    
    # Perceived_demand_imblance[region] = SMOOTH3I ( Demand_imbalance[region] , Time_to_form_an_opinion_about_demand_imbalance , Dmd_imbalance_in_1980[region] )
        idxlhs = fcol_in_mdf['Perceived_demand_imblance']
        idxin = fcol_in_mdf['Demand_imbalance']
        idx2 = fcol_in_mdf['Perceived_demand_imblance_2']
        idx1 = fcol_in_mdf['Perceived_demand_imblance_1']
        idxout = fcol_in_mdf['Perceived_demand_imblance']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( Time_to_form_an_opinion_about_demand_imbalance / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( Time_to_form_an_opinion_about_demand_imbalance / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( Time_to_form_an_opinion_about_demand_imbalance / 3) * dt
    
    # Eff_of_dmd_imbalance_on_flow_of_available_capital[region] = 1 + Slope_of_Eff_of_dmd_imbalance_on_flow_of_available_capital * ( Perceived_demand_imblance[region] / Dmd_imbalance_in_1980[region] - 1 )
        idxlhs = fcol_in_mdf['Eff_of_dmd_imbalance_on_flow_of_available_capital']
        idx1 = fcol_in_mdf['Perceived_demand_imblance']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  +  Slope_of_Eff_of_dmd_imbalance_on_flow_of_available_capital  *  ( mdf[rowi , idx1:idx1 + 10] /  Dmd_imbalance_in_1980  -  1  ) 
    
    # Fraction_of_available_capital_to_new_capacity[region] = ( WSO_effect_on_available_capital[region] + Corporate_borrowing_cost_eff_on_available_capital[region] + Eff_of_dmd_imbalance_on_flow_of_available_capital[region] ) / 3
        idxlhs = fcol_in_mdf['Fraction_of_available_capital_to_new_capacity']
        idx1 = fcol_in_mdf['WSO_effect_on_available_capital']
        idx2 = fcol_in_mdf['Corporate_borrowing_cost_eff_on_available_capital']
        idx3 = fcol_in_mdf['Eff_of_dmd_imbalance_on_flow_of_available_capital']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] )  /  3 
    
    # Annual_shortfall_fraction_of_available_private_capital[region] = IF_THEN_ELSE ( Fraction_of_available_capital_to_new_capacity > 1 , Fraction_of_available_capital_to_new_capacity - 1 , 0 )
        idxlhs = fcol_in_mdf['Annual_shortfall_fraction_of_available_private_capital']
        idx1 = fcol_in_mdf['Fraction_of_available_capital_to_new_capacity']
        idx2 = fcol_in_mdf['Fraction_of_available_capital_to_new_capacity']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  ( mdf[rowi , idx1:idx1 + 10] >  1  , mdf[rowi , idx2:idx2 + 10] -  1  ,  0  ) 
    
    # Worker_consumption_demand[region] = Worker_cash_inflow_seasonally_adjusted[region] * Worker_consumption_fraction
        idxlhs = fcol_in_mdf['Worker_consumption_demand']
        idx1 = fcol_in_mdf['Worker_cash_inflow_seasonally_adjusted']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  Worker_consumption_fraction 
    
    # Workers_savings[region] = Worker_cash_inflow_seasonally_adjusted[region] - Worker_consumption_demand[region]
        idxlhs = fcol_in_mdf['Workers_savings']
        idx1 = fcol_in_mdf['Worker_cash_inflow_seasonally_adjusted']
        idx2 = fcol_in_mdf['Worker_consumption_demand']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10]
    
    # Owner_cash_inflow_seasonally_adjusted[region] = SMOOTHI ( Owner_cash_inflow_with_lending_transactions[region] , Time_to_adjust_owners_budget , Owner_income_in_1980[region] )
        idx1 = fcol_in_mdf['Owner_cash_inflow_seasonally_adjusted']
        idx2 = fcol_in_mdf['Owner_cash_inflow_with_lending_transactions']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi - 1, idx1:idx1 + 10]) / Time_to_adjust_owners_budget * dt
    
    # Owners_savings[region] = Owner_cash_inflow_seasonally_adjusted[region] * Owner_saving_fraction[region]
        idxlhs = fcol_in_mdf['Owners_savings']
        idx1 = fcol_in_mdf['Owner_cash_inflow_seasonally_adjusted']
        idx2 = fcol_in_mdf['Owner_saving_fraction']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # Total_savings[region] = Workers_savings[region] + Owners_savings[region]
        idxlhs = fcol_in_mdf['Total_savings']
        idx1 = fcol_in_mdf['Workers_savings']
        idx2 = fcol_in_mdf['Owners_savings']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10]
    
    # Available_private_capital_for_investment[region] = Total_savings[region] + Foreign_capital_inflow[region]
        idxlhs = fcol_in_mdf['Available_private_capital_for_investment']
        idx1 = fcol_in_mdf['Total_savings']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] +  Foreign_capital_inflow 
    
    # Annual_shortfall_of_available_private_capital[region] = Available_private_capital_for_investment[region] * Annual_shortfall_fraction_of_available_private_capital[region]
        idxlhs = fcol_in_mdf['Annual_shortfall_of_available_private_capital']
        idx1 = fcol_in_mdf['Available_private_capital_for_investment']
        idx2 = fcol_in_mdf['Annual_shortfall_fraction_of_available_private_capital']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # Annual_surplus_fraction_of_available_private_capital[region] = IF_THEN_ELSE ( Fraction_of_available_capital_to_new_capacity < 1 , 1 - Fraction_of_available_capital_to_new_capacity , 0 )
        idxlhs = fcol_in_mdf['Annual_surplus_fraction_of_available_private_capital']
        idx1 = fcol_in_mdf['Fraction_of_available_capital_to_new_capacity']
        idx2 = fcol_in_mdf['Fraction_of_available_capital_to_new_capacity']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  ( mdf[rowi , idx1:idx1 + 10] <  1  ,  1  - mdf[rowi , idx2:idx2 + 10] ,  0  ) 
    
    # Annual_surplus_of_available_private_capital[region] = Available_private_capital_for_investment[region] * Annual_surplus_fraction_of_available_private_capital[region]
        idxlhs = fcol_in_mdf['Annual_surplus_of_available_private_capital']
        idx1 = fcol_in_mdf['Available_private_capital_for_investment']
        idx2 = fcol_in_mdf['Annual_surplus_fraction_of_available_private_capital']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # Temp_diff_relevant_for_melting_or_freezing_anfang = Temp_surface - ( Temp_surface_1850 - SCALE_converter_zero_C_to_K ) * UNIT_conversion_Celsius_to_Kelvin_C_p_K
        idxlhs = fcol_in_mdf['Temp_diff_relevant_for_melting_or_freezing_anfang']
        idx1 = fcol_in_mdf['Temp_surface']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] -  (  Temp_surface_1850  -  SCALE_converter_zero_C_to_K  )  *  UNIT_conversion_Celsius_to_Kelvin_C_p_K 
    
    # Effect_of_temp_on_melting_antarctic_ice = 1 + Slope_temp_vs_antarctic_ice_melting * ( ( Temp_diff_relevant_for_melting_or_freezing_anfang / Ref_temp_difference_for_antarctic_ice_melting_3_degC ) - 1 )
        idxlhs = fcol_in_mdf['Effect_of_temp_on_melting_antarctic_ice']
        idx1 = fcol_in_mdf['Temp_diff_relevant_for_melting_or_freezing_anfang']
        mdf[rowi, idxlhs] =  1  +  Slope_temp_vs_antarctic_ice_melting  *  (  ( mdf[rowi, idx1] /  Ref_temp_difference_for_antarctic_ice_melting_3_degC  )  -  1  ) 
    
    # Heat_in_atmosphere_current_to_initial_ratio = Heat_in_atmosphere_ZJ / Heat_in_atmosphere_in_1850_ZJ
        idxlhs = fcol_in_mdf['Heat_in_atmosphere_current_to_initial_ratio']
        idx1 = fcol_in_mdf['Heat_in_atmosphere_ZJ']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Heat_in_atmosphere_in_1850_ZJ 
    
    # Effect_of_heat_in_atm_on_melting_ice_cut_off = WITH LOOKUP ( Heat_in_atmosphere_current_to_initial_ratio , ( [ ( 0 , 0 ) - ( 1 , 1 ) ] , ( 0 , 0 ) , ( 0.16 , 0.85 ) , ( 0.5 , 1 ) , ( 1 , 1 ) ) )
        tabidx = ftab_in_d_table['Effect_of_heat_in_atm_on_melting_ice_cut_off'] # fetch the correct table
        idxlhs = fcol_in_mdf['Effect_of_heat_in_atm_on_melting_ice_cut_off'] # get the location of the lhs in mdf
        idx1 = fcol_in_mdf['Heat_in_atmosphere_current_to_initial_ratio']
        look = d_table[tabidx]
        valgt = GRAPH(mdf[rowi,  idx1], look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # Land_covered_with_ice_to_land_area_ratio = Land_covered_with_ice_km2 / Land_area_km2
        idxlhs = fcol_in_mdf['Land_covered_with_ice_to_land_area_ratio']
        idx1 = fcol_in_mdf['Land_covered_with_ice_km2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Land_area_km2 
    
    # Snowball_earth_cutoff = WITH LOOKUP ( Land_covered_with_ice_to_land_area_ratio , ( [ ( 0.8 , 0 ) - ( 1 , 1 ) ] , ( 0.8 , 1 ) , ( 0.9 , 0.97 ) , ( 0.97 , 0.75 ) , ( 1 , 0 ) ) )
        tabidx = ftab_in_d_table['Snowball_earth_cutoff'] # fetch the correct table
        idxlhs = fcol_in_mdf['Snowball_earth_cutoff'] # get the location of the lhs in mdf
        idx1 = fcol_in_mdf['Land_covered_with_ice_to_land_area_ratio']
        look = d_table[tabidx]
        valgt = GRAPH(mdf[rowi,  idx1], look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # Atmos_heat_used_for_melting_last_year_1_py = SMOOTHI ( Atmos_heat_used_for_melting_1_py , per_annum_yr , Atmos_heat_used_for_melting_Initially_1_py )
        idxout = fcol_in_mdf['Atmos_heat_used_for_melting_last_year_1_py']
        idx1 = fcol_in_mdf['Atmos_heat_used_for_melting_1_py']
        mdf[rowi, idxout] = mdf[rowi-1, idxout] + (  mdf[rowi-1, idx1] - mdf[rowi - 1, idxout]) / per_annum_yr * dt
    
    # Melting_constraint_from_the_heat_in_atmosphere_reservoir_fraction = WITH LOOKUP ( Atmos_heat_used_for_melting_last_year_1_py , ( [ ( 0 , 0 ) - ( 0.5 , 1 ) ] , ( 0 , 1 ) , ( 0.4 , 0.95 ) , ( 0.45 , 0.75 ) , ( 0.5 , 0.01 ) ) )
        tabidx = ftab_in_d_table['Melting_constraint_from_the_heat_in_atmosphere_reservoir_fraction'] # fetch the correct table
        idxlhs = fcol_in_mdf['Melting_constraint_from_the_heat_in_atmosphere_reservoir_fraction'] # get the location of the lhs in mdf
        idx1 = fcol_in_mdf['Atmos_heat_used_for_melting_last_year_1_py']
        look = d_table[tabidx]
        valgt = GRAPH(mdf[rowi,  idx1], look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # Ocean_heat_used_for_melting_last_year_ZJ_py = SMOOTHI ( Ocean_heat_used_for_melting_ZJ_py , per_annum_yr , Ocean_heat_used_for_melting_Initially_1_py )
        idxout = fcol_in_mdf['Ocean_heat_used_for_melting_last_year_ZJ_py']
        idx1 = fcol_in_mdf['Ocean_heat_used_for_melting_ZJ_py']
        mdf[rowi, idxout] = mdf[rowi-1, idxout] + (  mdf[rowi-1, idx1] - mdf[rowi - 1, idxout]) / per_annum_yr * dt
    
    # Melting_constraint_from_the_heat_in_ocean_surface_reservoir = WITH LOOKUP ( Ocean_heat_used_for_melting_last_year_ZJ_py , ( [ ( 0 , 0 ) - ( 0.5 , 1 ) ] , ( 0 , 1 ) , ( 0.4 , 0.95 ) , ( 0.45 , 0.75 ) , ( 0.5 , 0.01 ) ) )
        tabidx = ftab_in_d_table['Melting_constraint_from_the_heat_in_ocean_surface_reservoir'] # fetch the correct table
        idxlhs = fcol_in_mdf['Melting_constraint_from_the_heat_in_ocean_surface_reservoir'] # get the location of the lhs in mdf
        idx1 = fcol_in_mdf['Ocean_heat_used_for_melting_last_year_ZJ_py']
        look = d_table[tabidx]
        valgt = GRAPH(mdf[rowi,  idx1], look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py = ( Antarctic_ice_volume_km3 / Effective_time_to_melt_or_freeze_antarctic_ice_at_the_reference_delta_temp ) * Effect_of_temp_on_melting_antarctic_ice * Effect_of_heat_in_atm_on_melting_ice_cut_off * Snowball_earth_cutoff * Melting_constraint_from_the_heat_in_atmosphere_reservoir_fraction * Melting_constraint_from_the_heat_in_ocean_surface_reservoir
        idxlhs = fcol_in_mdf['Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py']
        idx1 = fcol_in_mdf['Antarctic_ice_volume_km3']
        idx2 = fcol_in_mdf['Effect_of_temp_on_melting_antarctic_ice']
        idx3 = fcol_in_mdf['Effect_of_heat_in_atm_on_melting_ice_cut_off']
        idx4 = fcol_in_mdf['Snowball_earth_cutoff']
        idx5 = fcol_in_mdf['Melting_constraint_from_the_heat_in_atmosphere_reservoir_fraction']
        idx6 = fcol_in_mdf['Melting_constraint_from_the_heat_in_ocean_surface_reservoir']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] /  Effective_time_to_melt_or_freeze_antarctic_ice_at_the_reference_delta_temp  )  * mdf[rowi, idx2] * mdf[rowi, idx3] * mdf[rowi, idx4] * mdf[rowi, idx5] * mdf[rowi, idx6]
    
    # Antarctic_ice_melting_km3_py = IF_THEN_ELSE ( Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py > 0 , Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py , 0 )
        idxlhs = fcol_in_mdf['Antarctic_ice_melting_km3_py']
        idx1 = fcol_in_mdf['Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py']
        idx2 = fcol_in_mdf['Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  ( mdf[rowi, idx1] >  0  , mdf[rowi, idx2] ,  0  ) 
    
    # Antarctic_ice_area_decrease_Mkm2_pr_yr = ( Antarctic_ice_melting_km3_py / Avg_thickness_Antarctic_km ) * UNIT_Conversion_from_km3_p_kmy_to_Mkm2_py
        idxlhs = fcol_in_mdf['Antarctic_ice_area_decrease_Mkm2_pr_yr']
        idx1 = fcol_in_mdf['Antarctic_ice_melting_km3_py']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] /  Avg_thickness_Antarctic_km  )  *  UNIT_Conversion_from_km3_p_kmy_to_Mkm2_py 
    
    # Antarctic_ice_freezing_km3_py = IF_THEN_ELSE ( Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py < 0 , Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py * ( - 1 ) , 0 )
        idxlhs = fcol_in_mdf['Antarctic_ice_freezing_km3_py']
        idx1 = fcol_in_mdf['Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py']
        idx2 = fcol_in_mdf['Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  ( mdf[rowi, idx1] <  0  , mdf[rowi, idx2] *  (  -  1  )  ,  0  ) 
    
    # Antarctic_ice_area_increase_Mkm2_pr_yr = ( Antarctic_ice_freezing_km3_py / Avg_thickness_Antarctic_km ) * UNIT_Conversion_from_km3_p_kmy_to_Mkm2_py
        idxlhs = fcol_in_mdf['Antarctic_ice_area_increase_Mkm2_pr_yr']
        idx1 = fcol_in_mdf['Antarctic_ice_freezing_km3_py']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] /  Avg_thickness_Antarctic_km  )  *  UNIT_Conversion_from_km3_p_kmy_to_Mkm2_py 
    
    # Antarctic_ice_losing_is_pos_or_gaining_is_neg_GtIce_py = Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py * GtIce_vs_km3
        idxlhs = fcol_in_mdf['Antarctic_ice_losing_is_pos_or_gaining_is_neg_GtIce_py']
        idx1 = fcol_in_mdf['Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  GtIce_vs_km3 
    
    # Antarctic_ice_melting_as_water_km3_py = Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py * Densitiy_of_water_relative_to_ice
        idxlhs = fcol_in_mdf['Antarctic_ice_melting_as_water_km3_py']
        idx1 = fcol_in_mdf['Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Densitiy_of_water_relative_to_ice 
    
    # Anthropogenic_aerosol_forcing = IF_THEN_ELSE ( Human_aerosol_forcing_1_is_ON_0_is_OFF == 0 , 0 , Aerosol_anthropogenic_emissions * Conversion_of_anthro_aerosol_emissions_to_forcing )
        idxlhs = fcol_in_mdf['Anthropogenic_aerosol_forcing']
        idx1 = fcol_in_mdf['Aerosol_anthropogenic_emissions']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  (  Human_aerosol_forcing_1_is_ON_0_is_OFF  ==  0  ,  0  , mdf[rowi, idx1] *  Conversion_of_anthro_aerosol_emissions_to_forcing  ) 
    
    # apl_to_acgl[region] = Abandoned_populated_land[region] / Time_for_abandoned_urban_land_to_become_fallow
        idxlhs = fcol_in_mdf['apl_to_acgl']
        idx1 = fcol_in_mdf['Abandoned_populated_land']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Time_for_abandoned_urban_land_to_become_fallow 
    
    # apl_to_pl[region] = MIN ( Abandoned_populated_land[region] , MAX ( 0 , Populated_land_gap[region] ) ) / Time_to_develop_urban_land_from_abandoned_land
        idxlhs = fcol_in_mdf['apl_to_pl']
        idx1 = fcol_in_mdf['Abandoned_populated_land']
        idx2 = fcol_in_mdf['Populated_land_gap']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.minimum  ( mdf[rowi , idx1:idx1 + 10] ,  np.maximum  (  0  , mdf[rowi , idx2:idx2 + 10] )  )  /  Time_to_develop_urban_land_from_abandoned_land 
    
    # Arctic_ice_on_sea_area_to_arctic_ice_area_max_ratio = Arctic_ice_on_sea_area_km2 / Arctic_ice_area_max_km2
        idxlhs = fcol_in_mdf['Arctic_ice_on_sea_area_to_arctic_ice_area_max_ratio']
        idx1 = fcol_in_mdf['Arctic_ice_on_sea_area_km2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Arctic_ice_area_max_km2 
    
    # Arctic_freezing_cutoff = WITH LOOKUP ( Arctic_ice_on_sea_area_to_arctic_ice_area_max_ratio , ( [ ( 0.8 , 0 ) - ( 1 , 1 ) ] , ( 0.8 , 1 ) , ( 0.899694 , 0.934211 ) , ( 0.949847 , 0.710526 ) , ( 1 , 0 ) ) )
        tabidx = ftab_in_d_table['Arctic_freezing_cutoff'] # fetch the correct table
        idxlhs = fcol_in_mdf['Arctic_freezing_cutoff'] # get the location of the lhs in mdf
        idx1 = fcol_in_mdf['Arctic_ice_on_sea_area_to_arctic_ice_area_max_ratio']
        look = d_table[tabidx]
        valgt = GRAPH(mdf[rowi,  idx1], look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # Temp_diff_relevant_for_melting_or_freezing_arctic_ice_from_anfang = SMOOTH ( Temp_surface_anomaly_compared_to_anfang_degC , Arctic_surface_temp_delay_yr )
        idx1 = fcol_in_mdf['Temp_diff_relevant_for_melting_or_freezing_arctic_ice_from_anfang']
        idx2 = fcol_in_mdf['Temp_surface_anomaly_compared_to_anfang_degC']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1 , idx2] - mdf[rowi -1 , idx1 ]) / Arctic_surface_temp_delay_yr * dt
    
    # Effect_of_temp_on_melting_or_freezing_of_Arctic_ice = 1 + Slope_temp_vs_Arctic_ice_melting * ( ( Temp_diff_relevant_for_melting_or_freezing_arctic_ice_from_anfang / Ref_temp_difference_for_Arctic_ice_melting ) - 1 )
        idxlhs = fcol_in_mdf['Effect_of_temp_on_melting_or_freezing_of_Arctic_ice']
        idx1 = fcol_in_mdf['Temp_diff_relevant_for_melting_or_freezing_arctic_ice_from_anfang']
        mdf[rowi, idxlhs] =  1  +  Slope_temp_vs_Arctic_ice_melting  *  (  ( mdf[rowi, idx1] /  Ref_temp_difference_for_Arctic_ice_melting  )  -  1  ) 
    
    # Arctic_ice_melting_is_pos_or_freezing_is_neg_km2_py = ( Arctic_ice_on_sea_area_km2 / Effective_time_to_melt_Arctic_ice_at_the_reference_delta_temp ) * Effect_of_temp_on_melting_or_freezing_of_Arctic_ice * Arctic_freezing_cutoff * Melting_constraint_from_the_heat_in_atmosphere_reservoir_fraction * Melting_constraint_from_the_heat_in_ocean_surface_reservoir
        idxlhs = fcol_in_mdf['Arctic_ice_melting_is_pos_or_freezing_is_neg_km2_py']
        idx1 = fcol_in_mdf['Arctic_ice_on_sea_area_km2']
        idx2 = fcol_in_mdf['Effect_of_temp_on_melting_or_freezing_of_Arctic_ice']
        idx3 = fcol_in_mdf['Arctic_freezing_cutoff']
        idx4 = fcol_in_mdf['Melting_constraint_from_the_heat_in_atmosphere_reservoir_fraction']
        idx5 = fcol_in_mdf['Melting_constraint_from_the_heat_in_ocean_surface_reservoir']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] /  Effective_time_to_melt_Arctic_ice_at_the_reference_delta_temp  )  * mdf[rowi, idx2] * mdf[rowi, idx3] * mdf[rowi, idx4] * mdf[rowi, idx5]
    
    # Arctic_land_surface_temp_anomaly_compared_to_anfang = SMOOTH ( Temp_surface_anomaly_compared_to_anfang_degC , Land_surface_temp_adjustment_time_yr )
        idx1 = fcol_in_mdf['Arctic_land_surface_temp_anomaly_compared_to_anfang']
        idx2 = fcol_in_mdf['Temp_surface_anomaly_compared_to_anfang_degC']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1 , idx2] - mdf[rowi -1 , idx1 ]) / Land_surface_temp_adjustment_time_yr * dt
    
    # Sensitivity_of_high_cloud_coverage_to_temp_logistics = Sensitivity_of_high_cloud_coverage_to_temp_normal + ( Logistics_curve_param_c / ( 1 + np.exp ( - Logistics_curve_param_k * ( zeit - Logistics_curve_param_shift ) ) ) )
        idxlhs = fcol_in_mdf['Sensitivity_of_high_cloud_coverage_to_temp_logistics']
        mdf[rowi, idxlhs] =  Sensitivity_of_high_cloud_coverage_to_temp_normal  +  (  Logistics_curve_param_c  /  (  1  +  np.exp  (  -  Logistics_curve_param_k  *  (  zeit  -  Logistics_curve_param_shift  )  )  )  ) 
    
    # Temp_surface_current_divided_by_value_anfang = Temp_surface_average_K / Temp_surface_1850
        idxlhs = fcol_in_mdf['Temp_surface_current_divided_by_value_anfang']
        idx1 = fcol_in_mdf['Temp_surface_average_K']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Temp_surface_1850 
    
    # Area_covered_by_high_clouds = Area_covered_by_high_clouds_in_1980 * ( 1 + Sensitivity_of_high_cloud_coverage_to_temp_logistics * ( Temp_surface_current_divided_by_value_anfang - 1 ) )
        idxlhs = fcol_in_mdf['Area_covered_by_high_clouds']
        idx1 = fcol_in_mdf['Sensitivity_of_high_cloud_coverage_to_temp_logistics']
        idx2 = fcol_in_mdf['Temp_surface_current_divided_by_value_anfang']
        mdf[rowi, idxlhs] =  Area_covered_by_high_clouds_in_1980  *  (  1  + mdf[rowi, idx1] *  ( mdf[rowi, idx2] -  1  )  ) 
    
    # Area_covered_by_low_clouds = Area_covered_by_low_clouds_in_1980 * ( 1 + Sensitivity_of_low_cloud_coverage_to_temp * ( Temp_surface_current_divided_by_value_anfang - 1 ) )
        idxlhs = fcol_in_mdf['Area_covered_by_low_clouds']
        idx1 = fcol_in_mdf['Temp_surface_current_divided_by_value_anfang']
        mdf[rowi, idxlhs] =  Area_covered_by_low_clouds_in_1980  *  (  1  +  Sensitivity_of_low_cloud_coverage_to_temp  *  ( mdf[rowi, idx1] -  1  )  ) 
    
    # Effect_of_temp_on_melting_or_freezing_glacial_ice = 1 + Slope_temp_vs_glacial_ice_melting * ( ( Temp_diff_relevant_for_melting_or_freezing_anfang / Ref_temp_difference_for_glacial_ice_melting_1_degC ) - 1 )
        idxlhs = fcol_in_mdf['Effect_of_temp_on_melting_or_freezing_glacial_ice']
        idx1 = fcol_in_mdf['Temp_diff_relevant_for_melting_or_freezing_anfang']
        mdf[rowi, idxlhs] =  1  +  Slope_temp_vs_glacial_ice_melting  *  (  ( mdf[rowi, idx1] /  Ref_temp_difference_for_glacial_ice_melting_1_degC  )  -  1  ) 
    
    # Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py = Glacial_ice_volume_km3 / Effective_time_to_melt_glacial_ice_at_the_reference_delta_temp * Effect_of_temp_on_melting_or_freezing_glacial_ice * Effect_of_heat_in_atm_on_melting_ice_cut_off
        idxlhs = fcol_in_mdf['Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py']
        idx1 = fcol_in_mdf['Glacial_ice_volume_km3']
        idx2 = fcol_in_mdf['Effect_of_temp_on_melting_or_freezing_glacial_ice']
        idx3 = fcol_in_mdf['Effect_of_heat_in_atm_on_melting_ice_cut_off']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Effective_time_to_melt_glacial_ice_at_the_reference_delta_temp  * mdf[rowi, idx2] * mdf[rowi, idx3]
    
    # Heat_used_in_melting_is_pos_or_freezing_is_neg_glacial_ice_ZJ_py = Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py * Heat_needed_to_melt_1_km3_of_ice_ZJ * UNIT_conversion_1_p_km3
        idxlhs = fcol_in_mdf['Heat_used_in_melting_is_pos_or_freezing_is_neg_glacial_ice_ZJ_py']
        idx1 = fcol_in_mdf['Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Heat_needed_to_melt_1_km3_of_ice_ZJ  *  UNIT_conversion_1_p_km3 
    
    # Heat_used_in_melting_is_pos_or_freezing_is_neg_antarctic_ice_ZJ_py = Antarctic_ice_losing_is_pos_or_gaining_is_neg_GtIce_py * Heat_needed_to_melt_1_km3_of_ice_ZJ * UNIT_conversion_GtIce_to_ZJ_melting
        idxlhs = fcol_in_mdf['Heat_used_in_melting_is_pos_or_freezing_is_neg_antarctic_ice_ZJ_py']
        idx1 = fcol_in_mdf['Antarctic_ice_losing_is_pos_or_gaining_is_neg_GtIce_py']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Heat_needed_to_melt_1_km3_of_ice_ZJ  *  UNIT_conversion_GtIce_to_ZJ_melting 
    
    # Effect_of_temp_on_melting_greenland_ice = 1 + Slope_temp_vs_greenland_ice_melting * ( ( Arctic_land_surface_temp_anomaly_compared_to_anfang / Ref_temp_difference_for_greenland_ice_melting_C ) - 1 )
        idxlhs = fcol_in_mdf['Effect_of_temp_on_melting_greenland_ice']
        idx1 = fcol_in_mdf['Arctic_land_surface_temp_anomaly_compared_to_anfang']
        mdf[rowi, idxlhs] =  1  +  Slope_temp_vs_greenland_ice_melting  *  (  ( mdf[rowi, idx1] /  Ref_temp_difference_for_greenland_ice_melting_C  )  -  1  ) 
    
    # Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py = ( Greenland_ice_volume_on_Greenland_km3 / Effective_time_to_melt_greenland_ice_at_the_reference_delta_temp ) * Effect_of_temp_on_melting_greenland_ice * Effect_of_heat_in_atm_on_melting_ice_cut_off * Snowball_earth_cutoff * Melting_constraint_from_the_heat_in_atmosphere_reservoir_fraction
        idxlhs = fcol_in_mdf['Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py']
        idx1 = fcol_in_mdf['Greenland_ice_volume_on_Greenland_km3']
        idx2 = fcol_in_mdf['Effect_of_temp_on_melting_greenland_ice']
        idx3 = fcol_in_mdf['Effect_of_heat_in_atm_on_melting_ice_cut_off']
        idx4 = fcol_in_mdf['Snowball_earth_cutoff']
        idx5 = fcol_in_mdf['Melting_constraint_from_the_heat_in_atmosphere_reservoir_fraction']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] /  Effective_time_to_melt_greenland_ice_at_the_reference_delta_temp  )  * mdf[rowi, idx2] * mdf[rowi, idx3] * mdf[rowi, idx4] * mdf[rowi, idx5]
    
    # Heat_used_in_melting_is_pos_or_freezing_is_neg_Greenland_ice_ZJ_py = Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py * Heat_needed_to_melt_1_km3_of_ice_ZJ * UNIT_conversion_1_p_km3
        idxlhs = fcol_in_mdf['Heat_used_in_melting_is_pos_or_freezing_is_neg_Greenland_ice_ZJ_py']
        idx1 = fcol_in_mdf['Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Heat_needed_to_melt_1_km3_of_ice_ZJ  *  UNIT_conversion_1_p_km3 
    
    # Heat_used_in_melting_is_pos_or_freezing_is_neg_arctic_sea_ice_ZJ_py = Arctic_ice_melting_is_pos_or_freezing_is_neg_km2_py * Average_thickness_arctic_ice_km * Heat_needed_to_melt_1_km3_of_ice_ZJ / UNIT_conversion_km2_times_km_to_km3
        idxlhs = fcol_in_mdf['Heat_used_in_melting_is_pos_or_freezing_is_neg_arctic_sea_ice_ZJ_py']
        idx1 = fcol_in_mdf['Arctic_ice_melting_is_pos_or_freezing_is_neg_km2_py']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Average_thickness_arctic_ice_km  *  Heat_needed_to_melt_1_km3_of_ice_ZJ  /  UNIT_conversion_km2_times_km_to_km3 
    
    # Slope_btw_temp_and_permafrost_melting_or_freezing = IF_THEN_ELSE ( zeit < 2020 , Slope_btw_temp_and_permafrost_melting_or_freezing_base , Slope_btw_temp_and_permafrost_melting_or_freezing_sensitivity )
        idxlhs = fcol_in_mdf['Slope_btw_temp_and_permafrost_melting_or_freezing']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  (  zeit  <  2020  ,  Slope_btw_temp_and_permafrost_melting_or_freezing_base  ,  Slope_btw_temp_and_permafrost_melting_or_freezing_sensitivity  ) 
    
    # Temp_diff_relevant_for_melting_or_freezing_from_anfang_smoothed = SMOOTH ( Temp_diff_relevant_for_melting_or_freezing_anfang , Time_to_smooth_out_temperature_diff_relevant_for_melting_or_freezing_from_1850_yr )
        idx1 = fcol_in_mdf['Temp_diff_relevant_for_melting_or_freezing_from_anfang_smoothed']
        idx2 = fcol_in_mdf['Temp_diff_relevant_for_melting_or_freezing_anfang']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1 , idx2] - mdf[rowi -1 , idx1 ]) / Time_to_smooth_out_temperature_diff_relevant_for_melting_or_freezing_from_1850_yr * dt
    
    # Effect_of_temp_on_permafrost_melting_dmnl = 1 + Slope_btw_temp_and_permafrost_melting_or_freezing * ( ( Temp_diff_relevant_for_melting_or_freezing_from_anfang_smoothed / Ref_temp_difference_4_degC ) - 1 )
        idxlhs = fcol_in_mdf['Effect_of_temp_on_permafrost_melting_dmnl']
        idx1 = fcol_in_mdf['Slope_btw_temp_and_permafrost_melting_or_freezing']
        idx2 = fcol_in_mdf['Temp_diff_relevant_for_melting_or_freezing_from_anfang_smoothed']
        mdf[rowi, idxlhs] =  1  + mdf[rowi, idx1] *  (  ( mdf[rowi, idx2] /  Ref_temp_difference_4_degC  )  -  1  ) 
    
    # Effect_of_temp_on_permafrost_melting_dmnl_smoothed = SMOOTH ( Effect_of_temp_on_permafrost_melting_dmnl , Time_to_propagate_temperature_change_through_the_volume_of_permafrost_yr )
        idx1 = fcol_in_mdf['Effect_of_temp_on_permafrost_melting_dmnl_smoothed']
        idx2 = fcol_in_mdf['Effect_of_temp_on_permafrost_melting_dmnl']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1 , idx2] - mdf[rowi -1 , idx1 ]) / Time_to_propagate_temperature_change_through_the_volume_of_permafrost_yr * dt
    
    # Slowing_of_recapture_of_CH4_dmnl = IF_THEN_ELSE ( Effect_of_temp_on_permafrost_melting_dmnl_smoothed < 0 , 0.01 , 1 )
        idxlhs = fcol_in_mdf['Slowing_of_recapture_of_CH4_dmnl']
        idx1 = fcol_in_mdf['Effect_of_temp_on_permafrost_melting_dmnl_smoothed']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  ( mdf[rowi, idx1] <  0  ,  0.01  ,  1  ) 
    
    # Permafrost_melting_cutoff = WITH LOOKUP ( C_in_permafrost_in_form_of_CH4 , ( [ ( 0 , 0 ) - ( 200 , 1 ) ] , ( 0 , 0 ) , ( 50 , 0.6 ) , ( 100 , 0.9 ) , ( 150 , 0.965 ) , ( 200 , 1 ) ) )
        tabidx = ftab_in_d_table['Permafrost_melting_cutoff'] # fetch the correct table
        idxlhs = fcol_in_mdf['Permafrost_melting_cutoff'] # get the location of the lhs in mdf
        idx1 = fcol_in_mdf['C_in_permafrost_in_form_of_CH4']
        look = d_table[tabidx]
        valgt = GRAPH(mdf[rowi,  idx1], look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # CH4_in_permafrost_area_melted_or_frozen_before_heat_constraint = ( Area_equivalent_of_linear_retreat_km2_py * Avg_amount_of_C_in_the_form_of_CH4_per_km2 * Effect_of_temp_on_permafrost_melting_dmnl_smoothed * Slowing_of_recapture_of_CH4_dmnl * Permafrost_melting_cutoff )
        idxlhs = fcol_in_mdf['CH4_in_permafrost_area_melted_or_frozen_before_heat_constraint']
        idx1 = fcol_in_mdf['Effect_of_temp_on_permafrost_melting_dmnl_smoothed']
        idx2 = fcol_in_mdf['Slowing_of_recapture_of_CH4_dmnl']
        idx3 = fcol_in_mdf['Permafrost_melting_cutoff']
        mdf[rowi, idxlhs] =  (  Area_equivalent_of_linear_retreat_km2_py  *  Avg_amount_of_C_in_the_form_of_CH4_per_km2  * mdf[rowi, idx1] * mdf[rowi, idx2] * mdf[rowi, idx3] ) 
    
    # Heat_gained_or_needed_for_the_desired_freezing_or_unfreezing_of_permafrost_ZJ_py = ( CH4_in_permafrost_area_melted_or_frozen_before_heat_constraint / Avg_amount_of_C_in_the_form_of_CH4_per_km2 ) * Avg_depth_of_permafrost_km * Heat_gained_or_needed_to_freeze_or_unfreeze_1_km3_permafrost_ZJ_p_km3 / UNIT_conversion_km3_div_km_to_km2
        idxlhs = fcol_in_mdf['Heat_gained_or_needed_for_the_desired_freezing_or_unfreezing_of_permafrost_ZJ_py']
        idx1 = fcol_in_mdf['CH4_in_permafrost_area_melted_or_frozen_before_heat_constraint']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] /  Avg_amount_of_C_in_the_form_of_CH4_per_km2  )  *  Avg_depth_of_permafrost_km  *  Heat_gained_or_needed_to_freeze_or_unfreeze_1_km3_permafrost_ZJ_p_km3  /  UNIT_conversion_km3_div_km_to_km2 
    
    # Heat_in_atmosphere_needed_to_available_ratio = Heat_gained_or_needed_for_the_desired_freezing_or_unfreezing_of_permafrost_ZJ_py / Heat_in_atmosphere_ZJ
        idxlhs = fcol_in_mdf['Heat_in_atmosphere_needed_to_available_ratio']
        idx1 = fcol_in_mdf['Heat_gained_or_needed_for_the_desired_freezing_or_unfreezing_of_permafrost_ZJ_py']
        idx2 = fcol_in_mdf['Heat_in_atmosphere_ZJ']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] / mdf[rowi, idx2]
    
    # Melting_restraint_for_permafrost_from_heat_in_atmophere = WITH LOOKUP ( Heat_in_atmosphere_needed_to_available_ratio , ( [ ( 0 , 0 ) - ( 0.5 , 1 ) ] , ( 0 , 1 ) , ( 0.4 , 0.95 ) , ( 0.45 , 0.75 ) , ( 0.5 , 0.01 ) ) )
        tabidx = ftab_in_d_table['Melting_restraint_for_permafrost_from_heat_in_atmophere'] # fetch the correct table
        idxlhs = fcol_in_mdf['Melting_restraint_for_permafrost_from_heat_in_atmophere'] # get the location of the lhs in mdf
        idx1 = fcol_in_mdf['Heat_in_atmosphere_needed_to_available_ratio']
        look = d_table[tabidx]
        valgt = GRAPH(mdf[rowi,  idx1], look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # CH4_release_or_capture_from_permafrost_area_loss_or_gain_GtC_py = CH4_in_permafrost_area_melted_or_frozen_before_heat_constraint * Melting_restraint_for_permafrost_from_heat_in_atmophere * Fraction_of_C_released_from_permafrost_released_as_CH4_dmnl
        idxlhs = fcol_in_mdf['CH4_release_or_capture_from_permafrost_area_loss_or_gain_GtC_py']
        idx1 = fcol_in_mdf['CH4_in_permafrost_area_melted_or_frozen_before_heat_constraint']
        idx2 = fcol_in_mdf['Melting_restraint_for_permafrost_from_heat_in_atmophere']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2] *  Fraction_of_C_released_from_permafrost_released_as_CH4_dmnl 
    
    # Heat_actually_gained_or_needed_for_freezing_or_unfreezing_of_permafrost_ZJ_py = ( CH4_release_or_capture_from_permafrost_area_loss_or_gain_GtC_py / Avg_amount_of_C_in_the_form_of_CH4_per_km2 ) * Avg_depth_of_permafrost_km * Heat_gained_or_needed_to_freeze_or_unfreeze_1_km3_permafrost_ZJ_p_km3 / UNIT_conversion_km3_div_km_to_km2
        idxlhs = fcol_in_mdf['Heat_actually_gained_or_needed_for_freezing_or_unfreezing_of_permafrost_ZJ_py']
        idx1 = fcol_in_mdf['CH4_release_or_capture_from_permafrost_area_loss_or_gain_GtC_py']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] /  Avg_amount_of_C_in_the_form_of_CH4_per_km2  )  *  Avg_depth_of_permafrost_km  *  Heat_gained_or_needed_to_freeze_or_unfreeze_1_km3_permafrost_ZJ_p_km3  /  UNIT_conversion_km3_div_km_to_km2 
    
    # Heat_withdrawn_from_atm_by_melting_pos_or_added_neg_by_freezing_ice_ZJ_py = Heat_used_in_melting_is_pos_or_freezing_is_neg_glacial_ice_ZJ_py + Heat_used_in_melting_is_pos_or_freezing_is_neg_antarctic_ice_ZJ_py * Fraction_of_heat_needed_to_melt_antarctic_ice_coming_from_air + Heat_used_in_melting_is_pos_or_freezing_is_neg_Greenland_ice_ZJ_py + Heat_used_in_melting_is_pos_or_freezing_is_neg_arctic_sea_ice_ZJ_py * Fraction_of_heat_needed_to_melt_arctic_ice_coming_from_air + Heat_actually_gained_or_needed_for_freezing_or_unfreezing_of_permafrost_ZJ_py
        idxlhs = fcol_in_mdf['Heat_withdrawn_from_atm_by_melting_pos_or_added_neg_by_freezing_ice_ZJ_py']
        idx1 = fcol_in_mdf['Heat_used_in_melting_is_pos_or_freezing_is_neg_glacial_ice_ZJ_py']
        idx2 = fcol_in_mdf['Heat_used_in_melting_is_pos_or_freezing_is_neg_antarctic_ice_ZJ_py']
        idx3 = fcol_in_mdf['Heat_used_in_melting_is_pos_or_freezing_is_neg_Greenland_ice_ZJ_py']
        idx4 = fcol_in_mdf['Heat_used_in_melting_is_pos_or_freezing_is_neg_arctic_sea_ice_ZJ_py']
        idx5 = fcol_in_mdf['Heat_actually_gained_or_needed_for_freezing_or_unfreezing_of_permafrost_ZJ_py']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] *  Fraction_of_heat_needed_to_melt_antarctic_ice_coming_from_air  + mdf[rowi, idx3] + mdf[rowi, idx4] *  Fraction_of_heat_needed_to_melt_arctic_ice_coming_from_air  + mdf[rowi, idx5]
    
    # Atmos_heat_used_for_melting_1_py = Heat_withdrawn_from_atm_by_melting_pos_or_added_neg_by_freezing_ice_ZJ_py / Heat_in_atmosphere_ZJ
        idxlhs = fcol_in_mdf['Atmos_heat_used_for_melting_1_py']
        idx1 = fcol_in_mdf['Heat_withdrawn_from_atm_by_melting_pos_or_added_neg_by_freezing_ice_ZJ_py']
        idx2 = fcol_in_mdf['Heat_in_atmosphere_ZJ']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] / mdf[rowi, idx2]
    
    # Average_wellbeing_index_1980_is_1[region] = Average_wellbeing_index[region] / Average_wellbeing_index_in_1980[region]
        idxlhs = fcol_in_mdf['Average_wellbeing_index_1980_is_1']
        idx1 = fcol_in_mdf['Average_wellbeing_index']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Average_wellbeing_index_in_1980[0:10] 
    
    # Carbon_in_top_ocean_layer_GtC = C_in_cold_surface_water_GtC + C_in_warm_surface_water_GtC
        idxlhs = fcol_in_mdf['Carbon_in_top_ocean_layer_GtC']
        idx1 = fcol_in_mdf['C_in_cold_surface_water_GtC']
        idx2 = fcol_in_mdf['C_in_warm_surface_water_GtC']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2]
    
    # Avg_C_concentration_in_top_layer = Carbon_in_top_ocean_layer_GtC / ( Cold_surface_water_volume + Warm_surface_water_volume )
        idxlhs = fcol_in_mdf['Avg_C_concentration_in_top_layer']
        idx1 = fcol_in_mdf['Carbon_in_top_ocean_layer_GtC']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  (  Cold_surface_water_volume  +  Warm_surface_water_volume  ) 
    
    # Avg_CC_in_ocean_top_layer_ymoles_per_litre = Avg_C_concentration_in_top_layer * UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre
        idxlhs = fcol_in_mdf['Avg_CC_in_ocean_top_layer_ymoles_per_litre']
        idx1 = fcol_in_mdf['Avg_C_concentration_in_top_layer']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre 
    
    # Avg_earths_surface_albedo = Albedo_ocean_with_arctic_ice_changes * Fraction_of_earth_surface_as_ocean + Albedo_land_biomes * ( 1 - Fraction_of_earth_surface_as_ocean )
        idxlhs = fcol_in_mdf['Avg_earths_surface_albedo']
        idx1 = fcol_in_mdf['Albedo_ocean_with_arctic_ice_changes']
        idx2 = fcol_in_mdf['Albedo_land_biomes']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Fraction_of_earth_surface_as_ocean  + mdf[rowi, idx2] *  (  1  -  Fraction_of_earth_surface_as_ocean  ) 
    
    # Historical_aerosol_forcing_volcanic = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , - 0.0843062 ) , ( 1981 , - 0.152848 ) , ( 1982 , - 0.823871 ) , ( 1983 , - 1.10866 ) , ( 1984 , - 0.552446 ) , ( 1985 , - 0.25566 ) , ( 1986 , - 0.1974 ) , ( 1987 , - 0.166556 ) , ( 1988 , - 0.126459 ) , ( 1989 , - 0.103155 ) , ( 1990 , - 0.105897 ) , ( 1991 , - 1.04732 ) , ( 1992 , - 1.6522 ) , ( 1993 , - 0.914346 ) , ( 1994 , - 0.363956 ) , ( 1995 , - 0.173753 ) , ( 1996 , - 0.108639 ) , ( 1997 , - 0.0791656 ) , ( 1998 , - 0.0448948 ) , ( 1999 , - 0.0161073 ) , ( 2000 , - 0.00376979 ) , ( 2001 , 0 ) , ( 2002 , 0 ) , ( 2003 , 0 ) , ( 2004 , 0 ) , ( 2005 , - 0.0484259 ) , ( 2006 , - 0.164648 ) , ( 2007 , - 0.232444 ) , ( 2008 , 0 ) , ( 2009 , 0 ) , ( 2010 , 0 ) , ( 2011 , 0 ) , ( 2012 , 0 ) , ( 2013 , 0 ) , ( 2014 , 0 ) , ( 2015 , 0 ) ) )
        tabidx = ftab_in_d_table['Historical_aerosol_forcing_volcanic'] # fetch the correct table
        idxlhs = fcol_in_mdf['Historical_aerosol_forcing_volcanic'] # get the location of the lhs in mdf
        look = d_table[tabidx]
        valgt = GRAPH( zeit, look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
     
    # Future_volcanic_emissions_shape_pulse_train = PULSE_TRAIN ( NEvt_2a_Volcanic_eruptions_in_the_future_VAEs_first_future_pulse , VAES_pulse_duration , VAES_puls_repetition , 9999 ) * VAES_pulse_height
        idxlhs = fcol_in_mdf['Future_volcanic_emissions_shape_pulse_train']
        mdf[rowi, idxlhs] = PULSE_TRAIN( zeit, NEvt_2a_Volcanic_eruptions_in_the_future_VAEs_first_future_pulse, VAES_pulse_duration, VAES_puls_repetition, VAES_pulse_height )
    
    # Future_volcanic_emissions_shape = IF_THEN_ELSE ( Future_volcanic_eruptions_1_is_ON_0_is_OFF == 0 , 0 , Future_volcanic_emissions_shape_pulse_train )
        idxlhs = fcol_in_mdf['Future_volcanic_emissions_shape']
        idx1 = fcol_in_mdf['Future_volcanic_emissions_shape_pulse_train']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  (  Future_volcanic_eruptions_1_is_ON_0_is_OFF  ==  0  ,  0  , mdf[rowi, idx1] ) 
    
    # Future_volcanic_emissions = SMOOTH3 ( Future_volcanic_emissions_shape , FVE_shape_time )
        idx1 = fcol_in_mdf['Future_volcanic_emissions_shape']
        idxin = fcol_in_mdf['Future_volcanic_emissions_shape' ]
        idx2 = fcol_in_mdf['Future_volcanic_emissions_2']
        idx1 = fcol_in_mdf['Future_volcanic_emissions_1']
        idxout = fcol_in_mdf['Future_volcanic_emissions']
        mdf[rowi, idxout] = mdf[rowi-1, idxout] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idxout]) / ( FVE_shape_time / 3) * dt
        mdf[rowi, idx2] = mdf[rowi-1, idx2] + ( mdf[rowi-1, idx1] - mdf[rowi-1, idx2]) / ( FVE_shape_time / 3) * dt
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idxin] - mdf[rowi-1, idx1]) / ( FVE_shape_time / 3) * dt
    
    # Volcanic_aerosols_emissions = IF_THEN_ELSE ( zeit < 2008 , Historical_aerosol_forcing_volcanic / Conversion_of_volcanic_aerosol_forcing_to_volcanic_aerosol_emissions , Future_volcanic_emissions )
        idxlhs = fcol_in_mdf['Volcanic_aerosols_emissions']
        idx1 = fcol_in_mdf['Historical_aerosol_forcing_volcanic']
        idx2 = fcol_in_mdf['Future_volcanic_emissions']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  (  zeit  <  2008  , mdf[rowi, idx1] /  Conversion_of_volcanic_aerosol_forcing_to_volcanic_aerosol_emissions  , mdf[rowi, idx2] ) 
    
    # Avg_volcanic_activity_GtC_py = Volcanic_aerosols_emissions * Conversion_of_volcanic_aerosol_emissions_to_CO2_emissions_GtC_pr_VAE
        idxlhs = fcol_in_mdf['Avg_volcanic_activity_GtC_py']
        idx1 = fcol_in_mdf['Volcanic_aerosols_emissions']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Conversion_of_volcanic_aerosol_emissions_to_CO2_emissions_GtC_pr_VAE 
    
    # BB_radiation_at_surface_temp_ZJ_py = Emissivity_surface * Stephan_Boltzmann_constant * Temp_surface_average_K ^ 4 * UNIT_conversion_W_p_m2_earth_to_ZJ_py
        idxlhs = fcol_in_mdf['BB_radiation_at_surface_temp_ZJ_py']
        idx1 = fcol_in_mdf['Temp_surface_average_K']
        mdf[rowi, idxlhs] =  Emissivity_surface  *  Stephan_Boltzmann_constant  * mdf[rowi, idx1] **  4  *  UNIT_conversion_W_p_m2_earth_to_ZJ_py 
    
    # Temp_atm_average_K = Heat_in_atmosphere_ZJ * Conversion_heat_atm_to_temp
        idxlhs = fcol_in_mdf['Temp_atm_average_K']
        idx1 = fcol_in_mdf['Heat_in_atmosphere_ZJ']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Conversion_heat_atm_to_temp 
    
    # BB_radiation_at_Temp_in_atm_ZJ_py = Emissivity_atm * Stephan_Boltzmann_constant * Temp_atm_average_K ^ 4 * UNIT_conversion_W_p_m2_earth_to_ZJ_py
        idxlhs = fcol_in_mdf['BB_radiation_at_Temp_in_atm_ZJ_py']
        idx1 = fcol_in_mdf['Temp_atm_average_K']
        mdf[rowi, idxlhs] =  Emissivity_atm  *  Stephan_Boltzmann_constant  * mdf[rowi, idx1] **  4  *  UNIT_conversion_W_p_m2_earth_to_ZJ_py 
    
    # Global_population_TLTL = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 4429.29 ) , ( 1981 , 4496.99 ) , ( 1982 , 4565.8 ) , ( 1983 , 4637.14 ) , ( 1984 , 4714.02 ) , ( 1985 , 4794.22 ) , ( 1986 , 4875.37 ) , ( 1987 , 4958.62 ) , ( 1988 , 5043.24 ) , ( 1989 , 5127.61 ) , ( 1990 , 5212.36 ) , ( 1991 , 5297.99 ) , ( 1992 , 5383.77 ) , ( 1993 , 5469.92 ) , ( 1994 , 5557.22 ) , ( 1995 , 5645.17 ) , ( 1996 , 5733.67 ) , ( 1997 , 5823.18 ) , ( 1998 , 5913.28 ) , ( 1999 , 6003.57 ) , ( 2000 , 6094.22 ) , ( 2001 , 6184.81 ) , ( 2002 , 6274.89 ) , ( 2003 , 6364.45 ) , ( 2004 , 6453.16 ) , ( 2005 , 6540.68 ) , ( 2006 , 6626.99 ) , ( 2007 , 6711.97 ) , ( 2008 , 6795.42 ) , ( 2009 , 6877.37 ) , ( 2010 , 6957.8 ) , ( 2011 , 7036.66 ) , ( 2012 , 7114 ) , ( 2013 , 7189.88 ) , ( 2014 , 7264.28 ) , ( 2015 , 7337.26 ) , ( 2016 , 7408.86 ) , ( 2017 , 7479.08 ) , ( 2018 , 7547.94 ) , ( 2019 , 7615.46 ) , ( 2020 , 7681.64 ) , ( 2021 , 7746.45 ) , ( 2022 , 7809.85 ) , ( 2023 , 7871.81 ) , ( 2024 , 7932.28 ) , ( 2025 , 7991.25 ) , ( 2026 , 8047.86 ) , ( 2027 , 8101.52 ) , ( 2028 , 8152.71 ) , ( 2029 , 8201.73 ) , ( 2030 , 8248.72 ) , ( 2031 , 8293.72 ) , ( 2032 , 8336.72 ) , ( 2033 , 8377.71 ) , ( 2034 , 8416.69 ) , ( 2035 , 8453.68 ) , ( 2036 , 8488.76 ) , ( 2037 , 8522.04 ) , ( 2038 , 8553.65 ) , ( 2039 , 8583.67 ) , ( 2040 , 8612.19 ) , ( 2041 , 8639.29 ) , ( 2042 , 8665.03 ) , ( 2043 , 8689.41 ) , ( 2044 , 8712.45 ) , ( 2045 , 8734.12 ) , ( 2046 , 8754.36 ) , ( 2047 , 8773.13 ) , ( 2048 , 8790.31 ) , ( 2049 , 8805.78 ) , ( 2050 , 8819.42 ) , ( 2051 , 8831.18 ) , ( 2052 , 8840.97 ) , ( 2053 , 8848.77 ) , ( 2054 , 8854.55 ) , ( 2055 , 8858.34 ) , ( 2056 , 8860.17 ) , ( 2057 , 8860.14 ) , ( 2058 , 8858.33 ) , ( 2059 , 8854.75 ) , ( 2060 , 8849.43 ) , ( 2061 , 8842.46 ) , ( 2062 , 8833.91 ) , ( 2063 , 8823.88 ) , ( 2064 , 8812.43 ) , ( 2065 , 8799.62 ) , ( 2066 , 8785.51 ) , ( 2067 , 8770.14 ) , ( 2068 , 8753.54 ) , ( 2069 , 8735.72 ) , ( 2070 , 8716.76 ) , ( 2071 , 8696.74 ) , ( 2072 , 8675.78 ) , ( 2073 , 8653.93 ) , ( 2074 , 8631.19 ) , ( 2075 , 8607.58 ) , ( 2076 , 8583.07 ) , ( 2077 , 8557.64 ) , ( 2078 , 8531.2 ) , ( 2079 , 8503.61 ) , ( 2080 , 8474.78 ) , ( 2081 , 8444.72 ) , ( 2082 , 8413.47 ) , ( 2083 , 8381.08 ) , ( 2084 , 8347.63 ) , ( 2085 , 8313.15 ) , ( 2086 , 8277.66 ) , ( 2087 , 8241.18 ) , ( 2088 , 8203.7 ) , ( 2089 , 8165.26 ) , ( 2090 , 8125.93 ) , ( 2091 , 8085.86 ) , ( 2092 , 8045.2 ) , ( 2093 , 8004.14 ) , ( 2094 , 7962.83 ) , ( 2095 , 7921.42 ) , ( 2096 , 7880.01 ) , ( 2097 , 7838.69 ) , ( 2098 , 7797.53 ) , ( 2099 , 7756.59 ) , ( 2100 , 7715.93 ) ) )
        tabidx = ftab_in_d_table['Global_population_TLTL'] # fetch the correct table
        idxlhs = fcol_in_mdf['Global_population_TLTL'] # get the location of the lhs in mdf
        look = d_table[tabidx]
        valgt = GRAPH( zeit, look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # Effect_of_population_on_forest_degradation_and_biocapacity = Global_population / Global_population_TLTL
        idxlhs = fcol_in_mdf['Effect_of_population_on_forest_degradation_and_biocapacity']
        idx1 = fcol_in_mdf['Global_population']
        idx2 = fcol_in_mdf['Global_population_TLTL']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] / mdf[rowi, idx2]
    
    # Biocapacity_with_population_effect = Biocapacity_reference / Effect_of_population_on_forest_degradation_and_biocapacity
        idxlhs = fcol_in_mdf['Biocapacity_with_population_effect']
        idx1 = fcol_in_mdf['Effect_of_population_on_forest_degradation_and_biocapacity']
        mdf[rowi, idxlhs] =  Biocapacity_reference  / mdf[rowi, idx1]
    
    # Biocapacity = IF_THEN_ELSE ( zeit >= 2020 , Biocapacity_with_population_effect , Biocapacity_reference )
        idxlhs = fcol_in_mdf['Biocapacity']
        idx1 = fcol_in_mdf['Biocapacity_with_population_effect']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  (  zeit  >=  2020  , mdf[rowi, idx1] ,  Biocapacity_reference  ) 
     
    # Global_GDPpp_USED = GDPpp_USED[us] * Regional_population_as_fraction_of_total[us] + GDPpp_USED[af] * Regional_population_as_fraction_of_total[af] + GDPpp_USED[cn] * Regional_population_as_fraction_of_total[cn] + GDPpp_USED[me] * Regional_population_as_fraction_of_total[me] + GDPpp_USED[sa] * Regional_population_as_fraction_of_total[sa] + GDPpp_USED[la] * Regional_population_as_fraction_of_total[la] + GDPpp_USED[pa] * Regional_population_as_fraction_of_total[pa] + GDPpp_USED[ec] * Regional_population_as_fraction_of_total[ec] + GDPpp_USED[eu] * Regional_population_as_fraction_of_total[eu] + GDPpp_USED[se] * Regional_population_as_fraction_of_total[se]
        idxlhs = fcol_in_mdf['Global_GDPpp_USED']
        idx1 = fcol_in_mdf['GDPpp_USED']
        idx2 = fcol_in_mdf['Regional_population_as_fraction_of_total']
        mdf[rowi, idxlhs] = ( mdf[rowi, idx1 + 0 ] *  mdf[rowi, idx2 + 0 ]+ mdf[rowi, idx1 + 1 ] *  mdf[rowi, idx2 + 1 ]+ mdf[rowi, idx1 + 2 ] *  mdf[rowi, idx2 + 2 ]+ mdf[rowi, idx1 + 3 ] *  mdf[rowi, idx2 + 3 ]+ mdf[rowi, idx1 + 4 ] *  mdf[rowi, idx2 + 4 ]+ mdf[rowi, idx1 + 5 ] *  mdf[rowi, idx2 + 5 ]+ mdf[rowi, idx1 + 6 ] *  mdf[rowi, idx2 + 6 ]+ mdf[rowi, idx1 + 7 ] *  mdf[rowi, idx2 + 7 ]+ mdf[rowi, idx1 + 8 ] *  mdf[rowi, idx2 + 8 ]+ mdf[rowi, idx1 + 9 ] *  mdf[rowi, idx2 + 9 ] )
    
    # Effect_of_Wealth_on_non_energy_footprint = WITH LOOKUP ( Global_GDPpp_USED , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 1.5 ) , ( 10 , 1.2 ) , ( 20 , 1 ) , ( 30 , 1.1 ) , ( 40 , 1.2 ) , ( 50 , 1.4 ) , ( 75 , 1.8 ) , ( 100 , 1.9 ) ) )
        tabidx = ftab_in_d_table['Effect_of_Wealth_on_non_energy_footprint'] # fetch the correct table
        idxlhs = fcol_in_mdf['Effect_of_Wealth_on_non_energy_footprint'] # get the location of the lhs in mdf
        idx1 = fcol_in_mdf['Global_GDPpp_USED']
        look = d_table[tabidx]
        valgt = GRAPH(mdf[rowi,  idx1], look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # Smoothed_Effect_of_Wealth_on_non_energy_footprint = SMOOTH ( Effect_of_Wealth_on_non_energy_footprint , Time_to_smooth_non_energy_footprint_changes )
        idx1 = fcol_in_mdf['Smoothed_Effect_of_Wealth_on_non_energy_footprint']
        idx2 = fcol_in_mdf['Effect_of_Wealth_on_non_energy_footprint']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1 , idx2] - mdf[rowi -1 , idx1 ]) / Time_to_smooth_non_energy_footprint_changes * dt
    
    # Non_energy_footprint_future = Non_energy_footprint_pp_future * Global_population * UNIT_conv_to_Mha_footprint * Smoothed_Effect_of_Wealth_on_non_energy_footprint
        idxlhs = fcol_in_mdf['Non_energy_footprint_future']
        idx1 = fcol_in_mdf['Non_energy_footprint_pp_future']
        idx2 = fcol_in_mdf['Global_population']
        idx3 = fcol_in_mdf['Smoothed_Effect_of_Wealth_on_non_energy_footprint']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2] *  UNIT_conv_to_Mha_footprint  * mdf[rowi, idx3]
    
    # Non_energy_footprint_pp = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1.6 ) , ( 1985 , 1.5 ) , ( 1990 , 1.44 ) , ( 1995 , 1.35 ) , ( 2000 , 1.28 ) , ( 2005 , 1.24 ) , ( 2010 , 1.13 ) , ( 2015 , 1.04 ) , ( 2020 , 0.99 ) ) )
        tabidx = ftab_in_d_table['Non_energy_footprint_pp'] # fetch the correct table
        idxlhs = fcol_in_mdf['Non_energy_footprint_pp'] # get the location of the lhs in mdf
        look = d_table[tabidx]
        valgt = GRAPH( zeit, look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # Non_energy_footprint_hist = Non_energy_footprint_pp * Global_population * UNIT_conv_to_Mha_footprint
        idxlhs = fcol_in_mdf['Non_energy_footprint_hist']
        idx1 = fcol_in_mdf['Non_energy_footprint_pp']
        idx2 = fcol_in_mdf['Global_population']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2] *  UNIT_conv_to_Mha_footprint 
    
    # Non_energy_footprint = IF_THEN_ELSE ( zeit >= 2020 , Non_energy_footprint_future , Non_energy_footprint_hist )
        idxlhs = fcol_in_mdf['Non_energy_footprint']
        idx1 = fcol_in_mdf['Non_energy_footprint_future']
        idx2 = fcol_in_mdf['Non_energy_footprint_hist']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  (  zeit  >=  2020  , mdf[rowi, idx1] , mdf[rowi, idx2] ) 
    
    # Smoothed_Non_energy_footprint = SMOOTH ( Non_energy_footprint , Time_to_smooth_non_energy_footprint_changes )
        idx1 = fcol_in_mdf['Smoothed_Non_energy_footprint']
        idx2 = fcol_in_mdf['Non_energy_footprint']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1 , idx2] - mdf[rowi -1 , idx1 ]) / Time_to_smooth_non_energy_footprint_changes * dt
    
    # Biocapacity_fraction_unused = ( Biocapacity - Smoothed_Non_energy_footprint ) / Biocapacity
        idxlhs = fcol_in_mdf['Biocapacity_fraction_unused']
        idx1 = fcol_in_mdf['Biocapacity']
        idx2 = fcol_in_mdf['Smoothed_Non_energy_footprint']
        idx3 = fcol_in_mdf['Biocapacity']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] - mdf[rowi, idx2] )  / mdf[rowi, idx3]
    
    # Biocapacity_risk_score = IF_THEN_ELSE ( Biocapacity_fraction_unused < pb_Biodiversity_loss_green_threshold , 1 , 0 )
        idxlhs = fcol_in_mdf['Biocapacity_risk_score']
        idx1 = fcol_in_mdf['Biocapacity_fraction_unused']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  ( mdf[rowi, idx1] <  pb_Biodiversity_loss_green_threshold  ,  1  ,  0  ) 
    
    # Effect_of_C_concentration_on_NMPP = 1 + LN ( Avg_C_concentration_in_top_layer / Concentration_of_C_in_ocean_top_layer_in_1850 ) / LN ( 2 )
        idxlhs = fcol_in_mdf['Effect_of_C_concentration_on_NMPP']
        idx1 = fcol_in_mdf['Avg_C_concentration_in_top_layer']
        mdf[rowi, idxlhs] =  1  +  np.log  ( mdf[rowi, idx1] /  Concentration_of_C_in_ocean_top_layer_in_1850  )  /  np.log  (  2  ) 
    
    # Temp_of_cold_downwelling_water = ( Temp_of_cold_surface_water + Temp_ocean_deep_in_C ) / 2
        idxlhs = fcol_in_mdf['Temp_of_cold_downwelling_water']
        idx1 = fcol_in_mdf['Temp_of_cold_surface_water']
        idx2 = fcol_in_mdf['Temp_ocean_deep_in_C']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] + mdf[rowi, idx2] )  /  2 
    
    # Carbon_concentration_in_CWTtB = C_in_cold_water_trunk_downwelling_GtC / ( Cold_water_volume_downwelling + Cumulative_ocean_volume_increase_due_to_ice_melting_km3 * UNIT_conversion_km3_to_Gm3 * Frac_vol_cold_ocean_downwelling_of_total )
        idxlhs = fcol_in_mdf['Carbon_concentration_in_CWTtB']
        idx1 = fcol_in_mdf['C_in_cold_water_trunk_downwelling_GtC']
        idx2 = fcol_in_mdf['Cumulative_ocean_volume_increase_due_to_ice_melting_km3']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  (  Cold_water_volume_downwelling  + mdf[rowi, idx2] *  UNIT_conversion_km3_to_Gm3  *  Frac_vol_cold_ocean_downwelling_of_total  ) 
    
    # CC_in_cold_downwelling_ymoles_per_litre = Carbon_concentration_in_CWTtB * UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre
        idxlhs = fcol_in_mdf['CC_in_cold_downwelling_ymoles_per_litre']
        idx1 = fcol_in_mdf['Carbon_concentration_in_CWTtB']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre 
    
    # CC_in_cold_downwelling_ymoles_per_litre_dmnl = CC_in_cold_downwelling_ymoles_per_litre * UNIT_conversion_ymoles_p_litre_to_dless
        idxlhs = fcol_in_mdf['CC_in_cold_downwelling_ymoles_per_litre_dmnl']
        idx1 = fcol_in_mdf['CC_in_cold_downwelling_ymoles_per_litre']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  UNIT_conversion_ymoles_p_litre_to_dless 
    
    # ph_in_cold_downwelling_water = UNIT_conversion_C_to_pH * ( 1 - 0.0017 * Temp_of_cold_downwelling_water - 0.0003 ) * ( 163.2 * CC_in_cold_downwelling_ymoles_per_litre_dmnl ^ ( - 0.385 ) )
        idxlhs = fcol_in_mdf['ph_in_cold_downwelling_water']
        idx1 = fcol_in_mdf['Temp_of_cold_downwelling_water']
        idx2 = fcol_in_mdf['CC_in_cold_downwelling_ymoles_per_litre_dmnl']
        mdf[rowi, idxlhs] =  UNIT_conversion_C_to_pH  *  (  1  -  0.0017  * mdf[rowi, idx1] -  0.0003  )  *  (  163.2  * mdf[rowi, idx2] **  (  -  0.385  )  ) 
    
    # Effect_of_acidification_on_NMPP = 1 + Slope_of_efffect_of_acidification_on_NMPP * ( ph_in_cold_downwelling_water / ph_in_cold_water_in_1980 - 1 )
        idxlhs = fcol_in_mdf['Effect_of_acidification_on_NMPP']
        idx1 = fcol_in_mdf['ph_in_cold_downwelling_water']
        mdf[rowi, idxlhs] =  1  +  Slope_of_efffect_of_acidification_on_NMPP  *  ( mdf[rowi, idx1] /  ph_in_cold_water_in_1980  -  1  ) 
    
    # Effect_of_temperature_on_NMPP = 1 + Slope_Effect_Temp_on_NMPP * ( Temp_surface / ( Temp_surface_1850 - 273.15 ) - 1 )
        idxlhs = fcol_in_mdf['Effect_of_temperature_on_NMPP']
        idx1 = fcol_in_mdf['Temp_surface']
        mdf[rowi, idxlhs] =  1  +  Slope_Effect_Temp_on_NMPP  *  ( mdf[rowi, idx1] /  (  Temp_surface_1850  -  273.15  )  -  1  ) 
    
    # Net_marine_primary_production_NMPP_GtC_pr_yr = Net_marine_primary_production_in_1850 * Effect_of_C_concentration_on_NMPP * Effect_of_acidification_on_NMPP * Effect_of_temperature_on_NMPP
        idxlhs = fcol_in_mdf['Net_marine_primary_production_NMPP_GtC_pr_yr']
        idx1 = fcol_in_mdf['Effect_of_C_concentration_on_NMPP']
        idx2 = fcol_in_mdf['Effect_of_acidification_on_NMPP']
        idx3 = fcol_in_mdf['Effect_of_temperature_on_NMPP']
        mdf[rowi, idxlhs] =  Net_marine_primary_production_in_1850  * mdf[rowi, idx1] * mdf[rowi, idx2] * mdf[rowi, idx3]
    
    # Biological_removal_of_C_from_WSW_GtC_per_yr = SMOOTH ( Net_marine_primary_production_NMPP_GtC_pr_yr , Time_to_let_shells_form_and_sink_to_sediment_yr )
        idx1 = fcol_in_mdf['Biological_removal_of_C_from_WSW_GtC_per_yr']
        idx2 = fcol_in_mdf['Net_marine_primary_production_NMPP_GtC_pr_yr']
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1 , idx2] - mdf[rowi -1 , idx1 ]) / Time_to_let_shells_form_and_sink_to_sediment_yr * dt
    
    # birth_rate_CN = ( birth_rate_a_CN * np.exp ( birth_rate_b_CN * GDPpp_USED[cn] * UNIT_conv_to_make_exp_dmnl ) - birth_rate_c_CN * np.exp ( birth_rate_d_CN * GDPpp_USED[cn] * UNIT_conv_to_make_exp_dmnl ) ) * UNIT_conv_to_make_the_bell_shaped_birth_rate_formula_have_units_of_1_pr_y
        idxlhs = fcol_in_mdf['birth_rate_CN']
        idx1 = fcol_in_mdf['GDPpp_USED']
        idx2 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs] =  (  birth_rate_a_CN  *  np.exp  (  birth_rate_b_CN  * mdf[rowi, idx1 + 2] *  UNIT_conv_to_make_exp_dmnl  )  -  birth_rate_c_CN  *  np.exp  (  birth_rate_d_CN  * mdf[rowi, idx2 + 2] *  UNIT_conv_to_make_exp_dmnl  )  )  *  UNIT_conv_to_make_the_bell_shaped_birth_rate_formula_have_units_of_1_pr_y 
    
    # birth_rate_WO_CN[region] = birth_rate_a[region] * ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl ) ^ birth_rate_b[region] + birth_rate_c[region]
        idxlhs = fcol_in_mdf['birth_rate_WO_CN']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  birth_rate_a[0:10]  *  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  )  **  birth_rate_b[0:10]  +  birth_rate_c[0:10] 
    
    # birth_rate_as_f_GDPpp_alone = IF_THEN_ELSE ( j==2 , birth_rate_CN , birth_rate_WO_CN )
        idxlhs = fcol_in_mdf['birth_rate_as_f_GDPpp_alone']
        idx1 = fcol_in_mdf['birth_rate_CN']
        idx2 = fcol_in_mdf['birth_rate_WO_CN']
        for j in range(0,10):
            mdf[rowi, idxlhs + j] =  IF_THEN_ELSE  (  j==2  , mdf[rowi , idx1] , mdf[rowi , idx2 + j] ) 
    
    # birth_rate[region] = SMOOTH3 ( birth_rate_as_f_GDPpp_alone[region] , Time_to_adjust_cultural_birth_rate_norm[region] )
        idxin = fcol_in_mdf['birth_rate_as_f_GDPpp_alone' ]
        idx2 = fcol_in_mdf['birth_rate_2']
        idx1 = fcol_in_mdf['birth_rate_1']
        idxout = fcol_in_mdf['birth_rate']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( Time_to_adjust_cultural_birth_rate_norm[0:10]  / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( Time_to_adjust_cultural_birth_rate_norm[0:10]  / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( Time_to_adjust_cultural_birth_rate_norm[0:10]  / 3) * dt
    
    # Cohort_15_to_45[region] = Cohort_15_to_19[region] + Cohort_20_to_24[region] + Cohort_25_to_29[region] + Cohort_30_to_34[region] + Cohort_35_to_39[region] + Cohort_40_to_44[region]
        idxlhs = fcol_in_mdf['Cohort_15_to_45']
        idx1 = fcol_in_mdf['Cohort_15_to_19']
        idx2 = fcol_in_mdf['Cohort_20_to_24']
        idx3 = fcol_in_mdf['Cohort_25_to_29']
        idx4 = fcol_in_mdf['Cohort_30_to_34']
        idx5 = fcol_in_mdf['Cohort_35_to_39']
        idx6 = fcol_in_mdf['Cohort_40_to_44']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] + mdf[rowi , idx4:idx4 + 10] + mdf[rowi , idx5:idx5 + 10] + mdf[rowi , idx6:idx6 + 10]
    
    # Births[region] = Cohort_15_to_45[region] * Births_effect_from_cohorts_outside_15_to_45[region] * birth_rate[region] * FEHC_mult_used[region]
        idxlhs = fcol_in_mdf['Births']
        idx1 = fcol_in_mdf['Cohort_15_to_45']
        idx2 = fcol_in_mdf['birth_rate']
        idx3 = fcol_in_mdf['FEHC_mult_used']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  Births_effect_from_cohorts_outside_15_to_45[0:10]  * mdf[rowi , idx2:idx2 + 10] * mdf[rowi , idx3:idx3 + 10]
    
    # MODEL_CH4_in_atm_in_ppb = C_in_atmosphere_in_form_of_CH4 * conversion_factor_CH4_Gt_to_ppb
        idxlhs = fcol_in_mdf['MODEL_CH4_in_atm_in_ppb']
        idx1 = fcol_in_mdf['C_in_atmosphere_in_form_of_CH4']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  conversion_factor_CH4_Gt_to_ppb 
    
    # CH4_concentration_ppb = MODEL_CH4_in_atm_in_ppb
        idxlhs = fcol_in_mdf['CH4_concentration_ppb']
        idx1 = fcol_in_mdf['MODEL_CH4_in_atm_in_ppb']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # Fraction_blocked_by_CH4_spectrum = WITH LOOKUP ( CH4_concentration_ppb , ( [ ( 0 , 0 ) - ( 1e+06 , 0.2 ) ] , ( 0 , 0 ) , ( 350 , 0.0028 ) , ( 700 , 0.0042 ) , ( 1200 , 0.0056 ) , ( 1700 , 0.007 ) , ( 3000 , 0.0106 ) , ( 5000 , 0.0125 ) , ( 7000 , 0.013477 ) , ( 10000 , 0.0153945 ) , ( 20000 , 0.0201881 ) , ( 40000 , 0.0259404 ) , ( 70000 , 0.0316927 ) , ( 100000 , 0.0355276 ) , ( 150000 , 0.0403212 ) , ( 250000 , 0.0456888 ) , ( 500000 , 0.0539356 ) , ( 1e+06 , 0.0625641 ) , ( 1e+07 , 0.0954476 ) , ( 1e+08 , 0.130154 ) , ( 5e+08 , 0.152204 ) , ( 9e+08 , 0.159776 ) , ( 1e+09 , 0.16112 ) ) )
        tabidx = ftab_in_d_table['Fraction_blocked_by_CH4_spectrum'] # fetch the correct table
        idxlhs = fcol_in_mdf['Fraction_blocked_by_CH4_spectrum'] # get the location of the lhs in mdf
        idx1 = fcol_in_mdf['CH4_concentration_ppb']
        look = d_table[tabidx]
        valgt = GRAPH(mdf[rowi,  idx1], look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # Blocked_by_CH4 = Fraction_blocked_by_CH4_spectrum
        idxlhs = fcol_in_mdf['Blocked_by_CH4']
        idx1 = fcol_in_mdf['Fraction_blocked_by_CH4_spectrum']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # CO2_concentration_ppm = CO2_concentration_used_after_any_experiments_ppm
        idxlhs = fcol_in_mdf['CO2_concentration_ppm']
        idx1 = fcol_in_mdf['CO2_concentration_used_after_any_experiments_ppm']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # Fraction_blocked_by_CO2_spectrum = WITH LOOKUP ( CO2_concentration_ppm , ( [ ( 0 , 0 ) - ( 1000 , 0.2 ) ] , ( 0 , 0 ) , ( 40 , 0.0508772 ) , ( 100 , 0.0756579 ) , ( 200 , 0.085978 ) , ( 285 , 0.091138 ) , ( 300 , 0.0919195 ) , ( 400 , 0.0960065 ) , ( 500 , 0.0993184 ) , ( 570 , 0.10117 ) , ( 600 , 0.1019 ) , ( 800 , 0.106134 ) , ( 1000 , 0.109347 ) , ( 10000 , 0.146835 ) ) )
        tabidx = ftab_in_d_table['Fraction_blocked_by_CO2_spectrum'] # fetch the correct table
        idxlhs = fcol_in_mdf['Fraction_blocked_by_CO2_spectrum'] # get the location of the lhs in mdf
        idx1 = fcol_in_mdf['CO2_concentration_ppm']
        look = d_table[tabidx]
        valgt = GRAPH(mdf[rowi,  idx1], look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # Blocked_by_CO2 = Fraction_blocked_by_CO2_spectrum
        idxlhs = fcol_in_mdf['Blocked_by_CO2']
        idx1 = fcol_in_mdf['Fraction_blocked_by_CO2_spectrum']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # Humidity_of_atmosphere_current_g_p_kg = Humidity_of_atmosphere
        idxlhs = fcol_in_mdf['Humidity_of_atmosphere_current_g_p_kg']
        idx1 = fcol_in_mdf['Humidity_of_atmosphere']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # Blocked_by_H20_Table_lookup = WITH LOOKUP ( Humidity_of_atmosphere_current_g_p_kg , ( [ ( 1.7 , 0 ) - ( 2.5 , 0.2 ) ] , ( 1.76 , 0.06 ) , ( 1.85 , 0.0638 ) , ( 1.9 , 0.0649123 ) , ( 1.95 , 0.071 ) , ( 1.97 , 0.0753 ) , ( 1.99 , 0.081 ) , ( 2.00026 , 0.0846 ) , ( 2.02999 , 0.092 ) , ( 2.05039 , 0.0976 ) , ( 2.07286 , 0.1025 ) , ( 2.10017 , 0.109 ) , ( 2.11642 , 0.113 ) , ( 2.14996 , 0.1205 ) , ( 2.16275 , 0.1235 ) , ( 2.18522 , 0.129 ) , ( 2.20009 , 0.132 ) , ( 2.21288 , 0.135 ) , ( 2.235 , 0.14 ) , ( 2.25022 , 0.144 ) , ( 2.26992 , 0.148 ) , ( 2.3 , 0.155 ) , ( 2.4 , 0.174 ) , ( 2.5 , 0.19 ) ) )
        tabidx = ftab_in_d_table['Blocked_by_H20_Table_lookup'] # fetch the correct table
        idxlhs = fcol_in_mdf['Blocked_by_H20_Table_lookup'] # get the location of the lhs in mdf
        idx1 = fcol_in_mdf['Humidity_of_atmosphere_current_g_p_kg']
        look = d_table[tabidx]
        valgt = GRAPH(mdf[rowi,  idx1], look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # Blocked_by_H20 = Blocked_by_H20_Table_lookup
        idxlhs = fcol_in_mdf['Blocked_by_H20']
        idx1 = fcol_in_mdf['Blocked_by_H20_Table_lookup']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # Kyoto_Fluor_concentration_ppt = Kyoto_Fluor_gases_in_atm * Conversion_from_Kyoto_Fluor_amount_to_concentration_ppt_p_kt
        idxlhs = fcol_in_mdf['Kyoto_Fluor_concentration_ppt']
        idx1 = fcol_in_mdf['Kyoto_Fluor_gases_in_atm']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Conversion_from_Kyoto_Fluor_amount_to_concentration_ppt_p_kt 
    
    # Blocking_multiplier_from_Kyoto_Fluor = IF_THEN_ELSE ( zeit > 1970 , 1 + Slope_btw_Kyoto_Fluor_ppt_and_blocking_multiplier / 1000 * ( Kyoto_Fluor_concentration_ppt / Kyoto_Fluor_concentration_in_1970_ppt - 1 ) , 1 )
        idxlhs = fcol_in_mdf['Blocking_multiplier_from_Kyoto_Fluor']
        idx1 = fcol_in_mdf['Kyoto_Fluor_concentration_ppt']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  (  zeit  >  1970  ,  1  +  Slope_btw_Kyoto_Fluor_ppt_and_blocking_multiplier  /  1000  *  ( mdf[rowi, idx1] /  Kyoto_Fluor_concentration_in_1970_ppt  -  1  )  ,  1  ) 
    
    # Montreal_gases_concentration_ppt = Montreal_gases_in_atm * Conversion_from_Montreal_gases_amount_to_concentration_ppt_p_kt
        idxlhs = fcol_in_mdf['Montreal_gases_concentration_ppt']
        idx1 = fcol_in_mdf['Montreal_gases_in_atm']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Conversion_from_Montreal_gases_amount_to_concentration_ppt_p_kt 
    
    # Blocking_multiplier_from_Montreal_gases = IF_THEN_ELSE ( zeit > 1970 , 1 + Slope_btw_Montreal_gases_ppt_and_blocking_multiplier / 100 * ( Montreal_gases_concentration_ppt / Montreal_gases_concentration_in_1970_ppt - 1 ) , 1 )
        idxlhs = fcol_in_mdf['Blocking_multiplier_from_Montreal_gases']
        idx1 = fcol_in_mdf['Montreal_gases_concentration_ppt']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  (  zeit  >  1970  ,  1  +  Slope_btw_Montreal_gases_ppt_and_blocking_multiplier  /  100  *  ( mdf[rowi, idx1] /  Montreal_gases_concentration_in_1970_ppt  -  1  )  ,  1  ) 
    
    # N2O_concentration_ppb = N2O_in_atmosphere_MtN2O * UNIT_Conversion_from_N2O_amount_to_concentration_ppb_p_MtN2O
        idxlhs = fcol_in_mdf['N2O_concentration_ppb']
        idx1 = fcol_in_mdf['N2O_in_atmosphere_MtN2O']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  UNIT_Conversion_from_N2O_amount_to_concentration_ppb_p_MtN2O 
    
    # Blocking_multiplier_from_N2O = 1 + Slope_btw_N2O_ppb_and_blocking_multiplier * ( N2O_concentration_ppb / Model_N2O_concentration_in_1850_ppb - 1 )
        idxlhs = fcol_in_mdf['Blocking_multiplier_from_N2O']
        idx1 = fcol_in_mdf['N2O_concentration_ppb']
        mdf[rowi, idxlhs] =  1  +  Slope_btw_N2O_ppb_and_blocking_multiplier  *  ( mdf[rowi, idx1] /  Model_N2O_concentration_in_1850_ppb  -  1  ) 
    
    # LW_Blocking_multiplier_from_other_GHG = ( Blocking_multiplier_from_Kyoto_Fluor + Blocking_multiplier_from_Montreal_gases + Blocking_multiplier_from_N2O ) / 3
        idxlhs = fcol_in_mdf['LW_Blocking_multiplier_from_other_GHG']
        idx1 = fcol_in_mdf['Blocking_multiplier_from_Kyoto_Fluor']
        idx2 = fcol_in_mdf['Blocking_multiplier_from_Montreal_gases']
        idx3 = fcol_in_mdf['Blocking_multiplier_from_N2O']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] )  /  3 
    
    # Fraction_blocked_by_other_GHG = LW_radiation_fraction_blocked_by_other_GHG_in_1850 * LW_Blocking_multiplier_from_other_GHG
        idxlhs = fcol_in_mdf['Fraction_blocked_by_other_GHG']
        idx1 = fcol_in_mdf['LW_Blocking_multiplier_from_other_GHG']
        mdf[rowi, idxlhs] =  LW_radiation_fraction_blocked_by_other_GHG_in_1850  * mdf[rowi, idx1]
    
    # Blocked_by_otherGHG = Fraction_blocked_by_other_GHG
        idxlhs = fcol_in_mdf['Blocked_by_otherGHG']
        idx1 = fcol_in_mdf['Fraction_blocked_by_other_GHG']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # Ratio_of_area_covered_by_low_clouds_current_to_init = Area_covered_by_low_clouds / Area_covered_by_low_clouds_in_1980
        idxlhs = fcol_in_mdf['Ratio_of_area_covered_by_low_clouds_current_to_init']
        idx1 = fcol_in_mdf['Area_covered_by_low_clouds']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Area_covered_by_low_clouds_in_1980 
    
    # LW_LO_cloud_radiation = LW_LO_cloud_radiation_reference_in_1980 * UNIT_conversion_W_p_m2_earth_to_ZJ_py * Ratio_of_area_covered_by_low_clouds_current_to_init
        idxlhs = fcol_in_mdf['LW_LO_cloud_radiation']
        idx1 = fcol_in_mdf['Ratio_of_area_covered_by_low_clouds_current_to_init']
        mdf[rowi, idxlhs] =  LW_LO_cloud_radiation_reference_in_1980  *  UNIT_conversion_W_p_m2_earth_to_ZJ_py  * mdf[rowi, idx1]
    
    # Ratio_of_area_covered_by_high_clouds_current_to_init = Area_covered_by_high_clouds / Area_covered_by_high_clouds_in_1980
        idxlhs = fcol_in_mdf['Ratio_of_area_covered_by_high_clouds_current_to_init']
        idx1 = fcol_in_mdf['Area_covered_by_high_clouds']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Area_covered_by_high_clouds_in_1980 
    
    # LW_HI_cloud_radiation = LW_HI_cloud_radiation_reference_in_1980 * UNIT_conversion_W_p_m2_earth_to_ZJ_py * Ratio_of_area_covered_by_high_clouds_current_to_init
        idxlhs = fcol_in_mdf['LW_HI_cloud_radiation']
        idx1 = fcol_in_mdf['Ratio_of_area_covered_by_high_clouds_current_to_init']
        mdf[rowi, idxlhs] =  LW_HI_cloud_radiation_reference_in_1980  *  UNIT_conversion_W_p_m2_earth_to_ZJ_py  * mdf[rowi, idx1]
    
    # Blocking_of_LW_rad_by_clouds = LW_LO_cloud_radiation + LW_HI_cloud_radiation
        idxlhs = fcol_in_mdf['Blocking_of_LW_rad_by_clouds']
        idx1 = fcol_in_mdf['LW_LO_cloud_radiation']
        idx2 = fcol_in_mdf['LW_HI_cloud_radiation']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2]
    
    # Budget_for_all_TA_per_region_calculated_as_pct_of_GDP[region] = GDP_USED[region] * pct_of_GDP_budgeted_for_GL
        idxlhs = fcol_in_mdf['Budget_for_all_TA_per_region_calculated_as_pct_of_GDP']
        idx1 = fcol_in_mdf['GDP_USED']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  pct_of_GDP_budgeted_for_GL 
    
    # Eff_of_env_damage_on_costs_of_TAs[region] = np.exp ( Combined_env_damage_indicator * expSoE_of_ed_on_cost_of_TAs ) / Actual_eff_of_relative_wealth_on_env_damage[region]
        idxlhs = fcol_in_mdf['Eff_of_env_damage_on_costs_of_TAs']
        idx1 = fcol_in_mdf['Combined_env_damage_indicator']
        idx2 = fcol_in_mdf['Actual_eff_of_relative_wealth_on_env_damage']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.exp  ( mdf[rowi , idx1] *  expSoE_of_ed_on_cost_of_TAs  )  / mdf[rowi , idx2:idx2 + 10]
    
    # Smoothed_Eff_of_env_damage_on_costs_of_TAs[region] = SMOOTH ( Eff_of_env_damage_on_costs_of_TAs[region] , Time_to_smooth_effect_of_env_dam_on_TAs )
        idx1 = fcol_in_mdf['Smoothed_Eff_of_env_damage_on_costs_of_TAs']
        idx2 = fcol_in_mdf['Eff_of_env_damage_on_costs_of_TAs']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1+10] + ( mdf[rowi-1 , idx2:idx2 + 10] - mdf[rowi -1 , idx1:idx1 + 10]) / Time_to_smooth_effect_of_env_dam_on_TAs * dt
    
    # Each_region_max_cost_estimate_energy_PES_with_env_dam_and_reform[region] = Each_region_max_cost_estimate_energy_PES[region] * Smoothed_Eff_of_env_damage_on_costs_of_TAs[region] / Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['Each_region_max_cost_estimate_energy_PES_with_env_dam_and_reform']
        idx1 = fcol_in_mdf['Each_region_max_cost_estimate_energy_PES']
        idx2 = fcol_in_mdf['Smoothed_Eff_of_env_damage_on_costs_of_TAs']
        idx3 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] / mdf[rowi , idx3:idx3 + 10]
    
    # Cost_per_regional_energy_policy[region] = Each_region_max_cost_estimate_energy_PES_with_env_dam_and_reform[region] / Nbr_of_relevant_energy_policies
        idxlhs = fcol_in_mdf['Cost_per_regional_energy_policy']
        idx1 = fcol_in_mdf['Each_region_max_cost_estimate_energy_PES_with_env_dam_and_reform']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Nbr_of_relevant_energy_policies 
    
    # Cutback_fraction_applied[region] = SMOOTH3I ( Shortfall_as_pct_of_needed[region] , Time_to_implement_cutbacks , 0 )
        idxin = fcol_in_mdf['Shortfall_as_pct_of_needed']
        idx2 = fcol_in_mdf['Cutback_fraction_applied_2']
        idx1 = fcol_in_mdf['Cutback_fraction_applied_1']
        idxout = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( Time_to_implement_cutbacks / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( Time_to_implement_cutbacks / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( Time_to_implement_cutbacks / 3) * dt
    
    # Planned_Spending_on_CCS[region] = Cost_per_regional_energy_policy[region] * ( ( CCS_policy[region] * 100 ) / CCS_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_CCS']
        idx1 = fcol_in_mdf['Cost_per_regional_energy_policy']
        idx2 = fcol_in_mdf['CCS_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] *  100  )  /  CCS_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_Spending_on_DAC[region] = Cost_per_regional_energy_policy[region] * ( ( DAC_policy[region] * 1 ) / DAC_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_DAC']
        idx1 = fcol_in_mdf['Cost_per_regional_energy_policy']
        idx2 = fcol_in_mdf['DAC_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] *  1  )  /  DAC_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_Spending_on_FTPEE[region] = Cost_per_regional_energy_policy[region] * ( ( FTPEE_rate_of_change_policy[region] - FTPEE_policy_Min ) / FTPEE_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_FTPEE']
        idx1 = fcol_in_mdf['Cost_per_regional_energy_policy']
        idx2 = fcol_in_mdf['FTPEE_rate_of_change_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] -  FTPEE_policy_Min  )  /  FTPEE_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_Spending_on_ISPV[region] = Cost_per_regional_energy_policy[region] * ( ( ( wind_and_PV_el_share_max[region] - ISPV_policy_Min / 100 ) * 100 ) / ISPV_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_ISPV']
        idx1 = fcol_in_mdf['Cost_per_regional_energy_policy']
        idx2 = fcol_in_mdf['wind_and_PV_el_share_max']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  (  ( mdf[rowi , idx2:idx2 + 10] -  ISPV_policy_Min  /  100  )  *  100  )  /  ISPV_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_Spending_on_NEP[region] = Cost_per_regional_energy_policy[region] * ( ( NEP_policy[region] * 100 ) / NEP_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_NEP']
        idx1 = fcol_in_mdf['Cost_per_regional_energy_policy']
        idx2 = fcol_in_mdf['NEP_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] *  100  )  /  NEP_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_investments_for_energy[region] = Planned_Spending_on_CCS[region] + Planned_Spending_on_DAC[region] + Planned_Spending_on_FTPEE[region] + Planned_Spending_on_ISPV[region] + Planned_Spending_on_NEP[region]
        idxlhs = fcol_in_mdf['Planned_investments_for_energy']
        idx1 = fcol_in_mdf['Planned_Spending_on_CCS']
        idx2 = fcol_in_mdf['Planned_Spending_on_DAC']
        idx3 = fcol_in_mdf['Planned_Spending_on_FTPEE']
        idx4 = fcol_in_mdf['Planned_Spending_on_ISPV']
        idx5 = fcol_in_mdf['Planned_Spending_on_NEP']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] + mdf[rowi , idx4:idx4 + 10] + mdf[rowi , idx5:idx5 + 10]
    
    # Each_region_max_cost_estimate_food_PES_with_env_dam_and_reform[region] = Each_region_max_cost_estimate_food_PES[region] * Smoothed_Eff_of_env_damage_on_costs_of_TAs[region] / Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['Each_region_max_cost_estimate_food_PES_with_env_dam_and_reform']
        idx1 = fcol_in_mdf['Each_region_max_cost_estimate_food_PES']
        idx2 = fcol_in_mdf['Smoothed_Eff_of_env_damage_on_costs_of_TAs']
        idx3 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] / mdf[rowi , idx3:idx3 + 10]
    
    # Cost_per_regional_food_policy[region] = Each_region_max_cost_estimate_food_PES_with_env_dam_and_reform[region] / Nbr_of_relevant_food_policies
        idxlhs = fcol_in_mdf['Cost_per_regional_food_policy']
        idx1 = fcol_in_mdf['Each_region_max_cost_estimate_food_PES_with_env_dam_and_reform']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Nbr_of_relevant_food_policies 
    
    # Planned_Spending_on_FLWR[region] = Cost_per_regional_food_policy[region] * ( ( FLWR_policy[region] * 100 ) / FLWR_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_FLWR']
        idx1 = fcol_in_mdf['Cost_per_regional_food_policy']
        idx2 = fcol_in_mdf['FLWR_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] *  100  )  /  FLWR_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_Spending_on_FWRP[region] = Cost_per_regional_food_policy[region] * ( ( FWRP_policy[region] * 100 ) / FWRP_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_FWRP']
        idx1 = fcol_in_mdf['Cost_per_regional_food_policy']
        idx2 = fcol_in_mdf['FWRP_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] *  100  )  /  FWRP_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_Spending_on_REFOREST[region] = Cost_per_regional_food_policy[region] * ( ( REFOREST_policy[region] * 100 ) / REFOREST_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_REFOREST']
        idx1 = fcol_in_mdf['Cost_per_regional_food_policy']
        idx2 = fcol_in_mdf['REFOREST_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] *  100  )  /  REFOREST_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_Spending_on_RIPLGF[region] = Cost_per_regional_food_policy[region] * ( ( RIPLGF_policy[region] * 100 ) / RIPLGF_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_RIPLGF']
        idx1 = fcol_in_mdf['Cost_per_regional_food_policy']
        idx2 = fcol_in_mdf['RIPLGF_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] *  100  )  /  RIPLGF_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_Spending_on_RMDR[region] = Cost_per_regional_food_policy[region] * ( ( RMDR_policy[region] * 100 ) / RMDR_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_RMDR']
        idx1 = fcol_in_mdf['Cost_per_regional_food_policy']
        idx2 = fcol_in_mdf['RMDR_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] *  100  )  /  RMDR_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_investments_for_food[region] = Planned_Spending_on_FLWR[region] + Planned_Spending_on_FWRP[region] + Planned_Spending_on_REFOREST[region] + Planned_Spending_on_RIPLGF[region] + Planned_Spending_on_RMDR[region]
        idxlhs = fcol_in_mdf['Planned_investments_for_food']
        idx1 = fcol_in_mdf['Planned_Spending_on_FLWR']
        idx2 = fcol_in_mdf['Planned_Spending_on_FWRP']
        idx3 = fcol_in_mdf['Planned_Spending_on_REFOREST']
        idx4 = fcol_in_mdf['Planned_Spending_on_RIPLGF']
        idx5 = fcol_in_mdf['Planned_Spending_on_RMDR']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] + mdf[rowi , idx4:idx4 + 10] + mdf[rowi , idx5:idx5 + 10]
    
    # Each_region_max_cost_estimate_inequality_PES_with_env_dam_and_reform[region] = Each_region_max_cost_estimate_inequality_PES[region] * Smoothed_Eff_of_env_damage_on_costs_of_TAs[region] / Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['Each_region_max_cost_estimate_inequality_PES_with_env_dam_and_reform']
        idx1 = fcol_in_mdf['Each_region_max_cost_estimate_inequality_PES']
        idx2 = fcol_in_mdf['Smoothed_Eff_of_env_damage_on_costs_of_TAs']
        idx3 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] / mdf[rowi , idx3:idx3 + 10]
    
    # Cost_per_regional_inequality_policy[region] = Each_region_max_cost_estimate_inequality_PES_with_env_dam_and_reform[region] / Nbr_of_relevant_inequality_policies
        idxlhs = fcol_in_mdf['Cost_per_regional_inequality_policy']
        idx1 = fcol_in_mdf['Each_region_max_cost_estimate_inequality_PES_with_env_dam_and_reform']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Nbr_of_relevant_inequality_policies 
    
    # Cost_per_regional_inequality_policy2[region] = Cost_per_regional_inequality_policy[region]
        idxlhs = fcol_in_mdf['Cost_per_regional_inequality_policy2']
        idx1 = fcol_in_mdf['Cost_per_regional_inequality_policy']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10]
    
    # Planned_Spending_on_Ctax[region] = Cost_per_regional_inequality_policy2[region] * ( ( Ctax_policy[region] * 1 ) / Ctax_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_Ctax']
        idx1 = fcol_in_mdf['Cost_per_regional_inequality_policy2']
        idx2 = fcol_in_mdf['Ctax_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] *  1  )  /  Ctax_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_Spending_on_ICTR[region] = Cost_per_regional_inequality_policy2[region] * ( ( ICTR_policy[region] * 100 ) / ICTR_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_ICTR']
        idx1 = fcol_in_mdf['Cost_per_regional_inequality_policy2']
        idx2 = fcol_in_mdf['ICTR_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] *  100  )  /  ICTR_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_Spending_on_IOITR[region] = Cost_per_regional_inequality_policy2[region] * ( ( IOITR_policy[region] * 100 ) / IOITR_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_IOITR']
        idx1 = fcol_in_mdf['Cost_per_regional_inequality_policy2']
        idx2 = fcol_in_mdf['IOITR_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] *  100  )  /  IOITR_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_Spending_on_IWITR[region] = Cost_per_regional_inequality_policy2[region] * ( ( IWITR_policy[region] * 100 ) / IWITR_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_IWITR']
        idx1 = fcol_in_mdf['Cost_per_regional_inequality_policy2']
        idx2 = fcol_in_mdf['IWITR_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] *  100  )  /  IWITR_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_Spending_on_SGRPI[region] = Cost_per_regional_inequality_policy2[region] * ( ( SGRPI_policy[region] * 100 ) / SGRPI_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_SGRPI']
        idx1 = fcol_in_mdf['Cost_per_regional_inequality_policy2']
        idx2 = fcol_in_mdf['SGRPI_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] *  100  )  /  SGRPI_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_Spending_on_StrUP[region] = Cost_per_regional_inequality_policy2[region] * ( ( StrUP_policy[region] * 100 ) / StrUP_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_StrUP']
        idx1 = fcol_in_mdf['Cost_per_regional_inequality_policy2']
        idx2 = fcol_in_mdf['StrUP_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] *  100  )  /  StrUP_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_Spending_on_Wreaction[region] = Cost_per_regional_inequality_policy2[region] * ( ( WReaction_policy[region] * 100 ) / WReaction_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_Wreaction']
        idx1 = fcol_in_mdf['Cost_per_regional_inequality_policy2']
        idx2 = fcol_in_mdf['WReaction_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] *  100  )  /  Wreaction_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_Spending_on_XtaxCom[region] = Cost_per_regional_inequality_policy2[region] * ( ( XtaxCom_policy[region] * 100 ) / XtaxCom_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_XtaxCom']
        idx1 = fcol_in_mdf['Cost_per_regional_inequality_policy2']
        idx2 = fcol_in_mdf['XtaxCom_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] *  100  )  /  XtaxCom_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_Spending_on_XtaxFrac[region] = Cost_per_regional_inequality_policy2[region] * ( ( ( Xtaxfrac_policy[region] - Xtaxfrac_policy_Min / 100 ) * 100 ) / Xtaxfrac_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_XtaxFrac']
        idx1 = fcol_in_mdf['Cost_per_regional_inequality_policy2']
        idx2 = fcol_in_mdf['Xtaxfrac_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  (  ( mdf[rowi , idx2:idx2 + 10] -  XtaxFrac_policy_Min  /  100  )  *  100  )  /  XtaxFrac_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_investments_for_inequality[region] = Planned_Spending_on_Ctax[region] + Planned_Spending_on_ICTR[region] + Planned_Spending_on_IOITR[region] + Planned_Spending_on_IWITR[region] + Planned_Spending_on_SGRPI[region] + Planned_Spending_on_StrUP[region] + Planned_Spending_on_Wreaction[region] + Planned_Spending_on_XtaxCom[region] + Planned_Spending_on_XtaxFrac[region]
        idxlhs = fcol_in_mdf['Planned_investments_for_inequality']
        idx1 = fcol_in_mdf['Planned_Spending_on_Ctax']
        idx2 = fcol_in_mdf['Planned_Spending_on_ICTR']
        idx3 = fcol_in_mdf['Planned_Spending_on_IOITR']
        idx4 = fcol_in_mdf['Planned_Spending_on_IWITR']
        idx5 = fcol_in_mdf['Planned_Spending_on_SGRPI']
        idx6 = fcol_in_mdf['Planned_Spending_on_StrUP']
        idx7 = fcol_in_mdf['Planned_Spending_on_Wreaction']
        idx8 = fcol_in_mdf['Planned_Spending_on_XtaxCom']
        idx9 = fcol_in_mdf['Planned_Spending_on_XtaxFrac']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] + mdf[rowi , idx4:idx4 + 10] + mdf[rowi , idx5:idx5 + 10] + mdf[rowi , idx6:idx6 + 10] + mdf[rowi , idx7:idx7 + 10] + mdf[rowi , idx8:idx8 + 10] + mdf[rowi , idx9:idx9 + 10]
    
    # Each_region_max_cost_estimate_empowerment_PES_with_env_dam_and_reform[region] = Each_region_max_cost_estimate_empowerment_PES[region] * Smoothed_Eff_of_env_damage_on_costs_of_TAs[region] / Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['Each_region_max_cost_estimate_empowerment_PES_with_env_dam_and_reform']
        idx1 = fcol_in_mdf['Each_region_max_cost_estimate_empowerment_PES']
        idx2 = fcol_in_mdf['Smoothed_Eff_of_env_damage_on_costs_of_TAs']
        idx3 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] / mdf[rowi , idx3:idx3 + 10]
    
    # Cost_per_regional_empowerment_policy[region] = Each_region_max_cost_estimate_empowerment_PES_with_env_dam_and_reform[region] / Nbr_of_relevant_empowerment_policies
        idxlhs = fcol_in_mdf['Cost_per_regional_empowerment_policy']
        idx1 = fcol_in_mdf['Each_region_max_cost_estimate_empowerment_PES_with_env_dam_and_reform']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Nbr_of_relevant_empowerment_policies 
    
    # Spent_on_FEHC[region] = Cost_per_regional_empowerment_policy[region] * ( ( FEHC_policy[region] * 100 ) / FEHC_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Spent_on_FEHC']
        idx1 = fcol_in_mdf['Cost_per_regional_empowerment_policy']
        idx2 = fcol_in_mdf['FEHC_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] *  100  )  /  FEHC_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Spent_on_SGMP[region] = Cost_per_regional_empowerment_policy[region] * ( ( SGMP_policy[region] * 100 ) / SGMP_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Spent_on_SGMP']
        idx1 = fcol_in_mdf['Cost_per_regional_empowerment_policy']
        idx2 = fcol_in_mdf['SGMP_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] *  100  )  /  SGMP_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Spent_on_XtaxRateEmp[region] = Cost_per_regional_empowerment_policy[region] * ( ( XtaxRateEmp_policy[region] * 100 ) / XtaxRateEmp_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Spent_on_XtaxRateEmp']
        idx1 = fcol_in_mdf['Cost_per_regional_empowerment_policy']
        idx2 = fcol_in_mdf['XtaxRateEmp_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] *  100  )  /  XtaxEmp_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_Spending_on_Empowerment[region] = Spent_on_FEHC[region] + Spent_on_SGMP[region] + Spent_on_XtaxRateEmp[region]
        idxlhs = fcol_in_mdf['Planned_Spending_on_Empowerment']
        idx1 = fcol_in_mdf['Spent_on_FEHC']
        idx2 = fcol_in_mdf['Spent_on_SGMP']
        idx3 = fcol_in_mdf['Spent_on_XtaxRateEmp']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10]
    
    # Each_region_max_cost_estimate_poverty_PES_with_env_dam_and_reform[region] = Each_region_max_cost_estimate_poverty_PES[region] * Smoothed_Eff_of_env_damage_on_costs_of_TAs[region] / Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['Each_region_max_cost_estimate_poverty_PES_with_env_dam_and_reform']
        idx1 = fcol_in_mdf['Each_region_max_cost_estimate_poverty_PES']
        idx2 = fcol_in_mdf['Smoothed_Eff_of_env_damage_on_costs_of_TAs']
        idx3 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] / mdf[rowi , idx3:idx3 + 10]
    
    # Cost_per_regional_poverty_policy[region] = Each_region_max_cost_estimate_poverty_PES_with_env_dam_and_reform[region] / Nbr_of_relevant_poverty_policies
        idxlhs = fcol_in_mdf['Cost_per_regional_poverty_policy']
        idx1 = fcol_in_mdf['Each_region_max_cost_estimate_poverty_PES_with_env_dam_and_reform']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Nbr_of_relevant_poverty_policies 
    
    # ExPS_rounds_via_Excel = IF_THEN_ELSE ( zeit >= Round3_start , ExPS_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , ExPS_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , ExPS_R1_via_Excel , ExPS_policy_Min ) ) )
        idxlhs = fcol_in_mdf['ExPS_rounds_via_Excel']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Round3_start  ,  ExPS_R3_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Round2_start  ,  ExPS_R2_via_Excel[0:10]  ,  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  ExPS_R1_via_Excel[0:10]  ,  ExPS_policy_Min  )  )  ) 
    
    # ExPS_policy_with_RW[region] = ExPS_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['ExPS_policy_with_RW']
        idx1 = fcol_in_mdf['ExPS_rounds_via_Excel']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
     
    # ExPS_pol_div_100[region] = MIN ( ExPS_policy_Max , MAX ( ExPS_policy_Min , ExPS_policy_with_RW[region] ) ) / 100
        idxlhs = fcol_in_mdf['ExPS_pol_div_100']
        idx1 = fcol_in_mdf['ExPS_policy_with_RW']
        mdf[rowi, idxlhs:idxlhs + 10] = np.clip(mdf[rowi , idx1:idx1 + 10], ExPS_policy_Min, ExPS_policy_Max) / 100
    
    # Planned_Spending_on_ExPS[region] = Cost_per_regional_poverty_policy[region] * ( ( ExPS_pol_div_100[region] * 100 ) / ExPS_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_ExPS']
        idx1 = fcol_in_mdf['Cost_per_regional_poverty_policy']
        idx2 = fcol_in_mdf['ExPS_pol_div_100']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] *  100  )  /  ExPS_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_Spending_on_FMPLDD[region] = Cost_per_regional_poverty_policy[region] * ( ( FMPLDD_policy[region] / UNIT_conv_to_1_per_yr * 100 ) / FMPLDD_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_FMPLDD']
        idx1 = fcol_in_mdf['Cost_per_regional_poverty_policy']
        idx2 = fcol_in_mdf['FMPLDD_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] /  UNIT_conv_to_1_per_yr  *  100  )  /  FMPLDD_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_Spending_on_FPGDC[region] = Cost_per_regional_poverty_policy[region] * ( ( FPGDC_logically_constrained[region] / UNIT_conv_to_1_per_yr * 100 ) / FPGDC_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_FPGDC']
        idx1 = fcol_in_mdf['Cost_per_regional_poverty_policy']
        idx2 = fcol_in_mdf['FPGDC_logically_constrained']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] /  UNIT_conv_to_1_per_yr  *  100  )  /  FPGDC_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_Spending_on_Lfrac[region] = Cost_per_regional_poverty_policy[region] * ( ( Lfrac_policy[region] * 100 ) / Lfrac_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_Lfrac']
        idx1 = fcol_in_mdf['Cost_per_regional_poverty_policy']
        idx2 = fcol_in_mdf['Lfrac_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] *  100  )  /  Lfrac_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_Spending_on_LPB[region] = Cost_per_regional_poverty_policy[region] * ( ( LPB_policy[region] * 100 ) / LPB_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_LPB']
        idx1 = fcol_in_mdf['Cost_per_regional_poverty_policy']
        idx2 = fcol_in_mdf['LPB_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] *  100  )  /  LPB_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_Spending_on_LPBgrant[region] = Cost_per_regional_poverty_policy[region] * ( ( LPBgrant_policy[region] * 100 ) / LPBgrant_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_LPBgrant']
        idx1 = fcol_in_mdf['Cost_per_regional_poverty_policy']
        idx2 = fcol_in_mdf['LPBgrant_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] *  100  )  /  LPBgrant_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_Spending_on_LPBsplit[region] = Cost_per_regional_poverty_policy[region] * ( ( LPBsplit_policy[region] * 100 ) / LPBsplit_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_LPBsplit']
        idx1 = fcol_in_mdf['Cost_per_regional_poverty_policy']
        idx2 = fcol_in_mdf['LPBsplit_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] *  100  )  /  LPBsplit_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_Spending_on_SSGDR[region] = Cost_per_regional_poverty_policy[region] * ( ( ( SSGDR_policy[region] - SSGDR_policy_Min ) * 1 ) / SSGDR_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_SSGDR']
        idx1 = fcol_in_mdf['Cost_per_regional_poverty_policy']
        idx2 = fcol_in_mdf['SSGDR_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  (  ( mdf[rowi , idx2:idx2 + 10] -  SSGDR_policy_Min  )  *  1  )  /  SSGDR_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_Spending_on_TOW[region] = Cost_per_regional_poverty_policy[region] * ( ( TOW_policy[region] / UNIT_conv_to_1_per_yr * 100 ) / TOW_policy_Max ) * ( 1 - Cutback_fraction_applied[region] )
        idxlhs = fcol_in_mdf['Planned_Spending_on_TOW']
        idx1 = fcol_in_mdf['Cost_per_regional_poverty_policy']
        idx2 = fcol_in_mdf['TOW_policy']
        idx3 = fcol_in_mdf['Cutback_fraction_applied']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  ( mdf[rowi , idx2:idx2 + 10] /  UNIT_conv_to_1_per_yr  *  100  )  /  TOW_policy_Max  )  *  (  1  - mdf[rowi , idx3:idx3 + 10] ) 
    
    # Planned_Spending_on_Poverty[region] = Planned_Spending_on_ExPS[region] + Planned_Spending_on_FMPLDD[region] + Planned_Spending_on_FPGDC[region] + Planned_Spending_on_Lfrac[region] + Planned_Spending_on_LPB[region] + Planned_Spending_on_LPBgrant[region] + Planned_Spending_on_LPBsplit[region] + Planned_Spending_on_SSGDR[region] + Planned_Spending_on_TOW[region]
        idxlhs = fcol_in_mdf['Planned_Spending_on_Poverty']
        idx1 = fcol_in_mdf['Planned_Spending_on_ExPS']
        idx2 = fcol_in_mdf['Planned_Spending_on_FMPLDD']
        idx3 = fcol_in_mdf['Planned_Spending_on_FPGDC']
        idx4 = fcol_in_mdf['Planned_Spending_on_Lfrac']
        idx5 = fcol_in_mdf['Planned_Spending_on_LPB']
        idx6 = fcol_in_mdf['Planned_Spending_on_LPBgrant']
        idx7 = fcol_in_mdf['Planned_Spending_on_LPBsplit']
        idx8 = fcol_in_mdf['Planned_Spending_on_SSGDR']
        idx9 = fcol_in_mdf['Planned_Spending_on_TOW']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] + mdf[rowi , idx4:idx4 + 10] + mdf[rowi , idx5:idx5 + 10] + mdf[rowi , idx6:idx6 + 10] + mdf[rowi , idx7:idx7 + 10] + mdf[rowi , idx8:idx8 + 10] + mdf[rowi , idx9:idx9 + 10]
    
    # Planned_investments_for_all_TAs[region] = Planned_investments_for_energy[region] + Planned_investments_for_food[region] + Planned_investments_for_inequality[region] + Planned_Spending_on_Empowerment[region] + Planned_Spending_on_Poverty[region]
        idxlhs = fcol_in_mdf['Planned_investments_for_all_TAs']
        idx1 = fcol_in_mdf['Planned_investments_for_energy']
        idx2 = fcol_in_mdf['Planned_investments_for_food']
        idx3 = fcol_in_mdf['Planned_investments_for_inequality']
        idx4 = fcol_in_mdf['Planned_Spending_on_Empowerment']
        idx5 = fcol_in_mdf['Planned_Spending_on_Poverty']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] + mdf[rowi , idx4:idx4 + 10] + mdf[rowi , idx5:idx5 + 10]
    
    # Budget_earmarked_for_GL[region] = MIN ( Budget_for_all_TA_per_region_calculated_as_pct_of_GDP[region] , Planned_investments_for_all_TAs[region] )
        idxlhs = fcol_in_mdf['Budget_earmarked_for_GL']
        idx1 = fcol_in_mdf['Budget_for_all_TA_per_region_calculated_as_pct_of_GDP']
        idx2 = fcol_in_mdf['Planned_investments_for_all_TAs']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.minimum  ( mdf[rowi , idx1:idx1 + 10] , mdf[rowi , idx2:idx2 + 10] ) 
    
    # CO2_conc_in_cold_surface_water_in_ppm = CC_in_cold_surface_ymoles_per_litre * Conversion_ymoles_per_kg_to_pCO2_yatm
        idxlhs = fcol_in_mdf['CO2_conc_in_cold_surface_water_in_ppm']
        idx1 = fcol_in_mdf['CC_in_cold_surface_ymoles_per_litre']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Conversion_ymoles_per_kg_to_pCO2_yatm 
    
    # CO2_conc_atm_less_CO2_conc_sea = CO2_concentration_used_after_any_experiments_ppm - CO2_conc_in_cold_surface_water_in_ppm
        idxlhs = fcol_in_mdf['CO2_conc_atm_less_CO2_conc_sea']
        idx1 = fcol_in_mdf['CO2_concentration_used_after_any_experiments_ppm']
        idx2 = fcol_in_mdf['CO2_conc_in_cold_surface_water_in_ppm']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] - mdf[rowi, idx2]
    
    # Guldberg_Waage_air_sea_formulation = ( CO2_conc_atm_less_CO2_conc_sea * Conversion_constant_GtC_to_ppm ) / Time_to_reach_C_equilibrium_between_atmosphere_and_ocean
        idxlhs = fcol_in_mdf['Guldberg_Waage_air_sea_formulation']
        idx1 = fcol_in_mdf['CO2_conc_atm_less_CO2_conc_sea']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] *  Conversion_constant_GtC_to_ppm  )  /  Time_to_reach_C_equilibrium_between_atmosphere_and_ocean 
    
    # C_diffusion_into_ocean_from_atm_net = Guldberg_Waage_air_sea_formulation
        idxlhs = fcol_in_mdf['C_diffusion_into_ocean_from_atm_net']
        idx1 = fcol_in_mdf['Guldberg_Waage_air_sea_formulation']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # C_absorption_by_ocean_from_atm_for_accumulation = C_diffusion_into_ocean_from_atm_net
        idxlhs = fcol_in_mdf['C_absorption_by_ocean_from_atm_for_accumulation']
        idx1 = fcol_in_mdf['C_diffusion_into_ocean_from_atm_net']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # C_in_NF_LB_GtC = NF_Living_biomass_GtBiomass * Carbon_per_biomass
        idxlhs = fcol_in_mdf['C_in_NF_LB_GtC']
        idx1 = fcol_in_mdf['NF_Living_biomass_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Carbon_per_biomass 
    
    # C_in_NF_DeadB_and_soil_GtC = NF_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass * Carbon_per_biomass
        idxlhs = fcol_in_mdf['C_in_NF_DeadB_and_soil_GtC']
        idx1 = fcol_in_mdf['NF_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Carbon_per_biomass 
    
    # C_in_NF_GtC = C_in_NF_LB_GtC + C_in_NF_DeadB_and_soil_GtC + NF_Biomass_locked_in_construction_material_GtBiomass * Carbon_per_biomass
        idxlhs = fcol_in_mdf['C_in_NF_GtC']
        idx1 = fcol_in_mdf['C_in_NF_LB_GtC']
        idx2 = fcol_in_mdf['C_in_NF_DeadB_and_soil_GtC']
        idx3 = fcol_in_mdf['NF_Biomass_locked_in_construction_material_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] *  Carbon_per_biomass 
    
    # C_in_TROP_LB_GtC = TROP_Living_biomass_GtBiomass * Carbon_per_biomass
        idxlhs = fcol_in_mdf['C_in_TROP_LB_GtC']
        idx1 = fcol_in_mdf['TROP_Living_biomass_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Carbon_per_biomass 
    
    # C_in_TROP_DeadB_and_soil_GtC = TROP_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass * Carbon_per_biomass
        idxlhs = fcol_in_mdf['C_in_TROP_DeadB_and_soil_GtC']
        idx1 = fcol_in_mdf['TROP_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Carbon_per_biomass 
    
    # C_in_TROP_GtC = C_in_TROP_LB_GtC + C_in_TROP_DeadB_and_soil_GtC + TROP_Biomass_locked_in_construction_material_GtBiomass * Carbon_per_biomass
        idxlhs = fcol_in_mdf['C_in_TROP_GtC']
        idx1 = fcol_in_mdf['C_in_TROP_LB_GtC']
        idx2 = fcol_in_mdf['C_in_TROP_DeadB_and_soil_GtC']
        idx3 = fcol_in_mdf['TROP_Biomass_locked_in_construction_material_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] *  Carbon_per_biomass 
    
    # C_in_GRASS_LB_GtC = GRASS_Living_biomass_GtBiomass * Carbon_per_biomass
        idxlhs = fcol_in_mdf['C_in_GRASS_LB_GtC']
        idx1 = fcol_in_mdf['GRASS_Living_biomass_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Carbon_per_biomass 
    
    # C_in_GRASS_DeadB_and_soil_GtC = GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass * Carbon_per_biomass
        idxlhs = fcol_in_mdf['C_in_GRASS_DeadB_and_soil_GtC']
        idx1 = fcol_in_mdf['GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Carbon_per_biomass 
    
    # C_in_GRASS_GtC = C_in_GRASS_LB_GtC + C_in_GRASS_DeadB_and_soil_GtC + GRASS_Biomass_locked_in_construction_material_GtBiomass * Carbon_per_biomass
        idxlhs = fcol_in_mdf['C_in_GRASS_GtC']
        idx1 = fcol_in_mdf['C_in_GRASS_LB_GtC']
        idx2 = fcol_in_mdf['C_in_GRASS_DeadB_and_soil_GtC']
        idx3 = fcol_in_mdf['GRASS_Biomass_locked_in_construction_material_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] *  Carbon_per_biomass 
    
    # C_in_TUNDRA_LB_GtC = TUNDRA_Living_biomass * Carbon_per_biomass
        idxlhs = fcol_in_mdf['C_in_TUNDRA_LB_GtC']
        idx1 = fcol_in_mdf['TUNDRA_Living_biomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Carbon_per_biomass 
    
    # C_in_TUNDRA_DeadB_and_soil_GtC = TUNDRA_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass * Carbon_per_biomass
        idxlhs = fcol_in_mdf['C_in_TUNDRA_DeadB_and_soil_GtC']
        idx1 = fcol_in_mdf['TUNDRA_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Carbon_per_biomass 
    
    # C_in_TUNDRA_GtC = C_in_TUNDRA_LB_GtC + C_in_TUNDRA_DeadB_and_soil_GtC + TUNDRA_Biomass_locked_in_construction_material_GtBiomass * Carbon_per_biomass
        idxlhs = fcol_in_mdf['C_in_TUNDRA_GtC']
        idx1 = fcol_in_mdf['C_in_TUNDRA_LB_GtC']
        idx2 = fcol_in_mdf['C_in_TUNDRA_DeadB_and_soil_GtC']
        idx3 = fcol_in_mdf['TUNDRA_Biomass_locked_in_construction_material_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] *  Carbon_per_biomass 
    
    # C_release_from_permafrost_melting_as_CO2_GtC_py = CH4_in_permafrost_area_melted_or_frozen_before_heat_constraint * Melting_restraint_for_permafrost_from_heat_in_atmophere * ( 1 - Fraction_of_C_released_from_permafrost_released_as_CH4_dmnl )
        idxlhs = fcol_in_mdf['C_release_from_permafrost_melting_as_CO2_GtC_py']
        idx1 = fcol_in_mdf['CH4_in_permafrost_area_melted_or_frozen_before_heat_constraint']
        idx2 = fcol_in_mdf['Melting_restraint_for_permafrost_from_heat_in_atmophere']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2] *  (  1  -  Fraction_of_C_released_from_permafrost_released_as_CH4_dmnl  ) 
    
    # TUNDRA_runoff = TUNDRA_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass / TUNDRA_runoff_time
        idxlhs = fcol_in_mdf['TUNDRA_runoff']
        idx1 = fcol_in_mdf['TUNDRA_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  TUNDRA_runoff_time 
    
    # C_runoff_from_biomass_soil = ( TROP_runoff + NF_runoff + GRASS_runoff + TUNDRA_runoff ) * Carbon_per_biomass
        idxlhs = fcol_in_mdf['C_runoff_from_biomass_soil']
        idx1 = fcol_in_mdf['TROP_runoff']
        idx2 = fcol_in_mdf['NF_runoff']
        idx3 = fcol_in_mdf['GRASS_runoff']
        idx4 = fcol_in_mdf['TUNDRA_runoff']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] + mdf[rowi, idx4] )  *  Carbon_per_biomass 
    
    # c_to_acgl[region] = abs ( MIN ( 0 , Cropland_gap[region] ) ) / Time_for_agri_land_to_become_abandoned
        idxlhs = fcol_in_mdf['c_to_acgl']
        idx1 = fcol_in_mdf['Cropland_gap']
        mdf[rowi, idxlhs:idxlhs + 10] =  abs  (  np.minimum  (  0  , mdf[rowi , idx1:idx1 + 10] )  )  /  Time_for_agri_land_to_become_abandoned 
    
    # c_to_pl[region] = MAX ( 0 , Populated_land_gap[region] ) * Fraction_of_cropland_developed_for_urban_land
        idxlhs = fcol_in_mdf['c_to_pl']
        idx1 = fcol_in_mdf['Populated_land_gap']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.maximum  (  0  , mdf[rowi , idx1:idx1 + 10] )  *  Fraction_of_cropland_developed_for_urban_land 
    
    # Private_Investment_in_new_capacity[region] = Available_private_capital_for_investment[region] * Fraction_of_available_capital_to_new_capacity[region]
        idxlhs = fcol_in_mdf['Private_Investment_in_new_capacity']
        idx1 = fcol_in_mdf['Available_private_capital_for_investment']
        idx2 = fcol_in_mdf['Fraction_of_available_capital_to_new_capacity']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # Govt_investment_in_public_capacity[region] = Actual_govt_cash_inflow_seasonally_adjusted[region] - Govt_consumption_ie_purchases[region]
        idxlhs = fcol_in_mdf['Govt_investment_in_public_capacity']
        idx1 = fcol_in_mdf['Actual_govt_cash_inflow_seasonally_adjusted']
        idx2 = fcol_in_mdf['Govt_consumption_ie_purchases']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10]
    
    # GL_spending_going_to_investments[region] = National_income_used_for_GL[region] * GL_investment_fraction
        idxlhs = fcol_in_mdf['GL_spending_going_to_investments']
        idx1 = fcol_in_mdf['National_income_used_for_GL']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  GL_investment_fraction 
    
    # GL_spending_going_to_public_investments[region] = GL_spending_going_to_investments[region] * ( 1 - GL_private_investment_fraction )
        idxlhs = fcol_in_mdf['GL_spending_going_to_public_investments']
        idx1 = fcol_in_mdf['GL_spending_going_to_investments']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  1  -  GL_private_investment_fraction  ) 
    
    # Increase_in_public_capacity[region] = ( Govt_investment_in_public_capacity[region] + Public_money_from_LPB_policy_to_investment[region] + GL_spending_going_to_public_investments[region] ) * ( 1 - Future_leakage[region] )
        idxlhs = fcol_in_mdf['Increase_in_public_capacity']
        idx1 = fcol_in_mdf['Govt_investment_in_public_capacity']
        idx2 = fcol_in_mdf['Public_money_from_LPB_policy_to_investment']
        idx3 = fcol_in_mdf['GL_spending_going_to_public_investments']
        idx4 = fcol_in_mdf['Future_leakage']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] )  *  (  1  - mdf[rowi , idx4:idx4 + 10] ) 
    
    # GL_spending_going_to_private_investments[region] = GL_spending_going_to_investments[region] * GL_private_investment_fraction
        idxlhs = fcol_in_mdf['GL_spending_going_to_private_investments']
        idx1 = fcol_in_mdf['GL_spending_going_to_investments']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  GL_private_investment_fraction 
    
    # Eff_of_env_damage_on_cost_of_new_capacity[region] = np.exp ( Combined_env_damage_indicator * expSoE_of_ed_on_cost_of_new_capacity ) / Actual_eff_of_relative_wealth_on_env_damage[region]
        idxlhs = fcol_in_mdf['Eff_of_env_damage_on_cost_of_new_capacity']
        idx1 = fcol_in_mdf['Combined_env_damage_indicator']
        idx2 = fcol_in_mdf['Actual_eff_of_relative_wealth_on_env_damage']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.exp  ( mdf[rowi , idx1] *  expSoE_of_ed_on_cost_of_new_capacity  )  / mdf[rowi , idx2:idx2 + 10]
    
    # Initiating_capacity_construction[region] = MAX ( ( Private_Investment_in_new_capacity[region] + Increase_in_public_capacity[region] + GL_spending_going_to_private_investments[region] ) * ( 1 - Future_leakage[region] ) / Eff_of_env_damage_on_cost_of_new_capacity[region] , 0 )
        idxlhs = fcol_in_mdf['Initiating_capacity_construction']
        idx1 = fcol_in_mdf['Private_Investment_in_new_capacity']
        idx2 = fcol_in_mdf['Increase_in_public_capacity']
        idx3 = fcol_in_mdf['GL_spending_going_to_private_investments']
        idx4 = fcol_in_mdf['Future_leakage']
        idx5 = fcol_in_mdf['Eff_of_env_damage_on_cost_of_new_capacity']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.maximum  (  ( mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] )  *  (  1  - mdf[rowi , idx4:idx4 + 10] )  / mdf[rowi , idx5:idx5 + 10] ,  0  ) 
    
    # Capacity_renewal_rate[region] = Initiating_capacity_construction[region] / Capacity[region]
        idxlhs = fcol_in_mdf['Capacity_renewal_rate']
        idx1 = fcol_in_mdf['Initiating_capacity_construction']
        idx2 = fcol_in_mdf['Capacity']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
     
    # Global_C_taken_out_of_the_atmo = SUM ( Actual_CO2_taken_directly_out_of_the_atmosphere_ie_direct_air_capture[region!] )
        idxlhs = fcol_in_mdf['Global_C_taken_out_of_the_atmo']
        idx1 = fcol_in_mdf['Actual_CO2_taken_directly_out_of_the_atmosphere_ie_direct_air_capture']
        globsum = 0
        for j in range(0,10):
            globsum = globsum + mdf[rowi, idx1 + j]
        mdf[rowi, idxlhs] = globsum 
    
    # Global_C_taken_directly_out_of_the_atmosphere_ie_direct_air_capture = Global_C_taken_out_of_the_atmo / UNIT_conv_CO2_to_C
        idxlhs = fcol_in_mdf['Global_C_taken_directly_out_of_the_atmosphere_ie_direct_air_capture']
        idx1 = fcol_in_mdf['Global_C_taken_out_of_the_atmo']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  UNIT_conv_CO2_to_C 
    
    # Total_use_of_fossil_fuels_BEING_compensated[region] = Total_use_of_fossil_fuels[region] * Fraction_of_fossil_fuels_compensated_by_CCS[region]
        idxlhs = fcol_in_mdf['Total_use_of_fossil_fuels_BEING_compensated']
        idx1 = fcol_in_mdf['Total_use_of_fossil_fuels']
        idx2 = fcol_in_mdf['Fraction_of_fossil_fuels_compensated_by_CCS']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # Total_CCS_from_fossil_fuels_BEING_compensated = IF_THEN_ELSE ( Total_use_of_fossil_fuels_BEING_compensated == 0 , 0 , toe_to_CO2_a * ( Total_use_of_fossil_fuels_BEING_compensated * UNIT_conv_to_Gtoe ) + toe_to_CO2_b )
        idxlhs = fcol_in_mdf['Total_CCS_from_fossil_fuels_BEING_compensated']
        idx1 = fcol_in_mdf['Total_use_of_fossil_fuels_BEING_compensated']
        idx2 = fcol_in_mdf['Total_use_of_fossil_fuels_BEING_compensated']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  ( mdf[rowi , idx1:idx1 + 10] ==  0  ,  0  ,  toe_to_CO2_a[0:10]  *  ( mdf[rowi , idx2:idx2 + 10] *  UNIT_conv_to_Gtoe  )  +  toe_to_CO2_b[0:10]  ) 
     
    # Global_Total_CCS_from_fossil_fuels_BEING_compensated = SUM ( Total_CCS_from_fossil_fuels_BEING_compensated[region!] )
        idxlhs = fcol_in_mdf['Global_Total_CCS_from_fossil_fuels_BEING_compensated']
        idx1 = fcol_in_mdf['Total_CCS_from_fossil_fuels_BEING_compensated']
        globsum = 0
        for j in range(0,10):
            globsum = globsum + mdf[rowi, idx1 + j]
        mdf[rowi, idxlhs] = globsum 
    
    # Carbon_captured_and_stored_GtC_py = Global_C_taken_directly_out_of_the_atmosphere_ie_direct_air_capture + Global_Total_CCS_from_fossil_fuels_BEING_compensated / UNIT_conv_CO2_to_C
        idxlhs = fcol_in_mdf['Carbon_captured_and_stored_GtC_py']
        idx1 = fcol_in_mdf['Global_C_taken_directly_out_of_the_atmosphere_ie_direct_air_capture']
        idx2 = fcol_in_mdf['Global_Total_CCS_from_fossil_fuels_BEING_compensated']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] /  UNIT_conv_CO2_to_C 
    
    # Carbon_concentration_in_deep_box_GtC_per_G_cubicM = C_in_deep_water_volume_1km_to_bottom_GtC / ( Deep_water_volume_1km_to_4km + Cumulative_ocean_volume_increase_due_to_ice_melting_km3 * UNIT_conversion_km3_to_Gm3 * Frac_vol_deep_ocean_of_total )
        idxlhs = fcol_in_mdf['Carbon_concentration_in_deep_box_GtC_per_G_cubicM']
        idx1 = fcol_in_mdf['C_in_deep_water_volume_1km_to_bottom_GtC']
        idx2 = fcol_in_mdf['Cumulative_ocean_volume_increase_due_to_ice_melting_km3']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  (  Deep_water_volume_1km_to_4km  + mdf[rowi, idx2] *  UNIT_conversion_km3_to_Gm3  *  Frac_vol_deep_ocean_of_total  ) 
    
    # Carbon_concentration_in_intermdiate_box_GtC_per_G_cubicM = C_in_intermediate_upwelling_water_100m_to_1km_GtC / ( Intermediate_upwelling_water_volume_100m_to_1km + Cumulative_ocean_volume_increase_due_to_ice_melting_km3 * UNIT_conversion_km3_to_Gm3 * Frac_vol_ocean_upwelling_of_total )
        idxlhs = fcol_in_mdf['Carbon_concentration_in_intermdiate_box_GtC_per_G_cubicM']
        idx1 = fcol_in_mdf['C_in_intermediate_upwelling_water_100m_to_1km_GtC']
        idx2 = fcol_in_mdf['Cumulative_ocean_volume_increase_due_to_ice_melting_km3']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  (  Intermediate_upwelling_water_volume_100m_to_1km  + mdf[rowi, idx2] *  UNIT_conversion_km3_to_Gm3  *  Frac_vol_ocean_upwelling_of_total  ) 
    
    # Carbon_flow_from_cold_surface_downwelling_Gtc_per_yr = C_in_cold_surface_water_GtC / Time_in_cold
        idxlhs = fcol_in_mdf['Carbon_flow_from_cold_surface_downwelling_Gtc_per_yr']
        idx1 = fcol_in_mdf['C_in_cold_surface_water_GtC']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Time_in_cold 
    
    # Carbon_flow_from_cold_to_deep_GtC_per_yr = C_in_cold_water_trunk_downwelling_GtC / Time_in_trunk
        idxlhs = fcol_in_mdf['Carbon_flow_from_cold_to_deep_GtC_per_yr']
        idx1 = fcol_in_mdf['C_in_cold_water_trunk_downwelling_GtC']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Time_in_trunk 
    
    # Carbon_flow_from_deep = C_in_deep_water_volume_1km_to_bottom_GtC / Time_in_deep
        idxlhs = fcol_in_mdf['Carbon_flow_from_deep']
        idx1 = fcol_in_mdf['C_in_deep_water_volume_1km_to_bottom_GtC']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Time_in_deep 
    
    # Carbon_flow_from_intermediate_to_surface_box_GtC_per_yr = C_in_intermediate_upwelling_water_100m_to_1km_GtC / Time_in_intermediate_yr
        idxlhs = fcol_in_mdf['Carbon_flow_from_intermediate_to_surface_box_GtC_per_yr']
        idx1 = fcol_in_mdf['C_in_intermediate_upwelling_water_100m_to_1km_GtC']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Time_in_intermediate_yr 
    
    # Carbon_flow_from_warm_to_cold_surface_GtC_per_yr = C_in_warm_surface_water_GtC / Time_in_warm
        idxlhs = fcol_in_mdf['Carbon_flow_from_warm_to_cold_surface_GtC_per_yr']
        idx1 = fcol_in_mdf['C_in_warm_surface_water_GtC']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Time_in_warm 
    
    # Carbon_intensity_last_year[region] = SMOOTH3 ( Carbon_intensity[region] , One_year )
        idxin = fcol_in_mdf['Carbon_intensity' ]
        idx2 = fcol_in_mdf['Carbon_intensity_last_year_2']
        idx1 = fcol_in_mdf['Carbon_intensity_last_year_1']
        idxout = fcol_in_mdf['Carbon_intensity_last_year']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( One_year / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( One_year / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( One_year / 3) * dt
    
    # CC_in_deep_box_ymoles_per_litre = Carbon_concentration_in_deep_box_GtC_per_G_cubicM * UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre
        idxlhs = fcol_in_mdf['CC_in_deep_box_ymoles_per_litre']
        idx1 = fcol_in_mdf['Carbon_concentration_in_deep_box_GtC_per_G_cubicM']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre 
    
    # CC_in_deep_box_ymoles_per_litre_dmnl = CC_in_deep_box_ymoles_per_litre * UNIT_conversion_ymoles_p_litre_to_dless
        idxlhs = fcol_in_mdf['CC_in_deep_box_ymoles_per_litre_dmnl']
        idx1 = fcol_in_mdf['CC_in_deep_box_ymoles_per_litre']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  UNIT_conversion_ymoles_p_litre_to_dless 
    
    # CC_in_intermediate_box_ymoles_per_litre = Carbon_concentration_in_intermdiate_box_GtC_per_G_cubicM * UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre
        idxlhs = fcol_in_mdf['CC_in_intermediate_box_ymoles_per_litre']
        idx1 = fcol_in_mdf['Carbon_concentration_in_intermdiate_box_GtC_per_G_cubicM']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre 
    
    # CC_in_intermediate_box_ymoles_per_litre_dmnl = CC_in_intermediate_box_ymoles_per_litre * UNIT_conversion_ymoles_p_litre_to_dless
        idxlhs = fcol_in_mdf['CC_in_intermediate_box_ymoles_per_litre_dmnl']
        idx1 = fcol_in_mdf['CC_in_intermediate_box_ymoles_per_litre']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  UNIT_conversion_ymoles_p_litre_to_dless 
    
    # CH4_conversion_to_CO2_and_H2O = C_in_atmosphere_in_form_of_CH4 / CH4_halflife_in_atmosphere
        idxlhs = fcol_in_mdf['CH4_conversion_to_CO2_and_H2O']
        idx1 = fcol_in_mdf['C_in_atmosphere_in_form_of_CH4']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  CH4_halflife_in_atmosphere 
    
    # CH4_emissions[region] = ( CH4_emi_from_agriculture[region] + CH4_emi_from_energy[region] + CH4_emi_from_waste[region] ) * UNIT_conversion_from_MtCH4_to_GtC
        idxlhs = fcol_in_mdf['CH4_emissions']
        idx1 = fcol_in_mdf['CH4_emi_from_agriculture']
        idx2 = fcol_in_mdf['CH4_emi_from_energy']
        idx3 = fcol_in_mdf['CH4_emi_from_waste']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] )  *  UNIT_conversion_from_MtCH4_to_GtC 
    
    # CH4_Emissions_CO2e[region] = CH4_emissions[region] * Global_Warming_Potential_CH4
        idxlhs = fcol_in_mdf['CH4_Emissions_CO2e']
        idx1 = fcol_in_mdf['CH4_emissions']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  Global_Warming_Potential_CH4 
    
    # CH4_in_the_atmosphere_converted_to_CO2 = CH4_conversion_to_CO2_and_H2O
        idxlhs = fcol_in_mdf['CH4_in_the_atmosphere_converted_to_CO2']
        idx1 = fcol_in_mdf['CH4_conversion_to_CO2_and_H2O']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # RoC_in_delivery_delay_index[region] = SoE_of_Inventory_on_RoC_of_ddx * ( Perceived_relative_inventory[region] / Sufficient_relative_inventory - 1 )
        idxlhs = fcol_in_mdf['RoC_in_delivery_delay_index']
        idx1 = fcol_in_mdf['Perceived_relative_inventory']
        mdf[rowi, idxlhs:idxlhs + 10] =  SoE_of_Inventory_on_RoC_of_ddx  *  ( mdf[rowi , idx1:idx1 + 10] /  Sufficient_relative_inventory  -  1  ) 
    
    # Change_in_delivery_delay_index[region] = Delivery_delay_index[region] * RoC_in_delivery_delay_index[region]
        idxlhs = fcol_in_mdf['Change_in_delivery_delay_index']
        idx1 = fcol_in_mdf['Delivery_delay_index']
        idx2 = fcol_in_mdf['RoC_in_delivery_delay_index']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # Eff_of_labour_imbalance_on_FOLP[region] = So_Eff_of_labour_imbalance_on_FOLP[region] * ( Theoretical_full_time_jobs_at_current_CLR[region] / Employed[region] - 1 )
        idxlhs = fcol_in_mdf['Eff_of_labour_imbalance_on_FOLP']
        idx1 = fcol_in_mdf['Theoretical_full_time_jobs_at_current_CLR']
        idx2 = fcol_in_mdf['Employed']
        mdf[rowi, idxlhs:idxlhs + 10] =  So_Eff_of_labour_imbalance_on_FOLP[0:10]  *  ( mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10] -  1  ) 
    
    # RoC_in_FOPOLM[region] = Eff_of_labour_imbalance_on_FOLP[region]
        idxlhs = fcol_in_mdf['RoC_in_FOPOLM']
        idx1 = fcol_in_mdf['Eff_of_labour_imbalance_on_FOLP']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10]
    
    # Change_in_Fraction_of_people_outside_of_labour_market[region] = ( Max_FOPOLM - Fraction_of_people_outside_of_labour_market_FOPOLM[region] ) * RoC_in_FOPOLM[region]
        idxlhs = fcol_in_mdf['Change_in_Fraction_of_people_outside_of_labour_market']
        idx1 = fcol_in_mdf['Fraction_of_people_outside_of_labour_market_FOPOLM']
        idx2 = fcol_in_mdf['RoC_in_FOPOLM']
        mdf[rowi, idxlhs:idxlhs + 10] =  (  Max_FOPOLM  - mdf[rowi , idx1:idx1 + 10] )  * mdf[rowi , idx2:idx2 + 10]
    
    # Change_in_future_footprint_pp = IF_THEN_ELSE ( zeit >= 2020 , Non_energy_footprint_pp_future / Half_life_of_tech_progress_in_non_energy_footprint , 0 )
        idxlhs = fcol_in_mdf['Change_in_future_footprint_pp']
        idx1 = fcol_in_mdf['Non_energy_footprint_pp_future']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  (  zeit  >=  2020  , mdf[rowi, idx1] /  Half_life_of_tech_progress_in_non_energy_footprint  ,  0  ) 
    
    # GenEq_cn = GenEq_cn_a * ( GDPpp_USED[cn] / UNIT_conv_to_make_base_dmnless ) ^ GenEq_cn_b
        idxlhs = fcol_in_mdf['GenEq_cn']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs] =  GenEq_cn_a  *  ( mdf[rowi, idx1 + 2] /  UNIT_conv_to_make_base_dmnless  )  **  GenEq_cn_b 
    
    # GenEq_ec = GenEq_ec_a * LN ( GDPpp_USED[ec] / UNIT_conv_to_make_base_dmnless ) + GenEq_ec_b
        idxlhs = fcol_in_mdf['GenEq_ec']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs] =  GenEq_ec_a  *  np.log  ( mdf[rowi, idx1 + 7] /  UNIT_conv_to_make_base_dmnless  )  +  GenEq_ec_b 
    
    # GenEq_me = GenEq_me_a * ( GDPpp_USED[me] / UNIT_conv_to_make_base_dmnless ) + GenEq_me_b
        idxlhs = fcol_in_mdf['GenEq_me']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs] =  GenEq_me_a  *  ( mdf[rowi, idx1 + 3] /  UNIT_conv_to_make_base_dmnless  )  +  GenEq_me_b 
    
    # GenEq_sa = GenEq_sa_la_af_a * LN ( GDPpp_USED[sa] / UNIT_conv_to_make_base_dmnless ) + GenEq_sa_la_af_b
        idxlhs = fcol_in_mdf['GenEq_sa']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs] =  GenEq_sa_la_af_a  *  np.log  ( mdf[rowi, idx1 + 4] /  UNIT_conv_to_make_base_dmnless  )  +  GenEq_sa_la_af_b 
    
    # GenEq_la = GenEq_sa_la_af_a * LN ( GDPpp_USED[la] / UNIT_conv_to_make_base_dmnless ) + GenEq_sa_la_af_b
        idxlhs = fcol_in_mdf['GenEq_la']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs] =  GenEq_sa_la_af_a  *  np.log  ( mdf[rowi, idx1 + 5] /  UNIT_conv_to_make_base_dmnless  )  +  GenEq_sa_la_af_b 
    
    # GenEq_af = GenEq_sa_la_af_a * LN ( GDPpp_USED[af] / UNIT_conv_to_make_base_dmnless ) + GenEq_sa_la_af_b
        idxlhs = fcol_in_mdf['GenEq_af']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs] =  GenEq_sa_la_af_a  *  np.log  ( mdf[rowi, idx1 + 1] /  UNIT_conv_to_make_base_dmnless  )  +  GenEq_sa_la_af_b 
    
    # GenEq_se_eu_pa_us[region] = GenEq_se_eu_pa_us_a * ( GDPpp_USED[region] / UNIT_conv_to_make_base_dmnless ) + GenEq_se_eu_pa_us_b
        idxlhs = fcol_in_mdf['GenEq_se_eu_pa_us']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  GenEq_se_eu_pa_us_a  *  ( mdf[rowi , idx1:idx1 + 10] /  UNIT_conv_to_make_base_dmnless  )  +  GenEq_se_eu_pa_us_b 
    
    # GenEq_before_female_leadership_spending = IF_THEN_ELSE ( j==2 , GenEq_cn , IF_THEN_ELSE ( j==7 , GenEq_ec , IF_THEN_ELSE ( j==3 , GenEq_me , IF_THEN_ELSE ( j==4 , GenEq_sa , IF_THEN_ELSE ( j==5 , GenEq_la , IF_THEN_ELSE ( j==1 , GenEq_af , GenEq_se_eu_pa_us ) ) ) ) ) )
        idxlhs = fcol_in_mdf['GenEq_before_female_leadership_spending']
        idx1 = fcol_in_mdf['GenEq_cn']
        idx2 = fcol_in_mdf['GenEq_ec']
        idx3 = fcol_in_mdf['GenEq_me']
        idx4 = fcol_in_mdf['GenEq_sa']
        idx5 = fcol_in_mdf['GenEq_la']
        idx6 = fcol_in_mdf['GenEq_af']
        idx7 = fcol_in_mdf['GenEq_se_eu_pa_us']
        for j in range(0,10):
            mdf[rowi, idxlhs + j] =  IF_THEN_ELSE  (  j==2  , mdf[rowi , idx1] ,  IF_THEN_ELSE  (  j==7  , mdf[rowi , idx2] ,  IF_THEN_ELSE  (  j==3  , mdf[rowi , idx3] ,  IF_THEN_ELSE  (  j==4  , mdf[rowi , idx4] ,  IF_THEN_ELSE  (  j==5  , mdf[rowi , idx5] ,  IF_THEN_ELSE  (  j==1  , mdf[rowi , idx6] , mdf[rowi , idx7 + j] )  )  )  )  )  ) 
    
    # Effect_of_Female_Leadership_on_gender_equality[region] = 1 + Female_leadership_spending[region] / GDP_USED[region]
        idxlhs = fcol_in_mdf['Effect_of_Female_Leadership_on_gender_equality']
        idx1 = fcol_in_mdf['Female_leadership_spending']
        idx2 = fcol_in_mdf['GDP_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  + mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # GenEq[region] = GenEq_before_female_leadership_spending[region] * Effect_of_Female_Leadership_on_gender_equality[region]
        idxlhs = fcol_in_mdf['GenEq']
        idx1 = fcol_in_mdf['GenEq_before_female_leadership_spending']
        idx2 = fcol_in_mdf['Effect_of_Female_Leadership_on_gender_equality']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # Cutoff_GE_change[region] = WITH LOOKUP ( GenderEquality[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 1 ) , ( 0.1 , 0.98 ) , ( 0.2 , 0.9 ) , ( 0.3 , 0.72 ) , ( 0.4 , 0.43 ) , ( 0.55 , 0.0001 ) ) )
        tabidx = ftab_in_d_table['Cutoff_GE_change'] # fetch the correct table
        idx2 = fcol_in_mdf['Cutoff_GE_change'] # get the location of the lhs in mdf
        idx3 = fcol_in_mdf['GenderEquality']
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:,0], look[:, 1])
    
    # Change_in_GE[region] = ( GenEq[region] - GenderEquality[region] ) / Time_to_change_GE[region] * Cutoff_GE_change[region]
        idxlhs = fcol_in_mdf['Change_in_GE']
        idx1 = fcol_in_mdf['GenEq']
        idx2 = fcol_in_mdf['GenderEquality']
        idx3 = fcol_in_mdf['Cutoff_GE_change']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10] )  /  Time_to_change_GE  * mdf[rowi, idx3:idx3 + 10]
    
    # Change_in_Owner_power[region] = Strength_of_owner_reaction_to_worker_resistance * Worker_resistance_or_resignation[region]
        idxlhs = fcol_in_mdf['Change_in_Owner_power']
        idx1 = fcol_in_mdf['Worker_resistance_or_resignation']
        mdf[rowi, idxlhs:idxlhs + 10] =  Strength_of_owner_reaction_to_worker_resistance  * mdf[rowi , idx1:idx1 + 10]
    
    # RoC_of_people_considering_entering_the_labor_pool[region] = Slope_of_RoC_of_people_considering_entering_the_labor_pool * ( Unemployment_ratio[region] - 1 )
        idxlhs = fcol_in_mdf['RoC_of_people_considering_entering_the_labor_pool']
        idx1 = fcol_in_mdf['Unemployment_ratio']
        mdf[rowi, idxlhs:idxlhs + 10] =  Slope_of_RoC_of_people_considering_entering_the_labor_pool  *  ( mdf[rowi , idx1:idx1 + 10] -  1  ) 
    
    # Change_in_people_considering_entering_the_pool[region] = People_considering_entering_the_pool[region] * RoC_of_people_considering_entering_the_labor_pool[region]
        idxlhs = fcol_in_mdf['Change_in_people_considering_entering_the_pool']
        idx1 = fcol_in_mdf['People_considering_entering_the_pool']
        idx2 = fcol_in_mdf['RoC_of_people_considering_entering_the_labor_pool']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # RoC_of_people_considering_leaving_the_labor_pool[region] = Slope_of_RoC_of_people_considering_leaving_the_labor_pool * ( Unemployment_ratio[region] - Scaling_strength_of_RoC_from_unemployed_to_pool[region] )
        idxlhs = fcol_in_mdf['RoC_of_people_considering_leaving_the_labor_pool']
        idx1 = fcol_in_mdf['Unemployment_ratio']
        mdf[rowi, idxlhs:idxlhs + 10] =  Slope_of_RoC_of_people_considering_leaving_the_labor_pool  *  ( mdf[rowi , idx1:idx1 + 10] -  Scaling_strength_of_RoC_from_unemployed_to_pool[0:10]  ) 
    
    # Change_in_people_considering_leaving_the_pool[region] = People_considering_leaving_the_pool[region] * RoC_of_people_considering_leaving_the_labor_pool[region]
        idxlhs = fcol_in_mdf['Change_in_people_considering_leaving_the_pool']
        idx1 = fcol_in_mdf['People_considering_leaving_the_pool']
        idx2 = fcol_in_mdf['RoC_of_people_considering_leaving_the_labor_pool']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # Public_capacity_N_yrs_ago[region] = SMOOTH3 ( Public_capacity[region] , the_N_for_PC_N_yrs_ago )
        idxin = fcol_in_mdf['Public_capacity' ]
        idx2 = fcol_in_mdf['Public_capacity_N_yrs_ago_2']
        idx1 = fcol_in_mdf['Public_capacity_N_yrs_ago_1']
        idxout = fcol_in_mdf['Public_capacity_N_yrs_ago']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( the_N_for_PC_N_yrs_ago / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( the_N_for_PC_N_yrs_ago / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( the_N_for_PC_N_yrs_ago / 3) * dt
    
    # RoC_in_in_RoTA_from_public_capacity[region] = ( SoE_of_PC_on_RoC_in_change_in_rate_of_tech_advance[region] / 1000 ) * ( 1 + Public_capacity[region] / Public_capacity_N_yrs_ago[region] - 1 )
        idxlhs = fcol_in_mdf['RoC_in_in_RoTA_from_public_capacity']
        idx1 = fcol_in_mdf['Public_capacity']
        idx2 = fcol_in_mdf['Public_capacity_N_yrs_ago']
        mdf[rowi, idxlhs:idxlhs + 10] =  (  SoE_of_PC_on_RoC_in_change_in_rate_of_tech_advance[0:10]  /  1000  )  *  (  1  + mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10] -  1  ) 
    
    # Size_of_agri_sector[region] = ( Size_of_agri_sector_a + Size_of_agri_sector_b * np.exp ( - 1 * ( GDPpp_USED[region] / Size_of_agri_sector_c ) ) ) / 100
        idxlhs = fcol_in_mdf['Size_of_agri_sector']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  (  Size_of_agri_sector_a  +  Size_of_agri_sector_b  *  np.exp  (  -  1  *  ( mdf[rowi , idx1:idx1 + 10] /  Size_of_agri_sector_c  )  )  )  /  100 
    
    # Size_of_tertiary_sector[region] = ( Size_of_tertiary_sector_lim - Size_of_tertiary_sector_a * np.exp ( - 1 * ( ( GDPpp_USED[region] ) / Size_of_tertiary_sector_c ) ) ) / 100
        idxlhs = fcol_in_mdf['Size_of_tertiary_sector']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  (  Size_of_tertiary_sector_lim  -  Size_of_tertiary_sector_a  *  np.exp  (  -  1  *  (  ( mdf[rowi , idx1:idx1 + 10] )  /  Size_of_tertiary_sector_c  )  )  )  /  100 
    
    # Size_of_industrial_sector[region] = 1 - Size_of_agri_sector[region] - Size_of_tertiary_sector[region]
        idxlhs = fcol_in_mdf['Size_of_industrial_sector']
        idx1 = fcol_in_mdf['Size_of_agri_sector']
        idx2 = fcol_in_mdf['Size_of_tertiary_sector']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  - mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10]
    
    # RoC_in_RoTA_in_TFP_from_industrialization[region] = SoE_of_industrialization_on_RoC_in_TFP * ( 1 + Size_of_industrial_sector[region] - 1 )
        idxlhs = fcol_in_mdf['RoC_in_RoTA_in_TFP_from_industrialization']
        idx1 = fcol_in_mdf['Size_of_industrial_sector']
        mdf[rowi, idxlhs:idxlhs + 10] =  SoE_of_industrialization_on_RoC_in_TFP  *  (  1  + mdf[rowi , idx1:idx1 + 10] -  1  ) 
    
    # RoC_in_RoTA_in_TFP_from_tertiary_sector[region] = SoE_of_tertiary_sector_on_RoC_in_TFP[region] * ( 1 + Size_of_tertiary_sector[region] - 1 )
        idxlhs = fcol_in_mdf['RoC_in_RoTA_in_TFP_from_tertiary_sector']
        idx1 = fcol_in_mdf['Size_of_tertiary_sector']
        mdf[rowi, idxlhs:idxlhs + 10] =  SoE_of_tertiary_sector_on_RoC_in_TFP[0:10]  *  (  1  + mdf[rowi , idx1:idx1 + 10] -  1  ) 
    
    # Change_in_RoTA[region] = Rate_of_tech_advance_RoTA_in_TFP[region] * ( RoC_in_in_RoTA_from_public_capacity[region] + RoC_in_RoTA_in_TFP_from_industrialization[region] + RoC_in_RoTA_in_TFP_from_tertiary_sector[region] )
        idxlhs = fcol_in_mdf['Change_in_RoTA']
        idx1 = fcol_in_mdf['Rate_of_tech_advance_RoTA_in_TFP']
        idx2 = fcol_in_mdf['RoC_in_in_RoTA_from_public_capacity']
        idx3 = fcol_in_mdf['RoC_in_RoTA_in_TFP_from_industrialization']
        idx4 = fcol_in_mdf['RoC_in_RoTA_in_TFP_from_tertiary_sector']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  ( mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] + mdf[rowi , idx4:idx4 + 10] ) 
    
    # Perceived_inflation[region] = SMOOTHI ( Inflation_rate_used_only_for_interest_rate[region] , Inflation_perception_time[region] , Perceived_inflation_in_1980[region] )
        idx1 = fcol_in_mdf['Perceived_inflation']
        idx2 = fcol_in_mdf['Inflation_rate_used_only_for_interest_rate']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi - 1, idx1:idx1 + 10]) / Inflation_perception_time[0:10] * dt
    
    # Eff_of_inflation_on_Indicated_signal_rate[region] = 1 + SoE_of_inflation_rate_on_indicated_signal_rate * ( Perceived_inflation[region] / Inflation_target[region] - 1 )
        idxlhs = fcol_in_mdf['Eff_of_inflation_on_Indicated_signal_rate']
        idx1 = fcol_in_mdf['Perceived_inflation']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  +  SoE_of_inflation_rate_on_indicated_signal_rate  *  ( mdf[rowi , idx1:idx1 + 10] /  Inflation_target[0:10]  -  1  ) 
    
    # Perceived_unemployment_rate[region] = SMOOTH ( Unemployment_rate[region] , Unemployment_perception_time )
        idx1 = fcol_in_mdf['Perceived_unemployment_rate']
        idx2 = fcol_in_mdf['Unemployment_rate']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1+10] + ( mdf[rowi-1 , idx2:idx2 + 10] - mdf[rowi -1 , idx1:idx1 + 10]) / Unemployment_perception_time * dt
    
    # Long_term_unemployment_rate[region] = SMOOTH ( Unemployment_rate[region] , Time_to_establish_Long_term_unemployment_rate )
        idx1 = fcol_in_mdf['Long_term_unemployment_rate']
        idx2 = fcol_in_mdf['Unemployment_rate']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1+10] + ( mdf[rowi-1 , idx2:idx2 + 10] - mdf[rowi -1 , idx1:idx1 + 10]) / Time_to_establish_Long_term_unemployment_rate * dt
    
    # Unemployment_rate_used = IF_THEN_ELSE ( SWITCH_unemp_target_or_long_term == 1 , Unemployment_target_for_interest , Long_term_unemployment_rate )
        idxlhs = fcol_in_mdf['Unemployment_rate_used']
        idx1 = fcol_in_mdf['Long_term_unemployment_rate']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  SWITCH_unemp_target_or_long_term[0:10]  ==  1  ,  Unemployment_target_for_interest[0:10]  , mdf[rowi , idx1:idx1 + 10] ) 
    
    # Eff_of_unemployment_on_Indicated_signal_rate[region] = SoE_of_unemployment_rate_on_indicated_signal_rate * ( Perceived_unemployment_rate[region] / Unemployment_rate_used[region] - 1 )
        idxlhs = fcol_in_mdf['Eff_of_unemployment_on_Indicated_signal_rate']
        idx1 = fcol_in_mdf['Perceived_unemployment_rate']
        idx2 = fcol_in_mdf['Unemployment_rate_used']
        mdf[rowi, idxlhs:idxlhs + 10] =  SoE_of_unemployment_rate_on_indicated_signal_rate  *  ( mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10] -  1  ) 
    
    # Indicated_signal_rate[region] = Normal_signal_rate[region] * ( Eff_of_inflation_on_Indicated_signal_rate[region] + Eff_of_unemployment_on_Indicated_signal_rate[region] )
        idxlhs = fcol_in_mdf['Indicated_signal_rate']
        idx1 = fcol_in_mdf['Eff_of_inflation_on_Indicated_signal_rate']
        idx2 = fcol_in_mdf['Eff_of_unemployment_on_Indicated_signal_rate']
        mdf[rowi, idxlhs:idxlhs + 10] =  Normal_signal_rate[0:10]  *  ( mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] ) 
    
    # Change_in_signal_rate[region] = ( Indicated_signal_rate[region] - Central_bank_signal_rate[region] ) / Signal_rate_adjustment_time
        idxlhs = fcol_in_mdf['Change_in_signal_rate']
        idx1 = fcol_in_mdf['Indicated_signal_rate']
        idx2 = fcol_in_mdf['Central_bank_signal_rate']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10] )  /  Signal_rate_adjustment_time 
    
    # Ratio_of_actual_public_spending_vs_reference[region] = Public_spending_as_share_of_GDP[region] / Reference_public_spending_fraction
        idxlhs = fcol_in_mdf['Ratio_of_actual_public_spending_vs_reference']
        idx1 = fcol_in_mdf['Public_spending_as_share_of_GDP']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Reference_public_spending_fraction 
    
    # Public_spending_effect_on_social_trust[region] = WITH LOOKUP ( Ratio_of_actual_public_spending_vs_reference[region] , ( [ ( 0 , 0 ) - ( 0.601626 , 0.822581 ) ] , ( 0 , 0.8 ) , ( 0.25 , 0.82 ) , ( 0.5 , 0.87 ) , ( 0.75 , 0.93 ) , ( 1 , 1 ) , ( 1.25 , 1.07 ) , ( 1.5 , 1.13 ) , ( 1.75 , 1.18 ) , ( 2 , 1.2 ) ) )
        tabidx = ftab_in_d_table['Public_spending_effect_on_social_trust'] # fetch the correct table
        idx2 = fcol_in_mdf['Public_spending_effect_on_social_trust'] # get the location of the lhs in mdf
        idx3 = fcol_in_mdf['Ratio_of_actual_public_spending_vs_reference']
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:,0], look[:, 1])
    
    # Ratio_of_actual_inequality_to_norm[region] = Actual_inequality_index_higher_is_more_unequal_N_years_ago[region] / Inequality_considered_normal_in_1980[region]
        idxlhs = fcol_in_mdf['Ratio_of_actual_inequality_to_norm']
        idx1 = fcol_in_mdf['Actual_inequality_index_higher_is_more_unequal_N_years_ago']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Inequality_considered_normal_in_1980 
    
    # Inequality_effect_on_social_trust[region] = WITH LOOKUP ( Ratio_of_actual_inequality_to_norm[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 2 ) , ( 0.2 , 1.975 ) , ( 0.4 , 1.913 ) , ( 0.6 , 1.767 ) , ( 0.8 , 1.465 ) , ( 1 , 1 ) , ( 1.2 , 0.5352 ) , ( 1.4 , 0.2331 ) , ( 1.6 , 0.08682 ) , ( 1.8 , 0.02526 ) , ( 2 , 0 ) ) )
        tabidx = ftab_in_d_table['Inequality_effect_on_social_trust'] # fetch the correct table
        idx2 = fcol_in_mdf['Inequality_effect_on_social_trust'] # get the location of the lhs in mdf
        idx3 = fcol_in_mdf['Ratio_of_actual_inequality_to_norm']
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:,0], look[:, 1])
    
    # Multplier_from_gender_inequality_on_indicated_social_trust[region] = 1 + ( SDG_5_Score[region] - 0.5 ) * Strength_of_Effect_of_gender_inequality_on_social_trust
        idxlhs = fcol_in_mdf['Multplier_from_gender_inequality_on_indicated_social_trust']
        idx1 = fcol_in_mdf['SDG_5_Score']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  +  ( mdf[rowi , idx1:idx1 + 10] -  0.5  )  *  Strength_of_Effect_of_gender_inequality_on_social_trust 
    
    # Smoothed_Multplier_from_gender_inequality_on_indicated_social_trust[region] = SMOOTH3 ( Multplier_from_gender_inequality_on_indicated_social_trust[region] , Time_to_smooth_Multplier_from_empowerment_on_indicated_social_trust )
        idxin = fcol_in_mdf['Multplier_from_gender_inequality_on_indicated_social_trust' ]
        idx2 = fcol_in_mdf['Smoothed_Multplier_from_gender_inequality_on_indicated_social_trust_2']
        idx1 = fcol_in_mdf['Smoothed_Multplier_from_gender_inequality_on_indicated_social_trust_1']
        idxout = fcol_in_mdf['Smoothed_Multplier_from_gender_inequality_on_indicated_social_trust']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( Time_to_smooth_Multplier_from_empowerment_on_indicated_social_trust / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( Time_to_smooth_Multplier_from_empowerment_on_indicated_social_trust / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( Time_to_smooth_Multplier_from_empowerment_on_indicated_social_trust / 3) * dt
    
    # Multplier_from_schooling_on_indicated_social_trust[region] = 1 + ( SDG4_Score[region] - 0.5 ) * Strength_of_Effect_of_schooling_on_social_trust
        idxlhs = fcol_in_mdf['Multplier_from_schooling_on_indicated_social_trust']
        idx1 = fcol_in_mdf['SDG4_Score']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  +  ( mdf[rowi , idx1:idx1 + 10] -  0.5  )  *  Strength_of_Effect_of_schooling_on_social_trust 
    
    # Smoothed_Multplier_from_schooling_on_indicated_social_trust[region] = SMOOTH3 ( Multplier_from_schooling_on_indicated_social_trust[region] , Time_to_smooth_Multplier_from_empowerment_on_indicated_social_trust )
        idxin = fcol_in_mdf['Multplier_from_schooling_on_indicated_social_trust' ]
        idx2 = fcol_in_mdf['Smoothed_Multplier_from_schooling_on_indicated_social_trust_2']
        idx1 = fcol_in_mdf['Smoothed_Multplier_from_schooling_on_indicated_social_trust_1']
        idxout = fcol_in_mdf['Smoothed_Multplier_from_schooling_on_indicated_social_trust']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( Time_to_smooth_Multplier_from_empowerment_on_indicated_social_trust / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( Time_to_smooth_Multplier_from_empowerment_on_indicated_social_trust / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( Time_to_smooth_Multplier_from_empowerment_on_indicated_social_trust / 3) * dt
    
    # Indicated_social_trust[region] = Public_spending_effect_on_social_trust[region] * Inequality_effect_on_social_trust[region] / Scaled_and_smoothed_Effect_of_poverty_on_social_tension_and_trust[region] * Smoothed_Multplier_from_gender_inequality_on_indicated_social_trust[region] * Smoothed_Multplier_from_schooling_on_indicated_social_trust[region]
        idxlhs = fcol_in_mdf['Indicated_social_trust']
        idx1 = fcol_in_mdf['Public_spending_effect_on_social_trust']
        idx2 = fcol_in_mdf['Inequality_effect_on_social_trust']
        idx3 = fcol_in_mdf['Scaled_and_smoothed_Effect_of_poverty_on_social_tension_and_trust']
        idx4 = fcol_in_mdf['Smoothed_Multplier_from_gender_inequality_on_indicated_social_trust']
        idx5 = fcol_in_mdf['Smoothed_Multplier_from_schooling_on_indicated_social_trust']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi, idx1:idx1 + 10] * mdf[rowi, idx2:idx2 + 10] / mdf[rowi , idx3:idx3 + 10] * mdf[rowi , idx4:idx4 + 10] * mdf[rowi , idx5:idx5 + 10]
    
    # Change_in_social_trust[region] = ( Indicated_social_trust[region] - Social_trust[region] ) / Time_to_change_social_trust
        idxlhs = fcol_in_mdf['Change_in_social_trust']
        idx1 = fcol_in_mdf['Indicated_social_trust']
        idx2 = fcol_in_mdf['Social_trust']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10] )  /  Time_to_change_social_trust 
    
    # Change_in_TFP[region] = Total_factor_productivity_TFP_before_env_damage[region] * Rate_of_tech_advance_RoTA_in_TFP[region]
        idxlhs = fcol_in_mdf['Change_in_TFP']
        idx1 = fcol_in_mdf['Total_factor_productivity_TFP_before_env_damage']
        idx2 = fcol_in_mdf['Rate_of_tech_advance_RoTA_in_TFP']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # Future_Annual_reduction_in_UAC = IF_THEN_ELSE ( zeit >= 2020 , Annual_reduction_in_UAC / 100 , 0 )
        idxlhs = fcol_in_mdf['Future_Annual_reduction_in_UAC']
        idx1 = fcol_in_mdf['Annual_reduction_in_UAC']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  (  zeit  >=  2020  , mdf[rowi, idx1] /  100  ,  0  ) 
    
    # Change_in_UACre = Future_Annual_reduction_in_UAC * UAC_reduction_effort
        idxlhs = fcol_in_mdf['Change_in_UACre']
        idx1 = fcol_in_mdf['Future_Annual_reduction_in_UAC']
        idx2 = fcol_in_mdf['UAC_reduction_effort']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2]
    
    # Eff_of_scenario_on_strength_of_worker_reaction_to_owner_power[region] = 1 + WReaction_policy[region]
        idxlhs = fcol_in_mdf['Eff_of_scenario_on_strength_of_worker_reaction_to_owner_power']
        idx1 = fcol_in_mdf['WReaction_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  + mdf[rowi , idx1:idx1 + 10]
    
    # Inequality_effect_on_food_TA[region] = 1 + ( Actual_inequality_index_higher_is_more_unequal[region] - 1 ) * Strength_of_inequality_effect_on_food_TA
        idxlhs = fcol_in_mdf['Inequality_effect_on_food_TA']
        idx1 = fcol_in_mdf['Actual_inequality_index_higher_is_more_unequal']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  +  ( mdf[rowi , idx1:idx1 + 10] -  1  )  *  Strength_of_inequality_effect_on_food_TA 
    
    # Reform_willingness_with_inequality[region] = ( Smoothed_Reform_willingness[region] / Inequality_effect_on_food_TA[region] )
        idxlhs = fcol_in_mdf['Reform_willingness_with_inequality']
        idx1 = fcol_in_mdf['Smoothed_Reform_willingness']
        idx2 = fcol_in_mdf['Inequality_effect_on_food_TA']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10] ) 
    
    # Effect_of_TAs_on_inequality[region] = Reform_willingness_with_inequality[region] / Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['Effect_of_TAs_on_inequality']
        idx1 = fcol_in_mdf['Reform_willingness_with_inequality']
        idx2 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # Scaled_Effect_of_TAs_on_inequality[region] = ( Effect_of_TAs_on_inequality[region] - 1 ) * Strength_of_Effect_of_TAs_on_inequality
        idxlhs = fcol_in_mdf['Scaled_Effect_of_TAs_on_inequality']
        idx1 = fcol_in_mdf['Effect_of_TAs_on_inequality']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] -  1  )  *  Strength_of_Effect_of_TAs_on_inequality 
    
    # Strength_of_worker_reaction_to_owner_power[region] = Strength_of_worker_reaction_to_owner_power_normal * Eff_of_scenario_on_strength_of_worker_reaction_to_owner_power[region] + Scaled_Effect_of_TAs_on_inequality[region]
        idxlhs = fcol_in_mdf['Strength_of_worker_reaction_to_owner_power']
        idx1 = fcol_in_mdf['Eff_of_scenario_on_strength_of_worker_reaction_to_owner_power']
        idx2 = fcol_in_mdf['Scaled_Effect_of_TAs_on_inequality']
        mdf[rowi, idxlhs:idxlhs + 10] =  Strength_of_worker_reaction_to_owner_power_normal  * mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10]
    
    # Change_in_worker_resistance[region] = Owner_power_or_weakness[region] * Strength_of_worker_reaction_to_owner_power[region]
        idxlhs = fcol_in_mdf['Change_in_worker_resistance']
        idx1 = fcol_in_mdf['Owner_power_or_weakness']
        idx2 = fcol_in_mdf['Strength_of_worker_reaction_to_owner_power']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # GRASS_Biomass_in_construction_material_being_burnt = GRASS_Biomass_locked_in_construction_material_GtBiomass / GRASS_Avg_life_of_building_yr * GRASS_Fraction_of_construction_waste_burned_0_to_1
        idxlhs = fcol_in_mdf['GRASS_Biomass_in_construction_material_being_burnt']
        idx1 = fcol_in_mdf['GRASS_Biomass_locked_in_construction_material_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  GRASS_Avg_life_of_building_yr  *  GRASS_Fraction_of_construction_waste_burned_0_to_1 
    
    # GRASS_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting = ( GRASS_being_deforested_Mkm2_py + GRASS_burning_Mkm2_py + GRASS_being_harvested_Mkm2_py ) * GRASS_living_biomass_densitiy_tBiomass_pr_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
        idxlhs = fcol_in_mdf['GRASS_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting']
        idx1 = fcol_in_mdf['GRASS_being_deforested_Mkm2_py']
        idx2 = fcol_in_mdf['GRASS_burning_Mkm2_py']
        idx3 = fcol_in_mdf['GRASS_being_harvested_Mkm2_py']
        idx4 = fcol_in_mdf['GRASS_living_biomass_densitiy_tBiomass_pr_km2']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] )  * mdf[rowi, idx4] /  UNIT_conversion_GtBiomass_py_to_Mkm2_py 
    
    # CO2_flow_from_GRASS_to_atmosphere_GtC_py = ( GRASS_Biomass_in_construction_material_being_burnt + GRASS_Dead_biomass_decomposing + GRASS_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting + GRASS_DeadB_SOM_being_lost_due_to_deforestation + GRASS_DeadB_SOM_being_lost_due_to_energy_harvesting + GRASS_soil_degradation_from_forest_fires + GRASS_runoff ) * Carbon_per_biomass
        idxlhs = fcol_in_mdf['CO2_flow_from_GRASS_to_atmosphere_GtC_py']
        idx1 = fcol_in_mdf['GRASS_Biomass_in_construction_material_being_burnt']
        idx2 = fcol_in_mdf['GRASS_Dead_biomass_decomposing']
        idx3 = fcol_in_mdf['GRASS_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting']
        idx4 = fcol_in_mdf['GRASS_DeadB_SOM_being_lost_due_to_deforestation']
        idx5 = fcol_in_mdf['GRASS_DeadB_SOM_being_lost_due_to_energy_harvesting']
        idx6 = fcol_in_mdf['GRASS_soil_degradation_from_forest_fires']
        idx7 = fcol_in_mdf['GRASS_runoff']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] + mdf[rowi, idx4] + mdf[rowi, idx5] + mdf[rowi, idx6] + mdf[rowi, idx7] )  *  Carbon_per_biomass 
    
    # NF_Biomass_in_construction_material_being_burnt = NF_Biomass_locked_in_construction_material_GtBiomass / NF_Avg_life_of_building_yr * NF_Fraction_of_construction_waste_burned_0_to_1
        idxlhs = fcol_in_mdf['NF_Biomass_in_construction_material_being_burnt']
        idx1 = fcol_in_mdf['NF_Biomass_locked_in_construction_material_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  NF_Avg_life_of_building_yr  *  NF_Fraction_of_construction_waste_burned_0_to_1 
    
    # NF_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting = ( NF_being_deforested_Mkm2_py + NF_burning_Mkm2_py + NF_being_harvested_by_clear_cutting_Mkm2_py + NF_being_harvested_normally_Mkm2_py ) * NF_living_biomass_densitiy_tBiomass_pr_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
        idxlhs = fcol_in_mdf['NF_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting']
        idx1 = fcol_in_mdf['NF_being_deforested_Mkm2_py']
        idx2 = fcol_in_mdf['NF_burning_Mkm2_py']
        idx3 = fcol_in_mdf['NF_being_harvested_by_clear_cutting_Mkm2_py']
        idx4 = fcol_in_mdf['NF_being_harvested_normally_Mkm2_py']
        idx5 = fcol_in_mdf['NF_living_biomass_densitiy_tBiomass_pr_km2']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] + mdf[rowi, idx4] )  * mdf[rowi, idx5] /  UNIT_conversion_GtBiomass_py_to_Mkm2_py 
    
    # CO2_flow_from_NF_to_atmosphere_GtC_py = ( NF_Biomass_in_construction_material_being_burnt + NF_Dead_biomass_decomposing + NF_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting + NF_DeadB_SOM_being_lost_due_to_deforestation + NF_DeadB_SOM_being_lost_due_to_energy_harvesting + NF_soil_degradation_from_clear_cutting + NF_soil_degradation_from_forest_fires + NF_runoff ) * Carbon_per_biomass
        idxlhs = fcol_in_mdf['CO2_flow_from_NF_to_atmosphere_GtC_py']
        idx1 = fcol_in_mdf['NF_Biomass_in_construction_material_being_burnt']
        idx2 = fcol_in_mdf['NF_Dead_biomass_decomposing']
        idx3 = fcol_in_mdf['NF_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting']
        idx4 = fcol_in_mdf['NF_DeadB_SOM_being_lost_due_to_deforestation']
        idx5 = fcol_in_mdf['NF_DeadB_SOM_being_lost_due_to_energy_harvesting']
        idx6 = fcol_in_mdf['NF_soil_degradation_from_clear_cutting']
        idx7 = fcol_in_mdf['NF_soil_degradation_from_forest_fires']
        idx8 = fcol_in_mdf['NF_runoff']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] + mdf[rowi, idx4] + mdf[rowi, idx5] + mdf[rowi, idx6] + mdf[rowi, idx7] + mdf[rowi, idx8] )  *  Carbon_per_biomass 
    
    # TROP_Biomass_in_construction_material_being_burnt = TROP_Biomass_locked_in_construction_material_GtBiomass / TROP_Avg_life_of_building_yr * TROP_Fraction_of_construction_waste_burned_0_to_1
        idxlhs = fcol_in_mdf['TROP_Biomass_in_construction_material_being_burnt']
        idx1 = fcol_in_mdf['TROP_Biomass_locked_in_construction_material_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  TROP_Avg_life_of_building_yr  *  TROP_Fraction_of_construction_waste_burned_0_to_1 
    
    # TROP_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting = ( TROP_being_deforested_Mkm2_py + TROP_burning + TROP_being_harvested_by_clear_cutting + TROP_being_harvested_normally ) * TROP_living_biomass_densitiy_tBiomass_pr_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
        idxlhs = fcol_in_mdf['TROP_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting']
        idx1 = fcol_in_mdf['TROP_being_deforested_Mkm2_py']
        idx2 = fcol_in_mdf['TROP_burning']
        idx3 = fcol_in_mdf['TROP_being_harvested_by_clear_cutting']
        idx4 = fcol_in_mdf['TROP_being_harvested_normally']
        idx5 = fcol_in_mdf['TROP_living_biomass_densitiy_tBiomass_pr_km2']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] + mdf[rowi, idx4] )  * mdf[rowi, idx5] /  UNIT_conversion_GtBiomass_py_to_Mkm2_py 
    
    # CO2_flow_from_TROP_to_atmosphere_GtC_py = ( TROP_Biomass_in_construction_material_being_burnt + TROP_Dead_biomass_decomposing + TROP_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting + TROP_DeadB_SOM_being_lost_due_to_deforestation + TROP_DeadB_SOM_being_lost_due_to_energy_harvesting + TROP_soil_degradation_from_clear_cutting + TROP_soil_degradation_from_forest_fires + TROP_runoff ) * Carbon_per_biomass
        idxlhs = fcol_in_mdf['CO2_flow_from_TROP_to_atmosphere_GtC_py']
        idx1 = fcol_in_mdf['TROP_Biomass_in_construction_material_being_burnt']
        idx2 = fcol_in_mdf['TROP_Dead_biomass_decomposing']
        idx3 = fcol_in_mdf['TROP_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting']
        idx4 = fcol_in_mdf['TROP_DeadB_SOM_being_lost_due_to_deforestation']
        idx5 = fcol_in_mdf['TROP_DeadB_SOM_being_lost_due_to_energy_harvesting']
        idx6 = fcol_in_mdf['TROP_soil_degradation_from_clear_cutting']
        idx7 = fcol_in_mdf['TROP_soil_degradation_from_forest_fires']
        idx8 = fcol_in_mdf['TROP_runoff']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] + mdf[rowi, idx4] + mdf[rowi, idx5] + mdf[rowi, idx6] + mdf[rowi, idx7] + mdf[rowi, idx8] )  *  Carbon_per_biomass 
    
    # TUNDRA_Biomass_in_construction_material_being_burnt = TUNDRA_Biomass_locked_in_construction_material_GtBiomass / TUNDRA_Avg_life_of_building_yr * TUNDRA_Fraction_of_construction_waste_burned_0_to_1
        idxlhs = fcol_in_mdf['TUNDRA_Biomass_in_construction_material_being_burnt']
        idx1 = fcol_in_mdf['TUNDRA_Biomass_locked_in_construction_material_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  TUNDRA_Avg_life_of_building_yr  *  TUNDRA_Fraction_of_construction_waste_burned_0_to_1 
    
    # TUNDRA_Dead_biomass_decomposing = TUNDRA_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass / TUNDRA_Time_to_decompose_undisturbed_dead_biomass_yr
        idxlhs = fcol_in_mdf['TUNDRA_Dead_biomass_decomposing']
        idx1 = fcol_in_mdf['TUNDRA_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  TUNDRA_Time_to_decompose_undisturbed_dead_biomass_yr 
    
    # TUNDRA_with_normal_cover_Mkm2 = Tundra_potential_area_Mkm2 - TUNDRA_area_burnt_Mkm2 - TUNDRA_deforested_Mkm2 - TUNDRA_area_harvested_Mkm2
        idxlhs = fcol_in_mdf['TUNDRA_with_normal_cover_Mkm2']
        idx1 = fcol_in_mdf['Tundra_potential_area_Mkm2']
        idx2 = fcol_in_mdf['TUNDRA_area_burnt_Mkm2']
        idx3 = fcol_in_mdf['TUNDRA_deforested_Mkm2']
        idx4 = fcol_in_mdf['TUNDRA_area_harvested_Mkm2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] - mdf[rowi, idx2] - mdf[rowi, idx3] - mdf[rowi, idx4]
    
    # TUNDRA_being_deforested_Mkm2_py = TUNDRA_with_normal_cover_Mkm2 * Fraction_TUNDRA_being_deforested_1_py
        idxlhs = fcol_in_mdf['TUNDRA_being_deforested_Mkm2_py']
        idx1 = fcol_in_mdf['TUNDRA_with_normal_cover_Mkm2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Fraction_TUNDRA_being_deforested_1_py 
    
    # TUNDRA_burning_Mkm2_py = TUNDRA_with_normal_cover_Mkm2 * Effect_of_temperature_on_fire_incidence * TUNDRA_Normal_fire_incidence_fraction_py / 100
        idxlhs = fcol_in_mdf['TUNDRA_burning_Mkm2_py']
        idx1 = fcol_in_mdf['TUNDRA_with_normal_cover_Mkm2']
        idx2 = fcol_in_mdf['Effect_of_temperature_on_fire_incidence']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2] *  TUNDRA_Normal_fire_incidence_fraction_py  /  100 
    
    # Use_of_TUNDRA_biomass_for_energy = Use_of_TUNDRA_for_energy_in_2000_GtBiomass * Effect_of_population_and_urbanization_on_biomass_use * UNIT_conversion_1_py
        idxlhs = fcol_in_mdf['Use_of_TUNDRA_biomass_for_energy']
        idx1 = fcol_in_mdf['Effect_of_population_and_urbanization_on_biomass_use']
        mdf[rowi, idxlhs] =  Use_of_TUNDRA_for_energy_in_2000_GtBiomass  * mdf[rowi, idx1] *  UNIT_conversion_1_py 
    
    # TUNDRA_living_biomass_densitiy_tBiomass_pr_km2 = TUNDRA_living_biomass_densitiy_at_initial_time_tBiomass_pr_km2 * Effect_of_CO2_on_new_biomass_growth * Effect_of_temperature_on_new_biomass_growth_dmnl
        idxlhs = fcol_in_mdf['TUNDRA_living_biomass_densitiy_tBiomass_pr_km2']
        idx1 = fcol_in_mdf['Effect_of_CO2_on_new_biomass_growth']
        idx2 = fcol_in_mdf['Effect_of_temperature_on_new_biomass_growth_dmnl']
        mdf[rowi, idxlhs] =  TUNDRA_living_biomass_densitiy_at_initial_time_tBiomass_pr_km2  * mdf[rowi, idx1] * mdf[rowi, idx2]
    
    # TUNDRA_being_harvested_Mkm2_py = Use_of_TUNDRA_biomass_for_energy / TUNDRA_living_biomass_densitiy_tBiomass_pr_km2 * UNIT_conversion_GtBiomass_py_to_Mkm2_py
        idxlhs = fcol_in_mdf['TUNDRA_being_harvested_Mkm2_py']
        idx1 = fcol_in_mdf['Use_of_TUNDRA_biomass_for_energy']
        idx2 = fcol_in_mdf['TUNDRA_living_biomass_densitiy_tBiomass_pr_km2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] / mdf[rowi, idx2] *  UNIT_conversion_GtBiomass_py_to_Mkm2_py 
    
    # TUNDRA_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting = ( TUNDRA_being_deforested_Mkm2_py + TUNDRA_burning_Mkm2_py + TUNDRA_being_harvested_Mkm2_py ) * TUNDRA_living_biomass_densitiy_tBiomass_pr_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
        idxlhs = fcol_in_mdf['TUNDRA_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting']
        idx1 = fcol_in_mdf['TUNDRA_being_deforested_Mkm2_py']
        idx2 = fcol_in_mdf['TUNDRA_burning_Mkm2_py']
        idx3 = fcol_in_mdf['TUNDRA_being_harvested_Mkm2_py']
        idx4 = fcol_in_mdf['TUNDRA_living_biomass_densitiy_tBiomass_pr_km2']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] )  * mdf[rowi, idx4] /  UNIT_conversion_GtBiomass_py_to_Mkm2_py 
    
    # TUNDRA_DeadB_and_SOM_tB_per_km2 = TUNDRA_DeadB_and_SOM_densitiy_at_initial_time_tBiomass_pr_km2 * Effect_of_CO2_on_new_biomass_growth * Effect_of_temperature_on_new_biomass_growth_dmnl
        idxlhs = fcol_in_mdf['TUNDRA_DeadB_and_SOM_tB_per_km2']
        idx1 = fcol_in_mdf['Effect_of_CO2_on_new_biomass_growth']
        idx2 = fcol_in_mdf['Effect_of_temperature_on_new_biomass_growth_dmnl']
        mdf[rowi, idxlhs] =  TUNDRA_DeadB_and_SOM_densitiy_at_initial_time_tBiomass_pr_km2  * mdf[rowi, idx1] * mdf[rowi, idx2]
    
    # TUNDRA_DeadB_SOM_being_lost_due_to_deforestation = TUNDRA_being_deforested_Mkm2_py * TUNDRA_fraction_of_DeadB_and_SOM_being_destroyed_by_deforesting * TUNDRA_DeadB_and_SOM_tB_per_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
        idxlhs = fcol_in_mdf['TUNDRA_DeadB_SOM_being_lost_due_to_deforestation']
        idx1 = fcol_in_mdf['TUNDRA_being_deforested_Mkm2_py']
        idx2 = fcol_in_mdf['TUNDRA_DeadB_and_SOM_tB_per_km2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  TUNDRA_fraction_of_DeadB_and_SOM_being_destroyed_by_deforesting  * mdf[rowi, idx2] /  UNIT_conversion_GtBiomass_py_to_Mkm2_py 
    
    # TUNDRA_DeadB_SOM_being_lost_due_to_energy_harvesting = TUNDRA_being_harvested_Mkm2_py * TUNDRA_fraction_of_DeadB_and_SOM_being_destroyed_by_energy_harvesting * TUNDRA_DeadB_and_SOM_tB_per_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
        idxlhs = fcol_in_mdf['TUNDRA_DeadB_SOM_being_lost_due_to_energy_harvesting']
        idx1 = fcol_in_mdf['TUNDRA_being_harvested_Mkm2_py']
        idx2 = fcol_in_mdf['TUNDRA_DeadB_and_SOM_tB_per_km2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  TUNDRA_fraction_of_DeadB_and_SOM_being_destroyed_by_energy_harvesting  * mdf[rowi, idx2] /  UNIT_conversion_GtBiomass_py_to_Mkm2_py 
    
    # TUNDRA_soil_degradation_from_forest_fires = TUNDRA_burning_Mkm2_py * TUNDRA_DeadB_and_SOM_tB_per_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py * TUNDRA_fraction_of_DeadB_and_SOM_destroyed_by_natural_fires
        idxlhs = fcol_in_mdf['TUNDRA_soil_degradation_from_forest_fires']
        idx1 = fcol_in_mdf['TUNDRA_burning_Mkm2_py']
        idx2 = fcol_in_mdf['TUNDRA_DeadB_and_SOM_tB_per_km2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2] /  UNIT_conversion_GtBiomass_py_to_Mkm2_py  *  TUNDRA_fraction_of_DeadB_and_SOM_destroyed_by_natural_fires 
    
    # CO2_flow_from_TUNDRA_to_atmosphere = ( TUNDRA_Biomass_in_construction_material_being_burnt + TUNDRA_Dead_biomass_decomposing + TUNDRA_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting + TUNDRA_DeadB_SOM_being_lost_due_to_deforestation + TUNDRA_DeadB_SOM_being_lost_due_to_energy_harvesting + TUNDRA_soil_degradation_from_forest_fires + TUNDRA_runoff ) * Carbon_per_biomass
        idxlhs = fcol_in_mdf['CO2_flow_from_TUNDRA_to_atmosphere']
        idx1 = fcol_in_mdf['TUNDRA_Biomass_in_construction_material_being_burnt']
        idx2 = fcol_in_mdf['TUNDRA_Dead_biomass_decomposing']
        idx3 = fcol_in_mdf['TUNDRA_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting']
        idx4 = fcol_in_mdf['TUNDRA_DeadB_SOM_being_lost_due_to_deforestation']
        idx5 = fcol_in_mdf['TUNDRA_DeadB_SOM_being_lost_due_to_energy_harvesting']
        idx6 = fcol_in_mdf['TUNDRA_soil_degradation_from_forest_fires']
        idx7 = fcol_in_mdf['TUNDRA_runoff']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] + mdf[rowi, idx4] + mdf[rowi, idx5] + mdf[rowi, idx6] + mdf[rowi, idx7] )  *  Carbon_per_biomass 
    
    # GRASS_potential_living_biomass_GtBiomass = ( GRASS_potential_area_Mkm2 - GRASS_deforested_Mkm2 ) * GRASS_living_biomass_densitiy_tBiomass_pr_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
        idxlhs = fcol_in_mdf['GRASS_potential_living_biomass_GtBiomass']
        idx1 = fcol_in_mdf['GRASS_potential_area_Mkm2']
        idx2 = fcol_in_mdf['GRASS_deforested_Mkm2']
        idx3 = fcol_in_mdf['GRASS_living_biomass_densitiy_tBiomass_pr_km2']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] - mdf[rowi, idx2] )  * mdf[rowi, idx3] /  UNIT_conversion_GtBiomass_py_to_Mkm2_py 
    
    # GRASS_potential_less_actual_living_biomass_GtBiomass = GRASS_potential_living_biomass_GtBiomass - GRASS_Living_biomass_GtBiomass
        idxlhs = fcol_in_mdf['GRASS_potential_less_actual_living_biomass_GtBiomass']
        idx1 = fcol_in_mdf['GRASS_potential_living_biomass_GtBiomass']
        idx2 = fcol_in_mdf['GRASS_Living_biomass_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] - mdf[rowi, idx2]
    
    # GRASS_biomass_new_growing = GRASS_potential_less_actual_living_biomass_GtBiomass / GRASS_Speed_of_regrowth_yr
        idxlhs = fcol_in_mdf['GRASS_biomass_new_growing']
        idx1 = fcol_in_mdf['GRASS_potential_less_actual_living_biomass_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  GRASS_Speed_of_regrowth_yr 
    
    # CO2_flux_from_atm_to_GRASS_for_new_growth_GtC_py = GRASS_biomass_new_growing * Carbon_per_biomass
        idxlhs = fcol_in_mdf['CO2_flux_from_atm_to_GRASS_for_new_growth_GtC_py']
        idx1 = fcol_in_mdf['GRASS_biomass_new_growing']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Carbon_per_biomass 
    
    # NF_potential_living_biomass_GtBiomass = ( NF_potential_area_Mkm2 - NF_area_deforested_Mkm2 ) * NF_living_biomass_densitiy_tBiomass_pr_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
        idxlhs = fcol_in_mdf['NF_potential_living_biomass_GtBiomass']
        idx1 = fcol_in_mdf['NF_potential_area_Mkm2']
        idx2 = fcol_in_mdf['NF_area_deforested_Mkm2']
        idx3 = fcol_in_mdf['NF_living_biomass_densitiy_tBiomass_pr_km2']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] - mdf[rowi, idx2] )  * mdf[rowi, idx3] /  UNIT_conversion_GtBiomass_py_to_Mkm2_py 
    
    # NF_potential_less_actual_living_biomass_GtBiomass = NF_potential_living_biomass_GtBiomass - NF_Living_biomass_GtBiomass
        idxlhs = fcol_in_mdf['NF_potential_less_actual_living_biomass_GtBiomass']
        idx1 = fcol_in_mdf['NF_potential_living_biomass_GtBiomass']
        idx2 = fcol_in_mdf['NF_Living_biomass_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] - mdf[rowi, idx2]
    
    # NF_biomass_new_growing = NF_potential_less_actual_living_biomass_GtBiomass / NF_Speed_of_regrowth_yr
        idxlhs = fcol_in_mdf['NF_biomass_new_growing']
        idx1 = fcol_in_mdf['NF_potential_less_actual_living_biomass_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  NF_Speed_of_regrowth_yr 
    
    # CO2_flux_from_atm_to_NF_for_new_growth_GtC_py = NF_biomass_new_growing * Carbon_per_biomass
        idxlhs = fcol_in_mdf['CO2_flux_from_atm_to_NF_for_new_growth_GtC_py']
        idx1 = fcol_in_mdf['NF_biomass_new_growing']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Carbon_per_biomass 
    
    # TROP_potential_living_biomass_GtBiomass = ( TROP_potential_area_Mkm2 - TROP_area_deforested ) * TROP_living_biomass_densitiy_tBiomass_pr_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
        idxlhs = fcol_in_mdf['TROP_potential_living_biomass_GtBiomass']
        idx1 = fcol_in_mdf['TROP_potential_area_Mkm2']
        idx2 = fcol_in_mdf['TROP_area_deforested']
        idx3 = fcol_in_mdf['TROP_living_biomass_densitiy_tBiomass_pr_km2']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] - mdf[rowi, idx2] )  * mdf[rowi, idx3] /  UNIT_conversion_GtBiomass_py_to_Mkm2_py 
    
    # TROP_potential_less_actual_living_biomass_GtBiomass = TROP_potential_living_biomass_GtBiomass - TROP_Living_biomass_GtBiomass
        idxlhs = fcol_in_mdf['TROP_potential_less_actual_living_biomass_GtBiomass']
        idx1 = fcol_in_mdf['TROP_potential_living_biomass_GtBiomass']
        idx2 = fcol_in_mdf['TROP_Living_biomass_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] - mdf[rowi, idx2]
    
    # TROP_biomass_new_growing = TROP_potential_less_actual_living_biomass_GtBiomass / TROP_Speed_of_regrowth_yr
        idxlhs = fcol_in_mdf['TROP_biomass_new_growing']
        idx1 = fcol_in_mdf['TROP_potential_less_actual_living_biomass_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  TROP_Speed_of_regrowth_yr 
    
    # CO2_flux_from_atm_to_TROP_for_new_growth_GtC_py = TROP_biomass_new_growing * Carbon_per_biomass
        idxlhs = fcol_in_mdf['CO2_flux_from_atm_to_TROP_for_new_growth_GtC_py']
        idx1 = fcol_in_mdf['TROP_biomass_new_growing']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Carbon_per_biomass 
    
    # TUNDRA_potential_living_biomass_GtBiomass = ( Tundra_potential_area_Mkm2 - TUNDRA_deforested_Mkm2 ) * TUNDRA_living_biomass_densitiy_tBiomass_pr_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
        idxlhs = fcol_in_mdf['TUNDRA_potential_living_biomass_GtBiomass']
        idx1 = fcol_in_mdf['Tundra_potential_area_Mkm2']
        idx2 = fcol_in_mdf['TUNDRA_deforested_Mkm2']
        idx3 = fcol_in_mdf['TUNDRA_living_biomass_densitiy_tBiomass_pr_km2']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] - mdf[rowi, idx2] )  * mdf[rowi, idx3] /  UNIT_conversion_GtBiomass_py_to_Mkm2_py 
    
    # TUNDRA_potential_less_actual_living_biomass_GtBiomass = TUNDRA_potential_living_biomass_GtBiomass - TUNDRA_Living_biomass
        idxlhs = fcol_in_mdf['TUNDRA_potential_less_actual_living_biomass_GtBiomass']
        idx1 = fcol_in_mdf['TUNDRA_potential_living_biomass_GtBiomass']
        idx2 = fcol_in_mdf['TUNDRA_Living_biomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] - mdf[rowi, idx2]
    
    # TUNDRA_biomass_new_growing = TUNDRA_potential_less_actual_living_biomass_GtBiomass / TUNDRA_Speed_of_regrowth_yr
        idxlhs = fcol_in_mdf['TUNDRA_biomass_new_growing']
        idx1 = fcol_in_mdf['TUNDRA_potential_less_actual_living_biomass_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  TUNDRA_Speed_of_regrowth_yr 
    
    # CO2_flux_from_atm_to_TUNDRA_for_new_growth = TUNDRA_biomass_new_growing * Carbon_per_biomass
        idxlhs = fcol_in_mdf['CO2_flux_from_atm_to_TUNDRA_for_new_growth']
        idx1 = fcol_in_mdf['TUNDRA_biomass_new_growing']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Carbon_per_biomass 
    
    # CO2_flux_GRASS_to_atm_GtC_py = CO2_flow_from_GRASS_to_atmosphere_GtC_py
        idxlhs = fcol_in_mdf['CO2_flux_GRASS_to_atm_GtC_py']
        idx1 = fcol_in_mdf['CO2_flow_from_GRASS_to_atmosphere_GtC_py']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # CO2_flux_NF_to_atm_GtC_py = CO2_flow_from_NF_to_atmosphere_GtC_py
        idxlhs = fcol_in_mdf['CO2_flux_NF_to_atm_GtC_py']
        idx1 = fcol_in_mdf['CO2_flow_from_NF_to_atmosphere_GtC_py']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # CO2_flux_TROP_to_atm_GtC_py = CO2_flow_from_TROP_to_atmosphere_GtC_py
        idxlhs = fcol_in_mdf['CO2_flux_TROP_to_atm_GtC_py']
        idx1 = fcol_in_mdf['CO2_flow_from_TROP_to_atmosphere_GtC_py']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # CO2_flux_TUNDRA_to_atm = CO2_flow_from_TUNDRA_to_atmosphere
        idxlhs = fcol_in_mdf['CO2_flux_TUNDRA_to_atm']
        idx1 = fcol_in_mdf['CO2_flow_from_TUNDRA_to_atmosphere']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # Cohort_50plus[region] = Cohort_50_to_54[region] + Cohort_55_to_59[region] + Cohort_60plus[region]
        idxlhs = fcol_in_mdf['Cohort_50plus']
        idx1 = fcol_in_mdf['Cohort_50_to_54']
        idx2 = fcol_in_mdf['Cohort_55_to_59']
        idx3 = fcol_in_mdf['Cohort_60plus']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10]
     
    # Global_All_SDG_Scores = All_SDG_Scores[us] * Regional_population_as_fraction_of_total[us] + All_SDG_Scores[af] * Regional_population_as_fraction_of_total[af] + All_SDG_Scores[cn] * Regional_population_as_fraction_of_total[cn] + All_SDG_Scores[me] * Regional_population_as_fraction_of_total[me] + All_SDG_Scores[sa] * Regional_population_as_fraction_of_total[sa] + All_SDG_Scores[la] * Regional_population_as_fraction_of_total[la] + All_SDG_Scores[pa] * Regional_population_as_fraction_of_total[pa] + All_SDG_Scores[ec] * Regional_population_as_fraction_of_total[ec] + All_SDG_Scores[eu] * Regional_population_as_fraction_of_total[eu] + All_SDG_Scores[se] * Regional_population_as_fraction_of_total[se]
        idxlhs = fcol_in_mdf['Global_All_SDG_Scores']
        idx1 = fcol_in_mdf['All_SDG_Scores']
        idx2 = fcol_in_mdf['Regional_population_as_fraction_of_total']
        mdf[rowi, idxlhs] = ( mdf[rowi, idx1 + 0 ] *  mdf[rowi, idx2 + 0 ]+ mdf[rowi, idx1 + 1 ] *  mdf[rowi, idx2 + 1 ]+ mdf[rowi, idx1 + 2 ] *  mdf[rowi, idx2 + 2 ]+ mdf[rowi, idx1 + 3 ] *  mdf[rowi, idx2 + 3 ]+ mdf[rowi, idx1 + 4 ] *  mdf[rowi, idx2 + 4 ]+ mdf[rowi, idx1 + 5 ] *  mdf[rowi, idx2 + 5 ]+ mdf[rowi, idx1 + 6 ] *  mdf[rowi, idx2 + 6 ]+ mdf[rowi, idx1 + 7 ] *  mdf[rowi, idx2 + 7 ]+ mdf[rowi, idx1 + 8 ] *  mdf[rowi, idx2 + 8 ]+ mdf[rowi, idx1 + 9 ] *  mdf[rowi, idx2 + 9 ] )
    
    # Smoothed_SDG_score_for_effect_of_wellbeing = SMOOTH3 ( Global_All_SDG_Scores , Time_to_smooth_the_anchor_SDG_scores_for_wellbeing )
        idx1 = fcol_in_mdf['Global_All_SDG_Scores']
        idxin = fcol_in_mdf['Global_All_SDG_Scores' ]
        idx2 = fcol_in_mdf['Smoothed_SDG_score_for_effect_of_wellbeing_2']
        idx1 = fcol_in_mdf['Smoothed_SDG_score_for_effect_of_wellbeing_1']
        idxout = fcol_in_mdf['Smoothed_SDG_score_for_effect_of_wellbeing']
        mdf[rowi, idxout] = mdf[rowi-1, idxout] + ( mdf[rowi-1, idx2] - mdf[rowi-1, idxout]) / ( Time_to_smooth_the_anchor_SDG_scores_for_wellbeing / 3) * dt
        mdf[rowi, idx2] = mdf[rowi-1, idx2] + ( mdf[rowi-1, idx1] - mdf[rowi-1, idx2]) / ( Time_to_smooth_the_anchor_SDG_scores_for_wellbeing / 3) * dt
        mdf[rowi, idx1] = mdf[rowi-1, idx1] + ( mdf[rowi-1, idxin] - mdf[rowi-1, idx1]) / ( Time_to_smooth_the_anchor_SDG_scores_for_wellbeing / 3) * dt
    
    # Comparison_Effect_of_SDG_score_on_wellbeing[region] = IF_THEN_ELSE ( zeit < 2023 , 1 , 1 + ( All_SDG_Scores / Smoothed_SDG_score_for_effect_of_wellbeing - 1 ) * Strength_of_Effect_of_SDG_scores_on_wellbeing )
        idxlhs = fcol_in_mdf['Comparison_Effect_of_SDG_score_on_wellbeing']
        idx1 = fcol_in_mdf['All_SDG_Scores']
        idx2 = fcol_in_mdf['Smoothed_SDG_score_for_effect_of_wellbeing']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  <  2023  ,  1  ,  1  +  ( mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2] -  1  )  *  Strength_of_Effect_of_SDG_scores_on_wellbeing  ) 
    
    # Investment_demand[region] = Initiating_capacity_construction[region]
        idxlhs = fcol_in_mdf['Investment_demand']
        idx1 = fcol_in_mdf['Initiating_capacity_construction']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10]
    
    # Future_WACC_fraction[region] = IF_THEN_ELSE ( zeit > Policy_start_year , Indicated_WACC_fraction , 0 )
        idxlhs = fcol_in_mdf['Future_WACC_fraction']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >  Policy_start_year  ,  Indicated_WACC_fraction[0:10]  ,  0  ) 
    
    # WACC_fraction[region] = SMOOTH3 ( Future_WACC_fraction[region] , Time_to_ease_in_wealth_accumulation )
        idxin = fcol_in_mdf['Future_WACC_fraction' ]
        idx2 = fcol_in_mdf['WACC_fraction_2']
        idx1 = fcol_in_mdf['WACC_fraction_1']
        idxout = fcol_in_mdf['WACC_fraction']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( Time_to_ease_in_wealth_accumulation / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( Time_to_ease_in_wealth_accumulation / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( Time_to_ease_in_wealth_accumulation / 3) * dt
    
    # Fraction_of_owner_income_left_for_consumption_or_wealth_accumulation[region] = 1 - Owner_saving_fraction[region]
        idxlhs = fcol_in_mdf['Fraction_of_owner_income_left_for_consumption_or_wealth_accumulation']
        idx1 = fcol_in_mdf['Owner_saving_fraction']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  - mdf[rowi , idx1:idx1 + 10]
    
    # Owner_consumption_fraction[region] = ( 1 - WACC_fraction[region] ) * Fraction_of_owner_income_left_for_consumption_or_wealth_accumulation[region]
        idxlhs = fcol_in_mdf['Owner_consumption_fraction']
        idx1 = fcol_in_mdf['WACC_fraction']
        idx2 = fcol_in_mdf['Fraction_of_owner_income_left_for_consumption_or_wealth_accumulation']
        mdf[rowi, idxlhs:idxlhs + 10] =  (  1  - mdf[rowi , idx1:idx1 + 10] )  * mdf[rowi , idx2:idx2 + 10]
    
    # Owner_consumption[region] = Owner_cash_inflow_seasonally_adjusted[region] * Owner_consumption_fraction[region]
        idxlhs = fcol_in_mdf['Owner_consumption']
        idx1 = fcol_in_mdf['Owner_cash_inflow_seasonally_adjusted']
        idx2 = fcol_in_mdf['Owner_consumption_fraction']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # End_user_consumption_to_be_taxed[region] = Owner_consumption[region] + Worker_consumption_demand[region]
        idxlhs = fcol_in_mdf['End_user_consumption_to_be_taxed']
        idx1 = fcol_in_mdf['Owner_consumption']
        idx2 = fcol_in_mdf['Worker_consumption_demand']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10]
    
    # Consumption_taxes[region] = End_user_consumption_to_be_taxed[region] * ( Consumption_tax_rate_ie_fraction + ICTR_policy[region] )
        idxlhs = fcol_in_mdf['Consumption_taxes']
        idx1 = fcol_in_mdf['End_user_consumption_to_be_taxed']
        idx2 = fcol_in_mdf['ICTR_policy']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  Consumption_tax_rate_ie_fraction  + mdf[rowi , idx2:idx2 + 10] ) 
    
    # Total_consumption[region] = Worker_consumption_demand[region] + Govt_consumption_ie_purchases[region] + Owner_consumption[region] - Consumption_taxes[region]
        idxlhs = fcol_in_mdf['Total_consumption']
        idx1 = fcol_in_mdf['Worker_consumption_demand']
        idx2 = fcol_in_mdf['Govt_consumption_ie_purchases']
        idx3 = fcol_in_mdf['Owner_consumption']
        idx4 = fcol_in_mdf['Consumption_taxes']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] - mdf[rowi , idx4:idx4 + 10]
    
    # Consumption_and_investment[region] = Investment_demand[region] + Total_consumption[region]
        idxlhs = fcol_in_mdf['Consumption_and_investment']
        idx1 = fcol_in_mdf['Investment_demand']
        idx2 = fcol_in_mdf['Total_consumption']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10]
    
    # Frac_blocked_by_ALL_GHG = Blocked_by_CO2 + Blocked_by_CH4 + Blocked_by_H20 + Blocked_by_otherGHG
        idxlhs = fcol_in_mdf['Frac_blocked_by_ALL_GHG']
        idx1 = fcol_in_mdf['Blocked_by_CO2']
        idx2 = fcol_in_mdf['Blocked_by_CH4']
        idx3 = fcol_in_mdf['Blocked_by_H20']
        idx4 = fcol_in_mdf['Blocked_by_otherGHG']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] + mdf[rowi, idx4]
    
    # Convection_as_f_of_temp_ZJ_py = ( Incoming_solar_in_1850_ZJ_py * Convection_as_f_of_incoming_solar_in_1850 ) * ( 1 + Sensitivity_of_convection_to_temp * ( Temp_surface_current_divided_by_value_anfang - 1 ) )
        idxlhs = fcol_in_mdf['Convection_as_f_of_temp_ZJ_py']
        idx1 = fcol_in_mdf['Temp_surface_current_divided_by_value_anfang']
        mdf[rowi, idxlhs] =  (  Incoming_solar_in_1850_ZJ_py  *  Convection_as_f_of_incoming_solar_in_1850  )  *  (  1  +  Sensitivity_of_convection_to_temp  *  ( mdf[rowi, idx1] -  1  )  ) 
    
    # Convection_aka_sensible_heat_flow = Convection_as_f_of_temp_ZJ_py
        idxlhs = fcol_in_mdf['Convection_aka_sensible_heat_flow']
        idx1 = fcol_in_mdf['Convection_as_f_of_temp_ZJ_py']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # Indicated_crop_yield_func_SE = Indicated_crop_yield_SE_L / ( 1 + np.exp ( - Indicated_crop_yield_SE_k * ( Nitrogen_use[se] * UNIT_conv_N_to_yield - Indicated_crop_yield_SE_x ) ) ) - ( Indicated_crop_yield_SE_L2 / ( 1 + np.exp ( - Indicated_crop_yield_SE_k2 * ( Nitrogen_use[se] * UNIT_conv_N_to_yield - Indicated_crop_yield_SE_x2 ) ) ) )
        idxlhs = fcol_in_mdf['Indicated_crop_yield_func_SE']
        idx1 = fcol_in_mdf['Nitrogen_use']
        idx2 = fcol_in_mdf['Nitrogen_use']
        mdf[rowi, idxlhs] =  Indicated_crop_yield_SE_L  /  (  1  +  np.exp  (  -  Indicated_crop_yield_SE_k  *  ( mdf[rowi, idx1 + 9] *  UNIT_conv_N_to_yield  -  Indicated_crop_yield_SE_x  )  )  )  -  (  Indicated_crop_yield_SE_L2  /  (  1  +  np.exp  (  -  Indicated_crop_yield_SE_k2  *  ( mdf[rowi, idx2 + 9] *  UNIT_conv_N_to_yield  -  Indicated_crop_yield_SE_x2  )  )  )  ) 
    
    # Indicated_crop_yield_min_SE = IF_THEN_ELSE ( Nitrogen_use[9] >= 5 , Indicated_crop_yield_func_SE , Indicated_crop_yield_SE_min )
        idxlhs = fcol_in_mdf['Indicated_crop_yield_min_SE']
        idx1 = fcol_in_mdf['Nitrogen_use']
        idx2 = fcol_in_mdf['Indicated_crop_yield_func_SE']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  ( mdf[rowi, idx1 + 9] >=  5  , mdf[rowi, idx2] ,  Indicated_crop_yield_SE_min  ) 
    
    # Indicated_crop_yield_rest[region] = Indicated_crop_yield_rest_L[region] / ( 1 + np.exp ( - Indicated_crop_yield_rest_k[region] * ( Nitrogen_use[region] * UNIT_conv_N_to_yield - Indicated_crop_yield_rest_x0[region] ) ) )
        idxlhs = fcol_in_mdf['Indicated_crop_yield_rest']
        idx1 = fcol_in_mdf['Nitrogen_use']
        mdf[rowi, idxlhs:idxlhs + 10] =  Indicated_crop_yield_rest_L[0:10]  /  (  1  +  np.exp  (  -  Indicated_crop_yield_rest_k[0:10]  *  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_N_to_yield  -  Indicated_crop_yield_rest_x0[0:10]  )  )  ) 
    
    # Crop_yield_from_N_use = IF_THEN_ELSE ( j==9 , Indicated_crop_yield_min_SE , Indicated_crop_yield_rest )
        idxlhs = fcol_in_mdf['Crop_yield_from_N_use']
        idx1 = fcol_in_mdf['Indicated_crop_yield_min_SE']
        idx2 = fcol_in_mdf['Indicated_crop_yield_rest']
        for j in range(0,10):
            mdf[rowi, idxlhs + j] =  IF_THEN_ELSE  (  j==9  , mdf[rowi , idx1] , mdf[rowi , idx2 + j] ) 
    
    # GDPpp_USED_for_influencing_death_rates[region] = SMOOTH3 ( GDPpp_USED[region] , Time_for_GDPpp_to_affect_death_rates )
        idxin = fcol_in_mdf['GDPpp_USED' ]
        idx2 = fcol_in_mdf['GDPpp_USED_for_influencing_death_rates_2']
        idx1 = fcol_in_mdf['GDPpp_USED_for_influencing_death_rates_1']
        idxout = fcol_in_mdf['GDPpp_USED_for_influencing_death_rates']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( Time_for_GDPpp_to_affect_death_rates / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( Time_for_GDPpp_to_affect_death_rates / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( Time_for_GDPpp_to_affect_death_rates / 3) * dt
    
    # death_rate_dr0[region] = dr0_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ^ dr0_b[region] )
        idxlhs = fcol_in_mdf['death_rate_dr0']
        idx1 = fcol_in_mdf['GDPpp_USED_for_influencing_death_rates']
        mdf[rowi, idxlhs:idxlhs + 10] =  dr0_a[0:10]  *  (  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  )  **  dr0_b[0:10]  ) 
    
    # Indicated_Eff_of_env_damage_on_dying[region] = np.exp ( Combined_env_damage_indicator * expSoE_of_ed_on_dying ) / Actual_eff_of_relative_wealth_on_env_damage[region]
        idxlhs = fcol_in_mdf['Indicated_Eff_of_env_damage_on_dying']
        idx1 = fcol_in_mdf['Combined_env_damage_indicator']
        idx2 = fcol_in_mdf['Actual_eff_of_relative_wealth_on_env_damage']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.exp  ( mdf[rowi , idx1] *  expSoE_of_ed_on_dying  )  / mdf[rowi , idx2:idx2 + 10]
    
    # Eff_of_env_damage_on_dying[region] = SMOOTH ( Indicated_Eff_of_env_damage_on_dying[region] , Time_lag_for_env_damage_to_affect_mortality )
        idx1 = fcol_in_mdf['Eff_of_env_damage_on_dying']
        idx2 = fcol_in_mdf['Indicated_Eff_of_env_damage_on_dying']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1+10] + ( mdf[rowi-1 , idx2:idx2 + 10] - mdf[rowi -1 , idx1:idx1 + 10]) / Time_lag_for_env_damage_to_affect_mortality * dt
    
    # Ratio_of_regionally_available_crop_including_imports_to_regional_demand[region] = All_crop_regional_dmd[region] / ( Crop_grown_regionally[region] + Actual_crop_import[region] )
        idxlhs = fcol_in_mdf['Ratio_of_regionally_available_crop_including_imports_to_regional_demand']
        idx1 = fcol_in_mdf['All_crop_regional_dmd']
        idx2 = fcol_in_mdf['Crop_grown_regionally']
        idx3 = fcol_in_mdf['Actual_crop_import']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  ( mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] ) 
    
    # Ratio_of_demand_and_supply_of_crops_smoothed[region] = SMOOTH3 ( Ratio_of_regionally_available_crop_including_imports_to_regional_demand[region] , Time_to_smooth_regional_food_balance )
        idxin = fcol_in_mdf['Ratio_of_regionally_available_crop_including_imports_to_regional_demand' ]
        idx2 = fcol_in_mdf['Ratio_of_demand_and_supply_of_crops_smoothed_2']
        idx1 = fcol_in_mdf['Ratio_of_demand_and_supply_of_crops_smoothed_1']
        idxout = fcol_in_mdf['Ratio_of_demand_and_supply_of_crops_smoothed']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( Time_to_smooth_regional_food_balance / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( Time_to_smooth_regional_food_balance / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( Time_to_smooth_regional_food_balance / 3) * dt
    
    # Malnutition_scaled_to_zero[region] = IF_THEN_ELSE ( zeit > Policy_start_year , ( Ratio_of_demand_and_supply_of_crops_smoothed - 1 ) * Strength_of_malnutrition_effect , 0 )
        idxlhs = fcol_in_mdf['Malnutition_scaled_to_zero']
        idx1 = fcol_in_mdf['Ratio_of_demand_and_supply_of_crops_smoothed']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >  Policy_start_year  ,  ( mdf[rowi , idx1:idx1 + 10] -  1  )  *  Strength_of_malnutrition_effect  ,  0  ) 
    
    # Malnutrition[region] = 1 + Malnutition_scaled_to_zero[region]
        idxlhs = fcol_in_mdf['Malnutrition']
        idx1 = fcol_in_mdf['Malnutition_scaled_to_zero']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  + mdf[rowi , idx1:idx1 + 10]
    
    # Effect_of_malnutrition_on_dying[region] = WITH LOOKUP ( Malnutrition[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1 , 1 ) , ( 2 , 1.15 ) , ( 3 , 1.5 ) , ( 4 , 2 ) , ( 5 , 3 ) , ( 10 , 15 ) ) )
        tabidx = ftab_in_d_table['Effect_of_malnutrition_on_dying'] # fetch the correct table
        idx2 = fcol_in_mdf['Effect_of_malnutrition_on_dying'] # get the location of the lhs in mdf
        idx3 = fcol_in_mdf['Malnutrition']
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:,0], look[:, 1])
    
    # Effect_of_malnutrition_on_dying_smoothed[region] = SMOOTH ( Effect_of_malnutrition_on_dying[region] , Time_to_smooth_malnutrition_effect )
        idx1 = fcol_in_mdf['Effect_of_malnutrition_on_dying_smoothed']
        idx2 = fcol_in_mdf['Effect_of_malnutrition_on_dying']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1+10] + ( mdf[rowi-1 , idx2:idx2 + 10] - mdf[rowi -1 , idx1:idx1 + 10]) / Time_to_smooth_malnutrition_effect * dt
    
    # Effect_of_poverty_on_dying[region] = WITH LOOKUP ( Fraction_of_population_below_existential_minimum[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 1 ) , ( 0.5 , 1.025 ) , ( 1 , 1.1 ) ) )
        tabidx = ftab_in_d_table['Effect_of_poverty_on_dying'] # fetch the correct table
        idx2 = fcol_in_mdf['Effect_of_poverty_on_dying'] # get the location of the lhs in mdf
        idx3 = fcol_in_mdf['Fraction_of_population_below_existential_minimum']
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:,0], look[:, 1])
    
    # Effect_of_poverty_on_dying_from_policy_start_scaled_to_zero[region] = IF_THEN_ELSE ( zeit > Policy_start_year , ( Effect_of_poverty_on_dying - 1 ) * Strength_of_poverty_effect , 0 )
        idxlhs = fcol_in_mdf['Effect_of_poverty_on_dying_from_policy_start_scaled_to_zero']
        idx1 = fcol_in_mdf['Effect_of_poverty_on_dying']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >  Policy_start_year  ,  ( mdf[rowi, idx1:idx1 + 10] -  1  )  *  Strength_of_poverty_effect  ,  0  ) 
    
    # Effect_of_poverty_on_dying_from_policy_start[region] = 1 + Effect_of_poverty_on_dying_from_policy_start_scaled_to_zero[region]
        idxlhs = fcol_in_mdf['Effect_of_poverty_on_dying_from_policy_start']
        idx1 = fcol_in_mdf['Effect_of_poverty_on_dying_from_policy_start_scaled_to_zero']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  + mdf[rowi , idx1:idx1 + 10]
    
    # Effect_of_poverty_on_dying_smoothed[region] = SMOOTH ( Effect_of_poverty_on_dying_from_policy_start[region] , Time_to_smooth_poverty_effect )
        idx1 = fcol_in_mdf['Effect_of_poverty_on_dying_smoothed']
        idx2 = fcol_in_mdf['Effect_of_poverty_on_dying_from_policy_start']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1+10] + ( mdf[rowi-1 , idx2:idx2 + 10] - mdf[rowi -1 , idx1:idx1 + 10]) / Time_to_smooth_poverty_effect * dt
    
    # Inequality_effect_on_mortality[region] = 1 + ( Actual_inequality_index_higher_is_more_unequal[region] - 1 ) * Strength_of_inequality_effect_on_mortality
        idxlhs = fcol_in_mdf['Inequality_effect_on_mortality']
        idx1 = fcol_in_mdf['Actual_inequality_index_higher_is_more_unequal']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  +  ( mdf[rowi , idx1:idx1 + 10] -  1  )  *  Strength_of_inequality_effect_on_mortality 
    
    # dying_0_to_4[region] = Cohort_0_to_4[region] * death_rate_dr0[region] * Eff_of_env_damage_on_dying[region] * Effect_of_malnutrition_on_dying_smoothed[region] * Effect_of_poverty_on_dying_smoothed[region] * Inequality_effect_on_mortality[region]
        idxlhs = fcol_in_mdf['dying_0_to_4']
        idx1 = fcol_in_mdf['Cohort_0_to_4']
        idx2 = fcol_in_mdf['death_rate_dr0']
        idx3 = fcol_in_mdf['Eff_of_env_damage_on_dying']
        idx4 = fcol_in_mdf['Effect_of_malnutrition_on_dying_smoothed']
        idx5 = fcol_in_mdf['Effect_of_poverty_on_dying_smoothed']
        idx6 = fcol_in_mdf['Inequality_effect_on_mortality']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] * mdf[rowi , idx3:idx3 + 10] * mdf[rowi , idx4:idx4 + 10] * mdf[rowi , idx5:idx5 + 10] * mdf[rowi , idx6:idx6 + 10]
    
    # death_rate_dr35[region] = dr35_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ) ^ dr35_b[region]
        idxlhs = fcol_in_mdf['death_rate_dr35']
        idx1 = fcol_in_mdf['GDPpp_USED_for_influencing_death_rates']
        mdf[rowi, idxlhs:idxlhs + 10] =  dr35_a[0:10]  *  (  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  )  )  **  dr35_b[0:10] 
    
    # death_rate_dr40[region] = dr40_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ) ^ dr40_b[region]
        idxlhs = fcol_in_mdf['death_rate_dr40']
        idx1 = fcol_in_mdf['GDPpp_USED_for_influencing_death_rates']
        mdf[rowi, idxlhs:idxlhs + 10] =  dr40_a[0:10]  *  (  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  )  )  **  dr40_b[0:10] 
    
    # death_rate_dr45[region] = dr45_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ) ^ dr45_b[region]
        idxlhs = fcol_in_mdf['death_rate_dr45']
        idx1 = fcol_in_mdf['GDPpp_USED_for_influencing_death_rates']
        mdf[rowi, idxlhs:idxlhs + 10] =  dr45_a[0:10]  *  (  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  )  )  **  dr45_b[0:10] 
    
    # death_rate_dr50[region] = dr50_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ) ^ dr50_b[region]
        idxlhs = fcol_in_mdf['death_rate_dr50']
        idx1 = fcol_in_mdf['GDPpp_USED_for_influencing_death_rates']
        mdf[rowi, idxlhs:idxlhs + 10] =  dr50_a[0:10]  *  (  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  )  )  **  dr50_b[0:10] 
    
    # death_rate_dr55[region] = dr55_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ) ^ dr55_b[region]
        idxlhs = fcol_in_mdf['death_rate_dr55']
        idx1 = fcol_in_mdf['GDPpp_USED_for_influencing_death_rates']
        mdf[rowi, idxlhs:idxlhs + 10] =  dr55_a[0:10]  *  (  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  )  )  **  dr55_b[0:10] 
    
    # death_rate_dr60[region] = dr60_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ) ^ dr60_b[region]
        idxlhs = fcol_in_mdf['death_rate_dr60']
        idx1 = fcol_in_mdf['GDPpp_USED_for_influencing_death_rates']
        mdf[rowi, idxlhs:idxlhs + 10] =  dr60_a[0:10]  *  (  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  )  )  **  dr60_b[0:10] 
    
    # death_rate_dr65[region] = dr65_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ) ^ dr65_b[region]
        idxlhs = fcol_in_mdf['death_rate_dr65']
        idx1 = fcol_in_mdf['GDPpp_USED_for_influencing_death_rates']
        mdf[rowi, idxlhs:idxlhs + 10] =  dr65_a[0:10]  *  (  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  )  )  **  dr65_b[0:10] 
    
    # death_rate_dr70[region] = dr70_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ) ^ dr70_b[region]
        idxlhs = fcol_in_mdf['death_rate_dr70']
        idx1 = fcol_in_mdf['GDPpp_USED_for_influencing_death_rates']
        mdf[rowi, idxlhs:idxlhs + 10] =  dr70_a[0:10]  *  (  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  )  )  **  dr70_b[0:10] 
    
    # death_rate_dr75[region] = dr75_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ) ^ dr75_b[region]
        idxlhs = fcol_in_mdf['death_rate_dr75']
        idx1 = fcol_in_mdf['GDPpp_USED_for_influencing_death_rates']
        mdf[rowi, idxlhs:idxlhs + 10] =  dr75_a[0:10]  *  (  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  )  )  **  dr75_b[0:10] 
    
    # death_rate_dr80[region] = dr80_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ) ^ dr80_b[region]
        idxlhs = fcol_in_mdf['death_rate_dr80']
        idx1 = fcol_in_mdf['GDPpp_USED_for_influencing_death_rates']
        mdf[rowi, idxlhs:idxlhs + 10] =  dr80_a[0:10]  *  (  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  )  )  **  dr80_b[0:10] 
    
    # death_rate_dr85[region] = dr85_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ) ^ dr85_b[region]
        idxlhs = fcol_in_mdf['death_rate_dr85']
        idx1 = fcol_in_mdf['GDPpp_USED_for_influencing_death_rates']
        mdf[rowi, idxlhs:idxlhs + 10] =  dr85_a[0:10]  *  (  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  )  )  **  dr85_b[0:10] 
    
    # death_rate_dr90[region] = dr90_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ) ^ dr90_b[region]
        idxlhs = fcol_in_mdf['death_rate_dr90']
        idx1 = fcol_in_mdf['GDPpp_USED_for_influencing_death_rates']
        mdf[rowi, idxlhs:idxlhs + 10] =  dr90_a[0:10]  *  (  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  )  )  **  dr90_b[0:10] 
    
    # death_rate_dr95_plus[region] = dr95p_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ) ^ dr95p_b[region]
        idxlhs = fcol_in_mdf['death_rate_dr95_plus']
        idx1 = fcol_in_mdf['GDPpp_USED_for_influencing_death_rates']
        mdf[rowi, idxlhs:idxlhs + 10] =  dr95p_a[0:10]  *  (  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  )  )  **  dr95p_b[0:10] 
     
    # Debt_cancelling_pulse[region] = ( ( STEP ( Debt_cancelling_stepheight , Policy_start_year ) - STEP ( Debt_cancelling_stepheight , Policy_start_year + Govt_debt_cancelling_spread[region] ) ) + ( STEP ( Debt_cancelling_stepheight , Round2_start ) - STEP ( Debt_cancelling_stepheight , Round2_start + Govt_debt_cancelling_spread[region] ) ) + ( STEP ( Debt_cancelling_stepheight , Round3_start ) - STEP ( Debt_cancelling_stepheight , Round3_start + Govt_debt_cancelling_spread[region] ) ) ) * ExPS_pol_div_100[region]
        idxlhs = fcol_in_mdf['Debt_cancelling_pulse']
        idx1 = fcol_in_mdf['ExPS_pol_div_100']
        for j in range(0,10):
            mdf[rowi, idxlhs + j] =   (  (  STEP  (  zeit  ,  Debt_cancelling_stepheight  ,  Policy_start_year  )  -  STEP  (  zeit  ,  Debt_cancelling_stepheight  ,  Policy_start_year  +  Govt_debt_cancelling_spread  )  )  +  (  STEP  (  zeit  ,  Debt_cancelling_stepheight  ,  Round2_start  )  -  STEP  (  zeit  ,  Debt_cancelling_stepheight  ,  Round2_start  +  Govt_debt_cancelling_spread  )  )  +  (  STEP  (  zeit  ,  Debt_cancelling_stepheight  ,  Round3_start  )  -  STEP  (  zeit  ,  Debt_cancelling_stepheight  ,  Round3_start  +  Govt_debt_cancelling_spread  )  )  )  * mdf[rowi, idx1 + j]
    
    # Decrease_in_GDPL[region] = Obligation_for_payback_of_debt_from_public_lenders[region] * ( 1 - Fraction_of_public_loans_not_serviced[region] )
        idxlhs = fcol_in_mdf['Decrease_in_GDPL']
        idx1 = fcol_in_mdf['Obligation_for_payback_of_debt_from_public_lenders']
        idx2 = fcol_in_mdf['Fraction_of_public_loans_not_serviced']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  1  - mdf[rowi , idx2:idx2 + 10] ) 
    
    # Decrease_in_public_capacity[region] = Public_capacity[region] / Lifetime_of_public_capacity
        idxlhs = fcol_in_mdf['Decrease_in_public_capacity']
        idx1 = fcol_in_mdf['Public_capacity']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Lifetime_of_public_capacity 
    
    # Decrease_in_public_loan_defaults[region] = Public_loan_defaults[region] / Time_to_write_of_public_loan_defaults
        idxlhs = fcol_in_mdf['Decrease_in_public_loan_defaults']
        idx1 = fcol_in_mdf['Public_loan_defaults']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Time_to_write_of_public_loan_defaults 
    
    # Smoothed_cumulative_N_use_for_regenerative_choice[region] = SMOOTHI ( Cumulative_N_use_since_2020[region] , Time_for_N_use_to_affect_regeneative_choice , Cumulative_N_use_since_2020_in_1980[region] )
        idx1 = fcol_in_mdf['Smoothed_cumulative_N_use_for_regenerative_choice']
        idx2 = fcol_in_mdf['Cumulative_N_use_since_2020']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi - 1, idx1:idx1 + 10]) / Time_for_N_use_to_affect_regeneative_choice * dt
    
    # Desired_regenerative_cropland_fraction[region] = WITH LOOKUP ( Smoothed_cumulative_N_use_for_regenerative_choice[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 0 ) , ( 10 , 0.02 ) , ( 20 , 0.1 ) , ( 30 , 0.5 ) ) )
        tabidx = ftab_in_d_table['Desired_regenerative_cropland_fraction'] # fetch the correct table
        idx2 = fcol_in_mdf['Desired_regenerative_cropland_fraction'] # get the location of the lhs in mdf
        idx3 = fcol_in_mdf['Smoothed_cumulative_N_use_for_regenerative_choice']
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:,0], look[:, 1])
    
    # Too_much_regen_cropland[region] = IF_THEN_ELSE ( Desired_regenerative_cropland_fraction + FLWR_policy - Regenerative_cropland_fraction < 0 , ( Desired_regenerative_cropland_fraction + FLWR_policy - Regenerative_cropland_fraction ) * - 1 , 0 )
        idxlhs = fcol_in_mdf['Too_much_regen_cropland']
        idx1 = fcol_in_mdf['Desired_regenerative_cropland_fraction']
        idx2 = fcol_in_mdf['FLWR_policy']
        idx3 = fcol_in_mdf['Regenerative_cropland_fraction']
        idx4 = fcol_in_mdf['Desired_regenerative_cropland_fraction']
        idx5 = fcol_in_mdf['FLWR_policy']
        idx6 = fcol_in_mdf['Regenerative_cropland_fraction']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  ( mdf[rowi, idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] - mdf[rowi , idx3:idx3 + 10] <  0  ,  ( mdf[rowi, idx4:idx4 + 10] + mdf[rowi , idx5:idx5 + 10] - mdf[rowi , idx6:idx6 + 10] )  *  -  1  ,  0  ) 
    
    # Decrease_in_regen_cropland[region] = Too_much_regen_cropland[region] / Time_to_implement_conventional_practices
        idxlhs = fcol_in_mdf['Decrease_in_regen_cropland']
        idx1 = fcol_in_mdf['Too_much_regen_cropland']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Time_to_implement_conventional_practices 
    
    # decrease_in_speculative_asset_pool[region] = MAX ( 0 , Annual_shortfall_of_available_private_capital[region] )
        idxlhs = fcol_in_mdf['decrease_in_speculative_asset_pool']
        idx1 = fcol_in_mdf['Annual_shortfall_of_available_private_capital']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.maximum  (  0  , mdf[rowi , idx1:idx1 + 10] ) 
    
    # Demand_imbalance[region] = ( Investment_demand[region] + Total_consumption[region] ) / Optimal_real_output[region]
        idxlhs = fcol_in_mdf['Demand_imbalance']
        idx1 = fcol_in_mdf['Investment_demand']
        idx2 = fcol_in_mdf['Total_consumption']
        idx3 = fcol_in_mdf['Optimal_real_output']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] )  / mdf[rowi , idx3:idx3 + 10]
    
    # Depositing_of_C_to_sediment = C_in_deep_water_volume_1km_to_bottom_GtC / Time_to_deposit_C_in_sediment
        idxlhs = fcol_in_mdf['Depositing_of_C_to_sediment']
        idx1 = fcol_in_mdf['C_in_deep_water_volume_1km_to_bottom_GtC']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Time_to_deposit_C_in_sediment 
    
    # Fraction_of_supply_imbalance_to_be_closed_by_imports_after_policy[region] = Reference_fraction_of_supply_imbalance_to_be_closed_by_imports[region] * ( 1 - RIPLGF_policy[region] )
        idxlhs = fcol_in_mdf['Fraction_of_supply_imbalance_to_be_closed_by_imports_after_policy']
        idx1 = fcol_in_mdf['RIPLGF_policy']
        mdf[rowi, idxlhs:idxlhs + 10] =  Reference_fraction_of_supply_imbalance_to_be_closed_by_imports[0:10]  *  (  1  - mdf[rowi , idx1:idx1 + 10] ) 
    
    # Desired_crop_import_indicated[region] = All_crop_regional_dmd_last_year[region] * Ratio_of_demand_to_regional_supply_of_crops[region] * Fraction_of_supply_imbalance_to_be_closed_by_imports_after_policy[region]
        idxlhs = fcol_in_mdf['Desired_crop_import_indicated']
        idx1 = fcol_in_mdf['All_crop_regional_dmd_last_year']
        idx2 = fcol_in_mdf['Ratio_of_demand_to_regional_supply_of_crops']
        idx3 = fcol_in_mdf['Fraction_of_supply_imbalance_to_be_closed_by_imports_after_policy']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] * mdf[rowi , idx3:idx3 + 10]
    
    # Eff_of_dmd_imbalance_on_life_of_capacity[region] = 1 + Slope_of_Eff_of_dmd_imbalnce_on_life_of_capacity * ( Perceived_demand_imblance[region] / Dmd_imbalance_in_1980[region] - 1 )
        idxlhs = fcol_in_mdf['Eff_of_dmd_imbalance_on_life_of_capacity']
        idx1 = fcol_in_mdf['Perceived_demand_imblance']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  +  Slope_of_Eff_of_dmd_imbalnce_on_life_of_capacity  *  ( mdf[rowi , idx1:idx1 + 10] /  Dmd_imbalance_in_1980  -  1  ) 
    
    # Lifetime_of_capacity[region] = Lifetime_of_capacity_in_1980 / Eff_of_dmd_imbalance_on_life_of_capacity[region]
        idxlhs = fcol_in_mdf['Lifetime_of_capacity']
        idx1 = fcol_in_mdf['Eff_of_dmd_imbalance_on_life_of_capacity']
        mdf[rowi, idxlhs:idxlhs + 10] =  Lifetime_of_capacity_in_1980  / mdf[rowi , idx1:idx1 + 10]
    
    # Discarding_capacity[region] = Capacity[region] / Lifetime_of_capacity[region]
        idxlhs = fcol_in_mdf['Discarding_capacity']
        idx1 = fcol_in_mdf['Capacity']
        idx2 = fcol_in_mdf['Lifetime_of_capacity']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # dying_35_to_39[region] = Cohort_35_to_39[region] * death_rate_dr35[region] * Eff_of_env_damage_on_dying[region] * Inequality_effect_on_mortality[region] * Effect_of_malnutrition_on_dying_smoothed[region]
        idxlhs = fcol_in_mdf['dying_35_to_39']
        idx1 = fcol_in_mdf['Cohort_35_to_39']
        idx2 = fcol_in_mdf['death_rate_dr35']
        idx3 = fcol_in_mdf['Eff_of_env_damage_on_dying']
        idx4 = fcol_in_mdf['Inequality_effect_on_mortality']
        idx5 = fcol_in_mdf['Effect_of_malnutrition_on_dying_smoothed']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] * mdf[rowi , idx3:idx3 + 10] * mdf[rowi , idx4:idx4 + 10] * mdf[rowi , idx5:idx5 + 10]
    
    # dying_40_to_45[region] = Cohort_40_to_44[region] * death_rate_dr40[region] * Eff_of_env_damage_on_dying[region] * Inequality_effect_on_mortality[region] * Effect_of_malnutrition_on_dying_smoothed[region]
        idxlhs = fcol_in_mdf['dying_40_to_45']
        idx1 = fcol_in_mdf['Cohort_40_to_44']
        idx2 = fcol_in_mdf['death_rate_dr40']
        idx3 = fcol_in_mdf['Eff_of_env_damage_on_dying']
        idx4 = fcol_in_mdf['Inequality_effect_on_mortality']
        idx5 = fcol_in_mdf['Effect_of_malnutrition_on_dying_smoothed']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] * mdf[rowi , idx3:idx3 + 10] * mdf[rowi , idx4:idx4 + 10] * mdf[rowi , idx5:idx5 + 10]
    
    # dying_50_to_54[region] = Cohort_50_to_54[region] * death_rate_dr50[region] * Eff_of_env_damage_on_dying[region] * Inequality_effect_on_mortality[region] * Effect_of_malnutrition_on_dying_smoothed[region]
        idxlhs = fcol_in_mdf['dying_50_to_54']
        idx1 = fcol_in_mdf['Cohort_50_to_54']
        idx2 = fcol_in_mdf['death_rate_dr50']
        idx3 = fcol_in_mdf['Eff_of_env_damage_on_dying']
        idx4 = fcol_in_mdf['Inequality_effect_on_mortality']
        idx5 = fcol_in_mdf['Effect_of_malnutrition_on_dying_smoothed']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] * mdf[rowi , idx3:idx3 + 10] * mdf[rowi , idx4:idx4 + 10] * mdf[rowi , idx5:idx5 + 10]
    
    # dying_55_to_59[region] = Cohort_55_to_59[region] * death_rate_dr55[region] * Eff_of_env_damage_on_dying[region] * Inequality_effect_on_mortality[region] * Effect_of_malnutrition_on_dying_smoothed[region]
        idxlhs = fcol_in_mdf['dying_55_to_59']
        idx1 = fcol_in_mdf['Cohort_55_to_59']
        idx2 = fcol_in_mdf['death_rate_dr55']
        idx3 = fcol_in_mdf['Eff_of_env_damage_on_dying']
        idx4 = fcol_in_mdf['Inequality_effect_on_mortality']
        idx5 = fcol_in_mdf['Effect_of_malnutrition_on_dying_smoothed']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] * mdf[rowi , idx3:idx3 + 10] * mdf[rowi , idx4:idx4 + 10] * mdf[rowi , idx5:idx5 + 10]
    
    # dying_60_to_64[region] = Cohort_60_to_64[region] * death_rate_dr60[region] * Eff_of_env_damage_on_dying[region] * Inequality_effect_on_mortality[region] * Effect_of_malnutrition_on_dying_smoothed[region]
        idxlhs = fcol_in_mdf['dying_60_to_64']
        idx1 = fcol_in_mdf['Cohort_60_to_64']
        idx2 = fcol_in_mdf['death_rate_dr60']
        idx3 = fcol_in_mdf['Eff_of_env_damage_on_dying']
        idx4 = fcol_in_mdf['Inequality_effect_on_mortality']
        idx5 = fcol_in_mdf['Effect_of_malnutrition_on_dying_smoothed']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] * mdf[rowi , idx3:idx3 + 10] * mdf[rowi , idx4:idx4 + 10] * mdf[rowi , idx5:idx5 + 10]
    
    # dying_65_to_69[region] = Cohort_65_to_69[region] * death_rate_dr65[region] * Eff_of_env_damage_on_dying[region] * Inequality_effect_on_mortality[region] * Effect_of_malnutrition_on_dying_smoothed[region]
        idxlhs = fcol_in_mdf['dying_65_to_69']
        idx1 = fcol_in_mdf['Cohort_65_to_69']
        idx2 = fcol_in_mdf['death_rate_dr65']
        idx3 = fcol_in_mdf['Eff_of_env_damage_on_dying']
        idx4 = fcol_in_mdf['Inequality_effect_on_mortality']
        idx5 = fcol_in_mdf['Effect_of_malnutrition_on_dying_smoothed']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] * mdf[rowi , idx3:idx3 + 10] * mdf[rowi , idx4:idx4 + 10] * mdf[rowi , idx5:idx5 + 10]
    
    # dying_70_to_74[region] = Cohort_70_to_74[region] * death_rate_dr70[region] * Eff_of_env_damage_on_dying[region] * Inequality_effect_on_mortality[region] * Effect_of_malnutrition_on_dying_smoothed[region]
        idxlhs = fcol_in_mdf['dying_70_to_74']
        idx1 = fcol_in_mdf['Cohort_70_to_74']
        idx2 = fcol_in_mdf['death_rate_dr70']
        idx3 = fcol_in_mdf['Eff_of_env_damage_on_dying']
        idx4 = fcol_in_mdf['Inequality_effect_on_mortality']
        idx5 = fcol_in_mdf['Effect_of_malnutrition_on_dying_smoothed']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] * mdf[rowi , idx3:idx3 + 10] * mdf[rowi , idx4:idx4 + 10] * mdf[rowi , idx5:idx5 + 10]
    
    # dying_75_to_79[region] = Cohort_75_to_79[region] * death_rate_dr75[region] * Eff_of_env_damage_on_dying[region] * Effect_of_malnutrition_on_dying_smoothed[region] * Effect_of_poverty_on_dying_smoothed[region] * Inequality_effect_on_mortality[region]
        idxlhs = fcol_in_mdf['dying_75_to_79']
        idx1 = fcol_in_mdf['Cohort_75_to_79']
        idx2 = fcol_in_mdf['death_rate_dr75']
        idx3 = fcol_in_mdf['Eff_of_env_damage_on_dying']
        idx4 = fcol_in_mdf['Effect_of_malnutrition_on_dying_smoothed']
        idx5 = fcol_in_mdf['Effect_of_poverty_on_dying_smoothed']
        idx6 = fcol_in_mdf['Inequality_effect_on_mortality']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] * mdf[rowi , idx3:idx3 + 10] * mdf[rowi , idx4:idx4 + 10] * mdf[rowi , idx5:idx5 + 10] * mdf[rowi , idx6:idx6 + 10]
    
    # dying_80_to_84[region] = Cohort_80_to_84[region] * death_rate_dr80[region] * mort_80_to_84_adjust_factor[region] * Eff_of_env_damage_on_dying[region] * Effect_of_malnutrition_on_dying_smoothed[region] * Effect_of_poverty_on_dying_smoothed[region] * Inequality_effect_on_mortality[region]
        idxlhs = fcol_in_mdf['dying_80_to_84']
        idx1 = fcol_in_mdf['Cohort_80_to_84']
        idx2 = fcol_in_mdf['death_rate_dr80']
        idx3 = fcol_in_mdf['Eff_of_env_damage_on_dying']
        idx4 = fcol_in_mdf['Effect_of_malnutrition_on_dying_smoothed']
        idx5 = fcol_in_mdf['Effect_of_poverty_on_dying_smoothed']
        idx6 = fcol_in_mdf['Inequality_effect_on_mortality']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] *  mort_80_to_84_adjust_factor[0:10]  * mdf[rowi , idx3:idx3 + 10] * mdf[rowi , idx4:idx4 + 10] * mdf[rowi , idx5:idx5 + 10] * mdf[rowi , idx6:idx6 + 10]
    
    # dying_85_to_89[region] = Cohort_85_to_89[region] * death_rate_dr85[region] * mort_85_to_89_adjust_factor[region] * Eff_of_env_damage_on_dying[region] * Effect_of_malnutrition_on_dying_smoothed[region] * Effect_of_poverty_on_dying_smoothed[region] * Inequality_effect_on_mortality[region]
        idxlhs = fcol_in_mdf['dying_85_to_89']
        idx1 = fcol_in_mdf['Cohort_85_to_89']
        idx2 = fcol_in_mdf['death_rate_dr85']
        idx3 = fcol_in_mdf['Eff_of_env_damage_on_dying']
        idx4 = fcol_in_mdf['Effect_of_malnutrition_on_dying_smoothed']
        idx5 = fcol_in_mdf['Effect_of_poverty_on_dying_smoothed']
        idx6 = fcol_in_mdf['Inequality_effect_on_mortality']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] *  mort_85_to_89_adjust_factor[0:10]  * mdf[rowi , idx3:idx3 + 10] * mdf[rowi , idx4:idx4 + 10] * mdf[rowi , idx5:idx5 + 10] * mdf[rowi , idx6:idx6 + 10]
    
    # dying_90_to_94[region] = Cohort_90_to_94[region] * death_rate_dr90[region] * mort_90_to_94_adjust_factor[region] * Eff_of_env_damage_on_dying[region] * Effect_of_malnutrition_on_dying_smoothed[region] * Effect_of_poverty_on_dying_smoothed[region] * Inequality_effect_on_mortality[region]
        idxlhs = fcol_in_mdf['dying_90_to_94']
        idx1 = fcol_in_mdf['Cohort_90_to_94']
        idx2 = fcol_in_mdf['death_rate_dr90']
        idx3 = fcol_in_mdf['Eff_of_env_damage_on_dying']
        idx4 = fcol_in_mdf['Effect_of_malnutrition_on_dying_smoothed']
        idx5 = fcol_in_mdf['Effect_of_poverty_on_dying_smoothed']
        idx6 = fcol_in_mdf['Inequality_effect_on_mortality']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] *  mort_90_to_94_adjust_factor[0:10]  * mdf[rowi , idx3:idx3 + 10] * mdf[rowi , idx4:idx4 + 10] * mdf[rowi , idx5:idx5 + 10] * mdf[rowi , idx6:idx6 + 10]
    
    # dying_95p[region] = Cohort_95p[region] * death_rate_dr95_plus[region] * mort_95plus_adjust_factor[region] * Eff_of_env_damage_on_dying[region] * Effect_of_malnutrition_on_dying_smoothed[region] * Effect_of_poverty_on_dying_smoothed[region] * Inequality_effect_on_mortality[region]
        idxlhs = fcol_in_mdf['dying_95p']
        idx1 = fcol_in_mdf['Cohort_95p']
        idx2 = fcol_in_mdf['death_rate_dr95_plus']
        idx3 = fcol_in_mdf['Eff_of_env_damage_on_dying']
        idx4 = fcol_in_mdf['Effect_of_malnutrition_on_dying_smoothed']
        idx5 = fcol_in_mdf['Effect_of_poverty_on_dying_smoothed']
        idx6 = fcol_in_mdf['Inequality_effect_on_mortality']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] *  mort_95plus_adjust_factor[0:10]  * mdf[rowi , idx3:idx3 + 10] * mdf[rowi , idx4:idx4 + 10] * mdf[rowi , idx5:idx5 + 10] * mdf[rowi , idx6:idx6 + 10]
    
    # dying[region] = dying_0_to_4[region] + dying_35_to_39[region] + dying_40_to_45[region] + dying_50_to_54[region] + dying_55_to_59[region] + dying_60_to_64[region] + dying_65_to_69[region] + dying_70_to_74[region] + dying_75_to_79[region] + dying_80_to_84[region] + dying_85_to_89[region] + dying_90_to_94[region] + dying_95p[region]
        idxlhs = fcol_in_mdf['dying']
        idx1 = fcol_in_mdf['dying_0_to_4']
        idx2 = fcol_in_mdf['dying_35_to_39']
        idx3 = fcol_in_mdf['dying_40_to_45']
        idx4 = fcol_in_mdf['dying_50_to_54']
        idx5 = fcol_in_mdf['dying_55_to_59']
        idx6 = fcol_in_mdf['dying_60_to_64']
        idx7 = fcol_in_mdf['dying_65_to_69']
        idx8 = fcol_in_mdf['dying_70_to_74']
        idx9 = fcol_in_mdf['dying_75_to_79']
        idx10 = fcol_in_mdf['dying_80_to_84']
        idx11 = fcol_in_mdf['dying_85_to_89']
        idx12 = fcol_in_mdf['dying_90_to_94']
        idx13 = fcol_in_mdf['dying_95p']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] + mdf[rowi , idx4:idx4 + 10] + mdf[rowi , idx5:idx5 + 10] + mdf[rowi , idx6:idx6 + 10] + mdf[rowi , idx7:idx7 + 10] + mdf[rowi , idx8:idx8 + 10] + mdf[rowi , idx9:idx9 + 10] + mdf[rowi , idx10:idx10 + 10] + mdf[rowi , idx11:idx11 + 10] + mdf[rowi , idx12:idx12 + 10] + mdf[rowi , idx13:idx13 + 10]
    
    # dying_45_to_49[region] = Cohort_45_to_49[region] * death_rate_dr45[region] * Eff_of_env_damage_on_dying[region] * Inequality_effect_on_mortality[region] * Effect_of_malnutrition_on_dying_smoothed[region]
        idxlhs = fcol_in_mdf['dying_45_to_49']
        idx1 = fcol_in_mdf['Cohort_45_to_49']
        idx2 = fcol_in_mdf['death_rate_dr45']
        idx3 = fcol_in_mdf['Eff_of_env_damage_on_dying']
        idx4 = fcol_in_mdf['Inequality_effect_on_mortality']
        idx5 = fcol_in_mdf['Effect_of_malnutrition_on_dying_smoothed']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] * mdf[rowi , idx3:idx3 + 10] * mdf[rowi , idx4:idx4 + 10] * mdf[rowi , idx5:idx5 + 10]
    
    # Each_region_max_cost_estimate_all_TAs_PES_0[region] = Each_region_max_cost_estimate_empowerment_PES_with_env_dam_and_reform[region] + Each_region_max_cost_estimate_energy_PES_with_env_dam_and_reform[region] + Each_region_max_cost_estimate_food_PES_with_env_dam_and_reform[region] + Each_region_max_cost_estimate_inequality_PES_with_env_dam_and_reform[region] + Each_region_max_cost_estimate_poverty_PES_with_env_dam_and_reform[region]
        idxlhs = fcol_in_mdf['Each_region_max_cost_estimate_all_TAs_PES_0']
        idx1 = fcol_in_mdf['Each_region_max_cost_estimate_empowerment_PES_with_env_dam_and_reform']
        idx2 = fcol_in_mdf['Each_region_max_cost_estimate_energy_PES_with_env_dam_and_reform']
        idx3 = fcol_in_mdf['Each_region_max_cost_estimate_food_PES_with_env_dam_and_reform']
        idx4 = fcol_in_mdf['Each_region_max_cost_estimate_inequality_PES_with_env_dam_and_reform']
        idx5 = fcol_in_mdf['Each_region_max_cost_estimate_poverty_PES_with_env_dam_and_reform']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] + mdf[rowi , idx4:idx4 + 10] + mdf[rowi , idx5:idx5 + 10]
    
    # Eff_of_env_damage_on_TFP[region] = np.exp ( Combined_env_damage_indicator * expSoE_of_ed_on_TFP ) / Actual_eff_of_relative_wealth_on_env_damage[region]
        idxlhs = fcol_in_mdf['Eff_of_env_damage_on_TFP']
        idx1 = fcol_in_mdf['Combined_env_damage_indicator']
        idx2 = fcol_in_mdf['Actual_eff_of_relative_wealth_on_env_damage']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.exp  ( mdf[rowi , idx1] *  expSoE_of_ed_on_TFP  )  / mdf[rowi , idx2:idx2 + 10]
    
    # Eff_of_wealth_on_regnerative_practices[region] = WITH LOOKUP ( GDPpp_USED[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 0 ) , ( 60 , 0.9 ) ) )
        tabidx = ftab_in_d_table['Eff_of_wealth_on_regnerative_practices'] # fetch the correct table
        idx2 = fcol_in_mdf['Eff_of_wealth_on_regnerative_practices'] # get the location of the lhs in mdf
        idx3 = fcol_in_mdf['GDPpp_USED']
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:,0], look[:, 1])
    
    # TFP_including_effect_of_env_damage[region] = Total_factor_productivity_TFP_before_env_damage[region] / Eff_of_env_damage_on_TFP[region]
        idxlhs = fcol_in_mdf['TFP_including_effect_of_env_damage']
        idx1 = fcol_in_mdf['Total_factor_productivity_TFP_before_env_damage']
        idx2 = fcol_in_mdf['Eff_of_env_damage_on_TFP']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # Indicated_TFP[region] = TFP_including_effect_of_env_damage[region]
        idxlhs = fcol_in_mdf['Indicated_TFP']
        idx1 = fcol_in_mdf['TFP_including_effect_of_env_damage']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10]
    
    # Effect_of_capacity_renewal[region] = ( Indicated_TFP[region] - Embedded_TFP[region] ) * Capacity_renewal_rate[region]
        idxlhs = fcol_in_mdf['Effect_of_capacity_renewal']
        idx1 = fcol_in_mdf['Indicated_TFP']
        idx2 = fcol_in_mdf['Embedded_TFP']
        idx3 = fcol_in_mdf['Capacity_renewal_rate']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10] )  * mdf[rowi , idx3:idx3 + 10]
    
    # Effect_of_GL_on_freshwater_use = WITH LOOKUP ( Which_Scenario_is_run_globally , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 1 ) , ( 0.25 , 0.97 ) , ( 0.5 , 0.9 ) , ( 0.75 , 0.8 ) , ( 1 , 0.66 ) ) )
        tabidx = ftab_in_d_table['Effect_of_GL_on_freshwater_use'] # fetch the correct table
        idxlhs = fcol_in_mdf['Effect_of_GL_on_freshwater_use'] # get the location of the lhs in mdf
        idx1 = fcol_in_mdf['Which_Scenario_is_run_globally']
        look = d_table[tabidx]
        valgt = GRAPH(mdf[rowi,  idx1], look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # Effect_of_GL_on_phaseout_time = WITH LOOKUP ( Which_Scenario_is_run_globally , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 1 ) , ( 0.25 , 0.97 ) , ( 0.5 , 0.9 ) , ( 0.75 , 0.5 ) , ( 1 , 0.33 ) ) )
        tabidx = ftab_in_d_table['Effect_of_GL_on_phaseout_time'] # fetch the correct table
        idxlhs = fcol_in_mdf['Effect_of_GL_on_phaseout_time'] # get the location of the lhs in mdf
        idx1 = fcol_in_mdf['Which_Scenario_is_run_globally']
        look = d_table[tabidx]
        valgt = GRAPH(mdf[rowi,  idx1], look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # Effect_of_humidity_on_shifting_biomes = 1 + Sensitivity_of_trop_to_humidity * ( Humidity_of_atmosphere / Humidity_of_atmosphere_in_1850_g_p_kg - 1 )
        idxlhs = fcol_in_mdf['Effect_of_humidity_on_shifting_biomes']
        idx1 = fcol_in_mdf['Humidity_of_atmosphere']
        mdf[rowi, idxlhs] =  1  +  Sensitivity_of_trop_to_humidity  *  ( mdf[rowi, idx1] /  Humidity_of_atmosphere_in_1850_g_p_kg  -  1  ) 
    
    # Effect_of_poverty_on_social_tension[region] = WITH LOOKUP ( Fraction_of_population_below_existential_minimum[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 1 ) , ( 0.1 , 0.7 ) , ( 0.25 , 0.4 ) , ( 0.5 , 0.2 ) , ( 0.75 , 0.15 ) , ( 1 , 0.1 ) ) )
        tabidx = ftab_in_d_table['Effect_of_poverty_on_social_tension'] # fetch the correct table
        idx2 = fcol_in_mdf['Effect_of_poverty_on_social_tension'] # get the location of the lhs in mdf
        idx3 = fcol_in_mdf['Fraction_of_population_below_existential_minimum']
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:,0], look[:, 1])
    
    # Worker_to_owner_income_after_tax_ratio[region] = Worker_income_after_tax[region] / Owner_income_after_tax_but_before_lending_transactions[region]
        idxlhs = fcol_in_mdf['Worker_to_owner_income_after_tax_ratio']
        idx1 = fcol_in_mdf['Worker_income_after_tax']
        idx2 = fcol_in_mdf['Owner_income_after_tax_but_before_lending_transactions']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # Worker_to_owner_income_after_tax_ratio_scaled_to_init[region] = Worker_to_owner_income_after_tax_ratio[region] / Worker_to_owner_income_after_tax_ratio_in_1980[region]
        idxlhs = fcol_in_mdf['Worker_to_owner_income_after_tax_ratio_scaled_to_init']
        idx1 = fcol_in_mdf['Worker_to_owner_income_after_tax_ratio']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Worker_to_owner_income_after_tax_ratio_in_1980[0:10] 
    
    # Effect_of_Worker_to_owner_income_after_tax_ratio_scaled_to_init[region] = 1 + Strength_of_effect_of_income_ratio_after_tax * ( Worker_to_owner_income_after_tax_ratio_scaled_to_init[region] - 1 )
        idxlhs = fcol_in_mdf['Effect_of_Worker_to_owner_income_after_tax_ratio_scaled_to_init']
        idx1 = fcol_in_mdf['Worker_to_owner_income_after_tax_ratio_scaled_to_init']
        mdf[rowi, idxlhs:idxlhs + 10] =  1  +  Strength_of_effect_of_income_ratio_after_tax  *  ( mdf[rowi , idx1:idx1 + 10] -  1  ) 
    
    # Effective_GDPpp_for_OSF[region] = SMOOTH ( GDPpp_USED[region] , Time_for_GDPpp_to_affect_owner_saving_fraction )
        idx1 = fcol_in_mdf['Effective_GDPpp_for_OSF']
        idx2 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1+10] + ( mdf[rowi-1 , idx2:idx2 + 10] - mdf[rowi -1 , idx1:idx1 + 10]) / Time_for_GDPpp_to_affect_owner_saving_fraction * dt
    
    # TROP_deforestation_cutoff_effect = WITH LOOKUP ( TROP_deforested_as_pct_of_potential_area , ( [ ( 0.5 , 0 ) - ( 0.8 , 10 ) ] , ( 0.5 , 1 ) , ( 0.619266 , 1.92982 ) , ( 0.683486 , 2.7193 ) , ( 0.733028 , 4.03509 ) , ( 0.76055 , 5.26316 ) , ( 0.783486 , 6.84211 ) , ( 0.8 , 10 ) ) )
        tabidx = ftab_in_d_table['TROP_deforestation_cutoff_effect'] # fetch the correct table
        idxlhs = fcol_in_mdf['TROP_deforestation_cutoff_effect'] # get the location of the lhs in mdf
        idx1 = fcol_in_mdf['TROP_deforested_as_pct_of_potential_area']
        look = d_table[tabidx]
        valgt = GRAPH(mdf[rowi,  idx1], look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # Effective_Time_to_regrow_TROP_after_deforesting = Reference_Time_to_regrow_TROP_after_deforesting / TROP_deforestation_cutoff_effect
        idxlhs = fcol_in_mdf['Effective_Time_to_regrow_TROP_after_deforesting']
        idx1 = fcol_in_mdf['TROP_deforestation_cutoff_effect']
        mdf[rowi, idxlhs] =  Reference_Time_to_regrow_TROP_after_deforesting  / mdf[rowi, idx1]
    
    # Labor_pool[region] = Employed[region] + Unemployed[region]
        idxlhs = fcol_in_mdf['Labor_pool']
        idx1 = fcol_in_mdf['Employed']
        idx2 = fcol_in_mdf['Unemployed']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10]
    
    # Employed_to_labor_pool_ratio[region] = Employed[region] / Labor_pool[region]
        idxlhs = fcol_in_mdf['Employed_to_labor_pool_ratio']
        idx1 = fcol_in_mdf['Employed']
        idx2 = fcol_in_mdf['Labor_pool']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # Energy_intensity_kWh_per_usd[region] = ( El_from_all_sources[region] + ( Fossil_fuel_for_NON_El_use_that_IS_NOT_being_electrified[region] + Fossil_fuel_for_NON_El_use_that_CANNOT_be_electrified[region] ) * Conversion_Mtoe_to_TWh[region] * 3 ) / GDP_USED[region]
        idxlhs = fcol_in_mdf['Energy_intensity_kWh_per_usd']
        idx1 = fcol_in_mdf['El_from_all_sources']
        idx2 = fcol_in_mdf['Fossil_fuel_for_NON_El_use_that_IS_NOT_being_electrified']
        idx3 = fcol_in_mdf['Fossil_fuel_for_NON_El_use_that_CANNOT_be_electrified']
        idx4 = fcol_in_mdf['GDP_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] +  ( mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] )  *  Conversion_Mtoe_to_TWh[0:10]  *  3  )  / mdf[rowi , idx4:idx4 + 10]
    
    # Labor_market_imbalance[region] = Labor_pool[region] / Max_people_in_labour_pool[region]
        idxlhs = fcol_in_mdf['Labor_market_imbalance']
        idx1 = fcol_in_mdf['Labor_pool']
        idx2 = fcol_in_mdf['Max_people_in_labour_pool']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # Limitation_on_entering_the_pool_from_market_imbalance[region] = WITH LOOKUP ( Labor_market_imbalance[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0.7 , 1 ) , ( 0.75 , 0.97 ) , ( 0.8 , 0.9 ) , ( 0.85 , 0.8 ) , ( 0.9 , 0.65 ) , ( 0.95 , 0.4 ) , ( 1 , 0.02 ) ) )
        tabidx = ftab_in_d_table['Limitation_on_entering_the_pool_from_market_imbalance'] # fetch the correct table
        idx2 = fcol_in_mdf['Limitation_on_entering_the_pool_from_market_imbalance'] # get the location of the lhs in mdf
        idx3 = fcol_in_mdf['Labor_market_imbalance']
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:,0], look[:, 1])
    
    # Entering_the_labor_pool[region] = ( People_considering_entering_the_pool[region] / Time_to_implement_actually_entering_the_pool ) * Limitation_on_entering_the_pool_from_market_imbalance[region]
        idxlhs = fcol_in_mdf['Entering_the_labor_pool']
        idx1 = fcol_in_mdf['People_considering_entering_the_pool']
        idx2 = fcol_in_mdf['Limitation_on_entering_the_pool_from_market_imbalance']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] /  Time_to_implement_actually_entering_the_pool  )  * mdf[rowi, idx2:idx2 + 10]
    
    # Evaporation_aka_latent_heat_flow = Evaporation_as_f_of_temp
        idxlhs = fcol_in_mdf['Evaporation_aka_latent_heat_flow']
        idx1 = fcol_in_mdf['Evaporation_as_f_of_temp']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # Max_forest_cut_after_policy[region] = Forest_land[region] * Reference_max_fraction_of_forest_possible_to_cut
        idxlhs = fcol_in_mdf['Max_forest_cut_after_policy']
        idx1 = fcol_in_mdf['Forest_land']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  Reference_max_fraction_of_forest_possible_to_cut 
    
    # Fraction_of_cropland_gap_closed_by_cutting_forests[us] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0 ) , ( 2000 , - 0.1 ) , ( 2010 , - 0.1 ) , ( 2020 , 0 ) , ( 2030 , 0 ) , ( 2050 , 0 ) , ( 2100 , 0 ) ) ) Fraction_of_cropland_gap_closed_by_cutting_forests[af] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.05 ) , ( 1990 , 0.02 ) , ( 2000 , 0 ) , ( 2010 , 0.03 ) , ( 2020 , 0 ) , ( 2030 , 0 ) , ( 2050 , 0.001 ) , ( 2100 , 0.01 ) ) ) Fraction_of_cropland_gap_closed_by_cutting_forests[cn] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.03 ) , ( 1990 , 0.02 ) , ( 2000 , 0 ) , ( 2010 , 0 ) , ( 2020 , 0 ) , ( 2030 , 0.0003 ) , ( 2050 , 0.001 ) , ( 2100 , 0.002 ) ) ) Fraction_of_cropland_gap_closed_by_cutting_forests[me] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0.03 ) , ( 2000 , 0.01 ) , ( 2010 , 0.01 ) , ( 2020 , 0.01 ) , ( 2030 , 0.01 ) , ( 2050 , 0.01 ) , ( 2100 , 0.01 ) ) ) Fraction_of_cropland_gap_closed_by_cutting_forests[sa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0.02 ) , ( 2000 , 0 ) , ( 2010 , 0.03 ) , ( 2020 , 0 ) , ( 2030 , 0.0003 ) , ( 2050 , 0.001 ) , ( 2100 , 0.001 ) ) ) Fraction_of_cropland_gap_closed_by_cutting_forests[la] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0.03 ) , ( 2000 , 0.01 ) , ( 2010 , 0.01 ) , ( 2020 , 0.01 ) , ( 2030 , 0.0107 ) , ( 2050 , 0.012 ) , ( 2100 , 0.015 ) ) ) Fraction_of_cropland_gap_closed_by_cutting_forests[pa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0 ) , ( 2000 , 0 ) , ( 2010 , 0 ) , ( 2020 , 0 ) , ( 2030 , 0 ) , ( 2050 , 0 ) , ( 2100 , 0 ) ) ) Fraction_of_cropland_gap_closed_by_cutting_forests[ec] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0 ) , ( 2000 , - 0.1 ) , ( 2010 , 0 ) , ( 2020 , 0 ) , ( 2030 , 0.000161 ) , ( 2050 , 0.001 ) , ( 2100 , 0.002 ) ) ) Fraction_of_cropland_gap_closed_by_cutting_forests[eu] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0 ) , ( 2000 , - 0.1 ) , ( 2010 , - 0.1 ) , ( 2020 , 0 ) , ( 2031 , 0 ) , ( 2050 , - 0.001 ) , ( 2100 , - 0.002 ) ) ) Fraction_of_cropland_gap_closed_by_cutting_forests[se] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0.02 ) , ( 2000 , 0 ) , ( 2010 , 0.03 ) , ( 2020 , 0 ) , ( 2030 , 0.00036 ) , ( 2050 , 0.001 ) , ( 2100 , 0.002 ) ) )
        tabidx = ftab_in_d_table['Fraction_of_cropland_gap_closed_by_cutting_forests'] # fetch the correct table
        idx2 = fcol_in_mdf['Fraction_of_cropland_gap_closed_by_cutting_forests'] # get the location of the lhs in mdf
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(zeit, look[:,0], look[:, j + 1])
    
    # fa_to_c[region] = MIN ( Max_forest_cut_after_policy[region] , MIN ( Forest_land[region] , MAX ( 0 , Cropland_gap[region] ) ) * Fraction_of_cropland_gap_closed_by_cutting_forests[region] )
        idxlhs = fcol_in_mdf['fa_to_c']
        idx1 = fcol_in_mdf['Max_forest_cut_after_policy']
        idx2 = fcol_in_mdf['Forest_land']
        idx3 = fcol_in_mdf['Cropland_gap']
        idx4 = fcol_in_mdf['Fraction_of_cropland_gap_closed_by_cutting_forests']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.minimum  ( mdf[rowi , idx1:idx1 + 10] ,  np.minimum  ( mdf[rowi , idx2:idx2 + 10] ,  np.maximum  (  0  , mdf[rowi , idx3:idx3 + 10] )  )  * mdf[rowi, idx4:idx4 + 10] ) 
    
    # Fraction_of_grazing_land_gap_closed_by_cutting_forests[us] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 1 ) , ( 2000 , 1 ) , ( 2010 , 1 ) , ( 2020 , 1 ) , ( 2030 , 1 ) , ( 2050 , 1 ) , ( 2075 , 1 ) , ( 2100 , 1 ) ) ) Fraction_of_grazing_land_gap_closed_by_cutting_forests[af] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 1 ) , ( 2000 , 1 ) , ( 2010 , 0 ) , ( 2020 , 0 ) , ( 2030 , 0 ) , ( 2050 , 0 ) , ( 2075 , 0 ) , ( 2100 , 0 ) ) ) Fraction_of_grazing_land_gap_closed_by_cutting_forests[cn] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 1 ) , ( 2000 , 1 ) , ( 2010 , 0 ) , ( 2020 , 0 ) , ( 2030 , 0 ) , ( 2050 , 0 ) , ( 2075 , 0 ) , ( 2100 , 0 ) ) ) Fraction_of_grazing_land_gap_closed_by_cutting_forests[me] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 1 ) , ( 2000 , 1 ) , ( 2010 , 1 ) , ( 2020 , 1 ) , ( 2030 , 1 ) , ( 2050 , 1 ) , ( 2075 , 1 ) , ( 2100 , 1 ) ) ) Fraction_of_grazing_land_gap_closed_by_cutting_forests[sa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 1 ) , ( 2000 , 1 ) , ( 2010 , 0 ) , ( 2020 , 0 ) , ( 2030 , 0 ) , ( 2050 , 0 ) , ( 2075 , 0 ) , ( 2100 , 0 ) ) ) Fraction_of_grazing_land_gap_closed_by_cutting_forests[la] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 1 ) , ( 2000 , 1 ) , ( 2010 , 1 ) , ( 2020 , 1 ) , ( 2030 , 1 ) , ( 2050 , 1 ) , ( 2075 , 1 ) , ( 2100 , 1 ) ) ) Fraction_of_grazing_land_gap_closed_by_cutting_forests[pa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 1 ) , ( 2000 , 1 ) , ( 2010 , 0 ) , ( 2020 , 0 ) , ( 2030 , 0 ) , ( 2050 , 0 ) , ( 2075 , 0 ) , ( 2100 , 0 ) ) ) Fraction_of_grazing_land_gap_closed_by_cutting_forests[ec] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 1 ) , ( 2000 , 1 ) , ( 2010 , 1 ) , ( 2020 , 1 ) , ( 2030 , 1 ) , ( 2050 , 1 ) , ( 2075 , 1 ) , ( 2100 , 1 ) ) ) Fraction_of_grazing_land_gap_closed_by_cutting_forests[eu] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 1 ) , ( 2000 , 1 ) , ( 2010 , 1 ) , ( 2020 , 1 ) , ( 2030 , 1 ) , ( 2050 , 1 ) , ( 2075 , 1 ) , ( 2100 , 1 ) ) ) Fraction_of_grazing_land_gap_closed_by_cutting_forests[se] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 1 ) , ( 2000 , 1 ) , ( 2010 , 0 ) , ( 2020 , 0 ) , ( 2030 , 0 ) , ( 2050 , 0 ) , ( 2075 , 0 ) , ( 2100 , 0 ) ) )
        tabidx = ftab_in_d_table['Fraction_of_grazing_land_gap_closed_by_cutting_forests'] # fetch the correct table
        idx2 = fcol_in_mdf['Fraction_of_grazing_land_gap_closed_by_cutting_forests'] # get the location of the lhs in mdf
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(zeit, look[:,0], look[:, j + 1])
    
    # fa_to_gl[region] = MIN ( Max_forest_cut_after_policy[region] , MIN ( Forest_land[region] , MAX ( 0 , Grazing_land_gap[region] ) ) * Fraction_of_grazing_land_gap_closed_by_cutting_forests[region] )
        idxlhs = fcol_in_mdf['fa_to_gl']
        idx1 = fcol_in_mdf['Max_forest_cut_after_policy']
        idx2 = fcol_in_mdf['Forest_land']
        idx3 = fcol_in_mdf['Grazing_land_gap']
        idx4 = fcol_in_mdf['Fraction_of_grazing_land_gap_closed_by_cutting_forests']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.minimum  ( mdf[rowi , idx1:idx1 + 10] ,  np.minimum  ( mdf[rowi , idx2:idx2 + 10] ,  np.maximum  (  0  , mdf[rowi , idx3:idx3 + 10] )  )  * mdf[rowi, idx4:idx4 + 10] ) 
    
    # Flow_from_atm_to_biomass = CO2_flux_from_atm_to_GRASS_for_new_growth_GtC_py + CO2_flux_from_atm_to_NF_for_new_growth_GtC_py + CO2_flux_from_atm_to_TROP_for_new_growth_GtC_py + CO2_flux_from_atm_to_TUNDRA_for_new_growth
        idxlhs = fcol_in_mdf['Flow_from_atm_to_biomass']
        idx1 = fcol_in_mdf['CO2_flux_from_atm_to_GRASS_for_new_growth_GtC_py']
        idx2 = fcol_in_mdf['CO2_flux_from_atm_to_NF_for_new_growth_GtC_py']
        idx3 = fcol_in_mdf['CO2_flux_from_atm_to_TROP_for_new_growth_GtC_py']
        idx4 = fcol_in_mdf['CO2_flux_from_atm_to_TUNDRA_for_new_growth']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] + mdf[rowi, idx4]
    
    # Flow_from_biomass_to_atm_Gtc_pr_yr = CO2_flux_GRASS_to_atm_GtC_py + CO2_flux_NF_to_atm_GtC_py + CO2_flux_TROP_to_atm_GtC_py + CO2_flux_TUNDRA_to_atm
        idxlhs = fcol_in_mdf['Flow_from_biomass_to_atm_Gtc_pr_yr']
        idx1 = fcol_in_mdf['CO2_flux_GRASS_to_atm_GtC_py']
        idx2 = fcol_in_mdf['CO2_flux_NF_to_atm_GtC_py']
        idx3 = fcol_in_mdf['CO2_flux_TROP_to_atm_GtC_py']
        idx4 = fcol_in_mdf['CO2_flux_TUNDRA_to_atm']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] + mdf[rowi, idx4]
    
    # Total_land_area[region] = Abandoned_crop_and_grazing_land[region] + Abandoned_populated_land[region] + Barren_land_which_is_ice_and_snow[region] + Cropland[region] + Grazing_land[region] + Populated_land[region] + Forest_land[region]
        idxlhs = fcol_in_mdf['Total_land_area']
        idx1 = fcol_in_mdf['Abandoned_crop_and_grazing_land']
        idx2 = fcol_in_mdf['Abandoned_populated_land']
        idx3 = fcol_in_mdf['Barren_land_which_is_ice_and_snow']
        idx4 = fcol_in_mdf['Cropland']
        idx5 = fcol_in_mdf['Grazing_land']
        idx6 = fcol_in_mdf['Populated_land']
        idx7 = fcol_in_mdf['Forest_land']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] + mdf[rowi , idx4:idx4 + 10] + mdf[rowi , idx5:idx5 + 10] + mdf[rowi , idx6:idx6 + 10] + mdf[rowi , idx7:idx7 + 10]
    
    # Forest_area_as_pct_of_total_land[region] = Forest_land[region] / Total_land_area[region]
        idxlhs = fcol_in_mdf['Forest_area_as_pct_of_total_land']
        idx1 = fcol_in_mdf['Forest_land']
        idx2 = fcol_in_mdf['Total_land_area']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # Forest_area_as_pct_of_total_land_last_year[region] = SMOOTH3 ( Forest_area_as_pct_of_total_land[region] , One_year )
        idxin = fcol_in_mdf['Forest_area_as_pct_of_total_land' ]
        idx2 = fcol_in_mdf['Forest_area_as_pct_of_total_land_last_year_2']
        idx1 = fcol_in_mdf['Forest_area_as_pct_of_total_land_last_year_1']
        idxout = fcol_in_mdf['Forest_area_as_pct_of_total_land_last_year']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( One_year / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( One_year / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( One_year / 3) * dt
    
    # Forest_area_last_year[region] = SMOOTH3I ( Forest_land[region] , One_year , Forest_land_in_1980[region] )
        idxlhs = fcol_in_mdf['Forest_area_last_year']
        idxin = fcol_in_mdf['Forest_land']
        idx2 = fcol_in_mdf['Forest_area_last_year_2']
        idx1 = fcol_in_mdf['Forest_area_last_year_1']
        idxout = fcol_in_mdf['Forest_area_last_year']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( One_year / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( One_year / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( One_year / 3) * dt
    
    # NF_area = NF_Living_biomass_GtBiomass / NF_living_biomass_densitiy_tBiomass_pr_km2 * UNIT_conv_to_Mkm2
        idxlhs = fcol_in_mdf['NF_area']
        idx1 = fcol_in_mdf['NF_Living_biomass_GtBiomass']
        idx2 = fcol_in_mdf['NF_living_biomass_densitiy_tBiomass_pr_km2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] / mdf[rowi, idx2] *  UNIT_conv_to_Mkm2 
    
    # TROP_area = TROP_Living_biomass_GtBiomass / TROP_living_biomass_densitiy_tBiomass_pr_km2 * UNIT_conv_to_Mkm2
        idxlhs = fcol_in_mdf['TROP_area']
        idx1 = fcol_in_mdf['TROP_Living_biomass_GtBiomass']
        idx2 = fcol_in_mdf['TROP_living_biomass_densitiy_tBiomass_pr_km2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] / mdf[rowi, idx2] *  UNIT_conv_to_Mkm2 
    
    # pb_Forest_degradation = ( NF_area + TROP_area ) * Effect_of_population_on_forest_degradation_and_biocapacity
        idxlhs = fcol_in_mdf['pb_Forest_degradation']
        idx1 = fcol_in_mdf['NF_area']
        idx2 = fcol_in_mdf['TROP_area']
        idx3 = fcol_in_mdf['Effect_of_population_on_forest_degradation_and_biocapacity']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] + mdf[rowi, idx2] )  * mdf[rowi, idx3]
    
    # Forest_degradation_risk_score = IF_THEN_ELSE ( pb_Forest_degradation_green_threshold > pb_Forest_degradation , 0 , 1 )
        idxlhs = fcol_in_mdf['Forest_degradation_risk_score']
        idx1 = fcol_in_mdf['pb_Forest_degradation']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  (  pb_Forest_degradation_green_threshold  > mdf[rowi, idx1] ,  0  ,  1  ) 
    
    # Forest_land_last_year[region] = SMOOTH3I ( Forest_land[region] , One_year , Forest_land_in_1980[region] )
        idxlhs = fcol_in_mdf['Forest_land_last_year']
        idxin = fcol_in_mdf['Forest_land']
        idx2 = fcol_in_mdf['Forest_land_last_year_2']
        idx1 = fcol_in_mdf['Forest_land_last_year_1']
        idxout = fcol_in_mdf['Forest_land_last_year']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( One_year / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( One_year / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( One_year / 3) * dt
    
    # Indicted_Fraction_deforested[region] = Annual_pct_deforested[region] / UNIT_conv_pct_to_fraction
        idxlhs = fcol_in_mdf['Indicted_Fraction_deforested']
        mdf[rowi, idxlhs:idxlhs + 10] =  Annual_pct_deforested[0:10]  /  UNIT_conv_pct_to_fraction 
    
    # Fraction_deforested[region] = SMOOTH ( Indicted_Fraction_deforested[region] , Time_to_implement_deforestation )
        idx1 = fcol_in_mdf['Fraction_deforested']
        idx2 = fcol_in_mdf['Indicted_Fraction_deforested']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1+10] + ( mdf[rowi-1 , idx2:idx2 + 10] - mdf[rowi -1 , idx1:idx1 + 10]) / Time_to_implement_deforestation * dt
     
    # Global_CO2_from_fossil_fuels_to_atm = SUM ( CO2_from_fossil_fuels_to_atm[region!] )
        idxlhs = fcol_in_mdf['Global_CO2_from_fossil_fuels_to_atm']
        idx1 = fcol_in_mdf['CO2_from_fossil_fuels_to_atm']
        globsum = 0
        for j in range(0,10):
            globsum = globsum + mdf[rowi, idx1 + j]
        mdf[rowi, idxlhs] = globsum 
    
    # Fraction_of_CO2_emi_from_fossils_attributable_to_a_region[region] = CO2_from_fossil_fuels_to_atm[region] / Global_CO2_from_fossil_fuels_to_atm
        idxlhs = fcol_in_mdf['Fraction_of_CO2_emi_from_fossils_attributable_to_a_region']
        idx1 = fcol_in_mdf['CO2_from_fossil_fuels_to_atm']
        idx2 = fcol_in_mdf['Global_CO2_from_fossil_fuels_to_atm']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2]
     
    # Fraction_of_govt_loan_obligations_to_PL_met[region] = ZIDZ ( Govt_loan_obligations_to_PL_MET[region] , Govt_loan_obligations_to_PL[region] )
        idxlhs = fcol_in_mdf['Fraction_of_govt_loan_obligations_to_PL_met']
        idx1 = fcol_in_mdf['Govt_loan_obligations_to_PL_MET']
        idx2 = fcol_in_mdf['Govt_loan_obligations_to_PL']
        for i in range(0,10):
            mdf[rowi, idxlhs + i] = ZIDZ ( mdf[rowi, idx1 + i], mdf[rowi, idx2 + i])
    
    # Fraction_of_population_over_50_still_working[region] = WITH LOOKUP ( GDPpp_USED[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 0.95 ) , ( 50 , 0.8 ) , ( 100 , 0.5 ) ) )
        tabidx = ftab_in_d_table['Fraction_of_population_over_50_still_working'] # fetch the correct table
        idx2 = fcol_in_mdf['Fraction_of_population_over_50_still_working'] # get the location of the lhs in mdf
        idx3 = fcol_in_mdf['GDPpp_USED']
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:,0], look[:, 1])
    
    # Freshwater_withdrawal_per_person = Freshwater_withdrawal_per_person_TLTL * Effect_of_GL_on_freshwater_use
        idxlhs = fcol_in_mdf['Freshwater_withdrawal_per_person']
        idx1 = fcol_in_mdf['Effect_of_GL_on_freshwater_use']
        mdf[rowi, idxlhs] =  Freshwater_withdrawal_per_person_TLTL  * mdf[rowi, idx1]
    
    # pb_Freshwater_withdrawal[region] = Freshwater_withdrawal_per_person * Population[region] * UNIT_conv_to_cubic_km_pr_yr
        idxlhs = fcol_in_mdf['pb_Freshwater_withdrawal']
        idx1 = fcol_in_mdf['Freshwater_withdrawal_per_person']
        idx2 = fcol_in_mdf['Population']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1] * mdf[rowi , idx2:idx2 + 10] *  UNIT_conv_to_cubic_km_pr_yr 
     
    # pb_Freshwater_withdrawal_global = SUM ( pb_Freshwater_withdrawal[region!] )
        idxlhs = fcol_in_mdf['pb_Freshwater_withdrawal_global']
        idx1 = fcol_in_mdf['pb_Freshwater_withdrawal']
        globsum = 0
        for j in range(0,10):
            globsum = globsum + mdf[rowi, idx1 + j]
        mdf[rowi, idxlhs] = globsum 
    
    # Freshwater_withdrawal_risk_score = IF_THEN_ELSE ( pb_Freshwater_withdrawal_global > pb_Freshwater_withdrawal_green_threshold , 1 , 0 )
        idxlhs = fcol_in_mdf['Freshwater_withdrawal_risk_score']
        idx1 = fcol_in_mdf['pb_Freshwater_withdrawal_global']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  ( mdf[rowi, idx1] >  pb_Freshwater_withdrawal_green_threshold  ,  1  ,  0  ) 
    
    # Funds_from_private_investment_leaked[region] = ( Private_Investment_in_new_capacity[region] ) * Future_leakage[region]
        idxlhs = fcol_in_mdf['Funds_from_private_investment_leaked']
        idx1 = fcol_in_mdf['Private_Investment_in_new_capacity']
        idx2 = fcol_in_mdf['Future_leakage']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] )  * mdf[rowi , idx2:idx2 + 10]
    
    # Funds_leaked_during_transfer_to_workers[region] = Gross_Govt_income[region] * Fraction_of_govt_income_transferred_to_workers[region] * Future_leakage[region]
        idxlhs = fcol_in_mdf['Funds_leaked_during_transfer_to_workers']
        idx1 = fcol_in_mdf['Gross_Govt_income']
        idx2 = fcol_in_mdf['Fraction_of_govt_income_transferred_to_workers']
        idx3 = fcol_in_mdf['Future_leakage']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] * mdf[rowi , idx3:idx3 + 10]
    
    # Funds_leaks_on_the_way_to_investment_in_public_capacity[region] = ( Govt_investment_in_public_capacity[region] + Public_money_from_LPB_policy_to_investment[region] ) * Future_leakage[region]
        idxlhs = fcol_in_mdf['Funds_leaks_on_the_way_to_investment_in_public_capacity']
        idx1 = fcol_in_mdf['Govt_investment_in_public_capacity']
        idx2 = fcol_in_mdf['Public_money_from_LPB_policy_to_investment']
        idx3 = fcol_in_mdf['Future_leakage']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] )  * mdf[rowi , idx3:idx3 + 10]
    
    # Funds_leaks_on_the_way_to_public_services[region] = ( Govt_consumption_ie_purchases[region] + Public_money_from_LPB_policy_to_public_spending[region] ) * Future_leakage[region]
        idxlhs = fcol_in_mdf['Funds_leaks_on_the_way_to_public_services']
        idx1 = fcol_in_mdf['Govt_consumption_ie_purchases']
        idx2 = fcol_in_mdf['Public_money_from_LPB_policy_to_public_spending']
        idx3 = fcol_in_mdf['Future_leakage']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] )  * mdf[rowi , idx3:idx3 + 10]
    
    # Increase_in_funds_leaked[region] = Funds_from_private_investment_leaked[region] + Funds_leaked_during_transfer_to_workers[region] + Funds_leaks_on_the_way_to_investment_in_public_capacity[region] + Funds_leaks_on_the_way_to_public_services[region]
        idxlhs = fcol_in_mdf['Increase_in_funds_leaked']
        idx1 = fcol_in_mdf['Funds_from_private_investment_leaked']
        idx2 = fcol_in_mdf['Funds_leaked_during_transfer_to_workers']
        idx3 = fcol_in_mdf['Funds_leaks_on_the_way_to_investment_in_public_capacity']
        idx4 = fcol_in_mdf['Funds_leaks_on_the_way_to_public_services']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] + mdf[rowi , idx4:idx4 + 10]
    
    # future_deforestation[region] = IF_THEN_ELSE ( zeit > Policy_start_year , Forest_land * Fraction_deforested , 0 )
        idxlhs = fcol_in_mdf['future_deforestation']
        idx1 = fcol_in_mdf['Forest_land']
        idx2 = fcol_in_mdf['Fraction_deforested']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >  Policy_start_year  , mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] ,  0  ) 
    
    # GDP_model_one_year_ago[region] = SMOOTH3 ( GDP_model[region] , One_year )
        idxin = fcol_in_mdf['GDP_model' ]
        idx2 = fcol_in_mdf['GDP_model_one_year_ago_2']
        idx1 = fcol_in_mdf['GDP_model_one_year_ago_1']
        idxout = fcol_in_mdf['GDP_model_one_year_ago']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( One_year / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( One_year / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( One_year / 3) * dt
    
    # GDPpp_model_One_yr_ago[region] = SMOOTH3 ( GDPpp_model[region] , One_year )
        idxin = fcol_in_mdf['GDPpp_model' ]
        idx2 = fcol_in_mdf['GDPpp_model_One_yr_ago_2']
        idx1 = fcol_in_mdf['GDPpp_model_One_yr_ago_1']
        idxout = fcol_in_mdf['GDPpp_model_One_yr_ago']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( One_year / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( One_year / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( One_year / 3) * dt
    
    # Hiring_rate[region] = Additional_people_required[region] / Time_required_to_fill_jobs
        idxlhs = fcol_in_mdf['Hiring_rate']
        idx1 = fcol_in_mdf['Additional_people_required']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Time_required_to_fill_jobs 
    
    # Unemployed_to_labor_pool_ratio[region] = Unemployed[region] / Labor_pool[region]
        idxlhs = fcol_in_mdf['Unemployed_to_labor_pool_ratio']
        idx1 = fcol_in_mdf['Unemployed']
        idx2 = fcol_in_mdf['Labor_pool']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # Getting_a_job_cut_off[region] = WITH LOOKUP ( Unemployed_to_labor_pool_ratio[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0.01 , 0 ) , ( 0.02 , 0.02 ) , ( 0.04 , 0.25 ) , ( 0.06 , 0.7 ) , ( 0.08 , 0.95 ) , ( 0.1 , 1 ) ) )
        tabidx = ftab_in_d_table['Getting_a_job_cut_off'] # fetch the correct table
        idx2 = fcol_in_mdf['Getting_a_job_cut_off'] # get the location of the lhs in mdf
        idx3 = fcol_in_mdf['Unemployed_to_labor_pool_ratio']
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:,0], look[:, 1])
    
    # Getting_a_job[region] = Hiring_rate[region] * Getting_a_job_cut_off[region]
        idxlhs = fcol_in_mdf['Getting_a_job']
        idx1 = fcol_in_mdf['Hiring_rate']
        idx2 = fcol_in_mdf['Getting_a_job_cut_off']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi, idx2:idx2 + 10]
    
    # N2O_emissions_in_CO2e[region] = ( N2O_emi_from_agri[region] + N2O_emi_X_agri[region] ) * Global_Warming_Potential_N20 / UNIT_conversion_Gt_to_Mt
        idxlhs = fcol_in_mdf['N2O_emissions_in_CO2e']
        idx1 = fcol_in_mdf['N2O_emi_from_agri']
        idx2 = fcol_in_mdf['N2O_emi_X_agri']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] )  *  Global_Warming_Potential_N20  /  UNIT_conversion_Gt_to_Mt 
    
    # Total_CO2_emissions_in_CO2e[region] = Total_CO2_emissions[region] * Global_warming_potential_CO2
        idxlhs = fcol_in_mdf['Total_CO2_emissions_in_CO2e']
        idx1 = fcol_in_mdf['Total_CO2_emissions']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  Global_warming_potential_CO2 
    
    # Kyoto_Fluor_emissions_allocated_to_region[region] = Kyoto_Fluor_emissions_GtCO2e_py * Regional_population_as_fraction_of_total[region]
        idxlhs = fcol_in_mdf['Kyoto_Fluor_emissions_allocated_to_region']
        idx1 = fcol_in_mdf['Kyoto_Fluor_emissions_GtCO2e_py']
        idx2 = fcol_in_mdf['Regional_population_as_fraction_of_total']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1] * mdf[rowi , idx2:idx2 + 10]
    
    # Montreal_emissions_allocated_to_region[region] = Montreal_emissions_GtCO2e_py * Regional_population_as_fraction_of_total[region]
        idxlhs = fcol_in_mdf['Montreal_emissions_allocated_to_region']
        idx1 = fcol_in_mdf['Montreal_emissions_GtCO2e_py']
        idx2 = fcol_in_mdf['Regional_population_as_fraction_of_total']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1] * mdf[rowi , idx2:idx2 + 10]
    
    # Total_GHG_emissions[region] = CH4_Emissions_CO2e[region] + N2O_emissions_in_CO2e[region] + Total_CO2_emissions_in_CO2e[region] + Kyoto_Fluor_emissions_allocated_to_region[region] + Montreal_emissions_allocated_to_region[region]
        idxlhs = fcol_in_mdf['Total_GHG_emissions']
        idx1 = fcol_in_mdf['CH4_Emissions_CO2e']
        idx2 = fcol_in_mdf['N2O_emissions_in_CO2e']
        idx3 = fcol_in_mdf['Total_CO2_emissions_in_CO2e']
        idx4 = fcol_in_mdf['Kyoto_Fluor_emissions_allocated_to_region']
        idx5 = fcol_in_mdf['Montreal_emissions_allocated_to_region']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] + mdf[rowi , idx4:idx4 + 10] + mdf[rowi , idx5:idx5 + 10]
    
    # GHG_intensity[region] = Total_GHG_emissions[region] / GDP_USED[region] * UNIT_conversion_to_tCO2e_pr_USD
        idxlhs = fcol_in_mdf['GHG_intensity']
        idx1 = fcol_in_mdf['Total_GHG_emissions']
        idx2 = fcol_in_mdf['GDP_USED']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10] *  UNIT_conversion_to_tCO2e_pr_USD 
    
    # GHG_intensity_last_year[region] = SMOOTH3 ( GHG_intensity[region] , One_year )
        idxin = fcol_in_mdf['GHG_intensity' ]
        idx2 = fcol_in_mdf['GHG_intensity_last_year_2']
        idx1 = fcol_in_mdf['GHG_intensity_last_year_1']
        idxout = fcol_in_mdf['GHG_intensity_last_year']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( One_year / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( One_year / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( One_year / 3) * dt
    
    # gl_to_acgl[region] = abs ( MIN ( 0 , Grazing_land_gap[region] ) ) / Time_for_agri_land_to_become_abandoned
        idxlhs = fcol_in_mdf['gl_to_acgl']
        idx1 = fcol_in_mdf['Grazing_land_gap']
        mdf[rowi, idxlhs:idxlhs + 10] =  abs  (  np.minimum  (  0  , mdf[rowi , idx1:idx1 + 10] )  )  /  Time_for_agri_land_to_become_abandoned 
    
    # Glacial_ice_melting_km3_py = IF_THEN_ELSE ( Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py > 0 , Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py , 0 )
        idxlhs = fcol_in_mdf['Glacial_ice_melting_km3_py']
        idx1 = fcol_in_mdf['Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py']
        idx2 = fcol_in_mdf['Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  ( mdf[rowi, idx1] >  0  , mdf[rowi, idx2] ,  0  ) 
    
    # Glacial_ice_area_decrease_Mkm2_pr_yr = ( Glacial_ice_melting_km3_py / Avg_thickness_glacier_km ) * UNIT_Conversion_from_km3_p_kmy_to_Mkm2_py
        idxlhs = fcol_in_mdf['Glacial_ice_area_decrease_Mkm2_pr_yr']
        idx1 = fcol_in_mdf['Glacial_ice_melting_km3_py']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] /  Avg_thickness_glacier_km  )  *  UNIT_Conversion_from_km3_p_kmy_to_Mkm2_py 
    
    # Glacial_ice_freezing_km3_py = IF_THEN_ELSE ( Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py < 0 , Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py * ( - 1 ) , 0 )
        idxlhs = fcol_in_mdf['Glacial_ice_freezing_km3_py']
        idx1 = fcol_in_mdf['Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py']
        idx2 = fcol_in_mdf['Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  ( mdf[rowi, idx1] <  0  , mdf[rowi, idx2] *  (  -  1  )  ,  0  ) 
    
    # Glacial_ice_area_increase_Mkm2_pr_yr = ( Glacial_ice_freezing_km3_py / Avg_thickness_glacier_km ) * UNIT_Conversion_from_km3_p_kmy_to_Mkm2_py
        idxlhs = fcol_in_mdf['Glacial_ice_area_increase_Mkm2_pr_yr']
        idx1 = fcol_in_mdf['Glacial_ice_freezing_km3_py']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] /  Avg_thickness_glacier_km  )  *  UNIT_Conversion_from_km3_p_kmy_to_Mkm2_py 
    
    # Glacial_ice_melting_as_water_km3_py = Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py * Densitiy_of_water_relative_to_ice
        idxlhs = fcol_in_mdf['Glacial_ice_melting_as_water_km3_py']
        idx1 = fcol_in_mdf['Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Densitiy_of_water_relative_to_ice 
     
    # Global_Actual_inequality_index_higher_is_more_unequal = Actual_inequality_index_higher_is_more_unequal[us] * Regional_population_as_fraction_of_total[us] + Actual_inequality_index_higher_is_more_unequal[af] * Regional_population_as_fraction_of_total[af] + Actual_inequality_index_higher_is_more_unequal[cn] * Regional_population_as_fraction_of_total[cn] + Actual_inequality_index_higher_is_more_unequal[me] * Regional_population_as_fraction_of_total[me] + Actual_inequality_index_higher_is_more_unequal[sa] * Regional_population_as_fraction_of_total[sa] + Actual_inequality_index_higher_is_more_unequal[la] * Regional_population_as_fraction_of_total[la] + Actual_inequality_index_higher_is_more_unequal[pa] * Regional_population_as_fraction_of_total[pa] + Actual_inequality_index_higher_is_more_unequal[ec] * Regional_population_as_fraction_of_total[ec] + Actual_inequality_index_higher_is_more_unequal[eu] * Regional_population_as_fraction_of_total[eu] + Actual_inequality_index_higher_is_more_unequal[se] * Regional_population_as_fraction_of_total[se]
        idxlhs = fcol_in_mdf['Global_Actual_inequality_index_higher_is_more_unequal']
        idx1 = fcol_in_mdf['Actual_inequality_index_higher_is_more_unequal']
        idx2 = fcol_in_mdf['Regional_population_as_fraction_of_total']
        mdf[rowi, idxlhs] = ( mdf[rowi, idx1 + 0 ] *  mdf[rowi, idx2 + 0 ]+ mdf[rowi, idx1 + 1 ] *  mdf[rowi, idx2 + 1 ]+ mdf[rowi, idx1 + 2 ] *  mdf[rowi, idx2 + 2 ]+ mdf[rowi, idx1 + 3 ] *  mdf[rowi, idx2 + 3 ]+ mdf[rowi, idx1 + 4 ] *  mdf[rowi, idx2 + 4 ]+ mdf[rowi, idx1 + 5 ] *  mdf[rowi, idx2 + 5 ]+ mdf[rowi, idx1 + 6 ] *  mdf[rowi, idx2 + 6 ]+ mdf[rowi, idx1 + 7 ] *  mdf[rowi, idx2 + 7 ]+ mdf[rowi, idx1 + 8 ] *  mdf[rowi, idx2 + 8 ]+ mdf[rowi, idx1 + 9 ] *  mdf[rowi, idx2 + 9 ] )
     
    # Global_average_Energy_footprint_pp = Energy_footprint_pp[us] * Regional_population_as_fraction_of_total[us] + Energy_footprint_pp[af] * Regional_population_as_fraction_of_total[af] + Energy_footprint_pp[cn] * Regional_population_as_fraction_of_total[cn] + Energy_footprint_pp[me] * Regional_population_as_fraction_of_total[me] + Energy_footprint_pp[sa] * Regional_population_as_fraction_of_total[sa] + Energy_footprint_pp[la] * Regional_population_as_fraction_of_total[la] + Energy_footprint_pp[pa] * Regional_population_as_fraction_of_total[pa] + Energy_footprint_pp[ec] * Regional_population_as_fraction_of_total[ec] + Energy_footprint_pp[eu] * Regional_population_as_fraction_of_total[eu] + Energy_footprint_pp[se] * Regional_population_as_fraction_of_total[se]
        idxlhs = fcol_in_mdf['Global_average_Energy_footprint_pp']
        idx1 = fcol_in_mdf['Energy_footprint_pp']
        idx2 = fcol_in_mdf['Regional_population_as_fraction_of_total']
        mdf[rowi, idxlhs] = ( mdf[rowi, idx1 + 0 ] *  mdf[rowi, idx2 + 0 ]+ mdf[rowi, idx1 + 1 ] *  mdf[rowi, idx2 + 1 ]+ mdf[rowi, idx1 + 2 ] *  mdf[rowi, idx2 + 2 ]+ mdf[rowi, idx1 + 3 ] *  mdf[rowi, idx2 + 3 ]+ mdf[rowi, idx1 + 4 ] *  mdf[rowi, idx2 + 4 ]+ mdf[rowi, idx1 + 5 ] *  mdf[rowi, idx2 + 5 ]+ mdf[rowi, idx1 + 6 ] *  mdf[rowi, idx2 + 6 ]+ mdf[rowi, idx1 + 7 ] *  mdf[rowi, idx2 + 7 ]+ mdf[rowi, idx1 + 8 ] *  mdf[rowi, idx2 + 8 ]+ mdf[rowi, idx1 + 9 ] *  mdf[rowi, idx2 + 9 ] )
     
    # Global_Average_wellbeing_index = Average_wellbeing_index[us] * Regional_population_as_fraction_of_total[us] + Average_wellbeing_index[af] * Regional_population_as_fraction_of_total[af] + Average_wellbeing_index[cn] * Regional_population_as_fraction_of_total[cn] + Average_wellbeing_index[me] * Regional_population_as_fraction_of_total[me] + Average_wellbeing_index[sa] * Regional_population_as_fraction_of_total[sa] + Average_wellbeing_index[la] * Regional_population_as_fraction_of_total[la] + Average_wellbeing_index[pa] * Regional_population_as_fraction_of_total[pa] + Average_wellbeing_index[ec] * Regional_population_as_fraction_of_total[ec] + Average_wellbeing_index[eu] * Regional_population_as_fraction_of_total[eu] + Average_wellbeing_index[se] * Regional_population_as_fraction_of_total[se]
        idxlhs = fcol_in_mdf['Global_Average_wellbeing_index']
        idx1 = fcol_in_mdf['Average_wellbeing_index']
        idx2 = fcol_in_mdf['Regional_population_as_fraction_of_total']
        mdf[rowi, idxlhs] = ( mdf[rowi, idx1 + 0 ] *  mdf[rowi, idx2 + 0 ]+ mdf[rowi, idx1 + 1 ] *  mdf[rowi, idx2 + 1 ]+ mdf[rowi, idx1 + 2 ] *  mdf[rowi, idx2 + 2 ]+ mdf[rowi, idx1 + 3 ] *  mdf[rowi, idx2 + 3 ]+ mdf[rowi, idx1 + 4 ] *  mdf[rowi, idx2 + 4 ]+ mdf[rowi, idx1 + 5 ] *  mdf[rowi, idx2 + 5 ]+ mdf[rowi, idx1 + 6 ] *  mdf[rowi, idx2 + 6 ]+ mdf[rowi, idx1 + 7 ] *  mdf[rowi, idx2 + 7 ]+ mdf[rowi, idx1 + 8 ] *  mdf[rowi, idx2 + 8 ]+ mdf[rowi, idx1 + 9 ] *  mdf[rowi, idx2 + 9 ] )
     
    # Global_Each_region_max_cost_estimate_all_TAs_PES_0 = SUM ( Each_region_max_cost_estimate_all_TAs_PES_0[region!] )
        idxlhs = fcol_in_mdf['Global_Each_region_max_cost_estimate_all_TAs_PES_0']
        idx1 = fcol_in_mdf['Each_region_max_cost_estimate_all_TAs_PES_0']
        globsum = 0
        for j in range(0,10):
            globsum = globsum + mdf[rowi, idx1 + j]
        mdf[rowi, idxlhs] = globsum 
     
    # Global_Energy_intensity_kWh_per_usd = Energy_intensity_kWh_per_usd[us] * GDP_USED[us] / Global_GDP_USED + Energy_intensity_kWh_per_usd[se] * GDP_USED[se] / Global_GDP_USED + Energy_intensity_kWh_per_usd[af] * GDP_USED[af] / Global_GDP_USED + Energy_intensity_kWh_per_usd[cn] * GDP_USED[cn] / Global_GDP_USED + Energy_intensity_kWh_per_usd[me] * GDP_USED[me] / Global_GDP_USED + Energy_intensity_kWh_per_usd[sa] * GDP_USED[sa] / Global_GDP_USED + Energy_intensity_kWh_per_usd[la] * GDP_USED[la] / Global_GDP_USED + Energy_intensity_kWh_per_usd[pa] * GDP_USED[pa] / Global_GDP_USED + Energy_intensity_kWh_per_usd[ec] * GDP_USED[ec] / Global_GDP_USED + Energy_intensity_kWh_per_usd[eu] * GDP_USED[eu] / Global_GDP_USED
        idxlhs = fcol_in_mdf['Global_Energy_intensity_kWh_per_usd']
        idx1 = fcol_in_mdf['Energy_intensity_kWh_per_usd']
        idx2 = fcol_in_mdf['GDP_USED']
        idx3 = fcol_in_mdf['Global_GDP_USED']
        mdf[rowi, idxlhs] = ( mdf[rowi, idx1 + 0 ] *  mdf[rowi, idx2 + 0 ] /  mdf[rowi, idx3] + mdf[rowi, idx1 + 1 ] *  mdf[rowi, idx2 + 1 ] /  mdf[rowi, idx3] + mdf[rowi, idx1 + 2 ] *  mdf[rowi, idx2 + 2 ] /  mdf[rowi, idx3] + mdf[rowi, idx1 + 3 ] *  mdf[rowi, idx2 + 3 ] /  mdf[rowi, idx3] + mdf[rowi, idx1 + 4 ] *  mdf[rowi, idx2 + 4 ] /  mdf[rowi, idx3] + mdf[rowi, idx1 + 5 ] *  mdf[rowi, idx2 + 5 ] /  mdf[rowi, idx3] + mdf[rowi, idx1 + 6 ] *  mdf[rowi, idx2 + 6 ] /  mdf[rowi, idx3] + mdf[rowi, idx1 + 7 ] *  mdf[rowi, idx2 + 7 ] /  mdf[rowi, idx3] + mdf[rowi, idx1 + 8 ] *  mdf[rowi, idx2 + 8 ] /  mdf[rowi, idx3] + mdf[rowi, idx1 + 9 ] *  mdf[rowi, idx2 + 9 ] /  mdf[rowi, idx3]  )
    
    # GLobal_GDP_in_terraUSD = GLobal_GDP * UNIT_conv_to_TUSD
        idxlhs = fcol_in_mdf['GLobal_GDP_in_terraUSD']
        idx1 = fcol_in_mdf['GLobal_GDP']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  UNIT_conv_to_TUSD 
    
    # Govt_debt_paid_back_to_private_lenders[region] = Govt_debt_repayment_obligation[region] * Fraction_of_govt_loan_obligations_to_PL_met[region]
        idxlhs = fcol_in_mdf['Govt_debt_paid_back_to_private_lenders']
        idx1 = fcol_in_mdf['Govt_debt_repayment_obligation']
        idx2 = fcol_in_mdf['Fraction_of_govt_loan_obligations_to_PL_met']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # Owner_income_from_lending_activity[region] = Worker_cashflow_to_owners[region] + Govt_cashflow_to_owners[region]
        idxlhs = fcol_in_mdf['Owner_income_from_lending_activity']
        idx1 = fcol_in_mdf['Worker_cashflow_to_owners']
        idx2 = fcol_in_mdf['Govt_cashflow_to_owners']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10]
    
    # Population_below_2p5_kusd_ppy[region] = Population[region] * Fraction_of_population_below_existential_minimum[region]
        idxlhs = fcol_in_mdf['Population_below_2p5_kusd_ppy']
        idx1 = fcol_in_mdf['Population']
        idx2 = fcol_in_mdf['Fraction_of_population_below_existential_minimum']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
     
    # Global_Population_below_2p5_kusd_p_py = SUM ( Population_below_2p5_kusd_ppy[region!] )
        idxlhs = fcol_in_mdf['Global_Population_below_2p5_kusd_p_py']
        idx1 = fcol_in_mdf['Population_below_2p5_kusd_ppy']
        globsum = 0
        for j in range(0,10):
            globsum = globsum + mdf[rowi, idx1 + j]
        mdf[rowi, idxlhs] = globsum 
    
    # RoC_GHG_intensity[region] = ( GHG_intensity[region] - GHG_intensity_last_year[region] ) / GHG_intensity_last_year[region] / One_year
        idxlhs = fcol_in_mdf['RoC_GHG_intensity']
        idx1 = fcol_in_mdf['GHG_intensity']
        idx2 = fcol_in_mdf['GHG_intensity_last_year']
        idx3 = fcol_in_mdf['GHG_intensity_last_year']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10] )  / mdf[rowi , idx3:idx3 + 10] /  One_year 
    
    # RoC_in_Carbon_intensity[region] = ( Carbon_intensity[region] - Carbon_intensity_last_year[region] ) / Carbon_intensity_last_year[region] / One_year
        idxlhs = fcol_in_mdf['RoC_in_Carbon_intensity']
        idx1 = fcol_in_mdf['Carbon_intensity']
        idx2 = fcol_in_mdf['Carbon_intensity_last_year']
        idx3 = fcol_in_mdf['Carbon_intensity_last_year']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10] )  / mdf[rowi , idx3:idx3 + 10] /  One_year 
     
    # Global_Smoothed_Social_tension_index_with_trust_effect = Smoothed_Social_tension_index_with_trust_effect[us] * Regional_population_as_fraction_of_total[us] + Smoothed_Social_tension_index_with_trust_effect[af] * Regional_population_as_fraction_of_total[af] + Smoothed_Social_tension_index_with_trust_effect[cn] * Regional_population_as_fraction_of_total[cn] + Smoothed_Social_tension_index_with_trust_effect[me] * Regional_population_as_fraction_of_total[me] + Smoothed_Social_tension_index_with_trust_effect[sa] * Regional_population_as_fraction_of_total[sa] + Smoothed_Social_tension_index_with_trust_effect[la] * Regional_population_as_fraction_of_total[la] + Smoothed_Social_tension_index_with_trust_effect[pa] * Regional_population_as_fraction_of_total[pa] + Smoothed_Social_tension_index_with_trust_effect[ec] * Regional_population_as_fraction_of_total[ec] + Smoothed_Social_tension_index_with_trust_effect[eu] * Regional_population_as_fraction_of_total[eu] + Smoothed_Social_tension_index_with_trust_effect[se] * Regional_population_as_fraction_of_total[se]
        idxlhs = fcol_in_mdf['Global_Smoothed_Social_tension_index_with_trust_effect']
        idx1 = fcol_in_mdf['Smoothed_Social_tension_index_with_trust_effect']
        idx2 = fcol_in_mdf['Regional_population_as_fraction_of_total']
        mdf[rowi, idxlhs] = ( mdf[rowi, idx1 + 0 ] *  mdf[rowi, idx2 + 0 ]+ mdf[rowi, idx1 + 1 ] *  mdf[rowi, idx2 + 1 ]+ mdf[rowi, idx1 + 2 ] *  mdf[rowi, idx2 + 2 ]+ mdf[rowi, idx1 + 3 ] *  mdf[rowi, idx2 + 3 ]+ mdf[rowi, idx1 + 4 ] *  mdf[rowi, idx2 + 4 ]+ mdf[rowi, idx1 + 5 ] *  mdf[rowi, idx2 + 5 ]+ mdf[rowi, idx1 + 6 ] *  mdf[rowi, idx2 + 6 ]+ mdf[rowi, idx1 + 7 ] *  mdf[rowi, idx2 + 7 ]+ mdf[rowi, idx1 + 8 ] *  mdf[rowi, idx2 + 8 ]+ mdf[rowi, idx1 + 9 ] *  mdf[rowi, idx2 + 9 ] )
     
    # Global_social_trust = Social_trust[us] * Regional_population_as_fraction_of_total[us] + Social_trust[af] * Regional_population_as_fraction_of_total[af] + Social_trust[cn] * Regional_population_as_fraction_of_total[cn] + Social_trust[me] * Regional_population_as_fraction_of_total[me] + Social_trust[sa] * Regional_population_as_fraction_of_total[sa] + Social_trust[la] * Regional_population_as_fraction_of_total[la] + Social_trust[pa] * Regional_population_as_fraction_of_total[pa] + Social_trust[ec] * Regional_population_as_fraction_of_total[ec] + Social_trust[eu] * Regional_population_as_fraction_of_total[eu] + Social_trust[se] * Regional_population_as_fraction_of_total[se]
        idxlhs = fcol_in_mdf['Global_social_trust']
        idx1 = fcol_in_mdf['Social_trust']
        idx2 = fcol_in_mdf['Regional_population_as_fraction_of_total']
        mdf[rowi, idxlhs] = ( mdf[rowi, idx1 + 0 ] *  mdf[rowi, idx2 + 0 ]+ mdf[rowi, idx1 + 1 ] *  mdf[rowi, idx2 + 1 ]+ mdf[rowi, idx1 + 2 ] *  mdf[rowi, idx2 + 2 ]+ mdf[rowi, idx1 + 3 ] *  mdf[rowi, idx2 + 3 ]+ mdf[rowi, idx1 + 4 ] *  mdf[rowi, idx2 + 4 ]+ mdf[rowi, idx1 + 5 ] *  mdf[rowi, idx2 + 5 ]+ mdf[rowi, idx1 + 6 ] *  mdf[rowi, idx2 + 6 ]+ mdf[rowi, idx1 + 7 ] *  mdf[rowi, idx2 + 7 ]+ mdf[rowi, idx1 + 8 ] *  mdf[rowi, idx2 + 8 ]+ mdf[rowi, idx1 + 9 ] *  mdf[rowi, idx2 + 9 ] )
    
    # pb_Global_Warming = Temp_surface_anomaly_compared_to_anfang_degC
        idxlhs = fcol_in_mdf['pb_Global_Warming']
        idx1 = fcol_in_mdf['Temp_surface_anomaly_compared_to_anfang_degC']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # Global_warming_risk_score = IF_THEN_ELSE ( pb_Global_Warming > pb_Global_Warming_green_threshold , 1 , 0 )
        idxlhs = fcol_in_mdf['Global_warming_risk_score']
        idx1 = fcol_in_mdf['pb_Global_Warming']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  ( mdf[rowi, idx1] >  pb_Global_Warming_green_threshold  ,  1  ,  0  ) 
    
    # Govt_debt_to_PL_to_be_cancelled[region] = Govt_debt_owed_to_private_lenders[region] * Debt_cancelling_pulse[region] / One_year
        idxlhs = fcol_in_mdf['Govt_debt_to_PL_to_be_cancelled']
        idx1 = fcol_in_mdf['Govt_debt_owed_to_private_lenders']
        idx2 = fcol_in_mdf['Debt_cancelling_pulse']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10] /  One_year 
    
    # Govt_debt_cancelling[region] = Govt_debt_to_PL_to_be_cancelled[region]
        idxlhs = fcol_in_mdf['Govt_debt_cancelling']
        idx1 = fcol_in_mdf['Govt_debt_to_PL_to_be_cancelled']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10]
    
    # Govt_debt_from_public_lenders_cancelled[region] = Govt_debt_from_public_lenders[region] * Public_Debt_cancelling_pulse[region]
        idxlhs = fcol_in_mdf['Govt_debt_from_public_lenders_cancelled']
        idx1 = fcol_in_mdf['Govt_debt_from_public_lenders']
        idx2 = fcol_in_mdf['Public_Debt_cancelling_pulse']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # Govt_loan_obligation_to_PL_not_met[region] = MAX ( 0 , Govt_loan_obligations_to_PL[region] - Govt_loan_obligations_to_PL_MET[region] )
        idxlhs = fcol_in_mdf['Govt_loan_obligation_to_PL_not_met']
        idx1 = fcol_in_mdf['Govt_loan_obligations_to_PL']
        idx2 = fcol_in_mdf['Govt_loan_obligations_to_PL_MET']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.maximum  (  0  , mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10] ) 
    
    # Govt_defaulting[region] = Govt_loan_obligation_to_PL_not_met[region]
        idxlhs = fcol_in_mdf['Govt_defaulting']
        idx1 = fcol_in_mdf['Govt_loan_obligation_to_PL_not_met']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10]
    
    # Govt_defaults_written_off[region] = Govt_in_default_to_private_lenders[region] / Time_to_write_off_govt_defaults_to_private_lenders
        idxlhs = fcol_in_mdf['Govt_defaults_written_off']
        idx1 = fcol_in_mdf['Govt_in_default_to_private_lenders']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Time_to_write_off_govt_defaults_to_private_lenders 
    
    # Govt_investment_share[region] = ( ( ( 1 - Future_leakage[region] ) * Govt_investment_in_public_capacity[region] ) / Eff_of_env_damage_on_cost_of_new_capacity[region] ) / GDP_USED[region]
        idxlhs = fcol_in_mdf['Govt_investment_share']
        idx1 = fcol_in_mdf['Future_leakage']
        idx2 = fcol_in_mdf['Govt_investment_in_public_capacity']
        idx3 = fcol_in_mdf['Eff_of_env_damage_on_cost_of_new_capacity']
        idx4 = fcol_in_mdf['GDP_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  (  (  (  1  - mdf[rowi , idx1:idx1 + 10] )  * mdf[rowi , idx2:idx2 + 10] )  / mdf[rowi , idx3:idx3 + 10] )  / mdf[rowi , idx4:idx4 + 10]
    
    # GRASS_Biomass_in_construction_material_left_to_rot = GRASS_Biomass_locked_in_construction_material_GtBiomass / GRASS_Avg_life_of_building_yr * ( 1 - GRASS_Fraction_of_construction_waste_burned_0_to_1 )
        idxlhs = fcol_in_mdf['GRASS_Biomass_in_construction_material_left_to_rot']
        idx1 = fcol_in_mdf['GRASS_Biomass_locked_in_construction_material_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  GRASS_Avg_life_of_building_yr  *  (  1  -  GRASS_Fraction_of_construction_waste_burned_0_to_1  ) 
    
    # Use_of_GRASS_biomass_for_construction = Use_of_GRASS_for_construction_in_2000_GtBiomass * Effect_of_population_and_urbanization_on_biomass_use * UNIT_conversion_1_py
        idxlhs = fcol_in_mdf['Use_of_GRASS_biomass_for_construction']
        idx1 = fcol_in_mdf['Effect_of_population_and_urbanization_on_biomass_use']
        mdf[rowi, idxlhs] =  Use_of_GRASS_for_construction_in_2000_GtBiomass  * mdf[rowi, idx1] *  UNIT_conversion_1_py 
    
    # GRASS_for_construction_use = Use_of_GRASS_biomass_for_construction
        idxlhs = fcol_in_mdf['GRASS_for_construction_use']
        idx1 = fcol_in_mdf['Use_of_GRASS_biomass_for_construction']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # GRASS_Living_biomass_rotting = GRASS_Living_biomass_GtBiomass / GRASS_Avg_life_biomass_yr
        idxlhs = fcol_in_mdf['GRASS_Living_biomass_rotting']
        idx1 = fcol_in_mdf['GRASS_Living_biomass_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  GRASS_Avg_life_biomass_yr 
    
    # GRASS_regrowing_after_being_burnt_Mkm2_py = GRASS_area_burnt_Mkm2 / Time_to_regrow_GRASS_yr
        idxlhs = fcol_in_mdf['GRASS_regrowing_after_being_burnt_Mkm2_py']
        idx1 = fcol_in_mdf['GRASS_area_burnt_Mkm2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Time_to_regrow_GRASS_yr 
    
    # GRASS_regrowing_after_being_deforested_Mkm2_py = GRASS_deforested_Mkm2 / Time_to_regrow_GRASS_after_deforesting_yr
        idxlhs = fcol_in_mdf['GRASS_regrowing_after_being_deforested_Mkm2_py']
        idx1 = fcol_in_mdf['GRASS_deforested_Mkm2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Time_to_regrow_GRASS_after_deforesting_yr 
    
    # GRASS_regrowing_after_harvesting_Mkm2_py = GRASS_area_harvested_Mkm2 / Time_to_regrow_GRASS_yr
        idxlhs = fcol_in_mdf['GRASS_regrowing_after_harvesting_Mkm2_py']
        idx1 = fcol_in_mdf['GRASS_area_harvested_Mkm2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Time_to_regrow_GRASS_yr 
    
    # Greenland_ice_melting_km3_py = IF_THEN_ELSE ( Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py > 0 , Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py , 0 )
        idxlhs = fcol_in_mdf['Greenland_ice_melting_km3_py']
        idx1 = fcol_in_mdf['Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py']
        idx2 = fcol_in_mdf['Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  ( mdf[rowi, idx1] >  0  , mdf[rowi, idx2] ,  0  ) 
    
    # Greenland_ice_area_decrease_Mkm2_pr_yr = ( Greenland_ice_melting_km3_py / Avg_thickness_Greenland_km ) * UNIT_Conversion_from_km3_p_kmy_to_Mkm2_py
        idxlhs = fcol_in_mdf['Greenland_ice_area_decrease_Mkm2_pr_yr']
        idx1 = fcol_in_mdf['Greenland_ice_melting_km3_py']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] /  Avg_thickness_Greenland_km  )  *  UNIT_Conversion_from_km3_p_kmy_to_Mkm2_py 
    
    # Greenland_ice_freezing_km3_py = IF_THEN_ELSE ( Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py < 0 , Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py * ( - 1 ) , 0 )
        idxlhs = fcol_in_mdf['Greenland_ice_freezing_km3_py']
        idx1 = fcol_in_mdf['Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py']
        idx2 = fcol_in_mdf['Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  ( mdf[rowi, idx1] <  0  , mdf[rowi, idx2] *  (  -  1  )  ,  0  ) 
    
    # Greenland_ice_area_increase_Mkm2_pr_yr = ( Greenland_ice_freezing_km3_py / Avg_thickness_Greenland_km ) * UNIT_Conversion_from_km3_p_kmy_to_Mkm2_py
        idxlhs = fcol_in_mdf['Greenland_ice_area_increase_Mkm2_pr_yr']
        idx1 = fcol_in_mdf['Greenland_ice_freezing_km3_py']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] /  Avg_thickness_Greenland_km  )  *  UNIT_Conversion_from_km3_p_kmy_to_Mkm2_py 
    
    # Greenland_ice_melting_as_water_km3_py = Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py * Densitiy_of_water_relative_to_ice
        idxlhs = fcol_in_mdf['Greenland_ice_melting_as_water_km3_py']
        idx1 = fcol_in_mdf['Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Densitiy_of_water_relative_to_ice 
    
    # Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_antarctic_ice_ZJ_py = Heat_used_in_melting_is_pos_or_freezing_is_neg_antarctic_ice_ZJ_py * ( 1 - Fraction_of_heat_needed_to_melt_antarctic_ice_coming_from_air )
        idxlhs = fcol_in_mdf['Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_antarctic_ice_ZJ_py']
        idx1 = fcol_in_mdf['Heat_used_in_melting_is_pos_or_freezing_is_neg_antarctic_ice_ZJ_py']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  (  1  -  Fraction_of_heat_needed_to_melt_antarctic_ice_coming_from_air  ) 
    
    # Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_arctic_ice_ZJ_py = Heat_used_in_melting_is_pos_or_freezing_is_neg_arctic_sea_ice_ZJ_py * ( 1 - Fraction_of_heat_needed_to_melt_arctic_ice_coming_from_air )
        idxlhs = fcol_in_mdf['Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_arctic_ice_ZJ_py']
        idx1 = fcol_in_mdf['Heat_used_in_melting_is_pos_or_freezing_is_neg_arctic_sea_ice_ZJ_py']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  (  1  -  Fraction_of_heat_needed_to_melt_arctic_ice_coming_from_air  ) 
    
    # historical_deforestation_table[us] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 1.1 ) , ( 2000 , - 2 ) , ( 2010 , - 1.1 ) , ( 2020 , 0 ) , ( 2030 , 0 ) , ( 2050 , 0 ) , ( 2075 , 0 ) , ( 2100 , 0 ) ) ) historical_deforestation_table[af] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 7 ) , ( 1990 , 4 ) , ( 2000 , 0 ) , ( 2010 , 6 ) , ( 2020 , - 1 ) , ( 2030 , - 1 ) , ( 2050 , - 1 ) , ( 2075 , - 1 ) , ( 2100 , - 1 ) ) ) historical_deforestation_table[cn] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 3 ) , ( 1990 , 7 ) , ( 2000 , - 1 ) , ( 2010 , 0 ) , ( 2020 , 0 ) , ( 2030 , 0 ) , ( 2050 , 0 ) , ( 2075 , 0 ) , ( 2100 , 0 ) ) ) historical_deforestation_table[me] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 2 ) , ( 1990 , 2 ) , ( 2000 , 2 ) , ( 2010 , 2 ) , ( 2020 , 1 ) , ( 2030 , 0.5 ) , ( 2050 , 0.5 ) , ( 2075 , 0.5 ) , ( 2100 , 0 ) ) ) historical_deforestation_table[sa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0.5 ) , ( 2000 , 0 ) , ( 2010 , 0.6 ) , ( 2020 , - 0.1 ) , ( 2030 , - 0.1 ) , ( 2050 , 0 ) , ( 2075 , 0 ) , ( 2100 , 0 ) ) ) historical_deforestation_table[la] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0 ) , ( 2000 , - 0.5 ) , ( 2010 , - 1 ) , ( 2020 , 0 ) , ( 2030 , 0 ) , ( 2050 , 0 ) , ( 2075 , 0 ) , ( 2100 , 0 ) ) ) historical_deforestation_table[pa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0 ) , ( 2000 , 0 ) , ( 2010 , 0 ) , ( 2020 , - 1 ) , ( 2030 , - 0.5 ) , ( 2050 , - 0.5 ) , ( 2075 , - 0.5 ) , ( 2100 , 0 ) ) ) historical_deforestation_table[ec] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 10 ) , ( 1990 , - 5 ) , ( 2000 , 2 ) , ( 2010 , 0 ) , ( 2020 , 0 ) , ( 2030 , 0 ) , ( 2050 , 0 ) , ( 2075 , 0 ) , ( 2100 , 0 ) ) ) historical_deforestation_table[eu] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0 ) , ( 2000 , - 0.5 ) , ( 2010 , 1 ) , ( 2020 , 0 ) , ( 2030 , 0 ) , ( 2050 , 0 ) , ( 2075 , 0 ) , ( 2100 , 0 ) ) ) historical_deforestation_table[se] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0 ) , ( 2000 , 0 ) , ( 2010 , 1 ) , ( 2020 , 0 ) , ( 2030 , - 1 ) , ( 2050 , - 1 ) , ( 2075 , - 1 ) , ( 2100 , - 1 ) ) )
        tabidx = ftab_in_d_table['historical_deforestation_table'] # fetch the correct table
        idx2 = fcol_in_mdf['historical_deforestation_table'] # get the location of the lhs in mdf
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(zeit, look[:,0], look[:, j + 1])
    
    # historical_deforestation_cutoff[region] = WITH LOOKUP ( Forest_land[region] , ( [ ( 0 , 0 ) - ( 3.00813 , 0.778226 ) ] , ( 0 , 0 ) , ( 4.5 , 0.08 ) , ( 8 , 0.27 ) , ( 10 , 0.5 ) , ( 12 , 0.73 ) , ( 15.5 , 0.92 ) , ( 20 , 1 ) ) )
        tabidx = ftab_in_d_table['historical_deforestation_cutoff'] # fetch the correct table
        idx2 = fcol_in_mdf['historical_deforestation_cutoff'] # get the location of the lhs in mdf
        idx3 = fcol_in_mdf['Forest_land']
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:,0], look[:, 1])
    
    # Indicated_historical_deforestation[region] = historical_deforestation_table[region] * historical_deforestation_cutoff[region]
        idxlhs = fcol_in_mdf['Indicated_historical_deforestation']
        idx1 = fcol_in_mdf['historical_deforestation_table']
        idx2 = fcol_in_mdf['historical_deforestation_cutoff']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi, idx1:idx1 + 10] * mdf[rowi, idx2:idx2 + 10]
    
    # historical_deforestation = IF_THEN_ELSE ( zeit >= Policy_start_year , 0 , Indicated_historical_deforestation )
        idxlhs = fcol_in_mdf['historical_deforestation']
        idx1 = fcol_in_mdf['Indicated_historical_deforestation']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  (  zeit  >=  Policy_start_year  ,  0  , mdf[rowi , idx1:idx1 + 10] ) 
    
    # Historical_forcing_from_solar_insolation_W_p_m2 = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.146265 ) , ( 1981 , 0.133052 ) , ( 1982 , 0.0955062 ) , ( 1983 , 0.0530031 ) , ( 1984 , 0.00780063 ) , ( 1985 , - 0.0241369 ) , ( 1986 , - 0.0251912 ) , ( 1987 , 0.0007525 ) , ( 1988 , 0.0577456 ) , ( 1989 , 0.115876 ) , ( 1990 , 0.127623 ) , ( 1991 , 0.107787 ) , ( 1992 , 0.0785487 ) , ( 1993 , 0.0382069 ) , ( 1994 , 0.00171938 ) , ( 1995 , - 0.0207681 ) , ( 1996 , - 0.0270988 ) , ( 1997 , - 0.00389812 ) , ( 1998 , 0.0457669 ) , ( 1999 , 0.099435 ) , ( 2000 , 0.134374 ) , ( 2001 , 0.143745 ) , ( 2002 , 0.127334 ) , ( 2003 , 0.08337 ) , ( 2004 , 0.0392613 ) , ( 2005 , 0.0124513 ) , ( 2006 , - 0.00364 ) , ( 2007 , - 0.0145513 ) , ( 2008 , - 0.0211619 ) , ( 2009 , 0.0257119 ) , ( 2010 , 0.099435 ) , ( 2011 , 0.134374 ) , ( 2012 , 0.15 ) , ( 2013 , 0.12 ) , ( 2014 , 0 ) , ( 2015 , - 0.02 ) , ( 2016 , - 0.03 ) , ( 2017 , - 0.02 ) , ( 2018 , 0 ) , ( 2019 , 0.1 ) , ( 2020 , 0.15 ) ) )
        tabidx = ftab_in_d_table['Historical_forcing_from_solar_insolation_W_p_m2'] # fetch the correct table
        idxlhs = fcol_in_mdf['Historical_forcing_from_solar_insolation_W_p_m2'] # get the location of the lhs in mdf
        look = d_table[tabidx]
        valgt = GRAPH( zeit, look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # Hydro_net_depreciation = IF_THEN_ELSE ( zeit > 2025 , Hydro_net_depreciation_multiplier_on_gen_cap * Hydro_future_net_dep_rate , 0 )
        idxlhs = fcol_in_mdf['Hydro_net_depreciation']
        idx1 = fcol_in_mdf['Hydro_net_depreciation_multiplier_on_gen_cap']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  (  zeit  >  2025  , mdf[rowi, idx1] *  Hydro_future_net_dep_rate  ,  0  ) 
    
    # Solar_sine_forcing_W_p_m2 = np.sin ( 2 * 3.14 * ( zeit - Solar_sine_forcing_offset_yr ) / Solar_sine_forcing_period_yr ) * ( Solar_sine_forcing_amplitude ) + Solar_sine_forcing_lift
        idxlhs = fcol_in_mdf['Solar_sine_forcing_W_p_m2']
        mdf[rowi, idxlhs] =  np.sin  (  2  *  3.14  *  (  zeit  -  Solar_sine_forcing_offset_yr  )  /  Solar_sine_forcing_period_yr  )  *  (  Solar_sine_forcing_amplitude  )  +  Solar_sine_forcing_lift 
    
    # Solar_cycle_W_p_m2 = IF_THEN_ELSE ( zeit > 2019 , Solar_sine_forcing_W_p_m2 , Historical_forcing_from_solar_insolation_W_p_m2 )
        idxlhs = fcol_in_mdf['Solar_cycle_W_p_m2']
        idx1 = fcol_in_mdf['Solar_sine_forcing_W_p_m2']
        idx2 = fcol_in_mdf['Historical_forcing_from_solar_insolation_W_p_m2']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  (  zeit  >  2019  , mdf[rowi, idx1] , mdf[rowi, idx2] ) 
    
    # Incoming_solar_W_p_m2 = 340 + Solar_cycle_W_p_m2
        idxlhs = fcol_in_mdf['Incoming_solar_W_p_m2']
        idx1 = fcol_in_mdf['Solar_cycle_W_p_m2']
        mdf[rowi, idxlhs] =  340  + mdf[rowi, idx1]
    
    # Incoming_solar_ZJ_py = Incoming_solar_W_p_m2 * UNIT_conversion_W_p_m2_earth_to_ZJ_py
        idxlhs = fcol_in_mdf['Incoming_solar_ZJ_py']
        idx1 = fcol_in_mdf['Incoming_solar_W_p_m2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  UNIT_conversion_W_p_m2_earth_to_ZJ_py 
    
    # Increase_in_exepi[region] = Extra_energy_productivity_index_2024_is_1[region] * ( FTPEE_rate_of_change_policy[region] / 100 ) * UNIT_conv_to_1_per_yr
        idxlhs = fcol_in_mdf['Increase_in_exepi']
        idx1 = fcol_in_mdf['Extra_energy_productivity_index_2024_is_1']
        idx2 = fcol_in_mdf['FTPEE_rate_of_change_policy']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  ( mdf[rowi , idx2:idx2 + 10] /  100  )  *  UNIT_conv_to_1_per_yr 
    
    # Increase_in_existential_minimum = IF_THEN_ELSE ( zeit > 2023 , 0 , 0 )
        idxlhs = fcol_in_mdf['Increase_in_existential_minimum']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  (  zeit  >  2023  ,  0  ,  0  ) 
    
    # Increase_in_existential_minimum_income = Indicated_Existential_minimum_income * Increase_in_existential_minimum
        idxlhs = fcol_in_mdf['Increase_in_existential_minimum_income']
        idx1 = fcol_in_mdf['Indicated_Existential_minimum_income']
        idx2 = fcol_in_mdf['Increase_in_existential_minimum']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2]
    
    # Increase_in_GDPL[region] = Public_money_from_LPB_policy[region] * ( 1 - LPBgrant_policy[region] )
        idxlhs = fcol_in_mdf['Increase_in_GDPL']
        idx1 = fcol_in_mdf['Public_money_from_LPB_policy']
        idx2 = fcol_in_mdf['LPBgrant_policy']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  1  - mdf[rowi , idx2:idx2 + 10] ) 
    
    # Increase_in_public_loan_defaults[region] = All_loan_service_obligations_to_public_lenders_not_met[region]
        idxlhs = fcol_in_mdf['Increase_in_public_loan_defaults']
        idx1 = fcol_in_mdf['All_loan_service_obligations_to_public_lenders_not_met']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10]
    
    # Not_enough_regen_cropland = IF_THEN_ELSE ( Desired_regenerative_cropland_fraction + FLWR_policy - Regenerative_cropland_fraction >= 0.03 , ( Desired_regenerative_cropland_fraction + FLWR_policy - Regenerative_cropland_fraction ) , 0 )
        idxlhs = fcol_in_mdf['Not_enough_regen_cropland']
        idx1 = fcol_in_mdf['Desired_regenerative_cropland_fraction']
        idx2 = fcol_in_mdf['FLWR_policy']
        idx3 = fcol_in_mdf['Regenerative_cropland_fraction']
        idx4 = fcol_in_mdf['Desired_regenerative_cropland_fraction']
        idx5 = fcol_in_mdf['FLWR_policy']
        idx6 = fcol_in_mdf['Regenerative_cropland_fraction']
        mdf[rowi, idxlhs:idxlhs + 10] =  IF_THEN_ELSE  ( mdf[rowi, idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] - mdf[rowi , idx3:idx3 + 10] >=  0.03  ,  ( mdf[rowi, idx4:idx4 + 10] + mdf[rowi , idx5:idx5 + 10] - mdf[rowi , idx6:idx6 + 10] )  ,  0  ) 
    
    # Increase_in_regen_cropland[region] = Not_enough_regen_cropland[region] / Time_to_implement_regen_practices * Eff_of_wealth_on_regnerative_practices[region]
        idxlhs = fcol_in_mdf['Increase_in_regen_cropland']
        idx1 = fcol_in_mdf['Not_enough_regen_cropland']
        idx2 = fcol_in_mdf['Eff_of_wealth_on_regnerative_practices']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Time_to_implement_regen_practices  * mdf[rowi, idx2:idx2 + 10]
    
    # increase_in_speculative_asset_pool[region] = MAX ( 0 , Annual_surplus_of_available_private_capital[region] + Increase_in_funds_leaked[region] )
        idxlhs = fcol_in_mdf['increase_in_speculative_asset_pool']
        idx1 = fcol_in_mdf['Annual_surplus_of_available_private_capital']
        idx2 = fcol_in_mdf['Increase_in_funds_leaked']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.maximum  (  0  , mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10] ) 
    
    # Indicated_inequality_index_with_tax[region] = Indicated_inequality_index_higher_is_more_unequal[region] / Effect_of_Worker_to_owner_income_after_tax_ratio_scaled_to_init[region]
        idxlhs = fcol_in_mdf['Indicated_inequality_index_with_tax']
        idx1 = fcol_in_mdf['Indicated_inequality_index_higher_is_more_unequal']
        idx2 = fcol_in_mdf['Effect_of_Worker_to_owner_income_after_tax_ratio_scaled_to_init']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # OSF_from_GDPpp_alone[region] = OSF_in_1980[region] * ( 1 + Slope_of_OSF_from_GDPpp_alone[region] * ( Effective_GDPpp_for_OSF[region] / GDPpp_in_1980[region] - 1 ) )
        idxlhs = fcol_in_mdf['OSF_from_GDPpp_alone']
        idx1 = fcol_in_mdf['Effective_GDPpp_for_OSF']
        mdf[rowi, idxlhs:idxlhs + 10] =  OSF_in_1980[0:10]  *  (  1  +  Slope_of_OSF_from_GDPpp_alone[0:10]  *  ( mdf[rowi , idx1:idx1 + 10] /  GDPpp_in_1980[0:10]  -  1  )  ) 
    
    # Scaled_Size_of_industrial_sector[region] = Size_of_industrial_sector[region] / Size_of_industrial_sector_in_1980[region]
        idxlhs = fcol_in_mdf['Scaled_Size_of_industrial_sector']
        idx1 = fcol_in_mdf['Size_of_industrial_sector']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Size_of_industrial_sector_in_1980[0:10] 
    
    # Indicated_OSF_with_ind_sector_effect[region] = MIN ( Max_OSF , MAX ( Min_OSF , OSF_from_GDPpp_alone[region] ) ) * Scaled_Size_of_industrial_sector[region] * Strength_of_effect_of_industrial_sector_size_on_OSF[region]
        idxlhs = fcol_in_mdf['Indicated_OSF_with_ind_sector_effect']
        idx1 = fcol_in_mdf['OSF_from_GDPpp_alone']
        idx2 = fcol_in_mdf['Scaled_Size_of_industrial_sector']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.minimum  (  Max_OSF  ,  np.maximum  (  Min_OSF  , mdf[rowi , idx1:idx1 + 10] )  )  * mdf[rowi , idx2:idx2 + 10] *  Strength_of_effect_of_industrial_sector_size_on_OSF[0:10] 
    
    # pb_Air_Pollution_global = pb_Air_Pollution_a * ( GLobal_GDP_in_terraUSD / pb_Air_Pollution_Unit_conv_to_make_LN_dmnl_from_terra_USD ) + pb_Air_Pollution_b
        idxlhs = fcol_in_mdf['pb_Air_Pollution_global']
        idx1 = fcol_in_mdf['GLobal_GDP_in_terraUSD']
        mdf[rowi, idxlhs] =  pb_Air_Pollution_a  *  ( mdf[rowi, idx1] /  pb_Air_Pollution_Unit_conv_to_make_LN_dmnl_from_terra_USD  )  +  pb_Air_Pollution_b 
    
    # Urban_aerosol_concentration_hist = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1990 , 39.7 ) , ( 1995 , 39.6 ) , ( 2000 , 40.1 ) , ( 2005 , 41 ) , ( 2010 , 41.9 ) , ( 2015 , 41.9 ) , ( 2020 , 43.5 ) ) )
        tabidx = ftab_in_d_table['Urban_aerosol_concentration_hist'] # fetch the correct table
        idxlhs = fcol_in_mdf['Urban_aerosol_concentration_hist'] # get the location of the lhs in mdf
        look = d_table[tabidx]
        valgt = GRAPH( zeit, look[:,0], look[:, 1])
        mdf[rowi, idxlhs] = valgt
    
    # Indicated_Urban_aerosol_concentration_future = IF_THEN_ELSE ( zeit >= 2020 , pb_Air_Pollution_global * UNIT_conv_to_UAC , Urban_aerosol_concentration_hist )
        idxlhs = fcol_in_mdf['Indicated_Urban_aerosol_concentration_future']
        idx1 = fcol_in_mdf['pb_Air_Pollution_global']
        idx2 = fcol_in_mdf['Urban_aerosol_concentration_hist']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  (  zeit  >=  2020  , mdf[rowi, idx1] *  UNIT_conv_to_UAC  , mdf[rowi, idx2] ) 
    
    # Recent_sales[region] = SMOOTHI ( Sales[region] , Sales_averaging_time , Demand_in_1980[region] )
        idx1 = fcol_in_mdf['Recent_sales']
        idx2 = fcol_in_mdf['Sales']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi - 1, idx1:idx1 + 10]) / Sales_averaging_time * dt
    
    # Inventory_coverage[region] = Inventory[region] / Recent_sales[region]
        idxlhs = fcol_in_mdf['Inventory_coverage']
        idx1 = fcol_in_mdf['Inventory']
        idx2 = fcol_in_mdf['Recent_sales']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # Inventory_coverage_to_goal_ratio[region] = Inventory_coverage[region] / Goal_for_inventory_coverage
        idxlhs = fcol_in_mdf['Inventory_coverage_to_goal_ratio']
        idx1 = fcol_in_mdf['Inventory_coverage']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Goal_for_inventory_coverage 
    
    # Perceived_inventory_ratio[region] = SMOOTH3 ( Inventory_coverage_to_goal_ratio[region] , Time_required_for_inventory_fluctuations_to_impact_inflation_rate )
        idxin = fcol_in_mdf['Inventory_coverage_to_goal_ratio' ]
        idx2 = fcol_in_mdf['Perceived_inventory_ratio_2']
        idx1 = fcol_in_mdf['Perceived_inventory_ratio_1']
        idxout = fcol_in_mdf['Perceived_inventory_ratio']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( Time_required_for_inventory_fluctuations_to_impact_inflation_rate / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( Time_required_for_inventory_fluctuations_to_impact_inflation_rate / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( Time_required_for_inventory_fluctuations_to_impact_inflation_rate / 3) * dt
    
    # Inflation_rate_used_only_for_interest_rate[region] = MAX ( 0 , SoE_of_inventory_on_inflation_rate[region] * ( Perceived_inventory_ratio[region] / Minimum_relative_inventory_without_inflation[region] - 1 ) )
        idxlhs = fcol_in_mdf['Inflation_rate_used_only_for_interest_rate']
        idx1 = fcol_in_mdf['Perceived_inventory_ratio']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.maximum  (  0  ,  SoE_of_inventory_on_inflation_rate[0:10]  *  ( mdf[rowi , idx1:idx1 + 10] /  Minimum_relative_inventory_without_inflation[0:10]  -  1  )  ) 
    
    # Kyoto_Fluor_degradation = Kyoto_Fluor_gases_in_atm / Time_to_degrade_Kyoto_Fluor_yr
        idxlhs = fcol_in_mdf['Kyoto_Fluor_degradation']
        idx1 = fcol_in_mdf['Kyoto_Fluor_gases_in_atm']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Time_to_degrade_Kyoto_Fluor_yr 
    
    # Laying_off_cut_off[region] = WITH LOOKUP ( Employed_to_labor_pool_ratio[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0.01 , 0 ) , ( 0.02 , 0.02 ) , ( 0.04 , 0.25 ) , ( 0.06 , 0.7 ) , ( 0.08 , 0.95 ) , ( 0.1 , 1 ) ) )
        tabidx = ftab_in_d_table['Laying_off_cut_off'] # fetch the correct table
        idx2 = fcol_in_mdf['Laying_off_cut_off'] # get the location of the lhs in mdf
        idx3 = fcol_in_mdf['Employed_to_labor_pool_ratio']
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:,0], look[:, 1])
    
    # Number_of_people_to_be_let_go[region] = MAX ( 0 , Employed[region] - Full_time_jobs_with_participation_constraint[region] )
        idxlhs = fcol_in_mdf['Number_of_people_to_be_let_go']
        idx1 = fcol_in_mdf['Employed']
        idx2 = fcol_in_mdf['Full_time_jobs_with_participation_constraint']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.maximum  (  0  , mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10] ) 
    
    # Laying_off_rate[region] = Number_of_people_to_be_let_go[region] / Time_to_implement_lay_off
        idxlhs = fcol_in_mdf['Laying_off_rate']
        idx1 = fcol_in_mdf['Number_of_people_to_be_let_go']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Time_to_implement_lay_off 
    
    # P_Pb_Phaseout_time = P_Pb_Phaseout_time_TLTL * Effect_of_GL_on_phaseout_time
        idxlhs = fcol_in_mdf['P_Pb_Phaseout_time']
        idx1 = fcol_in_mdf['Effect_of_GL_on_phaseout_time']
        mdf[rowi, idxlhs] =  P_Pb_Phaseout_time_TLTL  * mdf[rowi, idx1]
    
    # P_Pb_Phaseout_multiplier = np.exp ( - ( ( zeit - Start_year_P_Pb_phaseout ) / P_Pb_Phaseout_time ) )
        idxlhs = fcol_in_mdf['P_Pb_Phaseout_multiplier']
        idx1 = fcol_in_mdf['P_Pb_Phaseout_time']
        mdf[rowi, idxlhs] =  np.exp  (  -  (  (  zeit  -  Start_year_P_Pb_phaseout  )  / mdf[rowi, idx1] )  ) 
    
    # Lead_release_global = ( ( Lead_release_a * LN ( GLobal_GDP / Unit_conv_to_make_LN_dmnl_from_terra_USD ) - Lead_release_b ) * P_Pb_Phaseout_multiplier ) * Lead_UNIT_conv_to_Mt_pr_yr
        idxlhs = fcol_in_mdf['Lead_release_global']
        idx1 = fcol_in_mdf['GLobal_GDP']
        idx2 = fcol_in_mdf['P_Pb_Phaseout_multiplier']
        mdf[rowi, idxlhs] =  (  (  Lead_release_a  *  np.log  ( mdf[rowi, idx1] /  Unit_conv_to_make_LN_dmnl_from_terra_USD  )  -  Lead_release_b  )  * mdf[rowi, idx2] )  *  Lead_UNIT_conv_to_Mt_pr_yr 
    
    # Leaving_the_labor_pool_limitation[region] = WITH LOOKUP ( Unemployed_to_labor_pool_ratio[region] , ( [ ( 0 , 0 ) - ( 0.55382 , 39.1651 ) ] , ( 0.01 , 0 ) , ( 0.02 , 0.02 ) , ( 0.04 , 0.25 ) , ( 0.06 , 0.7 ) , ( 0.08 , 0.95 ) , ( 0.1 , 1 ) ) )
        tabidx = ftab_in_d_table['Leaving_the_labor_pool_limitation'] # fetch the correct table
        idx2 = fcol_in_mdf['Leaving_the_labor_pool_limitation'] # get the location of the lhs in mdf
        idx3 = fcol_in_mdf['Unemployed_to_labor_pool_ratio']
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:,0], look[:, 1])
    
    # Leaving_the_labor_pool[region] = ( People_considering_leaving_the_pool[region] / Time_to_implement_actually_leaving_the_pool ) * Leaving_the_labor_pool_limitation[region]
        idxlhs = fcol_in_mdf['Leaving_the_labor_pool']
        idx1 = fcol_in_mdf['People_considering_leaving_the_pool']
        idx2 = fcol_in_mdf['Leaving_the_labor_pool_limitation']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] /  Time_to_implement_actually_leaving_the_pool  )  * mdf[rowi, idx2:idx2 + 10]
    
    # Private_investment_share[region] = ( Private_Investment_in_new_capacity[region] - Funds_from_private_investment_leaked[region] ) / Eff_of_env_damage_on_cost_of_new_capacity[region] / GDP_USED[region]
        idxlhs = fcol_in_mdf['Private_investment_share']
        idx1 = fcol_in_mdf['Private_Investment_in_new_capacity']
        idx2 = fcol_in_mdf['Funds_from_private_investment_leaked']
        idx3 = fcol_in_mdf['Eff_of_env_damage_on_cost_of_new_capacity']
        idx4 = fcol_in_mdf['GDP_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10] )  / mdf[rowi , idx3:idx3 + 10] / mdf[rowi , idx4:idx4 + 10]
    
    # Local_private_and_govt_investment_share[region] = Govt_investment_share[region] + Private_investment_share[region]
        idxlhs = fcol_in_mdf['Local_private_and_govt_investment_share']
        idx1 = fcol_in_mdf['Govt_investment_share']
        idx2 = fcol_in_mdf['Private_investment_share']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10]
    
    # Loosing_a_job[region] = Laying_off_rate[region] * Laying_off_cut_off[region]
        idxlhs = fcol_in_mdf['Loosing_a_job']
        idx1 = fcol_in_mdf['Laying_off_rate']
        idx2 = fcol_in_mdf['Laying_off_cut_off']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi, idx2:idx2 + 10]
    
    # LPB_investment_share[region] = ( ( ( 1 - Future_leakage[region] ) * Public_money_from_LPB_policy_to_investment[region] ) / Eff_of_env_damage_on_cost_of_new_capacity[region] ) / GDP_USED[region]
        idxlhs = fcol_in_mdf['LPB_investment_share']
        idx1 = fcol_in_mdf['Future_leakage']
        idx2 = fcol_in_mdf['Public_money_from_LPB_policy_to_investment']
        idx3 = fcol_in_mdf['Eff_of_env_damage_on_cost_of_new_capacity']
        idx4 = fcol_in_mdf['GDP_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  (  (  (  1  - mdf[rowi , idx1:idx1 + 10] )  * mdf[rowi , idx2:idx2 + 10] )  / mdf[rowi , idx3:idx3 + 10] )  / mdf[rowi , idx4:idx4 + 10]
    
    # Net_growth_in_forest_area[region] = ( Forest_land[region] - Forest_area_last_year[region] ) / One_year
        idxlhs = fcol_in_mdf['Net_growth_in_forest_area']
        idx1 = fcol_in_mdf['Forest_land']
        idx2 = fcol_in_mdf['Forest_area_last_year']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10] )  /  One_year 
    
    # Net_growth_in_forest_area_causing_CO2_emissions_resp_absorption[region] = SMOOTH3 ( Net_growth_in_forest_area[region] , Time_to_adjust_forest_area_to_CO2_emissions )
        idxin = fcol_in_mdf['Net_growth_in_forest_area' ]
        idx2 = fcol_in_mdf['Net_growth_in_forest_area_causing_CO2_emissions_resp_absorption_2']
        idx1 = fcol_in_mdf['Net_growth_in_forest_area_causing_CO2_emissions_resp_absorption_1']
        idxout = fcol_in_mdf['Net_growth_in_forest_area_causing_CO2_emissions_resp_absorption']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( Time_to_adjust_forest_area_to_CO2_emissions / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( Time_to_adjust_forest_area_to_CO2_emissions / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( Time_to_adjust_forest_area_to_CO2_emissions / 3) * dt
    
    # LW_surface_emission = BB_radiation_at_surface_temp_ZJ_py
        idxlhs = fcol_in_mdf['LW_surface_emission']
        idx1 = fcol_in_mdf['BB_radiation_at_surface_temp_ZJ_py']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # LW_surface_emissions_escaping_through_atm_window = LW_surface_emission * Frac_of_surface_emission_through_atm_window
        idxlhs = fcol_in_mdf['LW_surface_emissions_escaping_through_atm_window']
        idx1 = fcol_in_mdf['LW_surface_emission']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Frac_of_surface_emission_through_atm_window 
    
    # LW_Clear_sky_emissions_from_atm = ( BB_radiation_at_Temp_in_atm_ZJ_py + LW_surface_emissions_escaping_through_atm_window ) * ( 1 - Frac_blocked_by_ALL_GHG )
        idxlhs = fcol_in_mdf['LW_Clear_sky_emissions_from_atm']
        idx1 = fcol_in_mdf['BB_radiation_at_Temp_in_atm_ZJ_py']
        idx2 = fcol_in_mdf['LW_surface_emissions_escaping_through_atm_window']
        idx3 = fcol_in_mdf['Frac_blocked_by_ALL_GHG']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] + mdf[rowi, idx2] )  *  (  1  - mdf[rowi, idx3] ) 
    
    # LW_clear_sky_emissions_to_surface = BB_radiation_at_Temp_in_atm_ZJ_py
        idxlhs = fcol_in_mdf['LW_clear_sky_emissions_to_surface']
        idx1 = fcol_in_mdf['BB_radiation_at_Temp_in_atm_ZJ_py']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # LW_Cloudy_sky_emissions_from_atm = LW_Clear_sky_emissions_from_atm - Blocking_of_LW_rad_by_clouds
        idxlhs = fcol_in_mdf['LW_Cloudy_sky_emissions_from_atm']
        idx1 = fcol_in_mdf['LW_Clear_sky_emissions_from_atm']
        idx2 = fcol_in_mdf['Blocking_of_LW_rad_by_clouds']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] - mdf[rowi, idx2]
    
    # LW_re_radiated_by_clouds = LW_LO_cloud_radiation + LW_HI_cloud_radiation
        idxlhs = fcol_in_mdf['LW_re_radiated_by_clouds']
        idx1 = fcol_in_mdf['LW_LO_cloud_radiation']
        idx2 = fcol_in_mdf['LW_HI_cloud_radiation']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2]
    
    # LW_surface_emissions_NOT_escaping_through_atm_window = LW_surface_emission * ( 1 - Frac_of_surface_emission_through_atm_window )
        idxlhs = fcol_in_mdf['LW_surface_emissions_NOT_escaping_through_atm_window']
        idx1 = fcol_in_mdf['LW_surface_emission']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  (  1  -  Frac_of_surface_emission_through_atm_window  ) 
    
    # LW_TOA_radiation_from_atm_to_space = LW_Cloudy_sky_emissions_from_atm
        idxlhs = fcol_in_mdf['LW_TOA_radiation_from_atm_to_space']
        idx1 = fcol_in_mdf['LW_Cloudy_sky_emissions_from_atm']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # Model_Volcanic_aerosol_forcing_W_p_m2 = Volcanic_aerosols_in_stratosphere / Time_for_volcanic_aerosols_to_remain_in_the_stratosphere * Conversion_of_volcanic_aerosol_forcing_to_volcanic_aerosol_emissions
        idxlhs = fcol_in_mdf['Model_Volcanic_aerosol_forcing_W_p_m2']
        idx1 = fcol_in_mdf['Volcanic_aerosols_in_stratosphere']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Time_for_volcanic_aerosols_to_remain_in_the_stratosphere  *  Conversion_of_volcanic_aerosol_forcing_to_volcanic_aerosol_emissions 
    
    # Montreal_gases_degradation = Montreal_gases_in_atm / Time_to_degrade_Montreal_gases_yr
        idxlhs = fcol_in_mdf['Montreal_gases_degradation']
        idx1 = fcol_in_mdf['Montreal_gases_in_atm']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Time_to_degrade_Montreal_gases_yr 
     
    # Nitrogen_syn_use_global = SUM ( Nitrogen_syn_use[region!] )
        idxlhs = fcol_in_mdf['Nitrogen_syn_use_global']
        idx1 = fcol_in_mdf['Nitrogen_syn_use']
        globsum = 0
        for j in range(0,10):
            globsum = globsum + mdf[rowi, idx1 + j]
        mdf[rowi, idxlhs] = globsum 
    
    # N_pb_overloading = Nitrogen_syn_use_global / Nitrogen_PB_green_threshold
        idxlhs = fcol_in_mdf['N_pb_overloading']
        idx1 = fcol_in_mdf['Nitrogen_syn_use_global']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Nitrogen_PB_green_threshold 
    
    # N2O_degradation_MtN2O_py = N2O_in_atmosphere_MtN2O / Time_to_degrade_N2O_in_atmopshere_yr
        idxlhs = fcol_in_mdf['N2O_degradation_MtN2O_py']
        idx1 = fcol_in_mdf['N2O_in_atmosphere_MtN2O']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Time_to_degrade_N2O_in_atmopshere_yr 
    
    # Net_change_in_OSF[region] = ( Indicated_OSF_with_ind_sector_effect[region] - Owner_saving_fraction[region] ) / Time_to_adjust_owner_investment_behaviour_in_productive_assets
        idxlhs = fcol_in_mdf['Net_change_in_OSF']
        idx1 = fcol_in_mdf['Indicated_OSF_with_ind_sector_effect']
        idx2 = fcol_in_mdf['Owner_saving_fraction']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10] )  /  Time_to_adjust_owner_investment_behaviour_in_productive_assets 
    
    # Temp_ocean_surface_in_K = Temp_surface_average_K - Temp_gradient_in_surface_degK
        idxlhs = fcol_in_mdf['Temp_ocean_surface_in_K']
        idx1 = fcol_in_mdf['Temp_surface_average_K']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] -  Temp_gradient_in_surface_degK 
    
    # Surface_deep_ocean_temp_diff_degC = Temp_ocean_surface_in_K - Temp_ocean_deep_in_K
        idxlhs = fcol_in_mdf['Surface_deep_ocean_temp_diff_degC']
        idx1 = fcol_in_mdf['Temp_ocean_surface_in_K']
        idx2 = fcol_in_mdf['Temp_ocean_deep_in_K']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] - mdf[rowi, idx2]
    
    # Net_heat_flow_ocean_from_surface_to_deep_ZJ_py = Surface_deep_ocean_temp_diff_degC * Net_heat_flow_ocean_between_surface_and_deep_per_K_of_difference_ZJ_py_K
        idxlhs = fcol_in_mdf['Net_heat_flow_ocean_from_surface_to_deep_ZJ_py']
        idx1 = fcol_in_mdf['Surface_deep_ocean_temp_diff_degC']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Net_heat_flow_ocean_between_surface_and_deep_per_K_of_difference_ZJ_py_K 
    
    # net_migration_function[region] = nmf_a[region] * LN ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl ) + nmf_b[region] + nmf_c[region]
        idxlhs = fcol_in_mdf['net_migration_function']
        idx1 = fcol_in_mdf['GDPpp_USED']
        mdf[rowi, idxlhs:idxlhs + 10] =  nmf_a[0:10]  *  np.log  ( mdf[rowi , idx1:idx1 + 10] *  UNIT_conv_to_make_exp_dmnl  )  +  nmf_b[0:10]  +  nmf_c[0:10] 
    
    # net_migration_10_to_14[region] = Migration_fraction_10_to_14_cohort[region] * net_migration_function[region] * Factor_to_account_for_net_migration_not_officially_recorded[region]
        idxlhs = fcol_in_mdf['net_migration_10_to_14']
        idx1 = fcol_in_mdf['net_migration_function']
        mdf[rowi, idxlhs:idxlhs + 10] =  Migration_fraction_10_to_14_cohort[0:10]  * mdf[rowi , idx1:idx1 + 10] *  Factor_to_account_for_net_migration_not_officially_recorded[0:10] 
    
    # net_migration_20_to_24[region] = net_migration_function[region] * Migration_fraction_20_to_24_cohort[region] * Factor_to_account_for_net_migration_not_officially_recorded[region]
        idxlhs = fcol_in_mdf['net_migration_20_to_24']
        idx1 = fcol_in_mdf['net_migration_function']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  Migration_fraction_20_to_24_cohort[0:10]  *  Factor_to_account_for_net_migration_not_officially_recorded[0:10] 
    
    # net_migration_25_to_29[region] = Migration_fraction_25_to_29_cohort[region] * net_migration_function[region] * Factor_to_account_for_net_migration_not_officially_recorded[region]
        idxlhs = fcol_in_mdf['net_migration_25_to_29']
        idx1 = fcol_in_mdf['net_migration_function']
        mdf[rowi, idxlhs:idxlhs + 10] =  Migration_fraction_25_to_29_cohort[0:10]  * mdf[rowi , idx1:idx1 + 10] *  Factor_to_account_for_net_migration_not_officially_recorded[0:10] 
    
    # net_migration_30_to_34[region] = net_migration_function[region] * Migration_fraction_30_to_34_cohort[region] * Factor_to_account_for_net_migration_not_officially_recorded[region]
        idxlhs = fcol_in_mdf['net_migration_30_to_34']
        idx1 = fcol_in_mdf['net_migration_function']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  Migration_fraction_30_to_34_cohort[0:10]  *  Factor_to_account_for_net_migration_not_officially_recorded[0:10] 
    
    # Use_of_NF_biomass_for_construction = Use_of_NF_for_construction_in_2000_GtBiomass * Effect_of_population_and_urbanization_on_biomass_use * UNIT_conversion_1_py
        idxlhs = fcol_in_mdf['Use_of_NF_biomass_for_construction']
        idx1 = fcol_in_mdf['Effect_of_population_and_urbanization_on_biomass_use']
        mdf[rowi, idxlhs] =  Use_of_NF_for_construction_in_2000_GtBiomass  * mdf[rowi, idx1] *  UNIT_conversion_1_py 
    
    # NF_for_construction_use = Use_of_NF_biomass_for_construction
        idxlhs = fcol_in_mdf['NF_for_construction_use']
        idx1 = fcol_in_mdf['Use_of_NF_biomass_for_construction']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # NF_Living_biomass_rotting = NF_Living_biomass_GtBiomass / NF_Avg_life_biomass_yr
        idxlhs = fcol_in_mdf['NF_Living_biomass_rotting']
        idx1 = fcol_in_mdf['NF_Living_biomass_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  NF_Avg_life_biomass_yr 
    
    # NF_regrowing_after_being_burnt_Mkm2_py = NF_area_burnt_Mkm2 / Time_to_regrow_NF_yr
        idxlhs = fcol_in_mdf['NF_regrowing_after_being_burnt_Mkm2_py']
        idx1 = fcol_in_mdf['NF_area_burnt_Mkm2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Time_to_regrow_NF_yr 
    
    # NF_regrowing_after_being_clear_cut_Mkm2_py = NF_area_clear_cut_Mkm2 / ( Time_to_regrow_NF_yr * 2 )
        idxlhs = fcol_in_mdf['NF_regrowing_after_being_clear_cut_Mkm2_py']
        idx1 = fcol_in_mdf['NF_area_clear_cut_Mkm2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  (  Time_to_regrow_NF_yr  *  2  ) 
    
    # NF_regrowing_after_being_deforested_Mkm2_py = NF_area_deforested_Mkm2 / Time_to_regrow_NF_after_deforesting_yr
        idxlhs = fcol_in_mdf['NF_regrowing_after_being_deforested_Mkm2_py']
        idx1 = fcol_in_mdf['NF_area_deforested_Mkm2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Time_to_regrow_NF_after_deforesting_yr 
    
    # NF_regrowing_after_harvesting_Mkm2_py = NF_area_harvested_Mkm2 / Time_to_regrow_NF_yr
        idxlhs = fcol_in_mdf['NF_regrowing_after_harvesting_Mkm2_py']
        idx1 = fcol_in_mdf['NF_area_harvested_Mkm2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Time_to_regrow_NF_yr 
    
    # NF_TUNDRA_Biomass_in_construction_material_left_to_rot = NF_Biomass_locked_in_construction_material_GtBiomass / NF_Avg_life_of_building_yr * ( 1 - NF_Fraction_of_construction_waste_burned_0_to_1 )
        idxlhs = fcol_in_mdf['NF_TUNDRA_Biomass_in_construction_material_left_to_rot']
        idx1 = fcol_in_mdf['NF_Biomass_locked_in_construction_material_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  NF_Avg_life_of_building_yr  *  (  1  -  NF_Fraction_of_construction_waste_burned_0_to_1  ) 
    
    # Nitrogen_risk_score = IF_THEN_ELSE ( Nitrogen_syn_use_global > Nitrogen_PB_green_threshold , 1 , 0 )
        idxlhs = fcol_in_mdf['Nitrogen_risk_score']
        idx1 = fcol_in_mdf['Nitrogen_syn_use_global']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  ( mdf[rowi, idx1] >  Nitrogen_PB_green_threshold  ,  1  ,  0  ) 
    
    # Nitrogen_use_per_ha[region] = Nitrogen_syn_use[region] / Cropland[region]
        idxlhs = fcol_in_mdf['Nitrogen_use_per_ha']
        idx1 = fcol_in_mdf['Nitrogen_syn_use']
        idx2 = fcol_in_mdf['Cropland']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # Nuclear_net_depreciation = IF_THEN_ELSE ( zeit > 2025 , Nuclear_net_depreciation_multiplier_on_gen_cap * Nuclear_future_net_dep_rate , 0 )
        idxlhs = fcol_in_mdf['Nuclear_net_depreciation']
        idx1 = fcol_in_mdf['Nuclear_net_depreciation_multiplier_on_gen_cap']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  (  zeit  >  2025  , mdf[rowi, idx1] *  Nuclear_future_net_dep_rate  ,  0  ) 
    
    # Phosphorous_release_global = ( ( P_release_a * LN ( GLobal_GDP / Unit_conv_to_make_LN_dmnl_from_terra_USD ) - P_release_b ) * P_Pb_Phaseout_multiplier ) * UNIT_conv_to_Mt_pr_yr
        idxlhs = fcol_in_mdf['Phosphorous_release_global']
        idx1 = fcol_in_mdf['GLobal_GDP']
        idx2 = fcol_in_mdf['P_Pb_Phaseout_multiplier']
        mdf[rowi, idxlhs] =  (  (  P_release_a  *  np.log  ( mdf[rowi, idx1] /  Unit_conv_to_make_LN_dmnl_from_terra_USD  )  -  P_release_b  )  * mdf[rowi, idx2] )  *  UNIT_conv_to_Mt_pr_yr 
    
    # Phosphorous_risk_score = IF_THEN_ELSE ( Phosphorous_release_global > Phosphorous_PB_green_threshold , 1 , 0 )
        idxlhs = fcol_in_mdf['Phosphorous_risk_score']
        idx1 = fcol_in_mdf['Phosphorous_release_global']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  ( mdf[rowi, idx1] >  Phosphorous_PB_green_threshold  ,  1  ,  0  ) 
    
    # Nutrient_risk_score = ( Nitrogen_risk_score + Phosphorous_risk_score ) / 2
        idxlhs = fcol_in_mdf['Nutrient_risk_score']
        idx1 = fcol_in_mdf['Nitrogen_risk_score']
        idx2 = fcol_in_mdf['Phosphorous_risk_score']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] + mdf[rowi, idx2] )  /  2 
    
    # Ocean_heat_used_for_melting_ZJ_py = ( Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_antarctic_ice_ZJ_py + Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_arctic_ice_ZJ_py ) / Heat_in_surface
        idxlhs = fcol_in_mdf['Ocean_heat_used_for_melting_ZJ_py']
        idx1 = fcol_in_mdf['Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_antarctic_ice_ZJ_py']
        idx2 = fcol_in_mdf['Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_arctic_ice_ZJ_py']
        idx3 = fcol_in_mdf['Heat_in_surface']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] + mdf[rowi, idx2] )  / mdf[rowi, idx3]
    
    # Output_last_year[region] = SMOOTHI ( Optimal_real_output[region] , One_year , Output_last_year_in_1980[region] )
        idx1 = fcol_in_mdf['Output_last_year']
        idx2 = fcol_in_mdf['Optimal_real_output']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi - 1, idx1:idx1 + 10]) / One_year * dt
    
    # Output_growth_rate_instant[region] = ( Optimal_real_output[region] - Output_last_year[region] ) / Output_last_year[region] / One_year
        idxlhs = fcol_in_mdf['Output_growth_rate_instant']
        idx1 = fcol_in_mdf['Optimal_real_output']
        idx2 = fcol_in_mdf['Output_last_year']
        idx3 = fcol_in_mdf['Output_last_year']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10] )  / mdf[rowi , idx3:idx3 + 10] /  One_year 
    
    # Owner_cash_inflow_with_lending_transactions[region] = Owner_income_after_tax_but_before_lending_transactions[region] + Owner_income_from_lending_activity[region]
        idxlhs = fcol_in_mdf['Owner_cash_inflow_with_lending_transactions']
        idx1 = fcol_in_mdf['Owner_income_after_tax_but_before_lending_transactions']
        idx2 = fcol_in_mdf['Owner_income_from_lending_activity']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] + mdf[rowi , idx2:idx2 + 10]
    
    # Owner_wealth_accumulation_fraction[region] = WACC_fraction[region] * Fraction_of_owner_income_left_for_consumption_or_wealth_accumulation[region]
        idxlhs = fcol_in_mdf['Owner_wealth_accumulation_fraction']
        idx1 = fcol_in_mdf['WACC_fraction']
        idx2 = fcol_in_mdf['Fraction_of_owner_income_left_for_consumption_or_wealth_accumulation']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # Owner_wealth_accumulating[region] = Owner_cash_inflow_seasonally_adjusted[region] * Owner_wealth_accumulation_fraction[region]
        idxlhs = fcol_in_mdf['Owner_wealth_accumulating']
        idx1 = fcol_in_mdf['Owner_cash_inflow_seasonally_adjusted']
        idx2 = fcol_in_mdf['Owner_wealth_accumulation_fraction']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi , idx2:idx2 + 10]
    
    # Release_of_Montreal_gases = Montreal_gases_emissions / UNIT_conversion_to_M
        idxlhs = fcol_in_mdf['Release_of_Montreal_gases']
        idx1 = fcol_in_mdf['Montreal_gases_emissions']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  UNIT_conversion_to_M 
    
    # pb_Ozone_depletion = Release_of_Montreal_gases * Effect_of_population_on_forest_degradation_and_biocapacity
        idxlhs = fcol_in_mdf['pb_Ozone_depletion']
        idx1 = fcol_in_mdf['Release_of_Montreal_gases']
        idx2 = fcol_in_mdf['Effect_of_population_on_forest_degradation_and_biocapacity']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2]
    
    # Ozone_depletion_risk_score = IF_THEN_ELSE ( pb_Ozone_depletion > pb_Ozone_depletion_green_threshold , 1 , 0 )
        idxlhs = fcol_in_mdf['Ozone_depletion_risk_score']
        idx1 = fcol_in_mdf['pb_Ozone_depletion']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  ( mdf[rowi, idx1] >  pb_Ozone_depletion_green_threshold  ,  1  ,  0  ) 
    
    # Past_Living_conditions_index_with_env_damage[region] = SMOOTH ( Living_conditions_index_with_env_damage[region] , Social_tension_perception_delay )
        idx1 = fcol_in_mdf['Past_Living_conditions_index_with_env_damage']
        idx2 = fcol_in_mdf['Living_conditions_index_with_env_damage']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1+10] + ( mdf[rowi-1 , idx2:idx2 + 10] - mdf[rowi -1 , idx1:idx1 + 10]) / Social_tension_perception_delay * dt
    
    # pb_Air_Pollution_overloading = Smoothed_Urban_aerosol_concentration_future / pb_Urban_aerosol_concentration_green_threshold
        idxlhs = fcol_in_mdf['pb_Air_Pollution_overloading']
        idx1 = fcol_in_mdf['Smoothed_Urban_aerosol_concentration_future']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  pb_Urban_aerosol_concentration_green_threshold 
    
    # pb_Biodiversity_loss_overloading = Biocapacity_fraction_unused / pb_Biodiversity_loss_green_threshold
        idxlhs = fcol_in_mdf['pb_Biodiversity_loss_overloading']
        idx1 = fcol_in_mdf['Biocapacity_fraction_unused']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  pb_Biodiversity_loss_green_threshold 
    
    # pb_Forest_degradation_overloading = pb_Forest_degradation / pb_Forest_degradation_green_threshold
        idxlhs = fcol_in_mdf['pb_Forest_degradation_overloading']
        idx1 = fcol_in_mdf['pb_Forest_degradation']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  pb_Forest_degradation_green_threshold 
    
    # pb_Freshwater_withdrawal_overloading = pb_Freshwater_withdrawal_global / pb_Freshwater_withdrawal_green_threshold
        idxlhs = fcol_in_mdf['pb_Freshwater_withdrawal_overloading']
        idx1 = fcol_in_mdf['pb_Freshwater_withdrawal_global']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  pb_Freshwater_withdrawal_green_threshold 
    
    # pb_Global_warming_overloading = pb_Global_Warming / pb_Global_Warming_green_threshold
        idxlhs = fcol_in_mdf['pb_Global_warming_overloading']
        idx1 = fcol_in_mdf['pb_Global_Warming']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  pb_Global_Warming_green_threshold 
    
    # Phosphorous_overloading = Phosphorous_release_global / Phosphorous_PB_green_threshold
        idxlhs = fcol_in_mdf['Phosphorous_overloading']
        idx1 = fcol_in_mdf['Phosphorous_release_global']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Phosphorous_PB_green_threshold 
    
    # pb_Nutrient_overloading = ( N_pb_overloading + Phosphorous_overloading ) / 2
        idxlhs = fcol_in_mdf['pb_Nutrient_overloading']
        idx1 = fcol_in_mdf['N_pb_overloading']
        idx2 = fcol_in_mdf['Phosphorous_overloading']
        mdf[rowi, idxlhs] =  ( mdf[rowi, idx1] + mdf[rowi, idx2] )  /  2 
    
    # pb_Ocean_acidification_overloading = pb_Ocean_acidification_green_threshold / pb_Ocean_acidification
        idxlhs = fcol_in_mdf['pb_Ocean_acidification_overloading']
        idx1 = fcol_in_mdf['pb_Ocean_acidification']
        mdf[rowi, idxlhs] =  pb_Ocean_acidification_green_threshold  / mdf[rowi, idx1]
    
    # pb_Ozone_depletion_overloading = pb_Ozone_depletion / pb_Ozone_depletion_green_threshold
        idxlhs = fcol_in_mdf['pb_Ozone_depletion_overloading']
        idx1 = fcol_in_mdf['pb_Ozone_depletion']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  pb_Ozone_depletion_green_threshold 
    
    # PB_Toxic_entities = Lead_release_global / Lead_PB_green_threshold
        idxlhs = fcol_in_mdf['PB_Toxic_entities']
        idx1 = fcol_in_mdf['Lead_release_global']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Lead_PB_green_threshold 
    
    # PB_Toxic_risk_score = IF_THEN_ELSE ( Lead_release_global > Lead_PB_green_threshold , 1 , 0 )
        idxlhs = fcol_in_mdf['PB_Toxic_risk_score']
        idx1 = fcol_in_mdf['Lead_release_global']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  ( mdf[rowi, idx1] >  Lead_PB_green_threshold  ,  1  ,  0  ) 
    
    # pl_to_apl[region] = abs ( MIN ( 0 , Populated_land_gap[region] ) ) / Time_for_urban_land_to_become_abandoned
        idxlhs = fcol_in_mdf['pl_to_apl']
        idx1 = fcol_in_mdf['Populated_land_gap']
        mdf[rowi, idxlhs:idxlhs + 10] =  abs  (  np.minimum  (  0  , mdf[rowi , idx1:idx1 + 10] )  )  /  Time_for_urban_land_to_become_abandoned 
    
    # Planetary_risk = Acidification_risk_score + Air_Pollution_risk_score + Biocapacity_risk_score + Forest_degradation_risk_score + Freshwater_withdrawal_risk_score + Global_warming_risk_score + Nutrient_risk_score + Ozone_depletion_risk_score + PB_Toxic_risk_score
        idxlhs = fcol_in_mdf['Planetary_risk']
        idx1 = fcol_in_mdf['Acidification_risk_score']
        idx2 = fcol_in_mdf['Air_Pollution_risk_score']
        idx3 = fcol_in_mdf['Biocapacity_risk_score']
        idx4 = fcol_in_mdf['Forest_degradation_risk_score']
        idx5 = fcol_in_mdf['Freshwater_withdrawal_risk_score']
        idx6 = fcol_in_mdf['Global_warming_risk_score']
        idx7 = fcol_in_mdf['Nutrient_risk_score']
        idx8 = fcol_in_mdf['Ozone_depletion_risk_score']
        idx9 = fcol_in_mdf['PB_Toxic_risk_score']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] + mdf[rowi, idx4] + mdf[rowi, idx5] + mdf[rowi, idx6] + mdf[rowi, idx7] + mdf[rowi, idx8] + mdf[rowi, idx9]
    
    # Populated_land_last_year[region] = SMOOTH3 ( Populated_land[region] , One_year )
        idxin = fcol_in_mdf['Populated_land' ]
        idx2 = fcol_in_mdf['Populated_land_last_year_2']
        idx1 = fcol_in_mdf['Populated_land_last_year_1']
        idxout = fcol_in_mdf['Populated_land_last_year']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( One_year / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( One_year / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( One_year / 3) * dt
    
    # Population_last_year[region] = SMOOTH3I ( Population[region] , One_year , Population_in_1979[region] )
        idxlhs = fcol_in_mdf['Population_last_year']
        idxin = fcol_in_mdf['Population']
        idx2 = fcol_in_mdf['Population_last_year_2']
        idx1 = fcol_in_mdf['Population_last_year_1']
        idxout = fcol_in_mdf['Population_last_year']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( One_year / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( One_year / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( One_year / 3) * dt
    
    # Population_over_50_still_working[region] = Cohort_50plus[region] * Fraction_of_population_over_50_still_working[region]
        idxlhs = fcol_in_mdf['Population_over_50_still_working']
        idx1 = fcol_in_mdf['Cohort_50plus']
        idx2 = fcol_in_mdf['Fraction_of_population_over_50_still_working']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] * mdf[rowi, idx2:idx2 + 10]
    
    # Raw_Effect_of_poverty_on_social_tension[region] = Effect_of_poverty_on_social_tension[region] / Effect_of_poverty_on_social_tension_in_1980[region]
        idxlhs = fcol_in_mdf['Raw_Effect_of_poverty_on_social_tension']
        idx1 = fcol_in_mdf['Effect_of_poverty_on_social_tension']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi, idx1:idx1 + 10] /  Effect_of_poverty_on_social_tension_in_1980[0:10] 
    
    # REFOREST_policy_used[region] = REFOREST_policy[region] / 1 * UNIT_conv_to_1_per_yr
        idxlhs = fcol_in_mdf['REFOREST_policy_used']
        idx1 = fcol_in_mdf['REFOREST_policy']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  1  *  UNIT_conv_to_1_per_yr 
    
    # Reforestation_cutoff_from_lack_of_barren_land[region] = WITH LOOKUP ( Barren_land_which_is_ice_and_snow[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 0 ) , ( 10 , 0 ) , ( 20 , 0.06 ) , ( 30 , 0.2 ) , ( 40 , 0.5 ) , ( 50 , 0.8 ) , ( 60 , 0.95 ) , ( 70 , 1 ) ) )
        tabidx = ftab_in_d_table['Reforestation_cutoff_from_lack_of_barren_land'] # fetch the correct table
        idx2 = fcol_in_mdf['Reforestation_cutoff_from_lack_of_barren_land'] # get the location of the lhs in mdf
        idx3 = fcol_in_mdf['Barren_land_which_is_ice_and_snow']
        look = d_table[tabidx]
        for j in range(0,10):
            mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:,0], look[:, 1])
    
    # Reforestation_policy[region] = Forest_land[region] * ( REFOREST_policy_used[region] ) * Reforestation_cutoff_from_lack_of_barren_land[region]
        idxlhs = fcol_in_mdf['Reforestation_policy']
        idx1 = fcol_in_mdf['Forest_land']
        idx2 = fcol_in_mdf['REFOREST_policy_used']
        idx3 = fcol_in_mdf['Reforestation_cutoff_from_lack_of_barren_land']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  ( mdf[rowi , idx2:idx2 + 10] )  * mdf[rowi, idx3:idx3 + 10]
    
    # Renewable_energy_share_in_the_total_final_energy_consumption[region] = El_from_wind_and_PV[region] / ( El_from_all_sources[region] + Fossil_fuel_for_NON_El_use_that_IS_NOT_being_electrified[region] * Conversion_Mtoe_to_TWh[region] )
        idxlhs = fcol_in_mdf['Renewable_energy_share_in_the_total_final_energy_consumption']
        idx1 = fcol_in_mdf['El_from_wind_and_PV']
        idx2 = fcol_in_mdf['El_from_all_sources']
        idx3 = fcol_in_mdf['Fossil_fuel_for_NON_El_use_that_IS_NOT_being_electrified']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  ( mdf[rowi , idx2:idx2 + 10] + mdf[rowi , idx3:idx3 + 10] *  Conversion_Mtoe_to_TWh[0:10]  ) 
    
    # Time_to_implement_UN_policies[region] = Normal_Time_to_implement_UN_policies / Smoothed_Reform_willingness[region]
        idxlhs = fcol_in_mdf['Time_to_implement_UN_policies']
        idx1 = fcol_in_mdf['Smoothed_Reform_willingness']
        mdf[rowi, idxlhs:idxlhs + 10] =  Normal_Time_to_implement_UN_policies  / mdf[rowi , idx1:idx1 + 10]
    
    # RIPLGF_smoothing_time[region] = Time_to_implement_UN_policies[region] + RIPLGF_Addl_time_to_shift_govt_expenditure
        idxlhs = fcol_in_mdf['RIPLGF_smoothing_time']
        idx1 = fcol_in_mdf['Time_to_implement_UN_policies']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] +  RIPLGF_Addl_time_to_shift_govt_expenditure 
    
    # RoC_in_Forest_land[region] = Forest_land[region] / Forest_land_last_year[region] - 1
        idxlhs = fcol_in_mdf['RoC_in_Forest_land']
        idx1 = fcol_in_mdf['Forest_land']
        idx2 = fcol_in_mdf['Forest_land_last_year']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10] -  1 
    
    # RoC_in_Forest_land_geglaettet[region] = RoC_in_Forest_land[region]
        idxlhs = fcol_in_mdf['RoC_in_Forest_land_geglaettet']
        idx1 = fcol_in_mdf['RoC_in_Forest_land']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10]
    
    # RoC_in_GDPpp[region] = ( GDPpp_model[region] - GDPpp_model_One_yr_ago[region] ) / GDPpp_model_One_yr_ago[region] / One_year
        idxlhs = fcol_in_mdf['RoC_in_GDPpp']
        idx1 = fcol_in_mdf['GDPpp_model']
        idx2 = fcol_in_mdf['GDPpp_model_One_yr_ago']
        idx3 = fcol_in_mdf['GDPpp_model_One_yr_ago']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10] )  / mdf[rowi , idx3:idx3 + 10] /  One_year 
    
    # RoC_in_Living_conditions_index_with_env_damage[region] = ( Living_conditions_index_with_env_damage[region] - Past_Living_conditions_index_with_env_damage[region] ) / Social_tension_perception_delay
        idxlhs = fcol_in_mdf['RoC_in_Living_conditions_index_with_env_damage']
        idx1 = fcol_in_mdf['Living_conditions_index_with_env_damage']
        idx2 = fcol_in_mdf['Past_Living_conditions_index_with_env_damage']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10] )  /  Social_tension_perception_delay 
    
    # RoC_Populated_land[region] = ( Populated_land[region] - Populated_land_last_year[region] ) / Populated_land_last_year[region] / One_year
        idxlhs = fcol_in_mdf['RoC_Populated_land']
        idx1 = fcol_in_mdf['Populated_land']
        idx2 = fcol_in_mdf['Populated_land_last_year']
        idx3 = fcol_in_mdf['Populated_land_last_year']
        mdf[rowi, idxlhs:idxlhs + 10] =  ( mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10] )  / mdf[rowi , idx3:idx3 + 10] /  One_year 
    
    # Total_CO2_emissionslast_yr[region] = SMOOTH3 ( Total_CO2_emissions[region] , One_year )
        idxin = fcol_in_mdf['Total_CO2_emissions' ]
        idx2 = fcol_in_mdf['Total_CO2_emissionslast_yr_2']
        idx1 = fcol_in_mdf['Total_CO2_emissionslast_yr_1']
        idxout = fcol_in_mdf['Total_CO2_emissionslast_yr']
        mdf[rowi, idxout:idxout + 10] = mdf[rowi-1, idxout:idxout + 10] + ( mdf[rowi-1, idx2:idx2 + 10] - mdf[rowi-1, idxout:idxout + 10]) / ( One_year / 3) * dt
        mdf[rowi, idx2:idx2 + 10] = mdf[rowi-1, idx2:idx2 + 10] + ( mdf[rowi-1, idx1:idx1 + 10] - mdf[rowi-1, idx2:idx2 + 10]) / ( One_year / 3) * dt
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1 + 10] + ( mdf[rowi-1, idxin:idxin + 10] - mdf[rowi-1, idx1:idx1 + 10]) / ( One_year / 3) * dt
    
    # Scaled_Effect_of_poverty_on_social_tension_and_trust[region] = ( ( Raw_Effect_of_poverty_on_social_tension[region] - 1 ) * Scaling_factor_of_eff_of_poverty_on_social_tension ) + 1
        idxlhs = fcol_in_mdf['Scaled_Effect_of_poverty_on_social_tension_and_trust']
        idx1 = fcol_in_mdf['Raw_Effect_of_poverty_on_social_tension']
        mdf[rowi, idxlhs:idxlhs + 10] =  (  ( mdf[rowi , idx1:idx1 + 10] -  1  )  *  Scaling_factor_of_eff_of_poverty_on_social_tension  )  +  1 
    
    # Temp_driver_to_shift_biomes_degC = Temp_surface / ( ( Temp_surface_1850 - Zero_C_on_K_scale_K ) * K_to_C_conversion ) - 0
        idxlhs = fcol_in_mdf['Temp_driver_to_shift_biomes_degC']
        idx1 = fcol_in_mdf['Temp_surface']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  (  (  Temp_surface_1850  -  Zero_C_on_K_scale_K  )  *  K_to_C_conversion  )  -  0 
    
    # Shifting_DESERT_to_GRASS_Mkm2_py = IF_THEN_ELSE ( Temp_driver_to_shift_biomes_degC < 0 , DESERT_Mkm2 / Ref_shifting_biome_yr * Slope_of_effect_of_temp_shifting_DESERT_to_GRASS * Temp_driver_to_shift_biomes_degC , 0 )
        idxlhs = fcol_in_mdf['Shifting_DESERT_to_GRASS_Mkm2_py']
        idx1 = fcol_in_mdf['Temp_driver_to_shift_biomes_degC']
        idx2 = fcol_in_mdf['DESERT_Mkm2']
        idx3 = fcol_in_mdf['Temp_driver_to_shift_biomes_degC']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  ( mdf[rowi, idx1] <  0  , mdf[rowi, idx2] /  Ref_shifting_biome_yr  *  Slope_of_effect_of_temp_shifting_DESERT_to_GRASS  * mdf[rowi, idx3] ,  0  ) 
    
    # Shifting_GRASS_to_DESERT_Mkm2_py = IF_THEN_ELSE ( Temp_driver_to_shift_biomes_degC > 0 , GRASS_potential_area_Mkm2 / Ref_shifting_biome_yr * Slope_of_effect_of_temp_shifting_GRASS_to_DESERT * Temp_driver_to_shift_biomes_degC * Temp_driver_to_shift_biomes_degC * ( 1 / Effect_of_humidity_on_shifting_biomes ) , 0 )
        idxlhs = fcol_in_mdf['Shifting_GRASS_to_DESERT_Mkm2_py']
        idx1 = fcol_in_mdf['Temp_driver_to_shift_biomes_degC']
        idx2 = fcol_in_mdf['GRASS_potential_area_Mkm2']
        idx3 = fcol_in_mdf['Temp_driver_to_shift_biomes_degC']
        idx4 = fcol_in_mdf['Temp_driver_to_shift_biomes_degC']
        idx5 = fcol_in_mdf['Effect_of_humidity_on_shifting_biomes']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  ( mdf[rowi, idx1] >  0  , mdf[rowi, idx2] /  Ref_shifting_biome_yr  *  Slope_of_effect_of_temp_shifting_GRASS_to_DESERT  * mdf[rowi, idx3] * mdf[rowi, idx4] *  (  1  / mdf[rowi, idx5] )  ,  0  ) 
    
    # Shifting_GRASS_to_NF_Mkm2_py = IF_THEN_ELSE ( Temp_driver_to_shift_biomes_degC < 0 , GRASS_potential_area_Mkm2 / Ref_shifting_biome_yr * Slope_of_effect_of_temp_shifting_GRASS_to_NF * Temp_driver_to_shift_biomes_degC , 0 )
        idxlhs = fcol_in_mdf['Shifting_GRASS_to_NF_Mkm2_py']
        idx1 = fcol_in_mdf['Temp_driver_to_shift_biomes_degC']
        idx2 = fcol_in_mdf['GRASS_potential_area_Mkm2']
        idx3 = fcol_in_mdf['Temp_driver_to_shift_biomes_degC']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  ( mdf[rowi, idx1] <  0  , mdf[rowi, idx2] /  Ref_shifting_biome_yr  *  Slope_of_effect_of_temp_shifting_GRASS_to_NF  * mdf[rowi, idx3] ,  0  ) 
    
    # Shifting_GRASS_to_TROP_Mkm2_py = IF_THEN_ELSE ( Temp_driver_to_shift_biomes_degC < 0 , GRASS_potential_area_Mkm2 / Ref_shifting_biome_yr * Slope_of_effect_of_temp_shifting_GRASS_to_TROP * Temp_driver_to_shift_biomes_degC , 0 )
        idxlhs = fcol_in_mdf['Shifting_GRASS_to_TROP_Mkm2_py']
        idx1 = fcol_in_mdf['Temp_driver_to_shift_biomes_degC']
        idx2 = fcol_in_mdf['GRASS_potential_area_Mkm2']
        idx3 = fcol_in_mdf['Temp_driver_to_shift_biomes_degC']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  ( mdf[rowi, idx1] <  0  , mdf[rowi, idx2] /  Ref_shifting_biome_yr  *  Slope_of_effect_of_temp_shifting_GRASS_to_TROP  * mdf[rowi, idx3] ,  0  ) 
    
    # Shifting_ice_to_tundra_from_detail_ice_on_land_Mkm2_pr_yr = Antarctic_ice_area_decrease_Mkm2_pr_yr + Glacial_ice_area_decrease_Mkm2_pr_yr + Greenland_ice_area_decrease_Mkm2_pr_yr
        idxlhs = fcol_in_mdf['Shifting_ice_to_tundra_from_detail_ice_on_land_Mkm2_pr_yr']
        idx1 = fcol_in_mdf['Antarctic_ice_area_decrease_Mkm2_pr_yr']
        idx2 = fcol_in_mdf['Glacial_ice_area_decrease_Mkm2_pr_yr']
        idx3 = fcol_in_mdf['Greenland_ice_area_decrease_Mkm2_pr_yr']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3]
    
    # Shifting_ice_on_land_to_tundra_Mkm2_py = Shifting_ice_to_tundra_from_detail_ice_on_land_Mkm2_pr_yr
        idxlhs = fcol_in_mdf['Shifting_ice_on_land_to_tundra_Mkm2_py']
        idx1 = fcol_in_mdf['Shifting_ice_to_tundra_from_detail_ice_on_land_Mkm2_pr_yr']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # Shifting_NF_to_GRASS_Mkm2_py = IF_THEN_ELSE ( Temp_driver_to_shift_biomes_degC > 0 , NF_potential_area_Mkm2 / Ref_shifting_biome_yr * Slope_of_effect_of_temp_shifting_NF_to_GRASS * Temp_driver_to_shift_biomes_degC , 0 )
        idxlhs = fcol_in_mdf['Shifting_NF_to_GRASS_Mkm2_py']
        idx1 = fcol_in_mdf['Temp_driver_to_shift_biomes_degC']
        idx2 = fcol_in_mdf['NF_potential_area_Mkm2']
        idx3 = fcol_in_mdf['Temp_driver_to_shift_biomes_degC']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  ( mdf[rowi, idx1] >  0  , mdf[rowi, idx2] /  Ref_shifting_biome_yr  *  Slope_of_effect_of_temp_shifting_NF_to_GRASS  * mdf[rowi, idx3] ,  0  ) 
    
    # Shifting_NF_to_TROP_Mkm2_py = IF_THEN_ELSE ( Temp_driver_to_shift_biomes_degC > 0 , NF_potential_area_Mkm2 / Ref_shifting_biome_yr * Slope_of_effect_of_temp_shifting_NF_to_TROP * Temp_driver_to_shift_biomes_degC , 0 )
        idxlhs = fcol_in_mdf['Shifting_NF_to_TROP_Mkm2_py']
        idx1 = fcol_in_mdf['Temp_driver_to_shift_biomes_degC']
        idx2 = fcol_in_mdf['NF_potential_area_Mkm2']
        idx3 = fcol_in_mdf['Temp_driver_to_shift_biomes_degC']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  ( mdf[rowi, idx1] >  0  , mdf[rowi, idx2] /  Ref_shifting_biome_yr  *  Slope_of_effect_of_temp_shifting_NF_to_TROP  * mdf[rowi, idx3] ,  0  ) 
    
    # Shifting_NF_to_Tundra_Mkm2_py = IF_THEN_ELSE ( Temp_driver_to_shift_biomes_degC < 0 , NF_potential_area_Mkm2 / Ref_shifting_biome_yr * Slope_of_effect_of_temp_on_shifting_NF_to_Tundra * Temp_driver_to_shift_biomes_degC , 0 )
        idxlhs = fcol_in_mdf['Shifting_NF_to_Tundra_Mkm2_py']
        idx1 = fcol_in_mdf['Temp_driver_to_shift_biomes_degC']
        idx2 = fcol_in_mdf['NF_potential_area_Mkm2']
        idx3 = fcol_in_mdf['Temp_driver_to_shift_biomes_degC']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  ( mdf[rowi, idx1] <  0  , mdf[rowi, idx2] /  Ref_shifting_biome_yr  *  Slope_of_effect_of_temp_on_shifting_NF_to_Tundra  * mdf[rowi, idx3] ,  0  ) 
    
    # Shifting_TROP_to_GRASS_Mkm2_py = IF_THEN_ELSE ( Temp_driver_to_shift_biomes_degC > 0 , TROP_potential_area_Mkm2 / Ref_shifting_biome_yr * Slope_of_effect_of_temp_shifting_TROP_to_GRASS * Temp_driver_to_shift_biomes_degC * ( 1 / Effect_of_humidity_on_shifting_biomes ) , 0 )
        idxlhs = fcol_in_mdf['Shifting_TROP_to_GRASS_Mkm2_py']
        idx1 = fcol_in_mdf['Temp_driver_to_shift_biomes_degC']
        idx2 = fcol_in_mdf['TROP_potential_area_Mkm2']
        idx3 = fcol_in_mdf['Temp_driver_to_shift_biomes_degC']
        idx4 = fcol_in_mdf['Effect_of_humidity_on_shifting_biomes']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  ( mdf[rowi, idx1] >  0  , mdf[rowi, idx2] /  Ref_shifting_biome_yr  *  Slope_of_effect_of_temp_shifting_TROP_to_GRASS  * mdf[rowi, idx3] *  (  1  / mdf[rowi, idx4] )  ,  0  ) 
    
    # Shifting_TROP_to_NF_Mkm2_py = IF_THEN_ELSE ( Temp_driver_to_shift_biomes_degC < 0 , TROP_potential_area_Mkm2 / Ref_shifting_biome_yr * Slope_of_effect_of_temp_on_shifting_TROP_to_NF * Temp_driver_to_shift_biomes_degC , 0 )
        idxlhs = fcol_in_mdf['Shifting_TROP_to_NF_Mkm2_py']
        idx1 = fcol_in_mdf['Temp_driver_to_shift_biomes_degC']
        idx2 = fcol_in_mdf['TROP_potential_area_Mkm2']
        idx3 = fcol_in_mdf['Temp_driver_to_shift_biomes_degC']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  ( mdf[rowi, idx1] <  0  , mdf[rowi, idx2] /  Ref_shifting_biome_yr  *  Slope_of_effect_of_temp_on_shifting_TROP_to_NF  * mdf[rowi, idx3] ,  0  ) 
    
    # Shifting_tundra_to_ice_from_detail_ice_on_land_Mkm2_pr_yr = Antarctic_ice_area_increase_Mkm2_pr_yr + Glacial_ice_area_increase_Mkm2_pr_yr + Greenland_ice_area_increase_Mkm2_pr_yr
        idxlhs = fcol_in_mdf['Shifting_tundra_to_ice_from_detail_ice_on_land_Mkm2_pr_yr']
        idx1 = fcol_in_mdf['Antarctic_ice_area_increase_Mkm2_pr_yr']
        idx2 = fcol_in_mdf['Glacial_ice_area_increase_Mkm2_pr_yr']
        idx3 = fcol_in_mdf['Greenland_ice_area_increase_Mkm2_pr_yr']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3]
    
    # Shifting_tundra_to_ice_on_land_Mkm2_py = Shifting_tundra_to_ice_from_detail_ice_on_land_Mkm2_pr_yr
        idxlhs = fcol_in_mdf['Shifting_tundra_to_ice_on_land_Mkm2_py']
        idx1 = fcol_in_mdf['Shifting_tundra_to_ice_from_detail_ice_on_land_Mkm2_pr_yr']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # Shifting_Tundra_to_NF_Mkm2_py = IF_THEN_ELSE ( Temp_driver_to_shift_biomes_degC > 0 , Tundra_potential_area_Mkm2 / Ref_shifting_biome_yr * Slope_of_effect_of_temp_shifting_tundra_to_NF * Temp_driver_to_shift_biomes_degC , 0 )
        idxlhs = fcol_in_mdf['Shifting_Tundra_to_NF_Mkm2_py']
        idx1 = fcol_in_mdf['Temp_driver_to_shift_biomes_degC']
        idx2 = fcol_in_mdf['Tundra_potential_area_Mkm2']
        idx3 = fcol_in_mdf['Temp_driver_to_shift_biomes_degC']
        mdf[rowi, idxlhs] =  IF_THEN_ELSE  ( mdf[rowi, idx1] >  0  , mdf[rowi, idx2] /  Ref_shifting_biome_yr  *  Slope_of_effect_of_temp_shifting_tundra_to_NF  * mdf[rowi, idx3] ,  0  ) 
    
    # shortfall[region] = MAX ( 0 , Planned_investments_for_all_TAs[region] - Budget_earmarked_for_GL[region] )
        idxlhs = fcol_in_mdf['shortfall']
        idx1 = fcol_in_mdf['Planned_investments_for_all_TAs']
        idx2 = fcol_in_mdf['Budget_earmarked_for_GL']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.maximum  (  0  , mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10] ) 
     
    # Shortfall_as_pct_of_needed[region] = ZIDZ ( shortfall[region] , Planned_investments_for_all_TAs[region] )
        idxlhs = fcol_in_mdf['Shortfall_as_pct_of_needed']
        idx1 = fcol_in_mdf['shortfall']
        idx2 = fcol_in_mdf['Planned_investments_for_all_TAs']
        for i in range(0,10):
            mdf[rowi, idxlhs + i] = ZIDZ ( mdf[rowi, idx1 + i], mdf[rowi, idx2 + i])
    
    # Smoothed_RoC_in_GDPpp[region] = SMOOTH ( RoC_in_GDPpp[region] , Time_to_smooth_RoC_in_GDPpp )
        idx1 = fcol_in_mdf['Smoothed_RoC_in_GDPpp']
        idx2 = fcol_in_mdf['RoC_in_GDPpp']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1+10] + ( mdf[rowi-1 , idx2:idx2 + 10] - mdf[rowi -1 , idx1:idx1 + 10]) / Time_to_smooth_RoC_in_GDPpp * dt
    
    # SW_Atmospheric_absorption = Incoming_solar_ZJ_py * Frac_atm_absorption
        idxlhs = fcol_in_mdf['SW_Atmospheric_absorption']
        idx1 = fcol_in_mdf['Incoming_solar_ZJ_py']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Frac_atm_absorption 
    
    # Total_net_aerosol_forcings_W_p_m2 = Anthropogenic_aerosol_forcing + Model_Volcanic_aerosol_forcing_W_p_m2
        idxlhs = fcol_in_mdf['Total_net_aerosol_forcings_W_p_m2']
        idx1 = fcol_in_mdf['Anthropogenic_aerosol_forcing']
        idx2 = fcol_in_mdf['Model_Volcanic_aerosol_forcing_W_p_m2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2]
    
    # Total_net_aerosol_forcing_ZJ_py = Total_net_aerosol_forcings_W_p_m2 * UNIT_conversion_W_p_m2_earth_to_ZJ_py
        idxlhs = fcol_in_mdf['Total_net_aerosol_forcing_ZJ_py']
        idx1 = fcol_in_mdf['Total_net_aerosol_forcings_W_p_m2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  UNIT_conversion_W_p_m2_earth_to_ZJ_py 
    
    # SW_clear_sky_reflection_aka_scattering = Incoming_solar_ZJ_py * Frac_SW_clear_sky_reflection_aka_scattering - Total_net_aerosol_forcing_ZJ_py
        idxlhs = fcol_in_mdf['SW_clear_sky_reflection_aka_scattering']
        idx1 = fcol_in_mdf['Incoming_solar_ZJ_py']
        idx2 = fcol_in_mdf['Total_net_aerosol_forcing_ZJ_py']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Frac_SW_clear_sky_reflection_aka_scattering  - mdf[rowi, idx2]
    
    # SW_HI_cloud_efffect_aka_cloud_albedo = Incoming_solar_ZJ_py * Frac_SW_HI_cloud_efffect_aka_cloud_albedo * Ratio_of_area_covered_by_high_clouds_current_to_init
        idxlhs = fcol_in_mdf['SW_HI_cloud_efffect_aka_cloud_albedo']
        idx1 = fcol_in_mdf['Incoming_solar_ZJ_py']
        idx2 = fcol_in_mdf['Ratio_of_area_covered_by_high_clouds_current_to_init']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Frac_SW_HI_cloud_efffect_aka_cloud_albedo  * mdf[rowi, idx2]
    
    # SW_LO_cloud_efffect_aka_cloud_albedo = Incoming_solar_ZJ_py * Frac_SW_LO_cloud_efffect_aka_cloud_albedo * Ratio_of_area_covered_by_low_clouds_current_to_init
        idxlhs = fcol_in_mdf['SW_LO_cloud_efffect_aka_cloud_albedo']
        idx1 = fcol_in_mdf['Incoming_solar_ZJ_py']
        idx2 = fcol_in_mdf['Ratio_of_area_covered_by_low_clouds_current_to_init']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] *  Frac_SW_LO_cloud_efffect_aka_cloud_albedo  * mdf[rowi, idx2]
    
    # SW_to_surface = Incoming_solar_ZJ_py - SW_Atmospheric_absorption - SW_HI_cloud_efffect_aka_cloud_albedo - SW_LO_cloud_efffect_aka_cloud_albedo - SW_clear_sky_reflection_aka_scattering
        idxlhs = fcol_in_mdf['SW_to_surface']
        idx1 = fcol_in_mdf['Incoming_solar_ZJ_py']
        idx2 = fcol_in_mdf['SW_Atmospheric_absorption']
        idx3 = fcol_in_mdf['SW_HI_cloud_efffect_aka_cloud_albedo']
        idx4 = fcol_in_mdf['SW_LO_cloud_efffect_aka_cloud_albedo']
        idx5 = fcol_in_mdf['SW_clear_sky_reflection_aka_scattering']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] - mdf[rowi, idx2] - mdf[rowi, idx3] - mdf[rowi, idx4] - mdf[rowi, idx5]
    
    # SW_surface_reflection = Avg_earths_surface_albedo * SW_to_surface
        idxlhs = fcol_in_mdf['SW_surface_reflection']
        idx1 = fcol_in_mdf['Avg_earths_surface_albedo']
        idx2 = fcol_in_mdf['SW_to_surface']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2]
    
    # SW_surface_absorption = SW_to_surface - SW_surface_reflection
        idxlhs = fcol_in_mdf['SW_surface_absorption']
        idx1 = fcol_in_mdf['SW_to_surface']
        idx2 = fcol_in_mdf['SW_surface_reflection']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] - mdf[rowi, idx2]
    
    # Time_to_implement_SGRPI_policy[region] = Time_to_implement_UN_policies[region] + Addl_time_to_shift_govt_expenditure
        idxlhs = fcol_in_mdf['Time_to_implement_SGRPI_policy']
        idx1 = fcol_in_mdf['Time_to_implement_UN_policies']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] +  Addl_time_to_shift_govt_expenditure 
    
    # Total_government_revenue_as_a_proportion_of_GDP[region] = Govt_income_after_transfers[region] / GDP_USED[region]
        idxlhs = fcol_in_mdf['Total_government_revenue_as_a_proportion_of_GDP']
        idx1 = fcol_in_mdf['Govt_income_after_transfers']
        idx2 = fcol_in_mdf['GDP_USED']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] / mdf[rowi , idx2:idx2 + 10]
    
    # TROP_Biomass_in_construction_material_left_to_rot = TROP_Biomass_locked_in_construction_material_GtBiomass / TROP_Avg_life_of_building_yr * ( 1 - TROP_Fraction_of_construction_waste_burned_0_to_1 )
        idxlhs = fcol_in_mdf['TROP_Biomass_in_construction_material_left_to_rot']
        idx1 = fcol_in_mdf['TROP_Biomass_locked_in_construction_material_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  TROP_Avg_life_of_building_yr  *  (  1  -  TROP_Fraction_of_construction_waste_burned_0_to_1  ) 
    
    # Use_of_TROP_biomass_for_construction = Use_of_TROP_for_construction_in_2000_GtBiomass * Effect_of_population_and_urbanization_on_biomass_use * UNIT_conversion_1_py
        idxlhs = fcol_in_mdf['Use_of_TROP_biomass_for_construction']
        idx1 = fcol_in_mdf['Effect_of_population_and_urbanization_on_biomass_use']
        mdf[rowi, idxlhs] =  Use_of_TROP_for_construction_in_2000_GtBiomass  * mdf[rowi, idx1] *  UNIT_conversion_1_py 
    
    # TROP_for_construction_use = Use_of_TROP_biomass_for_construction
        idxlhs = fcol_in_mdf['TROP_for_construction_use']
        idx1 = fcol_in_mdf['Use_of_TROP_biomass_for_construction']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # TROP_Living_biomass_rotting = TROP_Living_biomass_GtBiomass / TROP_Avg_life_biomass_yr
        idxlhs = fcol_in_mdf['TROP_Living_biomass_rotting']
        idx1 = fcol_in_mdf['TROP_Living_biomass_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  TROP_Avg_life_biomass_yr 
    
    # TROP_regrowing_after_being_burnt_Mkm2_py = TROP_area_burnt / Time_to_regrow_TROP_yr
        idxlhs = fcol_in_mdf['TROP_regrowing_after_being_burnt_Mkm2_py']
        idx1 = fcol_in_mdf['TROP_area_burnt']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Time_to_regrow_TROP_yr 
    
    # TROP_regrowing_after_being_clear_cut = TROP_area_clear_cut / ( Time_to_regrow_TROP_yr * 2 )
        idxlhs = fcol_in_mdf['TROP_regrowing_after_being_clear_cut']
        idx1 = fcol_in_mdf['TROP_area_clear_cut']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  (  Time_to_regrow_TROP_yr  *  2  ) 
    
    # TROP_regrowing_after_being_deforested = TROP_area_deforested / Effective_Time_to_regrow_TROP_after_deforesting
        idxlhs = fcol_in_mdf['TROP_regrowing_after_being_deforested']
        idx1 = fcol_in_mdf['TROP_area_deforested']
        idx2 = fcol_in_mdf['Effective_Time_to_regrow_TROP_after_deforesting']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] / mdf[rowi, idx2]
    
    # TROP_regrowing_after_harvesting_Mkm2_py = TROP_area_harvested_Mkm2 / Time_to_regrow_TROP_yr
        idxlhs = fcol_in_mdf['TROP_regrowing_after_harvesting_Mkm2_py']
        idx1 = fcol_in_mdf['TROP_area_harvested_Mkm2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Time_to_regrow_TROP_yr 
    
    # TUNDRA_Biomass_in_construction_material_left_to_rot = TUNDRA_Biomass_locked_in_construction_material_GtBiomass / TUNDRA_Avg_life_of_building_yr * ( 1 - TUNDRA_Fraction_of_construction_waste_burned_0_to_1 )
        idxlhs = fcol_in_mdf['TUNDRA_Biomass_in_construction_material_left_to_rot']
        idx1 = fcol_in_mdf['TUNDRA_Biomass_locked_in_construction_material_GtBiomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  TUNDRA_Avg_life_of_building_yr  *  (  1  -  TUNDRA_Fraction_of_construction_waste_burned_0_to_1  ) 
    
    # Use_of_TUNDRA_biomass_for_construction = Use_of_TUNDRA_for_construction_in_2000_GtBiomass * Effect_of_population_and_urbanization_on_biomass_use * UNIT_conversion_1_py
        idxlhs = fcol_in_mdf['Use_of_TUNDRA_biomass_for_construction']
        idx1 = fcol_in_mdf['Effect_of_population_and_urbanization_on_biomass_use']
        mdf[rowi, idxlhs] =  Use_of_TUNDRA_for_construction_in_2000_GtBiomass  * mdf[rowi, idx1] *  UNIT_conversion_1_py 
    
    # TUNDRA_for_construction_use = Use_of_TUNDRA_biomass_for_construction
        idxlhs = fcol_in_mdf['TUNDRA_for_construction_use']
        idx1 = fcol_in_mdf['Use_of_TUNDRA_biomass_for_construction']
        mdf[rowi, idxlhs] = mdf[rowi, idx1]
    
    # TUNDRA_Living_biomass_rotting = TUNDRA_Living_biomass / TUNDRA_Avg_life_biomass_yr
        idxlhs = fcol_in_mdf['TUNDRA_Living_biomass_rotting']
        idx1 = fcol_in_mdf['TUNDRA_Living_biomass']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  TUNDRA_Avg_life_biomass_yr 
    
    # TUNDRA_regrowing_after_being_burnt_Mkm2_py = TUNDRA_area_burnt_Mkm2 / Time_to_regrow_TUNDRA_yr
        idxlhs = fcol_in_mdf['TUNDRA_regrowing_after_being_burnt_Mkm2_py']
        idx1 = fcol_in_mdf['TUNDRA_area_burnt_Mkm2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Time_to_regrow_TUNDRA_yr 
    
    # TUNDRA_regrowing_after_being_deforested_Mkm2_py = TUNDRA_deforested_Mkm2 / Time_to_regrow_TUNDRA_after_deforesting_yr
        idxlhs = fcol_in_mdf['TUNDRA_regrowing_after_being_deforested_Mkm2_py']
        idx1 = fcol_in_mdf['TUNDRA_deforested_Mkm2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Time_to_regrow_TUNDRA_after_deforesting_yr 
    
    # TUNDRA_regrowing_after_harvesting_Mkm2_py = TUNDRA_area_harvested_Mkm2 / Time_to_regrow_TUNDRA_yr
        idxlhs = fcol_in_mdf['TUNDRA_regrowing_after_harvesting_Mkm2_py']
        idx1 = fcol_in_mdf['TUNDRA_area_harvested_Mkm2']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Time_to_regrow_TUNDRA_yr 
    
    # Unemployment_rate_smoothed[region] = SMOOTH ( Unemployment_rate[region] , Time_to_smooth_unemp_rate )
        idx1 = fcol_in_mdf['Unemployment_rate_smoothed']
        idx2 = fcol_in_mdf['Unemployment_rate']
        mdf[rowi, idx1:idx1 + 10] = mdf[rowi-1, idx1:idx1+10] + ( mdf[rowi-1 , idx2:idx2 + 10] - mdf[rowi -1 , idx1:idx1 + 10]) / Time_to_smooth_unemp_rate * dt
    
    # Urban_aerosol_concentration_future = Indicated_Urban_aerosol_concentration_future * UAC_reduction_effort
        idxlhs = fcol_in_mdf['Urban_aerosol_concentration_future']
        idx1 = fcol_in_mdf['Indicated_Urban_aerosol_concentration_future']
        idx2 = fcol_in_mdf['UAC_reduction_effort']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2]
    
    # Volcanic_aerosols_removed_from_stratosphere = Volcanic_aerosols_in_stratosphere / Time_for_volcanic_aerosols_to_remain_in_the_stratosphere
        idxlhs = fcol_in_mdf['Volcanic_aerosols_removed_from_stratosphere']
        idx1 = fcol_in_mdf['Volcanic_aerosols_in_stratosphere']
        mdf[rowi, idxlhs] = mdf[rowi, idx1] /  Time_for_volcanic_aerosols_to_remain_in_the_stratosphere 
    
    # W_loan_obligations_not_met[region] = Worker_loan_repayment_obligations[region] * ( 1 - Fraction_of_worker_loan_obligations_met[region] )
        idxlhs = fcol_in_mdf['W_loan_obligations_not_met']
        idx1 = fcol_in_mdf['Worker_loan_repayment_obligations']
        idx2 = fcol_in_mdf['Fraction_of_worker_loan_obligations_met']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] *  (  1  - mdf[rowi , idx2:idx2 + 10] ) 
    
    # Worker_cash_inflow[region] = Worker_income_after_tax[region] - Worker_cashflow_to_owners[region]
        idxlhs = fcol_in_mdf['Worker_cash_inflow']
        idx1 = fcol_in_mdf['Worker_income_after_tax']
        idx2 = fcol_in_mdf['Worker_cashflow_to_owners']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] - mdf[rowi , idx2:idx2 + 10]
    
    # Worker_debt_defaulting[region] = MAX ( 0 , W_loan_obligations_not_met[region] )
        idxlhs = fcol_in_mdf['Worker_debt_defaulting']
        idx1 = fcol_in_mdf['W_loan_obligations_not_met']
        mdf[rowi, idxlhs:idxlhs + 10] =  np.maximum  (  0  , mdf[rowi , idx1:idx1 + 10] ) 
    
    # Worker_defaults_written_off[region] = Worker_debt_defaults_outstanding[region] / Time_to_write_off_worker_defaults
        idxlhs = fcol_in_mdf['Worker_defaults_written_off']
        idx1 = fcol_in_mdf['Worker_debt_defaults_outstanding']
        mdf[rowi, idxlhs:idxlhs + 10] = mdf[rowi , idx1:idx1 + 10] /  Time_to_write_off_worker_defaults 

#
# save current rowi to mdf_plot
        mdf_plot = fill_mdf_plot_row_start(runde, mdf_plot, ch, plot_var_list, plot_var_list_10, mdf[rowi,:], rowi)

        start_tick_in_mdf_play += 1
        store_end = time.time()
#        store_tot = store_tot + (store_end-store_start)

    ##### END loop
    if runde == 99:
        row1990 = mdf[320, :]
        np.save('ro90.npy', row1990)
        np.save('mdf80_90.npy', mdf)
    elif runde == 0:
        row2025 = mdf[1120, :]
        np.save('ro25.npy', row2025)
        np.save('mdf90_25.npy', mdf)
        np.save('plot90_25.npy', mdf_plot)
        # TODO
        #### do buget for 2025
    #   budget_to_db(game_id, 1, ro, list(mdf.values))
    elif runde == 1:
        #    mdf_play = mdf_play_3841_415[0:1920, :]
        row2040 = mdf[480, :]
        np.save(path + game_id + '_ro40.npy', row2040)
        np.save(path + game_id + '_plot25_40.npy', mdf_plot)
        #### do buget for 2040
#        mdf_cur = np.load(game_id + '_plot25_40.npy')
#        ro = mdf_cur[480,:]
        budget_to_db(game_id, runde, mdf_plot[480, :], plot_var_list)
#        ro = mdf.iloc[480, :].to_numpy()
#        budget_to_db(game_id, 1, ro, list(mdf.columns.values))
    elif runde == 2:
        #   mdf_play = mdf_play_3841_415[0:2560, :]
        row2060 = mdf[640, :]
        np.save(path + game_id + '_ro60.npy', row2060)
        np.save(path + game_id + '_plot25_60.npy', mdf_plot)
        budget_to_db(game_id, runde, mdf_plot[640, :], plot_var_list)
    elif runde == 3:
        np.save(path + game_id + '_plot60_21.npy', mdf_plot)

### end ugregmod

