import time
import networkx as nx
import pickle
from operator import itemgetter
from networkx.drawing.nx_agraph import to_agraph
import sqlite3
import os

def create_non_empty_ids(id_list):

    new_id_list = {}
    
    for k,v in id_list.items():
        if not v:
            pass
        else:
            new_id_list[k]=v
    
    print (len(id_list))
    print (len(new_id_list))
    
    return new_id_list

def create_empty_pol_set(connection):
    
    total_count = {}
    cur = connection.cursor()
    
    cur.execute("select distinct party from political_entities")
    for row in cur.fetchall():
        total_count[str(row[0])]=0.0
    empty_set = total_count
    
    return empty_set

def filter_network_by_pol_and_degree(pol_ids,g):
    
    degs = {}
    new_g = g.copy()
    deg = nx.degree(g)
    sorted_deg = sorted(deg.items(), key=lambda x:x[1], reverse=True)
    slice = len(sorted_deg)*0.001 
    print (len(sorted_deg)*0.001)
    sorted_deg = sorted_deg[:int(slice)]
    for k,v in sorted_deg:
        degs[k]=True
    for node in new_g.nodes():
        if node in pol_ids or node in degs:
            pass
        else:
            new_g.remove_node(node)
    
    new_deg = nx.degree(new_g)
    for node in new_g.nodes():
        if new_deg[node] < 1:
            new_g.remove_node(node)
    
    return new_g

def make_all_pol_interactions(conn,title,path,data_types="",start_date="",end_date="",user_orient=True):
        
    print ("Building network...")
    
    global pol_ids
    global color_pol_ids
    pol_ids = pickle.load( open( path+"/analytics/batch/" +"pol_by_id.p", "rb" ) )
    pol_ids = create_non_empty_ids(pol_ids)
    color_pol_ids = {}
    
    def assign_color_from_pol(id_):
    
        color = ""
        global pol_ids
        global color_pol_ids
        if id_ in pol_ids:
            prev_v = 0
            for k,v in pol_ids[id_].items():
                if v > prev_v:
                    color = str(k)
                    prev_v = v
                    
        else:
            color = "none"
        
        #print (color)
        color_pol_ids[id_]=color
        return color

    def get_politicians(Main_path,DB_name='pol_'):
        politicians = {}
        conn = sqlite3.connect(Main_path+"/DB/"+DB_name+'.db')
        cur = conn.cursor()
        cur.execute('select PA.page_id, PA.page_name, PO.party from {0}page_info PA, political_entities PO where PO.web_name = PA.web_name'.format(DB_name))
        for row in cur.fetchall():
            politicians[str(row[0])]=(str(row[1]),str(row[2]))
            
        return politicians
    
    def renew_edge_list(edge_list,pair):
        
        if (pair[0],pair[1]) in edge_list:
            edge_list[(pair[0],pair[1])]+=1
        elif (pair[1],pair[0]) in edge_list:
            edge_list[(pair[1],pair[0])]+=1
        else:
            edge_list[(pair[0],pair[1])]=1
        
        return edge_list
    
    def find_actor_type(page_ids,id_):
        
        if id_ in page_ids:
            return "page"
        else:
            return "user"
        
    def add_edge_weights(g,edge_list):
        
        new_g = g.copy()
        ed = g.edges()
        for edge in ed:
            if (edge[0],edge[1]) in edge_list:
                new_g.remove_edge(edge[0],edge[1])
                new_g.add_edge(edge[0],edge[1],weight=edge_list[(edge[0],edge[1])])
            elif (edge[1],edge[0]) in edge_list:
                new_g.remove_edge(edge[1],edge[0])
                new_g.add_edge(edge[1],edge[0],weight=edge_list[(edge[1],edge[0])])
            else:
                pass
        
        return new_g

    g=nx.Graph()
    cur = conn.cursor()
    post_ids = []
    edge_list = {}
    page_ids = {}
    cur.execute("select page_id from {0}page_info limit 1000000".format(title))
    for row in cur.fetchall():
        page_ids[str(row[0])]=True
    #print (page_ids)
    if start_date:
        cur.execute("select P.post_made_by_id, P.post_made_by_name, P.post_message, P.post_link, P.id, PA.page_id, PA.page_name, PA.category, PA.country from {0}post_info P, {0}page_info PA where P.web_name = PA.web_name and date(P.post_time_created) between date('{1}') and date('{2}')".format(title,start_date,end_date))
    else:
        cur.execute("select P.post_made_by_id, P.post_made_by_name, P.post_message, P.post_link, P.id, PA.page_id, PA.page_name, PA.category, PA.country from {0}post_info P, {0}page_info PA where P.web_name = PA.web_name".format(title))
    for row in cur.fetchall():
        post_id = str(row[4])
        post_ids.append(post_id)
        if user_orient == True:
            g.add_node(str(row[0]),label=row[1],pol=assign_color_from_pol(str(row[0])),type=find_actor_type(page_ids, str(row[0])))
            if str(row[0]) != str(row[5]):
                g.add_node(str(row[5]),label=row[6],pol=assign_color_from_pol(str(row[5])),type=find_actor_type(page_ids, str(row[5])),category=str(row[7]),country=str(row[8]))
                g.add_edge(str(row[0]),str(row[5]))
                edge_list = renew_edge_list(edge_list, (str(row[0]),str(row[5])))
        else:
            g.add_node(post_id,label=row[1],type="post",message=row[2],link=str(row[3]))
            g.add_node(str(row[5]),label=row[6],type=find_actor_type(page_ids, str(row[5])),category=str(row[7]),country=str(row[8]))
            g.add_edge(post_id,str(row[5]))
            edge_list = renew_edge_list(edge_list, (post_id,str(row[5])))
        cur.execute("select L.post_like_by_id, L.post_like_by_name from {0}likes_info L where L.post_id = '{1}'".format(title,post_id))
        for rowl in cur.fetchall():
            if user_orient == True:
                #print (type(rowl[1]))
                g.add_node(str(rowl[0]),label=rowl[1],pol=assign_color_from_pol(str(rowl[0])),type=find_actor_type(page_ids, str(rowl[0])))
                g.add_edge(str(rowl[0]),str(row[0]))
                edge_list = renew_edge_list(edge_list, (str(rowl[0]),str(row[0])))
            else:
                g.add_node(str(rowl[0]),label=rowl[1],type=find_actor_type(page_ids, str(rowl[0])))
                g.add_edge(str(post_id),str(rowl[0]))
                edge_list = renew_edge_list(edge_list, (str(rowl[0]),post_id))
        cur.execute("select C.comment_made_by_id, C.comment_made_by_name, C.comment_message, C.comment_id from {0}comment_info C where C.post_id = '{1}'".format(title,post_id))
        for rowc in cur.fetchall():
            comment_id = str(rowc[3])
            if user_orient == True:
                g.add_node(str(rowc[0]),label=rowc[1],pol=assign_color_from_pol(str(rowc[0])),type=find_actor_type(page_ids, str(rowc[0])))
                g.add_edge(str(rowc[0]),str(row[0]))
                edge_list = renew_edge_list(edge_list, (str(rowc[0]),str(row[0])))
            else:
                g.add_node(str(comment_id),label=rowc[1],message=rowc[2],type="comment")
                g.add_edge(post_id,comment_id)
                edge_list = renew_edge_list(edge_list, (comment_id,post_id))
            cur.execute("select CL.comment_like_by_id, CL.comment_like_by_name from {0}comment_likes_info CL where CL.comment_id = '{1}'".format(title,comment_id))
            for rowcl in cur.fetchall():
                if user_orient == True:
                    g.add_node(str(rowcl[0]),label=rowcl[1],pol=assign_color_from_pol(str(rowcl[0])),type=find_actor_type(page_ids, str(rowcl[0])))
                    g.add_edge(str(rowcl[0]),str(rowc[0]))
                    edge_list = renew_edge_list(edge_list, (str(rowcl[0]),str(rowc[0])))
                else:
                    g.add_node(str(rowcl[0]),label=rowcl[1],type=find_actor_type(page_ids, str(rowcl[0])))
                    g.add_edge(str(comment_id),str(rowcl[0]))
                    edge_list = renew_edge_list(edge_list, (str(rowcl[0]),comment_id))
            cur.execute("select CT.tagged_id, CT.tagged_name from {0}comment_tags_info CT where CT.comment_id = '{1}'".format(title,comment_id))
            for rowct in cur.fetchall():
                if user_orient == True:
                    g.add_node(str(rowct[0]),label=rowct[1].decode('utf-8'),pol=assign_color_from_pol(str(rowct[0])),type=find_actor_type(page_ids, str(rowct[0])))
                    g.add_edge(str(rowct[0]),str(rowc[0]))
                    edge_list = renew_edge_list(edge_list, (str(rowct[0]),str(rowc[0])))
                else:
                    g.add_node(str(rowct[0]),label=str(rowct[1]),type=find_actor_type(page_ids, str(rowct[0])))
                    g.add_edge(str(comment_id),str(rowct[0]))
                    edge_list = renew_edge_list(edge_list, (str(rowct[0]),comment_id))
            cur.execute("select R.reply_made_by_id, R.reply_made_by_name, R.reply_message, R.reply_id from {0}replies_info R where R.comment_id = '{1}'".format(title,comment_id))
            for rowr in cur.fetchall():
                reply_id = str(rowr[3])
                if user_orient == True:
                    g.add_node(str(rowr[0]),label=rowr[1],pol=assign_color_from_pol(str(rowr[0])),type=find_actor_type(page_ids, str(rowr[0])))
                    g.add_edge(str(rowr[0]),str(rowc[0]))
                    edge_list = renew_edge_list(edge_list, (str(rowr[0]),str(rowc[0])))
                else:
                    g.add_node(str(reply_id),label=rowr[1],message=row[2],type="reply")
                    g.add_edge(str(comment_id),str(reply_id))
                    edge_list = renew_edge_list(edge_list, (str(reply_id),comment_id))
                cur.execute("select RL.reply_like_by_id, RL.reply_like_by_name from {0}reply_likes_info RL where RL.reply_id = '{1}'".format(title,reply_id))
                for rowrl in cur.fetchall():
                    if user_orient == True:
                        g.add_node(str(rowrl[0]),label=rowrl[1],pol=assign_color_from_pol(str(rowrl[0])),type=find_actor_type(page_ids, str(rowrl[0])))
                        g.add_edge(str(rowrl[0]),str(rowr[0]))
                        edge_list = renew_edge_list(edge_list, (str(rowrl[0]),str(rowr[0])))
                    else:
                        g.add_node(str(rowrl[0]),label=rowrl[1],type=find_actor_type(page_ids, str(rowrl[0])))
                        g.add_edge(str(rowrl[0]),str(reply_id))
                        edge_list = renew_edge_list(edge_list, (str(rowrl[0]),reply_id))
                        
    g = filter_network_by_pol_and_degree(pol_ids, g)
    g = add_edge_weights(g, edge_list)
     
    if start_date:
        if user_orient == True:
            nx.write_gexf(g, path+'/Gephi_files/{0}all_interactions_{1}_to_{2}_only_users_with_pol.gexf'.format(title,start_date,end_date))
        else:
            nx.write_gexf(g, path+'/Gephi_files/{0}all_interactions_{1}_to_{2}_with_pol.gexf'.format(title,start_date,end_date))
    else:
        if user_orient == True:
            nx.write_gexf(g, path+'/Gephi_files/{0}all_interactions_only_users_with_pol.gexf'.format(title))
        else:
            nx.write_gexf(g, path+'/Gephi_files/{0}all_interactions_with_pol.gexf'.format(title))

