from django.template.defaulttags import register

@register.filter
def get_item_in_dict(dictionary, key):

    try:
        KEY2 = key.split(",")[0]

        if KEY2==key:
            value=dictionary.get(key)
            return value
        else:
            VALUE2 = key.split(",")[1]
            value=dictionary[KEY2][VALUE2]
            print value
            return value
    except Exception as e:
        print e