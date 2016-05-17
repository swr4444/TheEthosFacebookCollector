import sqlite3
import pickle

global election_weights
global pol_ids
global Main_path
#Main_path = '/Users/Jakob/Documents/Analyse & Tal/Attention Triggers/database/TheEthosFacebookCollector/'

def create_non_empty_ids(id_list):
    
    new_id_list = {}
    
    for k,v in id_list.items():
        if not v:
            pass
        else:
            new_id_list[k]=v
    
    
    print ("Total number of users available  :  "+str(len(new_id_list)))
    
    return new_id_list

def get_ids_already_parsed(Main_path):
    
    try:
        posts_already_parsed = pickle.load( open( Main_path+"/analytics/batch/pol_by_id.p", "rb" ) )
    except:
        posts_already_parsed = {}
         
    return posts_already_parsed

def get_posts_already_parsed():
    
    try:
        posts_already_parsed = pickle.load( open( Main_path+"/analytics/batch/pol_posts.p", "rb" ) )
    except:
        posts_already_parsed = {}
         
    return posts_already_parsed

def get_election_results_weight(country_avg):
    
    weights = {}
    for party,percentage in country_avg.items():
        election_results = {'F':4.2,'OE':7.8,'A':26.3,'B':4.6,'AA':4.8,'Q':0.8,'I':7.5,'C':3.4,'V':19.5,'O':21.1,'N':0.98}
        election_result = election_results[party]
        weight = float(float(election_result/float(percentage)))
        weights[party]=weight
        #print (party + "\t" + str(weight) + "\t" + str(percentage))
        
    return weights

def create_dedi_groups(id_list, party):
    
    groups = {}
    
    zero = {}
    twen_fiv = {}
    fifty = {}
    seve_fiv = {}
    
    for k,v in id_list.items():
        if v[party] > 0.74:
            seve_fiv[k]=v
        elif v[party] > 0.59:
            fifty[k]=v
        elif v[party] > 0.24:
            twen_fiv[k]=v
        elif v[party] > 0.09 and v[party] < 0.25:
            zero[k]=v
        else:
            pass
    
    total_ids = float(len(zero) + len(twen_fiv) + len(fifty) + len(seve_fiv))
    
    print(str(float((len(zero))/total_ids)*100) + " : " + str(len(zero)))
    print(str(float((len(twen_fiv))/total_ids)*100) + " : " + str(len(twen_fiv)))
    print(str(float((len(fifty))/total_ids)*100) + " : " + str(len(fifty)))
    print(str(float((len(seve_fiv))/total_ids)*100) + " : " + str(len(seve_fiv)))
    
    print (total_ids)
    groups['0']=zero
    groups['25']=twen_fiv
    groups['50']=fifty
    groups['75']=seve_fiv
    
    return groups

def collapse_groups(groups):
    
    collapsed_group = {'all':{}}
    for k,v in groups.items():
        for kk,vv in v.items():
            collapsed_group['all'][kk]=vv
        
    return collapsed_group

def filter_group(groups,filters=[]):
    
    new_groups = {}
    for f in filters:
        if f in groups:
            new_groups[f]=groups[f]
            
        
    return new_groups

def create_dedi_collection(id_list,parties=["H","V","KrF","SV","Frp","MDG","A","Sp"],groups=['75','50','25','0']):
    
    chosen_ids = {}
    for party in parties:
        #Create specific groups of users that corresponds to dedication for a given party
        dedi_groups = create_dedi_groups(id_list, party)
        for id_,parties in collapse_groups(filter_group(dedi_groups, filters=groups))['all'].items():
            chosen_ids[id_]=parties

    return chosen_ids
    
def aggregate_likers(liker_list,print_len,normalize,party_,cur,title=""):
    
    rb = {}
    rb_template = []
    rb2 = {}
    
    cur.execute('select party from political_entities')
    for row in cur.fetchall():
        rb[str(row[0])]=0.0
        rb_template.append(row[0])
    
    for p in liker_list:
        for party in rb_template:
            rb[party]+=p[party]
    
    for k,v in rb.items():
        rb2[k]=float(float(v)/float(sum(rb.values())))
        
    if normalize == True:
        
        party_percent = float(1-rb2[party_])
        del rb2[party_]
        for k,v in rb2.items():
            if rb2[k] == 0:
                rb2[k]=0
            else:
                rb2[k]=(rb2[k]/party_percent)
    
    if print_len == True:
        
        total_per = 0
        #print (rb)
        for k,v in rb2.items():
            print (str(k) + "\t" + str(round(v*100,2))+"\t"+title)
            total_per+=v
            #print (len(liker_list))
        print (total_per)
    
    if '' in rb2:
        del rb2['']
    
    return rb2

def election_results_weight(party,percentage):
    
    global election_weights
    weighted_percentage = float(percentage*election_weights[party])
    return weighted_percentage

def make_election_weights(aggregated_likers_list,title=""):
    
    new_list = {}
    for k,v in aggregated_likers_list.items():
        new_list[k]=election_results_weight(k, v)
        #print (k+"\t"+str(round(election_results_weight(k, v),2))+"\t"+title)
    
    final_list = {}
    totals = float(100)/float(sum(new_list.values()))
    for k,v in new_list.items():
        final_list[k]=v*totals
    
    return final_list

def compare_aggregated_likers(set1,set2,comparename='X'):
    
    comparelist = {}
    for k,v in set1.items():
        comparelist[k]=float(v-set2[k])
        
    #for k,v in comparelist.items():
        #print (str(k) + "\t" + str(round(v,2)) + "\t" + comparename)

    return comparelist
    
def get_users_from_pages(conn,db,pages):
    
    local_users = {}
    DB_name = db
    cur = conn.cursor()
    
    if not pages:
        try:
            cur.execute("select comment_made_by_id from {0}comment_info limit 1000000000".format(DB_name))
            for row in cur.fetchall():
                if not row[0] in local_users:
                    local_users[row[0]]=True
            cur.execute("select comment_like_by_id from {0}comment_likes_info limit 1000000000".format(DB_name))
            for row in cur.fetchall():
                if not row[0] in local_users:
                    local_users[row[0]]=True
            cur.execute("select post_like_by_id from {0}likes_info limit 1000000000".format(DB_name))
            for row in cur.fetchall():
                if not row[0] in local_users:
                    local_users[row[0]]=True
            cur.execute("select post_made_by_id from {0}post_info limit 1000000000".format(DB_name))
            for row in cur.fetchall():
                if not row[0] in local_users:
                    local_users[row[0]]=True
            cur.execute("select tagged_id from {0}comment_tags_info limit 1000000000".format(DB_name))
            for row in cur.fetchall():
                if not row[0] in local_users:
                    local_users[row[0]]=True
        except:
            pass
        
        try:
            cur.execute("select member_id from {0}group_member_info limit 1000000000".format(DB_name))
            for row in cur.fetchall():
                if not row[0] in local_users:
                    local_users[row[0]]=True
        except:
            pass
        
        print ("Number of users in chosen collection  :  "+str(len(local_users)))
     
        return local_users
    
    else:
        
        for page in pages:
            try:
                cur.execute("select comment_made_by_id from {0}comment_info C , {0}post_info P, {0}page_info PA where P.web_name = PA.web_name and PA.web_name = '{1}' and P.id = C.post_id limit 1000000000".format(DB_name,page))
                for row in cur.fetchall():
                    if not row[0] in local_users:
                        local_users[row[0]]=True
                cur.execute("select CL.comment_like_by_id from {0}comment_likes_info CL,{0}comment_info C, {0}post_info P, {0}page_info PA where P.web_name = PA.web_name and PA.web_name = '{1}' and C.post_id = P.id and C.comment_id = CL.comment_id limit 1000000000".format(DB_name,page))
                for row in cur.fetchall():
                    if not row[0] in local_users:
                        local_users[row[0]]=True
                cur.execute("select L.post_like_by_id from {0}likes_info L {0}post_info P where P.id in (select id from {0}post_info P, {0}page_info PA where P.web_name = PA.web_name and PA.web_name = '{1}') and L.post_id = P.id limit 1000000000".format(DB_name,page))
                for row in cur.fetchall():
                    if not row[0] in local_users:
                        local_users[row[0]]=True
                cur.execute("select post_made_by_id from {0}post_info P, {0}page_info PA where P.web_name = PA.web_name and PA.web_name = '{1}' limit 1000000000".format(DB_name,page))
                for row in cur.fetchall():
                    if not row[0] in local_users:
                        local_users[row[0]]=True
                cur.execute("select CT.tagged_id from {0}comment_tags_info CT, {0}post_info P, {0}page_info PA where P.web_name = PA.web_name and PA.web_name = '{1}' limit 1000000000".format(DB_name,page))
                for row in cur.fetchall():
                    if not row[0] in local_users:
                        local_users[row[0]]=True
            except:
                pass
            
            try:
                cur.execute("select member_id from {0}group_member_info where web_name = '{1}' limit 1000000000".format(DB_name,page))
                for row in cur.fetchall():
                    if not row[0] in local_users:
                        local_users[row[0]]=True
            except:
                pass
                    
        print ("Number of users in chosen collection  :  "+str(len(local_users)))
       
        return local_users
    
def get_pol_from_users(userlist,cur,compare=False,election_weights=False,title="X"):
    
    global pol_ids
    pol_users = {}
    
    for user in userlist:
        if user in pol_ids:
            pol_users[user]=pol_ids[user]
    print ("Number of users in politically significant sample"+"  :  "+str(len(pol_users)))
    
    if election_weights == True:
                
        if compare == False:
            pol_users = make_election_weights(aggregate_likers(pol_users.values(), False, False, "", cur, title=title),title=title)
            return pol_users
        
        else:
            pol_users = make_election_weights(aggregate_likers(pol_users.values(), False, False, "", cur))
            all_pol_users = make_election_weights(aggregate_likers(pol_ids.values(), False, False, "", cur))
            compared_pol_users = compare_aggregated_likers(pol_users, all_pol_users,comparename=title )
            return compared_pol_users
    else:
        
        if compare == False:
            pol_users = aggregate_likers(pol_users.values(), False, False, "", cur, title=title)
            return pol_users
        
        else:
            pol_users = aggregate_likers(pol_users.values(), False, False, "", cur)
            all_pol_users = aggregate_likers(pol_ids.values(), False, False, "", cur)
            compared_pol_users = compare_aggregated_likers(pol_users, all_pol_users,comparename=title)
            return compared_pol_users
        

def get_swing(Main_path_,conn_,DB,pages_,title_="",compare_=False,election_weights_=False,print_result=True):
    
    def print_result(result,title,election_weight=False):
        
        print ("\n")
        print ("OVERALL POLITICAL SWING:")
        print ("\n")
        for k,v in result.items():
            if election_weight == True:
                print (str(k) + "\t" + str(round(v,3)) + "\t" + title)
            else:
                print (str(k) + "\t" + str(round(v,3)) + "\t" + title)
        print (sum(result.values()))
    
    global election_weights
    global pol_ids
    global conn
    global cur
    global Main_path
    conn = conn_
    Main_path = Main_path_
    DB_name = DB
    cur = conn.cursor()
    pol_ids = get_ids_already_parsed(Main_path)
    pol_ids = create_non_empty_ids(pol_ids)
    pol_ids = create_dedi_collection(pol_ids, parties=['A'],groups=['75'])
    if election_weights_ == True:
        election_weights = get_election_results_weight((aggregate_likers(pol_ids.values(), False, False, "", cur)))
    result = get_pol_from_users(get_users_from_pages(conn, DB_name,pages_), cur, compare=compare_,election_weights=election_weights_,title=title_)
    
    print_result(result, title_,election_weight=election_weights_)
    
    
    
    