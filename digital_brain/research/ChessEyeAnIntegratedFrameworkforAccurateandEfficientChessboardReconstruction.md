# ChessEye: An Integrated Framework for Accurate and Efficient Chessboard Reconstruction

©2023 IEEE

**Abstract**
This research paper presents a novel and generalizable approach for precisely detecting and identifying the configuration of pieces on both 2D and 3D chessboard images with different chess sets and varying background contexts. It makes a significant milestone in the digitalization of the chess world by enabling the recreation of physical chess boards on computer screens using a single image. It also provides a framework for real-time tracking and visualization of live chess games using video frames obtained directly from the camera. The novelty lies in the methodology that achieves remarkable accuracy through four key steps: (1) identifying the corner points of the chessboard, (2) detecting the chess pieces, (3) localizing the pieces within the chessboard, and (4) evaluating the position with the best possible variations. The introduction of the Fisher Linear Discriminant Analysis-based dynamic thresholding technique contributes to the perfect 100% accuracy in distinguishing between the white and black chess pieces. The entire algorithm undergoes a thorough experimentation and evaluation process, confirming the effectiveness and versatility of the proposed approach.

**Index Terms—** chessboard reconstruction, chess piece recognition, keypoint detection, transfer learning, YOLO

## I. INTRODUCTION

Chess is a highly popular sport that captivates individuals of all ages. The advancement of computer programs has made developing chess skills easier and more effective. However, a major limitation is that virtual chessboards are often incompatible with physical chess sets used during practice, leading to a tedious process of manually updating virtual boards to match physical ones for analysis.

This paper proposes a new approach to identify the corners of the chessboard by using a keypoint detector trained on multiple images taken and annotated from different scenarios rather than relying on image processing techniques. For chess piece detection, multiple state-of-the-art models, including YOLOv5, YOLOv8, and YOLO-NAS [10] are trained and evaluated. The best-performing model is selected based on mean Average Precision (mAP) and inferencing speeds. Based on the feedback from the two models, the chessboard in the captured image is reconstructed on a virtual screen and passes through the verification algorithm to ensure compliance with chess rules. The verified position is then analyzed by a chess engine.

## II. DATASET

The research team captured a diverse dataset, including various chess sets and piece arrangements in different lighting conditions and camera angles, including top-down and angled views. The dataset includes frames from live chess broadcasts, online platforms (chess.com, lichess, chess24), and open-source datasets (Roboflow universe). The dataset was annotated for both keypoint detection (corners) and object detection (pieces).

## III. CORNER POINTS DETECTION MODEL

The initial step is detecting the chessboard edges to crop the image for piece detection. Keypoint detection was identified as the best solution over contour detection or color segmentation, especially for unseen environments.

### A. Dataset Preparation
Data augmentation (brightness, contrast, rotation, zoom) expanded the dataset by 3x. Split: 70% training, 15% validation, 15% testing.

### B. Model
The model uses ResNet-152v2 as a backbone with fixed weights, followed by trained convolutional layers with ReLU activations to output 8 values (x, y for 4 corners). Input size: 250x250 pixels. Optimizer: Adam (lr=0.001). Loss: Mean Square Error.

### C. Results
Training for 300 epochs yielded a Mean Square Error of 0.0008 on the training set. The model successfully identifies corners in diverse scenarios, including 2D/3D boards and varying color schemes.

## IV. CHESS PIECE DETECTION

### A. Dataset Preparation
Data augmentation and active learning were used. Images with incorrect/incomplete detections from an initial YOLOv8x model were manually annotated.

### B. Model
YOLOv5, YOLOv8, and YOLO-NAS (medium sizes) were trained to identify 6 classes of chess pieces (Pawn, Knight, Bishop, Rook, Queen, King).

**Table I: Chess Piece Detection Performance Comparison**

| Model | mAP@0.5 | mAP@[0.5:0.9] | Speed CPU (ms) | Speed GPU (ms) |
| :--- | :--- | :--- | :--- | :--- |
| **YOLOv5** | **0.992** | **0.794** | 545.1 | 19.9 |
| YOLOv8 | 0.992 | 0.755 | 445.3 | 17.1 |
| YOLO-NAS | 0.987 | 0.769 | 380.7 | 14.3 |

YOLOv5 was selected for deployment due to superior detection capabilities, despite slightly slower inference speeds than YOLO-NAS.

### C. Results
The model reliably detects pieces across different chess sets and orientations.

### D. Dynamic Thresholding to Separate Pieces into White and Black Groups
Instead of training for 12 classes (6 pieces x 2 colors), the model detects the piece type, and color is determined by a dynamic thresholding technique based on mean pixel value within the bounding box. This resulted in **100% accuracy** in color separation.

## V. CHESS BOARD RECONSTRUCTION

1.  Identify corner points.
2.  Add margins (15%) to avoid cutting off pieces.
3.  Generate perspective view.
4.  Detect pieces and map to the 8x8 grid based on overlap.

## VI. POSITION VERIFICATION AND EVALUATION

The reconstructed position is verified against chess rules:
1.  No two pieces of same color on same square.
2.  Total pieces < 32.
3.  Exactly one King per side.
4.  Kings not adjacent.
5.  Pawns <= 8 per side.
6.  No pawns on first/last rows.
7.  Valid number of promoted pieces.

Verified positions are converted to FEN and analyzed by Stockfish 15.1.

## VII. INTERACTIVE MOBILE APPLICATION

The system is implemented as a mobile app where users capture images, which are processed on a server. Results (recommended moves) are displayed on the device.

## VIII. LIMITATIONS

*   Difficulty with multiple chessboards in one image.
*   Reduced accuracy on unique/unseen chess sets.
*   Requires all 4 corners to be visible.

## IX. CONCLUSIONS AND FUTURE WORK

The proposed "ChessEye" framework effectively digitizes physical chessboards for analysis. Key contributions include using keypoint detection for corners and dynamic thresholding for color classification. Future work includes real-time move recording and integration with robotic arms.

## REFERENCES
[1] G. Sala et al., 'Checking the “Academic Selection” argument...', *Intelligence*, 2017.
[2] A. P. Burgoyne et al., 'The relationship between cognitive ability and chess skill...', *Intelligence*, 2016.
[3] R. McIlroy-Young et al., 'Aligning Superhuman AI with Human Behavior...', *KDD*, 2020.
[4] D. Silver et al., 'A general reinforcement learning algorithm...', *Science*, 2018.
[10] J. R. Terven and D. M. Cordova-Esparaza, 'A Comprehensive Review of YOLO...', 2023.
[15] K. He et al., 'Identity mappings in deep residual networks', *ECCV*, 2016.
[19] J. Redmon et al., 'You Only Look Once...', *CVPR*, 2016.
[21] R. A. Fisher, 'The use of multiple measurements in taxonomic problems', *Annals of Eugenics*, 1936.
