# from string_utils import BATSMEN,BOWLING,TARGET,EXTRAS,\
# 	HOW_MANY_RUNS,SCORED,HOW_DID,GET_OUT,HOW_MANY_WICKETS,PICK,\
# 	MOST_RUNS,MOST_WICKETS, HOW_MANY_FOURS, HIT, HOW_MANY_SIX,\
# 	HOW_MANY_WIDES, BOWLED, FOW, WHEN_DID, AND,WWOSW,TTO,\
# 	DROP_CATCHES, DROPPED_BY, AT, INNINGS, DROPPED,ND, \
# 	MOM, TO,POM, MOMC, FOURS_COMM, SIXES_COMM,WICKETS_COMM, SUMMARY, \
# 	INNINGSC,MATCH_DETAILS,TOTAL, FINAL_SCORES,TOSS,WWT,PTS,WWM, \
# 	LOC,SCORE,LEAST_RUNS,PP, BS,DNB, SL,MATCH_DETAILS,PPS,CAPTAIN, \
# 	EXTRAS, EX,CONCEDE, BOS, LOS,NA,NO,NOA,DB,WBF, WBLF,TEAM,DB2,\
# 	ECN, ECO

import spacy
nlp = spacy.load("en_core_web_sm")

def generate_qna(question_str,answer_str):
	dict_ = dict()
	dict_["question"] = question_str
	# if NO in answer_str:
	# 	dict_["answer"] = NOA
	# 	return dict_
	if answer_str == '\n':
		dict_["answer"] = NA
	if answer_str is None:
		dict_["answer"] = NA
	if answer_str == '' or answer_str == ' ':
		dict_["answer"] = NA
	else:
		dict_["answer"] = answer_str
	return dict_
def get_how_out(data,team_1):
    scores = {}
    result = dict()
    
    data_len = len(data)
    for j,i in enumerate(range(data_len-1,-1,-1)):
        scores[j+1] = get_scorecard(data[i])
    for key in scores:
        for player in scores[key][0]:
            if player not in result:
                result[player] = []
            player_ = scores[key][0][player]
            if player_['fow'] == '':
                s = "Is {} ".format("not out")
                result[player].append(s)
                continue
            s = "At {} -- {}".format(player_['fow'],player_['wk_comm'])
            result[player].append(s)
    return result
    
    
def get_wickets_playerwise(data):
    scores = {}
    result = dict()
    
    data_len = len(data)
    for j,i in enumerate(range(data_len-1,-1,-1)):
        scores[j+1] = get_scorecard(data[i])
    for key in scores:
        for player in scores[key][1]:
            if player not in result:
                result[player] = []
            player_ = scores[key][1][player]
            s = "{}-{}-{}".format(player_['overs'], player_['runs_conceeded'],player_['wickets'])
            result[player].append(s)
    return result

def get_score_playerwise(data):
    scores = {}
    result = dict()
    
    data_len = len(data)
    for j,i in enumerate(range(data_len-1,-1,-1)):
        scores[j+1] = get_scorecard(data[i])
    for key in scores:
        for player in scores[key][0]:
            if player not in result:
                result[player] = []
            player_ = scores[key][0][player]
            s = "{} ({}) 4s:{},6s:{},SR:{}".format(player_['score'],player_['balls'],
                                            player_['4s'],player_['6s'],player_['sr'])
            result[player].append(s)
    return result
    
def get_dropped(data,team_1):
    util = 'DROPPED'
    if team_1:
        idx_list = [len(data) -1, len(data) - 3]
    else:
        idx_list = [len(data) -2, len(data)-4]
    comm = ["First Innings...."]
    flag = True
    innings_list = [data[idx_list[0]],data[idx_list[1]]]
    for inning in innings_list:
        try:
            for ball in reversed(inning['list']):
                if util in ball['Commentary']:
                    comm.append(ball["Over"]+ " "+ ball['Batsman_Name']+ ", "+ball['Commentary'])
        except IndexError:
            print("index error")
        if flag:
            comm.append("Second innings...")
            flag = False
    return comm

    

def get_bowling_summary(data,team):
    scores = {}
    data_len = len(data)
    for j,i in enumerate(range(data_len-1,-1,-1)):
        scores[j+1] = get_scorecard(data[i])
    result = dict()
    if team == 1:
        result['first_innings'] = scores[2][1]
        if data_len >=4:
            result['second_innings'] = scores[4][1]
        else:
            result['second_innings'] = None
    else:
        result['first_innings'] = scores[1][1]
        if data_len >= 3:
            result['second_innings'] = scores[3][1]
        else:
            result['second_innings'] = None
    return result

def get_batting_summary(data,team):
    scores = {}
    data_len = len(data)
    for j,i in enumerate(range(data_len-1,-1,-1)):
        scores[j+1] = get_scorecard(data[i])
    result = dict()
    if team == 1:
        result['first_innings'] = scores[1][0]
        if data_len >=3:
            result['second_innings'] = scores[3][0]
    else:
        result['first_innings'] = scores[2][0]
        if data_len >3:
            result['second_innings'] = scores[4][0]
    return result
        

def get_all_players(data):
    teams_dict = get_playing_eleven(data)
    all_players = []
    
    for team in teams_dict:
        all_players += teams_dict[team].split(',')
    return all_players

def get_mom(data):
    util = "man of the match"
    util2 = 'player of the match'
    mom_string = ""
    for ball in data[0]['list']:
        if util in ball["Commentary"].lower():
            idx = ball['Commentary'].lower().find('match')
            mom_string = ball['Commentary'][:idx]
            break
        if util2 in ball['Commentary'].lower():
            idx = ball['Commentary'].lower().find('match')
            mom_string = ball['Commentary'][:idx]
            break
    doc = nlp(mom_string)
    persons = []
    
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            persons.append(ent.text)
    all_players = get_all_players(data)
    for person in persons:
        for player in all_players:
            if person in player:
                return player.strip()
            
    return "couldt find any"


def get_game_result(scorecard,data):
    if get_eom_status(scorecard):
        #do it from scores
        return "team a or team b"
    else:
        return "game yet to be finished"
    
def get_eom_status(scorecard,data):
    util1="CLOSE OF PLAY"
    util2 = "MATCH NOTES"
    eom = "end of match"
    lines = scorecard.split('\n')
    for idx,line in enumerate(lines):
        if util1 in line:
            idx1 = idx
        if util2 in line:
            idx2 = idx
    if eom in lines[idx1+1:idx2][-1]:
        return get_mom(data)
    else:
        return "Match yet to end"

def get_team_names(scorecard):
    util = "1ST INNINGS"
    flag = False
    team1,team2 = '',''
    for line in scorecard.split('\n'):
        if util in line:
            if not flag:
                team1 = line.split(util)[0].title()
                flag = True
            else:
                team2 = line.split(util)[0].title()
    return team1,team2


def get_playing_eleven(data):  
    util = "(Playing XI) "
    teams = []
    for ball in data[len(data)-1]['list']:
        comm = ball['Commentary']
        if util in comm:
            teams.append(comm.split('-'))
    all_players = teams[0][1].split(',') + teams[1][1].split(',')
    team1 = teams[0][0][:teams[0][0].find('(')]
    team2 = teams[1][0][:teams[1][0].find('(')]
    teams_ = dict()
    teams_[team1.lower().strip()] = teams[0][1].strip()
    teams_[team2.lower().strip()] = teams[1][1].strip()
    return teams_            

def get_score(batsman,data):
    result_dict = dict(i1 = 0,i2 = 0)
    first_bat,first_bowl = get_scorecard(data[len(data)-1])
    for player in first_bat:
        if batsman.lower() in player.lower():
            player_dict = first_bat[player]
            s = "{}({}) 4s:{},6s:{},SR:{}".format(player_dict['score'], player_dict['balls'],
                                        player_dict['4s'],player_dict['6s'],player_dict['sr'])
            return s

def get_wickets_comm(data,team_1):
    if team_1:
        idx_list = [len(data) -1, len(data) - 3]
    else:
        idx_list = [len(data) -2, len(data)-4]
    comm = ["First Innings...."]
    flag = True
    innings_list = [data[idx_list[0]],data[idx_list[1]]]    
    
    for inning in innings_list:
        try:
            for ball in reversed(inning['list']):
                if "Iswicket" in ball and ball['Iswicket']:
                    comm.append(ball['Over']+ " "+ball['Batsman_Name']+" "+ball["Commentary"])

        except IndexError:
            print("index error")
        if flag:
            comm.append("Second innings...")
            flag = False
    return comm

def get_fours_comm(data, team_1):
    if team_1:
        idx_list = [len(data) -1, len(data) - 3]
    else:
        idx_list = [len(data) -2, len(data)-4]
    comm = ["First Innings...."]
    flag = True
    innings_list = [data[idx_list[0]],data[idx_list[1]]]
    for inning in innings_list:
        try:
            for ball in reversed(inning['list']):
                if ball['Batsman_Runs'] == '4':
                    comm.append(ball["Over"]+' '+ball['Commentary'])
        except IndexError:
            print("index error")
        if flag:
            comm.append("Second innings...")
            flag = False
    return comm

def get_six_comm(data, team_1):
    if team_1:
        idx_list = [len(data) -1, len(data) - 3]
    else:
        idx_list = [len(data) -2, len(data)-4]
    comm = ["First Innings...."]
    flag = True
    innings_list = [data[idx_list[0]],data[idx_list[1]]]
    for inning in innings_list:
        try:
            for ball in reversed(inning['list']):
                if ball['Batsman_Runs'] == '6':
                    comm.append(ball["Over"]+" "+ball['Batsman_Name']+" "+ball['Commentary'])
        except IndexError:
            print("index error")
        if flag:
            comm.append("Second innings...")
            flag = False
    return comm

def get_captain(data,team1,team2):
    cap = "(C"
    cap3 = "(WK/C)"
    pl = "(Playing XI"
    # team1,team2  ='',''
    teams = []
    teams.append(get_playing_eleven(data)[team1.lower()])
    teams.append(get_playing_eleven(data)[team2.lower()]) 
    cap1,cap2 = '',''
    for i in range(2):
        for player in teams[i].split(','):
            if pl in player:
                if i == 0:
                    team1 = player.split(pl)[0].strip()
                else:
                    team2 = player.split(pl)[0].strip()
            f1 = cap in player

            f3 = cap3 in player
            if f1 or f3:
                if i == 0:
                    cap1 = player.strip()
                else:
                    cap2 = player.strip()
    res = dict()
    res[team1.strip().lower()] = cap1
    res[team2.strip().lower()] = cap2
    return res


def get_scorecard(commentary):
    ##to do -- add maidens and no balls or wides
    ## run outs being added to bowler bowled fix needed
    batsman_scores = dict()
    bowler_stats = dict()
    wide = "WIDE"
    nobe = "NO BALL"
    for ball in commentary['list']:
        comm = ball["Commentary"]
        if ball['Isball']:
            bowler = ball["Bowler_Name"]
            batter = ball['Batsman_Name']
            score = int(ball['Batsman_Runs'])
            if bowler not in bowler_stats:
                bowler_stats[bowler] ={'overs':0,'runs_conceeded':0, "wickets":0,
                                       "wides":0,"no_ball":0} 
                
            if batter not in batsman_scores:
                    batsman_scores[batter] = {'score':0,'balls':0,'4s':0,
                                              '6s':0,'sr':0,'fow':'','wk_comm':''}
            if score == 4:
                batsman_scores[batter]['4s']+=1
            if score == 6:
                batsman_scores[batter]['6s'] +=1
            batsman_scores[batter]['score'] += int(score)
            batsman_scores[batter]['balls'] += 1
            bowler_stats[bowler]['runs_conceeded'] += int(ball["Bowler_Conceded_Runs"])
            f1 = wide in comm
            f2 = nobe in comm
            if f1:
                bowler_stats[bowler]['wides']+=1
            elif f2:
                bowler_stats[bowler]['no_ball']+=1
            else:
                bowler_stats[bowler]['overs'] += 1
            if "Iswicket" in ball and ball['Iswicket']:
                batsman_scores[batter]['fow'] = ball['Over']
                batsman_scores[batter]['wk_comm'] = comm
                if ball['Dismissal_Type'] == 'run out':
                    continue
                bowler_stats[bowler]['wickets'] += 1
                
    for bowler in bowler_stats:
        overs_ = bowler_stats[bowler]['overs']//6
        decimal = bowler_stats[bowler]['overs'] % 6
        overs = str(overs_)+'.'+str(decimal)
        bowler_stats[bowler]['overs'] = overs
        ##fix extras
    for batsman in batsman_scores:
        sr = int(batsman_scores[batsman]['score'])/int(batsman_scores[batsman]['balls']) * (100)
        batsman_scores[batsman]['sr'] = round(sr,2)
    return batsman_scores, bowler_stats

def get_day_summary(data):
    for ball in data[0]['list']:
        if ball['Isball']:
            break
        prev_ball = ball
    return prev_ball['Commentary']

def get_scores(data):
    current = len(data)
    result_scores = []
    result_wickets = []
    result_dict = dict()
    for inning in data:
        card = get_scorecard(inning)
        score,wickets = 0,0
        for player in card[0]:
            score +=card[0][player]['score']
        for player in card[1]:
            wickets+= card[1][player]['wickets']
        result_scores.append(score)
        result_wickets.append(len(card[0]) - 1)
    assert len(result_scores) == len(result_wickets)
    k = 0 
    for idx in range(len(data),0,-1):
        temp = 'i'+ str(idx)
        result_dict[temp] = str(result_scores[k]) + '/'+ str(result_wickets[k])
        k+=1
    
    return result_dict

def get_daywise(data):
    from collections import Counter
    all_days = []
    daywise = dict(day1 = list(), day2 = list(), day3 = list(), day4 = list(), day5 = list())
    for ball in data[-1]['list']:
        if 'Timestamp' in ball:
            time = ball['Timestamp']
            day1 = int(time.split('T')[0][-2:])
            if day1 > 26:
                print("might face issue, TODO part, will deal with it")
            break
    day2,day3,day4,day5 = day1+1, day1+2,day1+3,day1+4
    print(day1,day2,day3,day4,day5)
    for j,i in enumerate(range(len(data)-1,0,-1)):
        for ball in reversed(data[i]['list']):
            time = ball['Timestamp']
            day = int(time.split('T')[0][-2:])
            all_days.append(day)
            if day == day1:
                daywise['day1'].append(ball)
            elif day == day2:
                daywise['day2'].append(ball)
            elif day == day3:
                daywise['day3'].append(ball)
            elif day == day4:
                daywise['day4'].append(ball)
            elif day == day5:
                daywise['day5'].append(ball)
    print(Counter(all_days))
    
    return daywise


def get_teams(scorecard):
    util = "1ST INNINGS"
    flag = False
    team1,team2 = '',''
    for line in scorecard.split('\n'):
        if util in line:
            if not flag:
                team1 = line.split(util)[0].title()
                flag = True
            else:
                team2 = line.split(util)[0].title()
    return team1,team2

def get_toss(scorecard):
    for line in scorecard.split('\n'):
        if "toss" in line.lower():
            return line.split('\t')[-1].strip()

def util_fours_comm(comm):
    ans = ''
    for com in comm:
        ans+=com
        ans+='\n'
    return ans

def util_dropped_comm(summary):
    ans =""
    if len(summary)<2:
        return "No drop catches"
    else:
        for x in summary:
            ans+=x
            ans+='\n'
        return ans

def util_summary_batsman(summary):
    ans = "---First Innings---\n"
    for idx,inning in enumerate(summary):
        if idx == 1:
            ans+='---Second Innings---\n'
        for player in summary[inning]:
            player_ = summary[inning][player]
            s = "{} {}({})".format(player,player_['score'],player_['balls'])
            ans+=s
            ans+='\n'
        ans+='\n'
        
    return ans

def util_summary_bowling(summary):
    ans = "---First Innings---\n"
    for idx,inning in enumerate(summary):
        if idx == 1:
            ans+='---Second Innings---\n'
        try:
            for player in summary[inning]:
                player_ = summary[inning][player]
                s = "{} ----- {}-{}-{}".format(player,player_['overs'],player_['runs_conceeded'],player_['wickets'])
                ans+=s
                ans+='\n'
        except TypeError:
            ans+="   Yet to start"
        print(ans)
        
    return ans


def process():

	import requests
	
	header = {'accept':"appication/json"}
	# resp = requests.get("https://graph.xploree.in/cricket/nzpk01032021198122/commentary?limit=all", headers = header)
	resp = requests.get("https://graph.xploree.in/cricket/auin01072021195484/commentary?limit=all", headers = header)
	data = resp.json()
	scorecard = """

	AUSTRALIA 1ST INNINGS
	BATSMEN	 	R	B	M	4s	6s	SR	 
	Will Pucovski 	lbw b Saini	62	110	150	4	0	56.36	
	David Warner 	c Pujara b Mohammed Siraj	5	8	17	0	0	62.50	
	Marnus Labuschagne 	c Rahane b Jadeja	91	196	281	11	0	46.43	
	Steven Smith 	run out (Jadeja)	131	226	303	16	0	57.96	
	Matthew Wade 	c Bumrah b Jadeja	13	16	25	2	0	81.25	
	Cameron Green 	lbw b Bumrah	0	21	31	0	0	0.00	
	Tim Paine (c)†	 b Bumrah	1	10	18	0	0	10.00	
	Pat Cummins 	 b Jadeja	0	13	28	0	0	0.00	
	Mitchell Starc 	c Shubman Gill b Saini	24	30	32	2	1	80.00	
	Nathan Lyon 	lbw b Jadeja	0	3	5	0	0	0.00	
	Josh Hazlewood 	not out	1	6	16	0	0	16.67	
	Extras	(b 4, nb 5, w 1)	10	
	TOTAL	(105.4 Ov, RR: 3.20)	338	
	Fall of wickets: 1-6 (David Warner, 3.3 ov), 2-106 (Will Pucovski, 34.2 ov), 3-206 (Marnus Labuschagne, 70.5 ov), 4-232 (Matthew Wade, 76.5 ov), 5-249 (Cameron Green, 84.5 ov), 6-255 (Tim Paine, 88.5 ov), 7-278 (Pat Cummins, 94.4 ov), 8-310 (Mitchell Starc, 101.5 ov), 9-315 (Nathan Lyon, 102.4 ov), 10-338 (Steven Smith, 105.4 ov)
	BOWLING	O	M	R	W	ECON	WD	NB	 
	Jasprit Bumrah	25.4	7	66	2	2.57	0	0	
	Mohammed Siraj	25	4	67	1	2.68	1	0	
	Ravichandran Ashwin	24	1	74	0	3.08	0	0	
	Navdeep Saini	13	0	65	2	5.00	0	3	
	Ravindra Jadeja	18	3	62	4	3.44	0	2	
	INDIA 1ST INNINGS
	BATSMEN	 	R	B	M	4s	6s	SR	 
	Rohit Sharma 	c & b Hazlewood	26	77	111	3	1	33.77	
	Shubman Gill 	c Green b Cummins	50	101	134	8	0	49.50	
	Cheteshwar Pujara 	c †Paine b Cummins	50	176	278	5	0	28.41	
	Ajinkya Rahane (c)	 b Cummins	22	70	95	1	1	31.43	
	Hanuma Vihari 	run out (Hazlewood)	4	38	56	0	0	10.53	
	Rishabh Pant †	c Warner b Hazlewood	36	67	101	4	0	53.73	
	Ravindra Jadeja 	not out	28	37	75	5	0	75.68	
	Ravichandran Ashwin 	run out (Cummins/Labuschagne)	10	15	23	2	0	66.67	
	Navdeep Saini 	c Wade b Starc	3	13	11	0	0	23.08	
	Jasprit Bumrah 	run out (Labuschagne)	0	2	9	0	0	0.00	
	Mohammed Siraj 	c †Paine b Cummins	6	10	28	1	0	60.00	
	Extras	(lb 2, nb 2, w 5)	9	
	TOTAL	(100.4 Ov, RR: 2.43)	244	
	Fall of wickets: 1-70 (Rohit Sharma, 26.6 ov), 2-85 (Shubman Gill, 32.1 ov), 3-117 (Ajinkya Rahane, 54.4 ov), 4-142 (Hanuma Vihari, 67.2 ov), 5-195 (Rishabh Pant, 87.4 ov), 6-195 (Cheteshwar Pujara, 88.2 ov), 7-206 (Ravichandran Ashwin, 92.2 ov), 8-210 (Navdeep Saini, 94.5 ov), 9-216 (Jasprit Bumrah, 96.3 ov), 10-244 (Mohammed Siraj, 100.4 ov)
	BOWLING	O	M	R	W	ECON	WD	NB	 
	Mitchell Starc	19	7	61	1	3.21	0	2	
	Josh Hazlewood	21	10	43	2	2.05	1	0	
	Pat Cummins	21.4	10	29	4	1.34	0	0	
	Nathan Lyon	31	8	87	0	2.81	0	0	
	Marnus Labuschagne	3	0	11	0	3.67	0	0	
	Cameron Green	5	2	11	0	2.20	0	0	
	AUSTRALIA 2ND INNINGS
	BATSMEN	 	R	B	M	4s	6s	SR	 
	David Warner 	lbw b Ashwin	13	29	50	1	0	44.83	
	Will Pucovski 	c sub (WP Saha) b Mohammed Siraj	10	16	30	2	0	62.50	
	Marnus Labuschagne 	c sub (WP Saha) b Saini	73	118	179	9	0	61.86	
	Steven Smith 	lbw b Ashwin	81	167	261	8	1	48.50	
	Matthew Wade 	c sub (WP Saha) b Saini	4	11	16	1	0	36.36	
	Cameron Green 	c sub (WP Saha) b Bumrah	84	132	183	8	4	63.64	
	Tim Paine (c)†	not out	39	52	99	6	0	75.00	
	Extras	(b 1, lb 4, nb 3)	8	
	TOTAL	(87 Ov, RR: 3.58)	312/6d	
	Did not bat: Pat Cummins, Mitchell Starc, Nathan Lyon, Josh Hazlewood 
	Fall of wickets: 1-16 (Will Pucovski, 5.5 ov), 2-35 (David Warner, 9.2 ov), 3-138 (Marnus Labuschagne, 46.1 ov), 4-148 (Matthew Wade, 48.6 ov), 5-208 (Steven Smith, 67.4 ov), 6-312 (Cameron Green, 86.6 ov)
	BOWLING	O	M	R	W	ECON	WD	NB	 
	Jasprit Bumrah	21	4	68	1	3.24	0	0	
	Mohammed Siraj	25	5	90	1	3.60	0	1	
	Navdeep Saini	16	2	54	2	3.38	0	2	
	Ravichandran Ashwin	25	1	95	2	3.80	0	0	
	INDIA 2ND INNINGS (TARGET: 407 RUNS)
	BATSMEN	 	R	B	M	4s	6s	SR	 
	Rohit Sharma 	c Starc b Cummins	52	98	136	5	1	53.06	
	Shubman Gill 	c †Paine b Hazlewood	31	64	103	4	0	48.44	
	Cheteshwar Pujara 	 b Hazlewood	77	205	205	12	0	37.56	
	Ajinkya Rahane (c)	c Wade b Lyon	4	18	18	0	0	22.22	
	Rishabh Pant †	c Cummins b Lyon	97	118	118	12	3	82.20	
	Hanuma Vihari 	not out	23	161	161	4	0	14.29	
	Ravichandran Ashwin 	not out	39	128	128	7	0	30.47	
	Extras	(lb 3, nb 6, w 2)	11	
	TOTAL	(131 Ov, RR: 2.55)	334/5	
	Did not bat: Ravindra Jadeja, Navdeep Saini, Jasprit Bumrah, Mohammed Siraj 
	Fall of wickets: 1-71 (Shubman Gill, 22.1 ov), 2-92 (Rohit Sharma, 30.2 ov), 3-102 (Ajinkya Rahane, 35.4 ov), 4-250 (Rishabh Pant, 79.1 ov), 5-272 (Cheteshwar Pujara, 88.2 ov)
	BOWLING	O	M	R	W	ECON	WD	NB	 
	Mitchell Starc	22	6	66	0	3.00	0	2	
	Josh Hazlewood	26	12	39	2	1.50	0	1	
	Pat Cummins	26	6	72	1	2.77	0	2	
	Nathan Lyon	46	17	114	2	2.48	0	0	
	Cameron Green	7	0	31	0	4.43	2	0	
	Marnus Labuschagne	4	2	9	0	2.25	0	1	
	MATCH DETAILS
	Sydney Cricket Ground
	Toss	Australia, elected to bat first
	Series	
	India tour of Australia
	ICC World Test Championship
	Season	2020/21
	Player Of The Match	
	Steven Smith
	Steven Smith
	Series result	4-match series level 1-1
	Match number	TEST No. 2402
	Match days	7,8,9,10,11 January 2021 - day match (5-day match)
	Test debut	
	Navdeep Saini
	Navdeep Saini
	Will Pucovski
	Will Pucovski
	Umpires	
	Australia Image
	Paul Reiffel
	Australia Image
	Paul Wilson
	TV Umpire	
	Australia Image
	Bruce Oxenford
	Reserve Umpire	
	Australia Image
	Claire Polosak
	Match Referee	
	Australia Image
	David Boon
	Points	Australia 10, India 10
	CLOSE OF PLAY
	Thu, 07 Jan - day 1 -Australia 1st innings 166/2 (Marnus Labuschagne 67*, Steven Smith 31*, 55 ov)
	Fri, 08 Jan - day 2 -India 1st innings 96/2 (Cheteshwar Pujara 9*, Ajinkya Rahane 5*, 45 ov)
	Sat, 09 Jan - day 3 -Australia 2nd innings 103/2 (Marnus Labuschagne 47*, Steven Smith 29*, 29 ov)
	Sun, 10 Jan - day 4 -India 2nd innings 98/2 (Cheteshwar Pujara 9*, Ajinkya Rahane 4*, 34 ov)
	Mon, 11 Jan - day 5 -India 2nd innings 334/5 (131 ov) - end of match
	MATCH NOTES
	Day 1
	Australia 1st innings
	Rain: Australia - 21/1 in 7.1 overs (WJ Pucovski 14, M Labuschagne 2)
	Lunch: Australia - 21/1 in 7.1 overs (WJ Pucovski 14, M Labuschagne 2)
	Rain: Australia - 21/1 in 7.1 overs (WJ Pucovski 14, M Labuschagne 2)
	Wet Ground: Australia - 21/1 in 7.1 overs (WJ Pucovski 14, M Labuschagne 2)
	Australia: 50 runs in 23.2 overs (140 balls), Extras 0
	2nd Wicket: 50 runs in 124 balls (WJ Pucovski 31, M Labuschagne 19, Ex 0)
	WJ Pucovski: 50 off 97 balls (4 x 4)
	Tea: Australia - 93/1 in 31.0 overs (WJ Pucovski 54, M Labuschagne 34)
	Wet Ground: Australia - 93/1 in 31.0 overs (WJ Pucovski 54, M Labuschagne 34)
	Australia: 100 runs in 32.6 overs (198 balls), Extras 0
	2nd Wicket: 100 runs in 184 balls (WJ Pucovski 61, M Labuschagne 39, Ex 0)
	M Labuschagne: 50 off 108 balls (6 x 4)
	Drinks: Australia - 148/2 in 43.0 overs (M Labuschagne 56, SPD Smith 24)
	Australia: 150 runs in 43.2 overs (261 balls), Extras 1
	3rd Wicket: 50 runs in 80 balls (M Labuschagne 25, SPD Smith 27, Ex 1)
	End Of Day: Australia - 166/2 in 55.0 overs (M Labuschagne 67, SPD Smith 31)
	Day 2
	Over 63.2: Review by India (Bowling), Umpire - P Wilson, Batsman - SPD Smith (Struck down)
	Rain: Australia - 188/2 in 66.0 overs (M Labuschagne 78, SPD Smith 42)
	Australia: 200 runs in 68.5 overs (414 balls), Extras 1
	3rd Wicket: 100 runs in 218 balls (M Labuschagne 52, SPD Smith 47, Ex 1)
	SPD Smith: 50 off 116 balls (7 x 4)
	Rain: Australia - 213/3 in 72.0 overs (SPD Smith 52, MS Wade 2)
	New ball taken after 80 overs
	Lunch: Australia - 249/5 in 84.5 overs (SPD Smith 76)
	Australia: 250 runs in 87.3 overs (526 balls), Extras 2
	SPD Smith: 100 off 201 balls (13 x 4)
	Australia: 300 runs in 100.1 overs (605 balls), Extras 9
	Drinks: Australia - 310/8 in 101.5 overs (SPD Smith 104)
	Over 102.4: Review by Australia (Batting), Umpire - PR Reiffel, Batsman - NM Lyon (Struck down)
	Innings Break: Australia - 338/10 in 105.4 overs (JR Hazlewood 1)
	India 1st innings
	Tea: India - 26/0 in 9.0 overs (RG Sharma 11, Shubman Gill 14)
	India: 50 runs in 18.1 overs (110 balls), Extras 1
	1st Wicket: 50 runs in 110 balls (RG Sharma 22, Shubman Gill 27, Ex 1)
	Over 23.4: Review by India (Batting), Umpire - P Wilson, Batsman - RG Sharma (Upheld)
	Drinks: India - 70/1 in 27.0 overs (Shubman Gill 38)
	Shubman Gill: 50 off 100 balls (8 x 4)
	Over 39.4: Review by Australia (Bowling), Umpire - P Wilson, Batsman - AM Rahane (Struck down - Umpires Call)
	End Of Day: India - 96/2 in 45.0 overs (CA Pujara 9, AM Rahane 5)
	Day 3
	India: 100 runs in 45.5 overs (276 balls), Extras 6
	Over 55.3: Review by Australia (Bowling), Umpire - P Wilson, Batsman - CA Pujara (Struck down)
	Drinks: India - 132/3 in 63.0 overs (CA Pujara 27, GH Vihari 1)
	India: 150 runs in 69.3 overs (418 balls), Extras 6
	Over 73.1: Review by Australia (Bowling), Umpire - P Wilson, Batsman - RR Pant (Struck down)
	Lunch: India - 180/4 in 79.0 overs (CA Pujara 42, RR Pant 29)
	New ball taken after 80 overs
	5th Wicket: 50 runs in 115 balls (CA Pujara 15, RR Pant 35, Ex 1)
	CA Pujara: 50 off 174 balls (5 x 4)
	India: 200 runs in 89.4 overs (539 balls), Extras 7
	Drinks: India - 202/6 in 90.0 overs (RA Jadeja 1, R Ashwin 6)
	Innings Break: India - 244/10 in 100.4 overs (RA Jadeja 28)
	Over 100.4: Review by India (Batting), Umpire - PR Reiffel, Batsman - Mohammed Siraj (Struck down)
	Australia 2nd innings
	WP Saha kept wickets in place of RR Pant from the start of the 3rd innings
	Over 9.2: Review by Australia (Batting), Umpire - PR Reiffel, Batsman - DA Warner (Struck down - Umpires Call)
	Over 11.1: Review by India (Bowling), Umpire - PR Reiffel, Batsman - SPD Smith (Struck down - Umpires Call)
	Drinks: Australia - 41/2 in 13.0 overs (M Labuschagne 13, SPD Smith 3)
	Australia: 50 runs in 13.6 overs (85 balls), Extras 2
	3rd Wicket: 50 runs in 87 balls (M Labuschagne 28, SPD Smith 22, Ex 1)
	Australia: 100 runs in 28.5 overs (176 balls), Extras 4
	End Of Day: Australia - 103/2 in 29.0 overs (M Labuschagne 47, SPD Smith 29)
	Tea: Australia - 0/0
	Day 4
	M Labuschagne: 50 off 82 balls (6 x 4)
	3rd Wicket: 100 runs in 220 balls (M Labuschagne 61, SPD Smith 36, Ex 3)
	Drinks: Australia - 143/3 in 48.0 overs (SPD Smith 39, MS Wade 4)
	Australia: 150 runs in 49.3 overs (300 balls), Extras 4
	SPD Smith: 50 off 134 balls (5 x 4)
	Lunch: Australia - 182/4 in 64.0 overs (SPD Smith 58, C Green 20)
	5th Wicket: 50 runs in 98 balls (SPD Smith 29, C Green 21, Ex 0)
	Australia: 200 runs in 66.2 overs (401 balls), Extras 4
	Over 67.4: Review by India (Bowling), Umpire - PR Reiffel, Batsman - SPD Smith (Upheld)
	Australia: 250 runs in 77.6 overs (471 balls), Extras 4
	6th Wicket: 50 runs in 67 balls (C Green 21, TD Paine 29, Ex 0)
	Drinks: Australia - 258/5 in 79.0 overs (C Green 44, TD Paine 29)
	New ball taken after 82nd over
	C Green: 50 off 116 balls (7 x 4)
	Australia: 300 runs in 85.6 overs (519 balls), Extras 8
	6th Wicket: 100 runs in 115 balls (C Green 61, TD Paine 39, Ex 4)
	Tea: Australia - 312/6 in 87.0 overs (TD Paine 39)
	Over 86.6: Review by Australia (Batting), Umpire - P Wilson, Batsman - C Green (Struck down)
	India 2nd innings
	Over 7.2: Review by India (Batting), Umpire - PR Reiffel, Batsman - RG Sharma (Upheld)
	Over 7.4: Review by Australia (Bowling), Umpire - PR Reiffel, Batsman - Shubman Gill (Struck down)
	Drinks: India - 46/0 in 17.0 overs (RG Sharma 22, Shubman Gill 23)
	India: 50 runs in 18.6 overs (114 balls), Extras 1
	1st Wicket: 50 runs in 114 balls (RG Sharma 22, Shubman Gill 30, Ex 1)
	Over 22.1: Review by India (Batting), Umpire - P Wilson, Batsman - Shubman Gill (Struck down)
	Over 22.4: Review by India (Batting), Umpire - P Wilson, Batsman - CA Pujara (Upheld)
	RG Sharma: 50 off 95 balls (5 x 4, 1 x 6)
	End Of Day: India - 98/2 in 34.0 overs (CA Pujara 9, AM Rahane 4)
	Day 5
	India: 100 runs in 35.2 overs (213 balls), Extras 2
	India: 150 runs in 52.3 overs (318 balls), Extras 4
	4th Wicket: 50 runs in 103 balls (CA Pujara 13, RR Pant 35, Ex 2)
	Drinks: India - 152/3 in 53.0 overs (CA Pujara 26, RR Pant 35)
	RR Pant: 50 off 64 balls (4 x 4, 3 x 6)
	India: 200 runs in 67.6 overs (412 balls), Extras 5
	4th Wicket: 100 runs in 197 balls (CA Pujara 24, RR Pant 73, Ex 3)
	Lunch: India - 206/3 in 70.0 overs (CA Pujara 41, RR Pant 73)
	CA Pujara: 50 off 170 balls (7 x 4)
	India: 250 runs in 78.1 overs (473 balls), Extras 8
	New ball taken after 80th over
	Drinks: India - 262/4 in 84.0 overs (CA Pujara 70, GH Vihari 0)
	Over 91.4: Review by Australia (Bowling), Umpire - PR Reiffel, Batsman - R Ashwin (Struck down)
	Tea: India - 280/5 in 96.0 overs (GH Vihari 4, R Ashwin 7)
	Over 96.1: Review by India (Batting), Umpire - P Wilson, Batsman - R Ashwin (Upheld)
	India: 300 runs in 114.6 overs (694 balls), Extras 8
	Drinks: India - 305/5 in 117.0 overs (GH Vihari 7, R Ashwin 28)
	6th Wicket: 50 runs in 246 balls (GH Vihari 16, R Ashwin 33, Ex 3)
	"""
	##comm_data all 4 inning list
	
	team1, team2 = get_team_names(scorecard)
	# daywise_comm = get_daywise(data)
	
	# for day in daywise_comm:
	# 	if len(daywise_comm[day]) == 0:
	# 		break
	# 	prev_day = day

	# current_day = prev_day[-1]
	# data_len = len(data)
	# scores = {}
	# for j,i in enumerate(range(data_len,0,-1)):
	# 	scores[j+1] = get_scorecard(data[i])

	
	team1 = team1.strip('\t').strip()
	team2 = team2.strip('\t').strip()
	result_list = list()
	print(get_playing_eleven(data))
	print(team1,team2)
	# result_list.append(generate_qna(LOC, location))#from scorecard maybe for now.
	result_list.append(generate_qna("who is the captain of {}".format(team1),
											get_captain(data,team1,team2)[team1.lower()]))
	result_list.append(generate_qna("who is the captain of {}".format(team2),
											get_captain(data,team1,team2)[team2.lower()]))
	result_list.append(generate_qna("playing eleven of {}".format(team1)
								,get_playing_eleven(data)[team1.lower()]))
	result_list.append(generate_qna("playing eleven of {}".format(team2),
								get_playing_eleven(data)[team2.lower()]))
	# result_list.append(generate_qna("Current scores status -- "), get_scores(comm_data)) ## give lead, trial info maybe
	result_list.append(generate_qna("who won the toss...",get_toss(scorecard))) ##need score card info
	result_list.append(generate_qna("Who won the game -- ",get_eom_status(scorecard,data))) ##write func to see result
	# result_list.append(generate_qna("give session wise summary")) ##could be done from scorecard
	#link to be updated
	# result_list.append(generate_qna("give summary of today --", get_day_summary(data,scorecard)))##done
	#get eom status	
	result_list.append(generate_qna("mom -- ",get_mom(data))) ##can be done from score card actually, not in sc,done
	result_list.append(generate_qna("who batted first", team1)) ##score card da.
	result_list.append(generate_qna("who bowled first",team2)) ## score card easy da.
	result_list.append(generate_qna("summary batting {}".format(team1),
								util_summary_batsman(get_batting_summary(data,1))))
	result_list.append(generate_qna("summary batting {}".format(team2),
								util_summary_batsman(get_batting_summary(data,2))))
	result_list.append(generate_qna("bowling summary of {}".format(team1),
								util_summary_bowling(get_bowling_summary(data,1))))
	result_list.append(generate_qna("bowling summary of {}".format(team2),
								util_summary_bowling(get_bowling_summary(data,2))))

	# result_list.append(generate_qna("commentary of fours for team1"), ) #
	result_list.append(generate_qna("commentary of fours {}".format(team1),
									util_fours_comm(get_fours_comm(data,True))))
	result_list.append(generate_qna("commentary of fours {}".format(team2),
									util_fours_comm(get_fours_comm(data,False))))
	# result_list.append(generate_qna("commentary of sixes for team1"))
	result_list.append(generate_qna("comm of sixes {}".format(team1),
									util_fours_comm(get_six_comm(data,True))))
	result_list.append(generate_qna("comm of sixes {}".format(team2),
									util_fours_comm(get_six_comm(data,False))))
	result_list.append(generate_qna("comm of wickets {}".format(team1),
									util_fours_comm(get_wickets_comm(data,True))))
	result_list.append(generate_qna("comm of wickets {}".format(team2),
									util_fours_comm(get_wickets_comm(data,False))))

	# result_list.append(generate_qna("drop catches for team1"))
	# result_list.append(generate_qna("drop catches for team2"))
	result_list.append(generate_qna("Dropped catches comm {}".format(team1)
									,util_dropped_comm(get_dropped(data,True))))
	result_list.append(generate_qna("Dropped catches comm {}".format(team2)
									,util_dropped_comm(get_dropped(data,False))))
	batting_scores = get_score_playerwise(data)
	for player in batting_scores:
		if len(batting_scores[player]) ==2:
			ans = ''
			ans = "First inning \n{}\nSecond inning\n{}".format(batting_scores[player][0],
																batting_scores[player][1])
		if len(batting_scores[player]) ==1:
			ans = ''
			ans = "First inning \n{}\nSecond inning\nyet to bat/not batted".format(batting_scores[player][0])

		
		result_list.append(generate_qna("how many did {}".format(player),ans))
	bowling_stats = get_wickets_playerwise(data)
	for player in bowling_stats:
		if len(bowling_stats[player]) ==2:
			ans = ''
			ans = "First inning \n{}\nSecond inning\n{}".format(bowling_stats[player][0],
																bowling_stats[player][1])
		if len(bowling_stats[player]) ==1:
			ans = ''
			ans = "First inning \n{}\nSecond inning\nyet to bowl/not bowled".format(bowling_stats[player][0])
		result_list.append(generate_qna("Bowling figures of {}".format(player),ans))

	for qna in result_list:
		print(qna['question'])
		print("**************")
		print(qna["answer"])
		print('\n') 
	#how many runs each batsman

	#how each batsman got out
	#how many fours and sixes each batsman hit.
	#how many wickets each bowler picked
	#how many wides bowler bowled
	#how many no balls they bowled
	#when a player got out
	#who scored most runs ## innings wise team wise de do
	#Who scored least runs ## innings wise team wise de do
	##who picked most wickets ## team wise inning wise
	##sixes,fours,wides team wise



	# for ball in comm_data[0]['list']:
	# 	print(ball)
	# 	break
	# return {}

if __name__ == '__main__':
	process()



