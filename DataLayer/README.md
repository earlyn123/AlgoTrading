## Data Layer
- Handles aggregation and cleaning of the raw DataBento trade data
- Acts as the WS client for the Model Layer
  - Need to run `../ModelLayer/model_layer_entrypoint.py` before `data_layer.py` for the client to connect correctly 