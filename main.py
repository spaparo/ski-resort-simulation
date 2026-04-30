from observers import StatsManager

stats = StatsManager()

stats.update("lift_wait", 5)
stats.update("run", 1)
stats.update("cafe", 1)
stats.update("fall", 1)
stats.update("visitor_type", "skier")

print(stats.wait_times)
print(stats.total_runs)
print(stats.cafe_visits)
print(stats.falls)
print(stats.visitor_types)