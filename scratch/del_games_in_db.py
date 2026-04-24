import sqlite3
import pandas as pd
import os
import shutil

#path = "C:\\Users\\ekj26\\Desktop\\game_w2526\\"
path = "C:\\Users\\ekj26\\Desktop\\niceuv\\example\\"
dbpath = ""

con = sqlite3.connect(dbpath+"sdg3_game.db")
# Read sqlite query results into a pandas DataFrame
q = "SELECT * FROM games"
games = []
sdg_vars = pd.read_sql_query(q, con)
for index, row in sdg_vars.iterrows():
    print(row['game_id']+' '+row['updated_at'])
    games.append(row["game_id"])
#games.append('YJM-048')
print(games)
shutil.rmtree('.nicegui' , ignore_errors=True)
sq = """DELETE FROM sessions;"""
con.execute(sq, )
con.commit()
for game in games:
    print('Delete '+game+'? [y]')
    name = input()
    if name == 'y':
        print('deleting... ' + game)
        sq = """DELETE FROM policy_decisions WHERE game_id = ?;"""
        con.execute(sq, (game,))
        con.commit()
        sq = """DELETE FROM players WHERE game_id = ?;"""
        con.execute(sq, (game,))
        con.commit()
        sq = """DELETE FROM ai_regions WHERE game_id = ?;"""
        con.execute(sq, (game,))
        con.commit()
        sq = """DELETE FROM bud WHERE game_id = ?;"""
        con.execute(sq, (game,))
        con.commit()
        sq = """DELETE FROM games WHERE game_id = ?;"""
        con.execute(sq, (game,))
        con.commit()
        sq = """DELETE FROM human_regions WHERE game_id = ?;"""
        con.execute(sq, (game,))
        con.commit()
        sq = """DELETE FROM bud WHERE game_id = ?;"""
        con.execute(sq, (game,))
        con.commit()
        sq = """DELETE FROM region_submissions WHERE game_id = ?;"""
        con.execute(sq, (game,))
        con.commit()
        # import OS
        path = os.getcwd()
        os.chdir('./files')
        path2 = os.getcwd()
        for x in os.listdir():
            if x.startswith(game):
                os.remove(x)
                print('removed file '+x)
        os.chdir('..')


con.close()
