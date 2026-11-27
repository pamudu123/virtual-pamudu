# Deep Learning based Low Light Enhancements for Advanced Driver-Assistance Systems at Night

**©2023 IEEE. Accepted to be published in: 2023 IEEE 17th International Conference on Industrial and Information Systems (ICIIS), August 25-26, 2023.**

**Abstract**
In the modern automobile industry, autonomous driving systems heavily rely on sensors like cameras to interpret their surroundings. However, their performance is constrained by fluctuating light intensity and shadows. This research develops an effective low-light image enhancement system (LLE_UNET) to improve the perception and interpretability of images in low-light driving environments. The architecture surpasses existing models in real-time suitability, PSNR, and SSIM values while maintaining low resource usage, making it ideal for low-end devices and real-time autonomous driving.

**Index Terms—** Low-Light Image Enhancement, Autonomous Vehicles, Object Detection, Advanced Driver-Assistance System

## I. INTRODUCTION

Advanced Driver-Assistance Systems (ADAS) in autonomous vehicles face challenges in low-light conditions, where sensor data quality is compromised. Deep learning offers solutions to different techniques for low-light image enhancement (LLIE). We propose a novel LLE_UNET model, a lighter U-shaped encoder-decoder network bridged with a Convolution Block Attention Module (CBAM). It is designed to be trained from scratch in low-resource environments and deployed with low latency.

## II. BACKGROUND

Existing research focuses on improving quality, details, and exposure.
*   **MIRNet [4]:** Combines contextual information with high-resolution details.
*   **Zero-DCE [5]:** Estimates image-specific curves without reference images.
*   **EnlightenGAN [10]:** Unsupervised GAN for low-light enhancement.
*   **LLFormer [13]:** Transformer-based method.

Our review indicates a need for models that balance high quality with low computational cost for real-time edge deployment.

## III. METHODOLOGY

### A. Model Architectures
The **LLE_UNET** follows a UNET architecture:
*   **Contracting Path (Encoder):** Uses pre-trained VGG-16 weights to extract features. 2D Convolutional layers with pooling.
*   **Expansive Path (Decoder):** Expands data back to original size.
*   **Bridge:** Convolution Block Attention Module (CBAM) connects encoder and decoder. It uses spatial and channel attention to focus on important details (e.g., dark regions requiring enhancement).
*   **Skip Connections:** Concatenate encoder features with decoder features to reintroduce fine details.

### B. Evaluating Matrices
*   **PSNR (Peak Signal-to-Noise Ratio):** Measures reconstruction quality (higher is better).
*   **SSIM (Structural Similarity Index):** Measures structural similarity (closer to 1 is better).
*   **Loss Function:** **Charbonnier loss** (L1 smooth loss) is used for its robustness to outliers and ability to produce smooth images.

### C. Object Detection for Performance Evaluation
To verify utility, we evaluated object detection accuracy on enhanced images using **YOLOv8**.
*   **Dataset:** Locally collected dataset (vehicles, pedestrians, traffic signs), augmented to 865 images.
*   **Results:** Precision score of ~0.92, indicating effective detection on enhanced images.

### D. Real-Time Embedded System Development
The model was quantized (float16) and converted to TensorFlow Lite (LLE_UNET) and TensorRT (YOLOv8) for deployment on **NVIDIA Jetson Nano**. It achieved ~20 fps.

## IV. RESULTS AND DISCUSSION

**Table III: Performance Comparison**

| Method | PSNR | SSIM |
| :--- | :--- | :--- |
| Retinex-Net | 16.77 | 0.56 |
| Auto-Encoder | 19.72 | 0.70 |
| MIR-Net | 24.14 | 0.83 |
| **Our Method (LLE_UNET)** | **28.715** | **0.8197** |

Our method achieved the highest PSNR and second-highest SSIM (comparable to MIRNet but much faster).

**Table I & IV** (Visual Results): The enhanced images showed significant improvement in clarity and visibility compared to original low-light inputs.
**Table II** (Object Detection): YOLOv8 successfully detected traffic elements in the enhanced images.

**Limitations:**
*   Cannot generate new content/details not present in the original.
*   Not optimized for extreme darkness (0 lux).
*   Intense light sources (headlights) can cause whitish artifacts.

## V. CONCLUSION

The LLE_UNET model surpasses existing models in PSNR, real-time suitability, and low resource usage. It provides an efficient solution for ADAS in low-light conditions.

**GitHub:** [https://github.com/pamudu123/Low_Light_Image_Enhancement](https://github.com/pamudu123/Low_Light_Image_Enhancement)

## REFERENCES
[4] Zamir SW et al., 'Learning enriched features...', *ECCV*, 2020.
[5] Guo C et al., 'Zero-reference deep curve estimation...', *CVPR*, 2020.
[10] Jiang Y et al., 'Enlightengan...', *IEEE Transactions on Image Processing*, 2021.
[14] Guo C et al., 'Zero-reference deep curve estimation...', *CVPR*, 2020.
[17] Zou Z et al., 'Object detection in 20 years...', *Proceedings of the IEEE*, 2023.
