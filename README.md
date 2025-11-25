<div align="center">
  
  # LLM-Based Emergency Response Handling

  #### ILP Coursework 3: Lucas Bruckbauer (s2539949)
  
</div>
  
# Required Packages
Install the necessary python dependencies from your terminal
```
$ pip install -r requirements.txt
```

# Local LLM Setup
This project uses a local lightweight LLM (phi3) to classify emergency messages and choose medical supplies.
The model runs using Ollama, a small local inference runtime.

Download and install from the official site at [**https://ollama.com/download**](https://ollama.com/download).

Next, from the terminal run
```
$ ollama pull phi3
```
It is possible to use an alternative LLM with Ollama if preferred by running
```
$ ollama pull <model_name>
```
However, you must also change the `MODEL` parameter in `src/service/llm_service.py` to match the model name.

# Running the Service
to get the service up and running, simply run the following in the terminal:
```
$ python3 main.py
```

```json
[
    {
        "id": "1",
        "position":
        {
            "lng": -3.200,
            "lat": 55.945
        },
        "content": "Hi, I am having a severe allergic reaction! Send help ASAP"
    },
    ...
]
```
