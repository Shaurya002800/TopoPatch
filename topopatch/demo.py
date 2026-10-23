"""Small authored functional fixture; not a representative retrieval benchmark."""
def fixture():
    docs = [
        {'id':'car-guide','text':'car maintenance fix engine oil brakes'},
        {'id':'car-shopping','text':'automobile purchase dealer price warranty'},
        {'id':'doctor-care','text':'doctor care diagnosis treatment appointment'},
        {'id':'medical-jobs','text':'physician recruitment career hospital salary'},
        {'id':'dog-care','text':'dog feeding exercise training health'},
        {'id':'pet-shop','text':'canine purchase shop accessories toys'},
        {'id':'password-policy','text':'password safe account access authentication policy'},
        {'id':'password-blog','text':'credentials tips account login convenience blog'},
        {'id':'cat-care','text':'cat feeding grooming health veterinary'},
        {'id':'cat-toys','text':'feline toys play shop purchase'},
    ]
    for i in range(30):
        docs.append({'id':f'archive-{i:02d}', 'text':f'archive record {i} astronomy geology history mathematics research'})
    queries = [
        {'id':'q-car','text':'car fix engine','required':'car-guide','max_rank':2},
        {'id':'q-doctor','text':'doctor diagnosis treatment','required':'doctor-care','max_rank':2},
        {'id':'q-dog','text':'dog feeding training','required':'dog-care','max_rank':2},
        {'id':'q-policy','text':'password account policy','required':'password-policy','max_rank':1},
    ]
    progress = ['automobile repair engine', 'physician diagnosis treatment', 'canine feeding training', 'feline grooming health']
    return {'documents':docs,'protected_queries':queries,'progress_queries':progress}
