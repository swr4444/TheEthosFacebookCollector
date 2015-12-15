# -*- coding: utf-8 -*-
import sqlite3
import json
import sys
import os
import time
import codecs
import datetime
from os import listdir
if sys.version_info[0] < 3:
    print ("You need Python 3")
    sys.exit()
    import urllib as urllib2
else:
    import urllib.request
from urllib.error import HTTPError

def try_json_list(var_,keys_,index_):
    if len(keys_) == 2:
        try:
            new_data = var_[keys_[0]][keys_[1]][index_]
            if not new_data:
                return ""
            return ""
        except:
            return ""
    elif len(keys_) == 1:
        try:
            new_data = var_[keys_[0]][index_]
            if not new_data:
                return ""
            return new_data
        except:
            return ""

def try_json_str(var_,keys_):
    if len(keys_) == 2:
        try:
            new_data = str(var_[keys_[0]][keys_[1]])
            return new_data
        except:
            return str("")
    elif len(keys_) == 1:
        try:
            new_data = str(var_[keys_[0]])
            return new_data
        except:
            return str("")

def try_json_int(var_,keys_):
    if len(keys_) == 2:
        try:
            new_data = int(var_[keys_[0]][keys_[1]])
            return new_data
        except:
            return 0
    elif len(keys_) == 1:
        try:
            new_data = int(var_[keys_[0]])
            return new_data
        except:
            return 0

def try_json_float(var_,keys_):
    if len(keys_) == 2:
        try:
            new_data = float(var_[keys_[0]][keys_[1]])
            return new_data
        except:
            return 0.0
    elif len(keys_) == 1:
        try:
            new_data = float(var_[keys_[0]])
            return new_data
        except:
            return 0.0
        
        
def create_indeces(conn,title):
    
    cur = conn.cursor()
    create_idx = "CREATE INDEX IF NOT EXISTS idx1 ON {0}page_info (web_name, id, page_name); CREATE INDEX IF NOT EXISTS idx2 ON {0}page_likes_info (web_name, id, liked_page_id, liked_page_name); CREATE INDEX IF NOT EXISTS idx3 ON {0}post_info (web_name, id, post_time_created, fb_post_id, post_made_by_id); CREATE INDEX IF NOT EXISTS idx4 ON {0}comment_info (comment_id,post_id, id,comment_made_by_id, comment_made_by_name, comment_time_created); CREATE INDEX IF NOT EXISTS idx5 ON {0}likes_info (post_like_by_id,post_id, id); CREATE INDEX IF NOT EXISTS idx6 ON {0}comment_likes_info (comment_id, id, comment_like_by_id); CREATE INDEX IF NOT EXISTS idx7 ON {0}replies_info (comment_id, id, reply_id, reply_made_by_id); CREATE INDEX IF NOT EXISTS idx8 ON {0}comment_tags_info (comment_id, id, tagged_id);".format(title)
    for state in create_idx.split(";"):
        try:
            cur.execute(state)
        except:
            pass
    conn.commit()

def update_newest_posts(title,post_id,likes,comments,comment_likes,replies,reply_likes,comment_tags,reply_tags,connection):
    
    cursor = connection.cursor()
    
    #SQL statement for adding comment data
    insert_comments = ("INSERT INTO {0}newest_comment_info "
                       "(comment_id, comment_message, comment_like_count, comment_time_created, comment_made_by_id, comment_made_by_name, post_id, fb_post_id)"
                       "VALUES (?, ?, ?, ?, ?, ?, ?, ?)".format(title))
    
    insert_likes = ("INSERT INTO {0}newest_likes_info "
                       "(post_like_by_id, post_like_by_name, post_id, fb_post_id)"
                       "VALUES (?, ?, ?, ?)".format(title))
    
    
    insert_replies = ("INSERT INTO {0}newest_replies_info "
                       "(reply_id, reply_message, reply_like_count, reply_time_created, reply_made_by_id, reply_made_by_name, reply_made_to_id, reply_made_to_name, comment_id, fb_post_id)"
                       "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)").format(title)
    
    insert_comment_likes = ("INSERT INTO {0}newest_comment_likes_info "
                       "(comment_like_by_id, comment_like_by_name, comment_like_to_id, comment_like_to_name, comment_id, fb_post_id)"
                       "VALUES (?, ?, ?, ?, ?, ?)").format(title)
    
    insert_comment_tags = ("INSERT INTO {0}newest_comment_tags_info "
                       "(tagged_id, tagged_name, type, tag_made_by_id, tag_made_by_name, comment_id, fb_post_id)"
                       "VALUES (?, ?, ?, ?, ?, ?, ?)").format(title)
                       
    insert_reply_tags = ("INSERT INTO {0}newest_reply_tags_info "
                       "(tagged_id, tagged_name, type, tag_made_by_id, tag_made_by_name ,reply_id, fb_post_id)"
                       "VALUES (?, ?, ?, ?, ?, ?, ?)").format(title)
    
    insert_reply_likes = ("INSERT INTO {0}newest_reply_likes_info "
                       "(reply_like_by_id, reply_like_by_name, reply_like_to_id, reply_like_to_name, reply_id, fb_post_id)"
                       "VALUES (?, ?, ?, ?, ?, ?)").format(title)
    
    
                       
    
    
    for comment in comments:
        
        try:
            templist = []
            templist = comment
            templist.append(post_id)
            cursor.execute(insert_comments, templist)
        except:
            print ('comments insertion error....')
                        
    for comment_like in comment_likes:
        
        try:
            templist = []
            templist = comment_like
            templist.append(post_id)
            cursor.execute(insert_comment_likes, templist)
        except:
            print ('comment_likes insertion error....')
    
    for reply in replies:
        
        try:
            templist = []
            templist = reply
            templist.append(post_id)
            cursor.execute(insert_replies, templist)
        except:
            print ('replies insertion error....')
            
    for reply_like in reply_likes:
        
        try:
            templist = []
            templist = reply_like
            templist.append(post_id)
            cursor.execute(insert_reply_likes, templist)
        except:
            print ('reply_likes insertion error....')
            
    for tag in comment_tags:
        
        try:
            templist = []
            templist = tag
            templist.append(post_id)
            cursor.execute(insert_comment_tags,templist)
        except:
            print ('comment_tags insertion error....')
            
    for tag in reply_tags:
        
        try:
            templist = []
            templist = tag
            templist.append(post_id)
            cursor.execute(insert_reply_tags, templist)
        except:
            print ('reply_tags insertion error....')
    
    for like in likes:
        try:
            templist = []
            templist = like
            templist.append(post_id)
            cursor.execute(insert_likes, templist)
        except:
            print ('likes insertion error....')
        
    
    connection.commit()

def write_newest_posts(title,delete_date,company,post,likes,comments,comment_likes,replies,reply_likes,comment_tags,reply_tags,connection):
    
    cursor = connection.cursor()
    cursor.execute("CREATE  TABLE IF NOT EXISTS `{0}newest_post_info` (`fb_post_id` VARCHAR(100), `post_made_by_id` VARCHAR(100), `post_made_by_name` VARCHAR(100), `shares` INT, `post_type` VARCHAR(50), `post_picture` TEXT, `post_time_created` DATETIME, `post_caption` VARCHAR(300),`post_description` LONGTEXT,`post_headline` LONGTEXT, `post_link` VARCHAR(400), `post_message` LONGTEXT, `web_name` VARCHAR(200),`page_id` VARCHAR(300),`id` INTEGER PRIMARY KEY AUTOINCREMENT);".format(title))
    cursor.execute("CREATE  TABLE IF NOT EXISTS `{0}newest_replies_info` (`reply_id` VARCHAR(100),`reply_message` LONGTEXT,`reply_like_count` INT,`reply_time_created` DATETIME, `reply_made_by_id` VARCHAR(200), `reply_made_by_name` VARCHAR(200), `reply_made_to_id` VARCHAR(200), `reply_made_to_name` VARCHAR(200),  `comment_id` VARCHAR(300),`fb_post_id` VARCHAR(300),`id` INTEGER PRIMARY KEY AUTOINCREMENT );".format(title))
    cursor.execute("CREATE  TABLE IF NOT EXISTS `{0}newest_comment_likes_info` (`comment_like_by_id` VARCHAR(200), `comment_like_by_name` VARCHAR(200), `comment_like_to_id` VARCHAR(200), `comment_like_to_name` VARCHAR(200),`comment_id` VARCHAR(300),`fb_post_id` VARCHAR(300),`id` INTEGER PRIMARY KEY AUTOINCREMENT);".format(title))
    cursor.execute("CREATE  TABLE IF NOT EXISTS `{0}newest_reply_likes_info` (`reply_like_by_id` VARCHAR(200), `reply_like_by_name` VARCHAR(200),`reply_like_to_id` VARCHAR(200), `reply_like_to_name` VARCHAR(200), `reply_id` VARCHAR(300),`fb_post_id` VARCHAR(300),`id` INTEGER PRIMARY KEY AUTOINCREMENT);".format(title))
    cursor.execute("CREATE  TABLE IF NOT EXISTS `{0}newest_comment_tags_info` (`tagged_id` VARCHAR(200), `tagged_name` VARCHAR(200), `type` VARCHAR(50), `tag_made_by_id` VARCHAR(200), `tag_made_by_name` VARCHAR(200), `comment_id` VARCHAR(300),`fb_post_id` VARCHAR(300),`id` INTEGER PRIMARY KEY AUTOINCREMENT);".format(title))
    cursor.execute("CREATE  TABLE IF NOT EXISTS `{0}newest_reply_tags_info` (`tagged_id` VARCHAR(200), `tagged_name` VARCHAR(200), `type` VARCHAR(50), `tag_made_by_id` VARCHAR(200), `tag_made_by_name` VARCHAR(200), `reply_id` VARCHAR(300),`fb_post_id` VARCHAR(300),`id` INTEGER PRIMARY KEY AUTOINCREMENT);".format(title))
    cursor.execute("CREATE  TABLE IF NOT EXISTS `{0}newest_comment_info` (`comment_id` VARCHAR(100),`comment_message` LONGTEXT,`comment_like_count` INT,`comment_time_created` DATETIME,`comment_made_by_id` VARCHAR(200),`comment_made_by_name` VARCHAR(200),`post_id` VARCHAR(300),`fb_post_id` VARCHAR(300),`id` INTEGER PRIMARY KEY AUTOINCREMENT);".format(title))
    cursor.execute("CREATE  TABLE IF NOT EXISTS `{0}newest_likes_info` (`post_like_by_id` VARCHAR(200),`post_like_by_name` VARCHAR(200),`post_id` VARCHAR(300),`fb_post_id` VARCHAR(300),`id` INTEGER PRIMARY KEY AUTOINCREMENT);".format(title))
            
    
    
    cursor.execute("select distinct post_time_created, fb_post_id from {0}newest_post_info where web_name = '{1}' order by post_time_created desc".format(title,company))
    for row in cursor.fetchall():
        this_date = datetime.datetime.strptime(str(row[0]),'%Y-%m-%d %H:%M:%S')
        if this_date < delete_date:
    
            cursor.execute("delete from {0}newest_post_info where fb_post_id = '{1}'".format(title,str(row[1])))
            cursor.execute("delete from {0}newest_comment_info where fb_post_id = '{1}'".format(title,str(row[1])))
            cursor.execute("delete from {0}newest_likes_info where fb_post_id = '{1}'".format(title,str(row[1])))
            cursor.execute("delete from {0}newest_replies_info where fb_post_id = '{1}'".format(title,str(row[1])))
            cursor.execute("delete from {0}newest_comment_likes_info where fb_post_id = '{1}'".format(title,str(row[1])))
            cursor.execute("delete from {0}newest_reply_likes_info where fb_post_id = '{1}'".format(title,str(row[1])))
            cursor.execute("delete from {0}newest_comment_tags_info where fb_post_id = '{1}'".format(title,str(row[1])))
            cursor.execute("delete from {0}newest_reply_tags_info where fb_post_id = '{1}'".format(title,str(row[1])))
        
            connection.commit()
    
    #SQL statement for adding post data                
    insert_posts = ("INSERT INTO {0}newest_post_info "
                    "(fb_post_id, post_made_by_id, post_made_by_name, shares, post_type, post_picture, post_time_created, post_caption, post_description, post_headline, post_link, post_message,web_name ,page_id)"
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)".format(title))
    
    #SQL statement for adding comment data
    insert_comments = ("INSERT INTO {0}newest_comment_info "
                       "(comment_id, comment_message, comment_like_count, comment_time_created, comment_made_by_id, comment_made_by_name, post_id, fb_post_id)"
                       "VALUES (?, ?, ?, ?, ?, ?, ?, ?)".format(title))
    
    insert_likes = ("INSERT INTO {0}newest_likes_info "
                       "(post_like_by_id, post_like_by_name, post_id, fb_post_id)"
                       "VALUES (?, ?, ?, ?)".format(title))
    
    
    insert_replies = ("INSERT INTO {0}newest_replies_info "
                       "(reply_id, reply_message, reply_like_count, reply_time_created, reply_made_by_id, reply_made_by_name, reply_made_to_id, reply_made_to_name, comment_id, fb_post_id)"
                       "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)").format(title)
    
    insert_comment_likes = ("INSERT INTO {0}newest_comment_likes_info "
                       "(comment_like_by_id, comment_like_by_name, comment_like_to_id, comment_like_to_name, comment_id, fb_post_id)"
                       "VALUES (?, ?, ?, ?, ?, ?)").format(title)
    
    insert_comment_tags = ("INSERT INTO {0}newest_comment_tags_info "
                       "(tagged_id, tagged_name, type, tag_made_by_id, tag_made_by_name, comment_id, fb_post_id)"
                       "VALUES (?, ?, ?, ?, ?, ?, ?)").format(title)
                       
    insert_reply_tags = ("INSERT INTO {0}newest_reply_tags_info "
                       "(tagged_id, tagged_name, type, tag_made_by_id, tag_made_by_name ,reply_id, fb_post_id)"
                       "VALUES (?, ?, ?, ?, ?, ?, ?)").format(title)
    
    insert_reply_likes = ("INSERT INTO {0}newest_reply_likes_info "
                       "(reply_like_by_id, reply_like_by_name, reply_like_to_id, reply_like_to_name, reply_id, fb_post_id)"
                       "VALUES (?, ?, ?, ?, ?, ?)").format(title)
    
    try:
        cursor.execute(insert_posts, post)
    except:
        print ('newests posts insertion error....')
    
    for comment in comments:
        
        try:
            templist = []
            templist = comment
            templist.append(str(post[0]))
            cursor.execute(insert_comments, templist)
        except:
            print ('comments insertion error....')
                        
    for comment_like in comment_likes:
        
        try:
            templist = []
            templist = comment_like
            templist.append(str(post[0]))
            cursor.execute(insert_comment_likes, templist)
        except:
            print ('comment_likes insertion error....')
    
    for reply in replies:
        
        try:
            templist = []
            templist = reply
            templist.append(str(post[0]))
            cursor.execute(insert_replies, templist)
        except:
            print ('replies insertion error....')
            
    for reply_like in reply_likes:
        
        try:
            templist = []
            templist = reply_like
            templist.append(str(post[0]))
            cursor.execute(insert_reply_likes, templist)
        except:
            print ('reply_likes insertion error....')
            
    for tag in comment_tags:
        
        try:
            templist = []
            templist = tag
            templist.append(str(post[0]))
            cursor.execute(insert_comment_tags,templist)
        except:
            print ('comment_tags insertion error....')
            
    for tag in reply_tags:
        
        try:
            templist = []
            templist = tag
            templist.append(str(post[0]))
            cursor.execute(insert_reply_tags, templist)
        except:
            print ('reply_tags insertion error....')
    
    for like in likes:
        #try:
        templist = []
        templist = like
        templist.append(str(post[0]))
        cursor.execute(insert_likes, templist)
        #except:
        #print ('likes insertion error....')
            
    print ("inserting newest posts: " + str(post[6]))
    
    connection.commit()

def connect_db(db_path,title):
    #fill this out with your db connection info
    connection = sqlite3.connect(db_path+'/'+title+'.db') 
    return connection
 
def create_post_url(graph_url,firstdate,lastdate, APP_ID, APP_SECRET): 
    #create authenticated post URL
 
    if len(firstdate) > 24:
        start = str(firstdate)[:-16] 
    else:
        start = str(firstdate)[:-9]
    if len(lastdate) > 24:
        stop = str(lastdate)[:-16]
    else:
        stop = str(lastdate)[:-9]
    
    post_args = "/feed/?fields=id,from.fields(id,name),shares,type,picture,object_id,created_time,caption,description,name,link,message&limit=25&since=" + stop + "&until=" + start + "&key=value&access_token=" + APP_ID + "|" + APP_SECRET
    post_url = graph_url + post_args
 
    return post_url
    
def render_to_json(graph_url):
    #render graph url call to JSON
    tempG = graph_url
    tempB = False
    tempN = 0
    
    while tempN < 10:
        
        try:
            if sys.version_info[0] < 3:
                try:
                    web_response = urllib2.urlopen(tempG, timeout=30)
                except HTTPError:
                    if tempN > 2:
                        return {'data':['bad_request']}
                    else:
                        pass
            else:
                try:
                    web_response = urllib.request.urlopen(tempG, timeout=30)
                except HTTPError:
                    if tempN > 1:
                        return {'data':['bad_request']}
                    else:
                        pass
            readable_page = web_response.read().decode('latin-1')
            json_data = json.loads(readable_page)
            return json_data
            tempB = True
            tempN = 100
        except:
            tempB = False
            print ("recalling..... " + str(tempG))
            time.sleep(5)
            tempN+=1
            
    return []

def create_page_likes_url(graph_url, page, APP_ID, APP_SECRET):
    #create Graph API Call
    page_args = page + "/likes?limit=10000&fields=id,name,category,category_list&key=value&access_token=" + APP_ID + "|" + APP_SECRET
    page_likes_url = graph_url + page_args
    #print comments_url
    return page_likes_url


def get_page_likes(page_likes_url,page_likes_data,page):
    
    page_likes = render_to_json(page_likes_url)
    if not page_likes: return []
    try:
        page_likes = page_likes['data']
    except:
        page_likes = []
    
    for like in page_likes:
        try:
            categories = ''
            for c in like['category_list']:
                categories = c['name'] + ',' + categories
        except:
            categories = 'Null'

        try:
            page_likes_data.append([like['name'],like['id'],like['category'],categories,page])
        except:
            page_likes_data.append([ "error", "error", "error", "error", "error"])
    
    return page_likes_data

 
def scrape_posts_by_date(graph_url, date, firstdate, post_data, APP_ID, APP_SECRET):
    #render URL to JSON
    page_posts = render_to_json(graph_url)
    
    #extract next page
    try:
        next_page = page_posts["paging"]["next"]
    except:
        emptyList = []
        return emptyList
    
    #grab all posts
    page_posts = page_posts["data"]
    #boolean to tell us when to stop collecting
    collecting = True

    #for each post capture data
    for post in page_posts:
        try:
            current_post = [try_json_str(post,['id']),try_json_str(post,['from','id']),try_json_str(post,['from','name']),try_json_int(post,['shares','count']),try_json_str(post,['type']),try_json_str(post,['picture']),try_json_str(post,['created_time']).replace('T',' ').replace('+0000',''),try_json_str(post,['caption']),try_json_str(post,['description']),try_json_str(post,['name']),try_json_str(post,['link']),try_json_str(post,['message'])]        
            current_date = post['created_time'].replace('T',' ').replace('+0000','')               
        except Exception:
            current_post = [ "error", "error", "error", "error", "error", "error", "error", "error", "error","error","error","error"]
            print ("error")
        if current_post[6] != "error":
            current_date = datetime.datetime.strptime(str(current_date).replace("T"," "),'%Y-%m-%d %H:%M:%S')
            firstdate = datetime.datetime.strptime(str(firstdate).split(".")[0].replace("T"," "),'%Y-%m-%d %H:%M:%S')
            date = datetime.datetime.strptime(str(date).split(".")[0].replace("T"," "),'%Y-%m-%d %H:%M:%S')
            if firstdate > current_date:
                print (str(current_post[6])+ ' : ' + str(date))
                
                if date < current_date:
                    post_data.append(current_post)
                
                elif date > current_date:
                    print ("Done collecting")
                    collecting = False
                    break
    
    
    #If we still don't meet date requirements, run on next page            
    if collecting == True:
        scrape_posts_by_date(next_page, date, firstdate, post_data, APP_ID, APP_SECRET)
    
    return post_data
        
    
def create_comments_url(graph_url, post_id, APP_ID, APP_SECRET):
    #create Graph API Call
    comments_args = post_id + "/comments?fields=id,from.fields(id,name),message,created_time,like_count,message_tags,likes.limit(10000).fields(id,name),comments.limit(10000).fields(id,from.fields(id,name),message,created_time,like_count,message_tags,likes.limit(10000).fields(id,name))&limit=10000&key=value&access_token=" + APP_ID + "|" + APP_SECRET
    comments_url = graph_url + comments_args
    #print comments_url
    return comments_url

def create_specific_comment_url(graph_url, comment_id, APP_ID, APP_SECRET):
    comments_args = comment_id + "?fields=id,from.limit(1000).fields(id,name),message,created_time,like_count,message_tags,likes.limit(10000).fields(id,name),comments.limit(10000).fields(id,from.fields(id,name),message,created_time,like_count,message_tags,likes.limit(10000).fields(id,name))&limit=10000&key=value&access_token=" + APP_ID + "|" + APP_SECRET
    comments_url = graph_url + comments_args
    return comments_url
        

def create_likes_url(graph_url, post_id, APP_ID, APP_SECRET):
    #create Graph API Call
    likes_args = post_id + "/likes?fields=id,name&limit=100000&key=value&access_token=" + APP_ID + "|" + APP_SECRET
    likes_url = graph_url + likes_args
    #print comments_url
    return likes_url


def get_likes_data(likes_url, likes_data, post_id,title,connection):
    #render URL to JSON
    
    like_page = render_to_json(likes_url)
    if not like_page:
        cursor = connection.cursor()
        post_id_list = [post_id]
        cursor.execute("INSERT INTO {0}missed_post_id (post_id) values (?)".format(title),post_id_list)
        return []
    else:
    
        try:
            #extract next page
            next_page = like_page["paging"]["next"]
        except Exception:
            next_page = None
            
        likes = like_page["data"]
        
        #for each comment capture data
        for like in likes:
            try:
                current_likes = [try_json_str(like,["id"]),try_json_str(like,["name"]), post_id]
                #print current_comments
                likes_data.append(current_likes)
                
            except Exception:
                current_likes = ["error", "error", "error"]
                
                
        #if we have another page, recurse
        if next_page is not None:
            get_likes_data(next_page, likes_data, post_id, title, connection)
            
            
        return likes_data



def get_comments_data(comments_url, comment_data, comment_like_data, reply_data, reply_like_data, comment_tag_data, reply_tag_data, post_id, next_page_bool, title, connection, graph_url, APP_ID, APP_SECRET, bad_request, fb_post_id):
    #render URL to JSON
    comment_page = render_to_json(comments_url)
    #print (comments_url)
    if not comment_page:
        cursor = connection.cursor()
        post_id_list = [post_id]
        cursor.execute("INSERT INTO {0}missed_post_id (post_id) values (?)".format(title),post_id_list)
        return [[],[],[],[],[],[]]
    else:
        try:
            if comment_page['data'][0] == 'bad_request':
                    print ("Bad Request. Too much data. "+"\n"+"Reconfiguring API-CALL. Depending on the amount of data, it might take up to an hour...")
                    comment_args = str(fb_post_id) + "/comments?fields=id&limit=100000&key=value&access_token=" + APP_ID + "|" + APP_SECRET
                    specific_comments_url = graph_url + comment_args
                    comment_page = render_to_json(specific_comments_url)
                    bad_request = True
        except:
            pass
    
        if next_page_bool == True:
            try:
                #extract next page
                next_page = comment_page["paging"]["next"]
                #print next_page
            except Exception:
                next_page = None
            try:
                comments = comment_page["data"]
            except:
                comments = []
            
        else:
            
            try:
                #extract next page
                next_page = comment_page["comments"]["paging"]["next"]
                next_page_bool = True
            except Exception:
                next_page = None
            try:   
                comments = comment_page["data"]
            except:
                comments = []
        #for each comment capture data
        
        for comment in comments:
            
            if bad_request == True:
                try:
                    specific_comment_url = create_specific_comment_url(graph_url, comment['id'], APP_ID, APP_SECRET)
                    comment = render_to_json(specific_comment_url)
                except:
                    comment = []
                #print (specific_comment_url)
                if "bad_request" in str(comment): continue
            #if comment:
            try:
                current_comments = [try_json_str(comment, ["id"]), str(comment["message"]), comment["like_count"],
                                comment["created_time"].replace('T',' ').replace('+0000',''), try_json_str(comment,['from','id']), try_json_str(comment,['from','id']),post_id]
                #print current_comments
                comment_data.append(current_comments)
                
                try:
                    comment_likes = comment["likes"]["data"]
                    
                    for comment_like in comment_likes:
                        
                        current_comment_likes = [comment_like["id"],str(comment_like["name"]),comment["from"]["id"], str(comment["from"]["name"]),comment["id"]]
                        comment_like_data.append(current_comment_likes)
                except:
                    pass
                
                
                try:
                    comment_tags = comment["message_tags"]
                    
                    for tag in comment_tags:
                        current_comment_tags = [tag["id"], tag["name"].encode("utf-8"), tag["type"],comment["from"]["id"],str(comment["from"]["name"]),comment["id"]]
                        comment_tag_data.append(current_comment_tags)
                except:
                    pass
                    
                
                try:    
                    replies = comment["comments"]["data"]
                
                    for reply in replies:
                        
                        current_replies = [reply["id"], str(reply["message"]), reply["like_count"],
                                reply["created_time"].replace('T',' ').replace('+0000',''), reply["from"]["id"],str(reply["from"]["name"]),comment["from"]["id"],str(comment["from"]["name"]),comment["id"]]
                        reply_data.append(current_replies)
                        
                        reply_likes = reply["likes"]["data"]
                        
                        for reply_like in reply_likes:
                            
                            current_reply_likes = [reply_like["id"],str(reply_like["name"]),reply["from"]["id"],str(reply["from"]["name"]),reply["id"]]
                            reply_like_data.append(current_reply_likes)
                        
                        try:
                            reply_tags = reply["message_tags"]
                            
                            for tag in reply_tags:
                                current_reply_tags = [tag["id"], str(tag["name"]), tag["type"],reply["from"]["id"],str(reply["from"]["name"]),reply["id"]]
                                reply_tag_data.append(current_reply_tags)
                        except:
                            pass
                        
                except:
                    pass
                
            except:    
                current_comments = ["error", "error", "error", "error", "error", "error", "error"]
                #print ("comment error...")
                
                
        #if we have another page, recurse
        if next_page is not None:
            get_comments_data(next_page, comment_data, comment_like_data, reply_data, reply_like_data, comment_tag_data, reply_tag_data, post_id,next_page_bool,title,connection,graph_url, APP_ID, APP_SECRET, False, fb_post_id)
        return [comment_data, comment_like_data, reply_data, reply_like_data, comment_tag_data, reply_tag_data]
 
def make_count_tables(title,connection):
    
    cursor = connection.cursor()

    cursor.execute("CREATE  TABLE IF NOT EXISTS `{0}with_count_post_info` (`fb_post_id` VARCHAR(100), `post_made_by_id` VARCHAR(100), `post_made_by_name` VARCHAR(100), `shares` INT, `post_type` VARCHAR(50), `post_picture` TEXT, `post_time_created` DATETIME, `post_caption` VARCHAR(300),`post_description` LONGTEXT,`post_headline` LONGTEXT, `post_link` VARCHAR(400), `post_message` LONGTEXT, `web_name` VARCHAR(200),`page_id` VARCHAR(300), `page_name` VARCHAR(200), `post_likes_count` INT, `comment_count` INT, `users_count` INT, `lenght_of_message` INT, `tags_count` INT, `id` INTEGER PRIMARY KEY AUTOINCREMENT);".format(title))
    cursor.execute("CREATE  TABLE IF NOT EXISTS `{0}with_count_comment_info` (`comment_id` VARCHAR(100),`comment_message` LONGTEXT,`comment_like_count` INT,`comment_time_created` DATETIME,`comment_made_by_id` VARCHAR(200),`comment_made_by_name` VARCHAR(200),`post_id` VARCHAR(300),  `comment_made_to_id` VARCHAR(200), `comment_made_to_name` VARCHAR(200), `replies_count` INT, `length_of_message` INT, `tags_count` INT, `id` INTEGER PRIMARY KEY AUTOINCREMENT);".format(title))

        #SQL statement for adding post data                
    insert_posts = ("INSERT INTO {0}with_count_post_info "
                    "(fb_post_id, post_made_by_id, post_made_by_name, shares, post_type, post_picture, post_time_created, post_caption, post_description, post_headline, post_link, post_message,web_name ,page_id, page_name, post_likes_count, comment_count, users_count, lenght_of_message, tags_count)"
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)".format(title))
    
    #SQL statement for adding comment data
    insert_comments = ("INSERT INTO {0}with_count_comment_info "
                       "(comment_id, comment_message, comment_like_count, comment_time_created, comment_made_by_id, comment_made_by_name, post_id, comment_made_to_id, comment_made_to_name, replies_count, length_of_message, tags_count)"
                       "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)".format(title))
    
    posts = []
    comments = []
    
    cursor.execute("select P.*, PA.page_name, length(P.post_message) from {0}post_info P, {0}page_info PA where P.web_name = PA.web_name and P.id not in (select id from {0}newest_post_info) and P.id not in (select id from {0}with_count_post_info)".format(title))
    for row in cursor.fetchall():
        post = []
        list_row = list(row)
        length_of_message = int(list_row.pop())
        page_name = list_row.pop()
        id_ = str(list_row.pop())
        post = list_row
        
        likes_count = 0
        distinct_like_users = 0
        distinct_comment_users = 0
        comment_count = 0
        comment_tags_count = 0
        distinct_comment_tags_users = 0
        cursor.execute('select count(L.id), count(distinct L.post_like_by_id) from {0}post_info P, {0}likes_info L where L.post_id = P.id and P.id = "{1}" group by P.id'.format(title,id_))
        for irow in cursor.fetchall():
            likes_count = int(irow[0])
            distinct_like_users = int(irow[1])
        cursor.execute('select count(L.id), count(distinct L.comment_made_by_id) from {0}post_info P, {0}comment_info L where L.post_id = P.id and P.id = "{1}" group by P.id'.format(title,id_))
        for irow in cursor.fetchall():
            comment_count = int(irow[0])
            distinct_comment_users = int(irow[1])
        cursor.execute('select count(distinct CT.id), count(distinct CT.tagged_id) from {0}comment_tags_info CT, {0}post_info P, {0}comment_info L where CT.comment_id = L.comment_id and L.post_id = P.id and P.id = "{1}" group by P.id'.format(title,id_))
        for irow in cursor.fetchall():
            comment_tags_count = int(irow[0])
            distinct_comment_tags_users = int(irow[1])
        
        post.append(page_name)
        post.append(likes_count)
        post.append(comment_count)
        post.append(distinct_like_users+distinct_comment_users+distinct_comment_tags_users)
        post.append(length_of_message)
        post.append(comment_tags_count)
        
        cursor.execute(insert_posts,post)
        
        cursor.execute("select C.*, P.post_made_by_id, P.post_made_by_name, length(C.comment_message) from {0}post_info P, {0}comment_info C where P.id = C.post_id and P.id = '{1}'".format(title,id_))
        for crow in cursor.fetchall():
            comment = []
            list_crow = list(crow)
            c_length_of_message = int(list_crow.pop())
            c_page_name = list_crow.pop()
            c_page_id = str(list_crow.pop())
            c_id = str(list_crow.pop())
            comment = list_crow
            c_likes_count = 0
            c_replies_count = 0
            c_tags_count = 0
            
            cursor.execute("select count(CL.id) from {0}comment_info C, {0}comment_likes_info CL where C.comment_id = CL.comment_id and C.comment_id = '{1}'".format(title,c_id))
            for irow in cursor.fetchall():
                c_likes_count = int(irow[0])

            cursor.execute("select count(CL.id) from {0}comment_info C, {0}replies_info CL where C.comment_id = CL.comment_id and C.comment_id = '{1}'".format(title,c_id))
            for irow in cursor.fetchall():
                c_replies_count = int(irow[0])    
                
            cursor.execute("select count(CL.id) from {0}comment_info C, {0}comment_tags_info CL where C.comment_id = CL.comment_id and C.comment_id = '{1}'".format(title,c_id))
            for irow in cursor.fetchall():
                c_tags_count = int(irow[0])
                
            comment.append(c_page_id) 
            comment.append(c_page_name) 
           
            comment.append(c_replies_count) 
            comment.append(c_length_of_message)
            comment.append(c_tags_count)
            
            cursor.execute(insert_comments,comment)
    
    connection.commit()        
    
def make_CSV_files(db,db_path):
    
    import csv
    table_info = []
    table_list = ["with_count_post_info","with_count_comment_info","post_info","comment_info","page_info","page_likes_info","comment_likes_info","replies_info","reply_likes_info","reply_tags_info","comment_tags_info","likes_info"]
    chosen_files = []
    chosen_files_joined = []
    temp_table_list = {"1":"with_count_post_info","2":"with_count_comment_info","3":"post_info","4":"comment_info","5":"page_info","6":"page_likes_info","7":"comment_likes_info","8":"replies_info","9":"reply_likes_info","10":"reply_tags_info","11":"comment_tags_info","12":"likes_info"}
    temp_table_joined_list = {"13":"likes_info","14":"comment_info"}
    
    def write_csvs(title,path,conn,table_list):
        table_info = []
        for table in table_list:
            try:
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE name='{0}{1}';".format(title,table))
                if cur.fetchall():
                    cur.execute("pragma table_info({0}{1})".format(title,table))
                    table_info = []
                    for row in cur.fetchall():
                        table_info.append(row[1])
                    cur.execute("select * from {0}{1} limit 1000000000".format(title,table))
                    w = csv.writer(codecs.open(path+"{0}{1}.csv".format(title,table), "w", "utf-8"))
                    rows = cur.fetchall()
                    w.writerow(table_info)
                    for row in rows:
                        w.writerow(row)
            except:
                print ("Can't find table: [{0}]".format(table))
    
    def write_joined_csvs(title,path,conn,table_list):
        table_info = []
        for table in table_list:
            try:
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE name='{0}{1}';".format(title,table))
                if cur.fetchall():
                    cur.execute("pragma table_info({0}{1})".format(title,table))
                    for row in cur.fetchall():
                        table_info.append(row[1])
                cur.execute("SELECT name FROM sqlite_master WHERE name='{0}post_info';".format(title))
                if cur.fetchall():
                    cur.execute("pragma table_info({0}post_info)".format(title))
                    for row in cur.fetchall():
                        table_info.append(row[1])
                cur.execute("SELECT name FROM sqlite_master WHERE name='{0}page_info';".format(title))
                if cur.fetchall():
                    cur.execute("pragma table_info({0}page_info)".format(title))
                    for row in cur.fetchall():
                        table_info.append(row[1])
                    cur.execute("select * from {0}{1} L, {0}post_info P, {0}page_info PA where L.post_id = P.id and P.web_name = PA.web_name limit 1000000000".format(title,table))
                    w = csv.writer(codecs.open(path+"{0}joined_{1}_posts_pages.csv".format(title,table), "w", "utf-8"))
                    rows = cur.fetchall()
                    w.writerow(table_info)
                    for row in rows:
                        w.writerow(row)
            except:
                print ("Can't find table: [{0}]".format(table))
                    
    def choose_files(db,db_path):
            
        clear_screen()
        print ("Which tables do you want to write to CSV files? Enter done when you are finished.")
        print ("So far you have chosen: ")
        if not chosen_files and not chosen_files_joined:
            print ("(No tables chosen)")
        else:
            for f in chosen_files:
                print (f)
            for f in chosen_files_joined:
                print ("joined file: posts and {0}".format(f))
        print ("\n")
        print ("Choose from following tables: ")
        for k,v in sorted(temp_table_list.items()):
            print (k + " - " + v)
        for k,v in sorted(temp_table_joined_list.items()):
            print (k + " - post_info joined with "+ v)   
        
        answer = get_inp(">>> ") 
        while check_answer(answer,"13","14","done","0",*temp_table_list.keys()) == False:
            answer = get_inp(">>> ")
        
        if answer == "0":
            quit_interface()
        
        if answer == "done":
            
            print ("writing CSV-files...")
            path = db_path+"/CSV_files/"
            if not os.path.exists(path):
                os.makedirs(path)
            title = str(db).split('/')[-1].replace('.db','')
            conn = sqlite3.connect(db)
            
            #if True:
            try:
                write_csvs(title, path, conn, chosen_files)
                try:
                    write_joined_csvs(title, path, conn, chosen_files_joined)
                except:
                    pass
            except:
                print ("No data available...")
        
        elif answer in temp_table_joined_list:
            chosen_files_joined.append(temp_table_joined_list[answer])
            del temp_table_joined_list[answer]
            choose_files(db, db_path)    

        else:    
            chosen_files.append(temp_table_list[answer])
            del temp_table_list[answer]
            choose_files(db, db_path)
            
    
    choose_files(db, db_path)    
    

def make_gephi_files(db,db_path):
    try:
        import networkx as nx
    except:
        print ("you need networkx")
        sys.exit()
        
    network_choice = {"1":"Page Likes","2":"Posts and Likes","3":"Posts and Comments"}
    
    def make_page_likes(conn,title,path):
    
        g=nx.Graph()
        cur = conn.cursor()
        cur.execute("select PL.liked_page_name, PL.liked_page_id, PA.page_id from {0}page_likes_info PL, {0}page_info PA where PA.web_name = PL.web_name limit 10000000".format(title))
        for row in cur.fetchall():
            g.add_node(row[1], label=str(row[0]))
            g.add_edge(row[2], row[1])
        nx.write_gexf(g, path+'/{0}page_likes.gexf'.format(title))
        
    def make_post_likes(conn,title,path,start_date="",end_date=""):
        
        g=nx.Graph()
        cur = conn.cursor()
        if start_date:
            cur.execute("select P.id, PA.page_name, P.post_made_by_name from {0}post_info P, {0}page_info PA where PA.web_name = P.web_name and date(P.post_time_created) between date('{1}') and date('{2}')".format(title,start_date,end_date))
        else:
            cur.execute("select P.id, PA.page_name, P.post_made_by_name from {0}post_info P, {0}page_info PA where PA.web_name = P.web_name".format(title))
        for row in cur.fetchall():
            g.add_node(row[1],label=str(row[1]))
            g.add_node(row[0],label=str(row[2]))
            g.add_edge(row[0],row[1])
        
        if start_date:
            cur.execute("select L.post_like_by_id, L.post_like_by_name, P.id from {0}likes_info L, {0}post_info P, {0}page_info PA where L.post_id = P.id and PA.web_name = P.web_name and date(P.post_time_created) between date('{1}') and date('{2}')".format(title,start_date,end_date))
        else:
            cur.execute("select L.post_like_by_id, L.post_like_by_name, P.id from {0}likes_info L, {0}post_info P, {0}page_info PA where L.post_id = P.id and PA.web_name = P.web_name".format(title))
        for row in cur.fetchall():
            g.add_node(row[0], label=str(row[1]))
            g.add_edge(row[0], row[2])
        if start_date:
            nx.write_gexf(g, path+'/{0}post_likes_{1}_to_{2}.gexf'.format(title,start_date,end_date))
        else:
            nx.write_gexf(g, path+'/{0}post_likes.gexf'.format(title))
        
    def make_comments(conn,title,path,start_date="",end_date=""):
        
        g=nx.Graph()
        cur = conn.cursor()
        if start_date:
            cur.execute("select P.id, PA.page_name, P.post_made_by_name from {0}post_info P, {0}page_info PA where PA.web_name = P.web_name and date(P.post_time_created) between date('{1}') and date('{2}')".format(title,start_date,end_date))
        else:
            cur.execute("select P.id, PA.page_name, P.post_made_by_name from {0}post_info P, {0}page_info PA where PA.web_name = P.web_name".format(title))
        for row in cur.fetchall():
            g.add_node(row[1],label=str(row[1]))
            g.add_node(row[0],label=str(row[2]))
            g.add_edge(row[0],row[1])
        
        if start_date:
            cur.execute("select C.comment_made_by_id, C.comment_made_by_name, P.id from {0}comment_info C, {0}post_info P, {0}page_info PA where C.post_id = P.id and PA.web_name = P.web_name and date(P.post_time_created) between date('{1}') and date('{2}')".format(title,start_date,end_date))
        else:
            cur.execute("select C.comment_made_by_id, C.comment_made_by_name, P.id from {0}comment_info C, {0}post_info P, {0}page_info PA where C.post_id = P.id and PA.web_name = P.web_name".format(title))
        for row in cur.fetchall():
            g.add_node(row[0], label=str(row[1]))
            g.add_edge(row[0], row[2])
        if start_date:
            nx.write_gexf(g, path+'/{0}post_comments_{1}_to_{2}.gexf'.format(title,start_date,end_date))
        else:
            nx.write_gexf(g, path+'/{0}post_comments.gexf'.format(title))
    
    def choose_gephi_files(connection, title, path):
        
        clear_screen()
        print ("Choose the network you want to create. Enter 0 to quit.")
        for k,v in network_choice.items():
            print (k + ". " + v)
        print ("9. Make network from date range")
        
        answer = get_inp(">>> ") 
        while check_answer(answer,"0","9",*network_choice.keys()) == False:
            answer = get_inp(">>> ")
        
        if answer == "0":
            quit_interface()
        
        elif answer == "1":
            try:
                print ("writing Gephi files...")
                make_page_likes(connection,title, path)
            except:
                print ("No data available...")
        
        elif answer == "2":
            try:
                print ("writing Gephi files...")
                make_post_likes(connection, title, path)
            except:
                print ("No data available...")
                
        elif answer == "3":
            try:
                print ("writing Gephi files...")
                make_comments(connection, title, path)
            except:
                print ("No data available...")
        
        elif answer == "9":
            data_types = ""
            clear_screen()
            import analytics.pol_network as pn
            print ("What kind of network do you want?")
            print ("\n")
            #print ("1. All Interactions")
            print ("2. Posts and Likes")
            print ("3. Posts and Comments")
            answer = get_inp(">>> ")
            while check_answer(answer,"2","3") == False:
                answer = get_inp(">>> ")
            network_kind = answer
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
            if network_kind == '1': pass
            if network_kind == '2': make_post_likes(connection, title, path, start_date=start_date, end_date=end_date)
            if network_kind == '3': make_comments(connection, title, path, start_date=start_date, end_date=end_date)
            
    
    def gephi_make(db,path):
        if not os.path.exists(path):
            os.makedirs(path)
        title = str(db).split('/')[-1].replace('.db','')
        connection = sqlite3.connect(db)
        choose_gephi_files(connection, title, path)
        
        
    gephi_make(db,db_path+'/Gephi_files')

def find_page_like_network(args):
    
    unique_checker = {}

    def get_page_likes(page_likes_url,page_likes_data,page):
        
        page_likes = render_to_json(page_likes_url)
        if not page_likes:
            return []
        page_likes = page_likes['data']
        specific_page_id = render_to_json(page_likes_url.replace('likes',''))['id']
        if not str(specific_page_id) in unique_checker: page_likes_data.append(str(specific_page_id))
        for like in page_likes:
            if not str(like['id']) in unique_checker:
                page_likes_data.append(str(like['id']))
                unique_checker[str(like['id'])]=True
                try:
                    print (like['name'])
                except:
                    print ("Name not printable")
        
        return page_likes_data

    def find_network(args):
        pages_file = args[0]
        app_id = args[1]
        app_secret = args[2]
        outfolder = args[3]
        degree = int(args[4])
        page_list = []
        page_list2 = []
        page_list_final = []
        graph_url = "https://graph.facebook.com/v2.5/"
        page_reader = open(pages_file,'r')
        for p in page_reader.readlines():
            page_list.append(p.strip())
        
        for p in page_list:
            url = create_page_likes_url(graph_url, p, app_id, app_secret)
            page_list2 = get_page_likes(url, page_list2, p)
        
        if degree > 1:
            for p in page_list2:
                url = create_page_likes_url(graph_url, p, app_id, app_secret)
                page_list_final = get_page_likes(url, page_list_final, p)
        else:
            page_list_final = page_list2
            
        print (len(page_list_final))
        outfile = outfolder+'/'+str(pages_file).split("/")[-1].replace(".txt","")+"_with_["+str(degree)+"]_degree_extension"+".txt"
        with open(outfile,'w') as out:
            for p in page_list_final:
                out.write(p+'\n')

    find_network(args)
    


def main_collect(title_,coll_list_,collect_new_,update_new_,number_of_weeks_,app_id,app_secret,db_path,only_page_likes,make_count):
    
    title = title_
    coll_list = coll_list_
    connection = connect_db(db_path,title)
    cursor = connection.cursor()
    connection.commit()
    
    collect_new = collect_new_
    update_new = update_new_
    
    
    #simple data pull App Secret and App ID
    APP_SECRET = app_secret
    APP_ID = app_id
    
    #to find go to page's FB page, at the end of URL find username
    #e.g. http://facebook.com/walmart, walmart is the username
        
    url_list_infile = []
    infile = coll_list
    h=open(coll_list.strip(), "r")
    temp=h.readlines()
    for line in temp:
        try:
            print (line.strip())
            url_list_infile.append(str(line.strip()))
        except:
            pass
    list_companies = url_list_infile
    

    graph_url = "https://graph.facebook.com/v2.5/"
    
    #create db connection
    
    cursor.execute("CREATE  TABLE IF NOT EXISTS `{0}page_likes_info` (`liked_page_name` VARCHAR(200),`liked_page_id` VARCHAR(100), `main_category` VARCHAR(100),`sub_categories` TEXT,`web_name` VARCHAR(200),`id` INTEGER PRIMARY KEY AUTOINCREMENT);".format(title))
    cursor.execute("CREATE  TABLE IF NOT EXISTS `{0}page_info` (`page_id` VARCHAR(100),`page_name` VARCHAR(200), `category` VARCHAR(100), `country` VARCHAR(100), `city` VARCHAR(100), `latitude` FLOAT, `longitude` FLOAT, `cover_pic_link` VARCHAR(400), `page_description` TEXT, `page_username` VARCHAR(100), `page_email` VARCHAR(200), `page_like_count` INT,`talking_about` INT, `page_website` VARCHAR(200), `web_name` VARCHAR(200),`id` INTEGER PRIMARY KEY AUTOINCREMENT);".format(title))
    cursor.execute("CREATE  TABLE IF NOT EXISTS `{0}post_info` (`fb_post_id` VARCHAR(100), `post_made_by_id` VARCHAR(100), `post_made_by_name` VARCHAR(100), `shares` INT, `post_type` VARCHAR(50), `post_picture` TEXT, `post_time_created` DATETIME, `post_caption` VARCHAR(300),`post_description` LONGTEXT,`post_headline` LONGTEXT, `post_link` VARCHAR(400), `post_message` LONGTEXT, `web_name` VARCHAR(200),`page_id` VARCHAR(300),`id` INTEGER PRIMARY KEY AUTOINCREMENT);".format(title))

    
    #SQL statement for adding Facebook page data to database
    insert_info = ("INSERT INTO {0}page_info "
                    "(page_id, page_name ,category, country, city, latitude, longitude, cover_pic_link, page_description, page_username, page_email, talking_about, page_like_count, page_website, web_name)"
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)".format(title))
    
    insert_page_likes_info = ("INSERT INTO {0}page_likes_info "
                    "(liked_page_name, liked_page_id ,main_category, sub_categories, web_name)"
                    "VALUES (?, ?, ?, ?, ?)".format(title))
    
    #SQL statement for adding post data                
    insert_posts = ("INSERT INTO {0}post_info "
                    "(fb_post_id, post_made_by_id, post_made_by_name, shares, post_type, post_picture, post_time_created, post_caption, post_description, post_headline, post_link, post_message,web_name ,page_id)"
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)".format(title))
    
    #SQL statement for adding comment data
    insert_comments = ("INSERT INTO {0}comment_info "
                       "(comment_id, comment_message, comment_like_count, comment_time_created, comment_made_by_id, comment_made_by_name, post_id)"
                       "VALUES (?, ?, ?, ?, ?, ?, ?)".format(title))
    
    insert_likes = ("INSERT INTO {0}likes_info "
                       "(post_like_by_id, post_like_by_name, post_id)"
                       "VALUES (?, ?, ?)".format(title))
    
    
    insert_replies = ("INSERT INTO {0}replies_info "
                       "(reply_id, reply_message, reply_like_count, reply_time_created, reply_made_by_id, reply_made_by_name, reply_made_to_id, reply_made_to_name, comment_id)"
                       "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)").format(title)
    
    insert_comment_likes = ("INSERT INTO {0}comment_likes_info "
                       "(comment_like_by_id, comment_like_by_name, comment_like_to_id, comment_like_to_name, comment_id)"
                       "VALUES (?, ?, ?, ?, ?)").format(title)
    
    insert_comment_tags = ("INSERT INTO {0}comment_tags_info "
                       "(tagged_id, tagged_name, type, tag_made_by_id, tag_made_by_name, comment_id)"
                       "VALUES (?, ?, ?, ?, ?, ?)").format(title)
                       
    insert_reply_tags = ("INSERT INTO {0}reply_tags_info "
                       "(tagged_id, tagged_name, type, tag_made_by_id, tag_made_by_name ,reply_id)"
                       "VALUES (?, ?, ?, ?, ?, ?)").format(title)
    
    insert_reply_likes = ("INSERT INTO {0}reply_likes_info "
                       "(reply_like_by_id, reply_like_by_name, reply_like_to_id, reply_like_to_name, reply_id)"
                       "VALUES (?, ?, ?, ?, ?)").format(title)
                                              
    insert_temp = ("INSERT INTO {0}temp_used_comment_id "
                       "(comment_id)"
                       "VALUES (?)").format(title)
                       
    last_last_crawl = datetime.datetime.now()
    
    for company in list_companies:
        print (company)
        first_run = False
        #make graph api url with company username
        current_page = graph_url + company
        
        #open public page in facebook graph api
        
        count = 0
        cursor.execute('select count(*) from {0}post_info where web_name = "{1}"'.format(title,company))
        countlist = cursor.fetchone()
        for i in countlist:
            count = i
        count = int(count)
        if count != 0:
            cursor.execute('select MIN(post_time_created) from {0}post_info where web_name = "{1}"'.format(title,company))
            countlist = cursor.fetchone()
            for i in countlist:
                nowDate = str(i)
                
            nowDate = datetime.datetime.strptime(nowDate,'%Y-%m-%d %H:%M:%S')
            nowDate = nowDate - datetime.timedelta(days=1)
            first_crawl = nowDate
            startdate = first_crawl
            startdate += datetime.timedelta(days=1)
            startdate = startdate.isoformat()
            first_crawl = nowDate.isoformat()
        else:
            nowDate = datetime.datetime.now()
            first_crawl = nowDate
            startdate = first_crawl
            two_less_newest_date =  startdate - datetime.timedelta(days=5)
            startdate += datetime.timedelta(days=1)
            startdate = startdate.isoformat()
            first_crawl = nowDate.isoformat()
            first_run = True
        
        #print nowDate
        #the time of last weeks crawl
        last_crawl = nowDate - datetime.timedelta(weeks=number_of_weeks_)
        crawl_loop = False
        while crawl_loop == False: 
            #print last_crawl > (last_last_crawl - datetime.timedelta(days=1))
            if last_crawl > (last_last_crawl - datetime.timedelta(days=1)):
                last_crawl = last_crawl - datetime.timedelta(weeks=number_of_weeks_)
                
            else:
                crawl_loop = True
                             
        last_crawl = last_crawl.isoformat()
        if nowDate < last_last_crawl:
            last_last_crawl = nowDate
        else:
            pass
        
        
        if update_new == True:
            #cursor.execute("select P2.fb_post_id, P2.id from {0}post_info P2, (select max(P.time_created) as T from {0}post_info P where P.web_name = '{1}') as SUB where P2.web_name = '{1}' and P2.time_created > subdate(SUB.T, INTERVAL 1 DAY) order by P2.time_created desc limit 100000000".format(title,company))
            cursor.execute("select distinct P.fb_post_id, P2.id from {0}newest_post_info P, {0}post_info P2 where P2.fb_post_id = P.fb_post_id and P.web_name = '{1}'".format(title,company))
            
            for r in cursor.fetchall():
                
                comment_data = []
                likes_data = []
                comment_like_data = []
                reply_data = []
                reply_like_data = []
                comment_tag_data = []
                reply_tag_data = []
                next_page_bool = False
                #capture post id of data just inserted
        
                comment_url = create_comments_url(graph_url, str(r[0]), APP_ID, APP_SECRET)
                comments = get_comments_data(comment_url, comment_data, comment_like_data, reply_data, reply_like_data, comment_tag_data, reply_tag_data, str(r[1]), next_page_bool, title, connection,graph_url, APP_ID, APP_SECRET, False, str(r[0]))
                likes_url = create_likes_url(graph_url, str(r[0]), APP_ID, APP_SECRET)
                likes = get_likes_data(likes_url, likes_data, str(r[1]),title, connection)
                
                #insert comments
                new_comment_set = {}
                new_likes_set = {}
                new_comment_like_set = {}
                new_reply_set = {}
                new_reply_like_set = {}
                new_comment_tag_set = {}
                new_reply_tag_set = {}
                cursor.execute('select C.comment_id from {0}newest_comment_info C where C.fb_post_id = "{1}"'.format(title,str(r[0])))
                for row in cursor.fetchall():
                    new_comment_set[str(row[0])] = True
                cursor.execute('select C.post_like_by_id from {0}newest_likes_info C where C.fb_post_id = "{1}"'.format(title,str(r[0])))
                for row in cursor.fetchall():
                    new_likes_set[str(row[0])] = True
                cursor.execute('select C.comment_like_by_id from {0}newest_comment_likes_info C where C.fb_post_id = "{1}"'.format(title,str(r[0])))
                for row in cursor.fetchall():
                    new_comment_like_set[str(row[0])] = True
                cursor.execute('select C.reply_id from {0}newest_replies_info C where C.fb_post_id = "{1}"'.format(title,str(r[0])))
                for row in cursor.fetchall():
                    new_reply_set[str(row[0])] = True
                cursor.execute('select C.reply_like_by_id from {0}newest_reply_likes_info C where C.fb_post_id = "{1}"'.format(title,str(r[0])))
                for row in cursor.fetchall():
                    new_reply_like_set[str(row[0])] = True
                cursor.execute('select C.tagged_id from {0}newest_comment_tags_info C where C.fb_post_id = "{1}"'.format(title,str(r[0])))
                for row in cursor.fetchall():
                    new_comment_tag_set[str(row[0])] = True
                cursor.execute('select C.tagged_id from {0}newest_reply_tags_info C where C.fb_post_id = "{1}"'.format(title,str(r[0])))
                for row in cursor.fetchall():
                    new_reply_tag_set[str(row[0])] = True

                new_likes_count = 0
                new_comment_count = 0
                new_comment_like_count = 0
                new_reply_count = 0
                new_reply_like_count = 0
                new_comment_tag_count = 0
                new_reply_tag_count = 0
                for comment in comments[0]:
                   
                    if str(comment[0]) not in new_comment_set:
                        try:
                            new_comment_count+=1
                            cursor.execute(insert_comments, comment)
                            
                        except:
                            print ('insertion error....')
                    else:
                        pass
                
                for like in likes:
                    if str(like[0]) not in new_likes_set:
                        try:
                            new_likes_count+=1
                            cursor.execute(insert_likes, like)
                        except:
                            print ('insertion error....')
                    else:
                        pass
                
                for comment in comments[1]:
                    if str(comment[0]) not in new_comment_like_set:
                        try:
                            new_comment_like_count+=1
                            cursor.execute(insert_comment_likes, comment)
                            
                        except:
                            print ('insertion error....')
                    else:
                        pass
                
                for comment in comments[2]:
                    if str(comment[0]) not in new_reply_set:
                        try:
                            new_reply_count+=1
                            cursor.execute(insert_replies, comment)
                            
                        except:
                            print ('insertion error....')
                    else:
                        pass
                    
                for comment in comments[3]:
                    if str(comment[0]) not in new_reply_like_set:
                        try:
                            new_reply_like_count+=1
                            cursor.execute(insert_reply_likes, comment)
                            
                        except:
                            print ('insertion error....')
                    else:
                        pass
                    
                for comment in comments[4]:
                    if str(comment[0]) not in new_comment_tag_set:
                        try:
                            new_comment_tag_count+=1
                            cursor.execute(insert_comment_tags, comment)
                            
                        except:
                            print ('insertion error....')
                    else:
                        pass
                    
                for comment in comments[5]:
                    if str(comment[0]) not in new_reply_tag_set:
                        try:
                            new_reply_tag_count+=1
                            cursor.execute(insert_reply_tags, comment)
                            
                        except:
                            print ('insertion error....')
                    else:
                        pass
                
                update_newest_posts(title,str(r[0]),likes,comments[0],comments[1],comments[2],comments[3],comments[4],comments[5],connection)
                print(str(r[1])+" number of new comments: "+str(new_comment_count)+" and new likes: "+str(new_likes_count)+" and new comment_likes: "+str(new_comment_like_count)+" and new replies: "+str(new_reply_count)+" and new reply_likes: "+str(new_reply_like_count)+" and new comment_tags: "+str(new_comment_tag_count)+" and new reply_tags: "+str(new_reply_tag_count))
        
        
        if collect_new == True:
            
            cursor.execute('select MAX(post_time_created) from {0}post_info where web_name = "{1}"'.format(title,company))
            for i in cursor.fetchall():
                last_crawl = str(i[0])
            try:
                last_crawl = datetime.datetime.strptime(last_crawl,'%Y-%m-%d %H:%M:%S')
                last_crawl = last_crawl.isoformat()   
                startdate = datetime.datetime.now()
                first_crawl = startdate
                first_crawl = first_crawl.isoformat()
                two_less_newest_date =  startdate - datetime.timedelta(days=5)
                startdate += datetime.timedelta(days=1)
                startdate = startdate.isoformat()
            except:
                print ("NO DATABASE READ")
            
        #insert the data we pulled into db
        cursor.execute("select web_name from {0}page_info where web_name='{1}'".format(title,company))
        if len(cursor.fetchall()) < 1:
            try:
                page_url = current_page + '?' + "key=value&access_token=" + APP_ID + "|" + APP_SECRET
                if render_to_json(page_url)['privacy'] == 'OPEN':
                    page_url = current_page + '?' + "fields=id,name,cover,description&key=value&access_token=" + APP_ID + "|" + APP_SECRET
                    json_fbpage = render_to_json(page_url)
                else:
                    page_url = current_page + '?' + "fields=id,name,category,location,cover,description,username,emails,talking_about_count,likes,website&key=value&access_token=" + APP_ID + "|" + APP_SECRET
                    json_fbpage = render_to_json(page_url)

            except:        
                page_url = current_page + '?' + "fields=id,name,category,location,cover,description,username,emails,talking_about_count,likes,website&key=value&access_token=" + APP_ID + "|" + APP_SECRET
                json_fbpage = render_to_json(page_url)
                
            if not json_fbpage: continue
            print (page_url)
        
            #gather our page level JSON Data
            page_data = [try_json_str(json_fbpage, ["id"]), try_json_str(json_fbpage, ["name"]), try_json_str(json_fbpage, ["category"]), try_json_str(json_fbpage, ["location","country"]), try_json_str(json_fbpage, ["location","city"]), try_json_float(json_fbpage, ["location","latitude"]), try_json_float(json_fbpage, ["location","longitude"]), try_json_str(json_fbpage, ["cover","source"]), try_json_str(json_fbpage, ["description"]), try_json_str(json_fbpage, ["username"]), try_json_list(json_fbpage, ["emails"],0), try_json_int(json_fbpage, ["talking_about_count"]), try_json_int(json_fbpage, ["likes"]), try_json_str(json_fbpage, ["website"]), company]
            
            cursor.execute(insert_info, page_data)
            page_likes_data = get_page_likes(create_page_likes_url(graph_url, company, APP_ID, APP_SECRET), [], company)
            if not page_likes_data: continue
            for page_like in page_likes_data:
                cursor.execute(insert_page_likes_info,page_like)
            
            last_key = cursor.lastrowid
            connection.commit()
        else:
            cursor.execute('select count(id) from {0}page_info where web_name = "{1}"'.format(title,company))
            keylist = cursor.fetchone()
            for i in keylist:
                key = int(i)
            last_key = key
        #grab primary key
        
        if not only_page_likes == 'True':
            cursor.execute("CREATE  TABLE IF NOT EXISTS `{0}replies_info` (`reply_id` VARCHAR(100),`reply_message` LONGTEXT,`reply_like_count` INT,`reply_time_created` DATETIME, `reply_made_by_id` VARCHAR(200), `reply_made_by_name` VARCHAR(200), `reply_made_to_id` VARCHAR(200), `reply_made_to_name` VARCHAR(200),  `comment_id` VARCHAR(300),`id` INTEGER PRIMARY KEY AUTOINCREMENT );".format(title))
            cursor.execute("CREATE  TABLE IF NOT EXISTS `{0}comment_likes_info` (`comment_like_by_id` VARCHAR(200), `comment_like_by_name` VARCHAR(200), `comment_like_to_id` VARCHAR(200), `comment_like_to_name` VARCHAR(200),`comment_id` VARCHAR(300),`id` INTEGER PRIMARY KEY AUTOINCREMENT);".format(title))
            cursor.execute("CREATE  TABLE IF NOT EXISTS `{0}reply_likes_info` (`reply_like_by_id` VARCHAR(200), `reply_like_by_name` VARCHAR(200),`reply_like_to_id` VARCHAR(200), `reply_like_to_name` VARCHAR(200), `reply_id` VARCHAR(300),`id` INTEGER PRIMARY KEY AUTOINCREMENT);".format(title))
            cursor.execute("CREATE  TABLE IF NOT EXISTS `{0}comment_tags_info` (`tagged_id` VARCHAR(200), `tagged_name` VARCHAR(200), `type` VARCHAR(50), `tag_made_by_id` VARCHAR(200), `tag_made_by_name` VARCHAR(200), `comment_id` VARCHAR(300),`id` INTEGER PRIMARY KEY AUTOINCREMENT);".format(title))
            cursor.execute("CREATE  TABLE IF NOT EXISTS `{0}reply_tags_info` (`tagged_id` VARCHAR(200), `tagged_name` VARCHAR(200), `type` VARCHAR(50), `tag_made_by_id` VARCHAR(200), `tag_made_by_name` VARCHAR(200), `reply_id` VARCHAR(300),`id` INTEGER PRIMARY KEY AUTOINCREMENT);".format(title))
            cursor.execute("CREATE  TABLE IF NOT EXISTS `{0}temp_used_comment_id` (`comment_id` VARCHAR(300),`id` INTEGER PRIMARY KEY AUTOINCREMENT);".format(title))
            cursor.execute("CREATE  TABLE IF NOT EXISTS `{0}comment_info` (`comment_id` VARCHAR(100),`comment_message` LONGTEXT,`comment_like_count` INT,`comment_time_created` DATETIME,`comment_made_by_id` VARCHAR(200),`comment_made_by_name` VARCHAR(200),`post_id` VARCHAR(300),`id` INTEGER PRIMARY KEY AUTOINCREMENT);".format(title))
            cursor.execute("CREATE  TABLE IF NOT EXISTS `{0}likes_info` (`post_like_by_id` VARCHAR(200),`post_like_by_name` VARCHAR(200),`post_id` VARCHAR(300),`id` INTEGER PRIMARY KEY AUTOINCREMENT);".format(title))
            
            cursor.execute("CREATE  TABLE IF NOT EXISTS `{0}missed_post_id` (`post_id` VARCHAR(300),`id` INTEGER PRIMARY KEY AUTOINCREMENT);".format(title))
            create_indeces(connection, title)
    
            #extract post data
            post_url = create_post_url(current_page,startdate,last_crawl, APP_ID, APP_SECRET)

            post_data = []
            post_data = scrape_posts_by_date(post_url, last_crawl, first_crawl, post_data, APP_ID, APP_SECRET)
            
            comment_data = []
            #loop through and insert data
            for post in post_data:
                post.append(company)
                post.append(last_key)
                try:
                    cursor.execute(insert_posts, post)
                except:
                    print ('posts insertion error....')
                comment_data = []
                likes_data = []
                comment_like_data = []
                reply_data = []
                reply_like_data = []
                comment_tag_data = []
                reply_tag_data = []
                #capture post id of data just inserted
                post_key = cursor.lastrowid
                next_page_bool = False
                comment_url = create_comments_url(graph_url, post[0], APP_ID, APP_SECRET)
                comments = get_comments_data(comment_url, comment_data, comment_like_data, reply_data, reply_like_data, comment_tag_data, reply_tag_data, post_key, next_page_bool,title, connection,graph_url, APP_ID, APP_SECRET, False, post[0])
                likes_url = create_likes_url(graph_url, post[0], APP_ID, APP_SECRET)
                likes = get_likes_data(likes_url, likes_data, post_key, title, connection)
                try:
                    print (str(post_key) + " number of comments: " + str(len(comments[0])) + " likes: " + str(len(likes)) + " comment_likes: " + str(len(comments[1])) + " replies: " + str(len(comments[2])) + " reply_likes: " + str(len(comments[3])) + " tags: " + str(len(comments[4])+len(comments[5])))
                except:
                    print ("Some error....")
                #insert comments
                for comment in comments[0]:

                    try:
                        cursor.execute(insert_comments, comment)
                    except:
                        print ('comments insertion error....')
                        
                for comment_like in comments[1]:
                    
                    try:
                        cursor.execute(insert_comment_likes, comment_like)
                    except:
                        print ('comment_likes insertion error....')
                
                for reply in comments[2]:
                    
                    try:
                        cursor.execute(insert_replies, reply)
                    except:
                        print ('replies insertion error....')
                        
                for reply_like in comments[3]:
                    
                    try:
                        cursor.execute(insert_reply_likes, reply_like)
                    except:
                        print ('reply_likes insertion error....')
                        
                for tag in comments[4]:
                    
                    try:
                        cursor.execute(insert_comment_tags, tag)
                    except:
                        print ('comment_tags insertion error....')
                        
                for tag in comments[5]:
                    
                    try:
                        cursor.execute(insert_reply_tags, tag)
                    except:
                        print ('reply_tags insertion error....')
                
                for like in likes:
                    try:
                        cursor.execute(insert_likes, like)
                    except:
                        print ('likes insertion error....')
                    
                if collect_new == True or first_run == True:
                    newest_date = datetime.datetime.strptime(post[6],'%Y-%m-%d %H:%M:%S')
                    if newest_date > two_less_newest_date:
                        write_newest_posts(title,two_less_newest_date,company,post,likes,comments[0],comments[1],comments[2],comments[3],comments[4],comments[5],connection)
                        
                
                
                connection.commit()
                
            #commit the data to the db
                
            
        else:
            pass
    create_indeces(connection, title)
    if only_page_likes != 'True':
        if make_count == 'True':
            print ("Making with_count tables...")
            make_count_tables(title, connection)
        
    connection.close()
    

def check_date_answer(answer):
    try:
        nd = datetime.datetime.strptime(str(answer),'%Y-%m-%d')
        return True
    except:
        print ("Please enter a valid answer")
        return False

def print_db_log(path_,title):
    
    infile = r''+path_+'/'+title+'.txt'
    if os.path.isfile(infile):
        h=open(infile,'a')
        h.write('\n'+str(title)+'\t'+'last run: '+str(datetime.datetime.now()))
    else:
        new_file = r''+path_+'/'+title+'.txt'
        h=open(new_file,'w')
        h.write(str(title)+'\t'+'last run: '+str(datetime.datetime.now()))

def create_new_db_list(path_,db_title,db_list_name,app_id,app_secret,only,make,project):
    
    infile = r''+path_+'/'+db_title+'.txt'
    
    new_file = r''+path_+'/'+db_title+'.txt'
    h=open(new_file,'w')
    h.write(project+"\n")
    h.write(db_list_name)
    h.write(app_id)
    h.write(app_secret)
    h.write(only)
    h.write(make)
        
    
def check_page_list(path_,db_list_name):
    
    infile = r''+path_+'/'+db_list_name+'.txt'
    #print (infile)
    if os.path.isfile(infile):
        return True
    else:
        return False

def check_answer(answer,*args):
    
    
    for arg in list(args):
       
        if str(answer) == str(arg):
            return True
        
    print ("Please enter a valid answer")
    return False
        

def quit_interface():
    clear_screen()
    print ("Bye Bye!")
    quit()
    
def read_project(path_):
    
    app_id = ""
    app_secret = ""
    page_list = ""
    only_page_likes = ""
    make_count = ""
    
    with open(path_+'.txt',"r") as readfile:
        app_id = readfile.readline().split('=')[1]
        app_secret = readfile.readline().split('=')[1]
        page_list = readfile.readline().split('=')[1]
        only_page_likes = readfile.readline().split('=')[1]
        make_count = readfile.readline().split('=')[1]
    
    return app_id,app_secret,page_list,only_page_likes,make_count

def create_project_example(path_):
    
    with open(path_+"/Projects/project_example.txt","w") as pwrite:
        pwrite.write("App_id=yourAppId"+"\n")
        pwrite.write("App_secret=yourAppId"+"\n")
        pwrite.write("Path_to_page_list="+path_+"/Page Lists/list_example.txt"+"\n")
        pwrite.write("Scrape_only_pages_liked_by_page=True/False"+"\n")
        pwrite.write("Make_with_count_tables=True/False")
        
    page_list_temp = open(path_+"/Page Lists/list_example.txt","w")
    page_list_temp.write('')

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

def menu_interface(main_path):
    
    path_ = main_path
    FBC = '/FBC_databases'
    crawl_logs = '/DB'
    pro_lists = '/Projects'
    page_lists = '/Page Lists'
    analytics = '/analytics'
    if not os.path.exists(path_+analytics):
        os.makedirs(path_+analytics)
    if not os.path.exists(path_+crawl_logs):
        os.makedirs(path_+crawl_logs)
    if not os.path.exists(path_+FBC):
        os.makedirs(path_+FBC)
    if not os.path.exists(path_+pro_lists):
        os.makedirs(path_+pro_lists)
    if not os.path.exists(path_+page_lists):
        os.makedirs(path_+page_lists)
        create_project_example(path_)
        
    collect_new = True
    update_new = True
    number_of_weeks = 1 # Only for collecting old data (collecting back through time)
    
    noise_string = "******************************"
    
    clear_screen()
    print ("\n")
    print (noise_string+"Welcome to the Ethos Facebook Collector"+noise_string)
    print ("\n")
    print ("What do you want to do?")
    print ("1. Create new data collection")
    print ("2. Use existing data collection")
    print ("3. Delete data collection")
    print ("4. Go to Analytics (Buggy Mode)")
    print ("0. Quit program")

    answer = get_inp(">>> ")
    while check_answer(answer,"1","2","3","4","0") == False:
        answer = get_inp(">>> ")
    clear_screen()
    
    if answer == "1":
        print ("What title do you want for your data collection?")
        print ("Must end with '_'")
        print ("Example: 'NEWS_'")
        templist = []
        for db in listdir(r''+path_+FBC):
            templist.append(db.replace(".txt",""))
        answer = get_inp(">>> ")
        if answer not in templist:
            while check_answer(answer[-1:],'_') == False:
                answer = get_inp(">>> ")
        else:
            print ("Already exists in database!")
            answer = get_inp("")
            menu_interface(main_path)
        db_title = answer
        clear_screen()
        print ("Are you sure you want "+db_title+" to be your data collection title? y/n")
        answer = get_inp(">>> ")
        while check_answer(answer.lower(),"y","n") == False:
            answer = get_inp(">>> ")
        clear_screen()
        if answer.lower() == 'y':
            print ("List of available projects: "+"\n")
            for project in listdir(path_+pro_lists):
                if project.endswith(".txt"): print (str(project).replace(".txt",""))
            print ("\n")
            print ("What is the .txt file containing the project details? type without '.txt' ending")
            answer = get_inp(">>> ")
            while check_page_list(path_+pro_lists,answer) == False:          
                print ("Please enter a valid answer")
                answer = get_inp(">>> ")
            clear_screen()
            app_id,app_secret,db_list_name,only,make = read_project(path_+pro_lists+'/'+answer)
            create_new_db_list(path_+FBC,db_title, db_list_name,app_id,app_secret,only,make,path_+pro_lists+'/'+answer)
            print ("A new data collection has now been created!")
            #print ("\n")
            print (db_title)
            answer = get_inp("Press any key to continue")
            menu_interface(main_path)
        else:
            menu_interface(main_path)
            
    elif answer == "2":
        clear_screen()
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
        clear_screen()
        db_title = answer
        db_file = open(r''+path_+FBC+'/'+db_title+'.txt',"r")
        project_title = db_file.readline().strip()
        app_id,app_secret,db_list_name,only,make = read_project(project_title)
        create_new_db_list(path_+FBC,db_title, db_list_name,app_id,app_secret,only,make,project_title)
        time.sleep(0.3)
        db_file = open(r''+path_+FBC+'/'+db_title+'.txt',"r")
        project_title = db_file.readline().strip()
        db_list_name = db_file.readline().strip()
        app_id = db_file.readline().strip()
        app_secret = db_file.readline().strip()
        only_page_likes = db_file.readline().strip()
        make_count = db_file.readline().strip()
        print ("You have chosen the data collection: "+db_title)
        print ("\n")
        print ("What do you want to do?")
        print ("1. Update collection with newest data")
        print ("2. Collect older data")
        print ("3. Make CSV files")
        print ("4. Make Gephi files (must have plugin module installed)")
        print ("5. Create extended page list from page likes")
        print ("0. Quit program")
        answer = get_inp(">>> ")
        while check_answer(answer,"1","2","3","4","5","0") == False:
            answer = get_inp(">>> ")
        clear_screen()
        
        if answer == "0":
            quit_interface()
        
        elif answer == "1":
            
            connection = connect_db(path_+crawl_logs,db_title)
            cur = connection.cursor()
            try:
                cur.execute("select post_time_created from {0}post_info".format(db_title))
                num_tuples = len(cur.fetchall())
            except:
                num_tuples = 0
            if not num_tuples > 0:
                print ("You must choose a data collection with some data in order to update it")
                answer = get_inp("Press any key to continue")
                menu_interface(main_path)
            
                
            collect_new = True
            update_new = True
            
            print ("Update new data on data collection: "+db_title)
            print ("\n")
            print ("Commence? y/n")
            answer = get_inp(">>> ")
            while check_answer(answer,"y","n") == False:
                answer = get_inp(">>> ")
            if answer == "y":
                title_ = '{0}'.format(db_title)
                coll_list = r'{0}'.format(db_list_name)                
                clear_screen()
                main_collect(title_, coll_list, collect_new, update_new, 1,app_id,app_secret,path_+crawl_logs,only_page_likes,make_count)
                answer = get_inp("Press any key to continue")
                menu_interface(main_path)
            else:
                menu_interface(main_path)
            
        elif answer == "2":
            collect_new = False
            update_new = False
            
            print ("Collection of older data starts from oldests collected date and goes back in time")
            print ("If no previous data has been collected, collection starts from today")
            print ("\n")
            print ("Type the number of weeks you wish to go back in time. Max 52 weeks.")
            answer = get_inp(">>> ")
            while check_answer(answer,*range(53)) == False:
                answer = get_inp(">>> ")
            clear_screen()
            number_of_weeks = int(answer)
            print ("Collect old data on data collection: "+db_title)
            print ("\n")
            print ("number of weeks: "+str(number_of_weeks))
            print ("\n")
            print ("Commence? y/n")
            answer = get_inp(">>> ")
            while check_answer(answer,"y","n") == False:
                answer = get_inp(">>> ")
            if answer == "y":
                title_ = '{0}'.format(db_title)
                coll_list = r'{0}'.format(db_list_name)                
                clear_screen()
                print (coll_list)
                main_collect(title_, coll_list, collect_new, update_new, number_of_weeks,app_id,app_secret,path_+crawl_logs,only_page_likes,make_count)
                print ("Collection done!")
                answer = get_inp("Press any key to continue")
                menu_interface(main_path)
            else:
                menu_interface(main_path)
        
        elif answer == "3":
            
            make_CSV_files(path_+crawl_logs+'/'+db_title+'.db',path_)
            print ("CSV-files have been made!")
            answer = get_inp("Press any key to continue")
            menu_interface(main_path)
               
        elif answer == "4":
            
            make_gephi_files(path_+crawl_logs+'/'+db_title+'.db',path_)
            print ("Gephi files have been made!")
            answer = get_inp("Press any key to continue")
            menu_interface(main_path)
        
        elif answer == "5":
            
            print ("Do you want to create list of pages from page likes with a distance of 1 or 2 degrees? Enter 0 to quit")
            answer = get_inp(">>> ")
            if answer =='0':
                quit_interface()
            while check_answer(answer,"1","2") == False:
                answer = get_inp(">>> ")
            find_page_like_network([db_list_name,app_id,app_secret,path_+page_lists,int(answer)])
            print ("Collection done!")
            answer = get_inp("Press any key to continue")
            menu_interface(main_path)

    elif answer == "3":
        clear_screen()
        templist = []
        print ("List of data collections: ")
        for db in listdir(r''+path_+FBC):
            if db.endswith(".txt"): print (db.replace(".txt",""))
            templist.append(db.replace(".txt",""))
        print ("\n")
        print ("Type the exact name of the data collection you wish to delete")
        answer = get_inp(">>> ")
        while check_answer(answer,*templist) == False:
            answer = get_inp(">>> ")
        col_for_deletion = answer
        clear_screen()
        print ("Are you sure you want to delete {0}? y/n".format(col_for_deletion))
        answer = get_inp(">>> ")
        while check_answer(answer,"y","n") == False:
            answer = get_inp(">>> ")
        if answer == "y":
            if os.path.exists(path_+crawl_logs+"/"+col_for_deletion+'.db'):
                os.remove(path_+crawl_logs+"/"+col_for_deletion+'.db')
            if os.path.exists(path_+FBC+"/"+col_for_deletion+'.txt'):
                os.remove(path_+FBC+"/"+col_for_deletion+'.txt')
            print ("Project deleted")
            answer = get_inp("Press any key to continue")
            menu_interface(main_path)
        else:
            menu_interface(main_path)
        
    elif answer == "4":
        from analytics import analytics_main as analytics
        analytics.analytics_menu(path_)
        
    elif answer == "0":
        quit_interface()
            
            
def main(argv):
    args = argv
    if len(args) > 1:
        menu_interface(args[1])
    else:
        path_ = str(os.path.abspath(os.path.dirname(__file__)))
        menu_interface(path_)  

if __name__ == "__main__":
    main(sys.argv)

