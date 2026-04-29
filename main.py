from observers import StatsManager

stats = StatsManager()

stats.update("lift_wait", 5)
stats.update("run", 1)
stats.update("cafe", 1)

print(stats.wait_times)
print(stats.runs)
print(stats.cafe_visits)