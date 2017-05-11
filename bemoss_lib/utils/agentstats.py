import subprocess
import settings
def agentstats():
    #returns a list of running agents and their status
    statusreply = subprocess.check_output(settings.PROJECT_DIR + '/env/bin/volttron-ctl status',shell=True)
    statusreply = statusreply.split('\n')
    result = {}
    for line in statusreply:
        #print(line, end='') #write to a next file name outfile
        words = line.split()
        if len(words) >= 4:
            result[words[2]] = words[3]
        elif len(words) == 3:
            result[words[2]] = ''

    return result

#print agentstats()