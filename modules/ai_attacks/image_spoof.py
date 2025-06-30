# image_spoof.py 
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet18
from PIL import Image
import matplotlib.pyplot as plt
import os

print("[*] Generating adversarial patch...")

# Parameters
IMAGE_PATH = "target.jpg"   # Replace with a real image path
SAVED_IMAGE = "spoofed_output.jpg"
PATCH_INTENSITY = 0.01

# Ensure image exists
if not os.path.exists(IMAGE_PATH):
    print("[!] Image not found. Place a 'target.jpg' in the script directory.")
    exit()

# Load image
orig_image = Image.open(IMAGE_PATH).convert('RGB')
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])
image_tensor = transform(orig_image).unsqueeze(0)

# Load model
model = resnet18(pretrained=True)
model.eval()

# Target misclassification label (e.g., class 5 = 'banana')
target_label = torch.tensor([5])

# Define loss
criterion = torch.nn.CrossEntropyLoss()

# Require gradient for input
image_tensor.requires_grad = True

# Forward pass
output = model(image_tensor)
loss = criterion(output, target_label)
model.zero_grad()
loss.backward()

# FGSM attack
adv_image = image_tensor + PATCH_INTENSITY * image_tensor.grad.sign()
adv_image = torch.clamp(adv_image, 0, 1)

# Convert to PIL and save
adv_pil = transforms.ToPILImage()(adv_image.squeeze())
adv_pil.save(SAVED_IMAGE)

# Show both
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.title("Original")
plt.imshow(orig_image)
plt.axis('off')

plt.subplot(1, 2, 2)
plt.title("Adversarial Patch")
plt.imshow(adv_pil)
plt.axis('off')

plt.tight_layout()
plt.show()

print(f"[✓] Adversarial image saved as: {SAVED_IMAGE}")
