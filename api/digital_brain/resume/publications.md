---
id: resume_publications
type: resume_section
section: publications
source: resume
confidence: high
---

## AI Approach for FRA Based Condition Assessment
**Source:** [AI_Approach_for_FRA Based_Condition_Assessment.md](../research/AI_Approach_for_FRA%20Based_Condition_Assessment.md)

This research proposes an automated Artificial Intelligence framework to assess the mechanical integrity of power transformers using Frequency Response Analysis (FRA). Traditionally, interpreting FRA signatures requires expert human analysis. We developed a Deep Learning model using Convolutional Neural Networks (CNNs) that treats FRA plots as images to classify various mechanical faults (e.g., axial displacement, bushing faults) with high accuracy. This approach significantly reduces the expertise barrier and potential for human error in transformer condition monitoring.

## ChessEye: Integrated Framework for Chessboard Reconstruction
**Source:** [ChessEyeAnIntegratedFrameworkforAccurateandEfficientChessboardReconstruction.md](../research/ChessEyeAnIntegratedFrameworkforAccurateandEfficientChessboardReconstruction.md)

"ChessEye" is a novel framework capable of digitizing physical chessboards from a single 2D image. The system uses a unique keypoint detection algorithm to accurately locate board corners and a custom YOLOv5 model for piece detection. A standout feature is the dynamic thresholding technique which achieves 100% accuracy in distinguishing black vs. white pieces. The framework was successfully deployed as a mobile app, allowing users to analyze real-world board positions digitally in real-time.

## Hybrid Y-Net Architecture for Singing Voice Separation
**Source:** [Hybrid YNet.md](../research/Hybrid%20YNet.md)

We introduced "Y-Net," a novel deep learning architecture for separating vocals from music tracks. Unlike traditional models that rely solely on spectrograms or raw audio, Y-Net employs a dual-branch encoder to extract features from *both* domains simultaneously. These features are fused in a shared decoder to generate high-quality vocal tracks. The model outperformed standard U-Net architectures and other state-of-the-art baselines on the MUSDB18 dataset, demonstrating superior signal-to-distortion ratios (SDR) with a more efficient parameter count.

## Low-Light Enhancements for Autonomous Driving (ICIIS)
**Source:** [ICIIS_LowLight.md](../research/ICIIS_LowLight.md)

To improve the safety of autonomous vehicles at night, we developed **LLE_UNET**, a lightweight deep learning model that enhances low-light video in real-time. The model uses a U-Net architecture with Convolutional Block Attention Modules (CBAM) to brighten dark scenes while preserving details. Optimized for edge computing, it achieved ~20 FPS on an NVIDIA Jetson Nano. Testing showed it significantly improves the accuracy of downstream object detection systems (like YOLO) in night-time driving scenarios, surpassing existing benchmarks in both image quality (PSNR/SSIM) and inference speed.

## Predicting Penalty Kick Direction with Multi-Modal Deep Learning
**Source:** [Penalty Kick Direction.md](../research/Penalty%20Kick%20Direction.md)

This study presents a real-time AI system that predicts the direction of a penalty kick (Left, Middle, Right) *before* the player strikes the ball. The model fuses two data streams: visual footage (processed by MobileNetV2) and body pose biomechanics (processed by LSTM). By using a novel pose-guided attention mechanism, the system learns to focus on critical cues like the plant foot angle and hip rotation. The system achieves 89% prediction accuracy with a latency of just 22ms, offering a powerful tool for goalkeeper training and live match analytics.
