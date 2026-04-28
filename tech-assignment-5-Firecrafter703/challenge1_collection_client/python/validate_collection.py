import csv
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

CSV_FILE = "my_collection.csv"
TARGET_EMPTY = 50
TARGET_PRESENT = 50


def load_collection():
    if not os.path.exists(CSV_FILE):
        print(f"Error: {CSV_FILE} not found!")
        sys.exit(1)

    frames = []
    with open(CSV_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pixels = [float(row[f'p{i}']) for i in range(64)]
            row['pixels'] = pixels
            frames.append(row)
    
    print(type(frames))
    return frames


def analyze_collection(frames):
    print("="*50)
    print("Collection Analysis")
    print(f"Target: {TARGET_EMPTY} empty + {TARGET_PRESENT} present = 100 frames")
    print("="*50)

    #variables that store the current empty and present frames
    EMPTY = 0
    PRESENT = 0

    # TODO: Count total frames
    print(f"\nTotal frames:{len(frames)}")

    # TODO: Count frames per label
    print("\nBy label:")

    for row in frames:
        #print((row["label"]))
        if(row["label"] == "empty"):
            EMPTY = EMPTY + 1
        if(row["label"] == "present"):
            PRESENT = PRESENT + 1
        
    
    print(f"  empty:   {EMPTY}/{TARGET_EMPTY}")
    print(f"  present: {PRESENT}/{TARGET_PRESENT}")
    TOTAL = EMPTY + PRESENT
    print(TOTAL)
    # TODO: Check balance status
    if(EMPTY == PRESENT and TOTAL == 100):
        print("\nBalance status: Balanced")
    else:

        print("\nBalance status: Not Balanced")

    # TODO: Find potentially mislabeled frames
    print("\nPotentially mislabeled frames:")
    
    prevrow = []
    for row in frames:
        #print((row["label"]))
        #print(prevrow == row)
        if(prevrow==row):
            print("mislabled row here:")
        prevrow=row
        


def visualize_collection(frames):
    label_counts = {'empty': 0, 'present': 0}
    for frame in frames:
        label = frame['label']
        if label in label_counts:
            label_counts[label] += 1

    fig, ax = plt.subplots(figsize=(8, 6))

    labels = ['Empty', 'Present']
    actual = [label_counts.get('empty', 0), label_counts.get('present', 0)]
    targets = [TARGET_EMPTY, TARGET_PRESENT]

    x = np.arange(len(labels))
    width = 0.35

    ax.bar(x - width/2, actual, width, label='Collected', color=['#2ecc71', '#e74c3c'])
    ax.bar(x + width/2, targets, width, label='Target', color='gray', alpha=0.5)

    ax.set_xlabel('Label')
    ax.set_ylabel('Count')
    ax.set_title('Collection Progress: 50 Empty + 50 Present')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    fig.tight_layout()
    fig.savefig('collection_summary.png', dpi=150)

    print("\nVisualization saved to: collection_summary.png")
    plt.show()


def main():
    frames = load_collection()
    analyze_collection(frames)
    visualize_collection(frames)


if __name__ == "__main__":
    main()
