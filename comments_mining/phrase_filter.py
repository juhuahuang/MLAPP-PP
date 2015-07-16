__author__ = 'Administrator'

# remove similar phrase

def read_in(path):
    ff=open(path)
    phrase =[]
    for line in ff:
        phrase.append(line)
    return phrase

def dtw(str1,str2):
    len_str1 = len(str1)
    len_str2 = len(str2)
    row = [None] * len_str1
    dist_matrix = [row] * len_str2

    dist_matrix[0][0] = 1 if str1[0] == str2[0] else 0


    for i in range(1,len_str1):
        dist_matrix[0][i] = dist_matrix[0][i-1] + distance(str1[i],str2[0])
    for j in range(1,len_str2):
        dist_matrix[j][0] = dist_matrix[j-1][0] + distance(str1[0],str2[j])
    for i in range(len_str1):
        for j in range(len_str2):
            dist_matrix[j][i] = min(dist_matrix[j][i-1],dist_matrix[j-1][i],dist_matrix[j-1][i-1]) + distance(str1[i],str2[j])
    return dist_matrix[len_str2-1][len_str1-1]/ min(len_str1,len_str2)


def distance( s1, s2):
    return 1 if s1 == s2 else 0

def remove_similar_phrase(phrase):
    result = []
    for i in range(len(phrase)):
        for ph in result:
            if dtw(ph,phrase[i]) <0.6:
                result.append(phrase[i])
        for j in range(i+1,len(phrase)):
            if dtw(phrase[i],phrase[j]) > 0.6:
                if len(phrase[i]) > len(phrase[j]):
                    result.remove(phrase[i])
                    result.append(phrase[j])
    return result



phrase = read_in('C:\Users\Administrator\Desktop\IR_PPhackthon\phrase')
distinct_phrase = remove_similar_phrase(phrase)

output = open('distinct_phrase','w')
for line in distinct_phrase:
    output.writelines(line)
output.close()

