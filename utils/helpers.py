import re

#this func simply remove some emojes from transactions categories like "Food [emoji of food]"
def remove_emojis(text):
    emoji_pattern = re.compile(
        pattern="[" +
        u"\U0001F600-\U0001F64F" +
        u"\U0001F300-\U0001F5FF" +
        u"\U0001F680-\U0001F6FF" +
        u"\U0001F1E0-\U0001F1FF" +
        u"\U00002600-\U000026FF" +
        u"\U00002700-\U000027BF" +
        "]+",
        flags=re.UNICODE)
    return emoji_pattern.sub(r'', text).strip()