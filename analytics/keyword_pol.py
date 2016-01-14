
import re
import datetime
from nltk.probability import FreqDist
import matplotlib.pyplot as plt
import numpy as np
import collections
from matplotlib.font_manager import FontProperties
import math
import sys
import os
import pickle
import sqlite3
from operator import itemgetter, attrgetter


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

class Simulator:
    
    
    def __init__(self,title,since,conn,path_):
        
        self.title = title
        self.since = since
        self._object_bank = {}
        self._object_count=0
        
        db = conn
        self.conn = db
        self.path_ = path_
        self._cur = db.cursor() 
        
        self._noise_string = "******************************"
    
    def mainMenu(self):
       
        clear_screen()
        print (self._noise_string+"Welcome to Facebook Pol_Keyword_Modelling"+self._noise_string+"\n")
        
        print ("What do you want to do? Enter the number corresponding to the tool you want or enter 0 to quit")
        
        inputloop = False
        print("1. Word Frequency Plots"+"\n"+"9. View already created plots")
        answer = get_inp(">>> ")
        
        while inputloop == False:
            
            if answer == '1':
                
                inputloop = True
                clear_screen()
                self.wfPlotMenu()
                
            elif answer == '2':
                
                inputloop = True
                clear_screen()
                
            elif answer == '3':
                
                inputloop = True
                clear_screen()
            
            elif answer == '9':
                
                if not self._object_bank:
                    print('List is empty, you must first create a plot')
                    answer = get_inp(">>> ")
                else:            
                    inputloop = True
                    clear_screen()
                    self.viewPlots()    
            
            elif answer == '0':
                inputloop = True
                sys.exit(0)
            else:
                print('please enter a valid answer')
                answer = get_inp(">>> ")
        

    def wfPlotMenu(self):
        
        print ("Do you want to analyze the word frequencies of aggregated entities or compare individual entities?")
        print ("Enter 9 to go back to main menu or 0 to quit"+"\n")
        inputloop = False
        
        print("1. Aggregated entities")
        start_answer = get_inp(">>> ")
        
        while inputloop == False:
        
            if start_answer == '1':
                clear_screen()
                self.wfPlotBuild(False, self.title)
                inputloop = True
                
            elif start_answer == '9':
                
                inputloop = True
                clear_screen()
                self.mainMenu()
            elif start_answer == '0':
    
                inputloop = True
                sys.exit(0)
            else:
                print('please enter a valid answer')
                start_answer = get_inp(">>> ")
                
    def wfPlotBuild(self,by,schema):
        
        self._cur.execute('select distinct P.web_name, count(P.post_message) from {0}post_info P, {0}page_info PA where PA.web_name = P.web_name group by P.web_name order by count(P.post_message) desc limit 10000000'.format(schema))
        
        elist = {}
        for row in self._cur.fetchall():
            elist[str(row[0])] = (str(row[1]))
        
        print ("Now, choose the entities with which the plot will be built"+"\n")
        print ("List of entities:"+"\n")
        
        for k,v in elist.items():
            print (str(k) + ' ('+str(v)+')')
        
        print ("\n"+"Enter the names of the entities you wish to include")
        if by == False:
            print ("Enter 'total' to include all entities")
        print("Enter 'done' when you are finished or 0 to quit")
        answer=get_inp(">>> ")
        
        choice_list = []
        
        inputloop = False
        while inputloop == False:
            if answer == "0":
                inputloop = True
                sys.exit(0)
            elif answer == "done":
                if not choice_list:
                    print("You have not chosen any entities")
                    answer=get_inp(">>> ")
                else:
                    clear_screen()
                    build = WordFrequency(schema,choice_list,by,self.since,self.conn,self.path_)
                    self._object_count+=1
                    self._object_bank[self._object_count] = build
                    
                    newloop=False
                    print("Would you like to create another plot? y/n")
                    done_answer = get_inp(">>> ")
                    while newloop == False:
                        if done_answer == 'y':
                            newloop=True
                            clear_screen()
                            self.wfPlotMenu()
                        elif done_answer == 'n':
                            inputloop = True
                            newloop=True
                            clear_screen()
                            self.viewPlots()
                        else:
                            print("you have not chosen any entities")
                            done_answer=get_inp(">>> ")
                            
            elif answer == "total":
                if by == True:
                    print("You cannot make a total count when comparing individual entities")
                    answer=get_inp(">>> ")
                else:
                    clear_screen()
                    build = WordFrequency(schema,[],by,self.since,self.conn,self.path_)
                    self._object_count+=1
                    self._object_bank[self._object_count] = build
                    
                    
                    newloop=False
                    print("Would you like to create another plot? y/n")
                    done_answer = get_inp(">>> ")
                    while newloop == False:
                        if done_answer == 'y':
                            newloop=True
                            clear_screen()
                            self.mainMenu()
                        elif done_answer == 'n':
                            inputloop = True
                            newloop=True
                            clear_screen()
                            self.viewPlots()
                        else:
                            print("you have not chosen any entities")
                            done_answer= get_inp(">>> ")
                    
            elif answer in elist:
                choice_list.append(answer)
                print(answer+" has been added, please choose the next one or enter 'done'")
                answer = get_inp(">>> ")
                
            else:
                print('please enter a valid answer')
                answer = get_inp(">>> ")
                
    
    def viewPlots(self):
        
        
        inputloop = False
        while inputloop == False:
            print("Enter the number of the plot you want to view or 0 to go to main menu")
            
            for k,v in self._object_bank.items():
                print(str(k)+": "+str(v.__class__.__name__)+": "+str(v.getEntities()))
            answer = get_inp(">>> ")
            
            found = False
            
            for k,v in self._object_bank.items():
                if int(answer) == k:
                    new_v = v
                    new_k = k
                    found = True
            if found == True:
                if str(new_v.__class__.__name__) == 'WordFrequency':
                    wf_inputloop = False
                    wf_list = []
                    outer_wf = []
                    clear_screen()
                    while wf_inputloop == False:
                        print("Please enter the word collection you want to query. Enter 'break' to create another set or enter 'done' if you are finished")
                        wf_answer = get_inp(">>> ").lower()
                        if wf_answer == 'done':
                            if not outer_wf and not wf_list:
                                print ("cannot search empty list")
                            else:
                                outer_wf.append(wf_list)
                                new_v.draw(outer_wf)
                                print("Do you want to make another query? y/n or enter co to see co-occuring keywords")
                                re_answer = get_inp(">>> ")
                                if re_answer == 'y':
                                    wf_list = []
                                    outer_wf = []
                                elif re_answer == 'co':
                                    new_v.find_co_occuring_keywords(self.conn)
                                    wf_inputloop=True
                                    wf_list = []
                                    self.viewPlots()
                                else:
                                    wf_inputloop=True
                                    wf_list = []
                                    self.viewPlots()
                        elif wf_answer == 'break':
                            outer_wf.append(wf_list)
                            wf_list = []
                        else:
                            clear_screen()
                            wf_list.append(wf_answer)
                            print ("So far you have chosen: ")
                            for f in wf_list: print (f)
                            for f in outer_wf: print (f)
            elif answer == "0":
                inputloop = True
                self.mainMenu()
            else:
                print('please enter a valid answer')
                answer = get_inp(">>> ")
        
        
        


"""class DanishWordCollection:
    
    
    def __init__(self,nouns,pronouns,prepositions,adverbs,adjectives,conjunctions,verbs):
        
        
        self._conjunctions = conjunctions
        self._pronouns = pronouns
        self._prepositions = prepositions
        self._adverbs = adverbs
        self._adjectives = adjectives
        self._nouns = nouns
        self._verbs = verbs
        
        db = MySQLdb.connect(host="localhost", user="root", passwd="", db="Facebook") 
        self._cur = db.cursor() 
        
        
    def verbs(self):
        tempdict={}
        self._cur.execute("select {0} from danish_words where {0} is not null limit 4132432".format(self._verbs))
        for row in self._cur.fetchall():
            tempdict[str(row[0])]=True
        
        return tempdict
    
    def nouns(self):
        tempdict={}
        self._cur.execute("select {0} from danish_words where {0} is not null limit 4132432".format(self._nouns))
        for row in self._cur.fetchall():
            tempdict[str(row[0])]=True
        
        return tempdict
    
    def adjectives(self):
        tempdict={}
        self._cur.execute("select {0} from danish_words where {0} is not null limit 4132432".format(self._adjectives))
        for row in self._cur.fetchall():
            tempdict[str(row[0])]=True
        
        return tempdict
    
    def adverbs(self):
        tempdict={}
        self._cur.execute("select {0} from danish_words where {0} is not null limit 4132432".format(self._adverbs))
        for row in self._cur.fetchall():
            tempdict[str(row[0])]=True
        
        return tempdict
    
    def prepositions(self):
        tempdict={}
        self._cur.execute("select {0} from danish_words where {0} is not null limit 4132432".format(self._prepositions))
        for row in self._cur.fetchall():
            tempdict[str(row[0])]=True
        
        return tempdict
    
    def pronouns(self):
        tempdict={}
        self._cur.execute("select {0} from danish_words where {0} is not null limit 4132432".format(self._pronouns))
        for row in self._cur.fetchall():
            tempdict[str(row[0])]=True
        
        return tempdict
    
    def conjunctions(self):
        tempdict={}
        self._cur.execute("select {0} from danish_words where {0} is not null limit 4132432".format(self._conjunctions))
        for row in self._cur.fetchall():
            tempdict[str(row[0])]=True
        
        return tempdict


    def getWords(self,type_list):
        tlist = type_list
        tempset={}
        for t in tlist:
            if t == 'nouns':
                tempset.update(self.nouns())
            if t == 'verbs':
                tempset.update(self.verbs())
            if t == 'adjectives':
                tempset.update(self.adjectives())
            if t == 'adverbs':
                tempset.update(self.adverbs())
            if t == 'pronouns':
                tempset.update(self.pronouns())
            if t == 'conjunctions':
                tempset.update(self.conjunctions())
            if t == 'prepositions':
                tempset.update(self.prepositions())
        
        return tempset"""
                


class WordFrequency:
    
    def __init__(self,schema,entities,by,since, conn,path_):
        
        
        db = conn 
        self._cur = db.cursor()
        self.conn = conn
        self.path_ = path_
        
        self._last_by_ids = []
        self._last_word_list = []
        self._by_id_already_parsed = {}
        self._schema = schema
        self._entities = entities
        self._by = by
        self._wordset = {}
        self._wordlists = []
        self.since = since
        
        
        self._by_id_already_parsed = pickle.load( open( path_+"/analytics/batch/" +"pol_by_id.p", "rb" ) )
        
        
        print (len(self._by_id_already_parsed))
        
        print('Loading database...')
        
        if self._by == False:
            self._wordlists = self.createWordFreq(self._schema, self._entities)
        else:
            for e in self._entities:
                self._templ = []
                self._templ.append(e)
                self._wordset[e] = self.createWordFreq(self._schema, self._templ)
    
        print('Loading finished!')
        
    def getEntities(self):
        
        return self._entities
    
    def createWordFreq(self,schema,entities):
        
        if not entities:
            total_count = True
        else:
            total_count = False
        
        
        if total_count == True:
            
            #self._cur.execute("select C.time_created, C.message, C.by_id from {0}comment_info C where date(C.time_created) > date('{1}')  order by date(time_created) asc, by_id asc limit 1000000000000".format(schema,self.since))
            self._cur.execute("select C.comment_time_created as tim, C.comment_message, C.comment_made_by_id from {0}comment_info C where date(C.comment_time_created) > date('{1}') union select R.reply_time_created as tim, R.reply_message, R.reply_made_by_id from {0}replies_info R where date(R.reply_time_created) > date('{1}') order by tim asc, C.comment_made_by_id asc limit 1000000000000".format(schema,self.since))
            #self._cur.execute("select C.time_created, C.message, C.by_id from {0}comment_info C, {0}post_info P, post_comment_like_dif D where C.post_id = P.id and P.fb_post_id = D.fb_post_id and D.dif > 10 and date(C.time_created) > date('{1}') union select R.time_created, R.message, R.by_id from {0}replies_info R, {0}comment_info C, {0}post_info P, post_comment_like_dif D where R.comment_id = C.comment_id and C.post_id = P.id and P.fb_post_id = D.fb_post_id and D.dif > 10 and date(R.time_created) > date('{1}') order by date(time_created) asc, by_id asc limit 1000000000000".format(schema,self.since))

        else:
            s = ''
            for u in entities:
                s = s + '"'+u+'"' + ' or P.web_name = '
            s = s[:-17]
            print (str(entities))
            self._cur.execute("select C.comment_time_created as tim, C.comment_message, C.comment_made_by_id from {0}comment_info C, {0}post_info P where date(C.comment_time_created) > date('{2}') and C.post_id = P.id and (P.web_name = {1}) union select R.reply_time_created as tim, R.reply_message, R.reply_made_by_id from {0}replies_info R, {0}comment_info C, {0}post_info P where date(R.reply_time_created) > date('{2}') and R.comment_id = C.comment_id and C.post_id = P.id and (P.web_name = {1}) order by tim asc, C.comment_made_by_id asc limit 1000000000000".format(schema,s,self.since))
       
            
        wd_dict = {}
        total_wd = {}
        prevDate = datetime.datetime.strptime("1980-01-01",'%Y-%m-%d')
        prevBy = ''
        by_wd = {}
        by_wd_list = []
        by_wd[prevDate] = {}
        wd_dist = FreqDist()
        by_dist = FreqDist()
        total = 0
        print ("Processing...")
        for row in self._cur.fetchall():
            
            dato = datetime.datetime.strptime(str(row[0])[:10],'%Y-%m-%d')
            nowDate = dato
            by_id = str(row[2])
            if nowDate != prevDate:
                
                print (nowDate)
                wd_dict[prevDate] = wd_dist
                wd_dist = FreqDist()
                total_wd[prevDate] = total
                total = 0
                by_wd[prevDate] = by_wd_list
                by_wd_list = []
                by_dist = FreqDist()
                templist = []
                templist = re.findall("[\w'æøå#]+|[?]", row[1].strip())
                for w in templist:
                    wd_dist[w.lower()] += 1
                    total +=1
                    by_dist[w.lower()] += 1
                tempset = {}
                tempset[by_id]=by_dist
                by_wd_list.append(tempset)
                by_dist = FreqDist()
                    
            else:
                templist = []
                templist = re.findall("[\w'æøå#]+|[?]", row[1].strip())
                for w in templist:
                    wd_dist[w.lower()] += 1
                    total +=1
                    by_dist[w.lower()] += 1
                tempset = {}
                tempset[by_id]=by_dist
                by_wd_list.append(tempset)
                by_dist = FreqDist()
                
                """if prevBy != by_id:
                    by_wd[prevDate]=by_dist
                    by_dist = FreqDist()
                    for w in templist:
                        by_dist[unicode(w,"utf-8").lower()] += 1
                else:
                    for w in templist:
                        by_dist[unicode(w,"utf-8").lower()] += 1"""
                    
            prevDate = dato
            prevBy = by_id
        
        del wd_dict[datetime.datetime.strptime("1980-01-01",'%Y-%m-%d')]
        del total_wd[datetime.datetime.strptime("1980-01-01",'%Y-%m-%d')]
        del by_wd[datetime.datetime.strptime("1980-01-01",'%Y-%m-%d')]
        new_wd_dict = sorted(wd_dict.items())
        new_total_wd = total_wd
        new_by_wd = sorted(by_wd.items())
        listo=[]
        listo.append(new_wd_dict)
        listo.append(new_total_wd)
        listo.append(new_by_wd)
            
        return listo

    def createWordFreqValues(self,arglist,searchWords,conn):
        
        def assign_wing(pol_by_id,wing):
    
            rb = {'b':0.0,'r':0.0}
            if not pol_by_id:
                pass
            else:
                p = pol_by_id
                rb['b']+=p['O']
                rb['b']+=p['V']
                rb['b']+=p['C']
                rb['b']+=p['I']
                rb['r']+=p['OE']
                rb['r']+=p['A']
                rb['r']+=p['B']
                rb['r']+=p['F']
                rb['r']+=p['AA']
                rb['r']+=p['N']
            if wing == 'r':
                return rb['r']
            else:
                return rb['b']
            
        """def get_pol_from_by_id(by_id,pol_by_id):
    
            connection = MySQLdb.connect(host="localhost", user="root", passwd="swordfish", db="Facebook") 
            cur = connection.cursor()
            bid_like_count = 0
            
            tempset = {}
            if bid_like_count >= 0:
            
                cur.execute("select PE.party, count(P.id) from DK_POLITICS_post_info P, political_entities PE where PE.web_name = P.web_name and P.id in (select post_id from DK_POLITICS_likes_info  where by_id = '{0}') group by PE.party".format(str(by_id)))
            
                total_likes = float(0.0)
                for r in cur.fetchall():
                    tempset[str(r[0])]=float(r[1])
                    total_likes = float(r[1]) + total_likes
                
                if total_likes < 4:
                    pass
                    return {}
                else:
                    for k,v in tempset.iteritems():
                        pol_by_id[k]+=float((v/total_likes))
                    
                    return pol_by_id"""
                
        def create_empty_pol_set(conn):
            
            connection = conn
            total_count = {}
            cur = connection.cursor()
            
            cur.execute("select distinct party from political_entities")
            for row in cur.fetchall():
                total_count[str(row[0])]=0.0
            empty_set = total_count
            
            return empty_set
        
        empty_pol_set = create_empty_pol_set(conn)
        search_words = searchWords
        tlist = arglist
        worddict = tlist[0]
        datedict = tlist[1]
        by_iddict = tlist[2]
    
        value_set = {}
        wings = ['r','b']
        self._last_by_ids = []
        self._last_word_list = search_words
        
        print ("Building plot...")
        
        for w in search_words:
            xlist1 = []
            ylist1 = []
            xlist2 = []
            ylist2 = []
            pair_list1 = []
            pair_list2 = []
            for k,v in by_iddict:
                ry = 0
                by = 0
                for r in v:
                    for kk,vv in r.items():
                        y = 0
                        y_total = 0
                        for ww in w:
                            y = vv.get(ww)
                            if not y == None:
                                y_total = y + y_total
                        if y_total > 0:
                            self._last_by_ids.append(r)
                            if kk in self._by_id_already_parsed:
                                ry = assign_wing(self._by_id_already_parsed[kk],'r')*y_total + ry
                                by = assign_wing(self._by_id_already_parsed[kk],'b')*y_total + by
                            else:
                                pass
                        else:
                            ry = ry + y_total
                            by = by + y_total
                xlist1.append(k)
                ylist1.append(ry/(float(datedict[k])+float(0.0000001)))
                xlist2.append(k)
                ylist2.append(by/(float(datedict[k])+float(0.0000001)))
            pair_list1.append(xlist1)
            pair_list1.append(ylist1)
            pair_list2.append(xlist2)
            pair_list2.append(ylist2)
            label_string = ''
            for sword in w:
                label_string = label_string + sword + ', '
                break
            label_string = label_string[:-2]
            value_set[label_string+" : "+"Left wing users"]=pair_list1
            value_set[label_string+" : "+"Right wing users"]=pair_list2
            new_value_set = sorted(value_set.items(), key=itemgetter(0), reverse=True)
            
        
        """for w in search_words:
            pair_list = []
            xlist = []
            ylist = []
            for d, wd in worddict.iteritems():
                x = d
                y = wd.get(w)
                if y == None:
                    y = 0
                xlist.append(x)
                ylist.append(y/float(tlist[1].get(d)))
            pair_list.append(xlist)
            pair_list.append(ylist)
            value_set[w] = pair_list"""
            
        
        return new_value_set
    
    def find_co_occuring_keywords(self,conn):
        
        self.conn = conn
        
        def create_word_filters(facebook,title,extra,except_words,conn):

            connection = conn
            cur = connection.cursor()
            
            x_words = {}
            if extra == True:
                cur.execute("select word from extrawords")
                for row in cur.fetchall():
                    x_words[row[0].lower()]=True
                    print (row[0])
            
            com_words = {}
            cur.execute("select word from common_danish_words")
            for row in cur.fetchall():
                com_words[row[0].lower()]=True
            for w in except_words:
                del com_words[w]
                
            eng_words = {}
            cur.execute("select word from common_english_words")
            for row in cur.fetchall():
                eng_words[row[0].lower()]=True
            
            return [eng_words,com_words,x_words]

        def clean_words(worddict,limit,facebook,word_filters,extralist):   
            
            clean_worddict = {}
            
            if facebook == False:
                for k,v in worddict.items():
                    if k not in word_filters[0] and len(k) > 1 and k not in word_filters[1] and k not in word_filters[2] and k not in word_filters[3] and k not in word_filters[4] and k not in extralist:
                        if v > limit:
                            clean_worddict[k]=v
            else:
                for k,v in worddict.items():
                    if k not in word_filters[0] and len(k) > 1 and k not in word_filters[1] and k not in word_filters[2] and k not in extralist:
                        if v > limit:
                            clean_worddict[k]=v
                            
            return clean_worddict
        
        def assign_wing(pol_by_id,wing):
    
            rb = {'b':0.0,'r':0.0}
            if not pol_by_id:
                pass
            else:
                p = pol_by_id
                rb['b']+=p['O']
                rb['b']+=p['V']
                rb['b']+=p['C']
                rb['b']+=p['I']
                rb['r']+=p['OE']
                rb['r']+=p['A']
                rb['r']+=p['B']
                rb['r']+=p['F']
                rb['r']+=p['AA']
                rb['r']+=p['N']
            if wing == 'r':
                return rb['r']
            else:
                return rb['b']
        
        def get_BAC(word,dist):
            
            total = 0
            for v in dist.values():
                total = total + v
                
            BAC = (float(dist[word])/float(total))*1000
            
            return BAC
        
        def go_deeper(word):
            
            r_co = FreqDist()
            b_co = FreqDist()
        
            for d in self._last_by_ids:
                for kk,vv in d.items():
                    if word in vv:
                        if kk in self._by_id_already_parsed:
                            if assign_wing(self._by_id_already_parsed[kk],'r') > 0.75:
                                for w,s in vv.items():
                                    if not w in self._last_word_list[0]:
                                        r_co[w]+=s
                            elif assign_wing(self._by_id_already_parsed[kk],'b') > 0.75:
                                for w,s in vv.items():
                                    if not w in self._last_word_list[0]:
                                        b_co[w]+=s
                            else:
                                pass
                    else:
                        pass
            word_filters2 = create_word_filters(True, "", False, ['ikke'],conn)
            r_co_c = clean_words(r_co, 0, True, word_filters2, [])
            b_co_c = clean_words(b_co, 0, True, word_filters2, [])
                    
            return [sorted(r_co_c.items(), key=lambda x:(x[1]) ,reverse=True),sorted(b_co_c.items(), key=lambda x:(x[1]) ,reverse=True),r_co,b_co]
        
        aloop = False
        r_co = FreqDist()
        b_co = FreqDist()
        
        for d in self._last_by_ids:
            for kk,vv in d.items():
                try:
                    if assign_wing(self._by_id_already_parsed[kk],'r') > 0.75:
                        for w,s in vv.items():
                            r_co[w]+=s
                    elif assign_wing(self._by_id_already_parsed[kk],'b') > 0.75:
                        for w,s in vv.items():
                            b_co[w]+=s
                    else:
                        pass
                except:
                    pass
        print (r_co)
        word_filters = create_word_filters(True, "", False, [], conn)
        r_co_c = clean_words(r_co, 0, True, word_filters, [])
        b_co_c = clean_words(b_co, 0, True, word_filters, [])
        
        r_co_c = sorted(r_co_c.items(),key=lambda x:(x[1]) ,reverse=True)
        b_co_c = sorted(b_co_c.items(),key=lambda x:(x[1]) ,reverse=True)
        
        
        def print_result(r_co_c,b_co_c,r_co,b_co):
            
            counter = 0
            print ("Red co-occuring keywords: ")
            for k,v in r_co_c:
                print (k + " : " + str(v) + "   -   " + "red BAC: " + str(get_BAC(k, r_co)) + " and blue BAC: " + str(get_BAC(k, b_co)))
                counter+=1
                if counter > 10:
                    break
            
            counter = 0
            print ("Blue co-occuring keywords: ")
            for k,v in b_co_c:
                print (k + " : " + str(v) + "   -   " + "blue BAC: " + str(get_BAC(k, b_co)) + " and red BAC: " + str(get_BAC(k, r_co)))
                counter+=1
                if counter > 10:
                    break
                
        print_result(r_co_c, b_co_c,r_co,b_co)
            
        first_run = True
        while aloop == False:
            print ("Do you want to go deeper? y/n")
            answer = get_inp(">>> ")
            if answer == "y":
                if first_run == False:
                    print_result(r_co_c, b_co_c,r_co,b_co)
                print ("please enter word")
                word_answer = get_inp(">>> ").lower()
                deep = go_deeper(word_answer)
                print_result(deep[0], deep[1], deep[2], deep[3])
                first_run = False
            elif answer == 'n':
                aloop = True
            else:
                print ("please enter valid answer")
            
    
    def createWordFreqPlot(self,searchWords):
        
        value_set = self.createWordFreqValues(self._wordlists,searchWords,self.conn)
        colors = ['blue', 'red', 'black', 'brown', 'green','yellow']
        counter = 0
        for k, v in value_set:    
            
            fontP = FontProperties()
            fontP.set_size('small')
            plt.suptitle(str(self._entities))
            plt.plot(v[0],v[1],label=k,color=colors[counter], lw=2.0)
            plt.legend(loc='upper left',ncol=3,prop = fontP)
            counter +=1
            if counter > 6:
                counter = 0
            
        plt.show()


    def createWordFreqPlotByEntity(self,searchWords):
        counter = 0 
        colors = ['blue', 'red', 'black', 'brown', 'green','yellow']

        for k,v in self._wordset.items():
            value_set = self.createWordFreqValues(v, searchWords,self.conn)
            for kk, vv in value_set:
                
                fontP = FontProperties()
                fontP.set_size('small')
                plt.suptitle(str(self._entities))
                plt.plot(vv[0],vv[1],label=k+' : '+str(kk),color=colors[counter],lw=2.0)
                plt.legend(loc='upper left',ncol=3,prop = fontP)
                counter +=1 
                if counter > 6:
                    counter = 0
        plt.show()
        
        
    def draw(self,searchWords):
        
        if self._by == False:
            self.createWordFreqPlot(searchWords)
        else:
            self.createWordFreqPlotByEntity(searchWords)
            

            

"""class LingPol:
    
    def __init__(self):
        
        db = MySQLdb.connect(host="localhost", user="root", passwd="", db="Facebook") 
        self._cur = db.cursor()
        
        self._ex_inter_set={}
    
    
    def createInternalWordLists(self,schema,entities,wordtypes,threshh,internal):
        
        intern_ents = self.analyzeRank(schema, [str(entities[0]+'2013'),str(entities[1]+'2014')], str(entities[1]+'2014'), wordtypes, threshh, internal)
        print(intern_ents)
        intern_num = int(intern_ents[str(entities[0]+'2013')])
        
        return intern_num
        
    
    
    def createWordLists(self,schema,entities,wordtypes,threshh,internal):
        
        wordclass = True
        
        if not wordtypes:
            wordclass = False
        
        ent_list = entities
        wd_lists = {}
        ex_inter_set={}
        total = 0
        for e in ent_list:
            wd_dist = FreqDist()
            if internal == False:
                self._cur.execute("select C.message from {0}comment_info C, DK_NEWS_post_info P where C.post_id = P.id and P.web_name = {1} union select P.message from {0}post_info P where P.web_name = {1} union select R.message from {0}replies_info R, DK_NEWS_comment_info C, DK_NEWS_post_info P where R.comment_id = C.comment_id and C.post_id = P.id and P.web_name = {1} limit 1000000000000".format(schema,'"'+e+'"'))
            else:
                self._cur.execute("select C.message from {0}comment_info C, DK_NEWS_post_info P where C.post_id = P.id and P.web_name = {1} and year(P.time_created) = {2} union select P.message from {0}post_info P where P.web_name = {1} and year(P.time_created) = {2} union select R.message from {0}replies_info R, DK_NEWS_comment_info C, DK_NEWS_post_info P where R.comment_id = C.comment_id and C.post_id = P.id and P.web_name = {1} and year(P.time_created) = {2} limit 1000000000000".format(schema,'"'+e[:-4]+'"',int(e[-4:])))
            
            if wordclass == False:
                for row in self._cur.fetchall():
                    templist = []
                    templist = re.findall(r"[\w']+|[!?;:()]", str(row[0]).rstrip())
                    for w in templist:
                        wd_dist[w.lower()] += 1
            else:
                coll = DanishWordCollection('substantiver', 'pronominer', 'prepositioner', 'adverbier', 'adjektiver', 'konjuktioner', 'verber')
                wt = coll.getWords(wordtypes)
                for row in self._cur.fetchall():
                    templist = []
                    templist = re.findall(r"[\w']+|[!?;:()]", str(row[0]).rstrip())
                    for w in templist:
                        if w in wt:
                            wd_dist[w.lower()] += 1
                        else:
                            pass
            wd_dist={key: value for key, value in wd_dist.items() if value > threshh}
            best_vals = sorted(wd_dist.iteritems(), key=lambda (w, s): s, reverse=False)
            prev=0
            rank=0
            rank_set = {}
            for w,f in best_vals:
                if f > prev:
                    rank+=1
                    rank_set[w]=rank
                    prev=f
                else:
                    rank_set[w]=rank
            
            wd_lists[e]=rank_set
            
              
        return wd_lists
    
    def analyzeRank(self,schema,entities,maentity,wordtypes,threshh,internal):
        
        value_set = self.createWordLists(schema,entities,wordtypes,threshh,internal)
        pol_set = {}
        non_set = {}
        inter_set = {}
        ex_inter_set={}
        
        
        for e in entities:
            pol_total = 0
            non_total = 0
            prevp = 0
            s=''
            for k, v in value_set[maentity].iteritems():
                p=0
                x=0
                y=0
                if k in value_set[e]:
                    y = value_set[e][k]
                    x = v
                    if x > y:
                        p = x-y
                    else:
                        p = y-x
                    if p > prevp:
                        s = str(k)
                    prevp = p
                    pol_total = pol_total + p
                else:
                    non_total+=1
                    y=0
                    x=v
                    p = x - y
                    pol_total = pol_total + p
            if internal == False:
                iii = self.createInternalWordLists(schema, [e,e], wordtypes, threshh, True)
                inter_set[e]=iii
                if e != maentity:
                    uuu = self.createInternalWordLists(schema, [e,maentity], wordtypes, threshh, True)
                    ex_inter_set[e]=uuu
                    uuu = self.createInternalWordLists(schema, [maentity,e], wordtypes, threshh, True)
                    ex_inter_set[maentity]=uuu
            pol_set[e]=pol_total
            non_set[e]=non_total
        if internal == True:
            
            return pol_set
        else:
            pass
            
        
        final_set = {}
        print(s)
        print(inter_set)
        print(ex_inter_set)
        ma_inter = inter_set[maentity]
        ex_ma_inter = ex_inter_set[maentity]
        for k,v in inter_set.iteritems():
            print(ex_inter_set[k])
            print(ex_ma_inter)
            print(ma_inter)
            print(v)
            n = (math.sqrt((ex_inter_set[k]*ex_ma_inter)))/(math.sqrt((ma_inter*v)))
            final_set[k]=n
            
        print(final_set)
        print(pol_set)
        print(non_set)
        
        

class SimpleTimePlot:
    
    def __init__(self,schema,entities,countable):
        
        db = MySQLdb.connect(host="localhost", user="root", passwd="", db="Facebook") 
        self._cur = db.cursor()
        
        self._schema = schema
        self._entities = entities
        if not self._entities:
            self._entities.append(schema)
        self._countable = countable
        self._readyset = {}
        
        print 'Loading database...'
        
        for e in self._entities:
            self._readylist = []
            self._readylist = self.makeData(self._schema, e, countable)
            self._readyset[e] = self._readylist
        
        print 'Loading finished!'
        
    def makeData(self,schema,entity,countable):
        
        if entity == schema:
            if countable == 'likes':
                self._cur.execute('select P.time_created, sum(P.likes_count)/count(P.id) from {0}post_info P group by year(P.time_created),month(P.time_created) order by P.time_created asc limit 3143212421'.format(schema))
            if countable == 'comments':
                self._cur.execute('select C.time_created, count(C.id)/count(distinct P.id) from {0}comment_info C, {0}post_info P where C.post_id = P.id group by year(C.time_created), month(C.time_created) order by C.time_created asc limit 431421332'.format(schema))
        else:
            if countable == 'likes':
                self._cur.execute('select P.time_created, sum(P.likes_count)/count(P.id) from {0}post_info P where P.web_name = "{1}" group by year(P.time_created),month(P.time_created) order by P.time_created asc limit 3143212421'.format(schema,entity))
            if countable == 'comments':
                    self._cur.execute('select C.time_created, count(C.id)/count(distinct P.id) from {0}comment_info C, {0}post_info P where P.web_name = "{1}" and P.id = C.post_id group by year(C.time_created), month(C.time_created) order by C.time_created asc limit 431421332'.format(schema,entity))
        
        
        return self._cur.fetchall()
    
    def getCountable(self,data):
        
        xlist=[]
        ylist=[]
        s = ''
        mlist=[]
        
        for row in data:
            s = str(row[0])
            dato = datetime.strptime(s[:10],'%Y-%m-%d')
            
            xlist.append(dato)
            ylist.append(int(row[1]))
        
        mlist.append(xlist)
        mlist.append(ylist)
        
        return mlist
    
    def draw(self):
        
        for k,v in self._readyset.iteritems():
            v = self.getCountable(v)
                
           
            fontP = FontProperties()
            fontP.set_size('small')
            plt.plot(v[0],v[1],label=k,lw=1.5)
            plt.legend(loc='upper left',ncol=2,prop = fontP)

        plt.show()"""



#p = WordFrequency('DK_NEWS_',['viunge','politiken'],False)
#p.createWordFreqPlotByEntity(['dansk','dansk','statsborger'],"DK_NEWS_",['ekstrabladet','dagbladetinformation','ditbt'])
#p.createWordFreqPlot(['dansk','dansker','statsborger'], "DK_NEWS_", [])

#wordtypes = ['verbs','nouns','pronouns','prepositions','conjunctions','adverbs','adjectives']
#l = LingPol()
#l.analyzeRank('DK_NEWS_', ['politiken','dagens.dk','viunge','ekstrabladet','tv2news',], 'politiken',wordtypes,0,False)


#st = SimpleTimePlot('DK_NEWS_', ['viunge','ekstrabladet','ditbt',],'likes')
#st.draw()               
#st.drawTotal('DK_NEWS_', 'comments')

#p.draw(['penge','forskning','kultur'])
#p.draw(['piger','drenge','fyre'])



since = '2015-01-01'

def start_keywords(title,conn,path_):
    sim = Simulator(title,since,conn,path_)
    sim.mainMenu()
                   
        
        
    
    