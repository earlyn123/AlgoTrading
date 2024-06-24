import sys
import os
import argparse
import asyncio

project_dir = os.path.abspath(os.path.dirname(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

async def run_layer(layer):
    match layer:
        case 'bento': 
            from FakeDataBento.fake_bento_layer import main as bento_main
            await bento_main()
        case 'model':
            from ModelLayer.model_layer import main as model_main
            await model_main()
        case 'data':
            from DataLayer.data_layer import main as data_main
            await data_main()
        case 'exe':
            from ExecutionLayer.execution_layer import main as execution_main
            await execution_main()
        case _:
            print(f"unknown layer {layer}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run different layers")
    parser.add_argument('layer', type=str, help='The layer to run (data, exe, model, bento)')
    args = parser.parse_args()
    asyncio.run(run_layer(args.layer))

