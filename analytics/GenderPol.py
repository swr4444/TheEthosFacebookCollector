 # -*- coding: utf-8 -*-
from tkinter import ttk
from tkinter import *
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pylab
import collections
import math
from easygui import *
from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import os
import pickle
import sys
import sqlite3
from analytics.InteractivePlot import InteractivePlot
from analytics.pol_post import pol_post
from analytics.AnnoteFinder import AnnoteFinder
import matplotlib.colors
import numpy as np

class FacebookApp:

    def __init__(self, master, path_, conn, db):
        self.path_ = path_
        self.connection = conn
        self.cur = self.connection.cursor()
        self.title = db.replace(".txt","")
        self._by_id_already_parsed = pickle.load( open( path_+"/analytics/batch/pol_by_id.p", "rb" ) )

        self.post_already_parsed = {}
        self.special_parsed = {}
        self.post_dif_list = []
 
        try:
            self.interactive_plot_list = self.load_old_plots()
        except:
            self.interactive_plot_list = []
            print ("No Load File")
            
        try:
            self.cur.execute('select * from {0}likes_info limit 1'.format(self.title))
        except:
            print ("You have no post data in your database")
            sys.exit()
       
        self.frame_header = ttk.Frame(master)
        self.frame_content = ttk.Frame(master)
        self.frame_content2 = ttk.Frame(master)
        self.frame_midbottom = ttk.Frame(master)
        self.frame_header.pack()
        self.frame_side_content = ttk.Frame(self.frame_content)
        self.pbar = ttk.Progressbar(self.frame_side_content, orient = "horizontal", length=200)
        self.pbar.config(mode = 'determinate', maximum = 5, value = 0.0)
        self.frame_model = ttk.Frame(master)
        self.frame_old_content = ttk.Frame(master)
        self.type_button = ttk.Label(self.frame_side_content, text="Choose type of measure: likes or comment").grid(row=0,column=0)
        self.measure_choice = StringVar()
        ttk.Radiobutton(self.frame_side_content, text="likes", variable = self.measure_choice, value='likes').grid(row=1,column=0)
        ttk.Radiobutton(self.frame_side_content, text="comment", variable = self.measure_choice, value='comment').grid(row=2,column=0)
        
        self.schema_choice_lab = ttk.Label(self.frame_header,text="Choose the schema you want to load")
        self.pol_choice_but = ttk.Button(self.frame_header,text="Start",command=lambda: self.set_schema(self.title,master))
        
        self.post_limit_entry = ttk.Entry(self.frame_side_content,width=15)
        self.post_limit_entry.grid(row=3,column=0)
        self.post_limit_entry.insert(0,'0')
        
        self.label = ttk.Label(self.frame_header, text = "Welcome to the FacebookApp")
        self.label.grid(row = 0, column = 1)
        
        self.exit_but = ttk.Button(self.frame_header, text="Exit Program", command=lambda: self._quit_master(master))
        
        self.new_but = ttk.Button(self.frame_header, text = "Make new GenPol_Model",
                   command = self.show_entities)
        self.load_but = ttk.Button(self.frame_header, text = "Load old GenPol_Model",
                   command = self.show_old_plots)
                   
        self.start_model_button = ttk.Button(self.frame_side_content, text="Make Scatter", command=self.draw_scatter)
        self.start_special_button = ttk.Button(self.frame_side_content, text="Make Special Scatter", command=self.draw_both_scatter)
        
        self.entity_set = {}
        self.entity_choices = []
        self.ent_buttonset=[]
        self.export_entities = {}
        
        self.schema_choice()
        
        self.temp_fig_list = []
        self.temp_af_list = []
        
        self.vscrollbar = ttk.Scrollbar(self.frame_content2, orient=VERTICAL)
        self.scroll_canvas = Canvas(self.frame_content2, bd=0, highlightthickness=0, width=800,
                        yscrollcommand=self.vscrollbar.set)
        self.vscrollbar.config(command=self.scroll_canvas.yview)
        
    class InteractivePlot:
        
            def __init__(self,scatter):
            
                self.af_list = scatter[1]
                self.fig = scatter[0]
                self.entities = scatter[2]
                self.measure = scatter[3]
                
            def get_af(self):
                return self.af_list
            
            def get_fig(self):
                return self.fig
            
    def schema_choice(self):
        
        self.schema_choice_lab.grid(row=1,column=1)
        self.pol_choice_but.grid(row=2,column=1)
        self.exit_but.grid(row=7,column=1)
        
    def show_main_menu(self,master):
        
        self.schema_choice_lab.grid_forget()
        self.pol_choice_but.grid_forget()
        self.new_but.grid(row=0,column=1)
        self.load_but.grid(row=1,column=1)
    
    def set_schema(self,schema,master):
        
        self.title = schema
        self.show_main_menu(master)
    
    def increase_pbar(self):
        
        self.pbar.step(1)
        self.pbar.update()
    
    def get_entities(self):
        
        self.cur.execute("select PA.page_name, PA.web_name from {0}page_info PA, {0}post_info P, {0}comment_info C where PA.web_name = P.web_name and P.id = C.post_id group by PA.page_name order by count(C.id) desc limit 70".format(self.title))

        tempset={}
        for row in self.cur.fetchall():
            tempset[str(row[0])]=str(row[1])
        
        self.entity_set = collections.OrderedDict(sorted(tempset.items()))
        return self.entity_set
    
    def add_entity_choice(self,index):
        self.entity_choices.append(self.export_entities[index])
        
        print (self.export_entities[index])
        if len(self.entity_choices)==5:
            for b in self.ent_buttonset:
                b.config(state="disabled")
        
        self.ent_buttonset[index].config(state="disabled")
        
    
    def show_entities(self):
        self.frame_content2.pack_forget()
        self.pbar.grid(row=6,column=0)
        self.entity_set = {}
        self.entity_choices = []
        self.ent_buttonset=[]
        self.export_entities = {}
        self.frame_content.pack()
        self.label.config(text = 'Here is the list of entities: ')
        entities = self.get_entities()
        row_count=0
        col_count=0
        index_count=0
        for k,v in entities.items():
            self.export_entities[index_count]=v
            row_count+=1
            temp_butt=ttk.Button(self.frame_content, text=k, command = lambda index=index_count: self.add_entity_choice(index))
            temp_butt.grid(row=row_count,column=col_count)
            self.ent_buttonset.append(temp_butt)
            if row_count > 18:
                col_count+=1
                row_count = 0
            index_count+=1
        self.frame_side_content.grid(row=0,column=10,rowspan=10)
        #self.frame_midbottom.pack()
        self.start_model_button.grid(row = 4,column=0)
        self.start_special_button.grid(row=5,column=0)
        
        
    def load_old_plots(self):
        
        int_plots = pickle.load( open( self.path_+"/analytics/batch/"+"save.p", "rb" ) )
            
        return int_plots
        
    def draw_scatter(self):
        
        temp_int = int(self.post_limit_entry.get())
        self.pbar.config(maximum = temp_int*len(self.entity_choices))
        self.pbar.update()
        scatter = self.draw_main_scatter(self.title,self.entity_choices,self.measure_choice.get(),self.post_limit_entry.get(),self.connection)
        p = self.InteractivePlot(scatter)
        self.pbar.config(value=0.0)
        self.pbar.pack_forget()
        self.show_plot(p.get_fig(),p.get_af())
        
        savebutton = ttk.Button(master=self.frame_model, text="Save Plot", command=lambda:self.save_plot(p))
        savebutton.pack()
        
    def draw_both_scatter(self):
        temp_int = int(self.post_limit_entry.get())
        self.pbar.config(maximum = temp_int*len(self.entity_choices))
        self.pbar.update()
        scatter = self.draw_special_scatter(self.title,self.entity_choices,self.measure_choice.get(),self.post_limit_entry.get(), self.connection)
        p = self.InteractivePlot(scatter)
        self.pbar.config(value=0.0)
        self.pbar.pack_forget()
        self.show_plot(p.get_fig(),p.get_af())
        
        savebutton = ttk.Button(master=self.frame_model, text="Save Plot", command=lambda:self.save_plot(p))
        savebutton.pack()
        
        
    def _quit_master(self,master):
        master.quit()
        master.destroy()
        
    def show_old_plots(self):
        
        
        self.frame_content.pack_forget()
        self.frame_content2.pack(expand=True)
        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        self.vscrollbar.pack(fill=Y, side="right", expand=False)
        self.scroll_canvas.xview_moveto(0)
        self.scroll_canvas.yview_moveto(0)
        self.scroll_frame = ttk.Frame(self.scroll_canvas)
        self.scroll_frame.bind("<Configure>", self.onFrameConfigure)
        self.interior = self.scroll_canvas.create_window(0, 0, window=self.scroll_frame,anchor=NW)
        ttk.Label(self.scroll_frame, text="List of previous plots: ").pack(side="top")
        index_count = 0
        for i in self.interactive_plot_list:
            self.temp_fig_list.append(i.get_fig())
            self.temp_af_list.append(i.get_af())
            temp_button = ttk.Button(self.scroll_frame,text=(str(i.entities)+" : "+str(i.measure)), command=lambda index=index_count: self.show_plot(self.temp_fig_list[index],self.temp_af_list[index]))
            temp_button.pack(expand=True)
            print (index_count)
            index_count +=1
    
    def onFrameConfigure(self, event):

        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
    
        
    def save_plot(self,int_plot):
        
        self.interactive_plot_list.append(int_plot)
        
        
        pickle.dump(self.interactive_plot_list, open( self.path_+"/analytics/batch/"+"save.p", "wb" ))
        
        def get_af(self):
            return self.af_list
        
        def get_fig(self):
            return self.fig
    
    def print_data(self,f):
       
        ax = f.get_axes()
        coll = ax[0].collections
        comments_pol = []
        likes_pol = []
        comments_gen = []
        likes_gen = []
        names = {}
        measure = 1
        name = 0
        for r in range(len(coll)):
            if measure == 2:
                for c in coll[r].get_offsets():
                    comments_pol.append(c[1])
                    comments_gen.append(c[0])
                print (np.corrcoef(np.array(comments_gen), np.array(comments_pol)))
                measure = 0
                names[ax[0].get_legend().get_texts()[name].get_text().encode("utf-8").decode("latin1")]=[float(sum(likes_pol))/float(len(likes_pol)),float(sum(likes_gen))/float(len(likes_gen)),float(sum(comments_pol))/float(len(comments_pol)),float(sum(comments_gen))/float(len(comments_gen))]
                comments_pol = []
                likes_pol = []
                comments_gen = []
                name += 1
                likes_gen = []
            else:
                for c in coll[r].get_offsets():
                    likes_pol.append(c[1])
                    likes_gen.append(c[0])
        
            measure += 1
    
        print (" " + "\t" + "post_likes_political" + "\t" + "post_likes_gender" +"\t" + "comments_political" +"\t" + "comments_gender")
        for k,v in names.items():
            print (k.encode("latin1").decode("utf-8") + "\t" + str(v[0]) + "\t" + str(v[1]) + "\t" + str(v[2]) + "\t" + str(v[3]))
            
            
                 
    
    def show_plot(self,f,afl):
        print (afl)
        self.frame_content.pack_forget()
        self.frame_content2.pack_forget()
        self.frame_midbottom.pack_forget()
        self.frame_header.pack_forget()
        self.frame_model.pack()
        self.canvas = FigureCanvasTkAgg(f, master=self.frame_model)
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        
        toolbar = NavigationToolbar2TkAgg( self.canvas, self.frame_model )
        toolbar.update()
        self.canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
        
        for a in afl:
            f.canvas.mpl_connect('button_press_event',a)
        self.print_data(f)
        self.canvas.show()
        
        def _quit_model():
                self.frame_model.pack_forget()
                for widget in self.frame_model.winfo_children():
                    widget.destroy()
                for widget in self.frame_content2.winfo_children():
                    widget.pack_forget()
                self.frame_header.pack()
            
        button = ttk.Button(master=self.frame_model, text='Quit', command=_quit_model)
        button.pack()
        
    
 
    class pol_post:
        
        def __init__(self, connection, schema, entity,type_ ,post_id):
            
            self._by_ids = []
            self._time_created = {}
            self._total_by_ids = 0.0
            self._total_count = {}
            
            self._bid_like_threshold = 0
            self._total_bids_parsed = 0
            self._empty_set = {}
            self._gender_set = {'m':0.1,'f':0.1}
            self._post_id = post_id
            
    
            self._cur = connection.cursor()
            """self._cur.execute("set names 'latin1'")
            self._cur.execute("select distinct party from political_entities")
            for row in self._cur.fetchall():
                self._total_count[str(row[0])]=0.0
            self._empty_set = self._total_count"""
            
            #self._cur.execute("select PA.name from {0}page_info PA where PA.web_name = '{1}'".format(schema,entity))
            #for row in self._cur.fetchall():
                #print str(row[0])
            if type_ == 'likes':
                self._cur.execute("select C.post_like_by_id, C.post_like_by_name from {0}post_info P, {0}{2}_info C where P.id = {1} and C.post_id = P.id limit 341324234".format(schema,self._post_id,type_))
            elif type_ == 'comment':
                self._cur.execute("select C.comment_made_by_id, C.comment_made_by_name from {0}post_info P, {0}{2}_info C where P.id = {1} and C.post_id = P.id union select R.reply_made_by_id, R.reply_made_by_name from {0}post_info P, {0}{2}_info C, {0}replies_info R where P.id = {1} and C.post_id = P.id and C.comment_id = R.comment_id limit 341324234".format(schema,self._post_id,type_))
            templist3 = self._cur.fetchall()
            self._total_bids_parsed = len(templist3)
            for row in templist3:
                self._by_ids.append(str(row[0]))
                
                #self._time_created[datetime.datetime.strptime(str(row[1]),'%Y-%m-%d %H:%M:%S')] = str(row[0])
                """bid_like_count = 0
                if self._bid_like_threshold != 0:
                    self._cur.execute("select sum(X.CP) from (select PE.party, count(P.id) as CP from DK_POLITICS_post_info P, political_entities PE where PE.web_name = P.web_name and P.id in (select post_id from DK_POLITICS_likes_info  where by_id = '{0}') group by PE.party) as X".format(str(row[0])))
                    for row_c in self._cur.fetchone():
                        try:
                            bid_like_count = int(row_c)
                        except:
                            bid_like_count = 0
                
                templist = []
                if bid_like_count >= self._bid_like_threshold:
                
                    self._cur.execute("select PE.party, count(P.id) from DK_POLITICS_post_info P, political_entities PE where PE.web_name = P.web_name and P.id in (select post_id from DK_POLITICS_likes_info  where by_id = '{0}') group by PE.party".format(str(row[0])))
    
                    total_likes = float(0.0)
                    for r in self._cur.fetchall():
                        templist.append({str(r[0]):float(r[1])})
                        total_likes = float(r[1]) + total_likes
                        
                templist2 = []
                for r in templist:
                    for k,v in r.iteritems():
                        
                        if total_likes < 4:
                            pass
                        else:
                            templist2.append({k:float(v/total_likes)})
                            self._total_count[k]+=float((v/total_likes))
                
                
                self._by_ids[str(row[0])] = templist2"""
                
                self._cur.execute("select gender from gender where by_id = '{0}'".format(str(row[0])))
                for row in self._cur.fetchall():
                    if str(row[0]) == 'u':
                        pass
                    else:
                        self._gender_set[str(row[0])]+=1
                    
        def get_gen_post(self):
            
            return self._gender_set
                
        def get_post_byids(self):
            
            return self._by_ids
        
        def get_total_bids(self):
            
            return self._total_bids_parsed
        
        def get_agg_gen_post(self):
            
            total_gender = self._gender_set['f']+self._gender_set['m']
            agg_gen = {'m':self._gender_set['m']/total_gender*100,'f':self._gender_set['f']/total_gender*100}
            
            
            return agg_gen
            
        def get_agg_post(self):
            
            return_set = {}
            
            hu = 0.1
            zup = 0
            for k,v in self._total_count.items():
                hu += v
            for k,v in self._total_count.items():
        
                #print str(k) + " : " + str(v/float(hu)*100)
                return_set[str(k)]=v/float(hu)*100
                zup += (v/float(hu)*100)
            #print str(hu-0.1) +" out of " + str(self._total_bids_parsed)
            
            return return_set
        
        
        def print_total_count(self):
            
            hu = 0.1
            zup = 0
            for k,v in self._total_count.items():
                hu += v
            for k,v in self._total_count.items():
        
                print (str(k) + " : " + str(v/float(hu)*100))
            
                zup += (v/float(hu)*100)
            print (str(hu-0.1) +" out of " + str(self._total_bids_parsed))

        
    def create_agg_post_plot(self,post_list,color,entity,special,conn):
        
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
            
        def get_pol_from_by_id(by_id,pol_by_id, conn):
    
            connection = conn
            cur = connection.cursor()
            bid_like_count = 0
            
            tempset = {}
            if bid_like_count >= 0:
            
                cur.execute("select PE.party, count(P.id) from {0}post_info P, political_entities PE where PE.web_name = P.web_name and P.id in (select post_id from {0}likes_info  where post_like_by_id = '{1}') group by PE.party".format(self.title,str(by_id)))
            
                total_likes = float(0.0)
                for r in cur.fetchall():
                    tempset[str(r[0])]=float(r[1])
                    total_likes = float(r[1]) + total_likes
                
                if total_likes < 4:
                    pass
                    return {}
                else:
                    for k,v in tempset.items():
                        pol_by_id[k]+=float((v/total_likes))
                    
                    return pol_by_id
                
        def create_empty_pol_set(conn):
            
            connection = conn
            total_count = {}
            cur = connection.cursor()
            
            cur.execute("select distinct party from political_entities")
            for row in cur.fetchall():
                total_count[str(row[0])]=0.0
            empty_set = total_count
            
            return empty_set
        
        def define_annotes(x_list,y_list,m_list,reverse,id_list):
            
            insert_dif = ("INSERT INTO post_comment_like_dif "
                       "(dif, fb_post_id)"
                       "VALUES (%s, %s)")
            
            #self.cur.execute("CREATE  TABLE IF NOT EXISTS `Facebook`.`post_comment_like_dif` (`dif` INT, `fb_post_id` VARCHAR(300), `id` BIGINT NOT NULL AUTO_INCREMENT, PRIMARY KEY (`id`) );")

            an_list = []
            new_x_list = []
            new_y_list = []
            dif_list = {}
            dif = 0
            dif_count = 0
            for i in range(len(m_list)):
                if self.special_parsed[i][1] > y_list[i]:
                    dif = self.special_parsed[i][1] - y_list[i]
                else:
                    dif = y_list[i] - self.special_parsed[i][1]
                dif_list[i]=dif
                #if id_list[i] not in self.post_dif_list:
                    #self.cur.execute(insert_dif,[dif,id_list[i]])
            #self.connection.commit()
            
            for w,s in sorted(dif_list.items(), key=lambda x: x[1], reverse=reverse):
                new_x_list.append(x_list[w])
                new_x_list.append(self.special_parsed[w][0])
                new_y_list.append(y_list[w])
                new_y_list.append(self.special_parsed[w][1])
                an_list.append(dif_count)
                an_list.append(dif_count)
                dif_count += 1
                if dif_count > 10:
                    break
            
            self.special_parsed = {}
            return [new_x_list,new_y_list,an_list]
        
        x_list = []
        y_list = []
        s_list = []
        cm_list = []
        rgb = matplotlib.colors.colorConverter
        
        if special == 0:
            color_list = ['red','green','blue','yellow','black']
        else:
            color_list = [rgb.to_rgba('#FF0000'),rgb.to_rgba('#FFA1A1'),rgb.to_rgba('#4C9900'),rgb.to_rgba('#A1FFA1'),rgb.to_rgba('#0000FF'),rgb.to_rgba('#A4A4FF'),rgb.to_rgba('#FFFF00'),rgb.to_rgba('#FFFFA5'),rgb.to_rgba('#000000'),rgb.to_rgba('#8A8A8A')]
        annotes = []
        
        empty_set = create_empty_pol_set(conn)
        
        for p in post_list[0]:
            parsed = 0
            total_pol = 0
            not_pol = 0
            ry = 0
            for byid in p:
                ry = 0
                if byid in self._by_id_already_parsed:
                    parsed += 1
                   
                    ry = assign_wing(self._by_id_already_parsed[byid],'r')
                else:
                    
                    not_pol += 1
                
                total_pol = total_pol + ry
            if parsed != 0:
                print ("percentage of users with political data: " + str((float(parsed)/float(parsed+not_pol))*100))
            else:
                print (0)
            if parsed == 0:
                y_list.append(0)
            else:
                y_list.append((float(total_pol)/float(parsed))*100)
            
        print (len(post_list[0]))
            #cm_list.append({'red':((rb['r'])),'green':((0.0)),'blue':((100-rb['r']))})
        for p in post_list[3]:
            annotes.append(p)
        
        for p in post_list[1]:
            x_list.append(p['f'])
            
        for p in post_list[2]:
            s_list.append(p)
        
        plt.scatter(x_list,y_list,s=s_list,c=color_list[color])
       
        if special != 0:
            if special == 1:   
                for i in range(len(post_list[3])):
                    self.special_parsed[i] = [x_list[i],y_list[i]]
            if special == 2:
                special_annotes = define_annotes(x_list, y_list, post_list[3],True,post_list[5])
                print (special_annotes)
                for x,y,a in zip(special_annotes[0],special_annotes[1],special_annotes[2]):
                    plt.annotate(a,xy=(x,y))
        af =  AnnoteFinder(x_list,y_list, annotes, xtol=1, ytol=1)
        plt.xlim([0,100])
        plt.ylim([0,100])
        
        return af

    def create_post_list(self,connection,schema,entity,type_,limit,e_run):
        
   
        cur = connection.cursor()
        templist = []
        return_list = []
        return_gen_list = []
        return_total_bid_list = []
        message_list = []
        id_list = []
        name_of_ent = ""

        if type_ == 'both':
            cur.execute("select P.id, P.post_message, P.post_headline, P.post_description, p.post_time_created, P.post_link, PA.page_name, P.fb_post_id from {0}page_info PA, {0}comment_info C, (select * from {0}post_info where web_name = '{1}') as P where P.id = C.post_id and P.web_name = PA.web_name group by P.id having count(C.id) > 19 limit {2}".format(schema,entity,limit))
            #cur.execute("select P.id, P.message, P.name, P.description, p.time_created, P.link, PA.name, P.fb_post_id from {0}page_info PA, {0}post_info P, {0}comment_info C where P.id = C.post_id and P.web_name = '{1}' and P.web_name = PA.web_name group by P.id having count(C.id) > 29 order by RANDOM() desc limit {2}".format(schema,entity,limit))
        else:
            cur.execute("select P.id, P.post_message, P.post_headline, P.post_description, p.post_time_created, P.post_link, PA.page_name, P.fb_post_id from {0}page_info PA, {0}post_info P, {0}{2}_info C where P.web_name = '{1}' and P.id = C.post_id and P.web_name = PA.web_name group by P.id having count(C.id) > 19 limit {3}".format(schema,entity,type_,limit))
        for row in cur.fetchall():
            templist.append(str(row[0]))
            message_list.append(["Post Message  :  "+str(row[1])+"\n\n","Headline  :  "+str(row[2])+"\n\n","Sub Headline  :  "+str(row[3])+"\n\n","Date and Time  :  "+str(row[4])+"\n\n","Link  :  "+str(row[5])+"\n\n", "Posted On  :  "+str(row[6])])
            name_of_ent = (row[6])
            id_list.append(str(row[7]))
        
        if type_ == 'both':
            
            master_return_list = []
            for t in ['likes','comment']:
                post_counter = 0*e_run
                return_list = []
                return_gen_list = []
                return_total_bid_list = []
                for p in templist:
                    post_counter+=1
                    
                    post = self.pol_post(connection,schema,entity,t,p)
                    return_list.append(post.get_post_byids())
                    return_gen_list.append(post.get_agg_gen_post())
                    if post.get_total_bids() > 500:
                        temp_total_bids = ((post.get_total_bids()-500)*0.45)+500
                        return_total_bid_list.append(temp_total_bids)
                    else:
                        return_total_bid_list.append(post.get_total_bids())
                    self.increase_pbar()
                master_return_list.append([return_list,return_gen_list,return_total_bid_list,message_list,name_of_ent,id_list])
                
            return master_return_list
        
        else:
            
            post_counter = 0*e_run
            for p in templist:
                
                post_counter+=1
                if p not in self.post_already_parsed:
                    post = self.pol_post(connection,schema,entity,type_,p)
                    self.post_already_parsed[p]=post
                else:
                    post = self.post_already_parsed[p]
                return_list.append(post.get_post_byids())
                return_gen_list.append(post.get_agg_gen_post())
                if post.get_total_bids() > 500:
                    temp_total_bids = ((post.get_total_bids()-500)*0.45)+500
                    return_total_bid_list.append(temp_total_bids)
                else:
                    return_total_bid_list.append(post.get_total_bids())
                self.increase_pbar()
                
            return [return_list,return_gen_list,return_total_bid_list,message_list,name_of_ent,id_list]
      
    def draw_main_scatter(self,schema_,ent_list,t,n, conn):
        connection = conn
        schema = schema_
        type_ = t
        entity_list = ent_list
        
        fig = plt.figure(figsize=(17,8))
        e_run = 0
        af_list = []
        name_list = []
        for e in entity_list:
            post_list = self.create_post_list(connection, schema, e, type_,n,e_run)
            af = self.create_agg_post_plot(post_list,e_run,e,False,conn)
            fig.canvas.mpl_connect('button_press_event', af)
            e_run+=1
            af_list.append(af)
            name_list.append(post_list[4])
        
        patch_list = []
        if len(entity_list) > 0:
            red_patch = mpatches.Patch(color='red', label=name_list[0])
            patch_list.append(red_patch)
        if len(entity_list) > 1:
            green_patch = mpatches.Patch(color='green', label=name_list[1])
            patch_list.append(green_patch)
        if len(entity_list) > 2:
            blue_patch = mpatches.Patch(color='blue', label=name_list[2])
            patch_list.append(blue_patch)
        if len(entity_list) > 3:
            yellow_patch = mpatches.Patch(color='yellow', label=name_list[3])
            patch_list.append(yellow_patch)
        if len(entity_list) > 4:
            black_patch = mpatches.Patch(color='black', label=name_list[4])
            patch_list.append(black_patch)
        plt.legend(
                   handles=patch_list,
                   scatterpoints=1,
                   markerscale=0.5,
                   loc='lower left',
                   ncol=3,
                   fontsize=8)
        plt.ylabel("blue coalitiion vs. red coalition")
        plt.xlabel("men vs. women")
        fig.suptitle("gender_pol scatter with measure: "+type_,fontsize=15)
        
        return [fig,af_list,entity_list,type_]
        #plt.show()
    
    def draw_special_scatter(self,schema_,ent_list,t,n, conn):
        connection = conn
        schema = schema_
        type_ = "both"
        entity_list = ent_list
        
        fig = plt.figure(figsize=(17,8))
        e_run = 0
        af_list = []
        name_list = []
        for e in entity_list:
            post_list = self.create_post_list(connection, schema, e, type_,n,e_run)
            t_run = 1
            for po in post_list:
                af = self.create_agg_post_plot(po,e_run,e,t_run,conn)
                fig.canvas.mpl_connect('button_press_event', af)
                af_list.append(af)
                e_run+=1
                t_run += 1
            name_list.append(post_list[0][4])
        
        patch_list = []
        if len(entity_list) > 0:
            red_patch = mpatches.Patch(color='red', label=name_list[0])
            patch_list.append(red_patch)
        if len(entity_list) > 1:
            green_patch = mpatches.Patch(color='green', label=name_list[1])
            patch_list.append(green_patch)
        if len(entity_list) > 2:
            blue_patch = mpatches.Patch(color='blue', label=name_list[2])
            patch_list.append(blue_patch)
        if len(entity_list) > 3:
            yellow_patch = mpatches.Patch(color='yellow', label=name_list[3])
            patch_list.append(yellow_patch)
        if len(entity_list) > 4:
            black_patch = mpatches.Patch(color='black', label=name_list[4])
            patch_list.append(black_patch)
        plt.legend(
                   handles=patch_list,
                   scatterpoints=1,
                   markerscale=0.5,
                   loc='lower left',
                   ncol=3,
                   fontsize=8)
        plt.ylabel("blue coalitiion vs. red coalition")
        plt.xlabel("men vs. women")
        fig.suptitle("gender_pol scatter with measure: "+type_,fontsize=15)
        
        return [fig,af_list,entity_list,type_]

        
def main_gender_pol(path_, conn, db):            
    
    root = Tk()
    app = FacebookApp(root, path_, conn, db)
    root.mainloop()
    