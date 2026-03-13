# Current patrol state
std_msgs/Header header
string current_room         # Room currently being patrolled
string[] rooms_completed    # Rooms already visited this patrol
string[] rooms_remaining    # Rooms still to visit
uint32 objects_logged       # Objects detected this patrol
float32 battery_percent     # Current battery level
uint8 state                 # 0=idle, 1=patrolling, 2=returning_to_dock, 3=docked
