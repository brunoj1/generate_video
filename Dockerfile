# Use specific version of nvidia cuda image
FROM wlsdml1114/multitalk-base:1.4 as runtime

RUN pip install -U "huggingface_hub[hf_transfer]"
RUN pip install runpod websocket-client

WORKDIR /

RUN git clone https://github.com/comfyanonymous/ComfyUI.git && \
    cd /ComfyUI && \
    pip install -r requirements.txt

RUN cd /ComfyUI/custom_nodes && \
    git clone https://github.com/Comfy-Org/ComfyUI-Manager.git && \
    cd ComfyUI-Manager && \
    pip install -r requirements.txt
    
RUN cd /ComfyUI/custom_nodes && \
    git clone https://github.com/city96/ComfyUI-GGUF && \
    cd ComfyUI-GGUF && \
    pip install -r requirements.txt

RUN cd /ComfyUI/custom_nodes && \
    git clone https://github.com/kijai/ComfyUI-KJNodes && \
    cd ComfyUI-KJNodes && \
    pip install -r requirements.txt

RUN cd /ComfyUI/custom_nodes && \
    git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite && \
    cd ComfyUI-VideoHelperSuite && \
    pip install -r requirements.txt
    
RUN cd /ComfyUI/custom_nodes && \
    git clone https://github.com/kael558/ComfyUI-GGUF-FantasyTalking && \
    cd ComfyUI-GGUF-FantasyTalking && \
    pip install -r requirements.txt
    
RUN cd /ComfyUI/custom_nodes && \
    git clone https://github.com/orssorbit/ComfyUI-wanBlockswap

RUN cd /ComfyUI/custom_nodes && \
    git clone https://github.com/kijai/ComfyUI-WanVideoWrapper && \
    cd ComfyUI-WanVideoWrapper && \
    pip install -r requirements.txt

COPY /workspace/wan2.2_vae.safetensors /ComfyUI/models/vae
COPY /workspace/mt5_xxl_fp16.safetensors /ComfyUI/models/text_encoders
COPY /workspace/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors /ComfyUI/models/diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors
COPY /workspace/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors /ComfyUI/models/diffusion_models/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors
COPY /workspace/Wan21_CausVid_14B_T2V_lora_rank32.safetensors /ComfyUI/models/loras/Wan21_CausVid_14B_T2V_lora_rank32.safetensors
COPY /workspace/Wan2.2-Lightning_I2V-A14B-4steps-lora_HIGH_fp16.safetensors /ComfyUI/models/loras/Wan2.2-Lightning_I2V-A14B-4steps-lora_HIGH_fp16.safetensors
COPY /workspace/Wan2.2-Lightning_I2V-A14B-4steps-lora_LOW_fp16.safetensors /ComfyUI/models/loras/Wan2.2-Lightning_I2V-A14B-4steps-lora_LOW_fp16.safetensors

RUN pip install onnx
RUN pip install onnxruntime-gpu

COPY . .
COPY extra_model_paths.yaml /ComfyUI/extra_model_paths.yaml
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]