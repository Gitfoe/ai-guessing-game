from whoosh.index import create_in
from whoosh.fields import *

# https://whoosh.readthedocs.io/en/latest/index.html

# Here, the structure of index entries is defined. You can add more fields with metadata, computed values etc.,
# and use them for searching and ranking.
# We only use a title and a text.
#
# The "stored" attribute is used for all parts that we want to be able to fully retrieve from the index

schema = Schema(title=TEXT(stored=True), content=TEXT)

# Create an index in the directory indexdr (the directory must already exist!)
ix = create_in("practice/project1/indexdir", schema)
writer = ix.writer()

# If you only want to use an index for searching, use:
#from whoosh import index
#ix = index.open_dir("indexdir")

# now let's add some texts (=documents)
writer.add_document(title=u"First document", content=u"This is the first document we've added!")
writer.add_document(title=u"Second document", content=u"The second one is even more interesting!")
writer.add_document(title=u"Songtext", content=u"Music was my first love and it will be the last")

# write the index to the disk
writer.commit()

# Retrieving data
from whoosh.qparser import QueryParser
with ix.searcher() as searcher:
    # find entries with the words 'first' AND 'last'
    query = QueryParser("content", ix.schema).parse("first last")
    results = searcher.search(query)
    
    # print all results
    for r in results:
        print(r)