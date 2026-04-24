import datetime
import os
import numpy as np
import matplotlib.pyplot as plt
from files import luf_original
import pickle
from io import BytesIO
import base64

#path = "C:\\Users\\ekj26\\Desktop\\game_w2526\\"
#dbpath = "C:\\Users\\ekj26\\PycharmProjects\\Sim_Mod_Claude\\"
dbpath = "C:\\Users\\ekj26\\Desktop\\nice\\from_260131_wing\\"
path = "C:\\Users\\ekj26\\Desktop\\nice\\from_260131_wing\\"
# File paths - adjust these to match your deployment
PLOT_VAR_LIST_PATH = "files/plot_var_list.pkl"
PLOT_90_25_PATH = "files/plot90_25.npy"

# Load variable list once at module level
try:
    with open(PLOT_VAR_LIST_PATH, 'rb') as f:
        game_vars = pickle.load(f)
except FileNotFoundError:
    game_vars = None
    print(f"Warning: Could not load {PLOT_VAR_LIST_PATH}")

regs = ['us', 'af', 'cn', 'me', 'sa', 'la', 'pa', 'ec', 'eu', 'se']

def load_historical_data():
    """Load the 1990-2025 historical data"""
    try:
        game_25 = np.load(PLOT_90_25_PATH)
        return game_25
    except FileNotFoundError:
        print(f"Warning: Could not load {PLOT_90_25_PATH}")
        return None

abc = load_historical_data()


def load_game_data(game_id: str, runde: int):
    """Load combined numpy data for the given round.

    runde=0 → historical only (1990-2025)
    runde=1 → + model run 1 (2025-2040)
    runde=2 → + model run 2 (2040-2060)
    runde=3 → + model run 3 (2060-2100)

    Returns (data, actual_runde) — actual_runde may be less than requested
    if model output files are not yet available.
    """
    try:
        game_25 = np.load(PLOT_90_25_PATH)
    except FileNotFoundError:
        return None, 0

    if runde == 0:
        return game_25, 0

    p40 = f"files/{game_id}_plot25_40.npy"
    if not os.path.exists(p40):
        return game_25, 0
    game_40 = np.load(p40)
    game_40 = game_40[1:, :]
    data = np.vstack((game_25, game_40))
    if runde == 1:
        return data, 1

    p60 = f"files/{game_id}_plot25_60.npy"
    if not os.path.exists(p60):
        return data, 1
    game_60 = np.load(p60)
    game_60 = game_60[1:, :]
    data = np.vstack((data, game_60))
    if runde == 2:
        return data, 2

    p21 = f"files/{game_id}_plot60_21.npy"
    if not os.path.exists(p21):
        return data, 2
    game_21 = np.load(p21)
    game_21 = game_21[1:, :]
    return np.vstack((data, game_21)), 3


def get_longrole_from_lu(x:str, lang: int):
    if x == 'Poverty':
        return luf_original.ta_to_mini_pov_str[lang]
    elif x == 'Inequality':
        return luf_original.ta_to_mini_ineq_str[lang]
    elif x == 'Empowerment':
        return luf_original.ta_to_mini_emp_str[lang]
    elif x == 'Food':
        return luf_original.ta_to_mini_food_str[lang]
    elif x == 'Energy':
        return luf_original.ta_to_mini_ener_str[lang]
    elif x == 'Future':
        return luf_original.ta_to_mini_fut_str[lang]

def pick(ys, x, y):
    """Pick specific years from data for scatter points"""
    o = []
    ys_len = len(ys)
    ys_cnt = 0
    ys_check = ys[ys_cnt]
    for i in range(0, len(x)):
        if ys_check == x[i]:
            o.append(y[i])
            ys_cnt += 1
            if ys_cnt == ys_len:
                ys_check = 1952
            else:
                ys_check = ys[ys_cnt]
        else:
            o.append(np.nan)
    return o


def get_ext(e):
    extensions = {
        'us': '.0',
        'af': '.1',
        'cn': '.2',
        'me': '.3',
        'sa': '.4',
        'la': '.5',
        'pa': '.6',
        'ec': '.7',
        'eu': '.8',
        'se': '.9'
    }
    return extensions.get(e, '')

def build_reg_role_lang_round_plot(game_id, reg, role, runde, lang, ai_regs):

    if runde == 0:
        game_25 = np.load(path + 'plot90_25.npy')
        game_data = game_25
    elif runde == 1:
        game_25 = np.load(path + 'plot90_25.npy')
        game_40 = np.load(path + game_id + '_plot25_40.npy')
        a = game_40.shape[0]
        game_40 = game_40[1:a, :]
        game_data = np.vstack((game_25, game_40))
    elif runde == 2:
        game_25 = np.load(path + 'plot90_25.npy')
        game_40 = np.load(path + game_id + '_plot25_40.npy')
        game_60 = np.load(path + game_id + '_plot25_60.npy')
        a = game_40.shape[0]
        game_40 = game_40[1:a, :]
        a = game_60.shape[0]
        game_60 = game_60[1:a, :]
        game_data = np.vstack((game_25, game_40, game_60))
    elif runde == 3:
        game_25 = np.load(path + 'plot90_25.npy')
        game_40 = np.load(path + game_id + '_plot25_40.npy')
        game_60 = np.load(path + game_id + '_plot25_60.npy')
        game_21 = np.load(path + game_id + '_plot60_21.npy')
        a = game_40.shape[0]
        game_40 = game_40[1:a, :]
        a = game_60.shape[0]
        game_60 = game_60[1:a, :]
        a = game_21.shape[0]
        game_21 = game_21[1:a, :]
        game_data = np.vstack((game_25, game_40, game_60, game_21))


def do_graph(game_data, row, round, reg, role, langx):
    if role == 'GM':
        is_gm = True
    else:
        is_gm = False
    xmin = 1990
#    print(' --- ')
#    print('do_graph')
#    print('    row=' + str(row) + ' reg=' + reg + ' role=' + role + ' round=' + str(round))
    if round == 0:
        yr_picks = [1990, 2000, 2010, 2020]
        end_year = 2025
        xmax = end_year
    elif round == 1:
        yr_picks = [2025, 2030, 2035, 2040]
        end_year = 2040
        xmax = end_year
    elif round == 2:
        yr_picks = [2040, 2050, 2060]
        end_year = 2060
        xmax = end_year
    elif round == 3:
        yr_picks = [2060, 2070, 2080, 2090, 2100]
        end_year = 2100
        xmax = end_year
    my_time = datetime.datetime.now().strftime("%a %d %b %G")
    #  print("off to build plot: regidx?"+ str(regidx)+ " cid:"+ cid+ " runde:"+ str(runde)+ " lang:"+ str(lang))
    foot1 = "mov251229_ge4a_10reg.mdl"  # 250726
    cap = foot1 + " - " + my_time

    fig, ax = plt.subplots()
    pct = row['pv_pct']
    var = row['pv_vensim_name']
    var = var.replace(' ', '_')
    ext = get_ext(reg)
    try:
        x_in_game_vars = game_vars.index(var+ext)
    except:
        x_in_game_vars = game_vars.index(var)
    x = game_data[:,0]
    y = game_data[:, x_in_game_vars + 1]
#    print('x_in_game_vars= '+str(x_in_game_vars))
#    print(x)
    y = y * pct
#    print(y)
    data_max = y.max() * 1.1
    data_min = y.min()
    plot_max = row['pv_ymax']
    plot_min = row['pv_ymin']
    ymin = min(data_min, plot_min)
    ymax = max(data_max, plot_max)
    rowid = int(row['pv_id'])
    if rowid not in [44, 45, 46]:
        if ymin > 0:
            ymin = 0
        if ymax < 0:
            ymax = 0
    if rowid in [27, 5]:  # Labour share of GDP | life expectancy
        ymin = plot_min  # red min
    if rowid in [26]:  # population |
        ymax = data_max
    if rowid in [33]: # RoC Forest land |
        if plot_min < data_min:
            ymin = plot_min
    if rowid in [32]:  # Nitrogen use
        ymax = max(25, data_max)
    if rowid in [21]:  # pH  |
        ymin = plot_min
        ymax = plot_max
    my_lab = row['pv_indicator']
    # hex values for regional lines
    if role == 'GM':
        my_colhex = '#000000'
    else:
        pyidx = regs.index(reg)
        farben = ["#435df4", "#b95c39", "#ff0000", "#ff37f6", "#ff9300", "#ad00ff", "#00ff0c", "#008a0f", "#00ffbf",
                  "#00b2ff"]
        my_colhex = farben[pyidx]
    plt.plot(x, y, color=my_colhex, linewidth=2.5, label=my_lab)
    ys = pick(yr_picks, x, y)
    plt.scatter(x, ys, color=my_colhex, s=150, alpha=0.75)
    if int(row['pv_lowerbetter']) == 1:
        grn_min = row['pv_ymin']
        grn_max = row['pv_green'] # vars_df.iloc[varx, 4]
        red_min = row['pv_red'] # vars_df.iloc[varx, 5]
        if rowid == 16:  # Emissions per person
            red_max = max(data_max, 8)
            ymax = red_max
        else:
            red_max = row['pv_ymax']  # vars_df.iloc[varx, 9]
        if red_max < ymax:
            red_max = ymax
        if rowid in [32,1]:
            if data_max > red_max:
                red_max = data_max
        yel_min = grn_max
        yel_max = red_min
    else: # lower is NOT better
        red_min = row['pv_ymin'] # vars_df.iloc[varx, 8]
        red_max = row['pv_red']  # vars_df.iloc[varx, 5]
        grn_min = row['pv_green']  # vars_df.iloc[varx, 4]
        grn_max = row['pv_ymax']  # vars_df.iloc[varx, 9]
        if rowid == 23: # public services pp
            if grn_max < ymax:
                grn_max = ymax
        if rowid == 10:  # Access to electricity
            if red_min > ymin:
                ymin = red_min
        if rowid == 33:  # RoC in forest area
            if ymin < red_min:
                red_min = ymin
        if rowid == 27:  # Labour share
            if grn_max < ymax:
                grn_max = ymax
        yel_min = red_max
        yel_max = grn_min
    plt.ylim(ymin, ymax)
#        plt.ylim(ymin, ymax)

    if not rowid in [26, 48]:  # population
        opa = 0.075 # opacity
        poly_coords = [(xmin, grn_max), (xmax, grn_max), (xmax, grn_min), (xmin, grn_min)]
        ax.add_patch(plt.Polygon(poly_coords, color="green", alpha=opa))
        poly_coords = [(xmin, red_max), (xmax, red_max), (xmax, red_min), (xmin, red_min)]
        ax.add_patch(plt.Polygon(poly_coords, color="red", alpha=opa))
        poly_coords = [(xmin, yel_max), (xmax, yel_max), (xmax, yel_min), (xmin, yel_min)]
        ax.add_patch(plt.Polygon(poly_coords, color="yellow", alpha=opa))
    if is_gm:
        plt.suptitle(my_lab, fontsize=12, wrap=True)
        metric = luf_original.metric[langx]
        cur_sub = metric+row['pv_subtitle']
        plt.title(cur_sub, fontsize=10, wrap=True)
    else:
        which_sdg = int(row["pv_id"])
        my_title = get_title_from_lu(which_sdg, langx)
        if role == 'Future':
            sdg = luf_original.sdg[langx]
            keepaneye = luf_original.keepaneye[langx]
            cur_title = keepaneye+ ' '+sdg+' ' + str(row["pv_sdg_nbr"]) + " '"  + my_title+"'"
        else:
            rolle = get_longrole_from_lu(role, langx)
            abcd = luf_original.affects_sdg[langx]
            cur_title = ''+rolle+':'+luf_original.affects_sdg[langx] + str(row["pv_sdg_nbr"]) + " '" + my_title+"'"
        plt.suptitle(cur_title, fontsize=11, wrap=True) # Main title
        metric = luf_original.metric[langx]
        subbi = luf_original.subtitle_dict[rowid][str(langx)]
        cur_sub = metric + subbi
        plt.title(cur_sub, fontsize=10, wrap=True)

    plt.figtext(.87, 0.02, cap, wrap=True, horizontalalignment='right', fontsize=8, style='italic')
    plt.grid(color="gainsboro", linestyle="-", linewidth=0.5)
    plt.box(False)
#    plt.show()
#    return fig
    # Convert to base64 for embedding
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=144, bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    return f"data:image/png;base64,{img_base64}"


def get_title_from_lu(x, lang):
    if x == 0:
        return luf_original.nat_graph_9_title[lang]
    if x == 1:
        return luf_original.sdgvarID_to_sdg_1_str[lang]
    if x == 2:
        return luf_original.sdgvarID_to_sdg_2_str[lang]
    if x == 3:
        return luf_original.sdgvarID_to_sdg_3_str[lang]
    if x == 4:
        return luf_original.sdgvarID_to_sdg_4_str[lang]
    if x == 5:
        return luf_original.sdgvarID_to_sdg_5_str[lang]
    if x == 6:
        return luf_original.sdgvarID_to_sdg_6_str[lang]
    if x == 7:
        return luf_original.sdgvarID_to_sdg_7_str[lang]
    if x == 8:
        return luf_original.sdgvarID_to_sdg_8_str[lang]
    if x == 9:
        return luf_original.sdgvarID_to_sdg_9_str[lang]
    if x == 10:
        return luf_original.sdgvarID_to_sdg_10_str[lang]
    if x == 11:
        return luf_original.sdgvarID_to_sdg_11_str[lang]
    if x == 12:
        return luf_original.sdgvarID_to_sdg_12_str[lang]
    if x == 13:
        return luf_original.sdgvarID_to_sdg_13_str[lang]
    if x == 14:
        return luf_original.sdgvarID_to_sdg_14_str[lang]
    if x == 15:
        return luf_original.sdgvarID_to_sdg_15_str[lang]
    if x == 16:
        return luf_original.sdgvarID_to_sdg_16_str[lang]
    if x == 17:
        return luf_original.sdgvarID_to_sdg_17_str[lang]
    if x == 18:
        return luf_original.sdgvarID_to_sdg_18_str[lang]
    if x == 19:
        return luf_original.sdgvarID_to_sdg_19_str[lang]
    if x == 20:
        return luf_original.sdgvarID_to_sdg_20_str[lang]
    if x == 21:
        return luf_original.sdgvarID_to_sdg_21_str[lang]
    if x == 22:
        return luf_original.sdgvarID_to_sdg_22_str[lang]
    if x == 23:
        return luf_original.sdgvarID_to_sdg_23_str[lang]
    if x == 24:
        return luf_original.sdgvarID_to_sdg_24_str[lang]
    if x == 25:
        return luf_original.sdgvarID_to_sdg_25_str[lang]
    if x == 26:
        return luf_original.sdgvarID_to_sdg_26_str[lang]
    if x == 27:
        return luf_original.sdgvarID_to_sdg_27_str[lang]
    if x == 28:
        return luf_original.sdgvarID_to_sdg_28_str[lang]
    if x == 29:
        return luf_original.sdgvarID_to_sdg_29_str[lang]
    if x == 30:
        return luf_original.sdgvarID_to_sdg_30_str[lang]
    if x == 31:
        return luf_original.sdgvarID_to_sdg_31_str[lang]
    if x == 32:
        return luf_original.sdgvarID_to_sdg_32_str[lang]
    if x == 33:
        return luf_original.sdgvarID_to_sdg_33_str[lang]
    if x == 34:
        return luf_original.sdgvarID_to_sdg_34_str[lang]
    if x == 35:
        return luf_original.sdgvarID_to_sdg_35_str[lang]
    if x == 36:
        return luf_original.sdgvarID_to_sdg_36_str[lang]
    if x == 37:
        return luf_original.sdgvarID_to_sdg_37_str[lang]
    if x == 38:
        return luf_original.sdgvarID_to_sdg_38_str[lang]
    if x == 39:
        return luf_original.nat_graph_7_title[lang]

def make_glob_overlay(game_data, lang):
    langx = lang2int(lang)
    df = game_data
    idx1 = game_vars.index('Global_population')
    idx2 = game_vars.index('Global_social_trust')
    idx3 = game_vars.index('Global_Actual_inequality_index_higher_is_more_unequal')
    idx4 = game_vars.index('Global_Average_wellbeing_index')
    idx5 = game_vars.index('Temp_surface_anomaly_compared_to_anfang_degC')
    idx6 = game_vars.index('Global_GDPpp_USED')
    x = df[:, 0]
    y1 = df[:, idx1+1]
    y2 = df[:, idx2+1]
    y3 = df[:, idx3+1]
    y4 = df[:, idx4+1]
    y5 = df[:, idx5+1]
    y6 = df[:, idx6+1]
    fig, ax1 = plt.subplots(figsize=(12, 8))
    fig.subplots_adjust(right=.7)
    fig.subplots_adjust(left=.07)
    ax1.plot(x, y1, 'red', label=luf_original.nat_graph_9_title[langx], linewidth=4.0)  # 'Population'
    plt.box(False)
    # ax1.set_xlabel('Years')
    ax1.set_ylabel(luf_original.nat_graph_9_title[langx], color='red')
    ax1.tick_params('y', colors='red')
    ax2 = ax1.twinx()
    ax2.plot(x, y2, 'brown', label=luf_original.nat_graph_7_title[langx], linewidth=3.0)  # 'Social tension'
    ax2.set_ylabel(luf_original.nat_graph_7_title[langx], color='brown')
    ax2.tick_params('y', colors='brown')
    ax3 = ax1.twinx()
    ax3.plot(x, y3, 'grey', label=luf_original.nat_graph_6_title[langx], linestyle='--', linewidth=5.0)  # 'Inequality'
    ax3.spines['right'].set_position(('outward', 50))
    ax3.set_ylabel(luf_original.nat_graph_6_title[langx], color='grey')
    ax3.tick_params('y', colors='grey')
    ax4 = ax1.twinx()
    ax4.plot(x, y4, 'green', label=luf_original.nat_graph_5_title[langx], linewidth=3.0)  # 'Wellbeing'
    ax4.spines['right'].set_position(('outward', 100))
    ax4.set_ylabel(luf_original.nat_graph_5_title[langx], color='green')
    ax4.tick_params('y', colors='green')
    ax5 = ax1.twinx()
    ax5.plot(x, y5, 'blue', label=luf_original.nat_graph_11_title[langx], linewidth=3.0)  # 'GDPpp'
    ax5.spines['right'].set_position(('outward', 150))
    ax5.set_ylabel(luf_original.nat_graph_11_title[langx], color='blue')
    ax5.tick_params('y', colors='blue')
    ax6 = ax1.twinx()
    ax6.plot(x, y6, 'black', label=luf_original.nat_graph_4_title[langx], linewidth=3.0)  # 'Warming'
    ax6.spines['right'].set_position(('outward', 200))
    ax6.set_ylabel(luf_original.nat_graph_4_title[langx], color='black')
    ax6.tick_params('y', colors='black')
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    lines3, labels3 = ax3.get_legend_handles_labels()
    lines4, labels4 = ax4.get_legend_handles_labels()
    lines5, labels5 = ax5.get_legend_handles_labels()
    lines6, labels6 = ax6.get_legend_handles_labels()
    lines = lines1 + lines2 + lines3 + lines4 + lines5 + lines6
    labels = labels1 + labels2 + labels3 + labels4 + labels5 + labels6
    plt.legend(lines, labels, loc='upper left')
    plt.title(luf_original.nat_graph_10_title[langx], fontsize=24, fontweight='bold')  # 'Global Overview'
    #  plt.savefig('foo.pdf', bbox_inches='tight')
#    plt.show()
#    return fig
    # Convert to base64 for embedding
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=144, bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    return f"data:image/png;base64,{img_base64}"

def lang2int(lang):
    languages = {
        'en': 0,
        'fr': 3,
        'de': 2,
        'no': 4
    }
    return languages.get(lang, 0)

def build_plot(game_data, var_df, cid, runde, lang, reg, role):
    lang = lang2int(lang)
    for index, row in var_df.iterrows():
#        print(reg+', '+role+', indicator: '+row['pv_indicator']+' | vensim_name: '+row['pv_vensim_name'])
        mpl_fig = do_graph(game_data, row, runde, reg, role, lang)
    return mpl_fig


