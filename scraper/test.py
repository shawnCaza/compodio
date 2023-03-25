def camel_case_split(str):
    split_words = [[str[0]]]
    for character in str[1:]:
        if split_words[-1][-1].islower() and character.isupper():
            split_words.append(list(character))
        else:
            split_words[-1].append(character)
    return ' '.join([''.join(word) for word in split_words])

print(camel_case_split('FoodFarm Talk'))