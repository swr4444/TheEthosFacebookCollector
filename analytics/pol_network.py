# -*- coding: utf-8 -*-
import networkx.generators.small
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import time
import networkx as nx
import pickle
from operator import itemgetter
from networkx.drawing.nx_agraph import to_agraph
import sqlite3
import os

def create_empty_pol_set(connection):
    
    total_count = {}
    cur = connection.cursor()
    
    cur.execute("select distinct party from political_entities")
    for row in cur.fetchall():
        total_count[str(row[0])]=0.0
    empty_set = total_count
    
    return empty_set

def trim_degrees(g, w_nodes, w_edges, degree=1):
    deleted_nodes = {}
    g2=g.copy()
    d=nx.degree(g2)
    new_w_edges = []
    #print d
    for n in g2.nodes():
        if d[n] < degree:
            deleted_nodes[n]=True
            g2.remove_node(n)
            del w_nodes[n]
    
    for e in g2.edges():
        if e[0] in deleted_nodes:
            g2.remove_edge(e[0],e[1])
        elif e[1] in deleted_nodes:
            g2.remove_edge(e[0],e[1])
        else:
            pass
    
    for e in w_edges:
        if e[0] in deleted_nodes:
            pass
        elif e[1] in deleted_nodes:
            pass
        else:
            new_w_edges.append(e)
    
    return [g2,w_nodes,new_w_edges]
    


def aggregate_likers(node_list,connection, byid_already_parsed):
    
    liker_list = []
    no_find = 0
    no_data = 0
    
    for n in node_list:
        try:
            liker_list.append(byid_already_parsed[str(n)])
        except:
            print ("no find")
            no_find += 1
    
    no_data = 0
    rb = {}
    
    cur = connection.cursor()

    cur.execute("select distinct party from political_entities")
    for row in cur.fetchall():
        rb[str(row[0])]=0.0
        
    for p in liker_list:
        if not p:
            no_data+=1
    
    for p in liker_list:
        if not p:
            pass
        else:
            try:
                rb['O']+=(p['O']/(len(liker_list)-no_data))
                rb['V']+=(p['V']/(len(liker_list)-no_data))
                rb['C']+=(p['C']/(len(liker_list)-no_data))
                rb['I']+=(p['I']/(len(liker_list)-no_data))
                rb['OE']+=(p['OE']/(len(liker_list)-no_data))
                rb['A']+=(p['A']/(len(liker_list)-no_data))
                rb['B']+=(p['B']/(len(liker_list)-no_data))
                rb['F']+=(p['F']/(len(liker_list)-no_data))
                rb['AA']+=(p['AA']/(len(liker_list)-no_data))
                rb['N']+=(p['N']/(len(liker_list)-no_data))
            except:
                print ("data fail")
    
    total_per = 0
    for k,v in rb.iteritems():
        print (str(k) + " : " + str(round(v*100,1))+"%")
        total_per+=v
    
    print (len(liker_list)-no_data)
    print (total_per)
        

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    if n == 0: return 0
    
    for i in range(0, len(l), int(n)):
        yield l[int(i):int(i+n)]
        
        
def user_group(title,connection,entity, s_date, e_date):
    
    cur = connection.cursor()

    
    return_list = {}
    counter = 0
    break_num = 10
    
    if not entity:
        cur.execute("select C.comment_made_by_id, count(distinct C.id)+count(distinct R.id)+count(distinct CL.id)+count(distinct RL.id) from {0}comment_info C, {0}comment_likes_info CL, {0}replies_info R, {0}reply_likes_info RL where C.comment_id = R.comment_id and C.comment_id = CL.comment_id and R.reply_id = RL.reply_id and date(C.comment_time_created) between '{1}' and '{2}' group by C.comment_made_by_id order by count(distinct C.id)+count(distinct R.id)+count(distinct CL.id)+count(distinct RL.id) desc".format(title,s_date,e_date))
        for row in cur.fetchall():
            return_list[str(row[0])]=[0,0,0]
            counter += 1
            if counter > break_num:
                break
    else:
        break_num = 49/len(entity)
        for e in entity:
            counter = 0
            #cur.execute("select C.by_id, count(distinct C.id)+count(distinct R.id)+count(distinct CL.id)+count(distinct RL.id) from {0}comment_info C, {0}comment_likes_info CL, {0}replies_info R, {0}reply_likes_info RL, {0}post_info P where P.id = C.post_id and P.web_name = '{3}' and C.comment_id = R.comment_id and C.comment_id = CL.comment_id and R.reply_id = RL.reply_id and date(C.time_created) between '{1}' and '{2}' group by by_id order by count(distinct C.id)+count(distinct R.id)+count(distinct CL.id)+count(distinct RL.id) desc".format(title,s_date,e_date,e))
            cur.execute("select C.comment_made_by_id, count(distinct C.id)+count(distinct R.id)+count(distinct CL.id) from {0}comment_info C, {0}comment_likes_info CL, {0}replies_info R, {0}post_info P where P.id = C.post_id and P.web_name = '{3}' and C.comment_id = R.comment_id and C.comment_id = CL.comment_id and date(C.comment_time_created) between '{1}' and '{2}' group by C.comment_made_by_id order by count(distinct C.id)+count(distinct R.id)+count(distinct CL.id) desc".format(title,s_date,e_date,e))
            #cur.execute("select C.by_id, count(distinct C.id)+count(distinct R.id) from {0}comment_info C,  {0}replies_info R, {0}post_info P where P.id = C.post_id and P.web_name = '{3}' and C.comment_id = R.comment_id and date(C.time_created) between '{1}' and '{2}' group by C.by_id order by count(distinct C.id)+count(distinct R.id) desc".format(title,s_date,e_date,e))

            for row in cur.fetchall():
                return_list[str(row[0])]=[0,0,0]
                counter += 1
                if counter > break_num:
                    break
    
    return return_list

def assign_wing_text(pol_by_id):
    
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
    
    if rb['r'] > rb['b']:
        return "red"
    elif rb['r'] < rb['b']:
        return "blue"
    else:
        return "black"
    
def get_politicians(connection,title,network_type):
    
    politicians_list = {}
    cur = connection.cursor()

    if network_type == "other":
        cur.execute("select PA.page_id ,PA.page_name from {0}page_info PA".format(title))
        for row in cur.fetchall():
            politicians_list[str(row[0])]=[str(row[1])]
    else:
        #cur.execute("select PA.fb_id, PA.name, PE.party from DK_POLITICS_page_info PA, political_entities PE where PE.web_name = PA.web_name")
        cur.execute("select PA.page_id ,PA.page_name, PE.party, count(C.id) from {0}comment_tags_info C, {0}page_info PA, political_entities PE where PE.web_name = PA.web_name and C.tagged_id = PA.page_id group by PA.page_name order by count(C.id) desc limit 100".format(title))
        for row in cur.fetchall():
            politicians_list[str(row[0])]=[str(row[1]),str(row[2]),int(row[3])]
    
    return politicians_list

    
def extract_data(title,connection,type_,limit,entity, s_date, e_date):

    cur = connection.cursor()
    if type_ == 'tags':
        if not entity:
            return_list = []
            cur.execute("select C.comment_made_by_id, CT.tagged_id from {0}comment_info C, {0}comment_tags_info CT where CT.comment_id = C.comment_id and date(C.comment_time_created) between '{2}' and '{3}' order by random() limit {1}".format(title,limit,s_date, e_date))
            return_list = list(cur.fetchall())
            cur.execute("select R.reply_made_by_id, RT.tagged_id from {0}comment_info C, {0}reply_tags_info RT, {0}replies_info R where R.comment_id = C.comment_id and RT.reply_id = R.reply_id and date(R.reply_time_created) between '{2}' and '{3}' order by random() limit {1}".format(title,limit,s_date, e_date))
            return_list.extend(cur.fetchall())
        else:
            for e in entity:
                return_list = []
                cur.execute("select C.comment_made_by_id, CT.tagged_id from {0}comment_info C, {0}comment_tags_info CT, {0}post_info P where P.id = C.post_id and CT.comment_id = C.comment_id and P.web_name = '{2}' and date(C.time_created) between '{3}' and '{4}' order by random() limit {1}".format(title,limit,e,s_date, e_date))
                return_list.extend(list(cur.fetchall()))
                cur.execute("select R.by_id, RT.tagged_id from {0}comment_info C, {0}reply_tags_info RT, {0}post_info P, {0}replies_info R where R.comment_id = C.comment_id and P.id = C.post_id and RT.reply_id = R.reply_id and P.web_name = '{2}' and date(R.time_created) between '{3}' and '{4}' order by random() limit {1}".format(title,limit,e,s_date, e_date))
                return_list.extend(list(cur.fetchall()))
        
        return return_list
    
    if type_ == 'likes':
        if not entity:
            return_list = []
            cur.execute("select C.comment_made_by_id, CL.comment_like_by_id from {0}comment_info C, {0}comment_likes_info CL, {0}post_info P where P.id = C.post_id and CL.comment_id = C.comment_id and date(C.comment_time_created) between '{2}' and '{3}' order by random() limit {1}".format(title,limit,s_date, e_date))
            return_list.extend(list(cur.fetchall()))
            cur.execute("select R.reply_made_by_id, RL.reply_like_by_id from {0}comment_info C, {0}reply_likes_info RL, {0}post_info P, {0}replies_info R where R.comment_id = C.comment_id and P.id = C.post_id and RL.reply_id = R.reply_id and date(R.reply_time_created) between '{2}' and '{3}' order by random() limit {1}".format(title,limit,s_date, e_date))
            return_list.extend(list(cur.fetchall()))
        else:
            return_list = []
            for e in entity:
                cur.execute("select C.comment_made_by_id, CL.comment_like_by_id from {0}comment_info C, {0}comment_likes_info CL, {0}post_info P where P.id = C.post_id and CL.comment_id = C.comment_id and P.web_name = '{2}' and date(C.comment_time_created) between '{3}' and '{4}' order by random() limit {1}".format(title,limit,e,s_date, e_date))
                return_list.extend(list(cur.fetchall()))
                cur.execute("select R.reply_made_by_id, RL.reply_like_by_id from {0}comment_info C, {0}reply_likes_info RL, {0}post_info P, {0}replies_info R where R.comment_id = C.comment_id and P.id = C.post_id and RL.reply_id = R.reply_id and P.web_name = '{2}' and date(R.reply_time_created) between '{3}' and '{4}' order by random() limit {1}".format(title,limit,e,s_date, e_date))
                return_list.extend(list(cur.fetchall()))
            
        return return_list
        
        
    if type_ == 'replies':
        if not entity:
            return_list = []
        
            cur.execute("select C.comment_made_by_id, R.reply_made_by_id from {0}comment_info C, {0}post_info P, {0}replies_info R where P.id = C.post_id and R.comment_id = C.comment_id and date(R.reply_time_created) between '{2}' and '{3}' order by random() limit {1}".format(title,limit,s_date, e_date))
            return_list.extend(list(cur.fetchall()))
            
        else:
            return_list = []
            for e in entity:
                cur.execute("select C.comment_made_by_id, R.by_id from {0}comment_info C, {0}post_info P, {0}replies_info R where P.id = C.post_id and R.comment_id = C.comment_id and P.web_name = '{2}' and date(R.reply_time_created) between '{3}' and '{4}' order by random() limit {1}".format(title,limit,e,s_date, e_date))
                return_list.extend(list(cur.fetchall()))
            
        return return_list
    
    
    if type_ == 'comments':
        if not entity:
            return_list = []
            cur.execute("select PA.page_id, C.comment_made_by_id from {0}comment_info C, {0}post_info P, {0}page_info PA where PA.web_name = P.web_name and P.id = C.post_id and date(C.comment_time_created) between '{2}' and '{3}' order by random() limit {1}".format(title,limit,s_date, e_date))
            return_list.extend(list(cur.fetchall()))
        else:
            return_list = []
            for e in entity:
                cur.execute("select PA.page_id, C.comment_made_by_id from {0}comment_info C, {0}post_info P, {0}page_info PA where PA.web_name = P.web_name and P.id = C.post_id and P.web_name = '{2}' and date(C.comment_time_created) between '{3}' and '{4}' order by random() limit {1}".format(title,limit,e,s_date, e_date))
                return_list.extend(list(cur.fetchall()))
            
        print (len(return_list))
        return return_list
        
#cur.execute("select C.by_id, CT.tagged_id from {0}comment_info C, {0}comment_tags_info CT where CT.comment_id = C.comment_id and C.by_id in (select C.by_id from {0}comment_info C, {0}comment_tags_info CT where CT.comment_id = C.comment_id group by C.by_id having count(CT.tagged_id) > 19) limit 1000".format(title))
#cur.execute("select C.by_id, R.by_id from {0}comment_info C, {0}replies_info R where R.comment_id = C.comment_id and R.by_id in (select R.by_id from {0}replies_info R group by R.by_id having count(R.id) > 9) and C.by_id in (select R.by_id from {0}replies_info R group by R.by_id having count(R.id) > 9) order by random() limit 3000".format(title))

def fill_nodes_edges(nodes,edges,data, byid_already_parsed):
    edge_count = {}
    for row in data:
        if not str(row[0]) in nodes:
            if str(row[0]) in byid_already_parsed:
                if byid_already_parsed[str(row[0])]:
                    nodes[str(row[0])]=assign_wing_text(byid_already_parsed[str(row[0])])
        if not str(row[1]) in nodes:
            if str(row[1]) in byid_already_parsed:
                if byid_already_parsed[str(row[1])]:
                    #print (byid_already_parsed[str(row[1])])
                    nodes[str(row[1])]=assign_wing_text(byid_already_parsed[str(row[1])])
        if str(row[0]) in byid_already_parsed and str(row[1]) in byid_already_parsed:
            if byid_already_parsed[str(row[1])] and byid_already_parsed[str(row[0])]:
                edge_tuple1 = (str(row[0]),str(row[1]))
                edge_tuple2 = (str(row[1]),str(row[0]))
                if edge_tuple1 in edges:
                    edges[edge_tuple1]+=1
                elif edge_tuple2 in edges:
                    edges[edge_tuple1]=0
                    edges[edge_tuple1]+=edges[edge_tuple2]
                    del edges[edge_tuple2]
                else:
                    edges[edge_tuple1]=1
        
        if not str(row[1]) in edge_count:
            edge_count[str(row[1])]=1
        else:
            edge_count[str(row[1])]+=1
            
        if not str(row[0]) in edge_count:
            edge_count[str(row[0])]=1
        else:
            edge_count[str(row[0])]+=1
        
    print (len(nodes.keys()))
    print (len(edges.keys()))
    
    return {'nodes':nodes,'edges':edges}

def fill_nodes_edges_entity(nodes,edges,data, byid_already_parsed):
    edge_count = {}
    for row in data:
        if not str(row[0]) in nodes:
            if str(row[0]) in byid_already_parsed:
                if byid_already_parsed[str(row[0])]:
                    nodes[str(row[0])]=assign_wing_text(byid_already_parsed[str(row[0])])
        if not str(row[1]) in nodes:
            nodes[str(row[1])]="black"
        if str(row[0]) in byid_already_parsed:
            if byid_already_parsed[str(row[0])]:
                edge_tuple1 = (str(row[0]),str(row[1]))
                edge_tuple2 = (str(row[1]),str(row[0]))
                if edge_tuple1 in edges:
                    edges[edge_tuple1]+=1
                elif edge_tuple2 in edges:
                    edges[edge_tuple1]=0
                    edges[edge_tuple1]+=edges[edge_tuple2]
                    del edges[edge_tuple2]
                else:
                    edges[edge_tuple1]=1
        
        if not str(row[1]) in edge_count:
            edge_count[str(row[1])]=1
        else:
            edge_count[str(row[1])]+=1
            
        if not str(row[0]) in edge_count:
            edge_count[str(row[0])]=1
        else:
            edge_count[str(row[0])]+=1
        
    print (len(nodes.keys()))
    print (len(edges.keys()))
    
    return {'nodes':nodes,'edges':edges}


def create_edge_node_lists(edges,nodes,g,title,s_date,e_date,ent,byid_already_parsed,conn,network_type): 
    
    connection = conn

    node_list_blue = []
    node_list_red = []
    node_list_black = [] 
    node_list_green = [] 
    node_list_key_red = []
    node_list_key_blue = [] 
    node_red_label = {}
    node_blue_label = {}
    node_green_label = {}
    legende_green = {}
    legend_red = {}
    legend_blue = {}
    label_count = 0
    red_key_size = []
    blue_key_size = []
    w_nodes = {}
    w_edges = []
    not_w_edges = []
    new_w_edges = []  
    
    print (float(sum(edges.values()))/float(len(edges.values())))
    #print (float(sum(edges.values()))/float(len(edges.values())))*2223.50
    lim = 0.0
    #lim_v = round(random.uniform(lim, lim+1), 2)
    for k,v in edges.items():
        not_w_edges.append((k[0],k[1]))
        if v > lim:
            
            w_edges.append((k[0],k[1],v))
            if not k[0] in w_nodes:
                w_nodes[k[0]]=nodes[k[0]]
            if not k[1] in w_nodes:
                w_nodes[k[1]]=nodes[k[1]]
               
    """for k,v in edges.iteritems():
        w_edges.append((k[0],k[1],v))"""
    
    g.add_weighted_edges_from(w_edges)
    for k,v in w_nodes.items():
        g.add_node(k)
    
    trim=trim_degrees(g, w_nodes, w_edges, degree=0)
    g=trim[0]
    w_nodes=trim[1]
    w_edges = trim[2]
    d=nx.degree(g)
    
    print (len(w_nodes))
    print (len(w_edges))
    b = get_politicians(connection,title,network_type)
    p = user_group(title, connection, ent, s_date, e_date)
    p.update(b)
    for k,v in w_nodes.items():
        if title == "DK_POLITICS_":
            if k in p:
                if p[k][1]== "I" or p[k][1]== "V" or p[k][1]== "K" or p[k][1]== "O":
                    node_list_key_blue.append(k)
                    blue_key_size.append(p[k][2])
                    label_count +=1
                    print (str(label_count) + p[k][0])
                    node_blue_label[k]=str(label_count)
                    legend_blue[p[k][0]]=label_count
                elif p[k][1]== "A" or p[k][1]== "F" or p[k][1]== "B" or p[k][1]== "OE" or p[k][1]== "L" or p[k][1]== "N":
                    node_list_key_red.append(k)
                    red_key_size.append(p[k][2])
                    label_count +=1
                    print (str(label_count) + p[k][0])
                    node_red_label[k]=str(label_count)
                    legend_red[p[k][0]]=label_count
                else:
                    if v == 'blue':
                        node_list_key_blue.append(k)
                        blue_key_size.append(0)
                    elif v == 'red':
                        node_list_key_red.append(k)
                        red_key_size.append(0)
                    else:
                        pass
                    
                print (p[k])
            elif v == 'blue':
                node_list_blue.append(k)
            elif v == 'red':
                node_list_red.append(k)
            else:
                node_list_black.append(k)
        else:
            if k in p:
                if v == 'blue':
                    node_list_key_blue.append(k)
                    blue_key_size.append(0)
                elif v == 'red':
                    node_list_key_red.append(k)
                    red_key_size.append(0)
                else:
                    pass
            if k in b:
                node_list_green.append(k)
                print (k)
                label_count +=1
                print (str(label_count) + b[k][0])
                node_green_label[k]=str(label_count)
                legende_green[b[k][0]]=label_count
            elif v == 'blue':
                node_list_blue.append(k)
            elif v == 'red':
                node_list_red.append(k)
            else:
                node_list_black.append(k)
            
    return {'nodes':[node_list_blue,node_list_red,node_list_black,node_list_key_red,node_list_key_blue,node_list_green],'edges':w_edges,'sizes':(red_key_size,blue_key_size),"labels":[node_red_label,node_blue_label,node_green_label],"legends":[legende_green,legend_red,legend_blue]}


def draw_undi_graph(conn,db,path_,data_types,start_date,end_date):
    connection = conn
    cur = connection.cursor()
    title = db.replace(".txt","")
    nodes = {}
    edges = {}
    entity = []
    network_type = "other"
    #entity = ['dagbladetinformation','politiken']
    #entity = ["politiken","dagbladetinformation","denkorteavis",'borsen.dk']
    #entity = ["politiken","dagbladetinformation","denkorteavis",'borsen.dk',"kristeligt","berlingske","jyllandsposten",'DRNyheder',"tv2news","Altingetdk","ekstrabladet","metroxpress",'ditbt',"dagens.dk","seoghoerdk","tv2nyhederne"]
    #entity = ["Altingetdk"]
    #entity = ["kristeligt","berlingske","jyllandsposten",'DRNyheder',"tv2news"]
    #entity = ["ekstrabladet","metroxpress",'ditbt',"dagens.dk","seoghoerdk"]
    #entity = ["sfparti","radikalevenstre","LiberalAlliance",'enhedslisten',"danskfolkeparti"]
    #entity = ["venstre.dk"]
    #entity = ["astrid.krag","mikkelsen.brian","ida.auken","maimercado.dk"]
    #entity = ["47520761764","zeniastampe","IngerStojberg","33510214383"]
    #entity = ["47520761764","zeniastampe","IngerStojberg","33510214383","astrid.krag","mikkelsen.brian","ida.auken","maimercado.dk","sfparti","radikalevenstre","LiberalAlliance",'enhedslisten',"danskfolkeparti","hellethorningschmidt","larsloekke","mettefrederiksen.dk","kristianjensen.venstre","AndersSamuelsenLA","politiker.pia.olsen.dyhr","johanneschmidt",'531761723507375',"oestergaard","socialdemokraterne","venstre.dk"]


    #try:
    byid_already_parsed = pickle.load( open( path_+"/analytics/batch/" +"pol_by_id.p", "rb" ) )
    #except:
    #byid_already_parsed = {}
    
    empty_set = create_empty_pol_set(connection)
    for k,v in get_politicians(connection,title,network_type).items():
        if k in byid_already_parsed:
            if not byid_already_parsed[k]:
                byid_already_parsed[k]=dict(empty_set)
        if k not in byid_already_parsed:
            byid_already_parsed[k]=dict(empty_set)
    #print byid_already_parsed["520449347983427"]


    limit = 1000000000
    s_date = start_date
    e_date = end_date
    key_users = False
    
    g = nx.Graph()
    

    #ne = fill_nodes_edges(nodes, edges, replies_data)
    if data_types == "comments":
        comments_data = extract_data(title, connection, 'comments', limit, entity, s_date, e_date)
        ne = fill_nodes_edges(nodes, edges, comments_data, byid_already_parsed)
        new_ne = create_edge_node_lists(ne['edges'], ne['nodes'],g,title,s_date,e_date,entity,byid_already_parsed,connection,network_type)
    else:
        likes_data = extract_data(title, connection, 'likes', limit, entity, s_date, e_date)
        tags_data = extract_data(title, connection, 'tags', limit, entity, s_date, e_date)
        replies_data = extract_data(title, connection, 'replies', limit, entity, s_date, e_date)
        comments_data = extract_data(title, connection, 'comments', limit, entity, s_date, e_date)
        ne1 = fill_nodes_edges(nodes, edges, replies_data,byid_already_parsed)
        ne2 = fill_nodes_edges(ne1['nodes'], ne1['edges'], comments_data,byid_already_parsed)
        ne3 = fill_nodes_edges(ne2['nodes'], ne2['edges'], tags_data,byid_already_parsed)
        ne4 = fill_nodes_edges(ne3['nodes'], ne3['edges'], likes_data,byid_already_parsed)
        new_ne = create_edge_node_lists(ne4['edges'], ne4['nodes'],g,title,s_date,e_date,entity,byid_already_parsed,connection,network_type)
    
    pages_ = get_politicians(connection,title,network_type)
    new_g = nx.Graph()
    for k,v in pages_.items():
        new_g.add_node(str(k),color="green",type="page",label=v)
    for b in new_ne['nodes'][0]:
        if b in pages_:
            new_g.add_node(str(b),color="green",type="page",label=pages_[b])
        else:
            new_g.add_node(str(b),color="blue",type="user",label="")
    for r in new_ne['nodes'][1]:  
        if r in pages_:
            new_g.add_node(str(r),color="green",type="page",label=pages_[r])
        else:
            new_g.add_node(str(r),color="red",type="user",label="")
    for bl in new_ne['nodes'][2]:  
        if bl in pages_:
            new_g.add_node(str(bl),color="green",type="page",label=pages_[bl])
        else:
            new_g.add_node(str(bl),color="black",type="user",label="")
            
    for e in new_ne['edges']:
        new_g.add_edge(str(e[0]),str(e[1]),color="black")
    if not os.path.exists(path_+'/Gephi_files/'):
        os.makedirs(path_+'/Gephi_files/')
    nx.write_gexf(new_g, path_+'/Gephi_files/{0}special_X.gexf'.format(title))

    #ne_degree = g.degree()
    #print sorted(ne_degree.iteritems(), key=lambda (w, s): s, reverse=True)
    print ("drawing layout...")
    pos=nx.spring_layout(g)
    #pos=nx.graphviz_layout(g)
    
    nx.draw_networkx_nodes(g,pos, nodelist=new_ne['nodes'][2], node_size=25, node_color='black')
    for b,r in zip(list(chunks(new_ne['nodes'][0], len(new_ne['nodes'][0])/40)),list(chunks(new_ne['nodes'][1], len(new_ne['nodes'][1])/40))):
        print ("drawing nodes...")
        nx.draw_networkx_nodes(g,pos, nodelist=b, node_size=25, node_color='blue')
        nx.draw_networkx_nodes(g,pos, nodelist=r, node_size=25, node_color='red')
    #nx.draw_networkx_nodes(g,pos, nodelist=new_ne['nodes'][3], node_size=125, node_color='red')
    #nx.draw_networkx_nodes(g,pos, nodelist=new_ne['nodes'][4], node_size=125, node_color='blue')
    patches = []
    if title == "DK_POLITICS_" or key_users == True:
        for n,s in zip(new_ne['nodes'][3],new_ne['sizes'][0]):
            print (s)
            nx.draw_networkx_nodes(g,pos, nodelist=[n], node_size=s*0.25+100, node_color='red')
            nx.draw_networkx_labels(g, pos, labels=new_ne['labels'][0], font_color="black",font_size=9,font_weight="normal")
        for k,v in sorted(new_ne['legends'][1].items()):
            patches.append(mpatches.Patch(color='red', label=str(v)+ " : " +k),)
        for n,s in zip(new_ne['nodes'][4],new_ne['sizes'][1]):
            nx.draw_networkx_nodes(g,pos, nodelist=[n], node_size=s*0.05+100, node_color='blue')
            nx.draw_networkx_labels(g, pos, labels=new_ne['labels'][1], font_color="black",font_size=9,font_weight="normal")
        for k,v in sorted(new_ne['legends'][2].items()):
            patches.append(mpatches.Patch(color='blue', label=str(v)+ " : " +k),)

    if network_type == "other":
        nx.draw_networkx_nodes(g,pos, nodelist=new_ne['nodes'][5], node_size=135, node_color='green')
        print (new_ne['nodes'][5])
        nx.draw_networkx_labels(g, pos, labels=new_ne['labels'][2], font_color="black",font_size=9,font_weight="normal")
        for k,v in sorted(new_ne['legends'][0].items()):
            patches.append(mpatches.Patch(color='green', label=str(v)+ " : " +k),)
    
    print ("drawing edges..")
    print (len(patches))
    nx.draw_networkx_edges(g,pos, edgelist=new_ne['edges'], edge_color='black', width=0.6,alpha=0.3)
    legend1 = plt.legend(handles=patches[:int(len(patches)/2)], fontsize=8, loc='upper right')
    plt.legend(handles=patches[int(len(patches)/2):], fontsize=8, loc='upper left')
    plt.gca().add_artist(legend1)
    if not os.path.exists(path_+'/Gephi_files/'):
        os.makedirs(path_+'/Gephi_files/')
    nx.write_gexf(g, path_+'/Gephi_files/{0}X.gexf'.format(title))
    plt.show()  
    
    #aggregate_likers(new_ne['nodes'][1], connection)
    
"""def draw_ego_graph():
    connection = MySQLdb.connect(host="localhost", user="root", passwd="swordfish", db="Facebook")
    cur = connection.cursor()
    title = "DK_NEWS_"
    nodes = {}
    edges = {}
    entity = 'dagbladetinformation'
    limit = 2000000
    
    g = nx.Graph()
    
    #likes_data = extract_data(title, connection, 'likes', limit, entity)
    #tags_data = extract_data(title, connection, 'tags', limit, entity)
    #replies_data = extract_data(title, connection, 'replies', limit, entity)
    comments_data = extract_data(title, connection, 'comments', limit, entity)
    ne = fill_nodes_edges(nodes, edges, comments_data)
    #ne1 = fill_nodes_edges(nodes, edges, likes_data)
    #ne2 = fill_nodes_edges(ne1['nodes'], ne1['edges'], tags_data)
    #ne3 = fill_nodes_edges(ne2['nodes'], ne2['edges'], replies_data)
    ne4 = fill_nodes_edges_entity(ne['nodes'], ne['edges'], comments_data)
    new_ne = create_edge_node_lists(ne4['edges'], ne4['nodes'],g)
    
    g.add_weighted_edges_from(new_ne['edges'])
    
    node_and_degree=g.degree()
    (largest_hub,degree)=sorted(node_and_degree.items(),key=itemgetter(1))[-1]
    hub_ego=nx.ego_graph(g,largest_hub)
    pos=nx.spring_layout(hub_ego)
    nx.draw(hub_ego,pos,node_color='b',node_size=30,with_labels=False)
    #nx.draw_networkx_nodes(hub_ego,pos, nodelist=new_ne['nodes'][0], node_size=25, node_color='blue')
    #nx.draw_networkx_nodes(hub_ego,pos, nodelist=new_ne['nodes'][1], node_size=25, node_color='red')
    #nx.draw_networkx_nodes(hub_ego,pos, nodelist=new_ne['nodes'][2], node_size=25, node_color='black')
    #nx.draw_networkx_edges(hub_ego,pos, edgelist=new_ne['edges'], edge_color='black', width=0.8,alpha=0.6)
    nx.draw_networkx_nodes(hub_ego,pos,nodelist=[largest_hub],node_size=60,node_color='green')
    print largest_hub
    
    plt.show() """

"""conn = sqlite3.connect("C:/Users/tempadmin/workspace/FacebookDEV/DB/test_.db")
cur = conn.cursor()
db = "test_"
path_ = "C:/Users/tempadmin/workspace/FacebookDEV"""


#draw_undi_graph(conn,db,path_)
#draw_ego_graph()


