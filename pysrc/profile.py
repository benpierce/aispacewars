import collections 
import datetime 
import operator 

class Profile(object):
    profile_data = collections.defaultdict(int)
    execution_data = collections.defaultdict(int)
    start_time = datetime.datetime.now()

    @classmethod 
    def start(cls, section):
        cls.start_time = datetime.datetime.now()
        cls.execution_data[section] += 1

    @classmethod 
    def stop(cls, section):
        delta = datetime.datetime.now() - cls.start_time 

        cls.profile_data[section] += delta.total_seconds() * 1000  

    @classmethod 
    def dump(cls):
        sorted_d = dict(sorted(cls.profile_data.items(), key=operator.itemgetter(1), reverse=True))
        total_ms = 0
        print('')
        print('*************************************** Performance Statistics **********************************')
        for key, value in sorted_d.items():
            print('{0}: {1} ms, called {2} times'.format(key, value, cls.execution_data[key]))
            total_ms += value 
        print('TOTAL: {0}'.format(total_ms))
        print('*************************************************************************************************')
        print('')