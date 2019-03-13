s = '''
-Xms256m - Xmx256m - XX:NewSize = 64 m - XX:+UseConcMarkSweepGC - XX:CMSInitiatingOccupancyFraction = 58 - XX:PermSize = 64 m - XX: MaxPermSize = 64 m - XX: ThreadStackSize = 228 
'''

import re
s_ =re.compile("(Xm)")
print(s_.findall(s))
