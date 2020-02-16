from re import search

STOP_ROWS = ['-->', '\n']
STOP_WORDS = ['-', '\n', '&', '']
STOP_PUNCTUATION = ['\n', '.', '?', '!', ',', ':', '\"', '&']
APOSTROPHE = '\''


def parse_text(path, isfile=True):

    def create_list_rows(data, stop_rows):
        rows = list()
        if isfile is True:
            file = open(str(data), 'r')
            for row in file:
                split_row = row.split(' ')
                rows.append(split_row)
            file.close()
        else:
            rows.append(data.split(' '))
        clear_rows = list()
        for row in rows:
            clear_rows.append(row)
            for stop_row in stop_rows:
                if stop_row in row:
                    clear_rows.pop()
        return clear_rows

    def create_word_list(row_list, stop_words, stop_punctuation, apostrophe=APOSTROPHE):
        words = list()
        for row in row_list:
            for word in row:
                for stop_mark in stop_punctuation:
                    if stop_mark in word:
                        word = word.replace(stop_mark, '')
                    if apostrophe in word:
                        word = ''
                words.append(word)
                for stop_word in stop_words:
                    if stop_word == word:
                        words.pop()
        for word in words:
            if search('[0-9]', word):
                words.pop(words.index(word))
        for word in words:
            if word[0] == '-':
                words[words.index(word)] = word[1:]
            if word[-1] == '-':
                words[words.index(word)] = word[:-1]
        return words

    def get_unique_words(word_list):
        words_lowercase = [x.lower() for x in word_list]
        unique_words = set(words_lowercase)
        word_frequency = list()
        for unique_word in unique_words:
            word_frequency.append((unique_word, words_lowercase.count(unique_word)))
        word_frequency.sort(key=lambda i: i[1])
        return word_frequency

    list_rows = create_list_rows(path, STOP_ROWS)
    list_words = create_word_list(list_rows, STOP_WORDS, STOP_PUNCTUATION)
    list_unique_words = get_unique_words(list_words)
    return list_unique_words
