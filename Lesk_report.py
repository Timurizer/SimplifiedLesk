import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import senseval

word = ''
context = ''

# stopwords
unwanted = set(nltk.corpus.stopwords.words("english"))
unwanted.update(list('!"#$%&\'()*+,-./:;<=>? @[\]^_`{|}~£'))


# method for getting all context words
def get_context(word, context):
    result = [i for i in nltk.word_tokenize(context.lower()) if i not in unwanted and i != word]
    return result


# method for getting a tag of a word within the context
def get_word_tag(word, context):
    result = ''
    tagged = nltk.pos_tag(nltk.word_tokenize(context.lower()))
    for i in tagged:
        if i[0] == word:
            result = i[1]
    print(tagged)
    return result


# map tags to WordNet part of speech names
def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return wn.ADJ
    elif tag.startswith('V'):
        return wn.VERB
    elif tag.startswith('N'):
        return wn.NOUN
    elif tag.startswith('R'):
        return wn.ADV
    else:
        return ''


# gets all the senses for the word of given part of speech
def get_all_senses(word, part_of_speech):
    pos = get_wordnet_pos(part_of_speech)
    senses = wn.synsets(wn.morphy(word), pos=pos)
    if len(senses) == 0:
        senses = wn.synsets(wn.morphy(word))
    return senses


# lesk itself
def simplified_lesk(word, sentence):
    tag = get_word_tag(word, sentence)
    senses = get_all_senses(word, tag)
    context_words = get_context(word, context)

    if len(senses) == 0:
        print("Something went wrong")
    # in case of only one sense
    if len(senses) == 1:
        return senses[0]

    max_overlap = 0
    best_sense = senses[0]

    for sense in senses:
        examples = wn.synset(sense.name()).examples()
        example_words = ''

        for example in examples:
            example_words += example + " "
        example_words = get_context(word, example_words)

        overlap = overlaping(example_words, context_words)

        if max_overlap < overlap:
            max_overlap = overlap
            best_sense = sense

    return best_sense


# method for counting overlap
def overlaping(x, y):
    count = 0
    for num in y:
        if num in x:
            count += 1
    return count


def test(instances, context_size):
    matched = 0
    progress = 0

    for inst in senseval.instances()[:instances]:
        context = ""
        p = inst.position
        left = ' '.join(w for (w, t) in inst.context[p - context_size:p])
        word = ' '.join(w for (w, t) in inst.context[p:p + 1])
        right = ' '.join(w for (w, t) in inst.context[p + 1:p + context_size])
        senses = ' '.join(inst.senses)

        context += left + " " + word + " " + right
        print(context)

        lesk_result = simplified_lesk(word, context)

        if senses == "HARD1" and lesk_result.name() == 'difficult.a.01':
            matched += 1
        if senses == "HARD2" and lesk_result.name() == 'hard.a.02':
            matched += 1
        if senses == "HARD3" and lesk_result.name() == 'hard.a.03.hard':
            matched += 1

        progress += 1
        print("PROGRESS: " + str(progress))
        print()

    return matched / instances


print("accuracy " + str(test(300, 7)))
