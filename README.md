# Wan22 for RunPod Serverless

** THIS IS A FORK of [![Runpod](https://api.runpod.io/badge/wlsdml1114/generate_video)](https://console.runpod.io/hub/wlsdml1114/generate_video)

This project is a template designed to easily deploy and use [Wan22](https://github.com/Comfy-Org/Wan_2.2_ComfyUI_Repackaged) in the RunPod .Serverless environment.

Wan22 is an advanced AI model that generates high-quality videos from images with natural motion and realistic animations.

## ✨ Key Features

*   **Image-to-Video Generation**: Converts static images into dynamic videos with natural motion.
*   **High-Quality Output**: Produces high-resolution videos with realistic animations.
*   **Customizable Parameters**: Control video generation with various parameters like seed, width, height, and prompts.
*   **ComfyUI Integration**: Built on top of ComfyUI for flexible workflow management.

## 🚀 RunPod Serverless Template

This template includes all the necessary components to run Wan22 as a RunPod Serverless Worker.

*   **Dockerfile**: Configures the environment and installs all dependencies required for model execution.
*   **handler.py**: Implements the handler function that processes requests for RunPod Serverless.
*   **entrypoint.sh**: Performs initialization tasks when the worker starts.
*   **wan22.json**: Workflow configuration for image-to-video generation.

### Input

The `input` object must contain the following fields. Images can be input using **Base64** 

#### Image Input
| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `first_image_base64` | `string` | No | `/example_image.png` | Base64 encoded string of the input image |
| `first_image_base64` | `string` | No | `/example_image.png` | Base64 encoded string of the input image |


**Important**: To use LoRA models, you must upload the LoRA files to the `/loras/` folder in your RunPod Network Volume. The LoRA model names in `lora_pairs` should match the filenames in the `/loras/` folder.

#### Video Generation Parameters
| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `prompt` | `string` | Yes | - | Description text for the video to be generated |
| `seed` | `integer` | Yes | - | Random seed for video generation |
| `cfg` | `float` | Yes | - | CFG scale for generation |
| `width` | `integer` | Yes | - | Width of the output video in pixels |
| `height` | `integer` | Yes | - | Height of the output video in pixels |
| `length` | `integer` | No | `81` | Length of the generated video |
| `steps` | `integer` | No | `10` | Number of denoising steps |

**Request Examples:**

#### 1. Basic Generation (No LoRA)
```json
{
  "input": {
    "prompt": "A person walking in a natural way.",
    "first_image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD...",
    "last_image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD...",
    "seed": 12345,
    "cfg": 7.5,
    "width": 512,
    "height": 512,
    "length": 81,
    "steps": 10
  }
}
```

### Output

#### Success

If the job is successful, it returns a JSON object with the generated video Base64 encoded.

| Parameter | Type | Description |
| --- | --- | --- |
| `video` | `string` | Base64 encoded video file data. |

**Success Response Example:**

```json
{
  "video": "data:video/mp4;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
}
```

#### Error

If the job fails, it returns a JSON object containing an error message.

| Parameter | Type | Description |
| --- | --- | --- |
| `error` | `string` | Description of the error that occurred. |

**Error Response Example:**

```json
{
  "error": "Unable to find video."
}
```

## 🛠️ Usage and API Reference

1.  Create a Serverless Endpoint on RunPod based on this repository.
2.  Once the build is complete and the endpoint is active, submit jobs via HTTP POST requests according to the API Reference below.

### 📁 Using Network Volumes

Instead of directly transmitting Base64 encoded files, you can use RunPod's Network Volumes to handle large files. This is especially useful when dealing with large image files and LoRA models.

1.  **Create and Connect Network Volume**: Create a Network Volume (e.g., S3-based volume) from the RunPod dashboard and connect it to your Serverless Endpoint settings.
2.  **Upload Files**: Upload the image files and LoRA models you want to use to the created Network Volume.
3.  **File Organization**: 
    - Place your input images anywhere in the Network Volume
4.  **Specify Paths**: When making an API request, specify the file paths within the Network Volume:
    - For `image_path`: Use the full path to your image file (e.g., `"/my_volume/images/portrait.jpg"`)

## 🔧 Workflow Configuration

This template includes multiple workflow configurations that are automatically selected based on the number of LoRA pairs:

*   **wan22.json**: First to last frame Image-to-video generation workflow without LoRA

### Workflow Selection Logic
The workflows are based on ComfyUI and include all necessary nodes for Wan22 processing, including:
- CLIP text encoding for prompts
- VAE loading and processing
- WanImageToVideo node for video generation
- LoRA loading and application nodes (when applicable)
- Image concatenation and processing nodes

## 🙏 Original Project

This project is based on the following original repository. All rights to the model and core logic belong to the original authors.

*   **Wan22:** [https://github.com/Wan-Video/Wan2.2](https://github.com/Wan-Video/Wan2.2)
*   **ComfyUI:** [https://github.com/comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI)
*   **ComfyUI-WanVideoWrapper** [https://github.com/kijai/ComfyUI-WanVideoWrapper](https://github.com/kijai/ComfyUI-WanVideoWrapper)

## 📄 License

The original Wan22 project follows its respective license. This template also adheres to that license.
