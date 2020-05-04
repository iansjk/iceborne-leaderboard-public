import os
import time

from flask import request
from flask import Flask, render_template
import mysql.connector
from mysql.connector import errorcode
import glob
from slugify import slugify
import time

application = Flask(__name__)
app = application

monsters = []
monsters_time = 0
quests = []
quests_time = 0
runs = []
runs_time = 0
runs_date = []
runs_date_time = 0
runners = []
runners_time = 0
weapons_dict = {}
weapons_dict['all'] = "All"
weapons_dict['bow'] = "Bow"
weapons_dict['charge-blade'] = "Charge Blade"
weapons_dict['dual-blades'] = "Dual Blades"
weapons_dict['great-sword'] = "Great Sword"
weapons_dict['gunlance'] = "Gunlance"
weapons_dict['hammer'] = "Hammer"
weapons_dict['heavy-bowgun'] = "Heavy Bowgun"
weapons_dict['hunting-horn'] = "Hunting Horn"
weapons_dict['insect-glaive'] = "Insect Glaive"
weapons_dict['lance'] = "Lance"
weapons_dict['light-bowgun'] = "Light Bowgun"
weapons_dict['long-sword'] = "Long Sword"
weapons_dict['switch-axe'] = "Switch Axe"
weapons_dict['sword-and-shield'] = "Sword & Shield"

cached_paths = {}

def get_db_creds():
    #replace with actual creds to test/dev
    db = ''
    username = ''
    password = ''
    hostname = ''
    return db, username, password, hostname

@app.route("/")
def home():

    global monsters
    global monsters_time

    if not monsters or time.time() - monsters_time > 1800:
        db, username, password, hostname = get_db_creds()
        
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM monsters ORDER BY star DESC, name")
        monsters = cur.fetchall()
        monsters_time = time.time()
        cnx.commit()

    global cached_paths

    quest_dict = {}

    if ('/' not in cached_paths or time.time() - cached_paths['/'][0] > 1800):
        six = [dict(name=row[0], url_name=row[1], runs=row[4]) for row in monsters if row[2] == 6]
        five = [dict(name=row[0], url_name=row[1], runs=row[4]) for row in monsters if row[2] == 5]
        four = [dict(name=row[0], url_name=row[1], runs=row[4]) for row in monsters if row[2] == 4]
        three = [dict(name=row[0], url_name=row[1], runs=row[4]) for row in monsters if row[2] == 3]
        two = [dict(name=row[0], url_name=row[1], runs=row[4]) for row in monsters if row[2] == 2]
        one = [dict(name=row[0], url_name=row[1], runs=row[4]) for row in monsters if row[2] == 1]
        quest_dict['six_star'] = six
        quest_dict['five_star'] = five
        quest_dict['four_star'] = four
        quest_dict['three_star'] = three
        quest_dict['two_star'] = two
        quest_dict['one_star'] = one
        cached_paths['/'] = (time.time(), quest_dict)
    else:
        quest_dict = cached_paths['/'][1]

    return render_template('monsters.html', monsterlist=True, six_star=quest_dict['six_star'], five_star=quest_dict['five_star'], four_star=quest_dict['four_star'], three_star=quest_dict['three_star'], two_star=quest_dict['two_star'], one_star=quest_dict['one_star'])

@app.route("/monsters")
def monsters_list():
    return home()

@app.route("/monsters/<monster_url>/<tbl_weapon>/<tbl_ruleset>/<tbl_platform>")
def monster_page(monster_url, tbl_weapon, tbl_ruleset, tbl_platform):
    global runs
    global runs_time
    if not runs or time.time() - runs_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM runs ORDER BY time, runner")
        runs = cur.fetchall()
        runs_time = time.time()
        cnx.commit()
    
    global quests
    global quests_time
    if not quests or time.time() - quests_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)
        cur = cnx.cursor()
        cur.execute("SELECT * FROM quests ORDER BY star, type DESC, name")
        quests = cur.fetchall()
        quests_time = time.time()
        cnx.commit()

    global runners
    global runners_time
    if not runners or time.time() - runners_time > 1800:
        db, username, password, hostname = get_db_creds()
        
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM runners ORDER BY name")
        runners = cur.fetchall()
        runners_time = time.time()
        cnx.commit()    

    global monsters
    global monsters_time
    if not monsters or time.time() - monsters_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM monsters ORDER BY star DESC, name")
        monsters = cur.fetchall()
        monsters_time = time.time()
        cnx.commit()

    monster = ''
    monster_runs = []
    monster_quests = []

    global cached_paths

    if (request.path not in cached_paths or time.time() - cached_paths[request.path][0] > 1800):
        monster = get_monster(monster_url)
        for run in runs:
            if run[1] == monster and (run[5] == tbl_weapon or tbl_weapon == 'all'):
                if (tbl_ruleset == 'ta-wiki-rules' and run[4] == tbl_ruleset) or tbl_ruleset == 'freestyle':
                    if (tbl_platform == 'all') or (tbl_platform == 'pc' and run[6] == 'pc') or (tbl_platform == 'ps4' and run[6] == 'ps4') or (tbl_platform == 'xbox' and run[6] == 'xbox') or (tbl_platform =='console' and (run[6] == 'ps4' or run[6] == 'xbox')):
                        runner = run[0]
                        runner_url = get_runner_url(runner)
                        run_time = run[3]
                        weapon = run[5]
                        quest_url = run[2]
                        quest = get_quest(quest_url)
                        platform = ''
                        if not run[6] == 'xbox':
                            platform=run[6].upper()
                        else:
                            platform='Xbox'
                        platform_url = run[6]
                        link = run[8]
                        ruleset = ''
                        if run[4] == 'freestyle':
                            ruleset = 'Freestyle'
                        else:
                            ruleset = 'TA Rules'
                        monster_runs.append(dict(runner=runner, runner_url=runner_url, time=run_time, weapon=weapon, quest_url=quest_url, quest=quest, link=link, ruleset=ruleset, platform=platform, platform_url=platform_url))
        monster_quests = [dict(name=row[0], url_name=row[1], monster=row[2], num_runs=row[5]) for row in quests if row[2] == monster]
        cached_paths[request.path] = (time.time(), monster_runs, monster_quests, monster)
    else:
        monster_runs = cached_paths[request.path][1]
        monster_quests = cached_paths[request.path][2]
        monster = cached_paths[request.path][3]

    global weapons_dict

    return render_template('monsters.html', monsterList=False, runs=monster_runs, monster_url=monster_url, weapon=tbl_weapon, ruleset=tbl_ruleset, platform=tbl_platform, monster=monster, monster_quests=monster_quests, weapon_name=weapons_dict[tbl_weapon])

def get_monster(monster_url):
    global monsters
    global monsters_time
    if not monsters or time.time() - monsters_time > 1800:
        db, username, password, hostname = get_db_creds()
        
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM monsters ORDER BY star DESC, name")
        monsters = cur.fetchall()
        monsters_time = time.time()
        cnx.commit()

    monster = ''
    for mon in monsters:
        if mon[1] == monster_url:
            monster = mon[0]
    
    return monster

def get_runner_url(runner):
    global runners
    global runners_time
    if not runners or time.time() - runners_time > 1800:
        db, username, password, hostname = get_db_creds()
        
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM runners ORDER BY name")
        runners = cur.fetchall()
        runners_time = time.time()
        cnx.commit()

    runner_url = ''
    for runner_entry in runners:
        if runner_entry[0] == runner:
            runner_url = runner_entry[1]
    
    return runner_url

def get_quest(quest_url):
    global quests
    global quests_time
    if not quests or time.time() - quests_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)
        cur = cnx.cursor()
        cur.execute("SELECT * FROM quests ORDER BY star, type DESC, name")
        quests = cur.fetchall()
        quests_time = time.time()
        cnx.commit()

    quest = ''
    for quest_entry in quests:
        if quest_entry[1] == quest_url:
            quest = quest_entry[0]
    
    return quest

def get_quest_monster(quest):
    global quests
    global quests_time
    if not quests or time.time() - quests_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)
        cur = cnx.cursor()
        cur.execute("SELECT * FROM quests ORDER BY star, type DESC, name")
        quests = cur.fetchall()
        quests_time = time.time()
        cnx.commit()

    monster = {}
    monster_name = ''
    monster_url = ''
    monster_num_runs = 0
    for quest_entry in quests:
        if quest_entry[0] == quest:
            monster_name = quest_entry[2]
    
    if monster_name:
        for monster_entry in monsters:
            if monster_entry[0] == monster_name:
                monster_url = monster_entry[1]
                monster_num_runs = monster_entry[4]
    
    monster['name'] = monster_name
    monster['url_name'] = monster_url
    monster['num_runs'] = monster_num_runs

    return monster
    

@app.route("/quests")
def quests_list():
    
    global quests
    global quests_time
    if not quests or time.time() - quests_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)
        cur = cnx.cursor()
        cur.execute("SELECT * FROM quests ORDER BY star, type DESC, name")
        quests = cur.fetchall()
        quests_time = time.time()
        cnx.commit()

    global cached_paths

    quest_dict = {}

    if ('/quests' not in cached_paths or time.time() - cached_paths['/quests'][0] > 1800):
        six = [dict(name=row[0], url_name=row[1], runs=row[5]) for row in quests if row[3] == 6]
        five = [dict(name=row[0], url_name=row[1], runs=row[5]) for row in quests if row[3] == 5]
        four = [dict(name=row[0], url_name=row[1], runs=row[5]) for row in quests if row[3] == 4]
        three = [dict(name=row[0], url_name=row[1], runs=row[5]) for row in quests if row[3] == 3]
        two = [dict(name=row[0], url_name=row[1], runs=row[5]) for row in quests if row[3] == 2]
        one = [dict(name=row[0], url_name=row[1], runs=row[5]) for row in quests if row[3] == 1]
        quest_dict['six_star'] = six
        quest_dict['five_star'] = five
        quest_dict['four_star'] = four
        quest_dict['three_star'] = three
        quest_dict['two_star'] = two
        quest_dict['one_star'] = one
        cached_paths['/quests'] = (time.time(), quest_dict)
    else:
        quest_dict = cached_paths['/quests'][1]

    return render_template('quests.html', questlist=True, six_star=quest_dict['six_star'], five_star=quest_dict['five_star'], four_star=quest_dict['four_star'], three_star=quest_dict['three_star'], two_star=quest_dict['two_star'], one_star=quest_dict['one_star'])

@app.route("/quests/<quest_url>/<tbl_weapon>/<tbl_ruleset>/<tbl_platform>")
def quest_page(quest_url, tbl_weapon, tbl_ruleset, tbl_platform):
    global runs
    global runs_time
    if not runs or time.time() - runs_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM runs ORDER BY time, runner")
        runs = cur.fetchall()
        runs_time = time.time()
        cnx.commit()
    
    global quests
    global quests_time
    if not quests or time.time() - quests_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)
        cur = cnx.cursor()
        cur.execute("SELECT * FROM quests ORDER BY star, type DESC, name")
        quests = cur.fetchall()
        quests_time = time.time()
        cnx.commit()

    global runners
    global runners_time
    if not runners or time.time() - runners_time > 1800:
        db, username, password, hostname = get_db_creds()
        
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM runners ORDER BY name")
        runners = cur.fetchall()
        runners_time = time.time()
        cnx.commit()    

    global monsters
    global monsters_time
    if not monsters or time.time() - monsters_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM monsters ORDER BY star DESC, name")
        monsters = cur.fetchall()
        monsters_time = time.time()
        cnx.commit()

    quest_runs = []
    quest = ''
    quest_monster = {}

    global cached_paths

    if (request.path not in cached_paths or time.time() - cached_paths[request.path][0] > 1800):
        quest = get_quest(quest_url)
        quest_monster = get_quest_monster(quest)
        for run in runs:
            if run[2] == quest_url and (run[5] == tbl_weapon or tbl_weapon == 'all'):
                if (tbl_ruleset == 'ta-wiki-rules' and run[4] == tbl_ruleset) or tbl_ruleset == 'freestyle':
                    if (tbl_platform == 'all') or (tbl_platform == 'pc' and run[6] == 'pc') or (tbl_platform == 'ps4' and run[6] == 'ps4') or (tbl_platform == 'xbox' and run[6] == 'xbox') or (tbl_platform =='console' and (run[6] == 'ps4' or run[6] == 'xbox')):
                        runner = run[0]
                        runner_url = get_runner_url(runner)
                        run_time = run[3]
                        weapon = run[5]
                        quest_url = run[2]
                        quest = get_quest(quest_url)
                        platform = ''
                        if not run[6] == 'xbox':
                            platform=run[6].upper()
                        else:
                            platform='Xbox'
                        platform_url = run[6]
                        link = run[8]
                        ruleset = ''
                        if run[4] == 'freestyle':
                            ruleset = 'Freestyle'
                        else:
                            ruleset = 'TA Rules'
                        quest_runs.append(dict(runner=runner, runner_url=runner_url, time=run_time, weapon=weapon, quest_url=quest_url, quest=quest, link=link, ruleset=ruleset, platform=platform, platform_url=platform_url))
        cached_paths[request.path] = (time.time(), quest_runs, quest, quest_monster)
    else:
        quest_runs = cached_paths[request.path][1]
        quest = cached_paths[request.path][2]
        quest_monster = cached_paths[request.path][3]
    
    global weapons_dict

    return render_template('quests.html', questList=False, runs=quest_runs, quest_url=quest_url, weapon=tbl_weapon, ruleset=tbl_ruleset, platform=tbl_platform, quest_name=quest, monster=quest_monster, weapon_name=weapons_dict[tbl_weapon])

@app.route("/runners")
def runners_list():

    global runners
    global runners_time
    if not runners or time.time() - runners_time > 1800:
        db, username, password, hostname = get_db_creds()
        
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM runners ORDER BY name")
        runners = cur.fetchall()
        runners_time = time.time()
        cnx.commit()    

    global cached_paths

    runner_list = []

    if (request.path not in cached_paths or time.time() - cached_paths[request.path][0] > 1800):
        runner_list = [dict(name = row[0], url_name = row[1], num_runs = row[2]) for row in runners]
        cached_paths[request.path] = (time.time(), runner_list)
    else:
        runner_list = cached_paths[request.path][1]

    return render_template('runners.html', runnerlist=True, runners=runner_list)

@app.route("/runners/<runner_url>")
def runner_page(runner_url):
    global runs
    global runs_time
    if not runs or time.time() - runs_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM runs ORDER BY time, runner")
        runs = cur.fetchall()
        runs_time = time.time()
        cnx.commit()
    
    global runs_date
    global runs_date_time
    if not runs_date or time.time() - runs_date_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM runs ORDER BY run_date DESC")
        runs_date = cur.fetchall()
        runs_date_time = time.time()
        cnx.commit()

    global quests
    global quests_time
    if not quests or time.time() - quests_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)
        cur = cnx.cursor()
        cur.execute("SELECT * FROM quests ORDER BY star, type DESC, name")
        quests = cur.fetchall()
        quests_time = time.time()
        cnx.commit()

    global runners
    global runners_time
    if not runners or time.time() - runners_time > 1800:
        db, username, password, hostname = get_db_creds()
        
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM runners ORDER BY name")
        runners = cur.fetchall()
        runners_time = time.time()
        cnx.commit()

    global monsters
    global monsters_time
    if not monsters or time.time() - monsters_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM monsters ORDER BY star DESC, name")
        monsters = cur.fetchall()
        monsters_time = time.time()
        cnx.commit()

    runner = ''
    runner_runs = []

    global cached_paths

    if (request.path not in cached_paths or time.time() - cached_paths[request.path][0] > 1800):
        runner = get_runner(runner_url)
        for run in runs_date:
            if run[0] == runner:
                runner = run[0]
                runner_url = get_runner_url(runner)
                run_time = run[3]
                weapon = run[5]
                quest_url = run[2]
                quest = get_quest(quest_url)
                platform = ''
                if not run[6] == 'xbox':
                    platform=run[6].upper()
                else:
                    platform='Xbox'
                platform_url = run[6]
                link = run[8]
                ruleset = ''
                if run[4] == 'freestyle':
                    ruleset = 'Freestyle'
                else:
                    ruleset = 'TA Rules'
                runner_runs.append(dict(runner=runner, runner_url=runner_url, time=run_time, weapon=weapon, quest_url=quest_url, quest=quest, link=link, ruleset=ruleset, platform=platform, platform_url=platform_url))
        cached_paths[request.path] = (time.time(), runner_runs, runner)
    else:
        runner_runs = cached_paths[request.path][1]
        runner = cached_paths[request.path][2]

    return render_template('runners.html', runnerlist=False, runs=runner_runs, runner_url=runner_url, runner=runner)

def get_runner(runner_url):
    global runners
    global runners_time
    if not runners or time.time() - runners_time > 1800:
        db, username, password, hostname = get_db_creds()
        
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM runners ORDER BY name")
        runners = cur.fetchall()
        runners_time = time.time()
        cnx.commit()
    
    for row in runners:
        if row[1] == runner_url:
            return row[0]

@app.route("/rankings")
def rankings():
    return render_template('rankings.html')

@app.route("/tierlist")
def tierlist():
    return render_template('tierlist.html')

@app.route("/rules")
def rules():
    return render_template('rules.html')

@app.route("/submit")
def submit():
    return render_template('submit.html')

@app.route("/about")
def about():
    return render_template('about.html')
    