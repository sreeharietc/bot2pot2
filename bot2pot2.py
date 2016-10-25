from socketIO_client import SocketIO
from select import select
import sys
import math

playerKey = 'Frgtpotr4e'
gameKey = 'fGmbGTO4EWX2EFP4fRwn'
socket_var = SocketIO('10.7.90.8', 4000)
first_strike = True
coins = []

def connection_response(*args):
  print args

def opponent_turn_response(*args):
  print 'oppponent turn response'

def first_hit():
  global first_strike 
  first_strike = False
  pos = 500
  force = 4000
  angle = 90
  socket_var.emit('player_input', {'position': pos, 'force': force, 'angle': angle})
  return

def manual_hit():
  pos = raw_input('pos')
  force = raw_input('forc')
  angle = raw_input('ang')
  socket_var.emit('player_input', {'position': pos, 'force': force, 'angle': angle})

def find_through_coins( coins ):
  through_coins = list()
  for i in range(0, len(coins)):
	if coins[i]['x'] > (153.2258+55) and coins[i]['id'] != 's1':
		through_coins.append(coins[i])
  return through_coins

def find_distance_dict( through_coins ):
  distance_dict = {}
  for i in range(0, len(through_coins)):
 	y_position = through_coins[i]['y']
   	distance = through_coins[i]['x'] - 153.2258
  	distance_dict[distance] = through_coins[i]['id']
  return distance_dict

def select_coin( distance_dict, through_coins ):
  distance_list = distance_dict.keys()
  min_dist = min(distance_list)
  min_dist_coin_id = distance_dict[min_dist]
  for i in range(0, len(through_coins)):
	if(through_coins[i]['id'] == min_dist_coin_id):
		selected_coin = through_coins[i]
  return selected_coin

def select_rev_cut_coin( distance_dict, through_coins ):
  distance_list = distance_dict.keys()
  min_dist = min(distance_list)
  if min_dist <= 205:
	flag = True
  else:
  	flag = False
  min_dist_coin_id = distance_dict[min_dist]
  for i in range(0, len(through_coins)):
	if(through_coins[i]['id'] == min_dist_coin_id):
		selected_coin = through_coins[i]
  return selected_coin

def calculate_striker_move(selected_pocket, selected_coin):
	global coins
	print '2 ', coins
	invalid = False
	coin_radius = 25
	striker_radius = 30
	strike_parameters = list()
	slope = (selected_pocket[1]-selected_coin['y'])/(selected_pocket[0]-selected_coin['x'])
	striker_anlge = 90 + (math.degrees(math.atan(slope)))
	striker_pos = (slope*(153.2258 - selected_coin['x']))+selected_coin['y']
	force = 800
	if striker_pos > 806.4516 or striker_pos < 193.5484:
		d = coin_radius + striker_radius
		cut_pos_x = selected_coin['x'] - (d*(1/(math.sqrt(1+math.pow(slope,2)))))
		cut_pos_y = (slope*(cut_pos_x - selected_coin['x'])) + selected_coin['y']
		print 'striker cut position'
		print cut_pos_x, cut_pos_y
		if striker_pos > 806.4516:
			striker_pos = 806.4516
		else:
			striker_pos = 193.5484
		slope = (cut_pos_y - striker_pos)/(cut_pos_x - 153.2258)
		striker_anlge = 90 + (math.degrees(math.atan(slope)))
		force = 1500
	base_coins = find_base_coins(coins)
	invalid = find_invalidity( striker_pos, base_coins) 
	if invalid:
		coins = remove_selected_coin(selected_coin) 
		hit_coins(coins)
	strike_parameters = [ striker_pos, striker_anlge, force]
	print 'strike', strike_parameters
	return strike_parameters

def find_base_coins( coins ):
  base_coins = list()
  for i in range(0, len(coins)):
	if coins[i]['x'] < (153.2258+55) and coins[i]['id'] != 's1':
		base_coins.append(coins[i])
  return base_coins

def find_invalidity( striker_pos, base_coins):
	for coin in base_coins:
		distance = math.sqrt((math.pow((striker_pos - coin['y']),2)) + (math.pow((153.2258 - coin['x']),2)))
		if distance <= 55:
			return True
	return False

def remove_selected_coin(selected_coin):
	global coins
	print '3 ', coins
	id  = selected_coin['id']
	print 'id ', id
	for i in range(0, len(coins)):
		print coins[i]['id']
		if coins[i]['id'] == id:
			del coins[i]
			return coins

def find_base_coins_distance_dict( base_coins ):
  distance_dict = {}
  selected_pocket = []
  bl_pocket = [32.2581, 32.2581]
  ul_pocket = [32.2581, 967.7419]
  for i in range(0, len(base_coins)):
 	y_position = base_coins[i]['y']
        if base_coins[i]['y'] <= 500:
		selected_pocket = bl_pocket
	else:
		selected_pocket = ul_pocket
   	distance = math.sqrt(math.pow((base_coins[i]['x'] - selected_pocket[0]), 2) + pow((base_coins[i]['y'] - selected_pocket[1]), 2))
  	distance_dict[distance] = base_coins[i]['id']
  return distance_dict

def near_coin_rev_cut_position(selected_coin, base_coins):
	board_pos_x = 970
   	d = 55
   	i = 0
   	invalid = False
	print 'selected coin'
	print selected_coin
	if selected_coin['y'] <= 500:
		selected_pocket = [32.2581, 32.2581]
	else:
		selected_pocket = [32.2581, 967.7419] 
	slope_bw_coin_and_pocket = (selected_coin['y'] - selected_pocket[1])/(selected_coin['x'] - selected_pocket[0])
	cut_pos_x = selected_coin['x'] + (d*(1/(math.sqrt(1+math.pow(slope_bw_coin_and_pocket,2)))))
	cut_pos_y = (slope_bw_coin_and_pocket*(cut_pos_x - selected_coin['x'])) + selected_coin['y']
	print 'striker cut position'
	print cut_pos_x, cut_pos_y
	while True:
		if selected_coin['y'] <= 500:
		 	rev_angle = 8 + i
		else:
		 	rev_angle = -8 - i 
		rev_slope = math.tan(math.radians(rev_angle))
		board_pos_y = (rev_slope*(board_pos_x - cut_pos_x)) + cut_pos_y
		print 'board positions'
		print board_pos_x, board_pos_y 
		striker_pos = ((-rev_slope)*(153.2258 - board_pos_x)) + board_pos_y
		striker_anlge = 90 - (math.degrees(math.atan(rev_slope)))
		force = 2500
		print 'pos, angl, forc:'
		print striker_pos, striker_anlge, force
		invalid = find_invalidity( striker_pos, base_coins)
		i = i+3
		if not invalid:
			break
	socket_var.emit('player_input', {'position': striker_pos, 'force': force, 'angle': striker_anlge})

def reverse_hit(coins):
  base_coins = list()
  distance_dict = {}
  selected_coin = {}
  base_coins = find_base_coins( coins )
  distance_dict = find_base_coins_distance_dict( base_coins )
  selected_coin = select_rev_cut_coin( distance_dict, base_coins )
  near_coin_rev_cut_position(selected_coin, base_coins)

def hit_coins(coins):
 	  through_coins = []	
	  distance_dict = {}
	  selected_coin = {}
	  bl_pocket = [32.2581, 32.2581]
	  ul_pocket = [32.2581, 967.7419]
	  br_pocket = [967.7419, 32.2581]
	  ur_pocket = [967.7419, 967.7419]
	  through_coins = find_through_coins( coins )
	  #print 'through coins:'
	  #print through_coins
	  if not through_coins:
		reverse_hit(coins)
		return
	  distance_dict = find_distance_dict( through_coins )
	  #print 'distance dictionary:'
	  #print distance_dict
	  selected_coin = select_coin( distance_dict, through_coins )
	  #print 'selected coin:'
	  #print selected_coin
	  if selected_coin['y'] <= 500:
		strike_parameters = calculate_striker_move( br_pocket, selected_coin )
	  else:
		strike_parameters = calculate_striker_move( ur_pocket, selected_coin )
	  #print 'striker parameters:'
	  #print strike_parameters
	  socket_var.emit('player_input', {'position': strike_parameters[0], 'force': strike_parameters[2], 'angle': strike_parameters[1]})

def your_turn_response(*args):
  print 'your turn:'
  #print args
  global first_strike
  state = raw_input('Bot or Manual?')
  if(state == 'n'):
	  manual_hit()
  else:
	  #if first_strike == True:
		#first_hit()
		#return	
	  global coins 
	  coins = args[0]['position']
	  print '1 ', coins
	  hit_coins(coins)
  
print socket_var.connected
socket_var.emit("connect_game", {'playerKey': playerKey, 'gameKey': gameKey})
socket_var.on('connect_game', connection_response)
socket_var.on('opponent_turn', opponent_turn_response)
socket_var.on('your_turn', your_turn_response)
socket_var.on('player_input', connection_response)
socket_var.wait()

