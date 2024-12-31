import llama_cpp
print("llama_cpp version:", llama_cpp.__version__)

# Create a very small context to test CUDA functionality
llm = llama_cpp.Llama(
    model_path=None,  # We don't need a real model for this test
    n_ctx=8,
    n_gpu_layers=1
)
print("CUDA available:", llm.context.cuda)
