# Hybrid Y-Net Architecture for Singing Voice Separation

**arXiv:2303.02599v1 [cs.SD] 5 Mar 2023**

**Abstract**
This research paper presents a novel deep learning-based neural network architecture, named Y-Net, for achieving music source separation. The proposed architecture performs end-to-end hybrid source separation by extracting features from both spectrogram and waveform domains. Inspired by the U-Net architecture, Y-Net predicts a spectrogram mask to separate vocal sources from a mixture signal. Our results demonstrate the effectiveness of the proposed architecture for music source separation with fewer parameters. Overall, our work presents a promising approach for improving the accuracy and efficiency of music source separation.

**Index Terms—** Short-Time Fourier Transform, spectrogram, waveform, U-Net, source separation, Y-Net

## I. INTRODUCTION

Music source separation is a complex task with applications in karaoke, transcription, and production. While spectrogram-based (time-frequency) and waveform-based (time-domain) approaches exist, each has limitations. Spectrograms lack phase information, while raw audio models are difficult to train effectively.

This paper proposes a novel architecture that combines the strengths of raw audio and spectrogram representations to estimate a time-frequency mask for separating singing voice. The proposed architecture consists of two main components: a learnable filter and a Y-net. The learnable filter offers the advantage of learning filters capable of extracting crucial features not present in the STFT spectrogram while incorporating phase information. The Y-net extracts features from both domains and recreates the spectrogram of the singing voice.

## II. RELATED WORK

The network is inspired by U-Net [6], widely used for mask estimation. Unlike X-shaped architectures that use separate branches for each input [15], [14], our Y-shaped approach uses a single decoder branch, resulting in fewer parameters, faster training, and lower computational cost.

## III. ARCHITECTURE

The network takes raw audio waveform and spectrogram as inputs to estimate a mask that separates the singing voice.

### A. Learnable Spectrogram
Converts raw audio into a spectrogram-like format using 1-D convolutions with varying dilation rates (1, 2, 4, 8, 16) to capture long-term dependencies.

### B. Encoder
Two encoder branches extract features:
1.  **Waveform Branch:** Processes the output of the learnable spectrogram.
2.  **Spectral Branch:** Processes the STFT magnitude spectrogram.

Both branches use a stack of convolutional layers, max pooling, and activation functions (LeakyRelu for waveform, ReLu for spectral). Features from both branches are concatenated at the network's core.

### C. Skip Connections
Propagate information from both encoder branches to the shared decoder to preserve high-frequency details.

### D. Decoder
Consists of up-sampling layers and convolutions. It receives inputs from the previous decoder layer and skip connections from both spectral and waveform encoders. The final output is an estimated mask, which is multiplied by the input mixture spectrogram to obtain the vocal spectrogram. The vocal waveform is reconstructed using the original phase (ISTFT).

## IV. RESULTS AND EXPERIMENT

### A. Dataset
MUSDB18 dataset [17] (150 songs: 100 train, 25 val, 25 test).

### B. Experimental Setup
*   **Framework:** PyTorch
*   **Hardware:** Nvidia V100 GPU
*   **Training:** 100 epochs, batch size 16, Adam optimizer (lr=0.0001), MSE loss.

### C. Evaluation Metric
*   Signal-to-Distortion Ratio (SDR) [19]
*   Scale-Invariant Signal to-Noise-Ratio (SI-SNR) [4]
*   Short-Time Objective Intelligibility (STOI) [20]

### D. Comparison Results

**Table I: Comparison of Source Separation Performance**

| Method | SDR | SI-SNR | STOI |
| :--- | :--- | :--- | :--- |
| U-Net | 6.61 | 5.82 | 0.55 |
| U-Net + Learnable Spectrogram | 4.75 | 3.93 | 0.54 |
| **Y-Net** | **7.56** | **6.13** | **0.62** |

The Y-Net significantly outperformed the baseline U-Net (0.95 dB increase in SDR) and the U-Net with learnable spectrogram input. The use of Hardtanh activation in the final layer further improved performance.

## V. CONCLUSION

The Y-Net architecture improves music source separation by leveraging both spectrogram and raw audio features via parallel encoder branches converging into a common core. It outperforms standard U-Net models while maintaining efficiency. A limitation is the use of ISTFT which may reduce SDR; future work could explore end-to-end waveform networks.

## REFERENCES
[1] M. Goto and H. Hashiguchi, ”Improved harmonic-percussive separation...”, *ICASSP*, 2003.
[4] Y. Luo and N. Mesgarani, ‘Conv-tasnet...’, *IEEE/ACM transactions on audio, speech, and language processing*, 2019.
[6] A. Jansson et al., ‘Singing voice separation with deep u-net convolutional networks’, 2017.
[17] Z. Rafii et al., ‘The MUSDB18 corpus for music separation’, 2017.
