import datetime


if __name__ == '__main__':

     time = str(datetime.datetime.now())
     fname = "Sweep Values " + time + ".txt"

     print(fname)

     testname = "swee :.values.txt"
     freq = "100"
     volts = "200"
     curr = "300"

     FORMAT = '%Y_%m_%d_%H%M'

     path = 'sweep_values'
     new_path = '%s_%s.txt' % (path, datetime.datetime.now().strftime(FORMAT))

     f = open(new_path,"w+")

     f.write("freq,volts,curr\n\n")
     for i in range(10):
     	f.write(freq + ',' + volts + ',' + curr + '\n')