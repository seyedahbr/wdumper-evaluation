import sys
import re
import requests
from SPARQLWrapper import JSON, SPARQLWrapper
from wordcloud import WordCloud
import matplotlib.pyplot as plt


def search_file_for_ids(file_path):
    ids = []
    pattern = r'<http://www\.wikidata\.org/prop/direct/(\w+)>'

    with open(file_path, 'r') as file:
        for line in file:
            matches = re.findall(pattern, line)
            if matches:
                ids.extend(matches)
    return ids

def fetch_label_from_wikidata(p_id):
    user_agent = "RQSSFramework Python/%s.%s" % (
        sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper(
        "https://query.wikidata.org/sparql", agent=user_agent)
    sparql.setQuery('''SELECT ?itemLabel WHERE {{BIND(wd:{0} AS ?item) SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" }}}}'''.format(p_id))
    try:
        sparql.setReturnFormat(JSON)
        data = sparql.query().convert()
        bindings = data['results']['bindings']
        if bindings:
            label = bindings[0]['itemLabel']['value']
            return label

    except Exception as e:
        print('\t\t ERROR: ', e)
    return None


file_path = sys.argv[1]

print('Fetching the statement P-ids...')
found_ids = search_file_for_ids(file_path)

id_labels = dict.fromkeys(found_ids)

print('Fetching the Pid labels from Wikidata...')
for p_id in id_labels:
    label = fetch_label_from_wikidata(p_id)
    if label:
        id_labels[p_id] = label
    else:
        print(f"{p_id}: Label not found")

print('Plotting the chart...')

words_text = ' '.join(['"{}"'.format(id_labels[word]) for word in found_ids])

wordcloud = WordCloud(width=800, height=800, background_color='white', collocations = False).generate(words_text)

plt.figure(figsize=(4, 4))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.savefig('{0}.png'.format(sys.argv[1]), format='png')

print('DONE. image saved in: ','{0}.png'.format(sys.argv[1]))

