import sys
import os
import datetime
import numpy as np
import matplotlib.pyplot as plt
from collections import OrderedDict
from analytics import analytics_main

def get_data(conn,db):
    
    likes = {}
    comments = {}
    shares = {}
    
    cur = conn.cursor()
    cur.execute("select P.post_time_created, count(L.id) from {0}post_info P, {0}likes_info L where L.post_id = P.id group by P.post_time_created order by P.post_time_created".format(db))
    for row in cur.fetchall():
        likes[datetime.datetime.strptime(str(row[0]),'%Y-%m-%d %H:%M:%S')]=int(row[1])
        
    cur.execute("select P.post_time_created, count(C.id) from {0}post_info P, {0}comment_info C where C.post_id = P.id group by P.post_time_created order by P.post_time_created".format(db))
    for row in cur.fetchall():
        comments[datetime.datetime.strptime(str(row[0]),'%Y-%m-%d %H:%M:%S')]=int(row[1])
        
    cur.execute("select P.post_time_created, shares from {0}post_info P group by P.post_time_created order by P.post_time_created".format(db))
    for row in cur.fetchall():
        shares[datetime.datetime.strptime(str(row[0]),'%Y-%m-%d %H:%M:%S')]=int(row[1])
    
    return likes, comments, shares

def make_plot(conn, db):
    
    likes, comments, shares = get_data(conn,db)
    likes = OrderedDict(sorted(likes.items()))
    comments = OrderedDict(sorted(comments.items()))
    shares = OrderedDict(sorted(shares.items()))
    fig = plt.figure(figsize=(17,8))
    like_plot = plt.plot(list(likes.keys()), list(likes.values()), c='r', label="Post Likes")
    comm_plot = plt.plot(list(comments.keys()), list(comments.values()), c='b',label="Comments")
    share_plot = plt.plot(list(shares.keys()), list(shares.values()), c='y', label="Shares")
    #plt.legend( (like_plot, comm_plot, share_plot), ('Post Likes', 'Comments', 'Shares') )
    plt.legend(loc='upper left',ncol=2)
    plt.show()

def create_activity_plot(conn,db, path_):
    
    make_plot(conn, db)
    analytics_main.analytics_start_menu(conn, db, path_)
    
    
    
    