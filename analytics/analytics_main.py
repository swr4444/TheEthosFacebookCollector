import os
import sys
import sqlite3
from os import listdir
import pickle
import codecs
import csv
import datetime
import re

FBC = '/FBC_databases'
crawl_logs = '/DB'
pro_lists = '/Projects'
page_lists = '/Page Lists'
analytics = '/analytics'
global pol_by_id
pol_by_id = {}

def find_names(url_list,only_first_names):
    
    import urllib.request
    from bs4 import BeautifulSoup
    name_list = []
    
    for url in url_list:
        try:    
            web_response = urllib.request.urlopen(url)
            readable_page = web_response.read().decode('latin-1')
            
            html = readable_page.encode('latin-1')
            soup = BeautifulSoup(html, "html.parser")
            text_ = soup.find_all()
            for element in text_:
                raw_text = str(element.text).rstrip().replace('\n',' ').replace('Denne','').replace("\t"," ")
                if only_first_names == False:
                    names = re.sub( '\s+', ' ', raw_text ).strip()
                    print (names)
                    names = re.findall(r"([A-Z][\w-]+(?=\s[A-Z])(?:\s[A-Z][\w-]+)+)",names.rstrip())
                else:
                    names = re.findall(r"([A-Z][\w-]+)",raw_text.rstrip())                
                for name in names:
                    if name not in name_list:
                        name_list.append(str(name))
        except:
            #print ("Text find not possible")
            pass
        
    return name_list

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
        
def get_first_names(path_,gender='male'):
    
    if gender == 'male':
        if os.path.isfile(path_+analytics+"/batch/"+"danske_drengenavne.p"):
            male_names = pickle.load(open(path_+analytics+"/batch/"+"danske_drengenavne.p", "rb" ))
        else:
            rn_list = ["http://www.danskernesnavne.navneforskning.ku.dk/Topnavne/Topnavn_reg10_s1_f.asp"]
            male_names = find_names(rn_list,True)
            pickle.dump(male_names, open(path_+analytics+"/batch/"+"danske_drengenavne.p", "wb" ))
            
        return male_names
            
    elif gender == 'female':
        if os.path.isfile(path_+analytics+"/batch/"+"danske_pigenavne.p"):
            female_names = pickle.load(open(path_+analytics+"/batch/"+"danske_pigenavne.p", "rb" ))
        else:
            rn_list = ["http://www.danskernesnavne.navneforskning.ku.dk/Topnavne/Topnavn_reg10_s0_f.asp"]
            female_names = find_names(rn_list,True)
            pickle.dump(female_names, open(path_+analytics+"/batch/"+"danske_pigenavne.p", "wb" ))
            
        return female_names
        
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
        
def analysis_complete():
    
    print ("\n")
    print ("Analysis complete.")
    print ("\n")
    answer = get_inp("Press any key to continue")


def check_answer(answer,*args, answer_length=0):
    
    if answer_length > 0:
        if len(str(answer)) < answer_length:
            return True
        else:
            print ("Input too long")
    
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
    
def set_custom_values(values):
    
    clear_screen()
    current_values = values
    new_values = {}
    
    v_count = 0
    for k,v in values.items():
        v_count += 1
        new_values[str(v_count)]=k
    
    def change_value(new_values,current_values,choice_value):
        
        if current_values[new_values[choice_value]] == False:
            current_values[new_values[choice_value]]=True
        else:
            current_values[new_values[choice_value]]=False
        
    def show_values(new_values,current_values):
        
        for k,v in new_values.items():
            if current_values[v] == False:
                new_v = "No"
            else:
                new_v = "Yes"
                
            print (str(k)+". "+str(v).replace("_","")+"  :  "+str(new_v))
    
    answer = ""
    while answer != 'done':
        print ("Enter the setting you wish to change. Enter 'done' when finished")
        print ("\n")
        show_values(new_values,current_values)
        print ("\n")
        answer = get_inp(">>> ")
        while check_answer(answer,*new_values.keys(),'done') == False:
            answer = get_inp(">>> ")
        if answer != 'done':
            change_value(new_values, current_values, answer)
            clear_screen()
            
    return current_values


def select_pages_from_db(conn,db):
    
    clear_screen()
    web_names = {}
    chosen_pages = []
    pages = {}
    cur = conn.cursor()
    cur.execute("select page_name,web_name from {0}page_info limit 100000".format(db))
    row_count = 0
    for row in cur.fetchall():
        row_count += 1
        pages[str(row_count)]=str(row[0])
        web_names[str(row[0])]=str(row[1])
        
    answer = ""
    while answer != 'done':
        print ("Please enter the page you want to add. Enter 'done' when finished.")
        answer = get_inp(">>> ")        
        while check_answer(answer,*pages.keys()) == False:
            answer = get_inp(">>> ")
        clear_screen()
        chosen_pages.append(web_names[pages[answer]])
        print (str(pages[answer]) + " has been added.")
        print ("\n")
    
    return chosen_pages
    

def create_empty_pol_set(conn):
    
    total_count = {}
    cur = conn.cursor()
    cur.execute("select distinct party from political_entities")
    for row in cur.fetchall():
        total_count[str(row[0])]=0.0
    empty_set = total_count
    
    return empty_set

def get_pol_from_id(by_id,pol_set,cur,db):
    
    cur.execute("select PE.party, count(P.id) from {0}post_info P, political_entities PE, {0}page_info PA where PE.web_name = PA.web_name and P.post_made_by_id = PA.page_id and P.id in (select post_id from {0}likes_info indexed by idxbi where post_like_by_id = '{1}') group by PE.party".format(db,str(by_id)))
    
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
    cur.execute("CREATE INDEX IF NOT EXISTS idxw ON political_entities (web_name, name, party);")
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
    check_for_extra_data(path_, conn, current_db)
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
    cur.execute("CREATE  TABLE IF NOT EXISTS `common_danish_words` (`word` text,`id` INTEGER PRIMARY KEY AUTOINCREMENT);")
    cur.execute("CREATE  TABLE IF NOT EXISTS `common_english_words` (`word` text,`id` INTEGER PRIMARY KEY AUTOINCREMENT);")
    cur.execute("CREATE  TABLE IF NOT EXISTS `extrawords` (`word` text,`id` INTEGER PRIMARY KEY AUTOINCREMENT);")
    cur.execute("CREATE  TABLE IF NOT EXISTS `male_names` (`name` VARCHAR(200),`id` INTEGER PRIMARY KEY AUTOINCREMENT);")
    cur.execute("CREATE  TABLE IF NOT EXISTS `female_names` (`name` VARCHAR(200),`id` INTEGER PRIMARY KEY AUTOINCREMENT);")
    cur.execute('select * from female_names')
    if not cur.fetchall():
        for name in get_first_names(path_, gender='female'):
            cur.execute("insert into female_names (name) VALUES (?)",[name])
    cur.execute('select * from male_names')
    if not cur.fetchall():
        for name in get_first_names(path_, gender='male'):
            cur.execute("insert into male_names (name) VALUES (?)",[name])
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
        print ("5. Overall political swing")
        print ("0. Quit program")
        answer = get_inp(">>> ")
        while check_answer(answer,"1","2","3","4","5","0") == False:
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
            import analytics.pol_network2 as pn
            print ("What data do you want?")
            print ("\n")
            print ("1. All")
            #print ("2. Comments")
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
            pn.make_all_pol_interactions(conn, db, path_, data_types=data_types, start_date=start_date, end_date=end_date)
            analytics_start_menu(conn, db, path_)
            
        elif answer == "4":
            import analytics.keyword_pol as kp
            kp.start_keywords(db, conn, path_)
            analytics_start_menu(conn, db, path_)
            
        elif answer == "5":
            clear_screen()
            import analytics.Political_swing as pw
            political_swing_settings = {"compare_":False,"election_weights_":False,"print_result":True}
            print ("What do you want as title for your output? Max 70 characters.")
            answer = get_inp(">>> ")
            while check_answer(answer,answer_length=70) == False:
                answer = get_inp(">>> ")
            title = str(answer)
            clear_screen()
            print ("Do you want select pages or all pages in the database?")
            print ("\n")
            print ("1. All pages")
            print ("2. select pages")
            answer = get_inp(">>> ")
            while check_answer(answer,"1","2") == False:
                answer = get_inp(">>> ")
            if str(answer) == "1":
                political_swing_settings = set_custom_values(political_swing_settings)
                pw.get_swing(path_,conn,db,[],title_=title,**political_swing_settings)
                analysis_complete()
                
            elif answer == "2":
                select_pages_from_db(conn, db)
                political_swing_settings = set_custom_values(political_swing_settings)
                pw.get_swing(path_,conn,db,[],title_=title,**political_swing_settings)
                analysis_complete()
                
            elif answer == "0":
                quit_interface()
                
            analytics_start_menu(conn, db, path_)
            
        elif answer == "0":
            quit_interface()
        
        
        
    
