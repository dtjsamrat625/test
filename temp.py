
##get list day wise, given data
def get_daywise(data):
    daywise = dict(day1 = list(), day2 = list(), day3 = list(), day4 = list(), day5 = list())
    for ball in data[-1]['list']:
        if 'Timestamp' in ball:
            time = ball['Timestamp']
            day1 = int(time.split('T')[0][-2:])
            day2,day3,day4,day5 = day1+1, day1+2,day1+3,day1+4
            if day1 > 25:
                print("might face issue, TODO part, will deal with it")
    for j,i in enumerate(range(len(data)-1,0,-1)):
        for ball in reversed(data[i]['list']):
            time = ball['Timestamp']
            day = int(time.split('T')[0][-2:])
            if day == day1:
                daywise['day1'].append(ball)
            elif day == day2:
                daywise['day2'].append(ball)
            elif day == day3:
                daywise['day3'].append(ball)
            elif day == day4:
                daywise['day4'].append(ball)
            else:
                daywise['day5'].append(ball)
    
    return daywise


def get_scorecard(commentary):
    ##to do -- add maidens 
    ## run outs being added to bowler bowled fix needed -- fixed
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
                    batsman_scores[batter] = {'score':0,'balls':0,'4s':0,'6s':0,'sr':0}
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

def get_captain(data):
    cap = "(C"
#     cap2 = "(C/WK)" #todo part
    cap3 = "(WK/C)"
    pl = "(Playing XI"
    team1,team2  ='',''
    teams = get_playing_eleven(data).split('\n')
    cap1,cap2 = '',''
    for i in range(2):
        for player in teams[i].split(','):
            if pl in player:
                if i == 0:
                    team1 = player.split(pl)[0].strip()
                else:
                    team2 = player.split(pl)[0].strip()
            f1 = cap in player
#             f2 = cap2 in player
            f3 = cap3 in player
            if f1 or f3:
                if i == 0:
                    cap1 = player.strip()
                else:
                    cap2 = player.strip()
    res = dict()
    res[team1] = cap1
    res[team2] = cap2
    return res


def get_scores(data):
    ##extras not considered in scores
    ##data is list of 4 inning
    ##get info about toss from scorecard
    result_scores,result_wickets = [],[]
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
#         if temp not in 
        result_dict[temp] = str(result_scores[k]) + '/'+ str(result_wickets[k])
        k+=1
    
    return result_dict

def get_toss(scorecard):
    for line in scorecard.split('\n'):
        if "toss" in line.lower():
            return line.split('\t')[-1].strip()

def get_day_summary(data,scorecard):
	##return current status
    for ball in data[0]['list']:
        if ball['Isball']:
            break
        prev_ball = ball
    return prev_ball['Commentary']

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

def get_fours_comm(data):
    comm = []
    for ball in reversed(data['list']):
        if ball['Batsman_Runs'] == '4':
            comm.append(ball["Over"]+ ' '+ball['Commentary'])
    return comm

def get_fours_six(data):
    comm = []
    for ball in reversed(data['list']):
        if ball['Batsman_Runs'] == '6':
            comm.append(ball["Over"]+ ' '+ball['Commentary'])
    return comm

def get_wickets_comm(data):
    comm = []
    for ball in reversed(data['list']):
        if "Iswicket" in ball and ball['Iswicket']:
            comm.append(ball['Over']+ " "+ball['Batsman_Name']+" "+ball["Commentary"])
    return comm

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
    teams_[team1] = teams[0][1].strip()
    teams_[team2] = teams[1][1].strip()
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