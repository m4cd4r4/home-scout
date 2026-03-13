# A single observation of an object at a location
std_msgs/Header header
string object_name          # Canonical name (e.g., "keys", "phone", "wallet")
string room                 # Room where observed (e.g., "kitchen", "living_room")
string zone                 # Sub-area within room (e.g., "counter", "couch")
geometry_msgs/Point position  # Map coordinates (x, y, z)
float32 confidence          # Detection confidence [0.0 - 1.0]
string source               # Camera source ("onboard_front", "esp32_kitchen", etc.)
builtin_interfaces/Time timestamp  # When the object was seen
