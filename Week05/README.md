# Week05 — Transfer Learning and Model Reuse

## Topic
Use a model exported from Teachable Machine and compare it with a pretrained MobileNetV2 transfer-learning workflow in Google Colab.

## Learning goals
- Explain transfer learning, feature extraction, and fine-tuning.
- Reuse a pretrained image model rather than training from scratch.
- Load an exported Teachable Machine model and run inference.
- Build a MobileNetV2 transfer-learning classifier with TensorFlow/Keras.
- Compare accuracy, training time, overfitting, and inference behavior.
- Record experiment settings and results reproducibly.

## Files
- Week05_TransferLearning_MobileNetV2_Lab.ipynb — student Colab workbook
- Week05_TransferLearning_MobileNetV2_Lab_강의자용해석.ipynb — instructor commentary version
- requirements.txt — minimal Python package list

## Recommended workflow
1. Prepare a small image dataset with 3 classes.
2. Run baseline inference with the Week04 Teachable Machine export.
3. Create train/validation datasets.
4. Load MobileNetV2 with ImageNet weights and freeze the base model.
5. Train the classification head.
6. Unfreeze upper layers and fine-tune with a small learning rate.
7. Compare baseline vs transfer-learning results.

## Colab
Open the notebook in Google Colab and run cells from top to bottom. GPU is optional for a small dataset but recommended for fine-tuning.
