# duolingo_streak_on_ice

Buy another "Streak on Ice" in Duolingo

## Description

[Duolingo](https://www.duolingo.com/) allows to pause your daily exercises, by [buying](https://www.duolingo.com/show_store) a "Streak on Ice" for 10 Lingots. A Lingot is the virtual currency used in [Duolingo](https://en.wikipedia.org/wiki/Duolingo).

If you follow through with your daily exercises, every 10 days you get another number Lingots credited to your account. The amount of Lingots is 10% of the days of your streak.

* 10 days streak: 1 Lingot
* 50 days streak: 5 Lingots
* 100 days streak: 10 Lingots
* 1000 days streak: 100 Lingots

Occasionally I forget to do my daily fun lessons. This script, if run as a daily [cron](https://en.wikipedia.org/wiki/Cron) job, will extend the streak.

```
python duolingo_streak.py -c duolingo.yaml -v
DEBUG: config file: duolingo.yaml
DEBUG: going to buy 'Streak on Ice' extension ...
INFO: bought streak extension for: <your username here>
```

