##
import lance
from tqdm.auto import tqdm
import dbm


def run(*columns):
    for item in dataset.to_table(columns=columns or None).to_batches():
        for row in item.to_pylist():
            yield row

# dataset = lance.dataset("wikidata-5m.lance")
dataset = lance.dataset("wikidata-latest-86m.lance")

##
file_path = 'dict-index.dbm'
with dbm.open(file_path, 'n') as db:
    for i, row in tqdm(enumerate(e['id'] for e in run('id')), total=dataset.count_rows()):
        # db[row['id']] = i
        db[row] = i.to_bytes(4, 'big')
##
with dbm.open(file_path, 'r') as db:
    index = int.from_bytes(db.get('Q43054'), 'big')
    print('Q43054', index)
    print(dataset.take([index]))

##
import pdict

file_path = 'dict-index.pdict'
db = pdict.create(file_path, capacity=dataset.count_rows())
for i, row in tqdm(enumerate(e['id'] for e in run('id')), total=dataset.count_rows()):
    db[row] = i
db.close()

##
import pysos
db = pysos.Dict('dict-index.pysos')
for i, row in tqdm(enumerate(e['id'] for e in run('id')), total=dataset.count_rows()):
    db[row] = i

##
import semidbm
db = semidbm.open('dict-index.semidb', 'c')
for i, row in tqdm(enumerate(e['id'] for e in run('id')), total=dataset.count_rows()):
    db[row] = i.to_bytes(4, 'big')


##
import lmdb

env = lmdb.open('dict-index.lmdb', map_size=dataset.count_rows() * 64, metasync=False, sync=False, map_async=True)
with env.begin(write=True) as txn:
    for i, row in tqdm(enumerate(e['id'] for e in run('id')), total=dataset.count_rows()):
        txn.put(row.encode(), i.to_bytes(4, 'big'))
env.sync(True)

##
import time
test = (
    'Q32043', 'Q353204', 'Q43111453', 'Q48783573', 'Q28036028', 'Q4065799', 'Q111905430', 'Q114507595',
    'Q7509664', 'Q114539448', 'Q59167536', 'Q60465340', 'Q1813536', 'Q70867427', 'Q55527801', 'Q43104343', 'Q33616093',
    'Q107307831', 'Q96695499', 'Q38030741', 'Q113852591', 'Q49156570', 'Q107196626', 'Q180445', 'Q348620', 'Q20505218',
    'Q2349697', 'Q863823', 'Q3664265', 'Q109502754', 'Q43054', 'Q415060', 'Q7002467', 'Q107306040', 'Q57265286',
    'Q80506473', 'Q83414976', 'Q1144851', 'Q80506239', 'Q15749150', 'Q108298349', 'Q85784904', 'Q96328859', 'Q64707422',
    'Q585710', 'Q6738289', 'Q3061805', 'Q111308734', 'Q7099986', 'Q52636577', 'Q113391982', 'Q3475759', 'Q7433565',
    'Q63718105', 'Q96735482', 'Q5281778', 'Q5179164', 'Q5179165', 'Q103355909', 'Q7113656', 'Q81854337', 'Q39379',
    'Q19869428', 'Q15946385', 'Q16191961', 'Q74429827', 'Q81083294', 'Q107324744', 'Q57551858', 'Q19105284', 'Q9684',
    'Q108864820', 'Q33184098', 'Q81565726', 'Q116890502', 'Q25459', 'Q24845', 'Q29779', 'Q24836', 'Q30409', 'Q11349517',
    'Q106465794', 'Q64509195', 'Q1826416', 'Q100698449', 'Q19798707', 'Q12147', 'Q93644472', 'Q45783286', 'Q81147897',
    'Q63487913', 'Q24853885', 'Q57682009', 'Q108678788', 'Q103927524', 'Q6802026', 'Q7640493', 'Q16801251', 'Q55230423',
    'Q30296836', 'Q201296', 'Q54912542', 'Q25440909', 'Q20862018', 'Q89121139', 'Q111469378', 'Q111469952',
    'Q111469864', 'Q45135672', 'Q5074440', 'Q26925044', 'Q924595', 'Q28228677', 'Q5994618', 'Q6063466', 'Q6802026',
    'Q16801251', 'Q7640493', 'Q55230423', 'Q30296836',
)
print(len(test))

##
# 0.0009s for 120
with dbm.open('dict-index.dbm', 'r') as db:
    t1 = time.time()
    results = [
        db.get(key)
        for key in test
    ]
    # dataset.take(results)
    t = time.time() - t1
    print("SELFTIMED:", t)
    print(results)


## >>> # open existing dictionary
db = pdict.Pdict('dict-index.pdict')
t1 = time.time()
results = [
    db.get(key)
    for key in test
]
t = time.time() - t1
print("SELFTIMED:", t)
print(results)
data = dataset.take([v for v in results if v is not None])
print(data)
db.close()
##
# db = pysos.Dict('dict-index.pysos')
print("Loaded")
t1 = time.time()
results = [
    db.get(key)
    for key in test
]
t = time.time() - t1
print("SELFTIMED:", t)
print(results)
data = dataset.take([v for v in results if v is not None])
print(data)
##
# db = semidbm.open('dict-index.semidb', 'r')
print("Loaded")
t1 = time.time()
results = [
    int.from_bytes(db[key], byteorder='big')
    for key in test
]
t = time.time() - t1
print("SELFTIMED:", t)
print(results)
data = dataset.take([v for v in results if v is not None])
print(data)
##
import lmdb
env = lmdb.Environment('dict-index.lmdb', readonly=True )
with env.begin() as txn:
    print("Loaded")
    t1 = time.time()
    results = [
        int.from_bytes(txn.get(key.encode()), byteorder='big')
        for key in test
    ]
    t = time.time() - t1
    print("SELFTIMED:", t)
    print(results)
    data = dataset.take([v for v in results if v is not None])
    print(data)
