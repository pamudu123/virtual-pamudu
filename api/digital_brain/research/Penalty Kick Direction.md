# Predicting Penalty Kick Direction Using Multi-Modal Deep Learning with Pose-Guided Attention

**Pasindu Ranasinghe** (University of New South Wales) and **Pamudu Ranasinghe** (Virtusa / University of Moratuwa)

**Abstract**
This study presents a real-time, multi-modal deep learning framework for predicting penalty kick direction (left, middle, right) before ball contact. The model uses a dual-branch architecture: MobileNetV2 for visual spatial features and an LSTM network for 2D pose keypoints. A pose-guided attention mechanism directs focus to relevant regions. The model achieves **89% accuracy** with an inference time of **22 ms**, making it suitable for real-time analytics and goalkeeper training.

**Keywords:** Penalty kick prediction, sports analytics, multi-modal learning, computer vision, action recognition

## 1. Introduction

Penalty kicks are pivotal moments in football. Predicting the outcome is challenging due to the variability of human performance. While AI and computer vision have advanced sports analytics, predicting penalty kick direction remains difficult. This paper proposes a framework fusing visual context and pose dynamics to interpret complex spatial dynamics like run-up angle and body posture.

## 2. Related Work

Deep learning (CNNs, LSTMs) is increasingly used in football analytics for player tracking and action spotting. Previous penalty analysis studies used techniques like localized object detection or isolated pose estimation. Our approach integrates both visual scene context and detailed pose dynamics in a unified, real-time framework to capture fine-grained biomechanical cues.

## 3. Methodology

### 3.1 Dataset Creation
*   **Penalty Kick Events:** 755 distinct events extracted from 154 match videos and 12 full matches. Annotated for final ball position (Left, Middle, Right).
*   **Object Detection Dataset:** ~6,300 frames annotated for Shooter, Goalkeeper, Net, and Ball to train a YOLOv8 model.
*   **Input Sequence:** 8 frames selected uniformly from the run-up phase. The sequence ends just before ball contact, determined by a normalized distance threshold between the kicker's foot and the ball.
*   **Pose Keypoints:** 17 body keypoints extracted using YOLOv8-Pose.

### 3.2 Neural Network Architecture
The model processes two parallel streams:
1.  **Spatial Feature Branch (Visual):** MobileNetV2 extracts features from RGB frames.
2.  **Skeletal Feature Branch (Pose):** LSTM processes 2D keypoint sequences to model biomechanics.
3.  **Pose-Guided Spatial Attention:** Uses pose information to create dynamic attention maps, guiding the visual branch to focus on relevant areas (e.g., kicking foot, body orientation).
4.  **Late Fusion:** Concatenates summary vectors from both branches for final classification using a Softmax layer.

Total Parameters: 57 million.

### 3.3 Training
*   **Optimizer:** Adam (lr=0.001)
*   **Loss:** Categorical Crossentropy
*   **Epochs:** 100 (with early stopping)

## 4. Results and Evaluation

### 4.1 Object Detection
YOLOv8 achieved **mAP@0.5 of 0.935**, ensuring reliable tracking of key elements.

### 4.2 Prediction Performance
*   **Impact of Distance Threshold:** The best accuracy (**89.38%**) was achieved with a threshold of 0.15 (closest to ball contact), capturing critical biomechanical cues.
*   **Ablation Study:**
    *   Visual-only: 75.22%
    *   Pose-only: 68.14%
    *   Dual-branch (no attention): 82.30%
    *   **Proposed (with attention): 89.38%**

The results confirm that fusing modalities and adding attention significantly improves performance. Attention maps correctly highlighted the kicking foot and surrounding context.

### 4.3 Inference Pipeline
The end-to-end pipeline (Object Detection -> Pose Estimation -> Sequence Extraction -> Prediction) runs in **22 milliseconds** on an RTX 4080 GPU.

## 5. Discussion

The model effectively learns player-specific cues (approach angle, trunk orientation). It performs significantly above chance even with earlier run-up phases (threshold 0.35), suggesting potential for early anticipation training for goalkeepers. The lightweight design allows for real-time applications in training and analytics.

## 6. Limitations
*   Dependent on clear visibility (camera angles, occlusions).
*   Limited to 3 broad direction categories.
*   Generalizability across different leagues needs further testing.

## 7. Conclusion

We introduced a fast (22ms), accurate (89%) multi-modal framework for penalty kick prediction. By combining visual features with pose-guided attention, the model offers a powerful tool for sports analytics and training.

## References
[1] Zheng, F. et al., 'A Review of Computer Vision Technology for Football Videos', *Information*, 2025.
[3] Pinheiro, G.D.S. et al., 'Body Pose Estimation...', *Frontiers in Sports and Active Living*, 2022.
[8] Chakraborty, D. et al., 'Deep Learning-Based Prediction...', *ICCIT*, 2023.
[10] Secco Faquin, B. et al., 'Prediction of ball direction...', *J Sports Sci*, 2023.
