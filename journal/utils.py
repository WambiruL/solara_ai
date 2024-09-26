import re
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords

import nltk
nltk.download('stopwords')

def extract_keywords(content):
    # Clean the content
    content = re.sub(r'\W+', ' ', content)  # Remove non-word characters
    content = content.lower()  # Convert to lowercase

    # Tokenize and remove stop words
    stop_words = set(stopwords.words('english'))
    words = content.split()
    keywords = [word for word in words if word not in stop_words and len(word) > 1]

    # Use CountVectorizer to identify the most common words
    vectorizer = CountVectorizer(max_features=5)
    vectorizer.fit([' '.join(keywords)])  # Fit on the keywords joined together
    keywords = vectorizer.get_feature_names_out()  # Get the feature names (keywords)

    return ' '.join(keywords)  # Return keywords as a space-separated string
