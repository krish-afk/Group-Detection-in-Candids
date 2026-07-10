 `Once you download the code, please remove the placeholder text files in backend/outputs, backend/uploads and backend/temp`
 `Also download the model dat file from the following link into the backend/model folder: [https://github.com/tzutalin/dlib-android/blob/master/data/shape_predictor_68_face_landmarks.dat]`

# Group Detection in Candids

Automatically detect social groups in candid event photos using computer vision, face recognition, and graph-based clustering.

This project was developed to organize large collections of candid photographs by identifying people who frequently appear together. Instead of manually sorting thousands of event images, the system builds relationships between detected individuals across photos and clusters them into meaningful groups that can be used for yearbooks, event albums, and personalized photo experiences.

---

## Overview

The pipeline combines modern computer vision techniques with graph algorithms to discover naturally occurring social groups from image collections.

The workflow consists of:

1. Detect faces in every image.
2. Generate facial embeddings for each detected person.
3. Match identities across multiple photos.
4. Build a weighted co-occurrence graph.
5. Apply graph clustering/community detection.
6. Visualize detected groups and their associated images.

---

## Features

- Face detection from candid photographs
- Face embedding generation
- Identity matching across images
- Graph construction based on co-occurrence
- Community detection for group discovery
- Visualization of detected groups
- Modular pipeline for experimentation

---

## Pipeline

```text
Input Images
      │
      ▼
Face Detection
      │
      ▼
Face Embeddings
      │
      ▼
Identity Matching
      │
      ▼
Co-occurrence Graph
      │
      ▼
Community Detection
      │
      ▼
Detected Social Groups
```

---

## Technologies Used

- Python
- OpenCV
- face_recognition / dlib
- NetworkX
- NumPy
- Pandas
- Matplotlib
- Scikit-learn

---

## Project Structure

```text
.
├── data/                 # Input images and metadata
├── embeddings/           # Face embeddings
├── graph/                # Graph construction utilities
├── clustering/           # Community detection algorithms
├── visualization/        # Graph and group visualization
├── notebooks/            # Experiments
├── outputs/              # Generated results
└── main.py               # Entry point
```

*(Adjust folders if your repository structure differs.)*

---

## How It Works

### 1. Face Detection

Each image is processed to locate all visible faces.

### 2. Face Recognition

Detected faces are converted into numerical embeddings, allowing the same individual to be recognized across different images.

### 3. Graph Construction

Each unique person becomes a node in a graph. Whenever two individuals appear together in a photograph, an edge is added or strengthened between them.

### 4. Community Detection

Graph clustering algorithms identify tightly connected communities that represent real-world friend groups or social circles.

### 5. Visualization

The discovered communities can be visualized alongside representative photos for easier interpretation.

---

## Example Applications

- Yearbook photo organization
- Event photo management
- Wedding photo grouping
- Corporate event albums
- Sports team media organization
- Personalized photo recommendations

---

## Future Improvements

- Temporal information from event timelines
- Pose-aware grouping
- Multi-camera event support
- Graph Neural Networks for improved clustering
- Interactive visualization dashboard
- Automatic group labeling

---

## Motivation

Large events often generate thousands of candid photographs, making manual organization difficult and time-consuming. This project leverages computer vision and graph-based machine learning to automatically discover meaningful social groups, significantly reducing the effort required to curate event photo collections.

---

## License

This project is intended for research and educational purposes.
