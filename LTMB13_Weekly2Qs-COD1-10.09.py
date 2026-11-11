# Word Frequency Counter:
class WordFrequencyCounter:
    def preprocess_text(self, text: str) -> list:
        import re
        clean_text = re.sub(r'[^\w\s]', '', text.lower())
        return clean_text.split()

    def compute_word_frequency(self, words: list) -> dict:
        dicts = {}
        for word in words:
            if word in dicts:
                dicts[word] += 1
            else:
                dicts[word] = 1
        return dicts

    def get_most_frequent_word(self, freq_dict: dict) -> tuple:
        freq_dict = {}

        most_frequent_word = None
        highest_frequency = 0

        for word, frequency in freq_dict.items():
            if frequency > highest_frequency:
                most_frequent_word = word
                highest_frequency = frequency

        return (most_frequent_word, highest_frequency)

    def filter_words_by_frequency(self, freq_dict: dict, n: int) -> dict:
        dict = {}

        for count in freq_dict:
            if freq_dict[count] >= n:
                dict[count]= freq_dict[count]
        return dict
         