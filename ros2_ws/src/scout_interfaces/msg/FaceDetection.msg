# A detected face with optional identity match
std_msgs/Header header
string person_name          # Matched name or "unknown"
float32 confidence          # Match confidence [0.0 - 1.0]
sensor_msgs/RegionOfInterest bounding_box  # Face location in frame
string source               # Camera source
bool is_enrolled            # Whether this face is in the database
