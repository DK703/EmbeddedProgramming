"""Feature Engineering (bring your implementation from Challenge 1)

Copy your completed features.py from tech_assignment_challenge_1/scripts/features.py here,
or implement it fresh. The train.py script imports engineer_features() from this module.

If you haven't completed Challenge 1 yet, a reference implementation is available in
the lab tutorial's scripts/step3_features.py.
"""
'''
raise NotImplementedError(
    "Copy your features.py from Challenge 1 into this file.\n"
    "  cp ../tech_assignment_challenge_1/scripts/features.py scripts/features.py"
)
'''

import sys
import os
import numpy as np
import pandas as pd
from collections import deque

sys.path.insert(0, os.path.dirname(__file__))
from clean import clean_data

PIXEL_COLS = [f"pixel_{i}" for i in range(64)]


def _largest_connected_component(grid, threshold):
    """Find the largest connected region of pixels > threshold in an 8x8 grid.

    Use BFS (breadth-first search) with 4-directional connectivity
    (up, down, left, right — no diagonals).

    Args:
        grid: 8x8 numpy array of temperature values.
        threshold: Pixels must be strictly greater than this to be "hot".

    Returns:
        int: Size of the largest connected component of hot pixels.
             Returns 0 if no pixels exceed the threshold.

    Hint:
        - Use a visited[][] array to track which cells you've already checked
        - For each unvisited hot pixel, do a BFS to find all connected hot pixels
        - Track the size of each component, keep the largest
        - The grid is small (8x8 = 64 cells) so efficiency doesn't matter
    """
    # TODO: Implement BFS to find the largest connected component
    # The basic algorithm:
    #   1. Create a visited array (8x8, all False)
    #   2. For each cell (r, c) in the grid:
    #      - If already visited or grid[r][c] <= threshold, skip
    #      - Otherwise, start a BFS from (r, c):
    #        a. Create a queue, add (r, c), mark visited
    #        b. While queue not empty:
    #           - Pop (cr, cc), increment size counter
    #           - Check 4 neighbors (up/down/left/right)
    #           - If neighbor is in-bounds, not visited, and > threshold:
    #             mark visited and add to queue
    #      - Update largest if this component's size is bigger
    #   3. Return largest
    rows, cols = 8,8
    visited =[[False for _ in range(cols)] for _ in range(rows)]
    #print(visited[1][1])
    largest = 0

    for row in range(rows):
        for cell in range(cols):
            #print(cell)
            if visited[row][cell] or grid[row][cell] <= threshold:
                continue
            size = 0
            q = deque([(row, cell)]) #creates a deque
            visited[row][cell] = True #marks visited!
            while q:
                cr, cc = q.popleft()
                size += 1
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < 8 and 0 <= nc < 8 and not visited[nr][nc] and grid[nr][nc] > threshold:
                        visited[nr][nc] = True
                        q.append((nr, nc))
                    if largest < size:
                        largest =size

            
    return largest

    pass  # Replace with your implementation


def compute_spatial_features(raw_row):
    """Compute 8 spatial features from a single 64-element raw pixel row.

    Args:
        raw_row: numpy array of shape (64,) — raw temperature values.

    Returns:
        numpy array of shape (8,) containing:
            [spatial_gradient, largest_blob, quadrant_var, center_vs_edge,
             row_profile_std, col_profile_std, hot_centroid_r, hot_pixel_ratio]

        REQUIRED: spatial_gradient (A), largest_blob (B),
                  quadrant_var (C), center_vs_edge (D),
                  row_profile_std / col_profile_std (E)
        EXTRA CREDIT: hot_centroid_r / hot_pixel_ratio (F)
        Unimplemented features default to 0.0.
    """
    grid = raw_row.reshape(8, 8)
    median = np.median(raw_row)
    threshold = median + 3.0

    # TODO A [REQUIRED]: spatial_gradient
    # Compute the mean absolute difference between horizontal neighbors
    # (grid[:, 1:] vs grid[:, :-1]) and vertical neighbors
    # (grid[1:, :] vs grid[:-1, :]). Average the two means.
    # This measures how "sharp" the temperature transitions are.
    horizontalDifference = np.mean(np.abs(grid[:, 1:] - grid[:,:-1]))
    verticalDifference = np.mean(np.abs(grid[1:, :] - grid[:-1,:]))

    spatial_gradient = (horizontalDifference+verticalDifference)/2  # Replace with your implementation

    # TODO B [REQUIRED]: largest_blob
    # Use your _largest_connected_component function to find the largest
    # connected region of pixels > threshold (4-directional connectivity).
    # A person creates a contiguous warm region; random noise does not.
    #largest_blob = 0
    largest_blob = _largest_connected_component(grid, threshold)  # Replace with your implementation

    # TODO C [REQUIRED]: quadrant_var
    # Split the 8x8 grid into four 4x4 quadrants:
    #   top-left:     grid[:4, :4]
    #   top-right:    grid[:4, 4:]
    #   bottom-left:  grid[4:, :4]
    #   bottom-right: grid[4:, 4:]
    # Compute the mean of each quadrant (4 values).
    # Return the variance of those 4 means.
    # This detects if heat is concentrated in one area vs spread evenly.
    top_left = grid[:4, :4]
    top_right = grid[:4, 4:]
    bottom_left =  grid[4:, :4]
    bottom_right = grid[4:, 4:]

    tlmean = np.mean(top_left)
    trmean = np.mean(top_right)
    blmean = np.mean(bottom_left)
    brmean = np.mean(bottom_right)
    #print(tlmean)
    #print(trmean)
    #print(blmean)
    #print(brmean)
    
    meanarray = np.array([tlmean,trmean,blmean,brmean])
    #print(meanarray)
    
    quadrant_var = np.var(meanarray)
    #quadrant_var = np.var(tlmean, trmean, blmean, brmean)  # Replace with your implementation

    # TODO D [REQUIRED]: center_vs_edge
    # Compute: mean(center 4x4 region) - mean(outer ring pixels)
    # Center region: rows 2-5, cols 2-5 (i.e., grid[2:6, 2:6])
    # Outer ring: all other pixels (the border)
    # Hint: Use a boolean mask — True for outer, False for center.
    centerarray = grid[2:6,2:6]
    
    #use where to get the values
    outerarray = np.empty([0])

    #outerindex = np.where(grid != centerarray, True, False)
   #print(outerindex)
    #find it difficult to get the mask condition if its center, so i just
    #write my own array

    #64-16=48

    #first 2 rows
    outerarray = np.append(grid[0],grid[1])
    #print("outerarray top:")
    #print(outerarray)

    for r in range (4):
        for c in range (2):
            outerarray = np.append(outerarray, grid[r+2,c])
    #print("outerarray left:")
    #print(outerarray)

    
    for r in range (4):
        for c in range (2):
            outerarray = np.append(outerarray, grid[r+2,c+6])


    #print("outerarray right:")
    #print(outerarray)

    outerarray = np.append(outerarray,grid[6])
    outerarray = np.append(outerarray,grid[7])

    #print(outerarray.size)
    center_vs_edge = np.mean(centerarray)-np.mean(outerarray)  # Replace with your implementation

    # TODO E [REQUIRED]: row_profile_std and col_profile_std
    # Take the max value in each row → 8 values → compute their std.
    # Do the same for columns.
    # If a person is present, the row/column maxima will vary more
    # (some rows/cols have the person, others don't).

    rowmax = np.array([np.max(grid[0]),np.max(grid[1]),np.max(grid[2]),np.max(grid[3]),np.max(grid[4]),np.max(grid[5]),np.max(grid[6]),np.max(grid[7])])
    colmax = np.array([np.max(grid[:,0]),np.max(grid[:,0]),np.max(grid[:,1]),np.max(grid[:,2]),np.max(grid[:,3]),np.max(grid[:,4]),np.max(grid[:,5]),np.max(grid[:,6]),np.max(grid[:,7])])
    row_profile_std =np.std(rowmax)  # Replace with your implementation
    col_profile_std = np.std(colmax)  # Replace with your implementation

    # TODO F [EXTRA CREDIT]: hot_centroid_r and hot_pixel_ratio
    # Find all pixels > threshold ("hot pixels").
    # Compute the centroid (mean row, mean col) of the hot pixels.
    # hot_centroid_r = euclidean distance from centroid to grid center (3.5, 3.5)
    # hot_pixel_ratio = count of hot pixels / 64
    # If no hot pixels exist, set hot_centroid_r = 0.
    #
    # Hint: np.where(grid > threshold) returns (row_indices, col_indices)

    maskarray = np.where(grid > threshold)
    #print(maskarray[0])
    #print(maskarray[1])

    #for r in range(maskarray[0].size):
        #print(maskarray[0], maskarray[1])
        #print(r)
       
    hot_centroid_r = 0.0  # Replace with your implementation
    hot_pixel_ratio = 0.0  # Replace with your implementation

    return np.array([
        spatial_gradient, largest_blob, quadrant_var, center_vs_edge,
        row_profile_std, col_profile_std, hot_centroid_r, hot_pixel_ratio,
    ], dtype=np.float32)


def engineer_features(df):
    """Engineer all 76 features from cleaned DataFrame.

    Args:
        df: Cleaned DataFrame with pixel_0..pixel_63 and label columns.

    Returns:
        tuple: (X, y) where X has shape (n_samples, 76) and y has shape (n_samples,)
    """
    pixels = df[PIXEL_COLS].values.astype(np.float32)

    # === Part A: Ambient Normalization (64 features) ===
    # The AMG8833 readings vary with room temperature (ambient).
    # A 25C room and a 30C room produce completely different raw values
    # for the same scene. Normalize each sample relative to its own
    # ambient baseline so features are comparable across environments.
    #
    # TODO: Compute per-row median and std across the 64 pixels.
    #       Then normalize: (pixel - median) / std
    #       Guard against division by zero: clamp std to min 0.1
    #
    # Hint:
    #   medians = np.median(pixels, axis=1, keepdims=True)  # shape: (n_samples, 1)
    #   stds = np.std(pixels, axis=1, keepdims=True)        # shape: (n_samples, 1)
    #   stds[stds < 0.1] = 0.1  # prevent division by zero
    #   normalized = (pixels - medians) / stds              # shape: (n_samples, 64)
    medians = np.median(pixels, axis=1, keepdims=True)   # shape: (n_samples, 1) — Replace with your implementation
    stds = np.std(pixels, axis=1, keepdims=True)       # shape: (n_samples, 1) — Replace with your implementation
    stds[stds < 0.1] = 0.1
    normalized = (pixels - medians) / stds # shape: (n_samples, 64) — Replace with your implementation
    #print(normalized.shape)

    # === Part B: Intensity Statistics (4 features) ===
    # These capture "how hot is the hottest pixel" and "how many pixels
    # are significantly above ambient" — signals that a warm body is present.
    #
    # TODO: Compute the following (each should be shape (n_samples, 1)):
    #   row_max:       maximum pixel value in each row (sample)
    #   row_range:     max - min pixel value in each row
    #   count_above_3: number of pixels more than 3 degrees above median
    #   count_above_5: number of pixels more than 5 degrees above median
    #
    # Hint: Use axis=1, keepdims=True for row_max
    #   row_max = pixels.max(axis=1, keepdims=True)
    #   For counts, use boolean comparison:
    #     (pixels > (medians + 3.0)).sum(axis=1).reshape(-1, 1)
    row_max = pixels.max(axis=1, keepdims=True)       # Replace with your implementation
    #print("row max")
    #print(row_max)
    #print("row min")
    
    row_min = pixels.min(axis=1, keepdims=True) 
    #print(row_min)
    row_range = row_max - row_min     # Replace with your implementation
    #print(row_range)
    count_above_3 = (pixels > (medians + 3.0)).sum(axis=1).reshape(-1, 1) # Replace with your implementation
    count_above_5 = (pixels > (medians + 5.0)).sum(axis=1).reshape(-1, 1) # Replace with your implementation

    # === Part C: Spatial Features (8 features) ===
    spatial = np.array([compute_spatial_features(row) for row in pixels])

    # === Putting everything together ===
    X = np.hstack([normalized, row_max, row_range, count_above_3, count_above_5, spatial])
    y = (df["label"].values == "present").astype(np.float32)

    print(f"Features: {X.shape[1]}, Samples: {len(X)} "
          f"({int(y.sum())} present, {int(len(y) - y.sum())} empty)")
   

    return X, y


if __name__ == "__main__":
    df_clean = clean_data("thermal_dataset.csv")
    X, y = engineer_features(df_clean)

    print(f"\nFeature matrix shape: {X.shape}")
    print(f"Labels shape: {y.shape}")
    print(f"Sample feature vector (first 5): {X[0, :5]}")