
from datetime import datetime



arr = "2022-01-14 00:00:00"
date_format_str = '%Y-%m-%d %H:%M:%S'
expiry_time = datetime.strptime(arr, date_format_str)
now_01 = str(datetime.now())
now_02 = (now_01[:19])
ex = datetime.strptime(now_02, date_format_str)
duration =   expiry_time - ex
duration_in_s = duration.total_seconds()
print(duration_in_s)