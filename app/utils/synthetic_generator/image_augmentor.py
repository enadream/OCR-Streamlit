import cv2
import numpy as np
import random

class ScannedDocumentAugmentor:
    def __init__(
        self,
        blur_prob: float = 0.5,
        skew_prob: float = 0.6,
        noise_prob: float = 0.7,
        smudge_prob: float = 0.3,
        brightness_prob: float = 0.8,
    ):
        self.probabilities = {
            "blur": blur_prob,
            "skew": skew_prob,
            "noise": noise_prob,
            "smudge": smudge_prob,
            "brightness": brightness_prob,
        }

    def _apply_gaussian_blur(self, image: np.ndarray) -> np.ndarray:
        # Applies a slight Gaussian blur.
        kernel_size = random.choice([(3, 3), (5, 5)])
        return cv2.GaussianBlur(image, kernel_size, 0)

    def _apply_skew(self, image: np.ndarray) -> np.ndarray:
        # Applies a slight perspective skew to the image.
        h, w = image.shape[:2]
        max_skew = 0.03 # Controls the max horizontal skew as a fraction of width
        
        # Original points
        pts1 = np.float32([[0, 0], [w - 1, 0], [0, h - 1], [w - 1, h - 1]])
        
        # New skewed points
        skew_x1 = random.uniform(-max_skew, max_skew) * w
        skew_x2 = random.uniform(-max_skew, max_skew) * w
        
        pts2 = np.float32([
            [skew_x1, 0], 
            [w - 1 + skew_x2, 0], 
            [0, h - 1], 
            [w - 1, h - 1]
        ])

        M = cv2.getPerspectiveTransform(pts1, pts2)
        return cv2.warpPerspective(image, M, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))

    def _add_gaussian_noise(self, image: np.ndarray) -> np.ndarray:
        # Adds Gaussian noise to the image.
        row, col, ch = image.shape
        mean = 0
        var = random.uniform(10, 50)  # Variance of noise
        sigma = var**0.5
        gauss = np.random.normal(mean, sigma, (row, col, ch))
        gauss = gauss.reshape(row, col, ch)
        noisy_image = np.clip(image + gauss, 0, 255)
        return noisy_image.astype(np.uint8)

    def _add_ink_smudges(self, image: np.ndarray) -> np.ndarray:
        # Adds dark, semi-transparent smudges.
        h, w = image.shape[:2]
        num_smudges = random.randint(1, 4)
        
        overlay = image.copy()
        
        for _ in range(num_smudges):
            center_x = random.randint(0, w)
            center_y = random.randint(0, h)
            size = random.randint(50, 150)
            
            # Create a transparent layer for the smudge
            smudge_layer = np.zeros_like(image, dtype=np.uint8)
            cv2.ellipse(smudge_layer, (center_x, center_y), (size, int(size * 0.6)), random.randint(0, 360), 0, 360, (0, 0, 0), -1)
            
            # Blur the smudge to make it soft
            smudge_layer = cv2.GaussianBlur(smudge_layer, (101, 101), 0)
            
            # Blend the smudge with the overlay
            alpha = random.uniform(0.05, 0.15) # Opacity of the smudge
            cv2.addWeighted(smudge_layer, alpha, overlay, 1 - alpha, 0, overlay)
            
        return overlay

    def _adjust_brightness_contrast(self, image: np.ndarray) -> np.ndarray:
        # Randomly adjusts brightness and contrast.
        contrast = random.uniform(0.8, 1.2)  # alpha
        brightness = random.randint(-20, 10) # beta
        return cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)

    def process_image(self, image_path: str) -> np.ndarray:
        """
        Loads an image and applies a random sequence of augmentations.

        Args:
            image_path (str): Path to the input image.

        Returns:
            np.ndarray: The augmented image in OpenCV (BGR) format.
        """
        image = cv2.imread(image_path)
        
        if random.random() < self.probabilities["skew"]:
            image = self._apply_skew(image)
        if random.random() < self.probabilities["blur"]:
            image = self._apply_gaussian_blur(image)
        if random.random() < self.probabilities["noise"]:
            image = self._add_gaussian_noise(image)
        if random.random() < self.probabilities["brightness"]:
            image = self._adjust_brightness_contrast(image)
        if random.random() < self.probabilities["smudge"]:
            image = self._add_ink_smudges(image)
            
        return image