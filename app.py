from flask import Flask, request
from flask_restful import Resource, Api, reqparse
# from flask_jwt import JWT, jwt_required, current_identity
# from security import authenticate, identity
########################################################################
# Data Initialization
########################################################################
import pandas as pd
import numpy as np
import cPickle

## Fragrance Dictionary
with open('pickles/frags_gnbnn.pkl','r') as frg:
    frags = cPickle.load(frg)

## Notes matrix: fragrance_id rows x note_name columns
with open('pickles/notes_matrix.pkl','r') as f_obj:
    notes_matrix = cPickle.load(f_obj)
    notes_matrix = notes_matrix.rename_axis('fragrance_id').rename_axis('note_name', axis='columns')
    # print len(notes_matrix)
    # notes_matrix.head()

## Ratings table: Each unique rating is given a separate row
#Load the ratings data into a dataframe
ratings_table = pd.read_csv('csv/ratings.csv', sep=',', encoding='latin-1')

## Notes matrix: fragrance_id rows x note_name columns
### Minimum of 10 ratings and 60% positive
with open('pickles/notes_matrix_min.pkl','r') as f_obj:
    notes_matrix_min = cPickle.load(f_obj)
notes_matrix_min = notes_matrix_min.rename_axis('fragrance_id').rename_axis('note_name', axis='columns')

## Olfactory Groups matrix
### All Fragrances
with open('pickles/groups_matrix.pkl','r') as f_obj:
    groups_matrix = cPickle.load(f_obj)
    groups_matrix = groups_matrix.rename_axis('fragrance_id').rename_axis('group_name', axis='columns')
    # print len(groups_matrix)
    # groups_matrix.head()

########################################################################
# Knowledge-Based Recommender
### User Notes Vector Definition

# a user enters preferred olfactory notes
# # a vector is created for these notes
# # the recommender returns the closest matches to that vector

def user_notes_vector(user_notes_list, frag_id = 0, user_entered = True):
    user_notes = {}
    for note_tuple in user_notes_list:
        user_notes[note_tuple[0]] = note_tuple[1]
    user_notes_list = []
    notes_list = []
    for name in list(notes_matrix.columns.values):
        notes_list.append(name)
        if name in user_notes:
            if user_entered:
                if user_notes[name] == 3:
                    user_notes_list.append(1)
                elif user_notes[name] == 1:
                    user_notes_list.append(-1)
            else:
                user_notes_list.append(user_notes[name])
        else:
            user_notes_list.append(0)
    user_notes_series = pd.Series(user_notes_list, index = notes_list)
    user_notes_v = user_notes_series.values.reshape(1,-1)
    return user_notes_v

u_notes_list = []
notes_vector = user_notes_vector(user_notes_list = u_notes_list, frag_id = 0, user_entered = True)

### Find Similar Fragrances, based on User Notes Vector
from sklearn.metrics.pairwise import cosine_similarity

def similars(user_notes_vector, notes_matrix, frag_id = 0, rating = 3, count = 10, popular=False):
    total = 0
    recs = []
    for note in np.nditer(user_notes_vector):
        total += note
    if total == 0 and frag_id != 0:
        recs.append([frags[frag_id]['brand'],
                frags[frag_id]['name'],
                'Not enough note definition to provide recommendation'] + [frag_id])
    cs_ndarray = cosine_similarity(notes_matrix, user_notes_vector)
    cs_df = pd.DataFrame(data = cs_ndarray)
    cs_series = cs_df.T.squeeze()
    cs_sort = cs_series.sort_values(ascending=False)
    print 'frag_id= ' + str(frag_id)
    if frag_id == 0:
        if popular:
            reason = 'note preferences: popular fragrances'
        else:
            reason = 'note preferences'
    else:
        reason = frags[frag_id]['name']
    if total != 0 and rating == 3:
        for i in range(count):
            print 'i= ' + str(i)
            n = cs_sort.index[i]
            print 'n= ' + str(n)
            num = str(frags[notes_matrix.iloc[n].name]['number'])
            if notes_matrix.iloc[n].name == '26149458':
                print 'YES for her!!!'
            if notes_matrix.iloc[n].name == '26131702':
                print 'YES for him!!!'
            print 'num= ' + str(num)
            if num != frag_id:
                recs.append([frags[notes_matrix.iloc[n].name]['brand'],
                        frags[notes_matrix.iloc[n].name]['name'],
                        reason] + [num])
                # print '%-30s' % frags[notes_matrix.iloc[n].name]['brand'] + '|' \
                #         + '%-30s' % frags[notes_matrix.iloc[n].name]['name'] + '|' \
                #         + '%-30s' % reason
    return recs


j = ''
for k in range(3):
    for i in range(30):
        j += '_'
    j += '|'

# print 'All fragrances:               |'
# print j[:30] + '|' + j[:30] + '_' + j[:30]
# print '%-30s' % 'Brand' + '|' \
#         + '%-30s' % 'Name' + '|' \
#         + '%-30s' % 'Similarity' + '|'
# print j

similars(user_notes_vector = notes_vector, notes_matrix = notes_matrix, count=10)
# print
# print 'Popular fragrances:           |'
# print j[:30] + '|' + j[:30] + '_' + j[:30]
# print '%-30s' % 'Brand' + '|' \
#         + '%-30s' % 'Name' + '|' \
#         + '%-30s' % 'Similarity' + '|'
# print j

similars(user_notes_vector = notes_vector, notes_matrix = notes_matrix_min, count=10, popular=True)


########################################################################
# Content-Based Recommender
### Create Fragrance Vectors, then Find Similar Fragrances
### Use Knowledge-Based Recommender Functions
# a user enters preferred fragrances
# a vector is created for these fragrances
# the recommender returns the closest matches to that vector

frag_list = []

# print '%-30s' % 'Brand' + ' ' \
#         + '%-30s' % 'Name' + ' ' \
#         + '%-30s' % 'Similarity'
j = ''
for k in range(3):
    for i in range(30):
        j += '_'
    j += ' '
# print j

columns = list(notes_matrix_min.columns.values)

for frag in frag_list:
    notes_tuple_list = []
    notes_list = list(notes_matrix.loc[frag[0]].values)
    for i in range(len(notes_list)):
        new_tuple = (columns[i], notes_list[i])
        notes_tuple_list.append(new_tuple)
    notes_vector = user_notes_vector(user_notes_list = notes_tuple_list, frag_id = frag[0], user_entered = False)
    similars(user_notes_vector = notes_vector, notes_matrix = notes_matrix_min, 
             frag_id = frag[0], rating = frag[1], count=4)
########################################################################
# Collaborative-Filter Recommender
### Create User Ratings Vector and Add to the Full Dataset of Ratings
### Calculate Estimated Ratings of All Fragrances, based on User-User Collaborative Filtering
### Return the Fragrances with Highest Estimated Ratings
########################################################################
from surprise import SVD, Reader, Dataset


def cf_predict_dict(frag_list, ratings_table):
    reader = Reader()
    user_rating = []
    for rating in frag_list:
        user_rating.append(['0', rating[0], rating[1]])
    user_rating_df = pd.DataFrame(user_rating, columns=['user_id','frag_id','rating'])

    for r_tuple in frag_list:
        user_data_series = pd.Series(['0', r_tuple[0], r_tuple[1]], index = ['user_id', 'frag_id', 'rating'])
        user_data_df = pd.DataFrame(user_data_series).transpose()

    data = Dataset.load_from_df(ratings_table[['user_id', 'frag_id', 'rating']], reader)
    data.split(n_folds=5)
    svd = SVD()
    trainset = data.build_full_trainset()
    svd.train(trainset)

    ratings_table = ratings_table.append(user_rating_df, ignore_index=True)
    predict_dict = {}
    for frag in ratings_table['frag_id']:
        predict_dict[frag] = svd.predict('0',frag).est
    return predict_dict
########################################################################
import pprint
import operator

predict_dict = cf_predict_dict(frag_list, ratings_table)
sorted_predict = sorted(predict_dict.items(), key=operator.itemgetter(1), reverse=True)

def cf_predict(frags, sorted_predict, count):
    recs = []
    for i in range(count):
        if frags[str(sorted_predict[i][0])]['group'] is None:
            frags[str(sorted_predict[i][0])]['group'] = 'Undefined'
        # sorted_notes = sorted(frags[str(sorted_predict[i][0])]['notes'].items(), 
        #                       key=operator.itemgetter(1), reverse=True)
        recs.append([frags[str(sorted_predict[i][0])]['brand'],
                frags[str(sorted_predict[i][0])]['name'],
                frags[str(sorted_predict[i][0])]['group'],
                str(frags[str(sorted_predict[i][0])]['number'])])
    return recs
########################################################################
print 'begin flask'
app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True # To allow flask propagating exception even if debug is set to false on app
app.secret_key = 'jose'
from flask_cors import CORS
api = Api(app)
CORS(app)

# jwt = JWT(app, authenticate, identity)

items = []

def knowledge_based_recs():
    global u_notes_list
    global notes_matrix
    if len(u_notes_list) == 0:
        return
    notes_vector = user_notes_vector(user_notes_list = u_notes_list, frag_id = 0, user_entered = True)
    return similars(user_notes_vector = notes_vector, notes_matrix = notes_matrix, count=10)

def knowledge_based_recs_pop():
    global u_notes_list
    global notes_matrix_min
    if len(u_notes_list) == 0:
        return
    notes_vector = user_notes_vector(user_notes_list = u_notes_list, frag_id = 0, user_entered = True)
    return similars(user_notes_vector = notes_vector, notes_matrix = notes_matrix_min,
            count=10, popular=True)

def content_based_recs():
    global frag_list
    global notes_matrix
    global notes_list
    global user_notes_list
    global notes_matrix_min
    sims = []
    for frag in frag_list:
        notes_tuple_list = []
        notes_list = list(notes_matrix.loc[frag[0]].values)
        for i in range(len(notes_list)):
            new_tuple = (columns[i], notes_list[i])
            notes_tuple_list.append(new_tuple)
        notes_vector = user_notes_vector(user_notes_list = notes_tuple_list, frag_id = frag[0], user_entered = False)
        sims.append(similars(user_notes_vector = notes_vector, notes_matrix = notes_matrix_min, 
                 frag_id = frag[0], rating = frag[1], count=4))
    return sims

def collaborative_filtering_recs():
    predict_dict = cf_predict_dict(frag_list, ratings_table)
    sorted_predict = sorted(predict_dict.items(), key=operator.itemgetter(1), reverse=True)
    recs = cf_predict(frags, sorted_predict, count=10)
    return recs

def create_new_list(old_list, item = '10210001', prefs = -1):
    # prefs = -1 --> remove all and return empty list
    new_list = []
    if prefs == -1:
        return new_list
    # prefs = 0 --> remove
    # (always remove before adding)
    for item_tuple in old_list:
        if item_tuple[0] != item:
            new_list.append(item_tuple)
    # prefs = 1 --> add to dislike
    # prefs = 3 --> add to likes
    if prefs == 1 or prefs == 3:
        new_list.append((item, prefs))
    return new_list

class Item(Resource):
    global frag_list
    global u_notes_list
    parser = reqparse.RequestParser()
    # parser.add_argument('price',
    parser.add_argument('typ',
        type=int,
        required=False,
        help="type 1 is fragrance, type 2 is note"
    )
    parser.add_argument('prefs',
        type=int,
        required=False,
        help="prefs -1 is clear all, 0 is remove, 1 is dislike, 3 is like"
    )


    # @jwt_required()
    def get(self, name):
        if name == '1':
            # knowledge-based recs
            return knowledge_based_recs()
        elif name == '2':
            # knowledge-based recs popular
            return knowledge_based_recs_pop()
        elif name == '3':
            # content-based recs
            return content_based_recs()
        elif name == '4':
            # collaborative filtering
            return collaborative_filtering_recs()
        # return {'item': next(filter(lambda x: x['name'] == name, items), None)}

    def post(self, name):
        if next(filter(lambda x: x['name'] == name, items), None) is not None:
            return {'message': "An item with name '{}' already exists.".format(name)}

        data = Item.parser.parse_args()

        item = {'name': name, 'price': data['price']}
        items.append(item)
        return item

    # @jwt_required()
    def delete(self, name):
        global items
        items = list(filter(lambda x: x['name'] != name, items))
        return {'message': 'Item deleted'}


    # @jwt_required()
    @app.route("/")
    def put(self, name):
        global create_new_list
        global frag_list
        global u_notes_list
        # prefs == -1: # clear all
        # prefs == 0: # remove
        # prefs == 1: # dislike
        # prefs == 3: # like
        data = Item.parser.parse_args()
        print 'data = ' + str(data)
        # item = {'name': name, 'price': data['price']}
        # name = str(name)
        typ = data['typ']
        print 'typ= ' + str(typ)
        prefs = data['prefs']
        print 'prefs= ' + str(prefs)
        print 'assign change_list'
        print 'old_list = '
        if typ == 1: # fragrance id
            print frag_list
            frag_list = create_new_list(old_list = frag_list, item = name, prefs = prefs)
            return frag_list
        elif typ == 2: # note id
            print u_notes_list
            u_notes_list = create_new_list(old_list = u_notes_list, item = name, prefs = prefs)
            print 'new_list = '
            print u_notes_list
            return u_notes_list
        # # Once again, print something not in the args to verify everything works
        print 'inside put'
        # item = next(filter(lambda x: x['name'] == name, items), None)
        # if item is None:
        #     item = {'name': name, 'price': data['price']}
        #     items.append(item)
        # else:
        #     item.update(data)
        # change_dict = dict(change_list)
        # return item

class ItemList(Resource):
    def get(self):
        return {'items': frag_list}
        # return {'items': items}

api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)  # important to mention debug=True
