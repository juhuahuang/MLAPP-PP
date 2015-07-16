__author__ = 'Administrator'

def top_k_word(path):
    ff = open(path)
    key_word=[]
    for line in ff:
        tmp = line.strip().split(' ')
        key_word.append({tmp[0] : [float(tmp[1]),tmp[2]]})
    key_word.sort(cmp=lambda x,y: cmp  (x.values()[0], y.values()[0]),reverse=True)
    return key_word




key_word = top_k_word('tfidf_word_renter_review')
print key_word[:10]