import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import (  # Dropout,; MaxPool2D,
    AveragePooling2D,
    Conv2D,
    Dense,
    Flatten,
    InputLayer,
    Reshape,
)
from tensorflow.keras.models import Sequential

from climetlab import load_source

# from tensorflow.python.keras.backend import one_hot


years = list(range(1979, 1979+4))

PARAMS = (
    129,
    134,
    136,
    137,
    139,
    140121,
    140122,
    140123,
    140124,
    140125,
    140126,
    140127,
    140128,
    140129,
    140207,
    140208,
    140209,
    140211,
    140212,
    140214,
    140215,
    140216,
    140217,
    140218,
    140219,
    140220,
    140221,
    140222,
    140223,
    140224,
    140225,
    140226,
    140227,
    140228,
    140229,
    140230,
    140231,
    140232,
    140233,
    140234,
    140235,
    140236,
    140237,
    140238,
    140239,
    140244,
    140245,
    140249,
    140252,
    140253,
    140254,
    141,
    142,
    143,
    144,
    145,
    146,
    147,
    148,
    15,
    151,
    159,
    16,
    160,
    161,
    162,
    162053,
    162054,
    162059,
    162060,
    162061,
    162062,
    162063,
    162064,
    162065,
    162066,
    162067,
    162068,
    162069,
    162070,
    162071,
    162072,
    162073,
    162074,
    162075,
    162076,
    162077,
    162078,
    162079,
    162080,
    162081,
    162082,
    162083,
    162084,
    162085,
    162086,
    162087,
    162088,
    162089,
    162090,
    162091,
    162092,
    163,
    164,
    165,
    166,
    167,
    168,
    169,
    17,
    170,
    172,
    175,
    176,
    177,
    178,
    179,
    18,
    180,
    181,
    182,
    183,
    186,
    187,
    188,
    195,
    196,
    197,
    198,
    205,
    206,
    207,
    208,
    209,
    210,
    211,
    212,
    213,
    228,
    228001,
    228003,
    228007,
    228008,
    228009,
    228010,
    228011,
    228012,
    228013,
    228014,
    228015,
    228016,
    228017,
    228018,
    228019,
    228021,
    228022,
    228023,
    228024,
    228029,
    228088,
    228089,
    228090,
    228129,
    228130,
    228131,
    228132,
    228217,
    228218,
    228219,
    228220,
    228221,
    228246,
    228247,
    228251,
    229,
    230,
    231,
    232,
    235,
    235020,
    235021,
    235023,
    235024,
    235025,
    235026,
    235027,
    235029,
    235030,
    235031,
    235032,
    235033,
    235034,
    235035,
    235036,
    235037,
    235038,
    235039,
    235040,
    235041,
    235042,
    235043,
    235045,
    235046,
    235047,
    235048,
    235049,
    235050,
    235051,
    235052,
    235053,
    235054,
    235055,
    235056,
    235057,
    235058,
    235059,
    235068,
    235069,
    235070,
    236,
    238,
    239,
    240,
    243,
    244,
    245,
    26,
    260015,
    260121,
    260123,
    27,
    28,
    29,
    30,
    31,
    32,
    33,
    34,
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    44,
    45,
    48,
    50,
    57,
    59,
    66,
    67,
    74,
    78,
    79,
    8,
    9,
)

s = load_source(
    "cds",
    "reanalysis-era5-single-levels-monthly-means",
    variable="all",
    year=years,
    month=list(range(1, 13)),
    time=0,
    product_type="monthly_averaged_reanalysis",
    grid=[1, 1],
    split_on="year",
)

print(s.sources[0].path)


dataset = s.to_tfdataset(label="paramId")

if False:
    first = next(dataset.take(1).as_numpy_iterator())
    avg = first[0]
    std = first[0]
    cnt = 1
    for d in dataset.skip(1).as_numpy_iterator():
        avg = avg + d[0]
        std = std + d[0] ** 2
        cnt += 1

    avg /= cnt
    std = avg ** 2 - std / cnt
    print(std)
# assert False

# first = next(dataset.take(1).as_numpy_iterator())
# mn = np.min(first[0])
# mx = np.max(first[0])
# cnt = 1
# for d in dataset.skip(1).as_numpy_iterator():
#     mn = min(mn, np.min(first[0]))
#     mx = max(mx, np.max(first[0]))
#     cnt += 1

# print(cnt, mn, mx)

# def normalize(data, year):
#     return (data-avg)/std , year

N_PARAMS = len(PARAMS)

PARAMS = tf.lookup.StaticHashTable(
    initializer=tf.lookup.KeyValueTensorInitializer(
        keys=tf.constant(PARAMS, dtype=tf.int64),
        values=tf.constant(list(range(N_PARAMS)), dtype=tf.int64),
    ),
    default_value=tf.constant(-1, dtype=tf.int64),
    name="paramId",
)


def one_hot(data, paramId):
    return data, tf.one_hot(PARAMS.lookup(paramId), N_PARAMS, name="paramId", axis=-1)


# def prepare(data, year):
#     return (data - mn) / (mx - mn), tf.one_hot(year - 1979, nyears)


print(dataset.element_spec)

dataset = dataset.shuffle(1024)
# dataset = dataset.map(normalize)
dataset = dataset.map(one_hot)
# dataset = dataset.map(prepare)

dataset = dataset.cache()
dataset = dataset.batch(N_PARAMS)
dataset = dataset.prefetch(tf.data.AUTOTUNE)


for n in dataset.take(1):
    print(n)
# assert False
shape = dataset.element_spec[0].shape
print(shape)

model = Sequential()
model.add(InputLayer(input_shape=(shape[-2], shape[-1])))

model.add(Reshape(target_shape=(shape[-2], shape[-1], 1)))
model.add(Conv2D(64, 2))
model.add(AveragePooling2D((10, 10)))

model.add(Flatten())
model.add(Dense(64, activation="relu"))
# model.add(Dropout(0.2))
model.add(Dense(N_PARAMS, activation="softmax"))
print(model.summary())
model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"],
)


print(model.summary())

split = 1
print(split)
validation = dataset.take(split)
train = dataset.skip(split)

# p = 0
# for _ in train.as_numpy_iterator():
#     p += 1

# print(p)


model.fit(
    train,
    epochs=1000,
    verbose=1,
    validation_data=validation,
    callbacks=[
        EarlyStopping(
            # monitor="val_accuracy",
            patience=10,
        )
    ],
)
# model.evaluate(test)
