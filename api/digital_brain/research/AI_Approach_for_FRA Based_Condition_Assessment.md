# AI Approach for FRA Based Condition Assessment of Power Transformers

©20XX IEEE

**Abstract**
Condition assessment of power transformers is important to avoid power system failures because it usually causes significant economic losses. Frequency response measurements (FRA) have been developed as an effective tool to detect the internal mechanical integrity of power transformer windings. However, interpretation of FRA results can sometimes be tedious when comparing transformers with different structures. This paper presents an FRA measurements-based AI approach to recognize different faulty and non-faulty transformers irrespectively of their design structures.

FRA data sets were collected from 10 field-aged power transformers with different capacities, and each data set consisted of 100 features (i.e., 4 FRA frequency bands, 5 FRA measuring methods, and 5 statistical analyzing parameters). It was found that with two Principal Components, faulty and non-faulty transformers could be easily separated. Accordingly, the 10 features were reduced to 64 features by optimizing FRA measuring methods from 5 to 3. Then different ML techniques and NN algorithms were used to further classify the faulty transformers into three different fault types. It was found that fine kNN was the best method for transformer classification with a 100% accuracy of the tested samples.

**Keywords:** Condition Assessment, FRA, AI model, Fault Identification

## I. INTRODUCTION

A safe and stable power supply is highly dependent on the reliability of the equipment used in the power system. Among all the electrical equipment in a power grid, transformers are one of the important and expensive equipment. The useful life of the transformer is expected to be more than 25 years, and with proper asset management, more transformer operating time can be obtained. Condition monitoring and diagnostics of transformers are very important to avoid failures or outages, which usually cause economic losses. Transformer faults can be generally classified mainly into mechanical and electrical faults according to the causes of the fault. The mechanical fault of transformer windings is referred to here as the winding movement, i.e., winding displacement or deformation.

As per [1], Frequency Response Analysis (FRA) has been developed as an effective and sensitive technique for testing the winding integrity of transformers. Different factors such as transformer cores, windings, winding properties, and instrumentation dominate different frequency regions of the FRA trace. Frequency response should be measured and recorded at the transformer factory, which can be then used as a reference for future diagnosis.

The FRA method involves comparing the reference and diagnostic frequency response, and any deviation between them can be used to identify potential mechanical faults. Additionally, it may be possible to determine the type, severity, and location of the curvature fault based on the deviation. It should be noted that various winding construction types may be more susceptible to specific winding faults due to their differing physical structures.

FRA measurements are crucial in assessing the condition of transformers, as they can reveal winding deformations resulting from mechanical deformations or large electromagnetic forces arising from over-currents during through faults, tap-changer faults, faulty synchronization, and more. Although mechanically robust, the likelihood of surviving a short circuit is significantly reduced once significant winding deformation has occurred due to local electromagnetic stresses. Additionally, any reduction in winding clamping resulting from insulation shrinkage due to aging will weaken the mechanical strength of the winding assembly, increasing the likelihood of failure. Mechanical assessments are therefore necessary to evaluate the transformer's expected reliability and its susceptibility to failure during a short circuit. FRA measurements are increasingly used as a quality assurance tool because they can provide information on winding consistency and core geometric structure.

## II. BACKGROUND

### A. AI Techniques for FRA Based Fault Identification

In literature, there have been many efforts where Machine Learning methods are implemented for the detection and identification of transformer winding faults using FRA.
*   [2] used the correlation coefficient (CC) calculated in three frequency sub-bands as a feature for ANN. However, a total of 26 cases were used for training and testing, and only two classes, healthy and defective, were identified.
*   [3] used the absolute ratio in the healthy state and deformed state FRA to extract features. Support vector machine (SVM) is used to detect four types of winding faults, using only two groups of setups.
*   [4] used 9 indices and 90 cases for a three-layer ANN, but all faults were applied to a single transformer model.
*   [5] used an ANN classifier to detect electrical and mechanical faults of transformer winding, but limited to a 1.2 MVA single transformer circuit model.
*   [6] used an SVM classifier to classify various mechanical faults on only one transformer model.
*   [7] employed SVM to identify winding type using FRA on a set of 400/275 kW transformers.

The main objective of the study is to develop an automated approach to manage transformer assets. The results demonstrated in the paper show the significant potential of Machine Learning algorithms in detecting and classifying faults.

### B. Statistical Indicators Methods

Various statistical indices used in the interpretation and diagnosis of FRA are summarized below.

**Table I. Method Equations**

| Method | Equation |
| :--- | :--- |
| Standard Deviation (SD) | $SD = \sqrt{\frac{1}{N-1}\sum_{i=1}^{N}(Y_i - X_i)^2}$ |
| Correlation Coefficient (CC) | $CC = \frac{\sum_{i=1}^{N}X_iY_i}{\sqrt{\sum_{i=1}^{N}X_i^2 \sum_{i=1}^{N}Y_i^2}}$ |
| Cross-Correlation Factor (CCF) | $CCF = \frac{\sum_{i=1}^{N}(X_i - \bar{X})(Y_i - \bar{Y})}{\sqrt{\sum_{i=1}^{N}(X_i - \bar{X})^2 \sum_{i=1}^{N}(Y_i - \bar{Y})^2}}$ |

*where $\bar{X} = \frac{1}{N}\sum_{i=1}^{N}X_i$ and $\bar{Y} = \frac{1}{N}\sum_{i=1}^{N}Y_i$*

Correlation coefficient (CC), standard deviation (SD), and Cross-Correlation Factor (CCF) are commonly used indices.
*   In [8], if CC > 0.995, FRA data groups are deemed equal.
*   In [9], stricter requirements are CC > 0.9998 for magnitude and 0.95 per phase. SD < 1 for magnitude and < 10 for phase indicates similarity. Higher SD indicates winding deformation.
*   In [10], CC and SD were used as ANN inputs for discriminating winding health conditions, achieving 95% accuracy with 24 training and 20 testing patterns.
*   In [11], Sum Squared Error, Correlation Coefficient, Sum Squared Ratio, Sum Squared Max-Min Ratio, and Absolute Sum of Logarithmic Error (ASLE) were used. ASLE performed best.

## III. METHODOLOGY

This study introduces a novel method to identify faults in a transformer using FRA data. The task was divided into three sub-tasks:
1.  Faults Detection and Classification with Reference FRA dataset.
2.  Faults Detection and Classification without Reference FRA dataset.
3.  Faults Detection and Classification regardless of the Transformer design (Power Rating, Model, Manufactured Year, etc.).

### A. Prepare the Dataset

Transformer datasets were obtained from the Ceylon Electricity Board (CEB) in `.tfra` format and exported as CSVs. 5 sub-datasets were obtained for every test:
*   High Voltage (Low Voltage Open)
*   High Voltage (LV Shorted)
*   Low Voltage, Capacitive, Inductive

Only Amplitude vs. frequency plots were used as phase angle impact was found to be insignificant.

### B. Reference Dataset

Reference datasets are usually manufacturing data. If unavailable (old transformers), industrial standards use:
*   **Time-based comparison:** Compare with earlier healthy stage data.
*   **Phase comparison:** Compare with other phases (fault usually in one phase).
*   **Sister transformer comparison:** Compare with a similar transformer.

### C. Data Comparison in Mathematical Domain

Each subplot was divided into 4 sub-frequency bands. 5 parameters were defined for comparison:
*   Standard Deviation
*   Correlation Coefficient
*   Cross-Correlation Factor
*   Absolute Sum of Logarithmic Error
*   Sum Squared Ratio Error

This created a dataset with 100 features (5 Sub datasets x 4 Sub Frequency Bands x 5 Mathematical Parameters).

### D. Classifying Faulty and Non-Faulty Transformers

**1) Dimensional Reduction (PCA)**
Principal Component Analysis (PCA) was used to reduce dimensionality. It helped to identify that the first 3 Principal Components gave a good separation between faulty and non-faulty transformers.

### E. Optimization

To reduce computational cost, the model was optimized. It was found that classification was possible with reduced data:
*   **3 Sub Data sets:** HV winding (LV Open), HV winding (LV Short), LV winding.
*   **3 Parameters:** Standard Deviation, Correlation Coefficient, Cross-Correlation Factor.

The dataset was reduced to 36 features (3 x 4 x 3) and classification was conducted in 2D using only 2 principal components.

### F. Classify The Transformer Faults Using Classification Algorithms

Fault classification was done into 4 categories using 2 principal components:
1.  Ground – Insulation Failure
2.  LV Turn – Turn Failure
3.  Free Bucking
4.  Non-Faulty

80% of data (50 sets) was utilized for training and 20% (14 sets) for testing.

**Table II. Accuracy using Supervised Learning Algorithms**

| Classification Algorithm | Accuracy (Validation) |
| :--- | :--- |
| Decision Tree | 96.2% |
| **Fine KNN** | **100%** |
| Medium KNN | 82.7% |
| Coarse KNN | 82.7% |
| Linear SVM | 84.6% |
| Quadratic SVM | 94.2% |
| Cubic SVM | 94.2% |
| Kernel Naive Bayes | 82.7% |

**Table III. Accuracy using Neural Network Architectures**

| Classification Algorithm | Accuracy (Validation) |
| :--- | :--- |
| Narrow Neural Network | 93.0% |
| Medium Neural Network | 93.0% |
| Wide Neural Network | 93.0% |

Fine k-Nearest Neighbour (kNN) was selected for fault classification due to 100% accuracy.

### G. Fine k-Nearest Neighbour Algorithm

k-NN is a supervised learning classifier based on proximity.
*   **Precision:** 1.0
*   **Recall:** 1.0
*   **F1 Score:** 1.0
*   **Accuracy:** 100%

## IV. RESULTS

1.  **Dimensional Reduction:** PCA was used effectively.
2.  **Classification:** Fine k-NN achieved 100% accuracy, Precision, Recall, and F1 Score.
3.  **Independence:** The model is independent of Transformer Parameters and supports Time, Phase, and Sister Transformer based comparisons.

## V. CONCLUSION

The statistical analyses of the four frequency bands of a typical FRA signature assess the condition of power transformers. The dominant three statistical parameters are the standard deviation, the correlation coefficient, and the cross-correlation factor. The paper confirms the adequacy of three types of FRA measurements (HV-LV open, HV-LV short, LV) to separate faulty and non-faulty transformers using PCA.

Faulty transformers can be classified into free buckling, ground-insulation failure, and turn-to-turn failure. Fine k-Nearest Neighbour algorithm was the best technique suitable for this classification with 100% accuracy.

## REFERENCES

[1] S. Kumara, et al., “Frequency Domain Measurements for Diagnosis of Power Transformers: Experiences from Australia, Malaysia, Sri Lanka and UK,” *CIGRE Sci. Eng. (CSE)*, 2021, 82–107.
[2] Z. Jin, J. Li, and Z. Zhu, “Diagnosis of transformer winding deformation on the basis of artificial neural network,” *6th ICPADM*, 2000.
[3] M. Bigdeli, et al., “Transformer winding faults classification based on transfer function analysis by support vector machine,” *IET Electr. Power Appl.*, 2012.
[4] K. R. Gandhi and K. P. Badgujar, “Artificial neural network-based identification of deviation in frequency response of power transformer windings,” *AICERA/iCMMD*, IEEE, 2014.
[5] A. J. Ghanizadeh and G. B. Gharehpetian, “ANN and cross-correlation based features for discrimination between electrical and mechanical defects...,” *IEEE Trans. Dielectr. Electr. Insul.*, 2014.
[6] J. Liu, et al., “Classifying transformer winding deformation fault types and degrees using FRA based on support vector machine,” *IEEE Access*, 2019.
[7] X. Mao, et al., “Winding type recognition through supervised machine learning using frequency response analysis (FRA) data,” *ICEMPE*, IEEE, 2019.
[8] H. El-Hajjar, *Identification of Transformer Mechanical Faults Using Frequency Response Analysis*, 2008.
[9] P. M. Nirgude, et al., “Application of numerical evaluation techniques for interpreting frequency response measurements in power transformers,” *IET Sci. Meas. Technol.*, 2008.
[10] D. K. Xu, “Application of artificial neural network to the detection of the transformer winding deformation,” *ISH99*, 1999.
[11] Kim, J.-W. et al. (2005) “Fault diagnosis of a power transformer using an improved frequency-response analysis,” *IEEE Transactions on Power Delivery*.
