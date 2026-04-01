import os
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

print("=== Quick Model Training ===")

IMAGE_SIZE = 224
BATCH_SIZE = 16
EPOCHS = 3
NUM_CLASSES = 4
CLASS_NAMES = ["Glioma", "Meningioma", "No Tumor", "Pituitary"]
DATA_DIR = "dataset"
TRAIN_DIR = os.path.join(DATA_DIR, "train")
MODEL_PATH = "models/efficientnet_brain_tumor.h5"

os.makedirs(TRAIN_DIR, exist_ok=True)
for c in CLASS_NAMES:
    os.makedirs(os.path.join(TRAIN_DIR, c), exist_ok=True)

print("Generating training images...")
for class_idx, class_name in enumerate(CLASS_NAMES):
    class_dir = os.path.join(TRAIN_DIR, class_name)
    for i in range(30):
        arr = np.random.randint(40, 200, (IMAGE_SIZE, IMAGE_SIZE, 3), dtype=np.uint8)
        
        if class_name == "No Tumor":
            center = IMAGE_SIZE // 2
            for y in range(IMAGE_SIZE):
                for x in range(IMAGE_SIZE):
                    if ((x - center)**2 + (y - center)**2) ** 0.5 < 70:
                        arr[y, x] = [160, 160, 160]
        elif class_name == "Glioma":
            arr[50:100, 60:120] = [70, 70, 70]
        elif class_name == "Meningioma":
            arr[60:100, 70:130] = [90, 90, 90]
        elif class_name == "Pituitary":
            arr[90:120, 90:120] = [80, 80, 80]
        
        Image.fromarray(arr).save(os.path.join(class_dir, f"img_{i}.jpg"))

print("Building model...")
base = keras.applications.EfficientNetB0(weights='imagenet', include_top=False, input_shape=(224,224,3))
base.trainable = False

model = keras.Sequential([
    base,
    layers.GlobalAveragePooling2D(),
    layers.Dropout(0.3),
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(4, activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

train_datagen = keras.preprocessing.image.ImageDataGenerator(rotation_range=15, width_shift_range=0.1, validation_split=0.2)
train_gen = train_datagen.flow_from_directory(TRAIN_DIR, target_size=(224,224), batch_size=BATCH_SIZE, class_mode='categorical', subset='training')
val_gen = train_datagen.flow_from_directory(TRAIN_DIR, target_size=(224,224), batch_size=BATCH_SIZE, class_mode='categorical', subset='validation')

print(f"Training: {train_gen.samples} samples, Validation: {val_gen.samples} samples")
print(f"Classes: {train_gen.class_indices}")

print("\n=== Training ===")
model.fit(train_gen, epochs=EPOCHS, validation_data=val_gen, verbose=2)

print(f"\nSaving to {MODEL_PATH}...")
model.save(MODEL_PATH)
print("Done!")