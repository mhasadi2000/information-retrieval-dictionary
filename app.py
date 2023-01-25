import json,re,operator
from hazm import * #Normalizer / stopwords_list  / Stemmer  / word_tokenize
from intersect import intersection
stopwords_list = stopwords_list()
  


def readFile(filename):
    f = open(filename)
    data = json.load(f)  
    f.close()
    return data


def createPossitionalIndex() :
    for docId in data :
        content = data[docId]['content'] 
        normalized = Normalizer().normalize(content)
        for position,word in enumerate(word_tokenize(normalized)):
            if word not in stopwords_list and len(word) != 1 :
                word = Stemmer().stem(word)
                
                if word in possitional_index:
                            
                    # Check if the word existed in that DocID before.
                    if docId in possitional_index[word]:
                        possitional_index[word][docId].append(position)
                            
                    else:
                        possitional_index[word][docId] = [position]
                else:
                    possitional_index[word] = {}
                    possitional_index[word][docId] = [position]
        
def createRankedMap(InList, notInList):
    
    final_map = {}
    for sbl in InList :
        for key in sbl :
            if key in final_map and final_map[key] == -1:
                continue
            if key in final_map :
                final_map[key] += 1
            else :
                final_map[key] = 1
                
    for nsbl in notInList :
        for key in nsbl :
            if key in final_map and final_map[key] == -1:
                continue
            else:
                final_map[key] = -1
    return final_map

def parseEntry(input) :
    freeTexts = []
    nots = []
    phrases = []
    free = ""
    i=0
    while i < len(input):
        if input[i] == '\"':
            i+=1
            in_phrase = ""
            while input[i] != '\"':
                in_phrase += input[i]
                i+=1
            phrases.append(in_phrase)
            i+=1
            continue
        if input[i] == '!':
            i+=1
            not_word = ""
            while i != len(input) and input[i] != ' ' :
                not_word += input[i]
                i+=1
            nots.append(not_word)
            i+=1
            continue
        if input[i] != ' ':
            free += input[i]
        else : 
            if free != "":
                freeTexts.append(free)
                free = ""
        i+=1
    if free != "":
        freeTexts.append(free)
    return freeTexts,nots,phrases


def SeperateListForRanking(freeTexts,nots,phrases):
    InList = []
    notInList = []
    for item in freeTexts :
        stemmed = Stemmer().stem(item)
        try :
            if item not in stopwords_list:
                InList.append(list(possitional_index[stemmed].keys()))
        except :
            pass
    for item in phrases:
        final_list = []
        try:
            wordsOfPhrase = item.split(' ')
            if len(wordsOfPhrase) == 1:
                return possitional_index[wordsOfPhrase[0]].keys()
            first = wordsOfPhrase[0]
            second = wordsOfPhrase[1]
            first = Stemmer().stem(first)
            second = Stemmer().stem(second)
            shared_docs = intersection(possitional_index[first].keys(),possitional_index[second].keys())
            for docId in shared_docs:
                first_possitional = possitional_index[first][docId]
                second_poses = possitional_index[second][docId]
                for pos in range(len(second_poses)):
                    second_poses[pos] -=1
                doc_intersect = intersection(first_possitional,second_poses)
                if len(doc_intersect) != 0:
                    final_list.append(docId)
        except Exception as e:
            print(e)
        InList.append(final_list)
    for item in nots :
        stemmed = Stemmer().stem(item)
        try :
            if item not in stopwords_list:
                notInList.append(list(possitional_index[stemmed].keys()))
        except :
            pass
    return InList,notInList


possitional_index = {}
data = readFile('IR_data_news_12k.json')
createPossitionalIndex()
j=0
while 1:
    
    query = input("Enter the query : ")
    if query == '0':
        break

    freeTexts,nots,phrases = parseEntry(query)

    InList, notInList = SeperateListForRanking(freeTexts,nots,phrases)

    rankedResult = createRankedMap(InList,notInList)

    rankedResult = dict(sorted(rankedResult.items(), key=operator.itemgetter(1),reverse=True))

    x=0
    for docId in rankedResult:
        rank = rankedResult[docId]
        if rank > 0 :
            print("عنوان:",data[docId]['title'])
            print(data[docId]['content'])
        x+=1
        if x == 5:
            break
    j+=1
    print("----****----****-----****-----****-----****-----****---- end of ",j,"attempt")


