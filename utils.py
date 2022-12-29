import random  
import string  


def random_string(length):
    # Print the string in Lowercase  
    return ''.join((random.choice(string.ascii_lowercase) for x in range(length))) 

