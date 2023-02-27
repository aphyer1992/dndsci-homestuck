import math
import random

log_location = 'dndsci_homestuck_data_smaller.csv'
powers = [
    {'class' : 'Knight', 'aspect' : 'Rage', 'combat' : 4, 'friendship' : 1, 'shenanigans' : 1 },
    {'class' : 'Maid', 'aspect' : 'Heart', 'combat' : 1, 'friendship' : 4, 'shenanigans' : 1 },
    {'class' : 'Seer', 'aspect' : 'Time', 'combat' : 1, 'friendship' : 1, 'shenanigans' : 4 },
    {'class' : 'Rogue', 'aspect' : 'Blood', 'combat' : 3, 'friendship' : 2, 'shenanigans' : 1 },
    {'class' : 'Thief', 'aspect' : 'Doom', 'combat' : 3, 'friendship' : 1, 'shenanigans' : 2 },
    {'class' : 'Bard', 'aspect' : 'Breath', 'combat' : 2, 'friendship' : 3, 'shenanigans' : 1 },
    {'class' : 'Sylph', 'aspect' : 'Life', 'combat' : 1, 'friendship' : 3, 'shenanigans' : 2 },
    {'class' : 'Witch', 'aspect' : 'Light', 'combat' : 2, 'friendship' : 1, 'shenanigans' : 3 },
    {'class' : 'Mage', 'aspect' : 'Mind', 'combat' : 1, 'friendship' : 2, 'shenanigans' : 3 },
    {'class' : 'Heir', 'aspect' : 'Space', 'combat' : 2, 'friendship' : 2, 'shenanigans' : 2 },
    {'class' : 'Prince', 'aspect' : 'Void', 'combat' : 2, 'friendship' : 2, 'shenanigans' : 2, 'mirror' : True },
    {'class' : 'Page', 'aspect' : 'Hope', 'combat' : 3, 'friendship' : 3, 'shenanigans' : 3, 'penalize' : True },
]

stats = [ 'combat', 'friendship', 'shenanigans']

class_names = [p['class'] for p in powers]
aspect_names = [p['aspect'] for p in powers]

for power in powers:
    if 'penalize' not in power.keys():
        power['penalize'] = False
    if 'mirror' not in power.keys():
        power['mirror'] = False

hit_chance = 0.25
miss_chance = 1 - hit_chance
prob_of_n_hits = []
prob_of_n_hits.append([1, 0, 0, 0, 0]) # 0 dice has a 100% chance of showing 0 hits

while len(prob_of_n_hits) < 60:
    previous_probs = prob_of_n_hits[len(prob_of_n_hits) - 1]
    new_probs = [previous_probs[0] * miss_chance ] # prob of 0 is prob of 0 with one less die times miss chance
    while len(new_probs) <= len(prob_of_n_hits) + 2:
        j = len(new_probs) # we currently have j elements, first being 0 hits, so next element is j hits
        prob = (previous_probs[j-1] * hit_chance) + (previous_probs[j] * miss_chance) # j-1 hits and then a hit, or j hits and then a miss
        new_probs.append(prob)
    new_probs.append(0) # add some zeroes to pad for the next one
    new_probs.append(0)
    new_probs.append(0)
    prob_of_n_hits.append(new_probs)
    
def roll_die(n):
    return(math.ceil(random.random() * n))

def get_stats_from_classpect(classpect):
    matches = [ p for p in powers if (p['class'] == classpect or p['aspect'] == classpect) ]
    assert(len(matches) == 1)
    return(matches[0])

def get_stats_from_classpect_pair(classpect_a, classpect_b):
    stats_a = get_stats_from_classpect(classpect_a)
    stats_b = get_stats_from_classpect(classpect_b)

    output = {}
    for stat in stats:
        a_stat = stats_a[stat]
        b_stat = stats_b[stat]
        if stats_a['penalize'] == True:
            b_stat = max(1, b_stat - 1)
        if stats_a['mirror'] == True:
            b_stat = 4 - b_stat
        if stats_b['penalize'] == True:
            a_stat = max(a_stat - 1, 1)
        if stats_b['mirror'] == True:
            a_stat = 4 - a_stat
        output[stat] = a_stat * b_stat

    output['aspect'] = classpect_b
    output['class'] = classpect_a
    output['name'] = '{} of {}'.format(classpect_a, classpect_b)
    return(output)

def get_stats_from_name(name):
    (class_name, aspect_name) = name.split(' of ')
    return(get_stats_from_classpect_pair(class_name, aspect_name))

def setup_chars():
    chars = []
    for class_name in class_names:
        for aspect_name in aspect_names:
            chars.append(get_stats_from_classpect_pair(class_name, aspect_name))
    return(chars)

def get_team_stats(team):
    stat_totals = {}
    for stat in stats:
        stat_totals[stat] = sum([c[stat] for c in team])
    stat_totals['min'] = min([stat_totals[s] for s in stats])
    return(stat_totals)

def cumulative_win_prob(target_number, num_dice):
    hit_distribution = prob_of_n_hits[num_dice]
    win_chance = 0
    loss_chance = 0
    index = 0
    while(index < len(hit_distribution)):
        if index < target_number:
            loss_chance = loss_chance + hit_distribution[index]
        else:
            win_chance = win_chance + hit_distribution[index]
        index = index + 1
    assert(abs(win_chance + loss_chance - 1) < 0.0001)
    return(win_chance)

def get_team_win_rate(team):
    team_stats = get_team_stats(team)
    return(cumulative_win_prob(len(team), team_stats['min']))

chars = setup_chars()

def troll_optimizer():
    trolls = [ 'Knight of Blood', 'Mage of Doom', 'Heir of Void', 'Prince of Hope', 'Page of Breath', 'Bard of Rage', 'Thief of Light', 'Rogue of Heart', 'Maid of Time', 'Witch of Life', 'Sylph of Space', 'Seer of Mind' ]
    troll_stats = [ get_stats_from_name(t) for t in trolls]
    troll_win_rate = get_team_win_rate(troll_stats)
    print('Base win rate is {:.2f}%.\n'.format(troll_win_rate * 100))
    for missing in troll_stats:
        print('Trying without the {}\n'.format(missing['name']))
        missing_team = [ t for t in troll_stats if t != missing ]
        missing_win_rate = get_team_win_rate(missing_team)
        print('Resulting win rate is {:.2f}%, {:.2f}% {}\n'.format((missing_win_rate * 100), (abs(missing_win_rate - troll_win_rate) * 100), 'higher' if missing_win_rate > troll_win_rate else 'lower'))

def gen_random_team(team_size):
    team = []
    available_chars = [ c for c in chars ]
    while len(team) < team_size:
        new_char = random.choice(available_chars)
        available_chars = [ c for c in available_chars if ((c['class'] != new_char['class']) and (c['aspect'] != new_char['aspect']))]
        team.append(new_char)
    return(team)

def setup_logs():
    log_row =  [ '# of Heroes' ]
    while len(log_row) < 13:
        log_row.append('Hero {}'.format(len(log_row)))
    #log_row.append('Win Rate')
    log_row.append('Won?')
    write_log_row(log_row, mode='w')
    
def write_log_row(log_row, mode='a'):
    log_string = ','.join([str(e) for e in log_row])+"\n"
    f = open(log_location, mode)
    f.write(log_string)
    

def gen_dataset_row():
    team_size = roll_die(12)
    team = gen_random_team(team_size)
    win_rate = get_team_win_rate(team)
    win = True if random.random() < win_rate else False
    while len(team) < 12:
        team.append(None)
    write_log_row([ team_size ] + [c['name'] if c is not None else '' for c in team] + [win])


def main():
    setup_logs()
    i = 0
    while i< 200000:
        if i % 1e5 == 0:
            print(i)
        gen_dataset_row()
        i = i + 1

def retrieve_data(apply_filter = lambda x : True):
    f = open(log_location)
    index_row = f.readline()
    index_row = index_row.replace('\n', '')
    cols = index_row.split(',')
    data = []
    i = 0
    while True:
        if i%1e5 == 0:
            print(i)
        i = i + 1
        row = f.readline()
        row = row.replace('\n', '')
        print(row)
        assert(1==2)
        if row is None:
            break
        row = row.split(',')
        if(len(row) < len(cols)):
            break
        row_data = {}
        col_index = 0
        while col_index < len(cols):
            row_data[cols[col_index]] = row[col_index]
            col_index= col_index + 1
        if apply_filter(row_data) == True:
            data.append(row_data)
    print(len(data))
    return(data)

#random.seed('homestuck')
#main()

test1 = [ c for c in chars if c['name'] == 'Knight of Blood' ][ 0 ]
test2 = [ c for c in chars if c['name'] == 'Mage of Time' ][ 0 ]
winrates = []
for char1 in chars:
    used_aspects = [ 'Blood', 'Time' ]
    used_classes = [ 'Mage', 'Knight']
    if char1['aspect'] in used_aspects or char1['class'] in used_classes:
        continue
    else:
        used_aspects.append(char1['aspect'])
        used_classes.append(char1['class'])
        for char2 in chars:
            if char2['aspect'] in used_aspects or char2['class'] in used_classes:
                continue
            else:
                party = [test1, test2, char1, char2]
                winrate = get_team_win_rate(party)
                winrates.append([party, winrate])
        
    

def solo_compare():
    data = retrieve_data(apply_filter = lambda row: True if row['# of Heroes'] == '1' else False)
    solo = [ e for e in data if e['# of Heroes'] == '1' ]
    heroes = {}
    for e in solo:
        hero = e['Hero 1']
        if hero not in heroes.keys():
            heroes[hero] = { 'runs' : 0, 'wins': 0, 'true_winrate' : e['Win Rate'] }
        heroes[hero]['runs'] = heroes[hero]['runs'] + 1
        if e['Won?'] == 'True':
            heroes[hero]['wins'] = heroes[hero]['wins'] + 1

    f = open('homestuck_solo_heroes.csv', 'w')
    f.write('Hero,Observed Winrate, True Winrate\n')
    for h in heroes.keys():    
        heroes[h]['observed_winrate'] = heroes[h]['wins'] / heroes[h]['runs']
        f.write('{},{:.4f},{:.4f}\n'.format(h, heroes[h]['observed_winrate'], float(heroes[h]['true_winrate'])))
    f.close()


def scenario_hunter():
    potential_wins = []
    for char_a in chars:
        temp_chars_1 = [c for c in chars if (c['aspect'] != char_a['aspect']) and (c['class'] != char_a['class'])]
        for char_b in temp_chars_1:
            if char_b['aspect'] < char_a['aspect']:
                continue
            print('\nConsidering starting team of {} and {}:\n'.format(char_a['name'], char_b['name']))
            best_total = 0
            best_teams = []
            temp_chars_2 = [c for c in temp_chars_1 if (c['aspect'] != char_b['aspect']) and (c['class'] != char_b['class'])]
            for char_c in temp_chars_2:
                temp_chars_3 = [c for c in temp_chars_2 if (c['aspect'] != char_c['aspect']) and (c['class'] != char_c['class'])]
                for char_d in temp_chars_3:
                    if char_d['aspect'] < char_c['aspect']:
                        continue
                    stat_totals = []
                    for stat in stats:
                        stat_totals.append(char_a[stat] + char_b[stat] + char_c[stat] + char_d[stat])
                    current_total = min(stat_totals)
                    if current_total > best_total:
                        best_total = current_total
                        best_teams = []
                    if current_total == best_total:
                        best_teams.append([char_a, char_b, char_c, char_d])
            doom_teams = [ t for t in best_teams if len([c for c in t if c['aspect'] == 'Doom']) > 0 ]
            good_teams = [ t for t in best_teams if len([c for c in t if c['aspect'] in ['Doom', 'Rage', 'Blood'] ]) == 0 ]
            print('\nBest possible score of {} can be obtained in {} ways of which {} involve Doom\n'.format(best_total, len(best_teams), len(doom_teams)))
            if( len(doom_teams) == 1 and len(good_teams) == 1 and len(best_teams) == 2 ):
                print('POTENTIAL!')
                potential_wins.append({
                    'starting_chars': [char_a['name'], char_b['name']],
                    'possible_teams' : [[t[2]['name'], t[3]['name']] for t in best_teams ],
                    'best_score' : best_total
                })
