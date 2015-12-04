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
            self._cur.execute("select C.by_id, C.by_name from {0}post_info P, {0}{2}_info C where P.id = {1} and C.post_id = P.id limit 341324234".format(schema,self._post_id,type_))
        elif type_ == 'comment':
            self._cur.execute("select C.by_id, C.by_name from {0}post_info P, {0}{2}_info C where P.id = {1} and C.post_id = P.id union select R.by_id, R.by_name from {0}post_info P, {0}{2}_info C, {0}replies_info R where P.id = {1} and C.post_id = P.id and C.comment_id = R.comment_id limit 341324234".format(schema,self._post_id,type_))
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
        for k,v in self._total_count.iteritems():
            hu += v
        for k,v in self._total_count.iteritems():
    
            #print str(k) + " : " + str(v/float(hu)*100)
            return_set[str(k)]=v/float(hu)*100
            zup += (v/float(hu)*100)
        #print str(hu-0.1) +" out of " + str(self._total_bids_parsed)
        
        return return_set
    
    
    def print_total_count(self):
        
        hu = 0.1
        zup = 0
        for k,v in self._total_count.iteritems():
            hu += v
        for k,v in self._total_count.iteritems():
    
            print (str(k) + " : " + str(v/float(hu)*100))
        
            zup += (v/float(hu)*100)
        print (str(hu-0.1) +" out of " + str(self._total_bids_parsed))