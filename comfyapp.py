import json
import subprocess
import uuid
from pathlib import Path
from typing import Dict

import modal


image = (  # build up a Modal Image to run ComfyUI, step by step
    modal.Image.debian_slim(  # start from basic Linux with Python
        python_version="3.11"
    )
    .apt_install("git")  # install git to clone ComfyUI
    .apt_install("nano")  # install to have a minimal text editor if we wanted to change something minimal
    .apt_install("libgl1-mesa-glx")  # needed to run ComfyUI
    .apt_install("libglib2.0-0")  # needed to run ComfyUI
    .pip_install_from_requirements(
        "requirements.txt"
    )
    .run_commands(  # use comfy-cli to install the ComfyUI repo and its dependencies
        "comfy --skip-prompt install --nvidia"
    )
)

image = (
    image.run_commands(
        "comfy --skip-prompt model download --url https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors --relative-path models/clip"
    )
    .run_commands(
        "comfy --skip-prompt model download --url https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors --relative-path models/clip"
    )
    .run_commands(
        "comfy --skip-prompt model download --url https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/ae.safetensors --relative-path models/vae"
    )
    .run_commands(# download the GGUF Q8 model
        "comfy --skip-prompt model download --url https://huggingface.co/city96/FLUX.1-dev-gguf/resolve/main/flux1-dev-Q8_0.gguf  --relative-path models/unet",
    )
    # .run_commands(
    #     "comfy --skip-prompt model download --url https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors --relative-path models/unet"
    # )
    # Add .run_commands(...) calls for any other models you want to download
)

# PULID
image = (
    image.run_commands(
        "comfy --skip-prompt model download --url https://huggingface.co/guozinan/PuLID/resolve/main/pulid_flux_v0.9.0.safetensors  --relative-path models/pulid",   
    )
    .run_commands(# download the GGUF Q8 model
        "comfy --skip-prompt model download --url https://huggingface.co/QuanSun/EVA-CLIP/resolve/main/EVA02_CLIP_L_336_psz14_s6B.pt  --relative-path models/clip",
    )
    .run_commands(
        "comfy --skip-prompt model download --url https://huggingface.co/MonsterMMORPG/tools/resolve/main/1k3d68.onnx  --relative-path models/insightface/models/antelopev2",
    )
    .run_commands(
        "comfy --skip-prompt model download --url https://huggingface.co/MonsterMMORPG/tools/resolve/main/2d106det.onnx  --relative-path models/insightface/models/antelopev2",
    )
    .run_commands(
        "comfy --skip-prompt model download --url https://huggingface.co/MonsterMMORPG/tools/resolve/main/genderage.onnx  --relative-path models/insightface/models/antelopev2",
    )
    .run_commands(
        "comfy --skip-prompt model download --url https://huggingface.co/MonsterMMORPG/tools/resolve/main/glintr100.onnx  --relative-path models/insightface/models/antelopev2",
    )
    .run_commands(
        "comfy --skip-prompt model download --url https://huggingface.co/MonsterMMORPG/tools/resolve/main/scrfd_10g_bnkps.onnx  --relative-path models/insightface/models/antelopev2",
    )

    
)

image = (
    image.run_commands(  # download a custom node
        "comfy node install image-resize-comfyui"
    )
    .run_commands( # gguf node required for q8 model
        "comfy node install https://github.com/city96/ComfyUI-GGUF"
    )
    .run_commands( # gguf node required for q8 model
        "comfy node install https://github.com/balazik/ComfyUI-PuLID-Flux.git"
    )
    # Add .run_commands(...) calls for any other custom nodes you want to download
)



# # XLABS STAFF
#  # put down here additional layers to your likings below
# image = (
#     image.run_commands( # XLabs ControlNet node 
#         "comfy node install https://github.com/XLabs-AI/x-flux-comfyui"
#     )
#     .run_commands( #download controlnet v3 xlabs ai
#         "comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-controlnet-depth-v3/resolve/main/flux-depth-controlnet-v3.safetensors --relative-path models/xlabs/controlnets",
#         "comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-controlnet-canny-v3/resolve/main/flux-canny-controlnet-v3.safetensors --relative-path models/xlabs/controlnets",
#         "comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-controlnet-hed-v3/resolve/main/flux-hed-controlnet-v3.safetensors --relative-path models/xlabs/controlnets",
#     )
#     .run_commands( #install control net requried for above xlabs
#         "comfy node install https://github.com/Fannovel16/comfyui_controlnet_aux"
#     )
#     .run_commands( #xlab loras --optional
#         "comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/art_lora_comfy_converted.safetensors --relative-path models/loras",
#         "comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/anime_lora_comfy_converted.safetensors --relative-path models/loras",
#         "comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/disney_lora_comfy_converted.safetensors --relative-path models/loras",
#         "comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/mjv6_lora_comfy_converted.safetensors --relative-path models/loras",
#         "comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/realism_lora_comfy_converted.safetensors --relative-path models/loras",
#         "comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/scenery_lora_comfy_converted.safetensors --relative-path models/loras"
#     )
# )


app = modal.App(name="flux1-dev-comfyui", image=image)

@app.function(
    allow_concurrent_inputs=10,
    concurrency_limit=1,
    container_idle_timeout=30,
    timeout=1800,
    gpu="A10G",
)
@modal.web_server(8000, startup_timeout=60)
def ui():
    subprocess.Popen("comfy launch -- --listen 0.0.0.0 --port 8000", shell=True)
