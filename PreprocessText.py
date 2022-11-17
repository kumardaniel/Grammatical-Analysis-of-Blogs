import os
from string import punctuation
import re
import nltk
import contractions


# Read Text from the extracted data
class TextReader():
    def read_text(self, path:str):
        with open(path, "r") as f:
            content = f.read()
        return content



# Word Level Analysis of Text(Syllables)
class WordAnalysis():
    def __init__(self):
        self.NUMBERS = re.compile(r"\d")

    def count_syllables(self, word: str) -> int:
        try:
            word = word.strip().lower().strip(punctuation)
            if not word:
                return 0
            if self._contains_numbers(word):
                return 0

            # compound words like self-care
            r = re.match("([^-]+)-(.+)", word)
            if r:
                s1 = self.count_syllables(r.group(1))
                s2 = self.count_syllables(r.group(2))

                if s1 == 0 or s2 == 0:
                    return 0
                else:
                    return s1 + s2

            return self.num_syllables(word)
        except:
            return 0


    def num_syllables(self, word: str) -> int:
        syllable_count = 0
        vowels = "aeiouy"       # Including y as a vovel considering linguistics

        # When a vovel is found at beginning of word, it is considered as syllable
        if word[0] in vowels:
            syllable_count += 1

        for index in range(1, len(word)):

            # Every time a vovel comes after consonant, syllable count is increased
            if word[index] in vowels and word[index - 1] not in vowels:
                syllable_count += 1

        if word.endswith("e") or word.endswith("es") or word.endswith("ed"):
            syllable_count -= 1
        if word.endswith("le") and len(word) > 2 and word[-3] not in vowels:
            syllable_count += 1
        if syllable_count == 0:
            syllable_count += 1
        return syllable_count


    def _contains_numbers(self, word: str) -> bool:
        return bool(self.NUMBERS.search(word))
    
    def isComplex(self, word: str) -> bool:
        return self.count_syllables(word) > 2
    
    def get_syllables_count_list(self, word_list):
        return list(map(lambda x: self.count_syllables(x), word_list))

    def get_complex_word_count(self, word_list):
        return len(list(filter(lambda x: self.isComplex(x), word_list)))



# Find Pronouns in the Text Data
class PersonalPronouns():
    def __init__(self) -> None:
        self.ppn_pattern = '(I|we|We|WE|My|MY|my|OURS|Ours|ours|us)'

    def get_ppn_dict(self, text) -> dict:
        personal_pronouns = {}
        for match in re.finditer(self.ppn_pattern, text):
            ppn = match.group()
            if(ppn != 'I'):
                ppn = ppn.lower()
            if(personal_pronouns.get(ppn) is None):
                personal_pronouns[ppn] = 1
            else:
                personal_pronouns[ppn] += 1
        return personal_pronouns



# Preprocessing Class implementing all the above
class TextPreprocessing():
    def __init__(self) -> None:
        self.tokenizer = nltk.WhitespaceTokenizer()
        self.personal_pn = PersonalPronouns()
        self.word_analyser = WordAnalysis()
        self.text_reader = TextReader()

        self.STOPWORDS = []
        self.POSITIVE_WORDS = []
        self.NEGATIVE_WORDS = []

        for stopwords_file in os.listdir('./Input Data/StopWords'):
            with open(('./Input Data/Stopwords/'+stopwords_file), "r") as f:
                for line in f:
                    line = line.replace("\n", " ")
                    line = re.sub(r'[^\w\s]',' ',line)
                    line = line.split()
                    for word in line:
                        self.STOPWORDS.append(word)


        with open(('./Input Data/MasterDictionary/positive-words.txt'), "r") as f:
            pos_words = f.read()
            pos_words = pos_words.split()
            for word in pos_words:
                self.POSITIVE_WORDS.append(word)


        with open(('./Input Data/MasterDictionary/negative-words.txt'), "r") as f:
                neg_words = f.read()
                neg_words = neg_words.split()
                for word in neg_words:
                    self.NEGATIVE_WORDS.append(word)

    def clean_text(self, text):
        text = text.lower()
        text = contractions.fix(text)
        text = re.sub(r'[^A-Za-z0-9]+', " ", text)
        return text

    def process_text(self, text):
        raw_word_tokenized = self.tokenizer.tokenize(text)
        raw_sent_tokenized = nltk.sent_tokenize(text)
        AVG_NUM_WORDS_PER_SENT = len(raw_word_tokenized) / len(raw_sent_tokenized)
        COMPLEX_WORDS_COUNT = self.word_analyser.get_complex_word_count(raw_word_tokenized)
        COMPLEX_WORDS_PERCENT = COMPLEX_WORDS_COUNT / len(raw_word_tokenized) * 100.0
        FOG_IDX = 0.4 * (AVG_NUM_WORDS_PER_SENT + COMPLEX_WORDS_PERCENT)
        SYLLABLE_PER_WORD = sum(self.word_analyser.get_syllables_count_list(raw_word_tokenized)) / len(raw_word_tokenized)
        PERSONAL_PRONOUNS = self.personal_pn.get_ppn_dict(text)
        text = self.clean_text(text)
        
        return {
            'AVG SENTENCE LENGTH': AVG_NUM_WORDS_PER_SENT,
            'PERCENTAGE OF COMPLEX WORDS': COMPLEX_WORDS_PERCENT,
            'FOG INDEX': FOG_IDX,
            'PERSONAL PRONOUNS': PERSONAL_PRONOUNS,
            'AVG NUMBER OF WORDS PER SENTENCE': AVG_NUM_WORDS_PER_SENT,
            'COMPLEX WORD COUNT': COMPLEX_WORDS_COUNT,
            'SYLLABLE PER WORD': SYLLABLE_PER_WORD,
        }, text
    
    def analyze_text(self, text):
        text_features, text = self.process_text(text)
        tokenized_text = self.tokenizer.tokenize(text)
        WORD_COUNT = len(tokenized_text)
        num_chars = 0
        POSITIVE_SCORE = 0
        NEGATIVE_SCORE = 0
        final_text = ""
        for word in tokenized_text:
            if word in self.STOPWORDS:
                continue
            if word in self.POSITIVE_WORDS:
                POSITIVE_SCORE += 1
            elif word in self.NEGATIVE_WORDS:
                NEGATIVE_SCORE += 1
            final_text += word
            num_chars += len(word)
        AVERAGE_WORD_LENGTH = num_chars / WORD_COUNT
        POLARITY_SCORE = (POSITIVE_SCORE - NEGATIVE_SCORE) / (POSITIVE_SCORE + NEGATIVE_SCORE + 0.000001)
        SUBJECTIVITY_SCORE = (POSITIVE_SCORE + NEGATIVE_SCORE) / (len(tokenized_text) + 0.000001)
        text_features['POSITIVE SCORE'] = POSITIVE_SCORE
        text_features['NEGATIVE SCORE'] = NEGATIVE_SCORE
        text_features['WORD COUNT'] = WORD_COUNT
        text_features['AVG WORD LENGTH'] = AVERAGE_WORD_LENGTH
        text_features['POLARITY SCORE'] = POLARITY_SCORE
        text_features['SUBJECTIVITY SCORE'] = SUBJECTIVITY_SCORE
        return text_features

    def get_features_from_urlId(self, urlId):
        path = f"./Extracted Text/{urlId}.txt"
        if(not os.path.exists(path)):
            return None
        text = self.text_reader.read_text(path)
        return self.analyze_text(text)