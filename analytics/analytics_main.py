import os
import sys
import sqlite3
from os import listdir
import pickle
import codecs
import csv
import datetime

FBC = '/FBC_databases'
crawl_logs = '/DB'
pro_lists = '/Projects'
page_lists = '/Page Lists'
analytics = '/analytics'
global pol_by_id
pol_by_id = {}

def quit_interface():
    clear_screen()
    print ("Bye Bye!")
    quit()

def get_basic_info(conn,db):
    
    cur = conn.cursor()
    basic_info = "select 'Number of', 'pages', count(distinct web_name), '' from {0}post_info union select 'Number of', 'comments', count(C.id), '' from  {0}comment_info C union select 'Number of', 'post-likes', count(L.id), '' from  {0}likes_info L union select 'Number of', 'users', count(distinct L.post_like_by_id), '' from  {0}likes_info L union select 'Number of', 'comment_likes', count(C.id), '' from  {0}comment_likes_info C union select 'Number of', 'replies', count(R.id), '' from  {0}replies_info R union select 'Number of', 'tags', count(C.id), '' from  {0}comment_tags_info C".format(db)
    cur.execute(basic_info)
    for row in cur.fetchall():
        print (str(row[0]) + " " + str(row[1]) + " " + str(row[2]))

def get_inp(inp):
    if sys.version_info[0] < 3:
        return raw_input(inp)
    else:
        return input(inp)

def clear_screen():
    import platform
    if str(platform.system()) == 'Windows':
        os.system('cls')
    else:
        os.system('clear')
        
def find_gender(conn, db):
    
    print ("Batching gender file...")
    male_list={}
    female_list={}
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS `gender` (`by_id` VARCHAR(300), `gender` VARCHAR(2), `id` INTEGER PRIMARY KEY AUTOINCREMENT);")
    cur.execute("CREATE INDEX IF NOT EXISTS idxm ON male_names (name,id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idxf ON female_names (name,id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idxg ON gender (gender,by_id,id);")
    conn.commit()
    
    cur.execute("select L.post_like_by_name,L.post_like_by_id from {0}likes_info L where L.post_like_by_id not in (select by_id from gender) limit 1001111111111".format(db))
    by_name_set = {}
    for row in cur.fetchall():
        by_name_set[(row[1])]=(str(row[0]).split(" ")[0].lower())
    cur.execute("select name from male_names limit 1000000000")
    for row in cur.fetchall():
        male_list[str(row[0]).lower()]=True
    
        
    cur.execute("select name from female_names limit 1000000000")
    for row in cur.fetchall():
        female_list[str(row[0]).lower()]=True
        
    for k,v in by_name_set.items():
        if v in male_list:
            
            templist = []
            templist.append(k)
            templist.append("m")
            cur.execute("insert into gender (by_id,gender) VALUES (?,?)",templist)
        elif v in female_list:
            
            templist = []
            templist.append(k)
            templist.append("f")
            cur.execute("insert into gender (by_id,gender) VALUES (?,?)",templist)
        else:
            
            templist = []
            templist.append(k)
            templist.append("u")
            cur.execute("insert into gender (by_id,gender) VALUES (?,?)",templist)
        
    conn.commit()
        

def check_answer(answer,*args):
    
    
    for arg in list(args):
       
        if str(answer) == str(arg):
            return True
        
    print ("Please enter a valid answer")
    return False

def check_date_answer(answer):
    try:
        nd = datetime.datetime.strptime(str(answer),'%Y-%m-%d')
        return True
    except:
        print ("Please enter a valid answer")
        return False
    


def create_empty_pol_set(conn):
    
    total_count = {}
    cur = conn.cursor()
    cur.execute("select distinct party from political_entities")
    for row in cur.fetchall():
        total_count[str(row[0])]=0.0
    empty_set = total_count
    
    return empty_set

def get_pol_from_id(by_id,pol_set,cur,db):
    
    cur.execute("select PE.party, count(P.id) from {0}post_info P, political_entities PE where PE.web_name = P.web_name and P.id in (select post_id from {0}likes_info  where post_like_by_id = '{1}') group by PE.party".format(db,str(by_id)))
    
    tempset = {}
    total_likes = float(0.0)
    for r in cur.fetchall():
        tempset[str(r[0])]=float(r[1])
        total_likes = float(r[1]) + total_likes
    
    if total_likes < 4:
        pass
        return {}
    else:
        for k,v in tempset.items():
            pol_set[k]+=float((v/total_likes))
        
        return pol_set


def make_batch_files(path_ ,conn, db):
    
    
    global pol_by_id
    clear_screen()
    if not os.path.isfile(path_+analytics+"/batch/pol_by_id.p"):
        pickle.dump(pol_by_id, open(path_+analytics+"/batch/pol_by_id.p", "wb"))
    else:
        pass
        #pol_by_id = pickle.load(open(path_+analytics+"/batch/pol_by_id.p", "rb"))
    db = db.replace(".txt","")
    print ("Creating batch files, might take a while...")
    blank_set = create_empty_pol_set(conn)
    cur = conn.cursor()
    cur.execute("CREATE INDEX IF NOT EXISTS idxw ON political_entities (web_name, id, name, party);")
    conn.commit()
    
    cur.execute("select distinct post_like_by_id from {0}likes_info limit 1000000000000".format(db))
    for row in cur.fetchall():
        id_ = get_pol_from_id(str(row[0]), dict(blank_set), cur, db)
        if str(row[0]) not in pol_by_id:
            pol_by_id[str(row[0])]=id_
    pickle.dump(pol_by_id, open(path_+analytics+"/batch/pol_by_id.p", "wb"))
    conn.close()
    
def batch_file_menu(path_, conn, db):
    clear_screen()
    templist = []
    print ("List of data collections: ")
    for db in listdir(r''+path_+FBC):
        if db.endswith(".txt"): print (db.replace(".txt",""))
        templist.append(db.replace(".txt",""))
    print ("\n")
    print ("Type the exact name of the data collection wherein the political data is held")
    answer = get_inp(">>> ")
    while check_answer(answer,*templist) == False:
        answer = get_inp(">>> ")
    tempdb = answer
    tempconn = sqlite3.connect(path_+crawl_logs+"/{0}.db".format(tempdb))
    check_for_extra_data(path_, tempconn, tempdb)
    make_batch_files(path_, tempconn, tempdb)
    analytics_pol_menu(path_, conn, db)


def analytics_start_menu(conn, current_db, path_):
    clear_screen()
    print ("What do you want to do?")
    print ("\n")
    print ("1. Standard Analysis Module")
    print ("2. Political alignment analysis (Danish Politics Only)")
    print ("0. Quit program")

    answer = get_inp(">>> ")
    while check_answer(answer,"1","2","0") == False:
        answer = get_inp(">>> ")
    
    if answer == "1":
        clear_screen()
        print ("What kind of analysis do you wish to perform?")
        print ("\n")
        print ("1. Basic Info")
        print ("2. Activity over time (Requires 'Numpy' and 'Matplotlib')")
        #print ("3. Undirected network analysis (Requires ('Networkx'))")
        #print ("4. Distribution of activity among pages (Requires 'Numpy' and 'Matplotlib')")
        print ("0. Quit program")
    
        answer = get_inp(">>> ")
        while check_answer(answer,"1","2","0") == False:
            answer = get_inp(">>> ")
        clear_screen()
        
        if answer == "1":
            get_basic_info(conn, current_db)
            print ("\n")
            answer = get_inp("Press any key to continue")
            analytics_start_menu(conn, current_db, path_)
        
        elif answer == "2":
            from analytics import activity_over_time
            print ("Drawing plot...")
            activity_over_time.create_activity_plot(conn, current_db, path_)
            
        elif answer == "3":
            pass
        
        elif answer == "4":
            pass
        
        elif answer == "5":
            pass
        
        elif answer == "0":
            quit_interface()
            
            
    elif answer == "2":
        analytics_pol_menu(path_, conn, current_db)
        
            
def check_for_extra_data(path_,conn,db):
    cur = conn.cursor()
    cur.execute("CREATE  TABLE IF NOT EXISTS `political_entities` (`name` VARCHAR(200),`web_name` VARCHAR(200),`party` VARCHAR(3),`id` INTEGER PRIMARY KEY AUTOINCREMENT);")
    cur.execute("CREATE  TABLE IF NOT EXISTS `common_danish_words` (`word` VARCHAR(200),`id` INTEGER PRIMARY KEY AUTOINCREMENT);")
    cur.execute("CREATE  TABLE IF NOT EXISTS `common_english_words` (`word` VARCHAR(200),`id` INTEGER PRIMARY KEY AUTOINCREMENT);")
    cur.execute("CREATE  TABLE IF NOT EXISTS `extrawords` (`word` VARCHAR(200),`id` INTEGER PRIMARY KEY AUTOINCREMENT);")
    cur.execute("CREATE  TABLE IF NOT EXISTS `male_names` (`name` VARCHAR(200),`id` INTEGER PRIMARY KEY AUTOINCREMENT);")
    cur.execute("CREATE  TABLE IF NOT EXISTS `female_names` (`name` VARCHAR(200),`id` INTEGER PRIMARY KEY AUTOINCREMENT);")
    for file_ in listdir(path_+analytics+"/Extra_tables"):
        if ".csv" in str(file_):
            cur.execute("SELECT * FROM {0};".format(str(file_).replace(".csv","")))
            if not cur.fetchall():
                print ("Inserting extra data...")
                tempscript = codecs.open(path_+analytics+"/Extra_tables/"+file_,"r","latin-1")
                reader = csv.reader(tempscript)
                for row in reader:
                    try:
                        if str(file_).replace(".csv","") == "political_entities": cur.execute("insert into political_entities (name,web_name,party) VALUES (?,?,?)",[row[0],row[1],row[2]])
                        if str(file_).replace(".csv","") == "common_danish_words": cur.execute("insert into common_danish_words (word) VALUES (?)",[row[0]])
                        if str(file_).replace(".csv","") == "common_english_words": cur.execute("insert into common_english_words (word) VALUES (?)",[row[0]])
                        if str(file_).replace(".csv","") == "extrawords": cur.execute("insert into extrawords (word) VALUES (?)",[row[0]])
                        if str(file_).replace(".csv","") == "male_names": cur.execute("insert into male_names (name) VALUES (?)",[row[0]])
                        if str(file_).replace(".csv","") == "female_names": cur.execute("insert into female_names (name) VALUES (?)",[row[0]])
                    except:
                        print ("There was a problem with insertion of "+str(file_))
                
    
    conn.commit()
                
            
            
def analytics_menu(path_):
    
    noise_string = "******************************"
    clear_screen()
    print ("\n")
    print (noise_string+"Welcome to the Ethos Facebook Analytics Module"+noise_string)
    print ("\n")
    
    templist = []
    print ("List of data collections: ")
    for db in listdir(r''+path_+FBC):
        if db.endswith(".txt"): print (db.replace(".txt",""))
        templist.append(db.replace(".txt",""))
    print ("\n")
    print ("Type the exact name of the data collection you wish to use")
    answer = get_inp(">>> ")
    while check_answer(answer,*templist) == False:
        answer = get_inp(">>> ")
    
    current_db = answer
    print (current_db)
    conn = sqlite3.connect(path_+"/DB/{0}.db".format(current_db))
    
    analytics_start_menu(conn, current_db, path_)
    

def analytics_pol_menu(path_,conn,db):
    clear_screen()
    check_for_extra_data(path_, conn, db)
    if not os.path.exists(path_+analytics+"/batch"):
        os.makedirs(path_+analytics+"/batch")
    if not os.path.isfile(path_+analytics+"/batch/pol_by_id.p"):
        try:
            cur = conn.cursor()
            cur.execute("select * from {0}likes_info limit 1".format(db))
        except:
            print ("You have no post data in your database")
            sys.exit()
        print ("A batch file is nescesary in order to make political analysis. Do you want to make it now? y/n")
        answer = get_inp(">>> ")
        while check_answer(answer,"y","n") == False:
            answer = get_inp(">>> ")
        if answer == "y":
            find_gender(conn, db)
            batch_file_menu(path_, conn, db)
        else:
            analytics_start_menu(conn, db, path_)
    
    else:
        clear_screen()
        print ("What kind of analysis do you wish to perform?")
        print ("\n")
        print ("1. Batch new file")
        print ("2. Gender_Pol_Modelling (Requires numpy, matplotlib and easygui)")
        print ("3. Pol_Network_Modelling (Requires numpy, matplotlib and networkx)")
        print ("4. Pol_Keyword_Modelling (Requires numpy, matplotlib and nltk)")
        print ("0. Quit program")
        answer = get_inp(">>> ")
        while check_answer(answer,"1","2","3","4","0") == False:
            answer = get_inp(">>> ")
            
        if answer == "1":
            find_gender(conn, db)
            batch_file_menu(path_, conn, db)
            
        elif answer == "2":
            import analytics.GenderPol as gp
            gp.main_gender_pol(path_, conn, db)
            analytics_start_menu(conn, db, path_)
        
        elif answer == "3":
            data_types = ""
            clear_screen()
            import analytics.pol_network as pn
            print ("What data do you want?")
            print ("\n")
            print ("1. All")
            print ("2. Comments")
            answer = get_inp(">>> ")
            while check_answer(answer,"1","2") == False:
                answer = get_inp(">>> ")
            if answer == "2": data_types = "comments"
            if answer == "1": data_types = "all"
            clear_screen()
            print ("What start date do you want? Type the exact format (yyyy-mm-dd). Example: 2015-11-18")
            answer = get_inp(">>> ")
            while check_date_answer(answer) == False:
                answer = get_inp(">>> ")
            start_date = str(answer)
            clear_screen()
            print ("Your start date is {0}. What end date do you want?".format(str(start_date)))
            answer = get_inp(">>> ")
            while check_date_answer(answer) == False:
                answer = get_inp(">>> ")
            end_date = str(answer)
            pn.draw_undi_graph(conn, db, path_, data_types, start_date, end_date)
            analytics_start_menu(conn, db, path_)
            
        elif answer == "4":
            import analytics.keyword_pol as kp
            kp.start_keywords(db, conn, path_)
            analytics_start_menu(conn, db, path_)
            
        elif answer == "0":
            quit_interface()
        
        
        
    
